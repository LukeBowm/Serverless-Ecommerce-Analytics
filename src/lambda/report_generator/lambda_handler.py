import json
import boto3
import os
from datetime import datetime, timedelta
import decimal
import csv
import io

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Table names
SALES_METRICS_TABLE = 'SalesMetrics'
CUSTOMER_INSIGHTS_TABLE = 'CustomerInsights'
INVENTORY_STATUS_TABLE = 'InventoryStatus'

# S3 bucket for reports
REPORTS_BUCKET = 'lukebowm-serverless-ecommerce-reports'

# Helper class to convert Decimal to float for JSON serialization
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o) if o % 1 > 0 else int(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    """Generate reports based on parameters in the event"""
    try:
        # Extract report parameters
        report_type = event.get('reportType', 'sales')
        format_type = event.get('format', 'json')
        time_period = event.get('period', 'last30')
        
        # Generate the appropriate report
        if report_type == 'sales':
            report_data = generate_sales_report(time_period)
            report_title = "Sales_Report"
        elif report_type == 'customers':
            report_data = generate_customer_report()
            report_title = "Customer_Report"
        elif report_type == 'inventory':
            report_data = generate_inventory_report()
            report_title = "Inventory_Report"
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f"Invalid report type: {report_type}"
                })
            }
        
        # Format and save the report
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        report_filename = f"{report_title}_{timestamp}"
        
        if format_type == 'csv':
            s3_key, report_url = save_report_csv(report_data, report_filename)
            content_type = 'text/csv'
        else:  # default to JSON
            s3_key, report_url = save_report_json(report_data, report_filename)
            content_type = 'application/json'
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'reportType': report_type,
                'format': format_type,
                'period': time_period,
                'timestamp': timestamp,
                'reportUrl': report_url,
                'expiresIn': '1 hour'
            })
        }
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f"Error generating report: {str(e)}"
            })
        }

def generate_sales_report(time_period):
    """Generate a sales report for the specified time period"""
    table = dynamodb.Table(SALES_METRICS_TABLE)
    
    # Define the time range based on the period
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if time_period == 'last7':
        start_date = today - timedelta(days=7)
        prefix = 'date#'
    elif time_period == 'last30':
        start_date = today - timedelta(days=30)
        prefix = 'date#'
    elif time_period == 'last12':
        start_date = today - timedelta(days=365)
        prefix = 'month#'
    else:
        # Default to last 30 days
        start_date = today - timedelta(days=30)
        prefix = 'date#'
    
    # Scan the table for items with the correct prefix
    response = table.scan(
        FilterExpression="begins_with(metric_key, :prefix)",
        ExpressionAttributeValues={
            ':prefix': prefix
        }
    )
    
    items = response.get('Items', [])
    
    # Filter by date range and sort
    filtered_items = []
    for item in items:
        time_value = item.get('time_value', '')
        
        # Try to parse the date
        try:
            if prefix == 'date#':
                date_obj = datetime.strptime(time_value, '%Y-%m-%d')
            elif prefix == 'month#':
                # Months are in format YYYY-MM
                date_obj = datetime.strptime(time_value, '%Y-%m')
            else:
                continue
            
            # Skip if before start date
            if date_obj < start_date:
                continue
            
            filtered_items.append(item)
        except ValueError:
            # Skip items with invalid date format
            continue
    
    # Sort by time value
    filtered_items.sort(key=lambda x: x.get('time_value', ''))
    
    # Calculate summary statistics
    total_sales = sum(item.get('total_sales', 0) for item in filtered_items)
    total_transactions = sum(item.get('transaction_count', 0) for item in filtered_items)
    total_items = sum(item.get('item_count', 0) for item in filtered_items)
    
    avg_transaction_value = total_sales / total_transactions if total_transactions > 0 else 0
    avg_items_per_transaction = total_items / total_transactions if total_transactions > 0 else 0
    
    # Create report
    report = {
        'reportType': 'sales',
        'period': time_period,
        'generatedAt': datetime.now().isoformat(),
        'summary': {
            'totalSales': total_sales,
            'totalTransactions': total_transactions,
            'totalItems': total_items,
            'avgTransactionValue': avg_transaction_value,
            'avgItemsPerTransaction': avg_items_per_transaction
        },
        'details': filtered_items
    }
    
    return report

