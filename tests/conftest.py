"""
Test configuration and fixtures.
"""

import pytest
import tempfile
import pandas as pd
from pathlib import Path


@pytest.fixture
def sample_csv_file():
    """Create a sample CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        # Write sample ESG emissions data
        f.write("date,scope,activity,co2_equivalent,unit\n")
        f.write("2024-01-01,Scope 1,Electricity,100.5,kg CO2e\n")
        f.write("2024-01-02,Scope 2,Gas,75.2,kg CO2e\n")
        f.write("2024-01-03,Scope 3,Transportation,250.0,kg CO2e\n")
        f.write("2024-01-04,Scope 1,,50.0,kg CO2e\n")  # Missing activity
        f.write("2024-01-05,Scope 2,Electricity,100.5,kg CO2e\n")  # Duplicate
        f.write("2024-01-05,Scope 2,Electricity,100.5,kg CO2e\n")  # Duplicate
        
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def sample_excel_file():
    """Create a sample Excel file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        temp_path = f.name
    
    # Create sample data
    data = {
        'supplier_name': ['Supplier A', 'Supplier B', 'Supplier C', ''],
        'category': ['Materials', 'Services', 'Materials', 'Transport'],
        'emissions_kg_co2e': [1500.0, 800.0, None, 450.0],
        'location': ['USA', 'Germany', 'Japan', 'UK']
    }
    
    df = pd.DataFrame(data)
    df.to_excel(temp_path, index=False)
    
    yield temp_path
    
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir
