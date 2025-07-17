targetScope = 'resourceGroup'

// Parameters
@description('The name of the environment (e.g., dev, prod)')
param environmentName string

@description('Location for all resources')
param location string = resourceGroup().location

@description('Principal ID for RBAC assignments')
param principalId string = ''

// Variables
// Generate unique resource suffix
var resourceToken = toLower(uniqueString(subscription().id, resourceGroup().id, environmentName))
var tags = {
  'azd-env-name': environmentName
  environment: environmentName
  project: 'esg-reporting'
}

// Storage Account for ESG data
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'esgdata${resourceToken}'
  location: location
  tags: union(tags, {
    'azd-service-name': 'storage'
  })
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    encryption: {
      services: {
        blob: {
          enabled: true
          keyType: 'Account'
        }
        file: {
          enabled: true
          keyType: 'Account'
        }
      }
      keySource: 'Microsoft.Storage'
    }
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    publicNetworkAccess: 'Enabled'
  }
}

// Blob Container for ESG data
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    cors: {
      corsRules: [
        {
          allowedOrigins: ['*']
          allowedMethods: ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']
          allowedHeaders: ['*']
          exposedHeaders: ['*']
          maxAgeInSeconds: 86400
        }
      ]
    }
  }
}

resource esgDataContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'esg-data'
  properties: {
    publicAccess: 'None'
  }
}

// Key Vault for secrets management
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'kv-esg-${resourceToken}'
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enabledForTemplateDeployment: true
    enableSoftDelete: true
    enablePurgeProtection: true
    softDeleteRetentionInDays: 7
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
}

// Log Analytics Workspace for monitoring
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-esg-${resourceToken}'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// Application Insights for application monitoring
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-esg-${resourceToken}'
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// Container Registry for storing container images
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: 'cresg${resourceToken}'
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
    policies: {
      quarantinePolicy: {
        status: 'disabled'
      }
      trustPolicy: {
        type: 'Notary'
        status: 'disabled'
      }
      retentionPolicy: {
        days: 7
        status: 'disabled'
      }
    }
    encryption: {
      status: 'disabled'
    }
    dataEndpointEnabled: false
    publicNetworkAccess: 'Enabled'
    networkRuleBypassOptions: 'AzureServices'
  }
}

// Container Apps Environment
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: 'cae-esg-${resourceToken}'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
  }
}

