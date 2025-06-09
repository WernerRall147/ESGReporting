"""
Enhanced Interactive Demo for ESG Reporting Solution with Azure Carbon Optimization.

This demo showcases the complete ESG reporting pipeline including:
1. Traditional ESG data processing (sample data)
2. Azure Carbon Optimization API integration (real Azure emissions)
3. Unified reporting and analytics
"""

import os
import sys
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.ENDC):
    """Print colored message to terminal."""
    print(f"{color}{message}{Colors.ENDC}")

def print_header(title):
    """Print section header."""
    print()
    print("=" * 80)
    print_colored(f"🌍 {title}", Colors.HEADER + Colors.BOLD)
    print("=" * 80)

def print_step(step_num, title):
    """Print step header."""
    print()
    print_colored(f"📊 STEP {step_num}: {title.upper()}", Colors.CYAN + Colors.BOLD)
    print("=" * 60)

def wait_for_user():
    """Wait for user to press Enter."""
    input(print_colored("\n⏸️  Press Enter to continue...", Colors.YELLOW))

def run_command(cmd, description=None):
    """Run command and display output."""
    if description:
        print_colored(f"\n🔄 {description}", Colors.BLUE)
        print_colored(f"💻 Command: {cmd}", Colors.CYAN)
    
    print_colored("📋 Output:", Colors.GREEN)
    print("-" * 40)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print_colored("⚠️ Errors/Warnings: " + result.stderr, Colors.YELLOW)
        
        if result.returncode != 0:
            print_colored(f"❌ Command failed with exit code: {result.returncode}", Colors.RED)
        else:
            print_colored("✅ Command completed successfully", Colors.GREEN)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print_colored("⏰ Command timed out", Colors.RED)
        return False
    except Exception as e:
        print_colored(f"❌ Command error: {e}", Colors.RED)
        return False
    finally:
        print("-" * 40)

def check_file_exists(file_path):
    """Check if file exists and show basic info."""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print_colored(f"✅ File exists: {file_path} ({size:,} bytes)", Colors.GREEN)
        return True
    else:
        print_colored(f"❌ File not found: {file_path}", Colors.RED)
        return False

def show_file_preview(file_path, lines=3):
    """Show preview of CSV file."""
    try:
        with open(file_path, 'r') as f:
            lines_data = f.readlines()
        
        print_colored(f"📄 File: {Path(file_path).name}", Colors.BLUE)
        print_colored(f"📏 Size: {len(lines_data)} rows", Colors.CYAN)
        print_colored(f"📋 Preview (first {lines} rows):", Colors.GREEN)
        
        for i, line in enumerate(lines_data[:lines+1]):  # +1 for header
            prefix = "Header" if i == 0 else f"Row {i}"
            print(f"   {prefix}: {line.strip()}")
            
    except Exception as e:
        print_colored(f"❌ Error reading file: {e}", Colors.RED)

