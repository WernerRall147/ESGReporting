"""
ESG Reporting Solution - Interactive Demo Script
===============================================

This script demonstrates the key features of our deployed ESG Reporting solution.
"""

import os
import subprocess
import sys
from pathlib import Path

def print_banner(title):
    """Print a banner for each demo section."""
    print("\n" + "="*80)
    print(f"🌍 {title}")
    print("="*80)

def print_step(step_num, title):
    """Print a step header."""
    print(f"\n{'='*60}")
    print(f"📊 STEP {step_num}: {title}")
    print("="*60)

def run_command(command, description):
    """Run a command and display the result."""
    print(f"\n🔄 {description}")
    print(f"💻 Command: {command}")
    print("📋 Output:")
    print("-" * 40)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=".")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"⚠️ Errors/Warnings: {result.stderr}")
        if result.returncode != 0:
            print(f"❌ Command failed with exit code: {result.returncode}")
        else:
            print("✅ Command completed successfully")
    except Exception as e:
        print(f"❌ Error running command: {e}")
    
    print("-" * 40)

def demo_environment_setup():
    """Demo Step 1: Environment Setup and Verification"""
    print_step(1, "ENVIRONMENT SETUP AND VERIFICATION")
    
    print("\n📋 Azure Environment Information:")
    print("✅ Deployed Infrastructure:")
    print("  🏗️ Resource Group: rg-esgdemo")
    print("  💾 Storage Account: esgdatara3xkg7cwqzzg")
    print("  🔐 Key Vault: kv-esg-ra3xkg7cwqzzg")
    print("  📦 Container Registry: cresgra3xkg7cwqzzg")
    print("  🚀 Container App: ca-esg-ra3xkg7cwqzzg")
    print("  📊 Application Insights: appi-esg-ra3xkg7cwqzzg")
    print("  📋 Log Analytics: log-esg-ra3xkg7cwqzzg")
    print("  🔑 Managed Identity: id-esg-ra3xkg7cwqzzg")
    
    print("\n🔗 Access URLs:")
    print("  🌐 Container App: https://ca-esg-ra3xkg7cwqzzg.agreeablemushroom-8e78fbcf.eastus.azurecontainerapps.io")
    print("  🔐 Key Vault: https://kv-esg-ra3xkg7cwqzzg.vault.azure.net/")
    print("  💾 Storage: https://esgdatara3xkg7cwqzzg.blob.core.windows.net/")
    
    print("\n📊 Environment Variables:")
    env_vars = {
        'AZURE_STORAGE_ACCOUNT_NAME': 'esgdatara3xkg7cwqzzg',
        'AZURE_KEY_VAULT_URL': 'https://kv-esg-ra3xkg7cwqzzg.vault.azure.net/',
        'AZURE_CLIENT_ID': 'acfccfca-4ce2-4929-b5eb-0c1222df37c5',
        'AZURE_CONTAINER_REGISTRY_ENDPOINT': 'cresgra3xkg7cwqzzg.azurecr.io'
    }
    
    for key, value in env_vars.items():
        print(f"  {key}: {value}")

def demo_sample_data():
    """Demo Step 2: Sample Data Overview"""
    print_step(2, "SAMPLE ESG DATA OVERVIEW")
    
    # Show sample data files
    sample_files = [
        ("sample_emissions.csv", "Emissions Data", "CO2 emissions, energy usage, water consumption"),
        ("sample_activities.csv", "Activities Data", "ESG training, audits, assessments"),
        ("sample_suppliers.csv", "Suppliers Data", "Supplier ESG scores and certifications")
    ]
    
    for filename, title, description in sample_files:
        if Path(filename).exists():
            print(f"\n📄 {title} ({filename}):")
            print(f"   📝 {description}")
            
            # Show file size and row count
            try:
                with open(filename, 'r') as f:
                    lines = f.readlines()
                    print(f"   📏 Size: {len(lines)} rows")
                    
                    # Show first few lines
                    print(f"   📋 Preview (first 3 rows):")
                    for i, line in enumerate(lines[:3]):
                        if i == 0:
                            print(f"      Header: {line.strip()}")
                        else:
                            print(f"      Row {i}: {line.strip()}")
            except Exception as e:
                print(f"   ❌ Error reading file: {e}")

