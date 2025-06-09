"""
Azure Carbon Optimization API integration for ESG Reporting.

This module provides functionality to fetch real emissions data from Azure's
Carbon Optimization service and integrate it with our ESG reporting pipeline.

Reference: https://learn.microsoft.com/en-us/azure/carbon-optimization/api-export-data
API Reference: https://learn.microsoft.com/en-us/rest/api/carbon/carbon-service/list-carbon-emission-reports
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum

import pandas as pd
import requests
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.core.exceptions import AzureError

logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Available Carbon Optimization report types per official API."""
    OVERALL_SUMMARY_REPORT = "OverallSummaryReport"
    MONTHLY_SUMMARY_REPORT = "MonthlySummaryReport"
    TOP_ITEMS_SUMMARY_REPORT = "TopItemsSummaryReport"
    TOP_ITEMS_MONTHLY_SUMMARY_REPORT = "TopItemsMonthlySummaryReport"
    ITEM_DETAILS_REPORT = "ItemDetailsReport"


class EmissionScope(Enum):
    """Carbon emission scopes."""
    SCOPE1 = "Scope1"
    SCOPE2 = "Scope2"
    SCOPE3 = "Scope3"


class CategoryType(Enum):
    """Category types for detailed emissions data."""
    RESOURCE = "Resource"
    RESOURCE_GROUP = "ResourceGroup"
    RESOURCE_TYPE = "ResourceType"
    LOCATION = "Location"
    SUBSCRIPTION = "Subscription"


class OrderByColumn(Enum):
    """Order by column options."""
    LATEST_MONTH_EMISSIONS = "LatestMonthEmissions"
    PREVIOUS_MONTH_EMISSIONS = "PreviousMonthEmissions"
    MONTH_OVER_MONTH_CHANGE = "MonthOverMonthEmissionsChangeRatio"


class SortDirection(Enum):
    """Sort direction options."""
    ASC = "Asc"
    DESC = "Desc"


@dataclass
class DateRange:
    """Date range for emissions data query."""
    start: str  # Format: YYYY-MM-DD
    end: str    # Format: YYYY-MM-DD


@dataclass
class EmissionsQuery:
    """Configuration for emissions data query."""
    report_type: ReportType
    subscription_list: List[str]
    carbon_scope_list: List[EmissionScope]
    date_range: DateRange
    
    # Optional filters
    location_list: Optional[List[str]] = None
    resource_group_url_list: Optional[List[str]] = None
    resource_type_list: Optional[List[str]] = None
    
    # For ItemDetailsReport
    category_type: Optional[CategoryType] = None
    order_by: Optional[OrderByColumn] = None
    sort_direction: Optional[SortDirection] = None
    page_size: Optional[int] = None
    skip_token: Optional[str] = None
    
    # For TopItems reports
    top_items: Optional[int] = None


