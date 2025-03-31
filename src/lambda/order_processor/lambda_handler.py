import json
import boto3
import os
from decimal import Decimal
import datetime

# Initialize existing clients
events = boto3.client('events')
EVENT_BUS_NAME = 'default'  # Use the default event bus or specify a custom one

# Add DynamoDB client
dynamodb = boto3.resource('dynamodb')
METRICS_TABLE = os.environ.get('METRICS_TABLE_NAME', 'sales-metrics')  # Get from environment or use default

def lambda_handler(event, context):
    processed_count = 0
    
    print(f"Received event: {json.dumps(event)}")
    
    for record in event['Records']:
        try:
            # Parse the message from SQS
            body = json.loads(record['body'])
            print(f"Parsed SQS message body: {json.dumps(body)}")
            
            message = json.loads(body['Message'])
            print(f"Extracted SNS message: {json.dumps(message)}")
            
            # Process only if it's a transaction message
            if 'transaction_id' in message:
                print(f"Processing transaction: {message['transaction_id']}")
                
                # Extract order information
                order_data = {
                    "transaction_id": message["transaction_id"],
                    "timestamp": message["timestamp"],
                    "customer_id": message["customer_id"],
                    "items": message["items"],
                    "total_amount": message["total_amount"],
                    "payment_method": message["payment_method"]
                }
                
                # Add order processing details
                order_data["processing_timestamp"] = context.invoked_function_arn
                order_data["status"] = "processed"
                order_data["fulfillment_center"] = assign_fulfillment_center(message["shipping_address"]["state"])
                
                # Calculate metrics
                order_data["item_count"] = sum(item["quantity"] for item in message["items"])
                order_data["avg_item_price"] = message["total_amount"] / order_data["item_count"]
                
                print(f"Prepared order data for EventBridge: {json.dumps(order_data)}")
                
                # Send to EventBridge
                print(f"Sending to EventBridge with source='com.ecommerce.orders', detailType='order_processed'")
                response = send_to_eventbridge(order_data, "order_processed")
                print(f"EventBridge response: {json.dumps(response)}")
                
                # NEW CODE: Aggregate and update daily metrics
                # Extract transaction date (YYYY-MM-DD)
                transaction_date = message["timestamp"].split("T")[0]
                total_amount = Decimal(str(message["total_amount"]))  # Convert to Decimal for DynamoDB
                item_count = order_data["item_count"]
                categories = [item["category"] for item in message["items"]]
                
                # Update daily metrics in DynamoDB
                update_daily_metrics(transaction_date, total_amount, item_count, 1, categories)
                
                processed_count += 1
                
        except Exception as e:
            print(f"Error processing record: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Processed {processed_count} orders successfully"
        })
    }

# NEW FUNCTION: Update daily metrics
def update_daily_metrics(date, sales_amount, item_count, transaction_count, categories):
    """Update the aggregated daily metrics in DynamoDB"""
    try:
        table = dynamodb.Table(METRICS_TABLE)
        metric_key = f"date#{date}"
        
        print(f"Updating daily metrics for {date} in table {METRICS_TABLE}")
        print(f"Values: sales={sales_amount}, items={item_count}, transactions={transaction_count}, categories={categories}")
        
        # Check if the record exists
        response = table.get_item(
            Key={
                'time_unit': 'date',
                'metric_key': metric_key
            }
        )
        
        if 'Item' not in response:
            # Create a new record
            print(f"Creating new record for {date}")
            table.put_item(
                Item={
                    'time_unit': 'date',
                    'metric_key': metric_key,
                    'time_value': date,
                    'total_sales': sales_amount,
                    'transaction_count': transaction_count,
                    'item_count': item_count,
                    'categories': categories,
                    'created_at': datetime.datetime.now().isoformat(),
                    'last_updated': datetime.datetime.now().isoformat()
                }
            )
        else:
            # Update existing record
            print(f"Updating existing record for {date}")
            response = table.update_item(
                Key={
                    'time_unit': 'date',
                    'metric_key': metric_key
                },
                UpdateExpression="ADD total_sales :s, item_count :i, transaction_count :t SET categories = list_append(if_not_exists(categories, :empty), :cats), last_updated = :updated",
                ExpressionAttributeValues={
                    ':s': sales_amount,
                    ':i': item_count,
                    ':t': transaction_count,
                    ':cats': categories,
                    ':empty': [],
                    ':updated': datetime.datetime.now().isoformat()
                },
                ReturnValues="UPDATED_NEW"
            )
            print(f"Updated metrics: {response.get('Attributes', {})}")
        
        return True
    except Exception as e:
        print(f"Error updating daily metrics: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

# Existing functions
def send_to_eventbridge(data, detail_type):
    """Send data to EventBridge"""
    try:
        entry = {
            'Source': 'com.ecommerce.orders',
            'DetailType': detail_type,
            'Detail': json.dumps(data),
            'EventBusName': EVENT_BUS_NAME
        }
        print(f"EventBridge entry: {json.dumps(entry)}")
        
        response = events.put_events(
            Entries=[entry]
        )
        return response
    except Exception as e:
        print(f"Error sending to EventBridge: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise e

def assign_fulfillment_center(state):
    """Assign an order to a fulfillment center based on the shipping state"""
    # East coast states
    east_coast = ["NY", "NJ", "PA", "MA", "CT", "RI", "NH", "ME", "VT", "DE", "MD", "VA", "NC", "SC", "GA", "FL"]
    # West coast states
    west_coast = ["CA", "OR", "WA", "NV", "AZ"]
    # Central states
    central = ["TX", "OK", "KS", "NE", "SD", "ND", "MN", "IA", "MO", "AR", "LA", "MS", "AL", "TN", "KY", "WV", "OH", "IN", "IL", "MI", "WI"]
    
    if state in east_coast:
        return "fc_east_001"
    elif state in west_coast:
        return "fc_west_001"
    else:  # central or any other
        return "fc_central_001"