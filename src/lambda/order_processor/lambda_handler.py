import json
import boto3
import os

# Initialize EventBridge client
events = boto3.client('events')
EVENT_BUS_NAME = 'default'  # Use the default event bus or specify a custom one

def lambda_handler(event, context):
    processed_count = 0
    
    for record in event['Records']:
        try:
            # Parse the message from SQS
            body = json.loads(record['body'])
            message = json.loads(body['Message'])
            
            # Process only if it's a transaction message
            if 'transaction_id' in message:
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
                
                # Send to EventBridge
                response = send_to_eventbridge(order_data, "order_processed")
                print(f"Event published to EventBridge: {response}")
                processed_count += 1
                
        except Exception as e:
            print(f"Error processing record: {str(e)}")
            # In a production environment, you might want to handle errors differently
            # For example, send to a dead-letter queue or retry
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Processed {processed_count} orders successfully"
        })
    }

def send_to_eventbridge(data, detail_type):
    """Send data to EventBridge"""
    response = events.put_events(
        Entries=[
            {
                'Source': 'com.ecommerce.orders',
                'DetailType': detail_type,
                'Detail': json.dumps(data),
                'EventBusName': EVENT_BUS_NAME
            }
        ]
    )
    return response

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