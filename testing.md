# Testing Guide for Serverless E-commerce Analytics

## End-to-End Testing

### 1. Generate Transaction Data
- Access the data generation API endpoint
- Send a POST request to trigger data generation
- Verify SNS message is published

### 2. Verify Data Processing
- Check CloudWatch logs for Lambda functions
- Verify records in DynamoDB tables
- Confirm EventBridge events are being triggered

### 3. Test Dashboard API
- Access the Dashboard API endpoints
- Verify data retrieval from DynamoDB
- Check response formats

### 4. Test Frontend Application
- Access CloudFront URL
- Verify dashboard loads and displays data
- Test report generation and download

## Component Testing

### Lambda Functions
- Test each Lambda function individually using AWS Lambda console
- Provide test events matching expected input formats
- Verify outputs and side effects

### API Gateway
- Test each API endpoint using Postman or curl
- Verify proper request/response handling
- Test error conditions

### DynamoDB
- Query tables directly to verify data structure
- Test access patterns used by Lambda functions

## Performance Testing
- Test concurrent Lambda executions
- Monitor CloudWatch metrics for bottlenecks
- Verify scaling behavior under load
