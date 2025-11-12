"""
AWS S3 Service for uploading/downloading live monitoring recordings
"""
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from django.conf import settings
import logging
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class S3Service:
    """AWS S3 client wrapper for live monitoring recordings"""
    
    def __init__(self):
        """Initialize S3 client with credentials from settings"""
        self.bucket_name = settings.AWS_LIVE_MONITORING_BUCKET_NAME
        self.region = settings.AWS_LIVE_MONITORING_REGION_NAME
        
        try:
            self.client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_LIVE_MONITORING_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_LIVE_MONITORING_SECRET_ACCESS_KEY,
                region_name=self.region
            )
            logger.info(f"✅ S3 client initialized for bucket: {self.bucket_name}")
        except NoCredentialsError:
            logger.error("❌ AWS credentials not found in settings")
            raise
        except Exception as e:
            logger.error(f"❌ Error initializing S3 client: {e}")
            raise
    
    def upload_video(
        self, 
        file_path: Path, 
        s3_key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Upload video file to S3
        
        Args:
            file_path: Path to local video file
            s3_key: S3 object key (e.g., "recordings/2025/01/video.mp4")
            metadata: Optional metadata dict
            
        Returns:
            S3 URL of uploaded file or None if failed
        """
        try:
            if not file_path.exists():
                logger.error(f"❌ File not found: {file_path}")
                return None
            
            # Upload with metadata
            extra_args = {
                'ContentType': 'video/mp4',
            }
            
            if metadata:
                extra_args['Metadata'] = metadata
            
            logger.info(f"📤 Uploading {file_path.name} to s3://{self.bucket_name}/{s3_key}")
            
            self.client.upload_file(
                str(file_path),
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            
            # Generate URL
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            logger.info(f"✅ Upload successful: {s3_url}")
            return s3_url
            
        except FileNotFoundError:
            logger.error(f"❌ File not found: {file_path}")
            return None
        except ClientError as e:
            logger.error(f"❌ S3 ClientError during upload: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error during upload: {e}")
            return None
    
    def download_video(self, s3_key: str, download_path: Path) -> bool:
        """
        Download video from S3
        
        Args:
            s3_key: S3 object key
            download_path: Local path to save file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"📥 Downloading s3://{self.bucket_name}/{s3_key} to {download_path}")
            
            # Ensure parent directory exists
            download_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.client.download_file(
                self.bucket_name,
                s3_key,
                str(download_path)
            )
            
            logger.info(f"✅ Download successful: {download_path}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ S3 ClientError during download: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error during download: {e}")
            return False
    
    def delete_video(self, s3_key: str) -> bool:
        """
        Delete video from S3
        
        Args:
            s3_key: S3 object key to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"🗑️ Deleting s3://{self.bucket_name}/{s3_key}")
            
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"✅ Deletion successful: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ S3 ClientError during deletion: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error during deletion: {e}")
            return False
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate presigned URL for temporary access
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Presigned URL or None if failed
        """
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            
            logger.info(f"🔗 Generated presigned URL for {s3_key} (expires in {expiration}s)")
            return url
            
        except ClientError as e:
            logger.error(f"❌ Error generating presigned URL: {e}")
            return None
    
    def list_recordings(self, prefix: str = "recordings/") -> list:
        """
        List all recordings in S3 bucket
        
        Args:
            prefix: S3 key prefix to filter (default: "recordings/")
            
        Returns:
            List of S3 object metadata dictionaries
        """
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                logger.info(f"📂 No recordings found with prefix: {prefix}")
                return []
            
            recordings = []
            for obj in response['Contents']:
                recordings.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'url': f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{obj['Key']}"
                })
            
            logger.info(f"📋 Found {len(recordings)} recordings with prefix: {prefix}")
            return recordings
            
        except ClientError as e:
            logger.error(f"❌ Error listing recordings: {e}")
            return []
