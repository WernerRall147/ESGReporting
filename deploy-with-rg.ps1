#!/usr/bin/env pwsh
# Deploy ESG Reporting solution with automatic resource group creation

param(
    [string]$EnvironmentName = "esg-prod",
    [string]$Location = "eastus"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 ESG Reporting Deployment Script" -ForegroundColor Green
Write-Host "Environment: $EnvironmentName" -ForegroundColor Yellow
Write-Host "Location: $Location" -ForegroundColor Yellow

# Check if Azure CLI is installed
if (!(Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error "Azure CLI is not installed or not in PATH. Please install Azure CLI first."
    exit 1
}

# Check if user is logged in
$accountInfo = az account show 2>$null
if (!$accountInfo) {
    Write-Host "❌ Not logged in to Azure. Please run 'az login' first." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Azure CLI authenticated" -ForegroundColor Green

# Define resource group name (using consistent naming)
$resourceGroupName = "rg-$EnvironmentName"

# Check if resource group exists
Write-Host "🔍 Checking if resource group '$resourceGroupName' exists..." -ForegroundColor Yellow
$rgExists = az group exists --name $resourceGroupName 2>$null

if ($rgExists -eq "false") {
    Write-Host "📦 Creating resource group '$resourceGroupName' in '$Location'..." -ForegroundColor Yellow
    az group create --name $resourceGroupName --location $Location --tags "azd-env-name=$EnvironmentName" "environment=$EnvironmentName" "project=esg-reporting"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Failed to create resource group"
        exit 1
    }
    
    Write-Host "✅ Resource group created successfully" -ForegroundColor Green
}
else {
    Write-Host "✅ Resource group '$resourceGroupName' already exists" -ForegroundColor Green
}

# Run azd up
Write-Host "🚀 Starting Azure deployment with azd up..." -ForegroundColor Yellow

# First ensure azd environment is initialized
Write-Host "🔧 Initializing azd environment..." -ForegroundColor Yellow
azd env set AZURE_RESOURCE_GROUP $resourceGroupName

azd up --environment $EnvironmentName

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Deployment failed"
    exit 1
}

Write-Host "✅ ESG Reporting solution deployed successfully!" -ForegroundColor Green
Write-Host "🎉 You can now test your ESG data download endpoints" -ForegroundColor Cyan
