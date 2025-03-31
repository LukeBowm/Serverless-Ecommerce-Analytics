# Cost Analysis

This document provides an analysis of the AWS costs associated with running this serverless e-commerce analytics project.

## AWS Free Tier Utilization

This project is deliberately designed to stay within AWS Free Tier limits for most services. Below is a breakdown of how different services are utilized.

### Lambda
- **Free Tier**: 1 million requests per month and 400,000 GB-seconds of compute time
- **Project Usage**: Estimated 500,000 invocations per month with 128MB memory allocation
- **Cost Impact**: Should remain within free tier for moderate usage

### API Gateway
- **Free Tier**: 1 million API calls per month for the first 12 months
- **Project Usage**: Estimated 50,000-100,000 API calls per month
- **Cost Impact**: Should remain within free tier

### DynamoDB
- **Free Tier**: 25 GB of storage and 25 units of read/write capacity
- **Project Usage**: Less than 1 GB of data and on-demand pricing
- **Cost Impact**: Should remain within free tier for demo purposes

### SNS/SQS
- **Free Tier**: 1 million SNS publishes and 1 million SQS requests
- **Project Usage**: Estimated 50,000 messages per month
- **Cost Impact**: Should remain within free tier

### CloudFront
- **Free Tier**: 1 TB of data transfer out and 10 million HTTP/HTTPS requests per month
- **Project Usage**: Minimal for a demo application
- **Cost Impact**: Should remain within free tier

### S3
- **Free Tier**: 5 GB of standard storage, 20,000 GET requests, 2,000 PUT requests
- **Project Usage**: Less than 1 GB for frontend app and reports
- **Cost Impact**: Should remain within free tier

### EventBridge
- **Free Tier**: No specific free tier, but 1 million events published are $1.00
- **Project Usage**: Estimated 50,000 events per month
- **Cost Impact**: Approximately $0.05 per month

### AppFlow
- **Free Tier**: No specific free tier
- **Project Usage**: Minimal flows per month for demo purposes
- **Cost Impact**: Approximately $0.10-$1.00 per month

## Total Estimated Cost

### Within Free Tier Period (First 12 Months)
- **Estimated Monthly Cost**: $0.15 - $1.05
- **Estimated Annual Cost**: $1.80 - $12.60

### After Free Tier
- **Estimated Monthly Cost**: $20 - $30
- **Estimated Annual Cost**: $240 - $360

## Cost Optimization Strategies

This project implements several cost optimization strategies:

1. **Serverless Architecture**: Pay only for what you use, no idle resources
2. **Right-sized Lambda Functions**: 128MB memory allocation for most functions
3. **DynamoDB On-Demand Pricing**: Scales with usage, no over-provisioning
4. **CloudFront Caching**: Reduces origin requests and improves performance
5. **Short Lambda Timeouts**: Prevents runaway costs from hung functions
6. **Automated Cleanup**: The Terraform scripts make it easy to tear down all resources

## Monitoring Costs

To monitor costs:

1. **AWS Cost Explorer**: Check actual service usage
2. **CloudWatch Metrics**: Monitor resource utilization
3. **AWS Budgets**: Set up alerts for cost thresholds

## Cost-Conscious Development

When extending this project, consider:

1. **Lambda Cold Starts**: Balance between memory allocation and performance
2. **DynamoDB Access Patterns**: Design efficient queries to minimize RCU/WCU
3. **S3 Storage Classes**: Use appropriate storage classes for different data types
4. **API Gateway Caching**: Enable caching for frequently accessed endpoints
5. **CloudFront Optimization**: Configure proper TTLs and compression

## Conclusion

This serverless architecture provides an excellent balance between functionality and cost efficiency. By leveraging AWS free tier offerings and pay-per-use services, the project can be run with minimal expense while still demonstrating a comprehensive set of cloud capabilities.