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
