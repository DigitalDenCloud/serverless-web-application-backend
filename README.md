# digitalden.cloud-backend

Website: https://digitalden.cloud

In the backend I create a visitor counter that is displayed on my webpage and updated every time there is a new visitor. The optimal way to do this is with a serverless app using the following tech stack:

**Tech-Stack**:
- AWS SAM (IAC)
- DynamoDB
- AWS Lambda
- API Gateway
- JavaScript
- GitHub Actions

#### Architecture:

### Project Description
Deployed all resources in the back-end using AWS SAM. Backend consists of **API Gateway**, **AWS Lambda** and **DynamoDB** and **DynamoDB JavaScript** to store and retrieve visitors count.

### DynamoDB
In the SAM template, created a new DynamoDB resource to hold visitor counter data. Named the table visitor-count-table. Set capacity to On-demand to save on costs. Holds a single attribute which will be updated by the Lambda function.

### Lambda Function
There are two types of Architectural Patterns.

**Monolithic Function** (Putting all code in single Lambda Deployment)
**Single Purposed Function** (Each Lambda per Functionality)

When deciding what architetural pattern to use there are many trade-offs between monoliths and services. 

A monolithic function that has more branching and in general does more things, would understandably take more cognitive effort to comprehend and follow through to the code that is relevant to the problem at hand.

Initally, I had started off by creating a single Monolithic lambda function, but then opted to create two single purposed functions.

I reconfigured my Hello World Function, and created a GET function for for getting values out of my database and a PUT functions for putting items into my DynamdoDB table.

### Java Scippt and API Gateway
The SAM CLI deploys API infrastructure under the hood. Rest API allows access to URL endpoint to accept GET and POST methods. When API URL is accessed the Lambda function is invoked, returning data from DynamoDB table.

Configured CORS headers. In the response of my Lambda Function,  I added the Access-Control-Allow-Origin headers and set the allow origin as “*”.

In index.html added a Java Script thats going to make a fetch request to my API from API gateway.

### Github Actions
Set up a CI/CD pipeline on GitHub Actions. The pipeline activates upon pushing code starting with SAM Validation, Build and Deploy.

Included an integration test, which test the API endpoint.

![Integration Test](resources/images/integration-test.png)

The test calls the GET API using curl and then calls my domain, digitalden.cloud. It Uses JQ, a query for JSON to grab the count property and then stores it in a variable.

The test then calls the API using curl, for a second time. However, this time it adds to the count, which increases the value, and stores it into a second variable.

If the first request is less than the second, the test passes.
