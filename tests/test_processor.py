"""
Tests for the data processor module.
"""

import pytest
import pandas as pd
from pathlib import Path

from esg_reporting.processor import ESGDataProcessor


class TestESGDataProcessor:
    
    def test_read_csv_file(self, sample_csv_file):
        """Test reading a CSV file."""
        processor = ESGDataProcessor()
        df, metadata = processor.read_file(sample_csv_file)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 6  # 6 rows including duplicates
        assert len(df.columns) == 5  # 5 columns
        assert metadata['file_type'] == 'csv'
        assert metadata['row_count'] == 6
        assert metadata['column_count'] == 5
        assert 'date' in df.columns
        assert 'co2_equivalent' in df.columns
    
    def test_read_excel_file(self, sample_excel_file):
        """Test reading an Excel file."""
        processor = ESGDataProcessor()
        df, metadata = processor.read_file(sample_excel_file)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 4  # 4 rows
        assert metadata['file_type'] == 'excel'
        assert 'supplier_name' in df.columns
        assert 'emissions_kg_co2e' in df.columns
    
    def test_validate_emissions_data(self, sample_csv_file):
        """Test validation of emissions data."""
        processor = ESGDataProcessor()
        df, _ = processor.read_file(sample_csv_file)
        
        validation_report = processor.validate_esg_data(df, 'emissions')
        
        assert validation_report['entity_type'] == 'emissions'
        assert validation_report['total_rows'] == 6
        assert validation_report['data_quality_score'] > 0
        assert len(validation_report['warnings']) > 0  # Should have warnings for missing data and duplicates
    
    def test_validate_suppliers_data(self, sample_excel_file):
        """Test validation of suppliers data."""
        processor = ESGDataProcessor()
        df, _ = processor.read_file(sample_excel_file)
        
        validation_report = processor.validate_esg_data(df, 'suppliers')
        
        assert validation_report['entity_type'] == 'suppliers'
        assert validation_report['total_rows'] == 4
        assert validation_report['data_quality_score'] > 0
    
    def test_clean_data(self, sample_csv_file):
        """Test data cleaning functionality."""
        processor = ESGDataProcessor()
        df, _ = processor.read_file(sample_csv_file)
        
        # First validate
        validation_report = processor.validate_esg_data(df, 'emissions')
        
        # Then clean
        cleaned_df, cleaning_report = processor.clean_data(df, validation_report)
        
        assert len(cleaned_df) < len(df)  # Should have fewer rows due to duplicate removal
        assert len(cleaning_report['actions_performed']) > 0
        assert cleaning_report['final_row_count'] == len(cleaned_df)
        
        # Check that duplicates were removed
        assert len(cleaned_df) == 5  # Original 6 rows minus 1 duplicate
        
        # Check that columns are standardized
        assert all('_' in col.lower() or col.lower() in ['date', 'scope', 'activity', 'unit'] 
                  for col in cleaned_df.columns if not col.startswith('_'))
    
    def test_save_processed_data_csv(self, sample_csv_file, temp_directory):
        """Test saving processed data as CSV."""
        processor = ESGDataProcessor()
        df, _ = processor.read_file(sample_csv_file)
        
        output_path = Path(temp_directory) / "test_output.csv"
        save_report = processor.save_processed_data(df, str(output_path), "csv")
        
        assert save_report['success'] is True
        assert output_path.exists()
        assert save_report['row_count'] == len(df)
        assert save_report['column_count'] == len(df.columns)
        
        # Verify the saved file can be read back
        saved_df = pd.read_csv(output_path)
        assert len(saved_df) == len(df)
    
    def test_save_processed_data_excel(self, sample_excel_file, temp_directory):
        """Test saving processed data as Excel."""
        processor = ESGDataProcessor()
        df, _ = processor.read_file(sample_excel_file)
        
        output_path = Path(temp_directory) / "test_output.xlsx"
        save_report = processor.save_processed_data(df, str(output_path), "excel")
        
        assert save_report['success'] is True
        assert output_path.exists()
        assert save_report['row_count'] == len(df)
        
        # Verify the saved file can be read back
        saved_df = pd.read_excel(output_path)
        assert len(saved_df) == len(df)
    
    def test_process_in_batches(self, sample_csv_file):
        """Test batch processing functionality."""
        processor = ESGDataProcessor(batch_size=2)  # Small batch size for testing
        df, _ = processor.read_file(sample_csv_file)
        
        def dummy_processing_func(batch_df):
            return len(batch_df)
        
        results = processor.process_in_batches(df, dummy_processing_func)
        
        # Should have 3 batches (6 rows / 2 batch_size = 3 batches)
        assert len(results) == 3
        assert results[0] == 2  # First batch has 2 rows
        assert results[1] == 2  # Second batch has 2 rows
        assert results[2] == 2  # Third batch has 2 rows
    
    def test_file_not_found(self):
        """Test error handling for non-existent files."""
        processor = ESGDataProcessor()
        
        with pytest.raises(FileNotFoundError):
            processor.read_file("non_existent_file.csv")
    
    def test_empty_dataframe_validation(self):
        """Test validation of empty DataFrame."""
        processor = ESGDataProcessor()
        empty_df = pd.DataFrame()
        
        validation_report = processor.validate_esg_data(empty_df, 'general')
        
        assert validation_report['total_rows'] == 0
        assert validation_report['data_quality_score'] == 0.0
        assert any('empty' in issue.lower() for issue in validation_report['issues'])
