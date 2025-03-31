import json
import boto3
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
SALES_METRICS_TABLE = 'SalesMetrics'
CUSTOMER_INSIGHTS_TABLE = 'CustomerInsights'
INVENTORY_STATUS_TABLE = 'InventoryStatus'
NOTIFICATIONS_TABLE = 'Notifications'

def lambda_handler(event, context):
    """Handler for Dashboard API Gateway requests"""
    try:
        # Get the HTTP method and path
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '')
        
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        
        # Route the request
        if http_method == 'GET':
            if path == '/api/sales':
                # Get sales metrics
                time_unit = query_params.get('timeUnit', 'day')
                period = query_params.get('period', 'last7')
                return get_sales_metrics(time_unit, period)
                
            elif path == '/api/customers':
                # Get customer insights
                cohort = query_params.get('cohort', None)
                return get_customer_insights(cohort)
                
            elif path == '/api/inventory':
                # Get inventory status
                status = query_params.get('status', None)
                category = query_params.get('category', None)
                return get_inventory_status(status, category)
                
            elif path == '/api/notifications':
                # Get recent notifications
                notification_type = query_params.get('type', None)
                limit = int(query_params.get('limit', 10))
                return get_notifications(notification_type, limit)
                
            elif path == '/api':
                # Default dashboard data
                return get_dashboard_summary()
                
            elif path == '/api/reports':
                # Handle GET request for report types
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'reportTypes': ['sales', 'customers', 'inventory'],
                        'formats': ['json', 'csv']
                    })
                }
        
        elif http_method == 'POST' and path == '/api/reports':
            # Generate report
            try:
                body = json.loads(event.get('body', '{}'))
                return generate_report(body)
            except Exception as e:
                print(f"Error parsing request body: {str(e)}")
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Invalid request body'
                    })
                }
        
        # Invalid request
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Invalid request'
            })
        }
        
    except Exception as e:
        print(f"Error processing API request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f"Internal server error: {str(e)}"
            })
        }

def get_sales_metrics(time_unit, period):
    """Get sales metrics for the specified time period"""
    table = dynamodb.Table(SALES_METRICS_TABLE)
    
    # Define the time range based on the period
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if period == 'last7':
        start_date = today - timedelta(days=7)
        date_format = '%Y-%m-%d'
    elif period == 'last30':
        start_date = today - timedelta(days=30)
        date_format = '%Y-%m-%d'
    elif period == 'last12':
        start_date = today - timedelta(days=365)
        date_format = '%Y-%m'
    else:
        # Default to last 7 days
        start_date = today - timedelta(days=7)
        date_format = '%Y-%m-%d'
    
    # Convert to string for comparison
    start_date_str = start_date.strftime('%Y-%m-%d')
    
    print(f"Querying sales data from {start_date_str} to today")
    
    # Map time_unit to the correct prefix
    prefix_map = {
        'day': 'date#',
        'week': 'week#',
        'month': 'month#'
    }
    
    prefix = prefix_map.get(time_unit, 'date#')
    
    # Scan the table for items with the correct prefix and time_unit
    try:
        response = table.scan(
            FilterExpression="begins_with(metric_key, :prefix) AND time_unit = :time_unit_val",
            ExpressionAttributeValues={
                ':prefix': prefix,
                ':time_unit_val': 'date' if time_unit == 'day' else time_unit
            }
        )
        
        items = response.get('Items', [])
        print(f"Found {len(items)} items with prefix {prefix}")
        
        # Filter by date range and sort
        filtered_items = []
        for item in items:
            time_value = item.get('time_value', '')
            
            # Skip items without time_value
            if not time_value:
                continue
            
            # For daily data, directly compare with the date string
            if time_unit == 'day':
                if time_value >= start_date_str:
                    filtered_items.append(item)
            else:
                # Try to parse the date for other time units
                try:
                    if time_unit == 'week':
                        # Weeks are in format YYYY-WNN
                        year, week = time_value.split('-W')
                        date_obj = datetime.strptime(f"{year}-{week}-1", '%Y-%W-%w')
                    elif time_unit == 'month':
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
        
        print(f"Filtered to {len(filtered_items)} items within date range")
        
        # Sort by time value
        filtered_items.sort(key=lambda x: x.get('time_value', ''))
        
        # Add debug data to check what's happening
        for item in filtered_items:
            print(f"Including item: time_value={item.get('time_value', 'N/A')}, "
                  f"metric_key={item.get('metric_key', 'N/A')}, "
                  f"total_sales={item.get('total_sales', 'N/A')}")
        
        # Format response
        result = {
            'period': period,
            'timeUnit': time_unit,
            'data': filtered_items
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error getting sales metrics: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f"Error getting sales metrics: {str(e)}"
            })
        }

def get_customer_insights(cohort=None):
    """Get customer insights, optionally filtered by cohort"""
    table = dynamodb.Table(CUSTOMER_INSIGHTS_TABLE)
    
    try:
        if cohort:
            # Get a specific cohort
            response = table.get_item(
                Key={
                    'insight_key': f"cohort#{cohort}"
                }
            )
            
            item = response.get('Item', {})
            
            result = {
                'cohort': cohort,
                'data': item
            }
        else:
            # Get all cohorts
            response = table.scan(
                FilterExpression="begins_with(insight_key, :prefix)",
                ExpressionAttributeValues={
                    ':prefix': 'cohort#'
                }
            )
            
            items = response.get('Items', [])
            
            # Sort by cohort
            items.sort(key=lambda x: x.get('cohort', ''))
            
            result = {
                'cohorts': items
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error getting customer insights: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f"Error getting customer insights: {str(e)}"
            })
        }