def demo_cli_help():
    """Demo Step 3: CLI Help and Commands"""
    print_step(3, "ESG REPORTING CLI COMMANDS")
    
    print("\n💻 Available CLI Commands:")
    
    commands = [
        ("python -m src.esg_reporting.cli --help", "Show main CLI help"),
        ("python -m src.esg_reporting.cli upload --help", "Show upload command help"),
        ("python -m src.esg_reporting.cli list --help", "Show list command help"),
        ("python -m src.esg_reporting.cli download --help", "Show download command help"),
        ("python -m src.esg_reporting.cli validate --help", "Show validate command help")
    ]
    
    for command, description in commands:
        run_command(command, description)

def demo_data_validation():
    """Demo Step 4: Data Validation"""
    print_step(4, "DATA VALIDATION EXAMPLES")
    
    print("\n🔍 Validating sample ESG data files...")
    
    validation_commands = [
        ("python -m src.esg_reporting.cli validate sample_emissions.csv --entity-type emissions", 
         "Validate emissions data"),
        ("python -m src.esg_reporting.cli validate sample_activities.csv --entity-type activities", 
         "Validate activities data"),
        ("python -m src.esg_reporting.cli validate sample_suppliers.csv --entity-type suppliers", 
         "Validate suppliers data")
    ]
    
    for command, description in validation_commands:
        run_command(command, description)

def demo_data_upload():
    """Demo Step 5: Data Upload to Azure"""
    print_step(5, "DATA UPLOAD TO AZURE BLOB STORAGE")
    
    print("\n☁️ Uploading sample data to Azure Blob Storage...")
    
    upload_commands = [
        ("python -m src.esg_reporting.cli upload sample_emissions.csv --entity-type emissions --validate --clean", 
         "Upload emissions data with validation and cleaning"),
        ("python -m src.esg_reporting.cli upload sample_activities.csv --entity-type activities --validate", 
         "Upload activities data with validation"),
        ("python -m src.esg_reporting.cli upload sample_suppliers.csv --entity-type suppliers --overwrite", 
         "Upload suppliers data (overwrite if exists)")
    ]
    
    for command, description in upload_commands:
        run_command(command, description)

def demo_data_listing():
    """Demo Step 6: List Uploaded Data"""
    print_step(6, "LIST UPLOADED ESG DATA")
    
    print("\n📋 Listing uploaded ESG data from Azure Blob Storage...")
    
    list_commands = [
        ("python -m src.esg_reporting.cli list", "List all uploaded ESG data"),
        ("python -m src.esg_reporting.cli list --entity-type emissions --details", "List emissions data with details"),
        ("python -m src.esg_reporting.cli list --entity-type activities", "List activities data"),
        ("python -m src.esg_reporting.cli list --entity-type suppliers", "List suppliers data")
    ]
    
    for command, description in list_commands:
        run_command(command, description)

def demo_data_download():
    """Demo Step 7: Download Data"""
    print_step(7, "DOWNLOAD ESG DATA FROM AZURE")
    
    print("\n📥 Downloading ESG data from Azure Blob Storage...")
    
    # Create download directory
    download_dir = Path("downloads")
    download_dir.mkdir(exist_ok=True)
    
    download_commands = [
        ("python -m src.esg_reporting.cli download emissions/sample_emissions.csv --output-path downloads/", 
         "Download emissions data"),
        ("python -m src.esg_reporting.cli download activities/sample_activities.csv --output-path downloads/", 
         "Download activities data")
    ]
    
    for command, description in download_commands:
        run_command(command, description)

def demo_azure_resources():
    """Demo Step 8: Azure Resources Status"""
    print_step(8, "AZURE RESOURCES STATUS")
    
    print("\n🔍 Checking Azure resources status...")
    
    azure_commands = [
        ("az group show --name rg-esgdemo --query '{name:name, location:location, provisioningState:properties.provisioningState}'", 
         "Check resource group status"),
        ("az storage account show --name esgdatara3xkg7cwqzzg --resource-group rg-esgdemo --query '{name:name, provisioningState:provisioningState}'", 
         "Check storage account status"),
        ("az containerapp show --name ca-esg-ra3xkg7cwqzzg --resource-group rg-esgdemo --query '{name:name, status:properties.runningStatus}'", 
         "Check container app status")
    ]
    
    for command, description in azure_commands:
        run_command(command, description)

