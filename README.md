<br />

<p align="center">
  <a href="img/">
    <img src="resources/images/digitalden.cloud-backend-architecture-2.png" alt="architecture">
  </a>
  <h1 align="center">A Serverless Website: Backend Repo</h1>
<p align="center">
    Built on AWS using AWS SAM CLI for IaC and GitHub Actions for CI/CD. 
    <br />
    Website: https://digitalden.cloud
    <br />
  </p>



</p>

<details open="open">
  <summary><h2 style="display: inline-block">Project Details</h2></summary>
  <ol>
    <li><a href="#tech-stack">Tech Stack</a>
    <li><a href="#project-date">Project Date</a></li>
    </li>
    <li><a href="#project-description">Project Description</a></li>
    <li><a href="#aws-sam-cli">AWS SAM CLI</a></li>    
    <li><a href="#dynamodb">DynamoDB</a></li>
    <li><a href="#lambda-function">Lambda Function</a></li>
    <li><a href="#api-gateway-and-javascript">API Gateway and JavaScript</a></li>
    <li><a href="#github-actions">Github Actions</a></li>
    <li><a href="#project-files">Project Files</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>

### Tech Stack
------------------
- AWS SAM
- DynamoDB
- AWS Lambda
- API Gateway
- JavaScript
- GitHub Actions

### Project Description
------------------

To deploy my architecture I used SAM CLI as my Infrastructure as Code method and GitHub Actions as my CI/CD method.

The backend components of my website support a counter of visitors to my  website.  The data (visitor count value) is stored in a DynamoDB database, which is accessed by a Lambda function written in Python3.  The function is accessed through a REST API created with API Gateway, which when called will invoke the Lambda function and forward back the direct response due to a “Lambda proxy” configuration.  Each time the page is loaded, a short JavaScript script utilizes Fetch API to ping the endpoint of my counter API, before rendering the response in the footer of the page.  My site can now fetch and display the latest visitor count, while the Lambda function handled incrementation as it interacted exclusively with the database.

### Project date
------------------
16.04-2023

### AWS SAM CLI
------------------

The AWS SAM CLI is a command line tool that I used with AWS SAM templates to build and run my serverless applications. 

#### Initialized my project

- I use the sam init command to initialize a new application project. I selected the Python for my Lambda code and Hello World Example project to start with. The AWS SAM CLI downloaded a starter template and created my project folder directory structure.

- The stack included API Gateway, IAM Role and Lambda function.

#### Built my application for deployment

- I packaged my function dependencies and organized my project code and folder structure to prepare for deployment.

- I used the sam build command to prepare my application for deployment. The AWS SAM CLI created a .aws-samdirectory and organized my application dependencies and files there for deployment.

#### Performed local debugging and testing

- I used the sam local invoke command to invoke my GetCountFunction and PutCountFunction locally. To accomplish this, the AWS SAM CLI created a local container, built my function, invokes it, and outputs the results.

![Sam Local Invoke](resources/images/sam-local-invoke-putcountfunction.png)

#### Deployed my application

- I configured my application's deployment settings and deployed to the AWS Cloud to provision my resources.

- I used the sam deploy --guided command to deploy my application through an interactive flow. The AWS SAM CLI guided me through configuring my application's deployment settings, transformed my template into AWS CloudFormation, and deployed to AWS CloudFormation to create my resources.

### DynamoDB
------------------
In the SAM template, I created a new DynamoDBTable resource to hold visitor count data. Named the table visitor-count-table. Set capacity to On-demand to save on costs. The table holds a single attribute (ID), which will be updated by the Lambda function.

```yaml
  DynamoDBTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: visitor-count-table
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: "ID"
            AttributeType: "S"
        KeySchema:
          - AttributeName: "ID"
            KeyType: "HASH"
```

### Lambda Function
------------------
There are two types of architectural patterns.

- Monolithic Function (Putting all code in single Lambda deployment)
- Single Purposed Function (Each Lambda per functionality)

When deciding what architectural pattern to use there are many trade-offs between monoliths and services. A monolithic function has more branching and in general does more things, this would understandably take more cognitive effort to comprehend and follow through to the code that is relevant to the problem at hand.

Initally, I created a single monolithic Lambda function:

```python
import json
import boto3
from boto3.dynamodb.conditions import Key

TABLE_NAME = "visitor-count-table"

dynamodb_client = boto3.client('dynamodb', region_name="eu-west-2")

dynamodb_table = boto3.resource('dynamodb', region_name="eu-west-2")
table = dynamodb_table.Table(TABLE_NAME)

def lambda_handler(event, context):
    response = table.get_item(
        TableName =TABLE_NAME,
        Key={
            "ID":'visitors',
        }
        )
    item = response['Item']

    table.update_item(
        Key={
            "ID":'visitors',
        },
        UpdateExpression='SET visitors = :val1',
        ExpressionAttributeValues={
            ':val1': item['visitors'] + 1
        }
    )
    return{
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
      "body": json.dumps({"Visit_Count": str(item['visitors'] + 1)})
    }
```

