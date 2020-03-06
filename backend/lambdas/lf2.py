import json
import boto3
import json
from elasticsearch import Elasticsearch

def getEsData(cuisine):
    query = {
        "size": 5,
        "query": {
            "match": {
                "cuisine":cuisine
            }
        }
    }
    es = Elasticsearch(['https://search-temp-fjykqtiytwbo6eomvvxvxhh4w4.us-east-1.es.amazonaws.com/'])
    result = es.search(index='example_index', body=query)
    listofrest = result['hits']['hits']
    restans = []
    for rest in listofrest:
        restans.append(rest['_source']["id"])
    # print("This is restans : ",restans)
    return restans

def getFromDynamo(ids):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('yelp-restaurants')
    item = []
    for id in ids:
        result = table.get_item(Key={
            'id': id
        })
        item.append(result['Item']['info'])
    return item

def sendMessage(cuisine, information, phone):
    session = boto3.Session()
    sns_client = session.client('sns')
    message = "Your recommendations for "+str(cuisine)+" restaurants are \n"
    for i in range(len(information)):
        rec = information[i]
        # print("This is rec : ",rec)
        message += (str(i+1) + '. ')
        message += (rec['name'] + " at " + rec['address'])
        message += "\n"
        if i!=len(information)-1:
            message += " "
        else:
            message += "."
    
    print("The message is : ",message)
    sns_client.publish(
        PhoneNumber=phone,
        Message=message,
        MessageAttributes={
            'AWS.SNS.SMS.SenderID': {
                'DataType': 'String',
                'StringValue': 'SENDERID'
            },
            'AWS.SNS.SMS.SMSType': {
                'DataType': 'String',
                'StringValue': 'Promotional'
            }
        }
    )
    
queue = 'https://sqs.us-east-1.amazonaws.com/205569651032/concierge'

def lambda_handler(event, context):
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/205569651032/concierge'
    # tempsqs = boto3.resource('sqs')
    # queueval = tempsqs.Queue(queue_url)
    deleteids = []
    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ], 
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    print("Message has been received from sqs : ",response)
    if (response and 'Messages' in response):
        # print(response['Messages'])
        cuisine = response['Messages'][0]["MessageAttributes"]["cuisine"]["StringValue"]
        phone = response['Messages'][0]["MessageAttributes"]["phone"]["StringValue"]
        if phone[0]!='+':
            if phone[0]!='1':
                phone = "+1" + phone
            else:
                phone = "+" + phone
        print(cuisine, phone)
        ids = getEsData(cuisine)
        result = getFromDynamo(ids)
        sendMessage(cuisine,result, phone)
        sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=response["Messages"][0]["ReceiptHandle"])
        print(result)
    return response;
