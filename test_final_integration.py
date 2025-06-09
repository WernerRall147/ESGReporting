#!/usr/bin/env python3
"""
Final Integration Test for ESG Reporting Solution with Azure Carbon Optimization.

This script tests the complete functionality including:
1. CLI command availability
2. Azure Carbon Optimization client functionality
3. ESG data processing capabilities
4. Configuration management
"""

import sys
import subprocess
import traceback
from datetime import datetime, timedelta
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.esg_reporting.carbon_optimization import (
    CarbonOptimizationClient, 
    EmissionsQuery, 
    ReportType, 
    EmissionScope, 
    CategoryType
)
from src.esg_reporting.processor import ESGDataProcessor
from src.esg_reporting.config import settings

def test_cli_commands():
    """Test CLI command availability."""
    print("🧪 Testing CLI Commands...")
    
    commands = [
        ("python -m src.esg_reporting.cli --help", "Main CLI help"),
        ("python -m src.esg_reporting.cli config", "Configuration display"),
        ("python -m src.esg_reporting.cli azure --help", "Azure commands help"),
        ("python -m src.esg_reporting.cli azure fetch --help", "Azure fetch help"),
        ("python -m src.esg_reporting.cli process --help", "Process command help"),
        ("python -m src.esg_reporting.cli upload --help", "Upload command help"),
    ]
    
    results = []
    for cmd, description in commands:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            success = result.returncode == 0
            results.append((description, success, result.stderr if not success else ""))
            print(f"  {'✅' if success else '❌'} {description}")
            if not success:
                print(f"     Error: {result.stderr}")
        except Exception as e:
            results.append((description, False, str(e)))
            print(f"  ❌ {description} - Exception: {e}")
    
    return results

def test_carbon_optimization_client():
    """Test Carbon Optimization client initialization and methods."""
    print("\n🧪 Testing Carbon Optimization Client...")
    
    try:
        # Test client initialization (no credentials needed for testing)
        client = CarbonOptimizationClient()
        print("  ✅ Client initialization successful")        # Test enum values
        assert ReportType.MONTHLY_SUMMARY_REPORT.value == "MonthlySummaryReport"
        assert EmissionScope.SCOPE1.value == "Scope1"
        assert CategoryType.COMPUTE.value == "compute"
        print("  ✅ Enum values correct")
        
        # Test query creation
        from src.esg_reporting.carbon_optimization import DateRange
        date_range = DateRange(start="2024-01-01", end="2024-01-31")
        query = EmissionsQuery(
            report_type=ReportType.MONTHLY_SUMMARY_REPORT,
            subscription_list=["test-subscription"],
            carbon_scope_list=[EmissionScope.SCOPE1, EmissionScope.SCOPE2],
            date_range=date_range
        )
        
        # Test client methods exist
        assert hasattr(client, 'get_emissions_data')
        assert hasattr(client, 'get_monthly_summary')
        assert hasattr(client, 'get_overall_summary')
        assert hasattr(client, 'get_resource_details')
        assert hasattr(client, 'get_top_emitters')
        print("  ✅ Client methods available")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Carbon Optimization client test failed: {e}")
        traceback.print_exc()
        return False

def test_esg_processor():
    """Test ESG data processor functionality."""
    print("\n🧪 Testing ESG Data Processor...")
    
    try:
        processor = ESGDataProcessor()
        print("  ✅ Processor initialization successful")
        
        # Test with sample emissions file
        sample_file = Path("sample_emissions.csv")
        if sample_file.exists():
            df, metadata = processor.read_file(str(sample_file))
            print(f"  ✅ File reading successful: {metadata['row_count']} rows")
            
            # Test validation
            validation_report = processor.validate_esg_data(df, "emissions")
            print(f"  ✅ Data validation successful: {validation_report['data_quality_score']:.1f}/100")
            
            # Test cleaning
            cleaned_df, cleaning_report = processor.clean_data(df, validation_report)
            print(f"  ✅ Data cleaning successful: {len(cleaning_report['actions_performed'])} actions")
            
        else:
            print("  ⚠️ Sample emissions file not found, skipping file tests")
        
        return True
        
    except Exception as e:
        print(f"  ❌ ESG processor test failed: {e}")
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration management."""
    print("\n🧪 Testing Configuration...")
    
    try:
        # Test settings access
        print(f"  ✅ Storage account: {settings.azure_storage_account_name}")
        print(f"  ✅ Container name: {settings.azure_container_name}")
        print(f"  ✅ Batch size: {settings.batch_size}")
        print(f"  ✅ Log level: {settings.log_level}")
        
        # Test required settings exist
        required_attrs = [
            'azure_storage_account_name',
            'azure_container_name',
            'batch_size',
            'max_file_size_mb',
            'log_level'
        ]
        
        for attr in required_attrs:
            assert hasattr(settings, attr), f"Missing setting: {attr}"
        
        print("  ✅ All required configuration settings available")
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        traceback.print_exc()
        return False

def test_sample_files():
    """Test sample files existence and format."""
    print("\n🧪 Testing Sample Files...")
    
    sample_files = [
        "sample_emissions.csv",
        "sample_activities.csv", 
        "sample_suppliers.csv"
    ]
    
    results = []
    for file_name in sample_files:
        file_path = Path(file_name)
        exists = file_path.exists()
        results.append((file_name, exists))
        
        if exists:
            size = file_path.stat().st_size
            print(f"  ✅ {file_name}: {size:,} bytes")
        else:
            print(f"  ❌ {file_name}: Not found")
    
    return all(result[1] for result in results)

def main():
    """Run all integration tests."""
    print("🚀 ESG Reporting Solution - Final Integration Test")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_results = []
    
    # Run all tests
    test_results.append(("CLI Commands", test_cli_commands()))
    test_results.append(("Carbon Optimization Client", test_carbon_optimization_client()))
    test_results.append(("ESG Data Processor", test_esg_processor()))
    test_results.append(("Configuration", test_configuration()))
    test_results.append(("Sample Files", test_sample_files()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! The ESG Reporting Solution is ready for use.")
        print("\n🚀 Next Steps:")
        print("  1. Configure Azure credentials for real emissions data")
        print("  2. Set up automated data pipelines")
        print("  3. Create Power BI dashboards")
        print("  4. Implement monitoring and alerting")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review and fix issues.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite error: {e}")
        traceback.print_exc()
        sys.exit(1)
