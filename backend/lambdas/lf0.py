import json
import boto3

def lambda_handler(event, context):
    # TODO implement
    print("This is the event : ",event);
    client = boto3.client('lex-runtime')
    # print(json.loads(event).body)
    uid="Sowmiya24" 
    response = client.post_text(botName='DiningConcierge',botAlias='$LATEST',userId=uid, inputText=event['body']['message'])
    print(response)
    return {
        'statusCode' : 200,
        'body' : response['message']
    }
    # return {
    #     'statusCode' : 200,
    #     'body' : json.dumps('Chatbot under development. Please be patience.')
    # }
    # return {
    #     'statusCode': 200,
    #     'body': json.dumps('Hello from Lambda!')
    # }