def generate_customer_report():
    """Generate a customer insights report"""
    table = dynamodb.Table(CUSTOMER_INSIGHTS_TABLE)
    
    # Get all cohorts
    response = table.scan(
        FilterExpression="begins_with(insight_key, :prefix)",
        ExpressionAttributeValues={
            ':prefix': 'cohort#'
        }
    )
    
    cohorts = response.get('Items', [])
    
    # Sort by cohort
    cohorts.sort(key=lambda x: x.get('cohort', ''))
    
    # Calculate overall statistics
    total_customers = sum(cohort.get('customer_count', 0) for cohort in cohorts)
    total_revenue = sum(cohort.get('total_revenue', 0) for cohort in cohorts)
    new_customers = sum(cohort.get('new_customers', 0) for cohort in cohorts)
    repeat_customers = sum(cohort.get('repeat_customers', 0) for cohort in cohorts)
    
    # Create report
    report = {
        'reportType': 'customers',
        'generatedAt': datetime.now().isoformat(),
        'summary': {
            'totalCustomers': total_customers,
            'totalRevenue': total_revenue,
            'newCustomers': new_customers,
            'repeatCustomers': repeat_customers,
            'avgRevenuePerCustomer': total_revenue / total_customers if total_customers > 0 else 0
        },
        'cohorts': cohorts
    }
    
    return report

def generate_inventory_report():
    """Generate an inventory status report"""
    table = dynamodb.Table(INVENTORY_STATUS_TABLE)
    
    # Get all inventory items
    response = table.scan()
    items = response.get('Items', [])
    
    # Group by category and status
    categories = {}
    status_counts = {
        'normal': 0,
        'low': 0
    }
    
    for item in items:
        category = item.get('category', 'unknown')
        status = item.get('inventory_status', 'unknown')
        
        # Update category grouping
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
        
        # Update status counts
        if status in status_counts:
            status_counts[status] += 1
    
    # Create report
    report = {
        'reportType': 'inventory',
        'generatedAt': datetime.now().isoformat(),
        'summary': {
            'totalProducts': len(items),
            'lowStockProducts': status_counts['low'],
            'normalStockProducts': status_counts['normal'],
            'categoryCount': len(categories)
        },
        'categories': {
            category: {
                'count': len(items),
                'items': items
            }
            for category, items in categories.items()
        }
    }
    
    return report

def save_report_json(report_data, filename):
    """Save report as JSON to S3 and generate a presigned URL"""
    try:
        # Convert to JSON
        json_data = json.dumps(report_data, cls=DecimalEncoder)
        
        # Upload to S3
        s3_key = f"reports/json/{filename}.json"
        
        s3.put_object(
            Bucket=REPORTS_BUCKET,
            Key=s3_key,
            Body=json_data,
            ContentType='application/json'
        )
        
        # Generate presigned URL (expires in 1 hour)
        report_url = generate_presigned_url(REPORTS_BUCKET, s3_key, 3600)
        
        return s3_key, report_url
    except Exception as e:
        print(f"Error saving JSON report: {str(e)}")
        raise e

def save_report_csv(report_data, filename):
    """Save report as CSV to S3 and generate a presigned URL"""
    try:
        # Prepare CSV data based on report type
        report_type = report_data.get('reportType')
        
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        
        if report_type == 'sales':
            # Write headers
            writer.writerow(['Date', 'Total Sales', 'Transactions', 'Items', 'Categories'])
            
            # Write data rows
            for item in report_data.get('details', []):
                writer.writerow([
                    item.get('time_value', ''),
                    item.get('total_sales', 0),
                    item.get('transaction_count', 0),
                    item.get('item_count', 0),
                    ', '.join(item.get('categories', []))
                ])
                
        elif report_type == 'customers':
            # Write headers
            writer.writerow(['Cohort', 'Customers', 'Revenue', 'New Customers', 'Repeat Customers'])
            
            # Write data rows
            for cohort in report_data.get('cohorts', []):
                writer.writerow([
                    cohort.get('cohort', ''),
                    cohort.get('customer_count', 0),
                    cohort.get('total_revenue', 0),
                    cohort.get('new_customers', 0),
                    cohort.get('repeat_customers', 0)
                ])
                
        elif report_type == 'inventory':
            # Write headers
            writer.writerow(['Product ID', 'Product Name', 'Category', 'Stock Level', 'Status'])
            
            # Write data rows for all categories
            for category, data in report_data.get('categories', {}).items():
                for item in data.get('items', []):
                    writer.writerow([
                        item.get('product_id', ''),
                        item.get('product_name', ''),
                        item.get('category', ''),
                        item.get('stock_level', 0),
                        item.get('inventory_status', '')
                    ])
        
        # Upload to S3
        s3_key = f"reports/csv/{filename}.csv"
        
        s3.put_object(
            Bucket=REPORTS_BUCKET,
            Key=s3_key,
            Body=csv_buffer.getvalue(),
            ContentType='text/csv'
        )
        
        # Generate presigned URL (expires in 1 hour)
        report_url = generate_presigned_url(REPORTS_BUCKET, s3_key, 3600)
        
        return s3_key, report_url
    except Exception as e:
        print(f"Error saving CSV report: {str(e)}")
        raise e

def generate_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL for an S3 object"""
    try:
        response = s3.generate_presigned_url('get_object',
                                           Params={'Bucket': bucket_name,
                                                   'Key': object_name},
                                           ExpiresIn=expiration)
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        raise e
    
    return response