class CarbonOptimizationClient:
    """
    Client for Azure Carbon Optimization API.
    
    Provides methods to fetch emissions data from Azure's Carbon Optimization
    service using managed identity authentication.
    
    Implements the official Microsoft Carbon Service REST API:
    https://learn.microsoft.com/en-us/rest/api/carbon/carbon-service/list-carbon-emission-reports
    """
    
    BASE_URL = "https://management.azure.com"
    API_VERSION = "2025-04-01"
    ENDPOINT = "/providers/Microsoft.Carbon/carbonEmissionReports"
    
    def __init__(self, credential: Optional[DefaultAzureCredential] = None):
        """
        Initialize the Carbon Optimization client.
        
        Args:
            credential: Azure credential for authentication. If None, uses DefaultAzureCredential.
        """
        self.credential = credential or DefaultAzureCredential()
        self.session = requests.Session()
        self._access_token = None
        self._token_expires_at = None
        
        logger.info("Initialized Carbon Optimization client with managed identity")
    
    def _get_access_token(self) -> str:
        """
        Get or refresh Azure access token.
        
        Returns:
            Valid access token for Azure Management API.
        """
        try:
            # Check if token needs refresh (refresh 5 minutes before expiry)
            if (self._access_token is None or 
                self._token_expires_at is None or 
                datetime.now() >= self._token_expires_at - timedelta(minutes=5)):
                
                logger.debug("Refreshing Azure access token")
                token = self.credential.get_token("https://management.azure.com/.default")
                self._access_token = token.token
                self._token_expires_at = datetime.fromtimestamp(token.expires_on)
                logger.debug(f"Token expires at: {self._token_expires_at}")
                
            return self._access_token
            
        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            raise AzureError(f"Authentication failed: {e}")
    
    def _build_request_payload(self, query: EmissionsQuery) -> Dict[str, Any]:
        """
        Build request payload according to API specification.
        
        Args:
            query: Emissions query configuration
            
        Returns:
            Request payload dictionary
        """
        # Base payload with required fields
        payload = {
            "reportType": query.report_type.value,
            "subscriptionList": [sub.lower() for sub in query.subscription_list],  # API requires lowercase
            "carbonScopeList": [scope.value for scope in query.carbon_scope_list],
            "dateRange": {
                "start": query.date_range.start,
                "end": query.date_range.end
            }
        }
        
        # Add optional filters
        if query.location_list:
            payload["locationList"] = [loc.lower() for loc in query.location_list]
        if query.resource_group_url_list:
            payload["resourceGroupUrlList"] = [url.lower() for url in query.resource_group_url_list]
        if query.resource_type_list:
            payload["resourceTypeList"] = [rt.lower() for rt in query.resource_type_list]
        
        # Add report-specific parameters
        if query.report_type in [ReportType.ITEM_DETAILS_REPORT]:
            if query.category_type:
                payload["categoryType"] = query.category_type.value
            if query.order_by:
                payload["orderBy"] = query.order_by.value
            if query.sort_direction:
                payload["sortDirection"] = query.sort_direction.value
            if query.page_size:
                payload["pageSize"] = min(query.page_size, 5000)  # API max is 5000
            if query.skip_token:
                payload["skipToken"] = query.skip_token
        
        if query.report_type in [ReportType.TOP_ITEMS_SUMMARY_REPORT, ReportType.TOP_ITEMS_MONTHLY_SUMMARY_REPORT]:
            if query.category_type:
                payload["categoryType"] = query.category_type.value
            if query.top_items:
                payload["topItems"] = min(query.top_items, 10)  # API max is 10
        
        return payload
    
    def _make_post_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make authenticated POST request to Azure Carbon Optimization API.
        
        Args:
            payload: Request payload
            
        Returns:
            API response as dictionary
        """
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.BASE_URL}{self.ENDPOINT}"
        params = {"api-version": self.API_VERSION}
        
        try:
            logger.debug(f"Making POST request to: {url}")
            logger.debug(f"Request payload: {json.dumps(payload, indent=2)}")
            
            response = self.session.post(
                url, 
                headers=headers, 
                params=params, 
                json=payload,
                timeout=120  # Extended timeout for large datasets
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Successfully retrieved emissions data with {len(result.get('value', []))} records")
            return result
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise AzureError(f"Carbon Optimization API HTTP error: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error occurred: {e}")
            raise AzureError(f"Carbon Optimization API request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API response: {e}")
            raise AzureError(f"Invalid API response format: {e}")
    
    def get_emissions_data(self, query: EmissionsQuery) -> pd.DataFrame:
        """
        Fetch emissions data from Azure Carbon Optimization API.
        
        Args:
            query: Emissions query configuration
            
        Returns:
            DataFrame containing emissions data
        """
        logger.info(f"Fetching {query.report_type.value} for {len(query.subscription_list)} subscriptions")
        logger.info(f"Date range: {query.date_range.start} to {query.date_range.end}")
        
        # Build and send request
        payload = self._build_request_payload(query)
        response = self._make_post_request(payload)
        
        # Process subscription access decisions
        access_decisions = response.get("subscriptionAccessDecisionList", [])
        denied_subs = [decision for decision in access_decisions if decision.get("decision") == "Denied"]
        if denied_subs:
            logger.warning(f"Access denied for {len(denied_subs)} subscriptions:")
            for denied in denied_subs:
                reason = denied.get("denialReason", "Unknown reason")
                logger.warning(f"  - {denied.get('subscriptionId')}: {reason}")
        
        # Convert to DataFrame
        data = response.get("value", [])
        if not data:
            logger.warning("No emissions data returned from API")
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        # Add metadata columns
        df["report_type"] = query.report_type.value
        df["query_date_start"] = query.date_range.start
        df["query_date_end"] = query.date_range.end
        df["retrieved_at"] = datetime.now().isoformat()
        
        logger.info(f"Successfully processed {len(df)} emissions records")
        return df    
    def get_monthly_summary(self, subscription_ids: List[str], start_date: str, end_date: str, 
                          carbon_scopes: Optional[List[EmissionScope]] = None) -> pd.DataFrame:
        """
        Get monthly summary emissions report for specified subscriptions.
        
        Args:
            subscription_ids: List of Azure subscription IDs
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            carbon_scopes: List of emission scopes to include (default: all scopes)
            
        Returns:
            DataFrame with monthly emissions summary
        """
        if carbon_scopes is None:
            carbon_scopes = [EmissionScope.SCOPE1, EmissionScope.SCOPE2, EmissionScope.SCOPE3]
        
        query = EmissionsQuery(
            report_type=ReportType.MONTHLY_SUMMARY_REPORT,
            subscription_list=subscription_ids,
            carbon_scope_list=carbon_scopes,
            date_range=DateRange(start=start_date, end=end_date)
        )
        
        return self.get_emissions_data(query)
    
    def get_overall_summary(self, subscription_ids: List[str], start_date: str, end_date: str,
                          carbon_scopes: Optional[List[EmissionScope]] = None) -> pd.DataFrame:
        """
        Get overall summary emissions report for specified subscriptions.
        
        Args:
            subscription_ids: List of Azure subscription IDs
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            carbon_scopes: List of emission scopes to include (default: all scopes)
            
        Returns:
            DataFrame with overall emissions summary
        """
        if carbon_scopes is None:
            carbon_scopes = [EmissionScope.SCOPE1, EmissionScope.SCOPE2, EmissionScope.SCOPE3]
        
        query = EmissionsQuery(
            report_type=ReportType.OVERALL_SUMMARY_REPORT,
            subscription_list=subscription_ids,
            carbon_scope_list=carbon_scopes,
            date_range=DateRange(start=start_date, end=end_date)
        )
        
        return self.get_emissions_data(query)
    
    def get_resource_details(self, subscription_ids: List[str], date: str,
                           category_type: CategoryType = CategoryType.RESOURCE,
                           carbon_scopes: Optional[List[EmissionScope]] = None,
                           page_size: int = 1000) -> pd.DataFrame:
        """
        Get detailed emissions data by resource, resource group, or other category.
        
        Args:
            subscription_ids: List of Azure subscription IDs
            date: Date in YYYY-MM-DD format (same start and end for ItemDetailsReport)
            category_type: Category type for detailed breakdown
            carbon_scopes: List of emission scopes to include (default: all scopes)
            page_size: Number of items per page (max 5000)
            
        Returns:
            DataFrame with detailed emissions data
        """
        if carbon_scopes is None:
            carbon_scopes = [EmissionScope.SCOPE1, EmissionScope.SCOPE2, EmissionScope.SCOPE3]
        
        query = EmissionsQuery(
            report_type=ReportType.ITEM_DETAILS_REPORT,
            subscription_list=subscription_ids,
            carbon_scope_list=carbon_scopes,
            date_range=DateRange(start=date, end=date),  # Same date for ItemDetailsReport
            category_type=category_type,
            order_by=OrderByColumn.LATEST_MONTH_EMISSIONS,
            sort_direction=SortDirection.DESC,
            page_size=min(page_size, 5000)
        )
        
        return self.get_emissions_data(query)
    
    def get_top_emitters(self, subscription_ids: List[str], date: str,
                        category_type: CategoryType = CategoryType.RESOURCE,
                        top_items: int = 10,
                        carbon_scopes: Optional[List[EmissionScope]] = None) -> pd.DataFrame:
        """
        Get top emitting items for a specific category.
        
        Args:
            subscription_ids: List of Azure subscription IDs
            date: Date in YYYY-MM-DD format
            category_type: Category type for top items analysis
            top_items: Number of top items to return (max 10)
            carbon_scopes: List of emission scopes to include (default: all scopes)
            
        Returns:
            DataFrame with top emitting items
        """
        if carbon_scopes is None:
            carbon_scopes = [EmissionScope.SCOPE1, EmissionScope.SCOPE2, EmissionScope.SCOPE3]
        
        query = EmissionsQuery(            report_type=ReportType.TOP_ITEMS_SUMMARY_REPORT,
            subscription_list=subscription_ids,
            carbon_scope_list=carbon_scopes,
            date_range=DateRange(start=date, end=date),
            category_type=category_type,
            top_items=min(top_items, 10)
        )
        
        return self.get_emissions_data(query)


def create_sample_query(subscription_id: str) -> EmissionsQuery:
    # Query for the previous month's data
    from datetime import datetime, timedelta
    
    # Get last month's date range
    today = datetime.now()
    first_day_current_month = today.replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    first_day_previous_month = last_day_previous_month.replace(day=1)
    
    start_date = first_day_previous_month.strftime("%Y-%m-%d")
    end_date = last_day_previous_month.strftime("%Y-%m-%d")
    
    return EmissionsQuery(
        report_type=ReportType.MONTHLY_SUMMARY_REPORT,
        subscription_list=[subscription_id],
        carbon_scope_list=[EmissionScope.SCOPE1, EmissionScope.SCOPE2, EmissionScope.SCOPE3],
        date_range=DateRange(start=start_date, end=end_date)
    )


def format_emissions_for_esg_report(emissions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Format Azure emissions data for integration with ESG reporting system.
    
    Args:
        emissions_df: Raw emissions data from Carbon Optimization API
        
    Returns:
        Formatted DataFrame ready for ESG reporting
    """
    if emissions_df.empty:
        logger.warning("Empty emissions dataset provided for formatting")
        return pd.DataFrame()
    
    try:
        # Create standardized ESG format
        esg_data = []
        
        for _, row in emissions_df.iterrows():
            # Extract common fields
            base_record = {
                "activity_type": "azure_cloud_emissions",
                "source": "Azure Carbon Optimization",
                "scope": "Scope 2",  # Cloud services are typically Scope 2
                "date": row.get("query_date_start", datetime.now().strftime("%Y-%m-%d")),
                "data_quality": "High",  # Azure provides high-quality data
                "verification_status": "Third-party verified",
                "retrieved_at": row.get("retrieved_at", datetime.now().isoformat())
            }
            
            # Handle different data types from the API response
            if "dataType" in row:
                data_type = row["dataType"]
                
                if "SummaryData" in data_type:
                    # Summary data format
                    record = base_record.copy()
                    record.update({
                        "emissions_co2_kg": row.get("latestMonthEmissions", 0),
                        "previous_period_emissions": row.get("previousMonthEmissions", 0),
                        "change_ratio": row.get("monthOverMonthEmissionsChangeRatio", 0),
                        "description": f"Azure Cloud Emissions Summary - {data_type}"
                    })
                    esg_data.append(record)
                
                elif "ResourceItemDetailsData" in data_type:
                    # Resource-level detail data
                    record = base_record.copy()
                    record.update({
                        "emissions_co2_kg": row.get("latestMonthEmissions", 0),
                        "resource_name": row.get("itemName", "Unknown"),
                        "resource_group": row.get("resourceGroup", "Unknown"),
                        "resource_type": row.get("resourceType", "Unknown"),
                        "location": row.get("location", "Unknown"),
                        "subscription_id": row.get("subscriptionId", "Unknown"),
                        "description": f"Azure Resource Emissions - {row.get('itemName', 'Unknown')}"
                    })
                    esg_data.append(record)
            
            else:
                # Generic handling for other response formats
                record = base_record.copy()
                record.update({
                    "emissions_co2_kg": row.get("latestMonthEmissions", row.get("totalEmissions", 0)),
                    "description": f"Azure Cloud Emissions - {row.get('report_type', 'General')}"
                })
                esg_data.append(record)
        
        result_df = pd.DataFrame(esg_data)
        logger.info(f"Successfully formatted {len(result_df)} emissions records for ESG reporting")
        return result_df
        
    except Exception as e:
        logger.error(f"Failed to format emissions data for ESG reporting: {e}")
        raise ValueError(f"Emissions data formatting error: {e}")


    def export_emissions_to_csv(self, query: EmissionsQuery, output_path: str) -> str:
        """
        Fetch emissions data and export to CSV file.
        
        Args:
            query: Emissions query configuration
            output_path: Path to save CSV file
            
        Returns:
            Path to the saved CSV file
        """
        logger.info(f"Exporting emissions data to: {output_path}")
        
        # Fetch data
        df = self.get_emissions_data(query)
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        
        logger.info(f"Successfully exported {len(df)} records to {output_path}")
        return output_path
    
    def get_available_subscriptions(self) -> List[Dict[str, str]]:
        """
        Get list of available subscriptions for the authenticated user.
        
        Returns:
            List of subscription dictionaries with id and displayName
        """
        url = f"{self.BASE_URL}/subscriptions"
        params = {"api-version": "2020-01-01"}
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(url, headers=headers, params=params, timeout=60)
            response.raise_for_status()
            response_data = response.json()
            
            subscriptions = []
            for sub in response_data.get("value", []):
                subscriptions.append({
                    "id": sub["subscriptionId"],
                    "displayName": sub["displayName"],
                    "state": sub["state"]
                })
            
            logger.info(f"Found {len(subscriptions)} available subscriptions")
            return subscriptions
            
        except Exception as e:
            logger.error(f"Failed to get subscriptions: {e}")
            raise


