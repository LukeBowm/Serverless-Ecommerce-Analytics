import json
import boto3
import os
from datetime import datetime, timedelta
from decimal import Decimal  # Added import for Decimal

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
SALES_METRICS_TABLE = 'SalesMetrics'
CUSTOMER_INSIGHTS_TABLE = 'CustomerInsights'
INVENTORY_STATUS_TABLE = 'InventoryStatus'

def lambda_handler(event, context):
    """Handle various events from EventBridge and update business metrics"""
    try:
        # Get event details
        event_source = event['source']
        detail_type = event['detail-type']
        detail = event['detail']
        
        # Process based on event type
        if event_source == 'com.ecommerce.orders' and detail_type == 'order_processed':
            # Update sales metrics
            update_sales_metrics(detail)
            
        elif event_source == 'com.ecommerce.customers' and detail_type == 'customer_analyzed':
            # Update customer insights
            update_customer_insights(detail)
            
        elif event_source == 'com.ecommerce.inventory' and detail_type == 'inventory_updated':
            # Update inventory metrics
            update_inventory_metrics(detail)
            
        elif event_source == 'com.ecommerce.inventory' and detail_type == 'inventory_alert':
            # Handle inventory alerts
            handle_inventory_alert(detail)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Successfully processed {event_source} - {detail_type} event"
            })
        }
        
    except Exception as e:
        print(f"Error processing event: {str(e)}")
        raise e

def update_sales_metrics(detail):
    """Update daily, weekly, and monthly sales metrics"""
    # Get transaction details
    transaction_id = detail['transaction_id']
    timestamp = detail['timestamp']
    total_amount = detail['total_amount']
    
    # Parse timestamp
    transaction_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    date_str = transaction_date.strftime('%Y-%m-%d')
    week_str = transaction_date.strftime('%Y-W%W')
    month_str = transaction_date.strftime('%Y-%m')
    
    # Update daily metrics
    update_time_based_metrics(SALES_METRICS_TABLE, 'date', date_str, total_amount, detail)
    
    # Update weekly metrics
    update_time_based_metrics(SALES_METRICS_TABLE, 'week', week_str, total_amount, detail)
    
    # Update monthly metrics
    update_time_based_metrics(SALES_METRICS_TABLE, 'month', month_str, total_amount, detail)
    
    print(f"Updated sales metrics for transaction {transaction_id}")

def update_time_based_metrics(table_name, time_unit, time_value, amount, detail):
    """Update metrics for a specific time unit (day, week, month)"""
    table = dynamodb.Table(table_name)
    
    # Convert float to Decimal for DynamoDB compatibility
    decimal_amount = Decimal(str(amount))
    
    # Compute item counts and categories
    item_count = sum(item['quantity'] for item in detail['items'])
    categories = set(item.get('category', 'unknown') for item in detail['items'])
    
    try:
        # Try to update existing record
        response = table.update_item(
            Key={
                'metric_key': f"{time_unit}#{time_value}"
            },
            UpdateExpression="ADD total_sales :amount, item_count :items, transaction_count :one " +
                            "SET categories = list_append(if_not_exists(categories, :empty_list), :cats), " +
                            "last_updated = :now",
            ExpressionAttributeValues={
                ':amount': decimal_amount,  # Now using Decimal
                ':items': item_count,
                ':one': 1,
                ':cats': list(categories),
                ':empty_list': [],
                ':now': datetime.now().isoformat()
            },
            ReturnValues="UPDATED_NEW"
        )
        
        # If successful update, return
        if 'Attributes' in response:
            return
    
    except Exception as e:
        # Record may not exist, create a new one
        print(f"Error updating metrics for {time_unit}#{time_value}: {str(e)}")
    
    # Create a new record
    try:
        table.put_item(
            Item={
                'metric_key': f"{time_unit}#{time_value}",
                'time_unit': time_unit,
                'time_value': time_value,
                'total_sales': decimal_amount,  # Now using Decimal
                'item_count': item_count,
                'transaction_count': 1,
                'categories': list(categories),
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        )
    except Exception as e:
        print(f"Error creating metrics for {time_unit}#{time_value}: {str(e)}")
        raise e

def update_customer_insights(detail):
    """Update customer insights based on analyzed customer data"""
    customer_id = detail['customer_id']
    customer_type = detail.get('customer_type', 'unknown')
    
    # Get cohort information
    cohort = detail.get('year_month_cohort', 'unknown')
    
    # Get purchase information and convert to Decimal
    total_spent = Decimal(str(detail.get('total_spent', 0)))
    total_purchases = detail.get('total_purchases', 0)
    avg_order_value = Decimal(str(detail.get('average_order_value', 0)))
    
    # Update cohort metrics
    table = dynamodb.Table(CUSTOMER_INSIGHTS_TABLE)
    
    try:
        # Try to update existing cohort record
        response = table.update_item(
            Key={
                'insight_key': f"cohort#{cohort}"
            },
            UpdateExpression="ADD customer_count :one, total_revenue :amount, " +
                            "repeat_customers :repeat, new_customers :new " +
                            "SET last_updated = :now",
            ExpressionAttributeValues={
                ':one': 1,
                ':amount': total_spent,  # Already converted to Decimal
                ':repeat': 1 if customer_type == 'repeat' else 0,
                ':new': 1 if customer_type == 'new' else 0,
                ':now': datetime.now().isoformat()
            },
            ReturnValues="UPDATED_NEW"
        )
    except Exception as e:
        # Create a new cohort record
        print(f"Creating new cohort record for {cohort}")
        table.put_item(
            Item={
                'insight_key': f"cohort#{cohort}",
                'insight_type': 'cohort',
                'cohort': cohort,
                'customer_count': 1,
                'total_revenue': total_spent,  # Already converted to Decimal
                'repeat_customers': 1 if customer_type == 'repeat' else 0,
                'new_customers': 1 if customer_type == 'new' else 0,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        )
    
    print(f"Updated customer insights for customer {customer_id}")

def update_inventory_metrics(detail):
    """Update inventory-related metrics"""
    transaction_id = detail.get('transaction_id', 'unknown')
    items_processed = detail.get('items_processed', 0)
    
    # In a real application, we might update aggregated inventory metrics here
    # For this project, we'll just log the event
    print(f"Processed inventory update for transaction {transaction_id} with {items_processed} items")

def handle_inventory_alert(detail):
    """Handle low inventory alerts"""
    product_id = detail.get('product_id', 'unknown')
    product_name = detail.get('product_name', 'unknown')
    stock_level = detail.get('stock_level', 0)
    
    # In a real application, we might:
    # 1. Create a purchase order
    # 2. Notify procurement team
    # 3. Update inventory management system
    
    # For this project, we'll just log the alert
    print(f"LOW INVENTORY ALERT: Product {product_name} (ID: {product_id}) has low stock: {stock_level}")
    
    # Update alerts in DynamoDB
    table = dynamodb.Table(INVENTORY_STATUS_TABLE)
    
    try:
        # Create an alert record
        alert_id = f"alert_{product_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Convert stock_level to Decimal if it might be a float
        if isinstance(stock_level, float):
            stock_level = Decimal(str(stock_level))
        
        table.put_item(
            Item={
                'alert_id': alert_id,
                'product_id': product_id,
                'product_name': product_name,
                'alert_type': 'low_inventory',
                'stock_level': stock_level,
                'status': 'open',
                'created_at': datetime.now().isoformat()
            }
        )
    except Exception as e:
        print(f"Error creating inventory alert: {str(e)}")