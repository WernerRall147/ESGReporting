#!/usr/bin/env python3
"""
Azure Carbon Optimization API - Working Example with Valid Date Range

This script demonstrates successfully fetching real Azure emissions data
using the correct date range that the API supports.
"""

import os
import sys
import logging
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from esg_reporting.carbon_optimization import (
    CarbonOptimizationClient, EmissionsQuery, DateRange, 
    ReportType, EmissionScope
)

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_with_valid_date_range():
    """Test with the valid date range supported by the API"""
    print("🎯 Testing Azure Carbon Optimization API with Valid Date Range")
    print("=" * 65)
    
    # Use the valid date range from the API error message
    start_date = "2024-04-01"  # API minimum date
    end_date = "2025-04-01"    # API maximum date
    subscription_id = "6690c42b-73e0-437c-92f6-a4161424f2a3"  # Management subscription
    
    print(f"📅 Using API-supported date range: {start_date} to {end_date}")
    print(f"📊 Subscription: {subscription_id}")
    
    try:
        # Initialize client
        client = CarbonOptimizationClient()
        print("✅ Client initialized successfully")
        
        # Test OverallSummaryReport
        print(f"\n🔍 Testing OverallSummaryReport...")
        query = EmissionsQuery(
            report_type=ReportType.OVERALL_SUMMARY_REPORT,
            date_range=DateRange(start=start_date, end=end_date),
            subscription_list=[subscription_id],
            carbon_scope_list=[EmissionScope.SCOPE1, EmissionScope.SCOPE2]
        )
        
        result_df = client.get_emissions_data(query)
        
        if result_df is not None and not result_df.empty:
            print(f"🎉 SUCCESS! Retrieved {len(result_df)} emissions records")
            print("\n📊 Sample data:")
            print(result_df.head().to_string())
            
            # Save the data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'real_azure_emissions_{timestamp}.csv'
            result_df.to_csv(output_file, index=False)
            print(f"\n💾 Saved real Azure emissions data to: {output_file}")
            
            return output_file
        else:
            print("⚠️ API call succeeded but returned no data")
            
            # Try with a shorter, more recent range
            print(f"\n🔍 Trying shorter date range within API limits...")
            recent_start = "2024-10-01"
            recent_end = "2025-01-01"
            print(f"📅 Testing range: {recent_start} to {recent_end}")
            
            query = EmissionsQuery(
                report_type=ReportType.OVERALL_SUMMARY_REPORT,
                date_range=DateRange(start=recent_start, end=recent_end),
                subscription_list=[subscription_id],
                carbon_scope_list=[EmissionScope.SCOPE1, EmissionScope.SCOPE2]
            )
            
            result_df = client.get_emissions_data(query)
            
            if result_df is not None and not result_df.empty:
                print(f"🎉 SUCCESS! Retrieved {len(result_df)} emissions records")
                print("\n📊 Sample data:")
                print(result_df.head().to_string())
                
                # Save the data
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = f'real_azure_emissions_{timestamp}.csv'
                result_df.to_csv(output_file, index=False)
                print(f"\n💾 Saved real Azure emissions data to: {output_file}")
                
                return output_file
            else:
                print("⚠️ No data found in shorter range either")
                return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_monthly_summary():
    """Test monthly summary report"""
    print(f"\n🔍 Testing MonthlySummaryReport...")
    
    try:
        client = CarbonOptimizationClient()
        
        # Use valid date range
        start_date = "2024-10-01"
        end_date = "2024-12-31"
        subscription_id = "6690c42b-73e0-437c-92f6-a4161424f2a3"
        
        query = EmissionsQuery(
            report_type=ReportType.MONTHLY_SUMMARY_REPORT,
            date_range=DateRange(start=start_date, end=end_date),
            subscription_list=[subscription_id],
            carbon_scope_list=[EmissionScope.SCOPE1, EmissionScope.SCOPE2]
        )
        
        result_df = client.get_emissions_data(query)
        
        if result_df is not None and not result_df.empty:
            print(f"🎉 Monthly Summary SUCCESS! Retrieved {len(result_df)} records")
            print("\n📊 Monthly data sample:")
            print(result_df.head().to_string())
            
            # Save the data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'monthly_azure_emissions_{timestamp}.csv'
            result_df.to_csv(output_file, index=False)
            print(f"\n💾 Saved monthly Azure emissions data to: {output_file}")
            
            return output_file
        else:
            print("⚠️ No monthly data found")
            return None
            
    except Exception as e:
        print(f"❌ Monthly summary error: {e}")
        return None

def main():
    """Run the corrected Azure emissions data test"""
    
    print("🚀 Azure Carbon Optimization - Fixed Date Range Test")
    print("This test uses the correct date range supported by the API")
    print()
    
    # Test overall summary
    overall_file = test_with_valid_date_range()
    
    # Test monthly summary
    monthly_file = test_monthly_summary()
    
    if overall_file or monthly_file:
        print(f"\n🎉 SUCCESS: Real Azure emissions data retrieved!")
        print(f"📁 Files generated:")
        if overall_file:
            print(f"   - Overall Summary: {overall_file}")
        if monthly_file:
            print(f"   - Monthly Summary: {monthly_file}")
        
        print(f"\n✅ Azure Carbon Optimization API is working correctly!")
        print(f"🔧 The issue was using dates outside the API's supported range")
        print(f"📅 Supported range: 2024-04-01 to 2025-04-01")
        
        return True
    else:
        print(f"\n❓ No emissions data found")
        print(f"💡 This might be because:")
        print(f"   - The subscription has no Azure resources generating emissions")
        print(f"   - No resources were active during the tested date ranges")
        print(f"   - Carbon Optimization tracking wasn't enabled")
        
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n🏁 Test result: {'SUCCESS' if success else 'NO DATA'}")
