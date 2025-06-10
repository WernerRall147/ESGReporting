#!/usr/bin/env python3
"""
Azure Carbon Optimization API Test Script

This script tests the Azure Carbon Optimization API connection step by step
to identify and resolve any authentication or API issues.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from esg_reporting.carbon_optimization import (
    CarbonOptimizationClient, EmissionsQuery, DateRange, 
    ReportType, EmissionScope
)

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_authentication():
    """Test Azure authentication"""
    print("🔐 Testing Azure Authentication...")
    
    try:
        from azure.identity import DefaultAzureCredential
        
        # Test getting a token
        credential = DefaultAzureCredential()
        
        # Try to get a token for the Azure management scope
        token = credential.get_token("https://management.azure.com/.default")
        print(f"✅ Successfully obtained Azure token")
        print(f"   Token expires at: {datetime.fromtimestamp(token.expires_on)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

def test_client_initialization():
    """Test Carbon Optimization client initialization"""
    print("\n🏗️ Testing Carbon Optimization Client Initialization...")
    
    try:
        client = CarbonOptimizationClient()
        print("✅ Client initialized successfully")
        return client
        
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return None

def test_simple_api_call(client, subscription_id):
    """Test a simple API call with minimal parameters"""
    print(f"\n📞 Testing Simple API Call for subscription: {subscription_id}")
    
    try:
        # Use a very recent date range (last month)
        end_date = datetime.now()
        start_date = end_date.replace(day=1)  # First day of current month
        
        # Create a simple query
        query = EmissionsQuery(
            report_type=ReportType.OVERALL_SUMMARY_REPORT,
            date_range=DateRange(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d')
            ),
            subscription_list=[subscription_id],
            carbon_scope_list=[EmissionScope.SCOPE1, EmissionScope.SCOPE2]
        )
        
        print(f"📅 Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"📊 Report type: {query.report_type.value}")
        print(f"🔍 Scopes: {[scope.value for scope in query.carbon_scope_list]}")
        
        # Make the API call
        print("\n🌐 Making API call...")
        result_df = client.get_emissions_data(query)
        
        if result_df is not None and not result_df.empty:
            print(f"✅ Successfully retrieved {len(result_df)} emissions records!")
            print("\n📊 Sample data:")
            print(result_df.head().to_string())
            return result_df
        else:
            print("⚠️ API call succeeded but returned no data")
            print("   This might be because:")
            print("   - No emissions data exists for the specified date range")
            print("   - No resources were active in the subscription during this period")
            return None
            
    except Exception as e:
        print(f"❌ API call failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # If it's a specific Azure error, provide more details
        if hasattr(e, 'response'):
            print(f"   HTTP Status: {e.response.status_code if hasattr(e.response, 'status_code') else 'Unknown'}")
            print(f"   Response: {e.response.text if hasattr(e.response, 'text') else 'No response text'}")
        
        return None

def test_different_date_ranges(client, subscription_id):
    """Test different date ranges to find data"""
    print(f"\n📅 Testing Different Date Ranges for subscription: {subscription_id}")
    
    # Test various date ranges
    test_ranges = [
        ("Last 30 days", timedelta(days=30)),
        ("Last 90 days", timedelta(days=90)),
        ("Last 6 months", timedelta(days=180)),
        ("Last year", timedelta(days=365))
    ]
    
    for range_name, delta in test_ranges:
        try:
            end_date = datetime.now()
            start_date = end_date - delta
            
            print(f"\n🔍 Testing {range_name}: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
            query = EmissionsQuery(
                report_type=ReportType.OVERALL_SUMMARY_REPORT,
                date_range=DateRange(
                    start=start_date.strftime('%Y-%m-%d'),
                    end=end_date.strftime('%Y-%m-%d')
                ),
                subscription_list=[subscription_id],
                carbon_scope_list=[EmissionScope.SCOPE1, EmissionScope.SCOPE2]
            )
            
            result_df = client.get_emissions_data(query)
            
            if result_df is not None and not result_df.empty:
                print(f"✅ Found {len(result_df)} records for {range_name}")
                return result_df
            else:
                print(f"⚠️ No data found for {range_name}")
                
        except Exception as e:
            print(f"❌ Error testing {range_name}: {e}")
    
    return None

def test_different_report_types(client, subscription_id):
    """Test different report types"""
    print(f"\n📋 Testing Different Report Types for subscription: {subscription_id}")
    
    # Use last 6 months for testing
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    report_types = [
        ReportType.OVERALL_SUMMARY_REPORT,
        ReportType.MONTHLY_SUMMARY_REPORT
    ]
    
    for report_type in report_types:
        try:
            print(f"\n🔍 Testing {report_type.value}...")
            
            query = EmissionsQuery(
                report_type=report_type,
                date_range=DateRange(
                    start=start_date.strftime('%Y-%m-%d'),
                    end=end_date.strftime('%Y-%m-%d')
                ),
                subscription_list=[subscription_id],
                carbon_scope_list=[EmissionScope.SCOPE1, EmissionScope.SCOPE2]
            )
            
            result_df = client.get_emissions_data(query)
            
            if result_df is not None and not result_df.empty:
                print(f"✅ {report_type.value} returned {len(result_df)} records")
                return result_df
            else:
                print(f"⚠️ {report_type.value} returned no data")
                
        except Exception as e:
            print(f"❌ Error with {report_type.value}: {e}")
    
    return None

def test_subscription_permissions(subscription_id):
    """Test if we have proper permissions on the subscription"""
    print(f"\n🔑 Testing Subscription Permissions for: {subscription_id}")
    
    try:
        import subprocess
        
        # Test basic subscription access
        result = subprocess.run(
            ['az', 'account', 'show', '--subscription', subscription_id, '--output', 'json'],
            capture_output=True,
            text=True,
            check=True,
            shell=True
        )
        
        sub_info = json.loads(result.stdout)
        print(f"✅ Subscription access confirmed")
        print(f"   Name: {sub_info.get('name', 'N/A')}")
        print(f"   State: {sub_info.get('state', 'N/A')}")
        
        # Test if we can list resources (basic permission test)
        result = subprocess.run(
            ['az', 'resource', 'list', '--subscription', subscription_id, '--output', 'json', '--query', '[0:5]'],
            capture_output=True,
            text=True,
            shell=True
        )
        
        if result.returncode == 0:
            resources = json.loads(result.stdout)
            print(f"✅ Can list resources: {len(resources)} sample resources found")
            return True
        else:
            print(f"⚠️ Cannot list resources: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Permission test failed: {e}")
        return False

def main():
    """Run comprehensive Azure Carbon Optimization API tests"""
    print("🧪 Azure Carbon Optimization API - Comprehensive Test")
    print("=" * 60)
    
    # Get default subscription ID
    subscription_id = "6690c42b-73e0-437c-92f6-a4161424f2a3"  # Management subscription
    
    # Step 1: Test authentication
    if not test_authentication():
        print("\n❌ Authentication failed. Please run 'az login' first.")
        return False
    
    # Step 2: Test subscription permissions
    if not test_subscription_permissions(subscription_id):
        print(f"\n⚠️ Limited permissions on subscription {subscription_id}")
    
    # Step 3: Test client initialization
    client = test_client_initialization()
    if not client:
        return False
    
    # Step 4: Test simple API call
    result = test_simple_api_call(client, subscription_id)
    if result is not None:
        print("\n🎉 SUCCESS: Found emissions data!")
        return True
    
    # Step 5: Test different date ranges
    result = test_different_date_ranges(client, subscription_id)
    if result is not None:
        print("\n🎉 SUCCESS: Found emissions data with different date range!")
        return True
    
    # Step 6: Test different report types
    result = test_different_report_types(client, subscription_id)
    if result is not None:
        print("\n🎉 SUCCESS: Found emissions data with different report type!")
        return True
    
    # If we get here, no data was found
    print("\n❓ No emissions data found in any test")
    print("📋 Possible reasons:")
    print("   1. The subscription has no Azure resources generating emissions")
    print("   2. Carbon Optimization data is not available for this subscription")
    print("   3. The subscription is in a region where Carbon Optimization is not available")
    print("   4. There's no historical data for the tested date ranges")
    print("   5. The account lacks specific Carbon Optimization permissions")
    
    print("\n💡 Recommendations:")
    print("   1. Try with a subscription that has active Azure resources")
    print("   2. Ensure Carbon Optimization is enabled in your Azure region")
    print("   3. Check if your account has 'Carbon Optimization Reader' permissions")
    print("   4. Try with a subscription that has been active for several months")
    
    return False

if __name__ == "__main__":
    success = main()
    print(f"\n🏁 Test completed: {'SUCCESS' if success else 'NO DATA FOUND'}")
