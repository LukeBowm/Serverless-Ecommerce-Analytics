output "mock_data_generator_lambda" {
  value = aws_lambda_function.mock_data_generator.function_name
  description = "Mock Data Generator Lambda Function"
}

output "sns_topic_arn" {
  value = aws_sns_topic.raw_transaction_data.arn
  description = "SNS Topic ARN for Raw Transaction Data"
}

output "data_api_gateway_url" {
  value = "${aws_api_gateway_deployment.ecommerce_api_deployment.invoke_url}/generate-data"
  description = "URL to trigger data generation"
}

output "dashboard_api_url" {
  value = "${aws_api_gateway_deployment.dashboard_api_deployment.invoke_url}/api"
  description = "Dashboard API URL"
}

output "frontend_url" {
  value = "https://${aws_cloudfront_distribution.frontend_distribution.domain_name}"
  description = "Frontend URL"
}

output "reports_bucket" {
  value = aws_s3_bucket.reports_bucket.bucket
  description = "S3 Bucket for reports"
}

output "appflow_bucket" {
  value = aws_s3_bucket.appflow_bucket.bucket
  description = "S3 Bucket for AppFlow data"
}