def get_inventory_status(status=None, category=None):
    """Get inventory status, optionally filtered by status or category"""
    table = dynamodb.Table(INVENTORY_STATUS_TABLE)
    
    try:
        filter_expression = None
        expression_values = {}
        
        if status:
            filter_expression = "inventory_status = :status"
            expression_values[':status'] = status
        
        if category:
            if filter_expression:
                filter_expression += " AND category = :category"
            else:
                filter_expression = "category = :category"
            expression_values[':category'] = category
        
        if filter_expression:
            response = table.scan(
                FilterExpression=filter_expression,
                ExpressionAttributeValues=expression_values
            )
        else:
            response = table.scan()
        
        items = response.get('Items', [])
        
        # Group by category
        categories = {}
        for item in items:
            item_category = item.get('category', 'unknown')
            if item_category not in categories:
                categories[item_category] = []
            categories[item_category].append(item)
        
        result = {
            'categories': categories,
            'totalItems': len(items)
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error getting inventory status: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f"Error getting inventory status: {str(e)}"
            })
        }

def get_notifications(notification_type=None, limit=10):
    """Get recent notifications, optionally filtered by type"""
    # For this demo, we'll create mock notifications from inventory alerts
    table = dynamodb.Table(INVENTORY_STATUS_TABLE)
    
    try:
        # Get items with low stock
        response = table.scan(
            FilterExpression="inventory_status = :status",
            ExpressionAttributeValues={
                ':status': 'low'
            }
        )
        
        low_stock_items = response.get('Items', [])
        
        # Convert to notifications
        notifications = []
        for item in low_stock_items:
            notifications.append({
                'id': f"alert_{item.get('product_id', 'unknown')}",
                'type': 'inventory_alert',
                'message': f"Low stock alert: {item.get('product_name', 'Product')} ({item.get('stock_level', 0)} remaining)",
                'timestamp': item.get('last_updated', datetime.now().isoformat()),
                'status': 'open'
            })
        
        # Sort by timestamp (most recent first) and limit
        notifications.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        notifications = notifications[:limit]
        
        result = {
            'notifications': notifications,
            'count': len(notifications)
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error getting notifications: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f"Error getting notifications: {str(e)}"
            })
        }

def get_dashboard_summary():
    """Get a summary of data for the dashboard homepage"""
    try:
        # Get recent sales data (last 7 days)
        sales_response = get_sales_metrics('day', 'last7')
        sales_data = json.loads(sales_response['body']) if sales_response['statusCode'] == 200 else {}
        
        # Get customer insights
        customer_response = get_customer_insights()
        customer_data = json.loads(customer_response['body']) if customer_response['statusCode'] == 200 else {}
        
        # Get inventory status
        inventory_response = get_inventory_status('low')
        inventory_data = json.loads(inventory_response['body']) if inventory_response['statusCode'] == 200 else {}
        
        # Get recent notifications
        notification_response = get_notifications(limit=5)
        notification_data = json.loads(notification_response['body']) if notification_response['statusCode'] == 200 else {}
        
        # Compile summary
        summary = {
            'recentSales': sales_data.get('data', []),
            'customerCohorts': customer_data.get('cohorts', []),
            'lowInventoryItems': inventory_data.get('totalItems', 0),
            'recentNotifications': notification_data.get('notifications', [])
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(summary, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error getting dashboard summary: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f"Error getting dashboard summary: {str(e)}"
            })
        }

def generate_report(request_body):
    """Generate a report based on the request parameters"""
    try:
        report_type = request_body.get('reportType', 'sales')
        report_format = request_body.get('format', 'json')
        period = request_body.get('period', 'last30')
        
        # Generate different reports based on type
        if report_type == 'sales':
            sales_response = get_sales_metrics('day', period)
            if sales_response['statusCode'] != 200:
                return sales_response
            
            report_data = json.loads(sales_response['body'])
            
        elif report_type == 'customers':
            customer_response = get_customer_insights()
            if customer_response['statusCode'] != 200:
                return customer_response
            
            report_data = json.loads(customer_response['body'])
            
        elif report_type == 'inventory':
            inventory_response = get_inventory_status()
            if inventory_response['statusCode'] != 200:
                return inventory_response
            
            report_data = json.loads(inventory_response['body'])
            
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': f"Invalid report type: {report_type}"
                })
            }
        
        # For a real application, we would generate a proper report here
        # For this demo, we'll just return the data with a fake URL
        
        result = {
            'reportType': report_type,
            'format': report_format,
            'period': period,
            'generatedAt': datetime.now().isoformat(),
            'reportUrl': f"https://example.com/reports/{report_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{report_format}",
            'data': report_data
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f"Error generating report: {str(e)}"
            })
        }

def decimal_default(obj):
    """Helper function to convert Decimal to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)