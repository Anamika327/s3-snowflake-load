import boto3
import pandas as pd
import os
from datetime import datetime

class S3DataIngest:
    def __init__(self, bucket_name):
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name

    def upload_file(self, file_path, s3_path):
        try:
            self.s3_client.upload_file(file_path, s3_path)
            print(f'Successfully uploaded {file_path} to s3://{self.bucket_name}/{s3_path}')
        except Exception as e:
            print(f'Error uploading file: {e}')

    def ingest_csv(self, csv_file_path):
        today = datetime.utcnow().strftime('%Y/%m/%d')
        s3_key = os.path.join('data', today, os.path.basename(csv_file_path))
        self.upload_file(csv_file_path, s3_key)

    def ingest_json(self, json_file_path):
        today = datetime.utcnow().strftime('%Y/%m/%d')
        s3_key = os.path.join('data', today, os.path.basename(json_file_path))
        self.upload_file(json_file_path, s3_key)

if __name__ == '__main__':
    # Example usage: Initialize with your S3 bucket name
    ingestion = S3DataIngest('your-bucket-name')
    ingestion.ingest_csv('path/to/your/file.csv')
    ingestion.ingest_json('path/to/your/file.json')