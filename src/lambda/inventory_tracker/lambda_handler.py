import json
import boto3
import os
from datetime import datetime

# Initialize EventBridge client
events = boto3.client('events')
EVENT_BUS_NAME = 'default'

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
INVENTORY_TABLE_NAME = 'InventoryStatus'  # We'll create this table later

def lambda_handler(event, context):
    processed_count = 0
    
    for record in event['Records']:
        try:
            # Parse the message from SQS
            body = json.loads(record['body'])
            message = json.loads(body['Message'])
            
            # Process only if it's a transaction message with items
            if 'transaction_id' in message and 'items' in message:
                # Process each item in the order
                for item in message['items']:
                    # Update inventory and get status
                    inventory_status = update_inventory(item)
                    
                    # If inventory is low, send alert event
                    if inventory_status.get('inventory_status') == 'low':
                        send_to_eventbridge(inventory_status, "inventory_alert")
                    
                    processed_count += 1
                
                # Send a summary event
                summary = {
                    "transaction_id": message["transaction_id"],
                    "timestamp": message["timestamp"],
                    "items_processed": len(message["items"]),
                    "inventory_updated": True
                }
                send_to_eventbridge(summary, "inventory_updated")
                
        except Exception as e:
            print(f"Error processing record: {str(e)}")
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Processed inventory for {processed_count} items successfully"
        })
    }

def update_inventory(item):
    """Update inventory for a product in DynamoDB"""
    product_id = item["product_id"]
    quantity_sold = item["quantity"]
    
    table = dynamodb.Table(INVENTORY_TABLE_NAME)
    
    try:
        # Get current inventory
        response = table.get_item(Key={'product_id': product_id})
        
        if 'Item' in response:
            current_inventory = response['Item']
            
            # Calculate new stock level
            current_stock = current_inventory.get('stock_level', 100)  # Default initial stock of 100
            new_stock = max(0, current_stock - quantity_sold)  # Don't go below 0
            
            # Check if stock is low (less than 20% of initial stock)
            stock_status = 'low' if new_stock < 20 else 'normal'
            
            # Update inventory record
            inventory_data = {
                'product_id': product_id,
                'product_name': item["product_name"],
                'category': item.get("category", "unknown"),
                'stock_level': new_stock,
                'inventory_status': stock_status,
                'last_updated': datetime.now().isoformat(),
                'units_sold_total': current_inventory.get('units_sold_total', 0) + quantity_sold
            }
            
            # Save to DynamoDB
            table.put_item(Item=inventory_data)
            
            return inventory_data
        else:
            # Create a new inventory record with simulated data
            initial_stock = 100  # Simulate initial stock level
            new_stock = initial_stock - quantity_sold
            stock_status = 'low' if new_stock < 20 else 'normal'
            
            inventory_data = {
                'product_id': product_id,
                'product_name': item["product_name"],
                'category': item.get("category", "unknown"),
                'stock_level': new_stock,
                'inventory_status': stock_status,
                'initial_stock': initial_stock,
                'last_updated': datetime.now().isoformat(),
                'units_sold_total': quantity_sold
            }
            
            # Save to DynamoDB
            table.put_item(Item=inventory_data)
            
            return inventory_data
    
    except Exception as e:
        print(f"Error updating inventory for product {product_id}: {str(e)}")
        raise e

def send_to_eventbridge(data, detail_type):
    """Send data to EventBridge"""
    response = events.put_events(
        Entries=[
            {
                'Source': 'com.ecommerce.inventory',
                'DetailType': detail_type,
                'Detail': json.dumps(data),
                'EventBusName': EVENT_BUS_NAME
            }
        ]
    )
    return response