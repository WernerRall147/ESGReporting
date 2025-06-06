"""
Data processing module for ESG reporting.

This module handles CSV/Excel file processing, validation, and transformation
following Azure best practices for data handling and error management.
"""

import logging
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
import json

from .config import settings


logger = logging.getLogger(__name__)


class ESGDataProcessor:
    """
    ESG data processor for cleaning, validating, and transforming data.
    
    Features:
    - Handles CSV and Excel files
    - Data validation and cleaning
    - Batch processing for large datasets
    - Comprehensive error handling
    - Detailed processing reports
    """
    
    def __init__(self, batch_size: Optional[int] = None):
        """
        Initialize the data processor.
        
        Args:
            batch_size: Number of records to process in each batch
        """
        self.batch_size = batch_size or settings.batch_size
        
    def read_file(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Read CSV or Excel file with comprehensive error handling.
        
        Args:
            file_path: Path to the data file
            
        Returns:
            Tuple of (DataFrame, metadata dictionary)
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        metadata = {
            "file_path": str(path),
            "file_name": path.name,
            "file_size_mb": round(path.stat().st_size / (1024 * 1024), 2),
            "read_timestamp": datetime.now(timezone.utc).isoformat(),
            "file_extension": path.suffix.lower()
        }
        
        try:
            # Determine file type and read accordingly
            if path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path, encoding='utf-8-sig')  # Handle BOM
                metadata["file_type"] = "csv"
            elif path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
                metadata["file_type"] = "excel"
            else:
                raise ValueError(f"Unsupported file type: {path.suffix}")
            
            # Add basic DataFrame metadata
            metadata.update({
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": list(df.columns),
                "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
            })
            
            logger.info(f"Successfully read file: {path.name} ({metadata['row_count']} rows, {metadata['column_count']} columns)")
            
            return df, metadata
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise
    
    def validate_esg_data(self, df: pd.DataFrame, entity_type: str = "general") -> Dict[str, Any]:
        """
        Validate ESG data for common issues and requirements.
        
        Args:
            df: DataFrame to validate
            entity_type: Type of ESG data (emissions, activities, suppliers, etc.)
            
        Returns:
            Validation report dictionary
        """
        validation_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entity_type": entity_type,
            "total_rows": len(df),
            "issues": [],
            "warnings": [],
            "data_quality_score": 100.0
        }
        
        # Check for empty DataFrame
        if df.empty:
            validation_report["issues"].append("DataFrame is empty")
            validation_report["data_quality_score"] = 0.0
            return validation_report
        
        # Check for missing data
        missing_data = df.isnull().sum()
        if missing_data.any():
            missing_info = []
            for col, count in missing_data.items():
                if count > 0:
                    percentage = (count / len(df)) * 100
                    missing_info.append(f"{col}: {count} missing ({percentage:.1f}%)")
                    
                    # Deduct points based on missing data percentage
                    if percentage > 50:
                        validation_report["data_quality_score"] -= 20
                    elif percentage > 25:
                        validation_report["data_quality_score"] -= 10
                    elif percentage > 10:
                        validation_report["data_quality_score"] -= 5
            
            if missing_info:
                validation_report["warnings"].append(f"Missing data found: {', '.join(missing_info)}")
        
        # Check for duplicate rows
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            duplicate_percentage = (duplicate_count / len(df)) * 100
            validation_report["warnings"].append(f"Found {duplicate_count} duplicate rows ({duplicate_percentage:.1f}%)")
            validation_report["data_quality_score"] -= min(duplicate_percentage, 15)
        
        # Check for common ESG data columns
        common_esg_columns = ['date', 'timestamp', 'value', 'unit', 'category', 'scope', 'activity']
        found_columns = [col for col in common_esg_columns if any(col.lower() in df_col.lower() for df_col in df.columns)]
        
        if not found_columns:
            validation_report["warnings"].append("No common ESG data columns detected")
            validation_report["data_quality_score"] -= 10
        
        # Check data types
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_columns) == 0:
            validation_report["warnings"].append("No numeric columns found")
            validation_report["data_quality_score"] -= 5
        
        # Entity-specific validations
        if entity_type == "emissions":
            self._validate_emissions_data(df, validation_report)
        elif entity_type == "activities":
            self._validate_activities_data(df, validation_report)
        elif entity_type == "suppliers":
            self._validate_suppliers_data(df, validation_report)
        
        # Ensure score doesn't go below 0
        validation_report["data_quality_score"] = max(0.0, validation_report["data_quality_score"])
        
        logger.info(f"Data validation completed. Quality score: {validation_report['data_quality_score']:.1f}/100")
        
        return validation_report
    
    def _validate_emissions_data(self, df: pd.DataFrame, report: Dict[str, Any]) -> None:
        """Validate emissions-specific data requirements."""
        # Check for scope columns (Scope 1, 2, 3)
        scope_columns = [col for col in df.columns if 'scope' in col.lower()]
        if not scope_columns:
            report["warnings"].append("No scope columns found for emissions data")
            report["data_quality_score"] -= 5
        
        # Check for CO2 equivalent or similar
        co2_columns = [col for col in df.columns if any(term in col.lower() for term in ['co2', 'carbon', 'emission'])]
        if not co2_columns:
            report["warnings"].append("No CO2/carbon/emission columns found")
            report["data_quality_score"] -= 10
    
    def _validate_activities_data(self, df: pd.DataFrame, report: Dict[str, Any]) -> None:
        """Validate activities-specific data requirements."""
        # Check for activity type or category
        activity_columns = [col for col in df.columns if any(term in col.lower() for term in ['activity', 'type', 'category'])]
        if not activity_columns:
            report["warnings"].append("No activity type/category columns found")
            report["data_quality_score"] -= 5
    
    def _validate_suppliers_data(self, df: pd.DataFrame, report: Dict[str, Any]) -> None:
        """Validate suppliers-specific data requirements."""
        # Check for supplier identification
        supplier_columns = [col for col in df.columns if any(term in col.lower() for term in ['supplier', 'vendor', 'company', 'name'])]
        if not supplier_columns:
            report["warnings"].append("No supplier identification columns found")
            report["data_quality_score"] -= 10
    
    def clean_data(self, df: pd.DataFrame, validation_report: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Clean and standardize ESG data.
        
        Args:
            df: DataFrame to clean
            validation_report: Validation report from validate_esg_data
            
        Returns:
            Tuple of (cleaned DataFrame, cleaning report)
        """
        cleaning_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "original_row_count": len(df),
            "actions_performed": [],
            "final_row_count": 0,
            "data_quality_improvement": 0.0
        }
        
        # Make a copy to avoid modifying original
        cleaned_df = df.copy()
        
        # Remove duplicate rows
        initial_count = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates()
        duplicates_removed = initial_count - len(cleaned_df)
        if duplicates_removed > 0:
            cleaning_report["actions_performed"].append(f"Removed {duplicates_removed} duplicate rows")
        
        # Standardize column names (lowercase, replace spaces with underscores)
        original_columns = cleaned_df.columns.tolist()
        cleaned_df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in cleaned_df.columns]
        if original_columns != cleaned_df.columns.tolist():
            cleaning_report["actions_performed"].append("Standardized column names")
        
        # Handle missing data (basic approach - can be enhanced based on requirements)
        for column in cleaned_df.columns:
            if cleaned_df[column].dtype in ['object', 'string']:
                # Fill string/object columns with 'Unknown' or empty string
                filled_count = cleaned_df[column].isnull().sum()
                if filled_count > 0:
                    cleaned_df[column] = cleaned_df[column].fillna('Unknown')
                    cleaning_report["actions_performed"].append(f"Filled {filled_count} missing values in '{column}' with 'Unknown'")
            elif cleaned_df[column].dtype in ['int64', 'float64']:
                # Fill numeric columns with 0 or median (configurable)
                filled_count = cleaned_df[column].isnull().sum()
                if filled_count > 0:
                    cleaned_df[column] = cleaned_df[column].fillna(0)
                    cleaning_report["actions_performed"].append(f"Filled {filled_count} missing values in '{column}' with 0")
        
        # Add processing metadata
        cleaned_df['_processed_timestamp'] = datetime.now(timezone.utc).isoformat()
        cleaned_df['_data_quality_score'] = validation_report.get('data_quality_score', 0)
        
        cleaning_report["final_row_count"] = len(cleaned_df)
        
        # Calculate improvement (simplified metric)
        if validation_report.get('data_quality_score', 0) < 100:
            # Assume cleaning improved quality by removing duplicates and handling missing data
            improvement = min(10.0, duplicates_removed / initial_count * 100)
            cleaning_report["data_quality_improvement"] = improvement
        
        logger.info(f"Data cleaning completed. {len(cleaning_report['actions_performed'])} actions performed")
        
        return cleaned_df, cleaning_report
    
    def process_in_batches(self, df: pd.DataFrame, processing_func, **kwargs) -> List[Any]:
        """
        Process large DataFrame in batches to manage memory usage.
        
        Args:
            df: DataFrame to process
            processing_func: Function to apply to each batch
            **kwargs: Additional arguments for processing_func
            
        Returns:
            List of results from each batch
        """
        results = []
        total_batches = (len(df) - 1) // self.batch_size + 1
        
        logger.info(f"Processing {len(df)} rows in {total_batches} batches of {self.batch_size}")
        
        for i in range(0, len(df), self.batch_size):
            batch_num = i // self.batch_size + 1
            batch = df.iloc[i:i + self.batch_size]
            
            logger.debug(f"Processing batch {batch_num}/{total_batches} ({len(batch)} rows)")
            
            try:
                result = processing_func(batch, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing batch {batch_num}: {e}")
                # Continue with next batch rather than failing completely
                results.append({"error": str(e), "batch_num": batch_num})
        
        logger.info(f"Batch processing completed. {len(results)} batches processed")
        return results
    
    def save_processed_data(self, df: pd.DataFrame, output_path: str, format: str = "csv") -> Dict[str, Any]:
        """
        Save processed data to file.
        
        Args:
            df: DataFrame to save
            output_path: Path for output file
            format: Output format ('csv' or 'excel')
            
        Returns:
            Save operation report
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        save_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "output_path": str(output_path),
            "format": format,
            "row_count": len(df),
            "column_count": len(df.columns),
            "success": False
        }
        
        try:
            if format.lower() == "csv":
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
            elif format.lower() == "excel":
                df.to_excel(output_path, index=False, engine='openpyxl')
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            # Get file size
            file_size_mb = round(output_path.stat().st_size / (1024 * 1024), 2)
            save_report.update({
                "success": True,
                "file_size_mb": file_size_mb
            })
            
            logger.info(f"Successfully saved processed data to {output_path} ({file_size_mb}MB)")
            
        except Exception as e:
            logger.error(f"Error saving processed data: {e}")
            save_report["error"] = str(e)
        
        return save_report