def create_emissions_query(
    subscription_ids: Union[str, List[str]],
    days_back: int = 30,
    report_type: ReportType = ReportType.OVERALL_SUMMARY_REPORT
) -> EmissionsQuery:
    """
    Create an emissions query for the last N days.
    
    Args:
        subscription_ids: Single subscription ID or list of subscription IDs
        days_back: Number of days back from today to query
        report_type: Type of emissions report
        
    Returns:
        Configured EmissionsQuery object
    """
    if isinstance(subscription_ids, str):
        subscription_ids = [subscription_ids]
    
    # Calculate date range - align with first day of months
    today = datetime.now()
    end_date = today.replace(day=1) - timedelta(days=1)  # Last day of previous month
    start_date = (end_date.replace(day=1) - timedelta(days=days_back)).replace(day=1)
    
    return EmissionsQuery(
        report_type=report_type,
        subscription_list=subscription_ids,
        carbon_scope_list=[EmissionScope.SCOPE1, EmissionScope.SCOPE2, EmissionScope.SCOPE3],
        date_range=DateRange(
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        )
    )


# Example usage and testing functions
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize client
    client = CarbonOptimizationClient()
    
    try:
        # Get available subscriptions
        subscriptions = client.get_available_subscriptions()
        print(f"Available subscriptions: {len(subscriptions)}")
        
        if subscriptions:
            # Use first available subscription for demo
            sub_id = subscriptions[0]["id"]
            print(f"Using subscription: {subscriptions[0]['displayName']} ({sub_id})")
            
            # Example 1: Get monthly summary
            monthly_data = client.get_monthly_summary(
                subscription_ids=[sub_id],
                start_date="2024-01-01",
                end_date="2024-03-01"
            )
            print(f"Monthly summary: {len(monthly_data)} records")
            
            # Example 2: Get overall summary  
            overall_data = client.get_overall_summary(
                subscription_ids=[sub_id],
                start_date="2024-01-01",
                end_date="2024-03-01"
            )
            print(f"Overall summary: {len(overall_data)} records")
            
            # Example 3: Get resource details (for single month)
            resource_data = client.get_resource_details(
                subscription_ids=[sub_id],
                date="2024-02-01",
                category_type=CategoryType.RESOURCE
            )
            print(f"Resource details: {len(resource_data)} records")
            
            # Example 4: Get top emitters
            top_emitters = client.get_top_emitters(
                subscription_ids=[sub_id],
                date="2024-02-01",
                category_type=CategoryType.RESOURCE,
                top_items=5
            )
            print(f"Top emitters: {len(top_emitters)} records")
            
            # Example 5: Format for ESG reporting
            if not monthly_data.empty:
                esg_formatted = format_emissions_for_esg_report(monthly_data)
                print(f"ESG formatted: {len(esg_formatted)} records")
                
                # Export to CSV
                output_file = f"azure_emissions_{datetime.now().strftime('%Y%m%d')}.csv"
                client.export_emissions_to_csv(
                    create_emissions_query(sub_id, days_back=90),
                    output_file
                )
                print(f"Exported data to: {output_file}")
        else:
            print("No subscriptions found or access denied")
            
    except Exception as e:
        print(f"Example failed: {e}")
        logger.exception("Example execution failed")
