import boto3

# Create SQS client
sqs = boto3.client('sqs', aws_access_key_id="AKIAS7XHH6FMIJTZCEU2", aws_secret_access_key="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")
queue_url = 'https://sqs.us-east-1.amazonaws.com/205569651032/concierge'
delaySeconds = 5
messageAttributes = {
    'cuisine': {
        'DataType': 'String',
        'StringValue': 'thai'
    },
    'location': {
        'DataType': 'String',
        'StringValue': 'brooklyn'
    },
    "time": {
        'DataType': "String",
        'StringValue': '8pm'
    },
    "date": {
        'DataType': "String",
        'StringValue': 'today'
    },
    'numPeople': {
        'DataType': 'Number',
        'StringValue': '3'
    },
    'phone': {
        'DataType' : 'String',
        'StringValue' : '3478818075'
    }
}
messageBody=('Recommendation for the food')

response = sqs.send_message(
    QueueUrl = queue_url,
    DelaySeconds = delaySeconds,
    MessageAttributes = messageAttributes,
    MessageBody = messageBody
    )

print(response['MessageId'])