// Container App for ESG Reporting service
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'ca-esg-${resourceToken}'
  location: location
  tags: union(tags, {
    'azd-service-name': 'esg-reporting'
  })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        corsPolicy: {
          allowedOrigins: ['*']
          allowedMethods: ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']
          allowedHeaders: ['*']
        }
      }
      registries: [
        {
          server: containerRegistry.properties.loginServer
          identity: managedIdentity.id
        }
      ]
    }
    template: {
      containers: [
        {
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          name: 'esg-reporting'
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          env: [
            {
              name: 'AZURE_STORAGE_ACCOUNT_NAME'
              value: storageAccount.name
            }
            {
              name: 'AZURE_KEY_VAULT_URL'
              value: keyVault.properties.vaultUri
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: managedIdentity.properties.clientId
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: applicationInsights.properties.ConnectionString
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 10
      }
    }
  }
}

// Logic App for ESG Reporting Automation
resource logicApp 'Microsoft.Logic/workflows@2019-05-01' = {
  name: 'logic-esg-${resourceToken}'
  location: location
  tags: union(tags, {
    'azd-service-name': 'esg-logic-app'
  })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  properties: {
    state: 'Enabled'
    definition: {
      '$schema': 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#'
      contentVersion: '1.0.0.0'
      parameters: {
        storageAccountName: {
          defaultValue: storageAccount.name
          type: 'String'
        }
        containerAppUrl: {
          defaultValue: 'https://${containerApp.properties.configuration.ingress.fqdn}'
          type: 'String'
        }
        keyVaultUrl: {
          defaultValue: keyVault.properties.vaultUri
          type: 'String'
        }
      }
      triggers: {
        Daily_ESG_Processing: {
          type: 'Recurrence'
          recurrence: {
            frequency: 'Day'
            interval: 1
            schedule: {
              hours: [
                '9'
              ]
              minutes: [
                0
              ]
            }
            timeZone: 'UTC'
          }
        }
        Manual_Trigger: {
          type: 'Request'
          kind: 'Http'
          inputs: {
            schema: {
              type: 'object'
              properties: {
                fileName: {
                  type: 'string'
                }
                containerName: {
                  type: 'string'
                }
                processType: {
                  type: 'string'
                }
              }
            }
          }
        }
      }
      actions: {
        Initialize_Variables: {
          type: 'InitializeVariable'
          inputs: {
            variables: [
              {
                name: 'fileName'
                type: 'string'
                value: '@{coalesce(triggerBody()?[\'fileName\'], \'manual-trigger\')}'
              }
              {
                name: 'processType'
                type: 'string'
                value: '@{coalesce(triggerBody()?[\'processType\'], \'download-all\')}'
              }
            ]
          }
        }
        Log_Start: {
          type: 'Http'
          inputs: {
            method: 'POST'
            uri: '@{parameters(\'containerAppUrl\')}/api/log'
            headers: {
              'Content-Type': 'application/json'
            }
            body: {
              level: 'INFO'
              message: 'Logic App started ESG workflow'
              fileName: '@variables(\'fileName\')'
              processType: '@variables(\'processType\')'
              timestamp: '@utcNow()'
            }
          }
          runAfter: {
            Initialize_Variables: [
              'Succeeded'
            ]
          }
        }
        Process_ESG_Data: {
          type: 'Switch'
          expression: '@variables(\'processType\')'
          cases: {
            Download_All: {
              case: 'download-all'
              actions: {
                Download_All_ESG_Data: {
                  type: 'Http'
                  inputs: {
                    method: 'POST'
                    uri: '@{parameters(\'containerAppUrl\')}/api/download/all'
                    headers: {
                      'Content-Type': 'application/json'
                    }
                    body: {
                      timestamp: '@utcNow()'
                    }
                    authentication: {
                      type: 'ManagedServiceIdentity'
                    }
                  }
                }
              }
            }
            Download_Emissions: {
              case: 'download-emissions'
              actions: {
                Download_Emissions_Data: {
                  type: 'Http'
                  inputs: {
                    method: 'POST'
                    uri: '@{parameters(\'containerAppUrl\')}/api/download/emissions'
                    headers: {
                      'Content-Type': 'application/json'
                    }
                    body: {
                      timestamp: '@utcNow()'
                    }
                    authentication: {
                      type: 'ManagedServiceIdentity'
                    }
                  }
                }
              }
            }
            Download_Activities: {
              case: 'download-activities'
              actions: {
                Download_Activities_Data: {
                  type: 'Http'
                  inputs: {
                    method: 'POST'
                    uri: '@{parameters(\'containerAppUrl\')}/api/download/activities'
                    headers: {
                      'Content-Type': 'application/json'
                    }
                    body: {
                      timestamp: '@utcNow()'
                    }
                    authentication: {
                      type: 'ManagedServiceIdentity'
                    }
                  }
                }
              }
            }
          }
          default: {
            actions: {
              Process_Existing_Data: {
                type: 'Http'
                inputs: {
                  method: 'POST'
                  uri: '@{parameters(\'containerAppUrl\')}/api/process'
                  headers: {
                    'Content-Type': 'application/json'
                  }
                  body: {
                    fileName: '@variables(\'fileName\')'
                    container: 'esg-data'
                    outputContainer: 'processed-data'
                  }
                  authentication: {
                    type: 'ManagedServiceIdentity'
                  }
                }
              }
            }
          }
          runAfter: {
            Log_Start: [
              'Succeeded'
            ]
          }
        }
        Notify_Success: {
          type: 'Http'
          inputs: {
            method: 'POST'
            uri: '@{parameters(\'containerAppUrl\')}/api/notify'
            headers: {
              'Content-Type': 'application/json'
            }
            body: {
              status: 'SUCCESS'
              message: 'ESG workflow completed successfully'
              fileName: '@variables(\'fileName\')'
              processType: '@variables(\'processType\')'
              timestamp: '@utcNow()'
            }
          }
          runAfter: {
            Process_ESG_Data: [
              'Succeeded'
            ]
          }
        }
        Handle_Errors: {
          type: 'Http'
          inputs: {
            method: 'POST'
            uri: '@{parameters(\'containerAppUrl\')}/api/notify'
            headers: {
              'Content-Type': 'application/json'
            }
            body: {
              status: 'ERROR'
              message: 'ESG workflow failed'
              processType: '@variables(\'processType\')'
              timestamp: '@utcNow()'
            }
          }
          runAfter: {
            Process_ESG_Data: [
              'Failed'
              'Skipped'
              'TimedOut'
            ]
          }
        }
      }
      outputs: {}
    }
  }
}

// User-assigned managed identity
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-esg-${resourceToken}'
  location: location
  tags: tags
}

