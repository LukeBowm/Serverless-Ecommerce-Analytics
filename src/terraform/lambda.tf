# IAM Role for Lambda functions
resource "aws_iam_role" "lambda_role" {
  name = "${var.username}-serverless-ecommerce-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda execution
resource "aws_iam_policy" "lambda_policy" {
  name        = "${var.username}-serverless-ecommerce-lambda-policy"
  description = "Policy for Lambda functions in serverless e-commerce analytics pipeline"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish",
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "events:PutEvents",
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# Mock Data Generator Lambda
resource "aws_lambda_function" "mock_data_generator" {
  function_name = "MockDataGenerator"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_handler.lambda_handler"
  runtime       = "python3.9"
  filename      = "../lambda/mock_data_generator.zip"
  source_code_hash = filebase64sha256("../lambda/mock_data_generator.zip")
  timeout       = 30
  memory_size   = 128

  environment {
    variables = {
      TOPIC_ARN = aws_sns_topic.raw_transaction_data.arn
    }
  }
}

# Order Processor Lambda
resource "aws_lambda_function" "order_processor" {
  function_name = "OrderProcessor"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_handler.lambda_handler"
  runtime       = "python3.9"
  filename      = "../lambda/order_processor.zip"
  source_code_hash = filebase64sha256("../lambda/order_processor.zip")
  timeout       = 30
  memory_size   = 128
}

# Customer Analytics Lambda
resource "aws_lambda_function" "customer_analytics" {
  function_name = "CustomerAnalytics"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_handler.lambda_handler"
  runtime       = "python3.9"
  filename      = "../lambda/customer_analytics.zip"
  source_code_hash = filebase64sha256("../lambda/customer_analytics.zip")
  timeout       = 30
  memory_size   = 128
}

# Inventory Tracker Lambda
resource "aws_lambda_function" "inventory_tracker" {
  function_name = "InventoryTracker"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_handler.lambda_handler"
  runtime       = "python3.9"
  filename      = "../lambda/inventory_tracker.zip"
  source_code_hash = filebase64sha256("../lambda/inventory_tracker.zip")
  timeout       = 30
  memory_size   = 128
}

# Business Logic Lambda
resource "aws_lambda_function" "business_logic" {
  function_name = "BusinessLogic"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_handler.lambda_handler"
  runtime       = "python3.9"
  filename      = "../lambda/business_logic.zip"
  source_code_hash = filebase64sha256("../lambda/business_logic.zip")
  timeout       = 30
  memory_size   = 128
}

# Notification Service Lambda
resource "aws_lambda_function" "notification_service" {
  function_name = "NotificationService"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_handler.lambda_handler"
  runtime       = "python3.9"
  filename      = "../lambda/notification_service.zip"
  source_code_hash = filebase64sha256("../lambda/notification_service.zip")
  timeout       = 30
  memory_size   = 128
}

# AppFlow Trigger Lambda
resource "aws_lambda_function" "appflow_trigger" {
  function_name = "AppFlowTrigger"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_handler.lambda_handler"
  runtime       = "python3.9"
  filename      = "../lambda/appflow_trigger.zip"
  source_code_hash = filebase64sha256("../lambda/appflow_trigger.zip")
  timeout       = 30
  memory_size   = 128
}

# Dashboard API Lambda
resource "aws_lambda_function" "dashboard_api" {
  function_name = "DashboardAPI"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_handler.lambda_handler"
  runtime       = "python3.9"
  filename      = "../lambda/dashboard_api.zip"
  source_code_hash = filebase64sha256("../lambda/dashboard_api.zip")
  timeout       = 30
  memory_size   = 128
}

# Report Generator Lambda
resource "aws_lambda_function" "report_generator" {
  function_name = "ReportGenerator"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_handler.lambda_handler"
  runtime       = "python3.9"
  filename      = "../lambda/report_generator.zip"
  source_code_hash = filebase64sha256("../lambda/report_generator.zip")
  timeout       = 30
  memory_size   = 128
}

# Lambda Event Source Mappings for SQS
resource "aws_lambda_event_source_mapping" "order_processor_mapping" {
  event_source_arn = aws_sqs_queue.order_queue.arn
  function_name    = aws_lambda_function.order_processor.function_name
  batch_size       = 10
}

resource "aws_lambda_event_source_mapping" "customer_analytics_mapping" {
  event_source_arn = aws_sqs_queue.customer_queue.arn
  function_name    = aws_lambda_function.customer_analytics.function_name
  batch_size       = 10
}

resource "aws_lambda_event_source_mapping" "inventory_tracker_mapping" {
  event_source_arn = aws_sqs_queue.inventory_queue.arn
  function_name    = aws_lambda_function.inventory_tracker.function_name
  batch_size       = 10
}
