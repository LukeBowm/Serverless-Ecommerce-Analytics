import json
import random
import uuid
import datetime
import boto3

# Initialize SNS client
sns = boto3.client('sns')
TOPIC_ARN = "arn:aws:sns:us-west-1:672645349229:RawTransactionData" 

def lambda_handler(event, context):
    # Generate random transaction data
    transaction = {
        "transaction_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.now().isoformat(),
        "customer_id": f"cust_{random.randint(1000, 9999)}",
        "items": generate_items(),
        "total_amount": 0,
        "payment_method": random.choice(["credit_card", "paypal", "apple_pay"]),
        "shipping_address": generate_address()
    }
    
    # Calculate total amount
    total = sum(item["price"] * item["quantity"] for item in transaction["items"])
    transaction["total_amount"] = round(total, 2)
    
    print(f"Generated transaction: {json.dumps(transaction)}")
    
    # Publish transaction to SNS topic
    try:
        print(f"Attempting to publish to SNS topic: {TOPIC_ARN}")
        response = sns.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps(transaction),
            Subject="New Transaction",
            MessageAttributes={
                'TransactionType': {
                    'DataType': 'String',
                    'StringValue': 'purchase'
                }
            }
        )
        print(f"Message published to SNS: {response['MessageId']}")
        print(f"Full SNS response: {json.dumps(response)}")
    except Exception as e:
        print(f"Error publishing to SNS: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        raise e
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": "Transaction processed successfully",
            "transaction_id": transaction["transaction_id"]
        })
    }

def generate_items():
    # Generate 1-5 random items
    num_items = random.randint(1, 5)
    items = []
    
    products = [
        {"id": "p1001", "name": "T-Shirt", "price": 19.99, "category": "clothing"},
        {"id": "p1002", "name": "Jeans", "price": 49.99, "category": "clothing"},
        {"id": "p1003", "name": "Sneakers", "price": 79.99, "category": "footwear"},
        {"id": "p1004", "name": "Backpack", "price": 39.99, "category": "accessories"},
        {"id": "p1005", "name": "Hat", "price": 14.99, "category": "accessories"},
        {"id": "p1006", "name": "Watch", "price": 99.99, "category": "accessories"},
        {"id": "p1007", "name": "Socks", "price": 9.99, "category": "clothing"},
        {"id": "p1008", "name": "Headphones", "price": 29.99, "category": "electronics"}
    ]
    
    for _ in range(num_items):
        product = random.choice(products)
        items.append({
            "product_id": product["id"],
            "product_name": product["name"],
            "category": product["category"],
            "price": product["price"],
            "quantity": random.randint(1, 3)
        })
    
    return items

def generate_address():
    return {
        "street": f"{random.randint(100, 999)} {random.choice(['Main St', 'Broadway', 'Park Ave', 'Elm St', 'Oak Rd'])}",
        "city": random.choice(["New York", "Los Angeles", "Chicago", "Seattle", "Austin", "Denver", "Boston", "Miami"]),
        "state": random.choice(["NY", "CA", "IL", "WA", "TX", "CO", "MA", "FL"]),
        "zip": f"{random.randint(10000, 99999)}"
    }
