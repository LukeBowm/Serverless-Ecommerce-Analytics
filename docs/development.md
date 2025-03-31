# Development Guide

This guide provides instructions for local development and testing of the Serverless E-commerce Analytics Pipeline.

## Local Development Environment Setup

### Prerequisites

- Node.js (v14+) and npm
- Python 3.9+
- AWS CLI configured with appropriate permissions
- Terraform (for infrastructure changes)
- Git

### Frontend Development

The dashboard is built with React and uses several libraries for UI components and data visualization.

#### Setting up the Frontend

```bash
# Navigate to the frontend directory
cd serverless-ecommerce-dashboard

# Install dependencies
npm install

# Start the development server
npm start
```

This will start a local development server at http://localhost:3000 that connects to your deployed AWS backend services.

#### Modifying the API Endpoint

During development, you'll need to connect to your deployed API Gateway endpoints. Update the API endpoint in the configuration file:

```javascript
// src/config.js
const config = {
  apiUrl: 'https://ssowmx2oq6.execute-api.us-west-1.amazonaws.com/prod'
};

export default config;
```

Replace the URL with your actual API Gateway endpoint.

### Backend Development

The backend consists of several Lambda functions that process data and interact with other AWS services.

#### Lambda Function Development

1. **Local Testing of Lambda Functions**

   You can use the AWS SAM CLI to test Lambda functions locally:

   ```bash
   # Install AWS SAM CLI
   pip install aws-sam-cli

   # Create a test event file (e.g., event.json)
   # Then invoke the function locally
   sam local invoke -e event.json "FunctionName"
   ```

2. **Modifying Lambda Functions**

   After making changes to Lambda functions:

   ```bash
   # Create a deployment package
   cd src/lambda/function_directory
   zip -r ../function_name.zip .

   # Update the Lambda function
   aws lambda update-function-code \
     --function-name FunctionName \
     --zip-file fileb://function_name.zip
   ```

### Infrastructure Development

The project uses Terraform for infrastructure as code.

#### Modifying Terraform Configuration

1. Make changes to the Terraform files in the `terraform` directory
2. Run `terraform validate` to check for syntax errors
3. Run `terraform plan` to preview the changes
4. Apply changes with `terraform apply`

## Testing

### Frontend Testing

```bash
# Run React unit tests
cd serverless-ecommerce-dashboard
npm test
```

### Backend Testing

Test individual Lambda functions:

```bash
# Invoke a Lambda function directly
aws lambda invoke \
  --function-name FunctionName \
  --payload fileb://test-event.json \
  response.json

# Check the response
cat response.json
```

### End-to-End Testing

For end-to-end testing:

1. **Generate test data** through the API Gateway endpoint:
   ```bash
   curl -X POST https://ssowmx2oq6.execute-api.us-west-1.amazonaws.com/dev/generate-data
   ```

2. **Verify data flow** through the system by checking:
   - CloudWatch logs for each Lambda function
   - Records in DynamoDB tables
   - Frontend dashboard visualizations

## Debugging

### CloudWatch Logs

For backend debugging, check CloudWatch logs:

```bash
# Get log streams for a Lambda function
aws logs describe-log-streams \
  --log-group-name "/aws/lambda/FunctionName" \
  --order-by LastEventTime \
  --descending

# Get log events
aws logs get-log-events \
  --log-group-name "/aws/lambda/FunctionName" \
  --log-stream-name "log-stream-name"
```

### React Developer Tools

For frontend debugging:
1. Install the React Developer Tools browser extension
2. Use browser developer console (F12) to debug frontend issues
3. Set up React's development environment with `REACT_APP_DEBUG=true`

## Best Practices

- Use consistent code formatting (ESLint and Prettier)
- Write unit tests for Lambda functions
- Add comments for complex logic
- Keep Lambda functions small and focused
- Use environment variables for configuration
- Document API changes
- Follow the serverless application model best practices

## CI/CD Integration

The GitHub Actions workflow will automatically build and deploy changes when you push to the main branch. For feature development:

1. Create a feature branch
2. Make and test your changes
3. Create a pull request
4. After review and approval, merge to main
5. The CI/CD pipeline will handle deployment