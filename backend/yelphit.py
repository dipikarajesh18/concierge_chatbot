from yelpapi import YelpAPI
import json
import pprint
import boto3
import datetime
from elasticsearch import Elasticsearch

api_key = "zkmV1ThUFeKMrjdeNWz0rTZfMkeKWW3FyTYe9If4yBQgRy_uc7jiUU90GYPr4F3z-VvJoi8RxkyrHUui4FP6y4QExkOamcLdLr4rynqCNyZpZ4MoOc7DA2MFC4RLXnYx" #  Replace this with your real API key

session = boto3.Session(
    aws_access_key_id="AKIAS7XHH6FMIJTZCEU2",
    aws_secret_access_key="oMs4uc3SLTAwu934+KXaee44QivlbBqoJGHhPHOe",
)


yelp_api = YelpAPI(api_key)
cuisines = ['italian', 'indian', 'chinese', 'japanese', 'thai', 'mexican']
items = []
pp = pprint.PrettyPrinter(indent=4)
for c in cuisines:
    for i in range(0, 1000, 50):
        search_results = yelp_api.search_query(term=c, location="manhattan", limit=50, offset=i)
        for rest in search_results["businesses"]:
            address = ""
            for st in rest["location"]["display_address"]:
                address += st
                address += " "
            resObj = {
                "id" : rest["id"],
                "name" : rest["name"],
                "address" : address[:-2],
                "cuisine" : c,
                "alias" : rest["alias"],
                "categories" : rest["categories"],
                "rating": int(rest["rating"]),
                "review_count": rest["review_count"]
            }
            items.append(resObj)


# print(len(items))
def insertIntoDynamo(items):
    dynamodb = session.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('yelp-restaurants')
    for resObj in items:
        table.put_item(
                Item={
                    'insertedAtTimestamp': str(datetime.datetime.now()),
                    'info': resObj,
                    'id': resObj['id']
                }
            )

def insertIntoElastic(items):
    es = Elasticsearch(['https://search-restaurants-pjsfkf5mcw4srdcztrgkaan5si.us-east-1.es.amazonaws.com/'])
    all_indices = es.indices.get_alias("*")
    # print(all_indices)
    if 'restaurants' not in all_indices:
        es.indices.create(index='restaurants')
    for resObj in items:
        insItem = {
            'id':resObj['id'],
            'cuisine': resObj['cuisine']
        }
        es.index(index='restaurants', body=insItem)

# insertIntoDynamo(items)
insertIntoElastic(items)

def deleteDynamo():
    dynamodb = session.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('yelp-restaurants')
    scan = None

    with table.batch_writer() as batch:
        count = 0
        while scan is None or 'LastEvaluatedKey' in scan:
            if scan is not None and 'LastEvaluatedKey' in scan:
                scan = table.scan(
                    ProjectionExpression='id',
                    ExclusiveStartKey=scan['LastEvaluatedKey'],
                )
            else:
                scan = table.scan(ProjectionExpression='id')

            for item in scan['Items']:
                if count % 5000 == 0:
                    print(count)
                batch.delete_item(Key={'id': item['id']})
                count = count + 1
# deleteDynamo()


# getEs("indian")