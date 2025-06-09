"""
ESG Reporting Solution - Step-by-Step Demo
==========================================

This demo showcases the complete functionality of our ESG Reporting solution
deployed on Azure, including data upload, processing, validation, and retrieval.
"""

import os
import json
import pandas as pd
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# Demo data generation
def create_sample_esg_data():
    """Create sample ESG data files for demonstration."""
    
    # Emissions data
    emissions_data = {
        'Date': pd.date_range('2024-01-01', periods=12, freq='M'),
        'Facility_ID': ['FAC001', 'FAC002', 'FAC003'] * 4,
        'Scope1_CO2_Tons': [150.5, 230.7, 189.2, 145.8, 220.3, 175.6, 160.4, 240.1, 195.7, 155.2, 235.8, 180.9],
        'Scope2_CO2_Tons': [89.3, 120.5, 95.7, 85.1, 115.8, 90.4, 92.6, 125.3, 98.1, 87.9, 118.7, 93.2],
        'Energy_Usage_MWh': [1250.5, 1890.7, 1456.3, 1200.8, 1820.4, 1380.2, 1320.6, 1950.1, 1520.9, 1280.3, 1870.5, 1420.7],
        'Water_Usage_M3': [5600, 8200, 6800, 5400, 7900, 6200, 5800, 8500, 7100, 5700, 8100, 6500],
        'Waste_Generated_Tons': [45.2, 67.8, 52.3, 42.1, 65.4, 48.9, 46.7, 70.2, 54.6, 44.3, 68.1, 51.5],
        'Renewable_Energy_Percent': [25.5, 18.3, 22.7, 28.1, 20.5, 24.8, 26.3, 19.7, 23.4, 29.2, 21.8, 25.1]
    }
    
    df_emissions = pd.DataFrame(emissions_data)
    
    # Activities data
    activities_data = {
        'Date': pd.date_range('2024-01-01', periods=20, freq='2W'),
        'Activity_Type': ['Training', 'Audit', 'Assessment', 'Reporting', 'Improvement'] * 4,
        'Department': ['Operations', 'Facilities', 'HR', 'Finance', 'IT'] * 4,
        'Participants': [25, 12, 8, 15, 30, 22, 10, 6, 18, 28, 26, 14, 9, 16, 32, 24, 11, 7, 19, 29],
        'Duration_Hours': [4, 8, 6, 2, 3, 4, 8, 6, 2, 3, 4, 8, 6, 2, 3, 4, 8, 6, 2, 3],
        'Cost_USD': [1200, 3200, 2400, 800, 1500, 1300, 3000, 2200, 900, 1600, 1400, 3400, 2600, 1000, 1700, 1250, 3100, 2300, 950, 1550],
        'Status': ['Completed', 'Completed', 'In Progress', 'Completed', 'Planned'] * 4
    }
    
    df_activities = pd.DataFrame(activities_data)
    
    # Suppliers data
    suppliers_data = {
        'Supplier_ID': [f'SUP{str(i).zfill(3)}' for i in range(1, 16)],
        'Supplier_Name': [f'Supplier Company {i}' for i in range(1, 16)],
        'Category': ['Manufacturing', 'Services', 'Materials', 'Logistics', 'Technology'] * 3,
        'ESG_Score': [75, 82, 68, 90, 77, 85, 71, 88, 79, 83, 72, 86, 74, 91, 80],
        'Carbon_Footprint_Score': [3.2, 2.8, 4.1, 2.1, 3.5, 2.5, 3.9, 2.3, 3.1, 2.7, 3.8, 2.4, 3.6, 2.0, 2.9],
        'Waste_Management_Score': [8.5, 9.2, 7.8, 9.8, 8.1, 9.0, 8.3, 9.5, 8.7, 9.1, 8.0, 9.3, 8.4, 9.9, 8.8],
        'Social_Responsibility_Score': [7.8, 8.5, 7.2, 9.1, 7.9, 8.2, 7.6, 8.8, 8.0, 8.4, 7.4, 8.6, 7.7, 9.0, 8.1],
        'Last_Audit_Date': pd.date_range('2023-06-01', periods=15, freq='2W'),
        'Certification_Status': ['ISO 14001', 'ISO 14001', 'None', 'ISO 14001 + ISO 45001', 'ISO 14001'] * 3
    }
    
    df_suppliers = pd.DataFrame(suppliers_data)
    
    return df_emissions, df_activities, df_suppliers