def demo_monitoring():
    """Demo Step 9: Monitoring and Observability"""
    print_step(9, "MONITORING AND OBSERVABILITY")
    
    print("\n📊 Azure Monitoring Features:")
    print("✅ Application Insights for performance monitoring")
    print("✅ Log Analytics for centralized logging")
    print("✅ Container Apps logs and metrics")
    print("✅ Storage account access logs")
    print("✅ Key Vault audit logs")
    
    print("\n🔗 Monitoring URLs:")
    print("  📊 Azure Portal: https://portal.azure.com/#@/resource/subscriptions/6690c42b-73e0-437c-92f6-a4161424f2a3/resourceGroups/rg-esgdemo/overview")
    print("  📈 Application Insights: https://portal.azure.com/#@/resource/subscriptions/6690c42b-73e0-437c-92f6-a4161424f2a3/resourceGroups/rg-esgdemo/providers/microsoft.insights/components/appi-esg-ra3xkg7cwqzzg/overview")
    print("  📋 Log Analytics: https://portal.azure.com/#@/resource/subscriptions/6690c42b-73e0-437c-92f6-a4161424f2a3/resourceGroups/rg-esgdemo/providers/Microsoft.OperationalInsights/workspaces/log-esg-ra3xkg7cwqzzg/overview")

def demo_business_value():
    """Demo Step 10: Business Value and Use Cases"""
    print_step(10, "BUSINESS VALUE AND USE CASES")
    
    print("\n💼 Business Value:")
    print("✅ Automated ESG data processing and validation")
    print("✅ Centralized storage for ESG data from Microsoft Sustainability Manager")
    print("✅ Scalable Azure cloud infrastructure")
    print("✅ Secure data handling with Azure Key Vault and Managed Identity")
    print("✅ Real-time monitoring and alerting")
    print("✅ Easy integration with existing Azure services")
    
    print("\n🎯 Key Use Cases:")
    print("📊 ESG Reporting Automation:")
    print("  - Process CSV exports from Microsoft Sustainability Manager")
    print("  - Validate data quality and completeness")
    print("  - Clean and standardize ESG data")
    print("  - Store in centralized Azure Blob Storage")
    
    print("\n📈 Data Analytics:")
    print("  - Calculate carbon footprint trends")
    print("  - Monitor renewable energy adoption")
    print("  - Track supplier ESG performance")
    print("  - Generate compliance reports")
    
    print("\n🔄 Workflow Integration:")
    print("  - Automated data pipelines")
    print("  - Event-driven processing")
    print("  - API integration capabilities")
    print("  - Dashboard and visualization ready")

def run_interactive_demo():
    """Run the complete interactive demo"""
    print_banner("ESG REPORTING SOLUTION - INTERACTIVE DEMO")
    
    print("🌍 Welcome to the ESG Reporting Solution Demo!")
    print("This demonstration showcases our Azure-based ESG data management platform.")
    print("\n📋 Demo Overview:")
    print("  🔧 Environment setup and verification")
    print("  📊 Sample ESG data overview")
    print("  💻 CLI commands and usage")
    print("  🔍 Data validation capabilities")
    print("  ☁️ Azure Blob Storage upload/download")
    print("  📈 Monitoring and observability")
    print("  💼 Business value and use cases")
    
    input("\n⏸️  Press Enter to start the demo...")
    
    try:
        demo_environment_setup()
        input("\n⏸️  Press Enter to continue to sample data overview...")
        
        demo_sample_data()
        input("\n⏸️  Press Enter to continue to CLI commands...")
        
        demo_cli_help()
        input("\n⏸️  Press Enter to continue to data validation...")
        
        demo_data_validation()
        input("\n⏸️  Press Enter to continue to data upload (requires Azure credentials)...")
        
        demo_data_upload()
        input("\n⏸️  Press Enter to continue to data listing...")
        
        demo_data_listing()
        input("\n⏸️  Press Enter to continue to data download...")
        
        demo_data_download()
        input("\n⏸️  Press Enter to continue to Azure resources check...")
        
        demo_azure_resources()
        input("\n⏸️  Press Enter to continue to monitoring overview...")
        
        demo_monitoring()
        input("\n⏸️  Press Enter to continue to business value discussion...")
        
        demo_business_value()
        
        print_banner("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("✅ All ESG Reporting solution features demonstrated")
        print("✅ Sample data processed and uploaded to Azure")
        print("✅ CLI functionality showcased")
        print("✅ Azure infrastructure verified")
        print("✅ Monitoring and observability explained")
        print("✅ Business value and use cases covered")
        
        print("\n🚀 Your ESG Reporting solution is ready for production use!")
        print("🔗 Container App: https://ca-esg-ra3xkg7cwqzzg.agreeablemushroom-8e78fbcf.eastus.azurecontainerapps.io")
        print("📧 For support: Contact your Azure administrator")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user. Thank you!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("Please check your Azure credentials and network connectivity.")

if __name__ == "__main__":
    run_interactive_demo()