// Role assignments for managed identity
// Storage Blob Data Contributor role for the managed identity
resource storageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: storageAccount
  name: guid(storageAccount.id, managedIdentity.id, 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    ) // Storage Blob Data Contributor
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Key Vault Secrets User role for the managed identity
resource keyVaultRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: keyVault
  name: guid(keyVault.id, managedIdentity.id, '4633458b-17de-408a-b874-0445c86b69e6')
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '4633458b-17de-408a-b874-0445c86b69e6'
    ) // Key Vault Secrets User
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// ACR Pull role for the managed identity
resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: containerRegistry
  name: guid(containerRegistry.id, managedIdentity.id, '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '7f951dda-4ed3-4680-a7ca-43fe172d538d'
    ) // AcrPull
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Optional: Role assignment for the current user/principal
resource userStorageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(principalId)) {
  scope: storageAccount
  name: guid(storageAccount.id, principalId, 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    ) // Storage Blob Data Contributor
    principalId: principalId
    principalType: 'User'
  }
}

resource userKeyVaultRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(principalId)) {
  scope: keyVault
  name: guid(keyVault.id, principalId, '4633458b-17de-408a-b874-0445c86b69e6')
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '4633458b-17de-408a-b874-0445c86b69e6'
    ) // Key Vault Secrets User
    principalId: principalId
    principalType: 'User'
  }
}

// Outputs
output AZURE_STORAGE_ACCOUNT_NAME string = storageAccount.name
output AZURE_STORAGE_ACCOUNT_ID string = storageAccount.id
output AZURE_CONTAINER_NAME string = esgDataContainer.name
output AZURE_KEY_VAULT_URL string = keyVault.properties.vaultUri
output AZURE_KEY_VAULT_NAME string = keyVault.name
output MANAGED_IDENTITY_CLIENT_ID string = managedIdentity.properties.clientId
output MANAGED_IDENTITY_ID string = managedIdentity.id
output LOG_ANALYTICS_WORKSPACE_ID string = logAnalyticsWorkspace.id
output APPLICATION_INSIGHTS_CONNECTION_STRING string = applicationInsights.properties.ConnectionString
output RESOURCE_GROUP_NAME string = resourceGroup().name
output RESOURCE_GROUP_ID string = resourceGroup().id
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.properties.loginServer
output AZURE_CONTAINER_APPS_ENVIRONMENT_ID string = containerAppsEnvironment.id
output AZURE_CONTAINER_APP_NAME string = containerApp.name
output LOGIC_APP_NAME string = logicApp.name
output LOGIC_APP_ID string = logicApp.id
