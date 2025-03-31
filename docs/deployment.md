# Deployment Guide

This guide provides step-by-step instructions for deploying the Serverless E-commerce Analytics Pipeline.

## Prerequisites

- AWS CLI installed and configured with appropriate permissions
- Terraform v1.0.0+ installed
- Node.js and npm installed (for frontend development)
- Git installed

## Deployment Steps

### 1. Clone the Repository

```bash
git clone https://github.com/LukeBowm/serverless-ecommerce-analytics.git
cd serverless-ecommerce-analytics
```

### 2. Deploy the Infrastructure with Terraform

```bash
cd terraform

# Initialize Terraform
terraform init

# Preview the changes
terraform plan

# Deploy the infrastructure
terraform apply
```

When prompted, type `yes` to confirm the deployment. The deployment will take approximately 5-10 minutes to complete.

Upon successful deployment, Terraform will output several important URLs, including:
- Frontend URL (CloudFront distribution)
- API Gateway endpoints
- Other resource identifiers

### 3. Build and Deploy the Frontend

```bash
# Navigate to the frontend directory
cd ../serverless-ecommerce-dashboard

# Install dependencies
npm install

# Update the API endpoint in the configuration
# Edit src/config.js with the API Gateway URL from Terraform output

# Build the application
npm run build

# Deploy to S3 (this will be automated via GitHub Actions for CI/CD)
aws s3 sync build/ s3://lukebowm-serverless-ecommerce-frontend/ --delete
```

### 4. Verify the Deployment

1. **Access the frontend** using the CloudFront URL provided in the Terraform output
2. **Test data generation** by sending a POST request to the data generation API endpoint
3. **Verify data processing** by checking for records in the DynamoDB tables
4. **Test report generation** from the dashboard

## Troubleshooting

### Common Issues

1. **Access Denied for S3**
   - Ensure the CloudFront distribution has proper OAI configuration
   - Check S3 bucket policy allows the CloudFront OAI

2. **API Gateway CORS Issues**
   - Verify OPTIONS method is properly configured
   - Ensure CORS headers are correctly set up

3. **Lambda Function Errors**
   - Check CloudWatch logs for each Lambda function
   - Verify IAM permissions are correctly set

## CI/CD Pipeline

This project includes a GitHub Actions workflow for continuous deployment. When properly configured:

1. Commits to the main branch will trigger the workflow
2. Terraform infrastructure will be validated and applied
3. Frontend will be built and deployed to S3

To set up GitHub Actions:

1. Configure AWS credentials as GitHub repository secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

2. Push your code to the main branch to trigger a deployment

## Clean Up

To avoid incurring charges, you can tear down the infrastructure when not in use:

```bash
cd terraform
terraform destroy
```

When prompted, type `yes` to confirm deletion of all resources.