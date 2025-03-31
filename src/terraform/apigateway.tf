# API Gateway for transaction data generation
resource "aws_api_gateway_rest_api" "ecommerce_api" {
  name        = "E-commerce-Analytics-API"
  description = "API for E-commerce Analytics Pipeline"
}

# /generate-data resource
resource "aws_api_gateway_resource" "generate_data_resource" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  parent_id   = aws_api_gateway_rest_api.ecommerce_api.root_resource_id
  path_part   = "generate-data"
}

# POST method for /generate-data
resource "aws_api_gateway_method" "generate_data_post" {
  rest_api_id   = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id   = aws_api_gateway_resource.generate_data_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# Integration with Lambda
resource "aws_api_gateway_integration" "generate_data_lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.generate_data_resource.id
  http_method = aws_api_gateway_method.generate_data_post.http_method
  
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.mock_data_generator.invoke_arn
}

# Method response
resource "aws_api_gateway_method_response" "generate_data_response_200" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.generate_data_resource.id
  http_method = aws_api_gateway_method.generate_data_post.http_method
  status_code = "200"
  
  response_models = {
    "application/json" = "Empty"
  }
}

# OPTIONS method for CORS
resource "aws_api_gateway_method" "generate_data_options" {
  rest_api_id   = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id   = aws_api_gateway_resource.generate_data_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

# OPTIONS integration
resource "aws_api_gateway_integration" "generate_data_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.generate_data_resource.id
  http_method = aws_api_gateway_method.generate_data_options.http_method
  
  type = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

# OPTIONS method response
resource "aws_api_gateway_method_response" "generate_data_options_response_200" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.generate_data_resource.id
  http_method = aws_api_gateway_method.generate_data_options.http_method
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true,
    "method.response.header.Access-Control-Allow-Methods" = true,
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

# OPTIONS integration response
resource "aws_api_gateway_integration_response" "generate_data_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  resource_id = aws_api_gateway_resource.generate_data_resource.id
  http_method = aws_api_gateway_method.generate_data_options.http_method
  status_code = aws_api_gateway_method_response.generate_data_options_response_200.status_code
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS,POST'",
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "ecommerce_api_deployment" {
  depends_on = [
    aws_api_gateway_integration.generate_data_lambda_integration,
    aws_api_gateway_integration.generate_data_options_integration
  ]
  
  rest_api_id = aws_api_gateway_rest_api.ecommerce_api.id
  stage_name  = "dev"
}

# Permission for API Gateway to invoke Lambda
resource "aws_lambda_permission" "api_gateway_lambda_permission" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.mock_data_generator.function_name
  principal     = "apigateway.amazonaws.com"
  
  source_arn = "${aws_api_gateway_rest_api.ecommerce_api.execution_arn}/*/*"
}

# Dashboard API Gateway
resource "aws_api_gateway_rest_api" "dashboard_api" {
  name        = "Dashboard-API"
  description = "API for E-commerce Analytics Dashboard"
}

# /api resource
resource "aws_api_gateway_resource" "api_resource" {
  rest_api_id = aws_api_gateway_rest_api.dashboard_api.id
  parent_id   = aws_api_gateway_rest_api.dashboard_api.root_resource_id
  path_part   = "api"
}

# GET method for /api
resource "aws_api_gateway_method" "api_get" {
  rest_api_id   = aws_api_gateway_rest_api.dashboard_api.id
  resource_id   = aws_api_gateway_resource.api_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

# Integration with Lambda
resource "aws_api_gateway_integration" "api_lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.dashboard_api.id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = aws_api_gateway_method.api_get.http_method
  
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.dashboard_api.invoke_arn
}

# Simplified CORS configuration for /api
resource "aws_api_gateway_method" "api_options" {
  rest_api_id   = aws_api_gateway_rest_api.dashboard_api.id
  resource_id   = aws_api_gateway_resource.api_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "api_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.dashboard_api.id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = aws_api_gateway_method.api_options.http_method
  
  type = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "api_options_response_200" {
  rest_api_id = aws_api_gateway_rest_api.dashboard_api.id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = aws_api_gateway_method.api_options.http_method
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true,
    "method.response.header.Access-Control-Allow-Methods" = true,
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

resource "aws_api_gateway_integration_response" "api_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.dashboard_api.id
  resource_id = aws_api_gateway_resource.api_resource.id
  http_method = aws_api_gateway_method.api_options.http_method
  status_code = aws_api_gateway_method_response.api_options_response_200.status_code
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'",
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }
}

# Dashboard API deployment
resource "aws_api_gateway_deployment" "dashboard_api_deployment" {
  depends_on = [
    aws_api_gateway_integration.api_lambda_integration,
    aws_api_gateway_integration.api_options_integration
  ]
  
  rest_api_id = aws_api_gateway_rest_api.dashboard_api.id
  stage_name  = "prod"
}

# Permission for API Gateway to invoke Dashboard API Lambda
resource "aws_lambda_permission" "dashboard_api_lambda_permission" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.dashboard_api.function_name
  principal     = "apigateway.amazonaws.com"
  
  source_arn = "${aws_api_gateway_rest_api.dashboard_api.execution_arn}/*/*"
}