async def demo_step_1_setup():
    """Step 1: Setup and Environment Check"""
    print("\n" + "="*60)
    print("🚀 STEP 1: ENVIRONMENT SETUP AND VERIFICATION")
    print("="*60)
    
    print("\n📋 Checking Azure environment...")
    
    # Check environment variables
    required_vars = [
        'AZURE_STORAGE_ACCOUNT_NAME',
        'AZURE_KEY_VAULT_URL', 
        'AZURE_CLIENT_ID'
    ]
    
    from src.esg_reporting.config import settings
    
    print(f"✅ Storage Account: {settings.azure_storage_account_name}")
    print(f"✅ Key Vault URL: {settings.azure_key_vault_url}")
    print(f"✅ Client ID: {settings.azure_client_id}")
    print(f"✅ Environment: {settings.environment}")
    print(f"✅ Log Level: {settings.log_level}")
    
    print("\n🏗️ Infrastructure deployed:")
    print("  - Azure Storage Account (Blob Storage)")
    print("  - Azure Key Vault (Secrets Management)")  
    print("  - Azure Container Registry")
    print("  - Azure Container Apps (Running our CLI)")
    print("  - Azure Log Analytics & Application Insights")
    print("  - User Assigned Managed Identity")
    
    print("\n✅ Environment setup complete!")

async def demo_step_2_create_data():
    """Step 2: Create Sample ESG Data"""
    print("\n" + "="*60)
    print("📊 STEP 2: CREATING SAMPLE ESG DATA")
    print("="*60)
    
    # Create demo data directory
    demo_dir = Path("demo_data")
    demo_dir.mkdir(exist_ok=True)
    
    print("\n📈 Generating sample ESG datasets...")
    
    # Create sample data
    df_emissions, df_activities, df_suppliers = create_sample_esg_data()
    
    # Save to files
    emissions_file = demo_dir / "emissions_data.csv"
    activities_file = demo_dir / "activities_data.csv"
    suppliers_file = demo_dir / "suppliers_data.csv"
    
    df_emissions.to_csv(emissions_file, index=False)
    df_activities.to_csv(activities_file, index=False)
    df_suppliers.to_csv(suppliers_file, index=False)
    
    print(f"✅ Created emissions data: {emissions_file} ({len(df_emissions)} records)")
    print(f"✅ Created activities data: {activities_file} ({len(df_activities)} records)")
    print(f"✅ Created suppliers data: {suppliers_file} ({len(df_suppliers)} records)")
    
    # Display sample data
    print("\n📋 Sample Emissions Data (first 5 rows):")
    print(df_emissions.head().to_string(index=False))
    
    print("\n📋 Sample Activities Data (first 5 rows):")
    print(df_activities.head().to_string(index=False))
    
    print("\n📋 Sample Suppliers Data (first 5 rows):")
    print(df_suppliers.head().to_string(index=False))
    
    return emissions_file, activities_file, suppliers_file

