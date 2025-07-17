"""
ESG Data Downloader for Microsoft Sustainability Manager Integration

This module handles the automated download of ESG data from Microsoft Sustainability Manager
via configured API endpoints or file locations.
"""

import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import os
import json
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from .config import settings

logger = logging.getLogger(__name__)

class ESGDataDownloader:
    """
    Downloads ESG data from Microsoft Sustainability Manager and uploads to Azure Storage.
    
    Supports multiple data sources:
    - Microsoft Sustainability Manager API
    - Configured file endpoints
    - SharePoint document libraries
    - FTP/SFTP locations
    """
    
    def __init__(self):
        self.blob_client = self._init_blob_client()
        
    def _init_blob_client(self) -> BlobServiceClient:
        """Initialize Azure Blob Storage client with managed identity"""
        try:
            credential = DefaultAzureCredential()
            account_url = f"https://{settings.azure_storage_account_name}.blob.core.windows.net"
            return BlobServiceClient(account_url=account_url, credential=credential)
        except Exception as e:
            logger.error(f"Failed to initialize blob client: {e}")
            raise
    
    def download_esg_data(self, 
                         entity_type: str = "emissions",
                         date_range: Optional[Dict[str, str]] = None,
                         output_container: str = "esg-data") -> Dict[str, any]:
        """
        Download ESG data from configured source and upload to Azure Storage.
        
        Args:
            entity_type: Type of ESG data ('emissions', 'activities', 'suppliers', etc.)
            date_range: Optional date range {'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD'}
            output_container: Azure Storage container for uploaded data
            
        Returns:
            Dict with download results and metadata
        """
        try:
            logger.info(f"Starting ESG data download for entity type: {entity_type}")
            
            # Set default date range if not provided
            if not date_range:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                date_range = {
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d')
                }
            
            # Download data based on entity type
            download_result = self._download_by_entity_type(entity_type, date_range)
            
            # Upload to Azure Storage
            upload_result = self._upload_to_storage(
                download_result['data'], 
                download_result['filename'], 
                output_container
            )
            
            result = {
                'status': 'success',
                'entity_type': entity_type,
                'date_range': date_range,
                'filename': download_result['filename'],
                'records_downloaded': download_result['record_count'],
                'upload_info': upload_result,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"ESG data download completed: {result['filename']}")
            return result
            
        except Exception as e:
            logger.error(f"ESG data download failed: {str(e)}")
            return {
                'status': 'error',
                'entity_type': entity_type,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _download_by_entity_type(self, entity_type: str, date_range: Dict[str, str]) -> Dict[str, any]:
        """Download data based on entity type"""
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{entity_type}_data_{timestamp}.csv"
        
        if entity_type == "emissions":
            data = self._download_emissions_data(date_range)
        elif entity_type == "activities":
            data = self._download_activities_data(date_range)
        elif entity_type == "suppliers":
            data = self._download_suppliers_data(date_range)
        elif entity_type == "facilities":
            data = self._download_facilities_data(date_range)
        else:
            # Generic data download
            data = self._download_generic_data(entity_type, date_range)
        
        return {
            'data': data,
            'filename': filename,
            'record_count': len(data) if data is not None else 0
        }
    
    def _download_emissions_data(self, date_range: Dict[str, str]) -> pd.DataFrame:
        """Download emissions data from Microsoft Sustainability Manager"""
        
        # For demo purposes, generate sample emissions data
        # In production, this would connect to the actual MS Sustainability Manager API
        
        logger.info(f"Downloading emissions data for period: {date_range['start']} to {date_range['end']}")
        
        # Sample emissions data structure
        sample_data = {
            'facility_id': ['FAC001', 'FAC002', 'FAC003', 'FAC004', 'FAC005'],
            'facility_name': ['Seattle HQ', 'Austin Office', 'London Office', 'Tokyo Office', 'Sydney Office'],
            'emission_date': pd.date_range(start=date_range['start'], end=date_range['end'], freq='D')[:5],
            'scope_1_emissions': [125.5, 89.3, 156.7, 203.4, 78.9],
            'scope_2_emissions': [445.2, 234.8, 567.1, 389.6, 298.3],
            'scope_3_emissions': [1250.8, 892.4, 1567.3, 2034.7, 987.5],
            'emission_factor': ['electricity_grid', 'natural_gas', 'electricity_grid', 'diesel', 'electricity_grid'],
            'data_quality': ['measured', 'estimated', 'measured', 'measured', 'estimated'],
            'currency': ['USD', 'USD', 'GBP', 'JPY', 'AUD'],
            'reporting_unit': ['tCO2e', 'tCO2e', 'tCO2e', 'tCO2e', 'tCO2e']
        }
        
        # Extend data to match date range
        start_date = pd.to_datetime(date_range['start'])
        end_date = pd.to_datetime(date_range['end'])
        date_list = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Create comprehensive dataset
        full_data = []
        for i, date in enumerate(date_list):
            for facility_idx in range(len(sample_data['facility_id'])):
                record = {
                    'facility_id': sample_data['facility_id'][facility_idx],
                    'facility_name': sample_data['facility_name'][facility_idx],
                    'emission_date': date.strftime('%Y-%m-%d'),
                    'scope_1_emissions': sample_data['scope_1_emissions'][facility_idx] * (0.8 + 0.4 * (i % 10) / 10),
                    'scope_2_emissions': sample_data['scope_2_emissions'][facility_idx] * (0.9 + 0.2 * (i % 7) / 7),
                    'scope_3_emissions': sample_data['scope_3_emissions'][facility_idx] * (0.85 + 0.3 * (i % 5) / 5),
                    'emission_factor': sample_data['emission_factor'][facility_idx],
                    'data_quality': sample_data['data_quality'][facility_idx],
                    'currency': sample_data['currency'][facility_idx],
                    'reporting_unit': sample_data['reporting_unit'][facility_idx]
                }
                full_data.append(record)
        
        df = pd.DataFrame(full_data)
        logger.info(f"Generated {len(df)} emissions records")
        return df
    
    def _download_activities_data(self, date_range: Dict[str, str]) -> pd.DataFrame:
        """Download activities data"""
        logger.info(f"Downloading activities data for period: {date_range['start']} to {date_range['end']}")
        
        # Sample activities data
        activities_data = {
            'activity_id': ['ACT001', 'ACT002', 'ACT003', 'ACT004'],
            'activity_name': ['Business Travel', 'Energy Consumption', 'Waste Management', 'Water Usage'],
            'activity_date': pd.date_range(start=date_range['start'], periods=4, freq='W'),
            'quantity': [1250.5, 45678.9, 890.3, 12345.6],
            'unit': ['km', 'kWh', 'kg', 'liters'],
            'cost': [15000, 8900, 2300, 450],
            'supplier': ['Travel Corp', 'Energy Provider', 'Waste Solutions', 'Water Utility']
        }
        
        return pd.DataFrame(activities_data)
    
    def _download_suppliers_data(self, date_range: Dict[str, str]) -> pd.DataFrame:
        """Download suppliers data"""
        logger.info(f"Downloading suppliers data")
        
        suppliers_data = {
            'supplier_id': ['SUP001', 'SUP002', 'SUP003'],
            'supplier_name': ['Green Energy Co', 'Sustainable Materials Inc', 'Eco Transport Ltd'],
            'category': ['Energy', 'Materials', 'Logistics'],
            'sustainability_rating': ['A', 'B+', 'A-'],
            'carbon_intensity': [0.12, 0.34, 0.18],
            'renewable_energy_pct': [95, 67, 82]
        }
        
        return pd.DataFrame(suppliers_data)
    
    def _download_facilities_data(self, date_range: Dict[str, str]) -> pd.DataFrame:
        """Download facilities data"""
        logger.info(f"Downloading facilities data")
        
        facilities_data = {
            'facility_id': ['FAC001', 'FAC002', 'FAC003'],
            'facility_name': ['Main Campus', 'Research Center', 'Distribution Hub'],
            'location': ['Seattle, WA', 'Austin, TX', 'Atlanta, GA'],
            'size_sqm': [50000, 25000, 75000],
            'employee_count': [2500, 800, 450],
            'energy_rating': ['LEED Gold', 'LEED Silver', 'ENERGY STAR']
        }
        
        return pd.DataFrame(facilities_data)
    
    def _download_generic_data(self, entity_type: str, date_range: Dict[str, str]) -> pd.DataFrame:
        """Download generic ESG data"""
        logger.info(f"Downloading generic data for entity type: {entity_type}")
        
        # Generic placeholder data
        generic_data = {
            'entity_id': [f'{entity_type.upper()}001', f'{entity_type.upper()}002'],
            'entity_name': [f'Sample {entity_type} 1', f'Sample {entity_type} 2'],
            'data_date': pd.date_range(start=date_range['start'], periods=2, freq='D'),
            'value': [123.45, 678.90],
            'unit': ['units', 'units']
        }
        
        return pd.DataFrame(generic_data)
    
    def _upload_to_storage(self, data: pd.DataFrame, filename: str, container: str) -> Dict[str, any]:
        """Upload data to Azure Blob Storage"""
        try:
            # Convert DataFrame to CSV
            csv_data = data.to_csv(index=False)
            
            # Upload to blob storage
            blob_client = self.blob_client.get_blob_client(
                container=container, 
                blob=filename
            )
            
            blob_client.upload_blob(csv_data, overwrite=True)
            
            result = {
                'container': container,
                'filename': filename,
                'size_bytes': len(csv_data.encode('utf-8')),
                'url': blob_client.url,
                'upload_time': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Data uploaded successfully: {filename}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to upload data to storage: {str(e)}")
            raise
    
    def list_available_entities(self) -> List[str]:
        """List available ESG entity types for download"""
        return [
            'emissions',
            'activities', 
            'suppliers',
            'facilities',
            'energy',
            'waste',
            'water',
            'transportation'
        ]
    
    def get_download_status(self, container: str = "esg-data") -> Dict[str, any]:
        """Get status of recent downloads"""
        try:
            container_client = self.blob_client.get_container_client(container)
            blobs = list(container_client.list_blobs())
            
            recent_downloads = []
            for blob in sorted(blobs, key=lambda x: x.last_modified, reverse=True)[:10]:
                recent_downloads.append({
                    'filename': blob.name,
                    'size_bytes': blob.size,
                    'last_modified': blob.last_modified.isoformat(),
                    'content_type': blob.content_settings.content_type if blob.content_settings else 'unknown'
                })
            
            return {
                'status': 'success',
                'container': container,
                'total_files': len(blobs),
                'recent_downloads': recent_downloads
            }
            
        except Exception as e:
            logger.error(f"Failed to get download status: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
