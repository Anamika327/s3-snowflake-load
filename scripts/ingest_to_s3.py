import argparse
import os
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Union, Dict, List
import pandas as pd
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class S3DataIngester:
    """
    Handles data ingestion from local files to AWS S3.
    Supports CSV, JSON formats with automatic partitioning.
    """
    
    def __init__(self, bucket_name: str = None, aws_profile: str = None):
        """
        Initialize S3 Data Ingester.
        
        Args:
            bucket_name (str): S3 bucket name. If None, reads from S3_BUCKET env var.
            aws_profile (str): AWS profile name. If None, uses default credentials.
        """
        try:
            self.bucket_name = bucket_name or os.getenv('S3_BUCKET')
            if not self.bucket_name:
                raise ValueError("S3_BUCKET not provided and not found in environment variables")
            
            session = boto3.Session(profile_name=aws_profile)
            self.s3_client = session.client('s3')
            
            # Verify bucket exists and is accessible
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"✅ Successfully connected to S3 bucket: {self.bucket_name}")
            
        except NoCredentialsError:
            logger.error("❌ AWS credentials not found.")
            raise
        except ClientError as e:
            logger.error(f"❌ Failed to connect to S3: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            raise
    
    def _generate_s3_key(self, file_path: str, s3_prefix: str, add_timestamp: bool = True) -> str:
        """Generate S3 key with date partitioning."""
        file_name = Path(file_path).stem
        file_ext = Path(file_path).suffix
        
        now = datetime.now()
        date_partition = f"year={now.year}/month={now.month:02d}/day={now.day:02d}"
        
        if add_timestamp:
            timestamp = now.strftime('%H%M%S')
            s3_key = f"{s3_prefix}{date_partition}/{file_name}_{timestamp}{file_ext}"
        else:
            s3_key = f"{s3_prefix}{date_partition}/{file_name}{file_ext}"
        
        return s3_key
    
    def ingest_csv(self, file_path: str, s3_prefix: str = 'raw/', add_metadata: bool = True) -> Dict:
        """Ingest CSV file to S3."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            df = pd.read_csv(file_path)
            logger.info(f"📖 Read {len(df)} rows from {Path(file_path).name}")
            
            if add_metadata:
                df['_ingested_at'] = datetime.now().isoformat()
                df['_source_file'] = Path(file_path).name
                logger.info("📝 Added metadata columns")
            
            s3_key = self._generate_s3_key(file_path, s3_prefix)
            
            csv_buffer = df.to_csv(index=False)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=csv_buffer.encode('utf-8'),
                ContentType='text/csv'
            )
            
            logger.info(f"✅ Uploaded to s3://{self.bucket_name}/{s3_key}")
            
            return {
                'success': True,
                'file_path': file_path,
                's3_uri': f"s3://{self.bucket_name}/{s3_key}",
                'rows_ingested': len(df),
                'columns': list(df.columns),
                'ingestion_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def ingest_json(self, file_path: str, s3_prefix: str = 'raw/', add_metadata: bool = True) -> Dict:
        """Ingest JSON file to S3."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                data = [data]
            
            logger.info(f"📖 Read {len(data)} records from {Path(file_path).name}")
            
            if add_metadata:
                ingestion_metadata = {
                    '_ingested_at': datetime.now().isoformat(),
                    '_source_file': Path(file_path).name,
                    '_record_count': len(data)
                }
                data = {**ingestion_metadata, 'records': data}
            
            s3_key = self._generate_s3_key(file_path, s3_prefix)
            
            json_body = json.dumps(data, default=str, indent=2)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json_body.encode('utf-8'),
                ContentType='application/json'
            )
            
            logger.info(f"✅ Uploaded to s3://{self.bucket_name}/{s3_key}")
            
            return {
                'success': True,
                'file_path': file_path,
                's3_uri': f"s3://{self.bucket_name}/{s3_key}",
                'records_ingested': len(data),
                'ingestion_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def ingest_file(self, file_path: str, s3_prefix: str = 'raw/', add_metadata: bool = True) -> Dict:
        """Ingest file based on extension."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = Path(file_path).suffix.lower()
        logger.info(f"🚀 Starting ingestion for {Path(file_path).name}")
        
        if file_ext == '.csv':
            return self.ingest_csv(file_path, s3_prefix, add_metadata)
        elif file_ext == '.json':
            return self.ingest_json(file_path, s3_prefix, add_metadata)
        else:
            error_msg = f"Unsupported file type: {file_ext}"
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def batch_ingest(self, directory: str, s3_prefix: str = 'raw/', file_pattern: str = None) -> List[Dict]:
        """Ingest multiple files from directory."""
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Directory not found: {directory}")
        
        logger.info(f"📂 Batch ingesting from: {directory}")
        
        path = Path(directory)
        if file_pattern:
            files = list(path.glob(file_pattern))
        else:
            files = [f for f in path.glob('*') if f.suffix.lower() in ['.csv', '.json']]
        
        if not files:
            logger.warning(f"⚠️ No files found")
            return []
        
        logger.info(f"Found {len(files)} files")
        
        results = []
        for file in files:
            result = self.ingest_file(str(file), s3_prefix)
            results.append(result)
        
        successful = sum(1 for r in results if r.get('success', False))
        logger.info(f"✅ Complete: {successful}/{len(files)} successful")
        
        return results


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Ingest data files (CSV/JSON) to AWS S3',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python ingest_to_s3.py --input data.csv
  python ingest_to_s3.py --batch ./data --file-pattern "*.csv"
  python ingest_to_s3.py --input data.json --s3-prefix raw/orders/
        '''
    )
    
    parser.add_argument('--input', help='Input file path (CSV or JSON)')
    parser.add_argument('--batch', help='Directory for batch ingestion')
    parser.add_argument('--s3-prefix', default='raw/', help='S3 prefix')
    parser.add_argument('--file-pattern', help='File pattern (e.g., *.csv)')
    parser.add_argument('--bucket', help='S3 bucket name')
    parser.add_argument('--no-metadata', action='store_true', help='Skip metadata')
    parser.add_argument('--aws-profile', help='AWS profile')
    
    args = parser.parse_args()
    
    try:
        ingester = S3DataIngester(bucket_name=args.bucket, aws_profile=args.aws_profile)
        
        if args.input:
            result = ingester.ingest_file(args.input, args.s3_prefix, not args.no_metadata)
            if result['success']:
                print(f"\n✅ Success! S3 URI: {result['s3_uri']}")
            else:
                print(f"\n❌ Failed: {result['error']}")
                sys.exit(1)
        elif args.batch:
            results = ingester.batch_ingest(args.batch, args.s3_prefix, args.file_pattern)
            successful = sum(1 for r in results if r.get('success'))
            print(f"\n✅ Batch complete: {successful}/{len(results)} successful")
        else:
            parser.print_help()
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
