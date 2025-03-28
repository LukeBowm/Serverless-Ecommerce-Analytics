import json
import boto3
import os
from datetime import datetime

# Initialize clients
s3 = boto3.client('s3')
events = boto3.client('events')
appflow = boto3.client('appflow')

# AppFlow configuration
APPFLOW_FLOW_NAME = "EcommerceMarketingIntegration"
S3_BUCKET = "lukebowm-appflow-data"
SOURCE_PREFIX = "source-data/"

def lambda_handler(event, context):
    """
    This function is triggered by EventBridge and:
    1. Generates a sample customer data file
    2. Uploads it to S3
    3. Triggers the AppFlow flow
    """
    try:
        # Get event details
        event_source = event.get('source', 'unknown')
        detail_type = event.get('detail-type', 'unknown')
        
        # Only process customer events
        if event_source == 'com.ecommerce.customers' and detail_type == 'customer_analyzed':
            detail = event['detail']
            
            # Generate sample customer marketing data
            customer_data = generate_customer_marketing_data(detail)
            
            # Create a unique filename
            filename = f"customer_{detail.get('customer_id')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            
            # Upload to S3
            upload_to_s3(customer_data, filename)
            
            # Trigger AppFlow (in a real scenario)
            # In this demo, we'll just log that we would trigger it
            print(f"Would trigger AppFlow flow: {APPFLOW_FLOW_NAME}")
            # Uncomment to actually trigger AppFlow
            # start_appflow_flow()
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": f"Successfully processed customer data and uploaded to S3: {filename}"
                })
            }
        else:
            print(f"Ignoring non-customer event: {event_source} - {detail_type}")
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Event ignored - not a customer event"
                })
            }
            
    except Exception as e:
        print(f"Error processing event: {str(e)}")
        raise e

def generate_customer_marketing_data(customer_detail):
    """Generate sample marketing data based on customer details"""
    customer_id = customer_detail.get('customer_id', 'unknown')
    customer_type = customer_detail.get('customer_type', 'unknown')
    total_spent = customer_detail.get('total_spent', 0)
    purchase_categories = customer_detail.get('purchase_categories', [])
    total_purchases = customer_detail.get('total_purchases', 0)
    
    # Determine customer segment
    if total_spent > 500:
        segment = "VIP"
    elif total_spent > 200:
        segment = "Frequent"
    elif customer_type == 'repeat':
        segment = "Loyal"
    else:
        segment = "New"
    
    # Determine recommended products
    recommended_products = []
    if 'clothing' in purchase_categories:
        recommended_products.extend(['p1001', 'p1002', 'p1007'])
    if 'footwear' in purchase_categories:
        recommended_products.extend(['p1003'])
    if 'accessories' in purchase_categories:
        recommended_products.extend(['p1004', 'p1005', 'p1006'])
    if 'electronics' in purchase_categories:
        recommended_products.extend(['p1008'])
    
    # Determine campaign eligibility
    campaigns = []
    if segment == "VIP":
        campaigns.append("premium_member_discount")
    if total_purchases > 5:
        campaigns.append("loyalty_rewards")
    if 'electronics' in purchase_categories:
        campaigns.append("tech_upgrade")
    if segment == "New":
        campaigns.append("welcome_discount")
    
    # Create the marketing data
    marketing_data = {
        "customer_id": customer_id,
        "customer_type": customer_type,
        "segment": segment,
        "total_spent": total_spent,
        "total_purchases": total_purchases,
        "purchase_categories": purchase_categories,
        "recommended_products": recommended_products,
        "eligible_campaigns": campaigns,
        "last_updated": datetime.now().isoformat()
    }
    
    return marketing_data

def upload_to_s3(data, filename):
    """Upload data to S3 bucket"""
    try:
        s3_key = f"{SOURCE_PREFIX}{filename}"
        
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(data),
            ContentType='application/json'
        )
        
        print(f"Successfully uploaded to s3://{S3_BUCKET}/{s3_key}")
        return True
    except Exception as e:
        print(f"Error uploading to S3: {str(e)}")
        raise e

def start_appflow_flow():
    """Trigger AppFlow flow execution"""
    try:
        response = appflow.start_flow(
            flowName=APPFLOW_FLOW_NAME
        )
        print(f"AppFlow flow started: {response}")
        return response
    except Exception as e:
        print(f"Error starting AppFlow flow: {str(e)}")
        raise e