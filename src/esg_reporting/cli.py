"""
Command-line interface for ESG Reporting solution.

This module provides an easy-to-use CLI for all ESG data operations,
following Azure best practices and providing comprehensive error handling.
"""

import click
import asyncio
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from .config import settings
from .storage import ESGBlobStorageClient
from .processor import ESGDataProcessor


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    ESG Reporting CLI - Automate ESG data processing with Azure services.
    
    This tool helps you upload, process, and manage ESG data exported from
    Microsoft Sustainability Manager using Azure Blob Storage and other Azure services.
    """
    pass


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--entity-type', default='general', 
              help='ESG entity type (emissions, activities, suppliers, general)')
@click.option('--blob-name', help='Custom blob name (optional)')
@click.option('--overwrite', is_flag=True, help='Overwrite existing blob')
@click.option('--validate', is_flag=True, help='Validate data before upload')
@click.option('--clean', is_flag=True, help='Clean data before upload')
def upload(file_path: str, entity_type: str, blob_name: Optional[str], 
           overwrite: bool, validate: bool, clean: bool):
    """
    Upload ESG data file to Azure Blob Storage.
    
    Examples:
    
    esg-cli upload data/emissions.csv --entity-type emissions --validate
    
    esg-cli upload data/suppliers.xlsx --entity-type suppliers --clean --overwrite
    """
    
    async def _upload():
        # Initialize clients
        storage_client = ESGBlobStorageClient()
        processor = ESGDataProcessor()
        
        click.echo(f"📁 Processing file: {file_path}")
        
        # Ensure container exists
        if not await storage_client.ensure_container_exists():
            click.echo("❌ Failed to ensure container exists", err=True)
            return
        
        processing_results = {}
        
        # Optional validation and cleaning
        if validate or clean:
            try:
                df, metadata = processor.read_file(file_path)
                processing_results['file_metadata'] = metadata
                click.echo(f"📊 File loaded: {metadata['row_count']} rows, {metadata['column_count']} columns")
                
                if validate:
                    validation_report = processor.validate_esg_data(df, entity_type)
                    processing_results['validation'] = validation_report
                    
                    click.echo(f"🔍 Data quality score: {validation_report['data_quality_score']:.1f}/100")
                    
                    if validation_report['issues']:
                        click.echo("❌ Data issues found:")
                        for issue in validation_report['issues']:
                            click.echo(f"  • {issue}")
                    
                    if validation_report['warnings']:
                        click.echo("⚠️  Data warnings:")
                        for warning in validation_report['warnings']:
                            click.echo(f"  • {warning}")
                
                if clean:
                    cleaned_df, cleaning_report = processor.clean_data(df, validation_report if validate else {})
                    processing_results['cleaning'] = cleaning_report
                    
                    click.echo(f"🧹 Data cleaned: {len(cleaning_report['actions_performed'])} actions performed")
                    
                    # Save cleaned data temporarily
                    temp_path = Path(file_path).parent / f"cleaned_{Path(file_path).name}"
                    save_report = processor.save_processed_data(cleaned_df, str(temp_path), "csv")
                    
                    if save_report['success']:
                        file_path = str(temp_path)  # Use cleaned file for upload
                        click.echo(f"💾 Cleaned data saved to: {temp_path}")
                    else:
                        click.echo(f"❌ Failed to save cleaned data: {save_report.get('error')}", err=True)
                        return
                        
            except Exception as e:
                click.echo(f"❌ Error during data processing: {e}", err=True)
                return
        
        # Upload file
        try:
            metadata = {
                "entity_type": entity_type,
                "processing_results": json.dumps(processing_results) if processing_results else None
            }
            
            result = await storage_client.upload_file(
                local_file_path=file_path,
                entity_type=entity_type,
                blob_name=blob_name,
                metadata=metadata,
                overwrite=overwrite
            )
            
            if result['success']:
                click.echo(f"✅ Upload successful!")
                click.echo(f"📍 Blob name: {result['blob_name']}")
                click.echo(f"🔗 Blob URL: {result['blob_url']}")
                click.echo(f"📏 File size: {result['file_size_mb']:.2f} MB")
            else:
                click.echo(f"❌ Upload failed: {result['error']}", err=True)
                
        except Exception as e:
            click.echo(f"❌ Upload error: {e}", err=True)
        finally:
            # Clean up temporary cleaned file if created
            if clean and 'temp_path' in locals():
                try:
                    temp_path.unlink(missing_ok=True)
                except:
                    pass
    
    # Run async function
    asyncio.run(_upload())


@cli.command()
@click.option('--entity-type', help='Filter by entity type')
@click.option('--date', help='Filter by date (YYYY-MM-DD)')
@click.option('--output', help='Save results to JSON file')
def list_files(entity_type: Optional[str], date: Optional[str], output: Optional[str]):
    """
    List files in Azure Blob Storage.
    
    Examples:
    
    esg-cli list-files --entity-type emissions
    
    esg-cli list-files --date 2024-01-15 --output files.json
    """
    
    async def _list_files():
        storage_client = ESGBlobStorageClient()
        
        # Parse date filter
        date_filter = None
        if date:
            try:
                date_filter = datetime.fromisoformat(date)
            except ValueError:
                click.echo(f"❌ Invalid date format: {date}. Use YYYY-MM-DD", err=True)
                return
        
        try:
            blobs = await storage_client.list_blobs(entity_type, date_filter)
            
            if not blobs:
                click.echo("📭 No files found matching the criteria")
                return
            
            click.echo(f"📂 Found {len(blobs)} files:")
            
            total_size_mb = 0
            for blob in blobs:
                size_mb = blob['size_mb']
                total_size_mb += size_mb
                
                # Format last modified
                last_modified = blob['last_modified'].strftime('%Y-%m-%d %H:%M:%S UTC')
                
                click.echo(f"  📄 {blob['name']}")
                click.echo(f"      Size: {size_mb:.2f} MB | Modified: {last_modified}")
                
                # Show metadata if available
                if blob['metadata']:
                    entity_type_meta = blob['metadata'].get('entity_type', 'N/A')
                    click.echo(f"      Entity Type: {entity_type_meta}")
            
            click.echo(f"\n📊 Total: {len(blobs)} files, {total_size_mb:.2f} MB")
            
            # Save to file if requested
            if output:
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'w') as f:
                    json.dump(blobs, f, indent=2, default=str)
                
                click.echo(f"💾 Results saved to: {output}")
                
        except Exception as e:
            click.echo(f"❌ Error listing files: {e}", err=True)
    
    asyncio.run(_list_files())


@cli.command()
@click.argument('blob_name')
@click.argument('local_path')
def download(blob_name: str, local_path: str):
    """
    Download a file from Azure Blob Storage.
    
    Examples:
    
    esg-cli download emissions/2024/01/15/emissions.csv ./downloads/emissions.csv
    """
    
    async def _download():
        storage_client = ESGBlobStorageClient()
        
        try:
            success = await storage_client.download_blob(blob_name, local_path)
            
            if success:
                click.echo(f"✅ Download successful!")
                click.echo(f"📁 Saved to: {local_path}")
            else:
                click.echo(f"❌ Download failed", err=True)
                
        except Exception as e:
            click.echo(f"❌ Download error: {e}", err=True)
    
    asyncio.run(_download())


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--entity-type', default='general',
              help='ESG entity type (emissions, activities, suppliers, general)')
@click.option('--output-dir', default='./processed',
              help='Output directory for processed files')
@click.option('--format', 'output_format', default='csv', type=click.Choice(['csv', 'excel']),
              help='Output format')
def process(file_path: str, entity_type: str, output_dir: str, output_format: str):
    """
    Process ESG data file (validate, clean, transform).
    
    Examples:
    
    esg-cli process data/emissions.csv --entity-type emissions
    
    esg-cli process data/raw.xlsx --output-dir ./clean --format excel
    """
    
    processor = ESGDataProcessor()
    
    try:
        click.echo(f"📁 Processing file: {file_path}")
        
        # Read file
        df, metadata = processor.read_file(file_path)
        click.echo(f"📊 File loaded: {metadata['row_count']} rows, {metadata['column_count']} columns")
        
        # Validate data
        validation_report = processor.validate_esg_data(df, entity_type)
        click.echo(f"🔍 Data quality score: {validation_report['data_quality_score']:.1f}/100")
        
        if validation_report['issues']:
            click.echo("❌ Data issues found:")
            for issue in validation_report['issues']:
                click.echo(f"  • {issue}")
        
        if validation_report['warnings']:
            click.echo("⚠️  Data warnings:")
            for warning in validation_report['warnings']:
                click.echo(f"  • {warning}")
        
        # Clean data
        cleaned_df, cleaning_report = processor.clean_data(df, validation_report)
        click.echo(f"🧹 Data cleaned: {len(cleaning_report['actions_performed'])} actions performed")
        
        for action in cleaning_report['actions_performed']:
            click.echo(f"  • {action}")
        
        # Save processed data
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        input_name = Path(file_path).stem
        output_file = output_path / f"processed_{input_name}.{output_format}"
        
        save_report = processor.save_processed_data(cleaned_df, str(output_file), output_format)
        
        if save_report['success']:
            click.echo(f"✅ Processing complete!")
            click.echo(f"💾 Processed file saved: {output_file}")
            click.echo(f"📏 Output size: {save_report['file_size_mb']:.2f} MB")
            
            # Save processing report
            report_file = output_path / f"processing_report_{input_name}.json"
            full_report = {
                "file_metadata": metadata,
                "validation": validation_report,
                "cleaning": cleaning_report,
                "save": save_report
            }
            
            with open(report_file, 'w') as f:
                json.dump(full_report, f, indent=2, default=str)
            
            click.echo(f"📋 Processing report saved: {report_file}")
        else:
            click.echo(f"❌ Failed to save processed data: {save_report.get('error')}", err=True)
            
    except Exception as e:
        click.echo(f"❌ Processing error: {e}", err=True)


@cli.command()
def config():
    """Show current configuration settings."""
    
    click.echo("⚙️  ESG Reporting Configuration")
    click.echo("=" * 40)
    click.echo(f"Storage Account: {settings.azure_storage_account_name}")
    click.echo(f"Container Name: {settings.azure_container_name}")
    click.echo(f"Key Vault URL: {settings.azure_key_vault_url or 'Not configured'}")
    click.echo(f"Batch Size: {settings.batch_size}")
    click.echo(f"Max File Size: {settings.max_file_size_mb} MB")
    click.echo(f"Parallel Upload Threshold: {settings.parallel_upload_threshold_mb} MB")
    click.echo(f"Log Level: {settings.log_level}")
    click.echo(f"Azure Monitor: {'Enabled' if settings.enable_azure_monitor else 'Disabled'}")


if __name__ == '__main__':
    cli()
