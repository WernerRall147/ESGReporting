# ESG Reporting - Microsoft Sustainability Manager to Azure Integration

A comprehensive Python-based solution for automating ESG data export from Microsoft Sustainability Manager, uploading to Azure Blob Storage, and processing via Azure services.

## 🚀 Features

- **Automated Data Processing**: Process ESG data from various formats (CSV, Excel, JSON)
- **Azure Integration**: Seamless connection to Azure Blob Storage with managed identity support
- **Secure Configuration**: Azure Key Vault integration for secrets management
- **Monitoring & Logging**: Azure Monitor integration with structured logging
- **Command Line Interface**: Easy-to-use CLI for all operations
- **Robust Testing**: Comprehensive test suite with pytest
- **Infrastructure as Code**: Azure resources defined with Bicep templates

## 📋 Prerequisites

- Python 3.8 or higher
- Azure subscription
- Azure Developer CLI (azd) - [Install azd](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd)
- Access to Microsoft Sustainability Manager

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd ESGReporting
pip install -r requirements.txt
pip install -e .
```

### 2. Deploy Azure Infrastructure

```bash
# Initialize azd environment
azd init

# Deploy Azure resources
azd up
```

This will deploy:
- Azure Storage Account with blob containers
- Azure Key Vault for secrets management
- Azure Log Analytics workspace for monitoring
- Managed Identity for secure authentication

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Azure resource details
# The azd deployment will output the required values
```

### 4. Test the Installation

```bash
# Run tests to ensure everything is working
pytest tests/

# Test CLI functionality
esg-reporting --help
```

## 📖 Usage

### Command Line Interface

The ESG Reporting tool provides a comprehensive CLI for all operations:

```bash
# Upload a file to Azure Blob Storage
esg-reporting upload /path/to/data.csv --container raw-data

# Process ESG data with validation and transformation
esg-reporting process /path/to/data.csv --output processed_data.csv

# List files in Azure Blob Storage
esg-reporting list --container raw-data

# Download processed data
esg-reporting download processed_data.csv --container processed-data
```

### Processing ESG Data

```python
from esg_reporting.processor import ESGDataProcessor

# Initialize processor
processor = ESGDataProcessor()

# Load and process data
data = processor.load_data("sustainability_data.csv")
validated_data = processor.validate_data(data)
processed_data = processor.process_data(validated_data)

# Save results
processor.save_data(processed_data, "processed_output.csv")
```

### Azure Storage Integration

```python
from esg_reporting.storage import BlobStorageClient

# Initialize client (uses managed identity)
client = BlobStorageClient()

# Upload file
client.upload_file("local_file.csv", "container-name", "remote_file.csv")

# Download file
client.download_file("container-name", "remote_file.csv", "local_download.csv")

# List files
files = client.list_files("container-name")
```

## 🔄 Recommended Workflow

### 1. Manual Export from Microsoft Sustainability Manager
- Navigate to the relevant entity (emissions, activities, suppliers)
- Use the Export button to download data as CSV/Excel
- Save files locally for processing

### 2. Upload and Process Data
```bash
# Upload raw data to Azure
esg-reporting upload sustainability_export.csv --container raw-data

# Process the data with validation and transformations
esg-reporting process sustainability_export.csv --output processed_data.csv

# Upload processed data
esg-reporting upload processed_data.csv --container processed-data
```

### 3. Integration with Azure Services

The solution integrates with:
- **Azure Data Factory**: For orchestrating complex data pipelines
- **Azure Synapse Analytics**: For advanced analytics and reporting
- **Azure Logic Apps**: For workflow automation and notifications
- **Power BI**: For ESG reporting dashboards

## 🏗️ Project Structure

```
ESGReporting/
├── src/esg_reporting/          # Main Python package
│   ├── cli.py                  # Command line interface
│   ├── processor.py            # Data processing logic
│   ├── storage.py              # Azure Blob Storage client
│   ├── config.py               # Configuration management
│   └── __init__.py             # Package initialization
├── infra/                      # Azure infrastructure
│   ├── main.bicep              # Bicep template for Azure resources
│   └── main.parameters.json    # Infrastructure parameters
├── tests/                      # Test suite
│   ├── test_processor.py       # Data processor tests
│   └── conftest.py             # Test configuration
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
├── azure.yaml                  # Azure Developer CLI configuration
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Azure Configuration
AZURE_STORAGE_ACCOUNT_NAME=your_storage_account
AZURE_STORAGE_CONTAINER_NAME=esg-data
AZURE_KEY_VAULT_URL=https://your-keyvault.vault.azure.net/

# Optional: For development with connection strings
AZURE_STORAGE_CONNECTION_STRING=your_connection_string

# Logging
LOG_LEVEL=INFO
```

### Azure Resources

The Bicep template creates:
- **Storage Account**: For raw and processed ESG data
- **Key Vault**: For secure storage of connection strings and secrets
- **Log Analytics Workspace**: For monitoring and diagnostics
- **Managed Identity**: For secure, keyless authentication

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/esg_reporting

# Run specific test file
pytest tests/test_processor.py -v
```

## � Security Best Practices

- **Managed Identity**: No connection strings stored in code
- **Key Vault Integration**: Secrets stored securely in Azure Key Vault
- **Least Privilege**: Role-based access control (RBAC) for Azure resources
- **Data Encryption**: Data encrypted in transit and at rest
- **Audit Logging**: All operations logged to Azure Monitor

## 📊 Monitoring and Logging

The solution includes comprehensive monitoring:

- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Azure Monitor Integration**: Logs sent to Log Analytics workspace
- **Performance Metrics**: Processing times and success rates tracked
- **Error Handling**: Detailed error logging with stack traces

## 🔄 Automation Options

### Power Automate Integration
For automated exports from Microsoft Sustainability Manager:
1. Create Power Automate flow triggered by schedule
2. Export data from MSM to SharePoint/OneDrive
3. Use the CLI to process and upload to Azure

### Azure Data Factory Pipeline
Create ADF pipeline to:
1. Monitor blob storage for new files
2. Trigger processing via CLI or direct Python execution
3. Move processed data to analytics platforms

### GitHub Actions CI/CD
```yaml
# Example workflow for automated deployment
name: Deploy ESG Reporting
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Deploy to Azure
        run: |
          pip install -r requirements.txt
          azd deploy
```

## 📚 API Reference

### ESGDataProcessor

```python
class ESGDataProcessor:
    def load_data(self, file_path: str) -> pd.DataFrame
    def validate_data(self, data: pd.DataFrame) -> pd.DataFrame
    def process_data(self, data: pd.DataFrame) -> pd.DataFrame
    def save_data(self, data: pd.DataFrame, output_path: str) -> None
```

### BlobStorageClient

```python
class BlobStorageClient:
    def upload_file(self, local_path: str, container: str, blob_name: str) -> None
    def download_file(self, container: str, blob_name: str, local_path: str) -> None
    def list_files(self, container: str) -> List[str]
    def delete_file(self, container: str, blob_name: str) -> None
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run the test suite
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:
1. Check the [GitHub Issues](../../issues) page
2. Review Azure service documentation
3. Check the test suite for usage examples

## 🔗 Related Resources

- [Microsoft Sustainability Manager Documentation](https://docs.microsoft.com/en-us/industry/sustainability/)
- [Azure Blob Storage Python SDK](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python)
- [Azure Developer CLI](https://docs.microsoft.com/en-us/azure/developer/azure-developer-cli/)
- [ESG Reporting Best Practices](https://docs.microsoft.com/en-us/industry/sustainability/esg-reporting)