"""
Example usage of the ESG Reporting Python package.

This script demonstrates how to use the ESG Reporting tools programmatically
for processing Microsoft Sustainability Manager data.
"""

import os
import logging
from pathlib import Path
import pandas as pd

from esg_reporting.processor import ESGDataProcessor
from esg_reporting.storage import BlobStorageClient
from esg_reporting.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main example workflow for ESG data processing."""
    
    # Initialize configuration
    config = Config()
    logger.info("Initialized configuration")
    
    # Initialize components
    processor = ESGDataProcessor()
    storage_client = BlobStorageClient()
    
    # Example 1: Process local CSV file
    logger.info("Example 1: Processing local CSV file")
    
    # Create sample data if it doesn't exist
    sample_file = "sample_esg_data.csv"
    if not os.path.exists(sample_file):
        create_sample_data(sample_file)
    
    try:
        # Load and process data
        data = processor.load_data(sample_file)
        logger.info(f"Loaded {len(data)} records from {sample_file}")
        
        # Validate data
        validated_data = processor.validate_data(data)
        logger.info(f"Validated {len(validated_data)} records")
        
        # Process data (apply transformations)
        processed_data = processor.process_data(validated_data)
        logger.info(f"Processed {len(processed_data)} records")
        
        # Save processed data
        output_file = "processed_esg_data.csv"
        processor.save_data(processed_data, output_file)
        logger.info(f"Saved processed data to {output_file}")
        
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        return
    
    # Example 2: Upload to Azure Blob Storage
    logger.info("Example 2: Uploading to Azure Blob Storage")
    
    try:
        # Upload original file
        storage_client.upload_file(
            local_path=sample_file,
            container_name="raw-data",
            blob_name=f"samples/{sample_file}"
        )
        logger.info(f"Uploaded {sample_file} to raw-data container")
        
        # Upload processed file
        storage_client.upload_file(
            local_path=output_file,
            container_name="processed-data",
            blob_name=f"samples/{output_file}"
        )
        logger.info(f"Uploaded {output_file} to processed-data container")
        
    except Exception as e:
        logger.error(f"Error uploading to Azure: {e}")
        logger.info("Make sure you have configured Azure credentials and storage account")
        return
    
    # Example 3: List files in storage
    logger.info("Example 3: Listing files in Azure Blob Storage")
    
    try:
        raw_files = storage_client.list_files("raw-data")
        logger.info(f"Files in raw-data container: {len(raw_files)}")
        for file in raw_files[:5]:  # Show first 5 files
            logger.info(f"  - {file}")
        
        processed_files = storage_client.list_files("processed-data")
        logger.info(f"Files in processed-data container: {len(processed_files)}")
        for file in processed_files[:5]:  # Show first 5 files
            logger.info(f"  - {file}")
            
    except Exception as e:
        logger.error(f"Error listing files: {e}")
    
    # Example 4: Download and verify processed data
    logger.info("Example 4: Downloading and verifying processed data")
    
    try:
        downloaded_file = "downloaded_processed_data.csv"
        storage_client.download_file(
            container_name="processed-data",
            blob_name=f"samples/{output_file}",
            local_path=downloaded_file
        )
        
        # Verify the downloaded file
        downloaded_data = pd.read_csv(downloaded_file)
        logger.info(f"Downloaded file has {len(downloaded_data)} records")
        
        # Clean up
        os.remove(downloaded_file)
        logger.info("Cleaned up downloaded file")
        
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
    
    logger.info("Example workflow completed successfully!")

def create_sample_data(filename: str):
    """Create sample ESG data for demonstration."""
    
    logger.info(f"Creating sample data file: {filename}")
    
    # Sample ESG data structure based on common sustainability metrics
    sample_data = {
        'Date': pd.date_range('2024-01-01', periods=100, freq='D'),
        'Entity': ['Facility A', 'Facility B', 'Facility C'] * 34 + ['Facility A', 'Facility B'],
        'Activity_Type': ['Energy Consumption', 'Water Usage', 'Waste Generation', 'Transportation'] * 25,
        'Metric': ['Electricity', 'Natural Gas', 'Water', 'Solid Waste', 'Fleet Fuel'] * 20,
        'Value': [round(x, 2) for x in (100 + 50 * pd.Series(range(100)).apply(lambda x: x % 10))],
        'Unit': ['kWh', 'MCF', 'Gallons', 'Tons', 'Gallons'] * 20,
        'Scope': ['Scope 1', 'Scope 2', 'Scope 3'] * 34 + ['Scope 1'],
        'Source': ['Utility Bill', 'Meter Reading', 'Vendor Report'] * 34 + ['Utility Bill'],
        'Quality_Score': [round(x, 1) for x in (8.0 + 2.0 * pd.Series(range(100)).apply(lambda x: (x % 5) / 5))],
        'Notes': [''] * 100
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv(filename, index=False)
    logger.info(f"Created sample data with {len(df)} records")

if __name__ == "__main__":
    main()
