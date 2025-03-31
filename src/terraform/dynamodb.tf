# DynamoDB Tables
resource "aws_dynamodb_table" "customer_profiles" {
  name         = "CustomerProfiles"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "customer_id"

  attribute {
    name = "customer_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "inventory_status" {
  name         = "InventoryStatus"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "product_id"

  attribute {
    name = "product_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "sales_metrics" {
  name         = "SalesMetrics"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "metric_key"

  attribute {
    name = "metric_key"
    type = "S"
  }
}

resource "aws_dynamodb_table" "customer_insights" {
  name         = "CustomerInsights"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "insight_key"

  attribute {
    name = "insight_key"
    type = "S"
  }
}

resource "aws_dynamodb_table" "notifications" {
  name         = "Notifications"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "notification_id"

  attribute {
    name = "notification_id"
    type = "S"
  }
}
