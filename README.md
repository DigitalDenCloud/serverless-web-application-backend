# digitalden.cloud-backend

Website: https://digitalden.cloud

In the backend I created a visitor counter that is displayed on my webpage and updated every time there is a new visitor. The optimal way to do this is with a serverless app using the following tech stack:

**Tech-Stack**:
- AWS SAM (IAC)
- DynamoDB
- AWS Lambda
- API Gateway
- JavaScript
- GitHub Actions

### Architecture

### Project Description
Deployed all resources in the back-end using AWS SAM. Backend consists of **API Gateway**, **AWS Lambda** and **DynamoDB** and **DynamoDB JavaScript** to store and retrieve visitors count.

### DynamoDB
In the SAM template, created a new DynamoDB resource to hold visitor count data. Named the table visitor-count-table. Set capacity to On-demand to save on costs. Holds a single attribute which will be updated by the Lambda function.

```
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
There are two types of architectural patterns.

- Monolithic Function (Putting all code in single Lambda deployment)
- Single Purposed Function (Each Lambda per functionality)

When deciding what architetural pattern to use there are many trade-offs between monoliths and services. A monolithic function has more branching and in general does more things, this would understandably take more cognitive effort to comprehend and follow through to the code that is relevant to the problem at hand.

Initally, I created a single monolithic Lambda function:

```
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

However, I read a really interesting article by Yan Cui about monolithic functions and single-purposed functions. You can read that [HERE](https://theburningmonk.com/2018/01/aws-lambda-should-you-have-few-monolithic-functions-or-many-single-purposed-functions/).

I decided to break my monolithic function. I reconfigured my Hello World Function, and created a get-function for for getting values out of my database:

```
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
and then created a put-function for putting items into my DynamdoDB table:

```
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
The SAM CLI deploys API infrastructure under the hood. Rest API allows access to URL endpoint to accept GET and POST methods. When API URL is accessed the Lambda function is invoked, returning data from DynamoDB table.

Configured CORS headers. In the response of my Lambda Function,  I added the Access-Control-Allow-Origin headers and set the allow origin as “*”.

```
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

In the index.html I added a JavaScript thats going to make a fetch request to my API from API gateway.

```
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

### Github Actions
Set up a CI/CD pipeline on GitHub Actions. The pipeline activates upon pushing code starting with SAM Validation, Build and Deploy.

```
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

Included an integration test, which test the GET API endpoint:

```
integration-test:
		FIRST=$$(curl -s "https://0qrguua9jg.execute-api.eu-west-2.amazonaws.com/Prod/get" | jq ".body| tonumber"); \
		curl -s "https://0qrguua9jg.execute-api.eu-west-2.amazonaws.com/Prod/put"; \
		SECOND=$$(curl -s "https://0qrguua9jg.execute-api.eu-west-2.amazonaws.com/Prod/get" | jq ".body| tonumber"); \
		echo "Comparing if first count ($$FIRST) is less than (<) second count ($$SECOND)"; \
		if [[ $$FIRST -le $$SECOND ]]; then echo "PASS"; else echo "FAIL";  fi
```  

- The test calls the GET API using curl and then calls my domain, digitalden.cloud. It Uses JQ, a query for JSON to grab the count property and then stores it in a variable.
- The test then calls the API using curl, for a second time. However, this time it adds to the count, which increases the value, and stores it into a second variable.
- If the first request is less than the second, the test passes.
