import boto3
import os
from app import db, sqs
from dotenv import load_dotenv
from beatmaps import fetch_all_beatmaps, fetch_beatmaps_from_profile

queue_url = os.environ.get('QUEUE_URL')

def consume_messages():
    while True:
        response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
        messages = response['Messages']
        
        for message in messages:
            user_id = message['Body']
            receipt_handle = message['ReceiptHandle']
            
            # query DB to see number of maps played
            # if above 20000, fetch_all_beatmaps, otherwise fetch_beatmaps_from_profile
            
            
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        
        
        
        
        