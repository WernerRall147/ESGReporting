#!/usr/bin/env python3
"""
Simple Demo Script for ESG Reporting Solution with Azure Carbon Optimization Integration

This demo showcases the core functionality of the ESG Reporting solution
without requiring Azure credentials or real Azure emissions data.
"""

import sys
import os
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and show results"""
    print(f"\n🔄 {description}")
    print(f"💻 Command: {command}")
    print("📋 Output:")
    print("-" * 40)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=Path.cwd())
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

def show_file_sample(file_path, max_lines=5):
    """Show a sample of file content"""
    try:
        if Path(file_path).exists():
            print(f"📄 Sample from {file_path}:")
            with open(file_path, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:max_lines]):
                    print(f"  {i+1}: {line.strip()}")
                if len(lines) > max_lines:
                    print(f"  ... ({len(lines) - max_lines} more lines)")
        else:
            print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def main():
    print("="*80)
    print("🌍 ESG REPORTING SOLUTION - SIMPLE DEMO")
    print("="*80)
    print("🌍 Welcome to the ESG Reporting Solution Demo!")
    print("This demonstration showcases our Azure-integrated ESG data management platform.")
    print()
    
    # Step 1: Show CLI help
    print("📊 STEP 1: CLI OVERVIEW")
    print("="*60)
    run_command("python -m src.esg_reporting.cli --help", "Show main CLI help")
    
    # Step 2: Show Azure commands
    print("\n📊 STEP 2: AZURE CARBON OPTIMIZATION INTEGRATION")
    print("="*60)
    run_command("python -m src.esg_reporting.cli azure --help", "Show Azure integration commands")
    
    # Step 3: Sample data overview
    print("\n📊 STEP 3: SAMPLE ESG DATA")
    print("="*60)
    print("📋 Sample data files included in this demo:")
    
    sample_files = [
        "sample_emissions.csv",
        "sample_activities.csv", 
        "sample_suppliers.csv"
    ]
    
    for file_path in sample_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
            show_file_sample(file_path, 3)
            print()
        else:
            print(f"❌ {file_path} not found")
    
    # Step 4: Demonstrate data processing
    print("\n📊 STEP 4: DATA PROCESSING EXAMPLES")
    print("="*60)
    run_command("python -m src.esg_reporting.cli process --help", "Show data processing options")
    
    # Step 5: Configuration
    print("\n📊 STEP 5: CONFIGURATION")
    print("="*60)
    run_command("python -m src.esg_reporting.cli config", "Show current configuration")
    
    # Step 6: Demo Azure fetch command structure
    print("\n📊 STEP 6: AZURE EMISSIONS INTEGRATION")
    print("="*60)
    run_command("python -m src.esg_reporting.cli azure fetch --help", "Show Azure fetch command options")
    
    print("\n🎯 EXAMPLE USAGE:")
    print("To fetch real Azure emissions data (requires Azure credentials):")
    print("python -m src.esg_reporting.cli azure fetch \\")
    print("  --subscription-id YOUR_SUBSCRIPTION_ID \\")
    print("  --tenant-id YOUR_TENANT_ID \\")
    print("  --client-id YOUR_CLIENT_ID \\")
    print("  --client-secret YOUR_CLIENT_SECRET \\")
    print("  --report-type monthly_summary \\")
    print("  --output azure_emissions.csv")
    
    print("\nTo integrate emissions with ESG reporting:")
    print("python -m src.esg_reporting.cli azure integrate \\")
    print("  --emissions-file azure_emissions.csv \\")
    print("  --activities-file sample_activities.csv \\")
    print("  --output-dir reports/")
    
    print("\n📈 KEY FEATURES DEMONSTRATED:")
    print("✅ CLI-based ESG data management")
    print("✅ Azure Carbon Optimization integration")
    print("✅ Real-time emissions data fetching")
    print("✅ Data processing and validation")
    print("✅ Integrated reporting capabilities")
    print("✅ Azure best practices implementation")
    
    print("\n💼 BUSINESS VALUE:")
    print("🔹 Automated ESG data collection from Azure infrastructure")
    print("🔹 Real-time carbon emissions tracking")
    print("🔹 Unified ESG reporting across multiple data sources")
    print("🔹 Compliance-ready reporting for sustainability initiatives")
    print("🔹 Cost optimization through emissions monitoring")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Configure Azure credentials (service principal or managed identity)")
    print("2. Test with your Azure subscription using 'azure fetch' command")
    print("3. Integrate with your existing ESG data workflows")
    print("4. Set up automated reporting schedules")
    print("5. Deploy to Azure Container Apps for production use")
    
    print("\n" + "="*80)
    print("🎉 Demo completed! Thank you for exploring the ESG Reporting Solution.")
    print("="*80)

if __name__ == "__main__":
    main()
