# SNS Topic
resource "aws_sns_topic" "raw_transaction_data" {
  name = "RawTransactionData"
}

# SQS Queues
resource "aws_sqs_queue" "order_queue" {
  name                      = "OrderQueue"
  visibility_timeout_seconds = 60
}

resource "aws_sqs_queue" "customer_queue" {
  name                      = "CustomerQueue"
  visibility_timeout_seconds = 60
}

resource "aws_sqs_queue" "inventory_queue" {
  name                      = "InventoryQueue"
  visibility_timeout_seconds = 60
}

# SQS Queue Policies
resource "aws_sqs_queue_policy" "order_queue_policy" {
  queue_url = aws_sqs_queue.order_queue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "sns.amazonaws.com"
        }
        Action = "sqs:SendMessage"
        Resource = aws_sqs_queue.order_queue.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_sns_topic.raw_transaction_data.arn
          }
        }
      }
    ]
  })
}

resource "aws_sqs_queue_policy" "customer_queue_policy" {
  queue_url = aws_sqs_queue.customer_queue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "sns.amazonaws.com"
        }
        Action = "sqs:SendMessage"
        Resource = aws_sqs_queue.customer_queue.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_sns_topic.raw_transaction_data.arn
          }
        }
      }
    ]
  })
}

resource "aws_sqs_queue_policy" "inventory_queue_policy" {
  queue_url = aws_sqs_queue.inventory_queue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "sns.amazonaws.com"
        }
        Action = "sqs:SendMessage"
        Resource = aws_sqs_queue.inventory_queue.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_sns_topic.raw_transaction_data.arn
          }
        }
      }
    ]
  })
}

# SNS Subscriptions
resource "aws_sns_topic_subscription" "order_subscription" {
  topic_arn = aws_sns_topic.raw_transaction_data.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.order_queue.arn
}

resource "aws_sns_topic_subscription" "customer_subscription" {
  topic_arn = aws_sns_topic.raw_transaction_data.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.customer_queue.arn
}

resource "aws_sns_topic_subscription" "inventory_subscription" {
  topic_arn = aws_sns_topic.raw_transaction_data.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.inventory_queue.arn
}
