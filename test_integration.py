"""
Test script to verify the ESG Reporting solution integration.

This script tests the core functionality without requiring full Azure setup.
"""

import os
import sys
import traceback
from pathlib import Path

def test_imports():
    """Test that all modules can be imported successfully."""
    print("🔄 Testing module imports...")
    
    try:
        from src.esg_reporting import config, processor, storage, carbon_optimization, cli
        print("✅ All core modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_carbon_optimization_client():
    """Test the Carbon Optimization client initialization."""
    print("\n🔄 Testing Carbon Optimization client...")
    
    try:
        from src.esg_reporting.carbon_optimization import (
            CarbonOptimizationClient, EmissionsQuery, ReportType, EmissionScope
        )
        
        # Test client initialization (won't authenticate without real credentials)
        client = CarbonOptimizationClient(
            subscription_id="test-sub-id",
            tenant_id="test-tenant-id", 
            client_id="test-client-id",
            client_secret="test-secret"
        )
        
        # Test query creation
        query = EmissionsQuery(
            start_date="2024-01-01",
            end_date="2024-12-31",
            emission_scopes=[EmissionScope.SCOPE1, EmissionScope.SCOPE2]
        )
        
        print("✅ Carbon Optimization client initialization successful")
        return True
    except Exception as e:
        print(f"❌ Carbon Optimization client error: {e}")
        traceback.print_exc()
        return False

def test_processor():
    """Test the ESG data processor with sample data."""
    print("\n🔄 Testing ESG data processor...")
    
    try:
        from src.esg_reporting.processor import ESGDataProcessor
        
        processor = ESGDataProcessor()
        
        # Test with sample emissions file if it exists
        if os.path.exists("sample_emissions.csv"):
            df, metadata = processor.read_file("sample_emissions.csv")
            print(f"✅ Sample data loaded: {metadata['row_count']} rows, {metadata['column_count']} columns")
            
            # Test validation
            validation_report = processor.validate_esg_data(df, "emissions")
            print(f"✅ Data validation completed. Quality score: {validation_report['data_quality_score']:.1f}/100")
            
        else:
            print("⚠️ Sample emissions file not found, skipping file processing test")
        
        print("✅ ESG data processor tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Processor error: {e}")
        traceback.print_exc()
        return False

def test_cli_help():
    """Test that CLI help commands work."""
    print("\n🔄 Testing CLI help commands...")
    
    try:
        import subprocess
        
        # Test main CLI help
        result = subprocess.run([
            sys.executable, "-m", "src.esg_reporting.cli", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and "ESG Reporting CLI" in result.stdout:
            print("✅ Main CLI help command works")
        else:
            print(f"❌ Main CLI help failed: {result.stderr}")
            return False
        
        # Test Azure subcommand help
        result = subprocess.run([
            sys.executable, "-m", "src.esg_reporting.cli", "azure", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and "Azure Carbon Optimization" in result.stdout:
            print("✅ Azure CLI help command works")
        else:
            print(f"❌ Azure CLI help failed: {result.stderr}")
            return False
        
        print("✅ CLI help commands test completed")
        return True
        
    except Exception as e:
        print(f"❌ CLI help test error: {e}")
        traceback.print_exc()
        return False

def test_sample_data():
    """Test that sample data files exist and are readable."""
    print("\n🔄 Testing sample data files...")
    
    sample_files = [
        "sample_emissions.csv",
        "sample_activities.csv", 
        "sample_suppliers.csv"
    ]
    
    all_exist = True
    for file_path in sample_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} exists ({size:,} bytes)")
        else:
            print(f"❌ {file_path} not found")
            all_exist = False
    
    return all_exist

def main():
    """Run all integration tests."""
    print("=" * 80)
    print("🧪 ESG REPORTING SOLUTION - INTEGRATION TESTS")
    print("=" * 80)
    
    tests = [
        ("Module Imports", test_imports),
        ("Carbon Optimization Client", test_carbon_optimization_client),
        ("ESG Data Processor", test_processor),
        ("CLI Help Commands", test_cli_help),
        ("Sample Data Files", test_sample_data)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! The integration is ready for use.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
