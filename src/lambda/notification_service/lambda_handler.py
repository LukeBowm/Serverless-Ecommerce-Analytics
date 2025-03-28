import json
import boto3
import os
from datetime import datetime

def lambda_handler(event, context):
    """Handle various notification events from EventBridge"""
    try:
        # Get event details
        event_source = event['source']
        detail_type = event['detail-type']
        detail = event['detail']
        
        # Process based on event type
        if event_source == 'com.ecommerce.inventory' and detail_type == 'inventory_alert':
            # Send inventory alert notification
            send_inventory_alert(detail)
            
        elif event_source == 'com.ecommerce.orders' and detail_type == 'order_processed':
            # Send order confirmation notification
            send_order_confirmation(detail)
            
        elif event_source == 'com.ecommerce.customers' and detail_type == 'customer_analyzed':
            # Send targeted marketing notification for repeat customers
            if detail.get('customer_type') == 'repeat' and detail.get('total_purchases', 0) > 3:
                send_customer_loyalty_message(detail)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Successfully sent notification for {event_source} - {detail_type} event"
            })
        }
        
    except Exception as e:
        print(f"Error processing notification event: {str(e)}")
        raise e

def send_inventory_alert(detail):
    """Send notification about low inventory"""
    product_id = detail.get('product_id', 'unknown')
    product_name = detail.get('product_name', 'unknown')
    stock_level = detail.get('stock_level', 0)
    
    # In a real application, we might send an email or SMS using AWS SNS
    # For this project, we'll just log the notification
    message = f"INVENTORY ALERT: Product {product_name} (ID: {product_id}) has low stock: {stock_level}. Please reorder."
    print(message)
    
    # Log the notification to DynamoDB for demonstration
    log_notification(
        notification_type="inventory_alert",
        subject=f"Low Inventory: {product_name}",
        message=message,
        recipient="inventory@example.com"
    )

def send_order_confirmation(detail):
    """Send order confirmation notification"""
    transaction_id = detail.get('transaction_id', 'unknown')
    customer_id = detail.get('customer_id', 'unknown')
    total_amount = detail.get('total_amount', 0)
    
    # In a real application, we would send this to the customer via email or SMS
    message = f"Thank you for your order #{transaction_id}! Your total is ${total_amount:.2f}."
    print(f"Order confirmation for customer {customer_id}: {message}")
    
    # Log the notification
    log_notification(
        notification_type="order_confirmation",
        subject=f"Order Confirmation #{transaction_id}",
        message=message,
        recipient=f"customer_{customer_id}@example.com"
    )

def send_customer_loyalty_message(detail):
    """Send loyalty program message to repeat customers"""
    customer_id = detail.get('customer_id', 'unknown')
    total_purchases = detail.get('total_purchases', 0)
    total_spent = detail.get('total_spent', 0)
    
    # Create a personalized message
    message = (
        f"Thank you for being a loyal customer! You've made {total_purchases} purchases "
        f"with us totaling ${total_spent:.2f}. As a token of our appreciation, "
        f"here's a 10% discount on your next purchase. Use code LOYAL10."
    )
    print(f"Loyalty message for customer {customer_id}: {message}")
    
    # Log the notification
    log_notification(
        notification_type="customer_loyalty",
        subject="Thank You for Your Loyalty!",
        message=message,
        recipient=f"customer_{customer_id}@example.com"
    )

def log_notification(notification_type, subject, message, recipient):
    """Log notification to DynamoDB for demonstration purposes"""
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Notifications')
    
    try:
        # Create a notification record
        notification_id = f"{notification_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        table.put_item(
            Item={
                'notification_id': notification_id,
                'notification_type': notification_type,
                'subject': subject,
                'message': message,
                'recipient': recipient,
                'status': 'sent',
                'created_at': datetime.now().isoformat()
            }
        )
    except Exception as e:
        print(f"Error logging notification: {str(e)}")