#!/usr/bin/env python3
"""
Real Azure Carbon Optimization Demo
===================================

This script demonstrates actual Azure Carbon Optimization integration
with real emissions data from your Azure infrastructure.

Prerequisites:
- Azure CLI authentication (run 'az login')
- Access to Azure subscriptions with emissions data
- Required Python packages installed (pip install -r requirements.txt)
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta

def run_command(cmd, description):
    """Run a command and display results."""
    print(f"\n🔄 {description}")
    print(f"💻 Command: {cmd}")
    print("📋 Output:")
    print("-" * 40)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(result.stdout)
            print("✅ Command completed successfully")
        else:
            print(f"❌ Command failed with code {result.returncode}")
            print(f"Error: {result.stderr}")
        print("-" * 40)
        return result.returncode == 0, result.stdout
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        print("-" * 40)
        return False, ""

def get_azure_subscriptions():
    """Get available Azure subscriptions."""
    success, output = run_command("az account list --output json", "Getting Azure subscriptions")
    if success:
        try:
            subscriptions = json.loads(output)
            return [sub for sub in subscriptions if sub.get('state') == 'Enabled']
        except:
            return []
    return []

def main():
    print("""
================================================================================
🌍 REAL AZURE CARBON OPTIMIZATION DEMO
================================================================================
🌍 Welcome to the Real Azure Carbon Optimization Demo!
This demonstration shows actual Azure emissions data integration.

📋 Demo Features:
  🔧 Azure CLI authentication verification
  📊 Real Azure emissions data fetching
  🌍 Multiple subscription support
  💻 Integration with ESG reporting
  📈 Data visualization and analysis
  ☁️ Azure storage upload capabilities