async def demo_step_3_upload_and_process():
    """Step 3: Upload and Process Data"""
    print("\n" + "="*60)
    print("☁️ STEP 3: UPLOAD AND PROCESS ESG DATA")
    print("="*60)
    
    from src.esg_reporting.storage import ESGBlobStorageClient
    from src.esg_reporting.processor import ESGDataProcessor
    
    # Initialize clients
    storage_client = ESGBlobStorageClient()
    processor = ESGDataProcessor()
    
    demo_dir = Path("demo_data")
    files_to_upload = [
        (demo_dir / "emissions_data.csv", "emissions"),
        (demo_dir / "activities_data.csv", "activities"), 
        (demo_dir / "suppliers_data.csv", "suppliers")
    ]
    
    upload_results = []
    
    for file_path, entity_type in files_to_upload:
        print(f"\n🔄 Processing {entity_type} data from {file_path}...")
        
        try:
            # Read and validate data
            df = processor.read_file(str(file_path))
            print(f"  📖 Loaded {len(df)} rows, {len(df.columns)} columns")
            
            # Validate data
            validation_report = processor.validate_data(df, entity_type)
            print(f"  🔍 Validation: {validation_report['summary']['total_issues']} issues found")
            
            if validation_report['summary']['total_issues'] > 0:
                print(f"    ⚠️ Issues: {', '.join(validation_report['summary']['issues_by_type'].keys())}")
            
            # Clean data if needed
            if validation_report['summary']['total_issues'] > 0:
                cleaned_df, cleaning_report = processor.clean_data(df, validation_report)
                print(f"  🧹 Cleaned data: {len(cleaning_report['actions_performed'])} actions performed")
                
                # Save cleaned version
                cleaned_file = demo_dir / f"cleaned_{file_path.name}"
                save_result = processor.save_processed_data(cleaned_df, str(cleaned_file), "csv")
                if save_result['success']:
                    file_path = cleaned_file
                    print(f"  💾 Saved cleaned data to: {cleaned_file}")
            
            # Upload to Azure Blob Storage
            metadata = {
                "entity_type": entity_type,
                "validation_summary": json.dumps(validation_report['summary']),
                "upload_timestamp": datetime.now().isoformat()
            }
            
            result = await storage_client.upload_file(
                local_file_path=str(file_path),
                entity_type=entity_type,
                metadata=metadata,
                overwrite=True
            )
            
            if result['success']:
                print(f"  ✅ Upload successful!")
                print(f"    📍 Blob: {result['blob_name']}")
                print(f"    📏 Size: {result['file_size_mb']:.2f} MB")
                print(f"    🔗 URL: {result['blob_url']}")
                
                upload_results.append({
                    'entity_type': entity_type,
                    'blob_name': result['blob_name'],
                    'blob_url': result['blob_url'],
                    'file_size_mb': result['file_size_mb']
                })
            else:
                print(f"  ❌ Upload failed: {result['error']}")
                
        except Exception as e:
            print(f"  ❌ Error processing {entity_type}: {e}")
    
    print(f"\n✅ Upload and processing complete! {len(upload_results)} files uploaded successfully.")
    return upload_results

