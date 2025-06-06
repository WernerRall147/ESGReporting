"""
Azure Blob Storage client for ESG data management.

This module provides secure, efficient blob storage operations following Azure best practices:
- Uses managed identity for authentication
- Implements retry logic with exponential backoff
- Handles large files with parallel uploads
- Provides comprehensive error handling and logging
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.storage.blob import StandardBlobTier
from azure.core.exceptions import AzureError, ResourceNotFoundError

from .config import settings


logger = logging.getLogger(__name__)


class ESGBlobStorageClient:
    """
    Azure Blob Storage client optimized for ESG data operations.
    
    Features:
    - Managed identity authentication
    - Automatic retry with exponential backoff
    - Parallel uploads for large files
    - Proper error handling and logging
    - File organization by date and entity type
    """
    
    def __init__(self, storage_account_name: Optional[str] = None, container_name: Optional[str] = None):
        """
        Initialize the blob storage client.
        
        Args:
            storage_account_name: Azure Storage account name
            container_name: Container name for ESG data
        """
        self.storage_account_name = storage_account_name or settings.azure_storage_account_name
        self.container_name = container_name or settings.azure_container_name
        
        # Build storage account URL
        self.account_url = f"https://{self.storage_account_name}.blob.core.windows.net"
        
        # Initialize credential using managed identity
        self.credential = DefaultAzureCredential()
        
        # Initialize clients
        self._blob_service_client = None
        self._container_client = None
    
    @property
    def blob_service_client(self) -> BlobServiceClient:
        """Lazy initialization of blob service client."""
        if not self._blob_service_client:
            self._blob_service_client = BlobServiceClient(
                account_url=self.account_url,
                credential=self.credential
            )
        return self._blob_service_client
    
    @property
    def container_client(self) -> ContainerClient:
        """Lazy initialization of container client."""
        if not self._container_client:
            self._container_client = self.blob_service_client.get_container_client(
                container=self.container_name
            )
        return self._container_client
    
    async def ensure_container_exists(self) -> bool:
        """
        Ensure the container exists, create if it doesn't.
        
        Returns:
            True if container exists or was created successfully
        """
        try:
            # Try to get container properties
            await self.container_client.get_container_properties()
            logger.info(f"Container '{self.container_name}' exists")
            return True
        except ResourceNotFoundError:
            try:
                # Container doesn't exist, create it
                await self.container_client.create_container()
                logger.info(f"Created container '{self.container_name}'")
                return True
            except AzureError as e:
                logger.error(f"Failed to create container '{self.container_name}': {e}")
                return False
        except AzureError as e:
            logger.error(f"Error checking container '{self.container_name}': {e}")
            return False
    
    def generate_blob_path(self, filename: str, entity_type: str = "general", 
                          date: Optional[datetime] = None) -> str:
        """
        Generate organized blob path following best practices.
        
        Args:
            filename: Original filename
            entity_type: Type of ESG entity (emissions, activities, suppliers, etc.)
            date: Date for organization (defaults to current date)
            
        Returns:
            Organized blob path: {entity_type}/{year}/{month}/{day}/{filename}
        """
        if date is None:
            date = datetime.now(timezone.utc)
        
        # Organize by entity type and date
        blob_path = f"{entity_type}/{date.year}/{date.month:02d}/{date.day:02d}/{filename}"
        return blob_path
    
    async def upload_file(self, 
                         local_file_path: str, 
                         entity_type: str = "general",
                         blob_name: Optional[str] = None,
                         metadata: Optional[Dict[str, str]] = None,
                         overwrite: bool = False) -> Dict[str, Any]:
        """
        Upload a file to blob storage with optimized handling.
        
        Args:
            local_file_path: Path to local file
            entity_type: ESG entity type for organization
            blob_name: Custom blob name (optional)
            metadata: Additional metadata to store with blob
            overwrite: Whether to overwrite existing blob
            
        Returns:
            Dictionary with upload results and blob information
        """
        local_path = Path(local_file_path)
        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_file_path}")
        
        # Generate blob path if not provided
        if blob_name is None:
            blob_name = self.generate_blob_path(local_path.name, entity_type)
        
        # Get file size for optimization decisions
        file_size_mb = local_path.stat().st_size / (1024 * 1024)
        
        try:
            blob_client = self.container_client.get_blob_client(blob=blob_name)
            
            # Prepare metadata
            upload_metadata = {
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "entity_type": entity_type,
                "original_filename": local_path.name,
                "file_size_mb": str(round(file_size_mb, 2))
            }
            if metadata:
                upload_metadata.update(metadata)
            
            # Choose upload strategy based on file size
            with open(local_path, 'rb') as data:
                if file_size_mb >= settings.parallel_upload_threshold_mb:
                    logger.info(f"Uploading large file ({file_size_mb:.2f}MB) with parallel transfer")
                    # Use parallel upload for large files
                    result = await blob_client.upload_blob(
                        data,
                        overwrite=overwrite,
                        metadata=upload_metadata,
                        standard_blob_tier=StandardBlobTier.Hot,
                        max_concurrency=4
                    )
                else:
                    logger.info(f"Uploading file ({file_size_mb:.2f}MB) with standard transfer")
                    # Standard upload for smaller files
                    result = await blob_client.upload_blob(
                        data,
                        overwrite=overwrite,
                        metadata=upload_metadata,
                        standard_blob_tier=StandardBlobTier.Hot
                    )
            
            logger.info(f"Successfully uploaded '{local_path.name}' to '{blob_name}'")
            
            return {
                "success": True,
                "blob_name": blob_name,
                "blob_url": blob_client.url,
                "file_size_mb": file_size_mb,
                "etag": result.get("etag"),
                "last_modified": result.get("last_modified"),
                "metadata": upload_metadata
            }
            
        except AzureError as e:
            logger.error(f"Failed to upload '{local_file_path}': {e}")
            return {
                "success": False,
                "error": str(e),
                "blob_name": blob_name,
                "file_size_mb": file_size_mb
            }
    
    async def list_blobs(self, 
                        entity_type: Optional[str] = None,
                        date_filter: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        List blobs with optional filtering.
        
        Args:
            entity_type: Filter by entity type
            date_filter: Filter by specific date
            
        Returns:
            List of blob information dictionaries
        """
        try:
            # Build name prefix for filtering
            name_prefix = ""
            if entity_type:
                name_prefix = entity_type
                if date_filter:
                    name_prefix += f"/{date_filter.year}/{date_filter.month:02d}/{date_filter.day:02d}"
            
            blobs = []
            async for blob in self.container_client.list_blobs(name_starts_with=name_prefix):
                blob_info = {
                    "name": blob.name,
                    "size_mb": round(blob.size / (1024 * 1024), 2),
                    "last_modified": blob.last_modified,
                    "etag": blob.etag,
                    "metadata": blob.metadata or {}
                }
                blobs.append(blob_info)
            
            logger.info(f"Found {len(blobs)} blobs with prefix '{name_prefix}'")
            return blobs
            
        except AzureError as e:
            logger.error(f"Failed to list blobs: {e}")
            return []
    
    async def download_blob(self, blob_name: str, local_file_path: str) -> bool:
        """
        Download a blob to local file.
        
        Args:
            blob_name: Name of blob to download
            local_file_path: Local path to save file
            
        Returns:
            True if download successful
        """
        try:
            blob_client = self.container_client.get_blob_client(blob=blob_name)
            
            # Ensure local directory exists
            local_path = Path(local_file_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download blob
            with open(local_path, 'wb') as download_file:
                download_stream = await blob_client.download_blob()
                download_file.write(await download_stream.readall())
            
            logger.info(f"Successfully downloaded '{blob_name}' to '{local_file_path}'")
            return True
            
        except AzureError as e:
            logger.error(f"Failed to download blob '{blob_name}': {e}")
            return False
    
    async def delete_blob(self, blob_name: str) -> bool:
        """
        Delete a blob.
        
        Args:
            blob_name: Name of blob to delete
            
        Returns:
            True if deletion successful
        """
        try:
            blob_client = self.container_client.get_blob_client(blob=blob_name)
            await blob_client.delete_blob()
            
            logger.info(f"Successfully deleted blob '{blob_name}'")
            return True
            
        except AzureError as e:
            logger.error(f"Failed to delete blob '{blob_name}': {e}")
            return False
