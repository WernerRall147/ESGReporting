"""
Command-line interface for ESG Reporting solution.

This module provides an easy-to-use CLI for all ESG data operations,
following Azure best practices and providing comprehensive error handling.
"""

import click
import asyncio
import logging
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from .config import settings
from .storage import ESGBlobStorageClient
from .processor import ESGDataProcessor
from .carbon_optimization import CarbonOptimizationClient, EmissionsQuery, ReportType, EmissionScope, CategoryType


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
    
    click.echo("ESG Reporting Configuration")
    click.echo("=" * 40)
    click.echo(f"Storage Account: {settings.azure_storage_account_name}")
    click.echo(f"Container Name: {settings.azure_container_name}")
    click.echo(f"Key Vault URL: {settings.azure_key_vault_url or 'Not configured'}")
    click.echo(f"Batch Size: {settings.batch_size}")
    click.echo(f"Max File Size: {settings.max_file_size_mb} MB")
    click.echo(f"Parallel Upload Threshold: {settings.parallel_upload_threshold_mb} MB")
    click.echo(f"Log Level: {settings.log_level}")
    click.echo(f"Azure Monitor: {'Enabled' if settings.enable_azure_monitor else 'Disabled'}")


@cli.group()
def azure():
    """Azure Carbon Optimization integration commands."""
    pass


@azure.command('fetch')
@click.option('--subscription-id', required=True, help='Azure subscription ID')
@click.option('--report-type', 
              type=click.Choice(['monthly_summary', 'overall_summary', 'resource_details', 'top_emitters']),
              default='monthly_summary',
              help='Type of emissions report to fetch')
@click.option('--start-date', help='Start date (YYYY-MM-DD), defaults to 30 days ago')
@click.option('--end-date', help='End date (YYYY-MM-DD), defaults to today')
@click.option('--output', '-o', help='Output file path (CSV format)')
@click.option('--scope', 
              type=click.Choice(['scope1', 'scope2', 'scope3']),
              multiple=True,
              help='Emission scopes to include (can specify multiple)')
def fetch_emissions(subscription_id, report_type, start_date, end_date, output, scope):
    """Fetch emissions data from Azure Carbon Optimization.
    
    Note: This command requires Azure CLI authentication or managed identity.
    Run 'az login' first to authenticate.
    """
    try:
        # Set up dates
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Convert scope strings to enums
        scopes = []
        if scope:
            scope_map = {
                'scope1': EmissionScope.SCOPE1,
                'scope2': EmissionScope.SCOPE2,
                'scope3': EmissionScope.SCOPE3
            }
            scopes = [scope_map[s] for s in scope]
        else:
            scopes = [EmissionScope.SCOPE1, EmissionScope.SCOPE2]  # Default scopes
          # Create client and query
        client = CarbonOptimizationClient()
        
        # Create date range
        from .carbon_optimization import DateRange
        date_range = DateRange(start=start_date, end=end_date)
        
        query = EmissionsQuery(
            report_type=report_type_map[report_type],
            subscription_list=[subscription_id],
            carbon_scope_list=scopes,
            date_range=date_range
        )
        
        click.echo(f"Fetching {report_type} emissions data from {start_date} to {end_date}...")
        click.echo(f"Subscription: {subscription_id}")
        
        # Fetch data based on report type
        report_type_map = {
            'monthly_summary': ReportType.MONTHLY_SUMMARY,
            'overall_summary': ReportType.OVERALL_SUMMARY,
            'resource_details': ReportType.RESOURCE_DETAILS,
            'top_emitters': ReportType.TOP_EMITTERS
        }
        
        df = client.get_emissions_data(query, report_type_map[report_type])
        
        if df.empty:
            click.echo("No emissions data found for the specified criteria.")
            return
        
        click.echo(f"Retrieved {len(df)} records.")
        
        # Output results
        if output:
            df.to_csv(output, index=False)
            click.echo(f"Data saved to {output}")
        else:
            click.echo("\nSample data:")
            click.echo(df.head().to_string())
            
    except Exception as e:
        click.echo(f"Error fetching emissions data: {e}", err=True)
        click.echo("Note: Ensure you are authenticated with Azure CLI (run 'az login')", err=True)
        raise click.ClickException(str(e))


@azure.command('integrate')
@click.option('--emissions-file', required=True, help='Path to emissions CSV file')
@click.option('--activities-file', help='Path to activities CSV file')
@click.option('--output-dir', default='output', help='Output directory for integrated reports')
@click.option('--subscription-id', help='Azure subscription ID for metadata')
def integrate_emissions(emissions_file, activities_file, output_dir, subscription_id):
    """Integrate Azure emissions data with ESG reporting."""
    try:
        click.echo("Integrating Azure emissions data with ESG reporting...")
        
        # Load emissions data
        emissions_df = pd.read_csv(emissions_file)
        click.echo(f"Loaded {len(emissions_df)} emissions records.")
          # Initialize processor
        processor = ESGDataProcessor()
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Process emissions data for ESG reporting
        if activities_file and Path(activities_file).exists():
            activities_df = pd.read_csv(activities_file)
            click.echo(f"Loaded {len(activities_df)} activity records.")
            
            # Combine with activities data
            integrated_df = processor.integrate_with_activities(emissions_df, activities_df)
        else:
            # Use emissions data directly
            integrated_df = emissions_df.copy()
        
        # Add metadata
        integrated_df['data_source'] = 'Azure Carbon Optimization'
        integrated_df['subscription_id'] = subscription_id or 'unknown'
        integrated_df['integration_timestamp'] = datetime.now().isoformat()
        
        # Generate reports
        report_file = output_path / f"integrated_emissions_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        integrated_df.to_csv(report_file, index=False)
        
        # Generate summary
        summary_file = output_path / f"emissions_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        summary = processor.generate_summary(integrated_df)
        summary.to_csv(summary_file, index=False)
        
        click.echo(f"Integration complete!")
        click.echo(f"Integrated report: {report_file}")
        click.echo(f"Summary report: {summary_file}")
        click.echo(f"Total CO2 equivalent: {integrated_df.get('total_emissions_kg_co2', integrated_df.get('emissions_kg_co2', [0])).sum():.2f} kg")
        
    except Exception as e:
        click.echo(f"Error integrating emissions data: {e}", err=True)
        raise click.ClickException(str(e))


@azure.command('list-subscriptions')
def list_subscriptions():
    """List available Azure subscriptions for emissions data.
    
    Note: This command requires Azure CLI authentication or managed identity.
    Run 'az login' first to authenticate.
    """
    try:
        click.echo("Listing available Azure subscriptions...")
        
        # For now, we'll use a placeholder since subscription listing requires different API
        # In a real implementation, you'd use Azure Resource Manager API
        click.echo("Note: This command requires Azure Resource Manager API integration.")
        click.echo("Please use the Azure CLI 'az account list' command to list subscriptions.")
        click.echo("Then use the subscription ID with the 'fetch' command.")
        
    except Exception as e:
        click.echo(f"Error listing subscriptions: {e}", err=True)
        raise click.ClickException(str(e))


if __name__ == '__main__':
    cli()