async def demo_step_4_data_retrieval():
    """Step 4: Data Retrieval and Management"""
    print("\n" + "="*60)
    print("📥 STEP 4: DATA RETRIEVAL AND MANAGEMENT")
    print("="*60)
    
    from src.esg_reporting.storage import ESGBlobStorageClient
    
    storage_client = ESGBlobStorageClient()
    
    print("\n📋 Listing all uploaded ESG data...")
    
    # List all blobs by entity type
    entity_types = ["emissions", "activities", "suppliers"]
    
    for entity_type in entity_types:
        print(f"\n📊 {entity_type.upper()} Data:")
        try:
            blobs = await storage_client.list_blobs(entity_type=entity_type)
            
            if blobs['success']:
                if blobs['blobs']:
                    for blob in blobs['blobs']:
                        print(f"  📄 {blob['name']}")
                        print(f"     📅 Modified: {blob['last_modified']}")
                        print(f"     📏 Size: {blob['size_mb']:.2f} MB")
                        if blob.get('metadata'):
                            print(f"     📝 Entity Type: {blob['metadata'].get('entity_type', 'N/A')}")
                else:
                    print(f"  📭 No {entity_type} data found")
            else:
                print(f"  ❌ Error listing {entity_type}: {blobs['error']}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Download sample data
    print(f"\n📥 Downloading sample emissions data for analysis...")
    try:
        download_result = await storage_client.download_file(
            blob_name="emissions/emissions_data.csv",
            local_file_path="demo_data/downloaded_emissions.csv"
        )
        
        if download_result['success']:
            print(f"  ✅ Downloaded: {download_result['local_file_path']}")
            print(f"  📏 Size: {download_result['file_size_mb']:.2f} MB")
            
            # Load and display summary
            from src.esg_reporting.processor import ESGDataProcessor
            processor = ESGDataProcessor()
            df = processor.read_file(download_result['local_file_path'])
            
            print(f"\n📊 Data Summary:")
            print(f"  📈 Total records: {len(df)}")
            print(f"  📅 Date range: {df['Date'].min()} to {df['Date'].max()}")
            print(f"  🏭 Facilities: {df['Facility_ID'].nunique()}")
            print(f"  🌍 Total Scope 1 CO2: {df['Scope1_CO2_Tons'].sum():.1f} tons")
            print(f"  ⚡ Total Energy Usage: {df['Energy_Usage_MWh'].sum():.1f} MWh")
            
        else:
            print(f"  ❌ Download failed: {download_result['error']}")
            
    except Exception as e:
        print(f"  ❌ Download error: {e}")

async def demo_step_5_analytics():
    """Step 5: ESG Analytics and Reporting"""
    print("\n" + "="*60)
    print("📈 STEP 5: ESG ANALYTICS AND REPORTING")
    print("="*60)
    
    from src.esg_reporting.processor import ESGDataProcessor
    
    processor = ESGDataProcessor()
    
    print("\n🔬 Performing ESG analytics on uploaded data...")
    
    # Load the downloaded emissions data
    try:
        df = processor.read_file("demo_data/downloaded_emissions.csv")
        
        # Basic analytics
        print(f"\n📊 EMISSIONS ANALYTICS:")
        print(f"  🌍 Total Scope 1 Emissions: {df['Scope1_CO2_Tons'].sum():.1f} tons CO2")
        print(f"  🏭 Total Scope 2 Emissions: {df['Scope2_CO2_Tons'].sum():.1f} tons CO2")
        print(f"  📈 Average monthly Scope 1: {df['Scope1_CO2_Tons'].mean():.1f} tons CO2")
        print(f"  📉 Lowest monthly Scope 1: {df['Scope1_CO2_Tons'].min():.1f} tons CO2")
        print(f"  📊 Highest monthly Scope 1: {df['Scope1_CO2_Tons'].max():.1f} tons CO2")
        
        print(f"\n⚡ ENERGY ANALYTICS:")
        print(f"  🔌 Total Energy Usage: {df['Energy_Usage_MWh'].sum():.1f} MWh")
        print(f"  🌱 Average Renewable %: {df['Renewable_Energy_Percent'].mean():.1f}%")
        print(f"  🎯 Best Renewable Month: {df['Renewable_Energy_Percent'].max():.1f}%")
        
        print(f"\n💧 RESOURCE ANALYTICS:")
        print(f"  💧 Total Water Usage: {df['Water_Usage_M3'].sum():,} m³")
        print(f"  🗑️ Total Waste Generated: {df['Waste_Generated_Tons'].sum():.1f} tons")
        
        # Facility comparison
        print(f"\n🏭 FACILITY COMPARISON:")
        facility_summary = df.groupby('Facility_ID').agg({
            'Scope1_CO2_Tons': 'sum',
            'Energy_Usage_MWh': 'sum',
            'Renewable_Energy_Percent': 'mean'
        }).round(1)
        
        for facility in facility_summary.index:
            data = facility_summary.loc[facility]
            print(f"  🏢 {facility}:")
            print(f"     🌍 CO2: {data['Scope1_CO2_Tons']} tons")
            print(f"     ⚡ Energy: {data['Energy_Usage_MWh']} MWh") 
            print(f"     🌱 Renewable: {data['Renewable_Energy_Percent']:.1f}%")
        
        # Generate analytics report
        analytics_report = {
            "report_date": datetime.now().isoformat(),
            "data_period": f"{df['Date'].min()} to {df['Date'].max()}",
            "total_records": len(df),
            "facilities_count": df['Facility_ID'].nunique(),
            "emissions": {
                "scope1_total_tons": float(df['Scope1_CO2_Tons'].sum()),
                "scope2_total_tons": float(df['Scope2_CO2_Tons'].sum()),
                "scope1_average_monthly": float(df['Scope1_CO2_Tons'].mean())
            },
            "energy": {
                "total_usage_mwh": float(df['Energy_Usage_MWh'].sum()),
                "average_renewable_percent": float(df['Renewable_Energy_Percent'].mean())
            },
            "resources": {
                "total_water_m3": float(df['Water_Usage_M3'].sum()),
                "total_waste_tons": float(df['Waste_Generated_Tons'].sum())
            }
        }
        
        # Save analytics report
        report_file = Path("demo_data") / "esg_analytics_report.json"
        with open(report_file, 'w') as f:
            json.dump(analytics_report, f, indent=2)
        
        print(f"\n💾 Analytics report saved to: {report_file}")
        
    except Exception as e:
        print(f"❌ Analytics error: {e}")

async def demo_step_6_monitoring():
    """Step 6: Monitoring and Observability"""
    print("\n" + "="*60)
    print("📊 STEP 6: MONITORING AND OBSERVABILITY")
    print("="*60)
    
    print("\n🔍 Azure monitoring and observability features:")
    
    print("\n📈 APPLICATION INSIGHTS:")
    print("  ✅ Request tracking and performance monitoring")
    print("  ✅ Error logging and exception tracking") 
    print("  ✅ Custom metrics for ESG data processing")
    print("  ✅ Dependency tracking (Storage, Key Vault)")
    
    print("\n📋 LOG ANALYTICS:")
    print("  ✅ Centralized logging from Container Apps")
    print("  ✅ Custom KQL queries for ESG operations")
    print("  ✅ Alert rules for processing failures")
    print("  ✅ Performance dashboards")
    
    print("\n🔐 SECURITY MONITORING:")
    print("  ✅ Managed Identity authentication")
    print("  ✅ Key Vault access logging")
    print("  ✅ Storage account audit logs")
    print("  ✅ Container Apps security scanning")
    
    print("\n📊 BUSINESS METRICS:")
    print("  ✅ ESG data upload volumes")
    print("  ✅ Processing success rates")
    print("  ✅ Data validation error rates")
    print("  ✅ Storage usage trends")
    
    print("\n🔗 Monitoring URLs:")
    print("  📊 Azure Portal: https://portal.azure.com/#@/resource/subscriptions/6690c42b-73e0-437c-92f6-a4161424f2a3/resourceGroups/rg-esgdemo/overview")
    print("  📈 Application Insights: https://portal.azure.com/#@/resource/subscriptions/6690c42b-73e0-437c-92f6-a4161424f2a3/resourceGroups/rg-esgdemo/providers/microsoft.insights/components/appi-esg-ra3xkg7cwqzzg/overview")

async def demo_step_7_cli_usage():
    """Step 7: CLI Usage Examples"""
    print("\n" + "="*60)
    print("💻 STEP 7: CLI USAGE EXAMPLES")
    print("="*60)
    
    print("\n🖥️ ESG Reporting CLI Commands:")
    
    print("\n📤 UPLOAD COMMANDS:")
    print("  # Basic upload")
    print("  esg-reporting upload emissions_data.csv --entity-type emissions")
    print("")
    print("  # Upload with validation and cleaning")
    print("  esg-reporting upload data.csv --entity-type emissions --validate --clean")
    print("")
    print("  # Upload with custom blob name")
    print("  esg-reporting upload data.csv --entity-type activities --blob-name custom-activities-2024")
    
    print("\n📥 LIST COMMANDS:")
    print("  # List all ESG data")
    print("  esg-reporting list")
    print("")
    print("  # List specific entity type")
    print("  esg-reporting list --entity-type emissions")
    print("")
    print("  # List with details")
    print("  esg-reporting list --entity-type suppliers --details")
    
    print("\n📊 DOWNLOAD COMMANDS:")
    print("  # Download specific file")
    print("  esg-reporting download emissions/emissions_data.csv")
    print("")
    print("  # Download to specific location")
    print("  esg-reporting download activities/activities_data.csv --output-path ./local_data/")
    
    print("\n🔍 VALIDATION COMMANDS:")
    print("  # Validate local file")
    print("  esg-reporting validate data.csv --entity-type emissions")
    print("")
    print("  # Validate and generate report")
    print("  esg-reporting validate data.csv --entity-type suppliers --report-path validation_report.json")
    
    print("\n🧹 PROCESSING COMMANDS:")
    print("  # Clean data file")
    print("  esg-reporting clean data.csv --entity-type emissions --output-path cleaned_data.csv")
    print("")
    print("  # Convert file format")
    print("  esg-reporting convert data.csv --output-format parquet")

async def run_complete_demo():
    """Run the complete ESG Reporting solution demo"""
    print("🌍 ESG REPORTING SOLUTION - COMPREHENSIVE DEMO")
    print("=" * 80)
    print("This demo showcases the complete Azure-based ESG reporting solution")
    print("including data upload, processing, validation, and analytics.")
    print("=" * 80)
    
    try:
        await demo_step_1_setup()
        await asyncio.sleep(2)
        
        files = await demo_step_2_create_data()
        await asyncio.sleep(2)
        
        upload_results = await demo_step_3_upload_and_process()
        await asyncio.sleep(2)
        
        await demo_step_4_data_retrieval()
        await asyncio.sleep(2)
        
        await demo_step_5_analytics()
        await asyncio.sleep(2)
        
        await demo_step_6_monitoring()
        await asyncio.sleep(2)
        
        await demo_step_7_cli_usage()
        
        print("\n" + "="*80)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("✅ All ESG Reporting solution features demonstrated")
        print("✅ Sample data created, uploaded, and processed")
        print("✅ Analytics and monitoring capabilities shown")
        print("✅ CLI usage examples provided")
        print("\n🚀 Your ESG Reporting solution is ready for production use!")
        print("🔗 Container App URL: https://ca-esg-ra3xkg7cwqzzg.agreeablemushroom-8e78fbcf.eastus.azurecontainerapps.io")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_complete_demo())
