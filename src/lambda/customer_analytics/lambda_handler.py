import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

# Initialize EventBridge client
events = boto3.client('events')
EVENT_BUS_NAME = 'default'  # Use the default event bus or specify a custom one

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
CUSTOMER_TABLE_NAME = 'CustomerProfiles'  # This table should already exist or be created by CloudFormation

def lambda_handler(event, context):
    processed_count = 0
    
    for record in event['Records']:
        try:
            # Parse the message from SQS
            body = json.loads(record['body'])
            message = json.loads(body['Message'])
            
            # Process only if it's a transaction message
            if 'transaction_id' in message and 'customer_id' in message:
                customer_id = message["customer_id"]
                
                # Analyze customer data
                customer_data = analyze_customer(customer_id, message)
                
                # Update customer profile in DynamoDB
                update_customer_profile(customer_data)
                
                # Send to EventBridge
                response = send_to_eventbridge(customer_data, "customer_analyzed")
                print(f"Event published to EventBridge: {response}")
                processed_count += 1
                
        except Exception as e:
            print(f"Error processing record: {str(e)}")
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Processed {processed_count} customer records successfully"
        })
    }

def analyze_customer(customer_id, transaction):
    """Analyze customer data from transaction"""
    # Get current date for cohort analysis
    current_date = datetime.now()
    year_month = f"{current_date.year}-{current_date.month:02d}"
    
    # Extract customer data from transaction
    customer_data = {
        "customer_id": customer_id,
        "last_purchase_date": transaction["timestamp"],
        "last_purchase_amount": Decimal(str(transaction["total_amount"])),
        "payment_method": transaction["payment_method"],
        "shipping_state": transaction["shipping_address"]["state"],
        "purchase_categories": list(set(item["category"] for item in transaction["items"])),
        "year_month_cohort": year_month
    }
    
    # Try to get existing customer profile
    table = dynamodb.Table(CUSTOMER_TABLE_NAME)
    try:
        response = table.get_item(Key={'customer_id': customer_id})
        if 'Item' in response:
            existing_customer = response['Item']
            
            # Update analytics data - using Decimal for monetary values
            customer_data["total_purchases"] = existing_customer.get("total_purchases", 0) + 1
            customer_data["total_spent"] = Decimal(str(existing_customer.get("total_spent", 0))) + Decimal(str(transaction["total_amount"]))
            customer_data["average_order_value"] = Decimal(str(customer_data["total_spent"] / customer_data["total_purchases"]))
            
            # Calculate days since first purchase for customer lifetime
            first_purchase_date = existing_customer.get("first_purchase_date", transaction["timestamp"])
            customer_data["first_purchase_date"] = first_purchase_date
            
            # Combine categories
            existing_categories = existing_customer.get("purchase_categories", [])
            customer_data["purchase_categories"] = list(set(customer_data["purchase_categories"] + existing_categories))
            
            # Determine if this is a repeat customer
            customer_data["customer_type"] = "repeat"
        else:
            # New customer
            customer_data["total_purchases"] = 1
            customer_data["total_spent"] = Decimal(str(transaction["total_amount"]))
            customer_data["average_order_value"] = Decimal(str(transaction["total_amount"]))
            customer_data["first_purchase_date"] = transaction["timestamp"]
            customer_data["customer_type"] = "new"
    
    except Exception as e:
        print(f"Error retrieving customer profile: {str(e)}")
        # Assume new customer if there's an error
        customer_data["total_purchases"] = 1
        customer_data["total_spent"] = Decimal(str(transaction["total_amount"]))
        customer_data["average_order_value"] = Decimal(str(transaction["total_amount"]))
        customer_data["first_purchase_date"] = transaction["timestamp"]
        customer_data["customer_type"] = "new"
    
    return customer_data

def update_customer_profile(customer_data):
    """Update customer profile in DynamoDB"""
    table = dynamodb.Table(CUSTOMER_TABLE_NAME)
    try:
        # Add timestamp for the update
        customer_data["last_updated"] = datetime.now().isoformat()
        
        # Put the item in the table
        response = table.put_item(Item=customer_data)
        print(f"Updated customer profile: {customer_data['customer_id']}")
        return response
    except Exception as e:
        print(f"Error updating customer profile: {str(e)}")
        # In a production system, you might want to retry or log this error
        raise e

def send_to_eventbridge(data, detail_type):
    """Send data to EventBridge"""
    # Convert Decimal to float for JSON serialization
    json_data = json.loads(json.dumps(data, default=decimal_default))
    
    response = events.put_events(
        Entries=[
            {
                'Source': 'com.ecommerce.customers',
                'DetailType': detail_type,
                'Detail': json.dumps(json_data),
                'EventBusName': EVENT_BUS_NAME
            }
        ]
    )
    return response

def decimal_default(obj):
    """Helper function to convert Decimal to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)