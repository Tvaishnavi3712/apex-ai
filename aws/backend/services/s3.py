"""
S3 service for document and file storage
"""

import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, List, Optional
import json

from core.config import settings


class S3Service:
    """S3 operations"""

    def __init__(self, bucket_name: str):
        self.s3 = boto3.client('s3', region_name=settings.AWS_REGION)
        self.bucket_name = bucket_name

    async def upload_file(
        self,
        content: bytes,
        key: str,
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None
    ) -> str:
        """Upload a file to S3"""
        try:
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            if content_type:
                extra_args['ContentType'] = content_type

            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content,
                **extra_args
            )

            return f"s3://{self.bucket_name}/{key}"

        except ClientError as e:
            raise Exception(f"Failed to upload to S3: {str(e)}")

    async def download_file(self, key: str) -> bytes:
        """Download a file from S3"""
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            return response['Body'].read()
        except ClientError as e:
            raise Exception(f"Failed to download from S3: {str(e)}")

    async def get_json(self, key: str) -> Dict[str, Any]:
        """Download and parse a JSON file"""
        content = await self.download_file(key)
        return json.loads(content.decode('utf-8'))

    async def put_json(self, key: str, data: Dict[str, Any]) -> str:
        """Upload JSON data to S3"""
        content = json.dumps(data, indent=2).encode('utf-8')
        return await self.upload_file(content, key, content_type='application/json')

    async def list_files(self, prefix: str = "", limit: int = 1000) -> List[Dict[str, Any]]:
        """List files in a bucket with prefix"""
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=limit
            )

            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'etag': obj['ETag']
                })

            return files

        except ClientError as e:
            raise Exception(f"Failed to list S3 objects: {str(e)}")

    async def delete_file(self, key: str) -> None:
        """Delete a file from S3"""
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
        except ClientError as e:
            raise Exception(f"Failed to delete from S3: {str(e)}")

    async def delete_prefix(self, prefix: str) -> int:
        """Delete all files with a prefix"""
        try:
            files = await self.list_files(prefix)
            deleted_count = 0

            for file in files:
                await self.delete_file(file['key'])
                deleted_count += 1

            return deleted_count

        except ClientError as e:
            raise Exception(f"Failed to delete prefix from S3: {str(e)}")

    async def get_presigned_url(
        self,
        key: str,
        expiration: int = 3600,
        operation: str = 'get_object'
    ) -> str:
        """Generate a presigned URL for temporary access"""
        try:
            url = self.s3.generate_presigned_url(
                operation,
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")

    async def copy_file(self, source_key: str, dest_key: str) -> str:
        """Copy a file within the bucket"""
        try:
            self.s3.copy_object(
                Bucket=self.bucket_name,
                CopySource={'Bucket': self.bucket_name, 'Key': source_key},
                Key=dest_key
            )
            return f"s3://{self.bucket_name}/{dest_key}"
        except ClientError as e:
            raise Exception(f"Failed to copy S3 object: {str(e)}")

    async def get_metadata(self, key: str) -> Dict[str, str]:
        """Get object metadata"""
        try:
            response = self.s3.head_object(Bucket=self.bucket_name, Key=key)
            return response.get('Metadata', {})
        except ClientError as e:
            raise Exception(f"Failed to get S3 metadata: {str(e)}")
