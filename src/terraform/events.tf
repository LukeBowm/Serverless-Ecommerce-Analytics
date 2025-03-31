# EventBridge Rules
resource "aws_cloudwatch_event_rule" "order_processed_rule" {
  name        = "OrderProcessedRule"
  description = "Rule for order processed events"

  event_pattern = jsonencode({
    source      = ["com.ecommerce.orders"]
    detail-type = ["order_processed"]
  })
}

resource "aws_cloudwatch_event_rule" "customer_analyzed_rule" {
  name        = "CustomerAnalyzedRule"
  description = "Rule for customer analyzed events"

  event_pattern = jsonencode({
    source      = ["com.ecommerce.customers"]
    detail-type = ["customer_analyzed"]
  })
}

resource "aws_cloudwatch_event_rule" "inventory_updated_rule" {
  name        = "InventoryUpdatedRule"
  description = "Rule for inventory updated events"

  event_pattern = jsonencode({
    source      = ["com.ecommerce.inventory"]
    detail-type = ["inventory_updated", "inventory_alert"]
  })
}

resource "aws_cloudwatch_event_rule" "notification_rule" {
  name        = "NotificationRule"
  description = "Rule for notification events"

  event_pattern = jsonencode({
    source      = ["com.ecommerce.orders", "com.ecommerce.inventory", "com.ecommerce.customers"]
    detail-type = ["order_processed", "inventory_alert", "customer_analyzed"]
  })
}

resource "aws_cloudwatch_event_rule" "customer_to_appflow_rule" {
  name        = "CustomerToAppFlowRule"
  description = "Rule for triggering AppFlow integration"

  event_pattern = jsonencode({
    source      = ["com.ecommerce.customers"]
    detail-type = ["customer_analyzed"]
  })
}

# EventBridge Targets
resource "aws_cloudwatch_event_target" "business_logic_order_target" {
  rule      = aws_cloudwatch_event_rule.order_processed_rule.name
  target_id = "BusinessLogicTarget"
  arn       = aws_lambda_function.business_logic.arn
}

resource "aws_cloudwatch_event_target" "business_logic_customer_target" {
  rule      = aws_cloudwatch_event_rule.customer_analyzed_rule.name
  target_id = "BusinessLogicTarget"
  arn       = aws_lambda_function.business_logic.arn
}

resource "aws_cloudwatch_event_target" "business_logic_inventory_target" {
  rule      = aws_cloudwatch_event_rule.inventory_updated_rule.name
  target_id = "BusinessLogicTarget"
  arn       = aws_lambda_function.business_logic.arn
}

resource "aws_cloudwatch_event_target" "notification_target" {
  rule      = aws_cloudwatch_event_rule.notification_rule.name
  target_id = "NotificationTarget"
  arn       = aws_lambda_function.notification_service.arn
}

resource "aws_cloudwatch_event_target" "appflow_trigger_target" {
  rule      = aws_cloudwatch_event_rule.customer_to_appflow_rule.name
  target_id = "AppFlowTriggerTarget"
  arn       = aws_lambda_function.appflow_trigger.arn
}

# Lambda permissions for EventBridge
resource "aws_lambda_permission" "business_logic_orders_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.business_logic.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.order_processed_rule.arn
}

resource "aws_lambda_permission" "business_logic_customers_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.business_logic.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.customer_analyzed_rule.arn
}

resource "aws_lambda_permission" "business_logic_inventory_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.business_logic.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.inventory_updated_rule.arn
}

resource "aws_lambda_permission" "notification_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.notification_service.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.notification_rule.arn
}

resource "aws_lambda_permission" "appflow_trigger_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.appflow_trigger.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.customer_to_appflow_rule.arn
}

# S3 bucket for AppFlow data
resource "aws_s3_bucket" "appflow_bucket" {
  bucket = "${var.username}-appflow-data"
}

resource "aws_s3_bucket_public_access_block" "appflow_bucket_access" {
  bucket = aws_s3_bucket.appflow_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# AppFlow bucket policy for service access
resource "aws_s3_bucket_policy" "appflow_bucket_policy" {
  bucket = aws_s3_bucket.appflow_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "appflow.amazonaws.com"
        }
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject",
          "s3:GetBucketAcl",
          "s3:PutObjectAcl"
        ]
        Resource = [
          aws_s3_bucket.appflow_bucket.arn,
          "${aws_s3_bucket.appflow_bucket.arn}/*"
        ]
      }
    ]
  })
}
