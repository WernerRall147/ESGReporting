"""
Configuration management for ESG Reporting solution.

This module handles all configuration settings using Azure Key Vault for sensitive
data and environment variables for non-sensitive configuration.
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


class Settings(BaseSettings):
    """
    Application settings with Azure Key Vault integration.
    
    Follows Azure best practices:
    - Uses managed identity for authentication
    - Stores sensitive data in Key Vault
    - Implements proper error handling
    """
    
    # Azure Configuration
    azure_storage_account_name: str = Field(..., env="AZURE_STORAGE_ACCOUNT_NAME")
    azure_container_name: str = Field("esg-data", env="AZURE_CONTAINER_NAME")
    azure_key_vault_url: Optional[str] = Field(None, env="AZURE_KEY_VAULT_URL")
    
    # Processing Configuration
    batch_size: int = Field(1000, env="BATCH_SIZE")
    max_file_size_mb: int = Field(100, env="MAX_FILE_SIZE_MB")
    parallel_upload_threshold_mb: int = Field(50, env="PARALLEL_UPLOAD_THRESHOLD_MB")
    
    # Monitoring
    log_level: str = Field("INFO", env="LOG_LEVEL")
    enable_azure_monitor: bool = Field(True, env="ENABLE_AZURE_MONITOR")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class SecureConfigManager:
    """
    Manages secure configuration using Azure Key Vault.
    
    Implements Azure best practices:
    - Uses DefaultAzureCredential for authentication
    - Handles credential rotation automatically
    - Implements proper error handling and logging
    """
    
    def __init__(self, key_vault_url: Optional[str] = None):
        self.settings = Settings()
        self.key_vault_url = key_vault_url or self.settings.azure_key_vault_url
        self._secret_client = None
        
    @property
    def secret_client(self) -> Optional[SecretClient]:
        """
        Lazy initialization of Key Vault client with managed identity.
        """
        if not self.key_vault_url:
            return None
            
        if not self._secret_client:
            try:
                credential = DefaultAzureCredential()
                self._secret_client = SecretClient(
                    vault_url=self.key_vault_url,
                    credential=credential
                )
            except Exception as e:
                # Log error but don't fail completely - fallback to env vars
                print(f"Warning: Could not initialize Key Vault client: {e}")
                return None
                
        return self._secret_client
    
    def get_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve a secret from Key Vault with fallback to environment variables.
        
        Args:
            secret_name: Name of the secret in Key Vault
            default: Default value if secret not found
            
        Returns:
            Secret value or default
        """
        # First try Key Vault
        if self.secret_client:
            try:
                secret = self.secret_client.get_secret(secret_name)
                return secret.value
            except Exception as e:
                print(f"Warning: Could not retrieve secret '{secret_name}' from Key Vault: {e}")
        
        # Fallback to environment variable
        env_value = os.getenv(secret_name.upper().replace('-', '_'), default)
        return env_value


# Global configuration instance
config_manager = SecureConfigManager()
settings = config_manager.settings
