# digitalden.cloud-backend

Website: https://digitalden.cloud

**Tech-Stack**:
- AWS SAM (IAC)
- AWS Lambda
- DynamoDB
- GitHub Actions

#### Architecture:

### Project Description
Deployed all resources in the back-end using AWS SAM. Backend consists of **API Gateway**, **AWS Lambda** and **DynamoDB** to store and retrieve visitors count.

### DynamoDB
In the SAM template, created a new DynamoDB resource to hold visitor counter data. Named the table visitor-count-table, and created a primary key, ID as a String Type. Set capacity to On-demand to save on costs.

### Lambda Function

### API Gateway

### Github Actions
Set up a CI/CD pipeline on GitHub Actions. The pipeline activates upon pushing code starting with SAM validation, Build and Deploy.

Included an integration test.