⚠️  IMPORTANT: This demo fetches REAL data from Azure Carbon Optimization API.
Make sure you're authenticated and have appropriate permissions.
""")

    input("⏸️  Press Enter to continue...")

    # Step 1: Verify Azure Authentication
    print(f"\n📊 STEP 1: AZURE AUTHENTICATION VERIFICATION")
    print("=" * 60)
    
    success, output = run_command("az account show", "Checking Azure authentication")
    if not success:
        print("❌ Azure authentication failed. Please run 'az login' first.")
        return
    
    # Step 2: List Available Subscriptions
    print(f"\n📊 STEP 2: AVAILABLE AZURE SUBSCRIPTIONS")
    print("=" * 60)
    
    subscriptions = get_azure_subscriptions()
    if not subscriptions:
        print("❌ No Azure subscriptions found or accessible.")
        return
    
    print(f"✅ Found {len(subscriptions)} enabled subscriptions:")
    for i, sub in enumerate(subscriptions, 1):
        print(f"  {i}. {sub['name']} ({sub['id']})")
    
    # Select subscription
    if len(subscriptions) == 1:
        selected_sub = subscriptions[0]
        print(f"\n🎯 Auto-selected: {selected_sub['name']}")
    else:
        while True:
            try:
                choice = input(f"\n🎯 Select subscription (1-{len(subscriptions)}): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(subscriptions):
                    selected_sub = subscriptions[int(choice) - 1]
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
            except KeyboardInterrupt:
                print("\n⏹️  Demo interrupted by user.")
                return
    
    subscription_id = selected_sub['id']
    print(f"✅ Selected: {selected_sub['name']} ({subscription_id})")

    input("⏸️  Press Enter to continue...")

    # Step 3: Fetch Real Azure Emissions Data
    print(f"\n📊 STEP 3: FETCHING REAL AZURE EMISSIONS DATA")
    print("=" * 60)
    
    # Calculate appropriate date range (Azure Carbon API requires dates within available range)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    
    print(f"📅 Date range: {start_date} to {end_date}")
    print("🌍 Fetching monthly summary emissions data...")
    
    # Fetch monthly summary
    cmd = f"python -m src.esg_reporting.cli azure fetch --subscription-id {subscription_id} --report-type monthly_summary --start-date {start_date} --end-date {end_date} --output real_azure_emissions.csv"
    success, output = run_command(cmd, "Fetching Azure emissions data")
    
    if not success:
        print("❌ Failed to fetch emissions data. This might be due to:")
        print("  • Date range outside available data (try 2024-04-01 to 2024-12-31)")
        print("  • Insufficient permissions for Carbon Optimization API")
        print("  • Subscription has no emissions data available")
        return

    # Check if data file was created
    if os.path.exists("real_azure_emissions.csv"):
        with open("real_azure_emissions.csv", 'r') as f:
            lines = f.readlines()
        print(f"✅ Retrieved {len(lines)-1} emissions records")
        
        if len(lines) > 1:
            print("\n📋 Sample data (first 3 lines):")
            for i, line in enumerate(lines[:3]):
                if i == 0:
                    print(f"   Header: {line.strip()}")
                else:
                    print(f"   Row {i}: {line.strip()}")

    input("⏸️  Press Enter to continue...")

    # Step 4: Fetch Overall Summary
    print(f"\n📊 STEP 4: FETCHING OVERALL SUMMARY DATA")
    print("=" * 60)
    
    cmd = f"python -m src.esg_reporting.cli azure fetch --subscription-id {subscription_id} --report-type overall_summary --start-date {start_date} --end-date {end_date} --output real_azure_overall.csv"
    success, output = run_command(cmd, "Fetching overall summary data")
    
    if success and os.path.exists("real_azure_overall.csv"):
        with open("real_azure_overall.csv", 'r') as f:
            content = f.read()
        print(f"✅ Overall summary data retrieved:")
        print(content)

    input("⏸️  Press Enter to continue...")

    # Step 5: Integration with ESG Data
    print(f"\n📊 STEP 5: INTEGRATING WITH ESG DATA")
    print("=" * 60)
    
    if os.path.exists("real_azure_emissions.csv") and os.path.exists("sample_activities.csv"):
        cmd = f"python -m src.esg_reporting.cli azure integrate --emissions-file real_azure_emissions.csv --activities-file sample_activities.csv --output-dir real_integration_output --subscription-id {subscription_id}"
        success, output = run_command(cmd, "Integrating Azure data with ESG activities")
        
        if success:
            # List generated files
            if os.path.exists("real_integration_output"):
                files = os.listdir("real_integration_output")
                print(f"\n✅ Integration complete! Generated files:")
                for file in files:
                    file_path = os.path.join("real_integration_output", file)
                    size = os.path.getsize(file_path)
                    print(f"  📄 {file} ({size} bytes)")

    input("⏸️  Press Enter to continue...")

    # Step 6: Validation and Analysis
    print(f"\n📊 STEP 6: DATA VALIDATION AND ANALYSIS")
    print("=" * 60)
    
    if os.path.exists("real_azure_emissions.csv"):
        cmd = f"python -m src.esg_reporting.cli process real_azure_emissions.csv --validate --output validated_azure_data.csv"
        success, output = run_command(cmd, "Validating Azure emissions data")

    # Step 7: Upload to Azure Storage (if configured)
    print(f"\n📊 STEP 7: AZURE STORAGE UPLOAD (OPTIONAL)")
    print("=" * 60)
    
    print("💾 Note: Azure Blob Storage upload requires proper configuration.")
    print("   Configure storage settings in your environment or config file.")
    
    if os.path.exists("real_azure_emissions.csv"):
        print("\n🔄 Attempting to upload to Azure Storage...")
        cmd = f"python -m src.esg_reporting.cli upload real_azure_emissions.csv --container esg-data --blob-name azure-emissions-{datetime.now().strftime('%Y%m%d')}.csv"
        run_command(cmd, "Uploading to Azure Blob Storage")

    # Summary
    print(f"\n📊 DEMO SUMMARY")
    print("=" * 60)
    print("🎉 Real Azure Carbon Optimization Demo Complete!")
    print("\n✅ Demonstrated capabilities:")
    print("  🔐 Azure authentication and subscription access")
    print("  🌍 Real emissions data fetching from Azure Carbon API")
    print("  📊 Multiple report types (monthly, overall summary)")
    print("  🔄 Data integration with existing ESG workflows")
    print("  ✅ Data validation and processing")
    print("  ☁️ Azure storage upload capabilities")
    
    print(f"\n📁 Generated files:")
    for filename in ["real_azure_emissions.csv", "real_azure_overall.csv", "validated_azure_data.csv"]:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  📄 {filename} ({size} bytes)")
    
    if os.path.exists("real_integration_output"):
        files = os.listdir("real_integration_output")
        for file in files:
            file_path = os.path.join("real_integration_output", file)
            size = os.path.getsize(file_path)
            print(f"  📄 real_integration_output/{file} ({size} bytes)")
    
    print(f"\n🚀 Next Steps:")
    print("  1. Analyze the retrieved emissions data")
    print("  2. Set up automated data pipelines")
    print("  3. Create Power BI dashboards")
    print("  4. Implement monitoring and alerting")
    print("  5. Integrate with compliance reporting workflows")
    
    print(f"\n🌍 Your Azure infrastructure emissions data is now accessible!")
    print("Thank you for using the ESG Reporting Solution! 🌱")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user. Thank you!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please check your Azure authentication and try again.")