However, after reading a really interesting article by Yan Cui, [AWS Lambda – should you have few monolithic functions or many single-purposed functions?](https://theburningmonk.com/2018/01/aws-lambda-should-you-have-few-monolithic-functions-or-many-single-purposed-functions/)

I decided to break my monolithic function into two single-purposed functions. I achieved this by reconfiguring my Hello World Function deployed by SAM CLI, and created a get-function for getting values out of my database, and a put-function for putting items into my database:

```yaml
  GetCountFunction:
    Type: AWS::Serverless::Function
    Properties:
      Policies:
        - DynamoDBCrudPolicy:
            TableName: visitor-count-table
      CodeUri: lambda-functions/single-purposed-functions/get-function/
      Handler: app.lambda_handler
      Runtime: python3.9
      Architectures:
        - x86_64
      Events:
        HelloWorld:
          Type: Api 
          Properties:
            Path: /get
            Method: get
```
```yaml
  PutCountFunction:
    Type: AWS::Serverless::Function
    Properties:
      Policies:
        - DynamoDBCrudPolicy:
            TableName: visitor-count-table
      CodeUri: lambda-functions/single-purposed-functions/put-function/
      Handler: app.lambda_handler
      Runtime: python3.9
      Architectures:
        - x86_64
      Events:
        HelloWorld:
          Type: Api
          Properties:
            Path: /put
            Method: get
```

#### Get-Function

I then updated my python in the functions:

```python
import boto3
import json
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('visitor-count-table')

def get_count():
    response = table.query(
        KeyConditionExpression=Key('ID').eq('visitors')
        )
    count = response['Items'][0]['visitors']
    return count

def lambda_handler(event, context):
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Credentials': '*',
            'Content-Type': 'application/json'
        },
        'body': get_count()
    }
```

#### Put-Function

```python
import boto3
import json
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('visitor-count-table')


def lambda_handler(event, context):
    response = table.update_item(     
        Key={        
            'ID': 'visitors'
        },   
        UpdateExpression='ADD ' + 'visitors' + ' :incr',
        ExpressionAttributeValues={        
            ':incr': 1    
        },    
        ReturnValues="UPDATED_NEW"
    )

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Credentials': '*',
            'Content-Type': 'application/json'
        }
    }
```

### API Gateway and JavaScript
------------------
The SAM CLI deploys API infrastructure under the hood. Rest API allows access to my URL endpoint to accept GET and POST methods. When API URL is accessed the Lambda function is invoked, returning data from my DynamoDB table.

It was important to configure CORS headers. In the response of my Lambda Function,  I added the Access-Control-Allow-Origin headers:

```python
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Credentials': '*',
            'Content-Type': 'application/json'
        }
    }
```

In the index.html I added a JavaScript that makes a fetch request to my API from API gateway.

```javascript
  <script type = "text/javascript">
    var apiUrl = "https://0qrguua9jg.execute-api.eu-west-2.amazonaws.com/Prod/put";
      fetch(apiUrl)
      .then(() => fetch("https://0qrguua9jg.execute-api.eu-west-2.amazonaws.com/Prod/get"))
      .then(response => response.json())
      .then(data =>{
          document.getElementById('hits').innerHTML = data
    console.log(data)});
  </script>
```

My website can now fetch and display the latest visitor count.

### Github Actions
------------------
I set up a CI/CD pipeline on GitHub Actions. The pipeline activates upon pushing code starting with SAM Validation, Build and Deploy.

```yaml
jobs:  
  build-and-deploy-infra:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - uses: aws-actions/setup-sam@v1
      - uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-west-2
      - name: SAM Validate
        run: |
          sam validate
      - name: SAM Build
        run: |
          sam build
      - name: SAM Deploy
        run: |
          sam deploy --no-confirm-changeset --no-fail-on-empty-changeset
```

This workflow updates the SAM stack currently deployed. The AWS access keys are stored as GitHub Secrets and the user has very limited access to resources. The SAM Deploy assumes a role to deploy the needed resources. This project is utilizing GitHub Actions over an AWS CodePipeline for cost savings and is a better alternative based on the scope of this project.

Included an integration test, which tests the GET API endpoint:

```bash
integration-test:
		FIRST=$$(curl -s "https://0qrguua9jg.execute-api.eu-west-2.amazonaws.com/Prod/get" | jq ".body| tonumber"); \
		curl -s "https://0qrguua9jg.execute-api.eu-west-2.amazonaws.com/Prod/put"; \
		SECOND=$$(curl -s "https://0qrguua9jg.execute-api.eu-west-2.amazonaws.com/Prod/get" | jq ".body| tonumber"); \
		echo "Comparing if first count ($$FIRST) is less than (<) second count ($$SECOND)"; \
		if [[ $$FIRST -le $$SECOND ]]; then echo "PASS"; else echo "FAIL";  fi
```  

This script performs the following steps:

1. Sends a GET request to the URL https://0qrguua9jg.execute-api.eu-west-2.amazonaws.com/Prod/get" and retrieves the value of the "body" field from the JSON response using the jq command, which is then assigned to the variable FIRST.

2. Sends a PUT request to the URL "https://0qrguua9jg.execute-api.eu-west-2.amazonaws.com/Prod/put".

3. Sends another GET request to the same URL as step 1 and retrieves the value of the "body" field from the JSON response using jq, which is then assigned to the variable SECOND.

4. Prints a message that compares the values of FIRST and SECOND to see if FIRST is less than or equal to SECOND.

5. If FIRST is less than or equal to SECOND, it prints "PASS", otherwise it prints "FAIL".

### Project Files
------------------
* [SAM template](template.yaml)

### Acknowledgements
------------------
* [Cloud Resume Challenge](https://cloudresumechallenge.dev/)