def main():
    """Main demo function."""
    print_header("ESG REPORTING SOLUTION - ENHANCED INTERACTIVE DEMO")
    
    print_colored("🌍 Welcome to the Enhanced ESG Reporting Solution Demo!", Colors.GREEN + Colors.BOLD)
    print("This demonstration showcases our Azure-based ESG data management platform")
    print("with integrated Azure Carbon Optimization for real emissions data.")
    print()
    print_colored("📋 Demo Overview:", Colors.BLUE)
    print("  🔧 Environment setup and verification")
    print("  📊 Sample ESG data overview")  
    print("  🌍 Azure Carbon Optimization integration")
    print("  💻 Enhanced CLI commands and usage")
    print("  🔍 Data validation capabilities")
    print("  ☁️ Azure Blob Storage upload/download")
    print("  📊 Unified reporting and analytics")
    print("  📈 Monitoring and observability")
    print("  💼 Business value and use cases")
    
    wait_for_user()
    
    # Step 1: Environment Setup
    print_step(1, "Environment Setup and Verification")
    
    print_colored("📋 Azure Environment Information:", Colors.BLUE)
    
    # Get Azure environment variables
    storage_account = os.getenv('AZURE_STORAGE_ACCOUNT_NAME', 'Not configured')
    key_vault_url = os.getenv('AZURE_KEY_VAULT_URL', 'Not configured')
    client_id = os.getenv('AZURE_CLIENT_ID', 'Not configured')
    container_registry = os.getenv('AZURE_CONTAINER_REGISTRY_ENDPOINT', 'Not configured')
    
    print_colored("✅ Deployed Infrastructure:", Colors.GREEN)
    print(f"  🏗️ Resource Group: rg-esgdemo")
    print(f"  💾 Storage Account: {storage_account}")
    print(f"  🔐 Key Vault: {key_vault_url}")
    print(f"  📦 Container Registry: {container_registry}")
    print(f"  🚀 Container App: ca-esg-ra3xkg7cwqzzg")
    print(f"  📊 Application Insights: appi-esg-ra3xkg7cwqzzg")
    print(f"  📋 Log Analytics: log-esg-ra3xkg7cwqzzg")
    print(f"  🔑 Managed Identity: {client_id}")
    
    print()
    print_colored("🔗 Access URLs:", Colors.BLUE)
    print(f"  🌐 Container App: https://ca-esg-ra3xkg7cwqzzg.agreeablemushroom-8e78fbcf.eastus.azurecontainerapps.io")
    print(f"  🔐 Key Vault: {key_vault_url}")
    print(f"  💾 Storage: https://{storage_account}.blob.core.windows.net/")
    
    wait_for_user()
    
    # Step 2: Sample Data Overview
    print_step(2, "Sample ESG Data Overview")
    
    sample_files = [
        ("sample_emissions.csv", "CO2 emissions, energy usage, water consumption"),
        ("sample_activities.csv", "ESG training, audits, assessments"),
        ("sample_suppliers.csv", "Supplier ESG scores and certifications")
    ]
    
    for file_path, description in sample_files:
        if check_file_exists(file_path):
            print_colored(f"📝 {description}", Colors.CYAN)
            show_file_preview(file_path)
            print()
    
    wait_for_user()
    
    # Step 3: Azure Carbon Optimization Integration
    print_step(3, "Azure Carbon Optimization Integration")
    
    print_colored("🌍 This is the game-changer! We can now fetch REAL Azure emissions data", Colors.GREEN + Colors.BOLD)
    print("from your Azure infrastructure using the Carbon Optimization API.")
    print()
      # Show Azure integration capabilities
    print_colored("📋 Note: Real Azure emissions data requires authentication credentials:", Colors.YELLOW)
    print("  • Azure Subscription ID")
    print("  • Azure Tenant ID") 
    print("  • Azure Client ID (Service Principal)")
    print("  • Azure Client Secret")
    print()
    print_colored("� Example command to fetch emissions data:", Colors.CYAN)
    print("python -m src.esg_reporting.cli azure fetch \\")
    print("  --subscription-id YOUR_SUBSCRIPTION_ID \\")
    print("  --tenant-id YOUR_TENANT_ID \\")
    print("  --client-id YOUR_CLIENT_ID \\")
    print("  --client-secret YOUR_CLIENT_SECRET \\")
    print("  --report-type monthly_summary \\")
    print("  --start-date 2024-01-01 \\")
    print("  --end-date 2024-12-31 \\")
    print("  --output azure_emissions.csv")
    print()
    
    # Show available commands
    print_colored("� Available Azure Carbon Optimization commands:", Colors.BLUE)
    run_command(
        "python -m src.esg_reporting.cli azure --help",
        "Available Azure Carbon Optimization commands"
    )
    
    wait_for_user()
    
    # Show fetch command details
    run_command(
        "python -m src.esg_reporting.cli azure fetch --help",
        "Detailed options for fetching emissions data"
    )
    
    wait_for_user()
    
    # Step 4: Enhanced CLI Commands
    print_step(4, "Enhanced ESG Reporting CLI Commands")
    
    print_colored("💻 Available CLI Commands:", Colors.BLUE)
    print()
    
    cli_commands = [
        ("python -m src.esg_reporting.cli --help", "Show main CLI help"),
        ("python -m src.esg_reporting.cli azure --help", "Show Azure integration commands"),
        ("python -m src.esg_reporting.cli upload --help", "Show upload command help"),
        ("python -m src.esg_reporting.cli validate --help", "Show validate command help"),
        ("python -m src.esg_reporting.cli process --help", "Show process command help")
    ]
    
    for cmd, description in cli_commands:
        run_command(cmd, description)
        print()
    
    wait_for_user()
      # Step 5: Data Validation Examples
    print_step(5, "Data Validation Examples")
    
    print_colored("🔍 Validating sample ESG data files...", Colors.BLUE)
    print()
    
    validation_commands = [
        ("sample_emissions.csv", "emissions"),
        ("sample_activities.csv", "activities"),
        ("sample_suppliers.csv", "suppliers")
    ]
    
    for file_path, entity_type in validation_commands:
        if check_file_exists(file_path):
            run_command(
                f"python -m src.esg_reporting.cli process {file_path} --entity-type {entity_type}",
                f"Process and validate {entity_type} data"
            )
            print()
    
    wait_for_user()
    
    # Step 6: Azure Integration Demo
    print_step(6, "Azure Blob Storage Integration")
    
    print_colored("☁️ Demonstrating Azure Blob Storage operations...", Colors.BLUE)
    print("(Note: Requires Azure credentials configured)")
    print()
    
    # Upload sample data
    for file_path, entity_type in [("sample_emissions.csv", "emissions")]:
        if check_file_exists(file_path):
            run_command(
                f"python -m src.esg_reporting.cli upload {file_path} --entity-type {entity_type} --validate",
                f"Upload and validate {entity_type} data"
            )
            print()
    
    # List blob storage contents
    run_command(
        "python -m src.esg_reporting.cli list-files",
        "List files in Azure Blob Storage"
    )
    
    wait_for_user()
    
    # Step 7: Unified Reporting
    print_step(7, "Unified ESG Reporting")
    
    print_colored("📊 Combining traditional ESG data with Azure emissions...", Colors.BLUE)
    print()
      # Show Azure integration example
    print_colored("💡 Example Azure emissions integration:", Colors.CYAN)
    print("python -m src.esg_reporting.cli azure integrate \\")
    print("  --emissions-file azure_emissions.csv \\") 
    print("  --activities-file sample_activities.csv \\")
    print("  --output-dir integrated_reports")
    print()
    
    wait_for_user()
    
    # Step 8: Configuration and Monitoring
    print_step(8, "Configuration and Monitoring")
    
    print_colored("⚙️ Current system configuration:", Colors.BLUE)
    run_command(
        "python -m src.esg_reporting.cli config",
        "Show current configuration"
    )
    
    print()
    print_colored("📈 Monitoring capabilities:", Colors.CYAN)
    print("  📊 Azure Monitor integration for logging and metrics")
    print("  🔍 Application Insights for performance monitoring")  
    print("  📋 Log Analytics workspace for centralized logging")
    print("  🚨 Custom alerts for data quality and processing errors")
    print("  📊 Power BI integration for ESG dashboards")
    
    wait_for_user()
    
    # Step 9: Business Value Summary
    print_step(9, "Business Value and Use Cases")
    
    print_colored("💼 Key Business Benefits:", Colors.GREEN + Colors.BOLD)
    print()
    print_colored("🎯 Real-time Azure Infrastructure Emissions:", Colors.BLUE)
    print("  • Automatic tracking of your Azure carbon footprint")
    print("  • Service-level and region-level emissions breakdown")
    print("  • Integration with sustainability reporting frameworks")
    print()
    print_colored("🔄 Automated ESG Data Pipeline:", Colors.BLUE) 
    print("  • Seamless integration with Microsoft Sustainability Manager")
    print("  • Automated validation and quality checks")
    print("  • Secure Azure-native storage and processing")
    print()
    print_colored("📊 Unified Reporting and Analytics:", Colors.BLUE)
    print("  • Combined traditional ESG data with cloud emissions")
    print("  • Power BI dashboards for executive reporting")
    print("  • Compliance with GRI, SASB, and TCFD frameworks")
    print()
    print_colored("🔒 Enterprise Security and Compliance:", Colors.BLUE)
    print("  • Managed identity authentication (no passwords)")
    print("  • Azure Key Vault for secrets management")
    print("  • Data encryption in transit and at rest")
    print("  • Audit trails and compliance reporting")
    
    print()
    print_colored("🚀 Next Steps:", Colors.YELLOW + Colors.BOLD)
    print("  1. Configure automatic Azure emissions data collection")
    print("  2. Set up Power Automate flows for MSM data export")
    print("  3. Create Power BI dashboards for stakeholder reporting")
    print("  4. Implement automated alerts for ESG KPI thresholds")
    print("  5. Integrate with existing business intelligence systems")
    
    print()
    print_header("DEMO COMPLETE")
    print_colored("🎉 Thank you for exploring the ESG Reporting Solution!", Colors.GREEN + Colors.BOLD)
    print_colored("📧 For questions or implementation support, please reach out to the development team.", Colors.CYAN)
    print_colored("🔗 Documentation and code samples are available in the repository.", Colors.CYAN)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n⏹️  Demo interrupted by user. Thank you!", Colors.YELLOW)
    except Exception as e:
        print_colored(f"\n\n❌ Demo error: {e}", Colors.RED)
        sys.exit(1)
