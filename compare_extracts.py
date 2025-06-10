#!/usr/bin/env python3
"""
Comparison script to analyze Azure portal extracts vs API data
"""

import pandas as pd
import os
from pathlib import Path

def analyze_portal_extracts():
    """Analyze the Azure portal extract files"""
    extract_dir = Path("AzureExtracts")
    
    print("🔍 ANALYZING AZURE PORTAL EXTRACTS")
    print("=" * 50)
    
    if not extract_dir.exists():
        print("❌ AzureExtracts directory not found")
        return
    
    extract_files = list(extract_dir.glob("*.csv"))
    
    if not extract_files:
        print("❌ No CSV files found in AzureExtracts directory")
        return
    
    print(f"📁 Found {len(extract_files)} extract files:")
    
    for file_path in extract_files:
        print(f"\n📋 Analyzing: {file_path.name}")
        print("-" * 30)
        
        try:
            df = pd.read_csv(file_path)
            print(f"   📊 Rows: {len(df)}")
            print(f"   📊 Columns: {len(df.columns)}")
            print(f"   📊 Columns: {list(df.columns)}")
            
            if len(df) > 0:
                print(f"   📊 Sample data:")
                print(f"   {df.head(2).to_string()}")
                
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")

def analyze_api_data():
    """Analyze the API-generated data files"""
    print("\n🔍 ANALYZING API-GENERATED DATA")
    print("=" * 50)
    
    # Look for recent API output files
    api_files = [
        "azure_emissions_final_demo_20250610_120405.csv",
        "real_azure_emissions_20250610_114601.csv",
        "overall_emissions.csv"
    ]
    
    for file_name in api_files:
        if os.path.exists(file_name):
            print(f"\n📋 Analyzing: {file_name}")
            print("-" * 30)
            
            try:
                df = pd.read_csv(file_name)
                print(f"   📊 Rows: {len(df)}")
                print(f"   📊 Columns: {len(df.columns)}")
                print(f"   📊 Columns: {list(df.columns)}")
                
                if len(df) > 0:
                    print(f"   📊 Sample data:")
                    print(f"   {df.head(2).to_string()}")
                    
            except Exception as e:
                print(f"   ❌ Error reading file: {e}")

def test_current_api():
    """Test current API to get fresh data"""
    print("\n🧪 TESTING CURRENT API")
    print("=" * 50)
    
    try:
        import sys
        sys.path.insert(0, 'src')
        
        from esg_reporting.carbon_optimization import (
            CarbonOptimizationClient, EmissionsQuery, DateRange, 
            ReportType, EmissionScope
        )
        
        print("📡 Initializing API client...")
        client = CarbonOptimizationClient()
        
        print("📊 Creating query...")
        query = EmissionsQuery(
            report_type=ReportType.OVERALL_SUMMARY_REPORT,
            date_range=DateRange(start='2024-10-01', end='2024-12-31'),
            subscription_list=['6690c42b-73e0-437c-92f6-a4161424f2a3'],
            carbon_scope_list=[EmissionScope.SCOPE1, EmissionScope.SCOPE2]
        )
        
        print("🔄 Fetching data...")
        df = client.get_emissions_data(query)
        
        if df is not None and not df.empty:
            print(f"✅ Retrieved {len(df)} records")
            print(f"📊 Columns: {list(df.columns)}")
            print(f"📊 Sample data:")
            print(df.to_string())
            
            # Save for comparison
            df.to_csv("current_api_test.csv", index=False)
            print("💾 Saved to current_api_test.csv")
        else:
            print("❌ No data retrieved")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    print("🚀 AZURE EMISSIONS DATA COMPARISON")
    print("=" * 60)
    
    analyze_portal_extracts()
    analyze_api_data()
    test_current_api()
    
    print("\n✅ COMPARISON COMPLETE")
