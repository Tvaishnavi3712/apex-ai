"""
Unit tests for S3 Service.
"""
import pytest
import json
from io import BytesIO
from unittest.mock import MagicMock, patch
from moto import mock_s3
import boto3


class TestS3Service:
    """Tests for S3Service class."""

    @pytest.fixture
    def mock_bucket(self):
        """Create a mock S3 bucket."""
        with mock_s3():
            s3 = boto3.client("s3", region_name="us-east-1")
            s3.create_bucket(Bucket="test-bucket")
            yield s3

    @pytest.fixture
    def service(self, mock_bucket):
        """Create S3Service instance with mocked bucket."""
        from backend.services.s3 import S3Service

        with patch.object(S3Service, "__init__", lambda self, bucket_name: None):
            svc = S3Service.__new__(S3Service)
            svc.bucket_name = "test-bucket"
            svc.s3 = mock_bucket
            yield svc

    @pytest.mark.unit
    def test_upload_file_success(self, service, mock_bucket):
        """Test successful file upload."""
        content = b"Test file content"

        service.upload_file(
            content=content,
            key="test/file.txt",
            content_type="text/plain"
        )

        response = mock_bucket.get_object(Bucket="test-bucket", Key="test/file.txt")
        assert response["Body"].read() == content

    @pytest.mark.unit
    def test_upload_file_with_metadata(self, service, mock_bucket):
        """Test file upload with custom metadata."""
        content = b"Test content"
        metadata = {"author": "test-user", "version": "1.0"}

        service.upload_file(
            content=content,
            key="test/meta-file.txt",
            metadata=metadata,
            content_type="text/plain"
        )

        response = mock_bucket.head_object(Bucket="test-bucket", Key="test/meta-file.txt")
        assert response["Metadata"]["author"] == "test-user"

    @pytest.mark.unit
    def test_download_file_existing(self, service, mock_bucket):
        """Test downloading an existing file."""
        mock_bucket.put_object(
            Bucket="test-bucket",
            Key="download/test.txt",
            Body=b"Download content"
        )

        result = service.download_file("download/test.txt")

        assert result == b"Download content"

    @pytest.mark.unit
    def test_download_file_not_found(self, service, mock_bucket):
        """Test downloading non-existent file raises error."""
        with pytest.raises(Exception):
            service.download_file("non-existent/file.txt")

    @pytest.mark.unit
    def test_put_json(self, service, mock_bucket):
        """Test uploading JSON data."""
        data = {"name": "Test", "values": [1, 2, 3]}

        service.put_json("data/test.json", data)

        response = mock_bucket.get_object(Bucket="test-bucket", Key="data/test.json")
        stored_data = json.loads(response["Body"].read().decode("utf-8"))
        assert stored_data == data

    @pytest.mark.unit
    def test_get_json(self, service, mock_bucket):
        """Test retrieving JSON data."""
        data = {"key": "value", "number": 42}
        mock_bucket.put_object(
            Bucket="test-bucket",
            Key="data/retrieve.json",
            Body=json.dumps(data).encode("utf-8")
        )

        result = service.get_json("data/retrieve.json")

        assert result == data

    @pytest.mark.unit
    def test_list_files(self, service, mock_bucket):
        """Test listing files with prefix."""
        # Upload test files
        for i in range(5):
            mock_bucket.put_object(
                Bucket="test-bucket",
                Key=f"list-test/file{i}.txt",
                Body=b"content"
            )
        mock_bucket.put_object(
            Bucket="test-bucket",
            Key="other/file.txt",
            Body=b"content"
        )

        result = service.list_files(prefix="list-test/")

        assert len(result) == 5
        assert all("list-test/" in item["key"] for item in result)

    @pytest.mark.unit
    def test_list_files_with_limit(self, service, mock_bucket):
        """Test listing files with limit."""
        for i in range(10):
            mock_bucket.put_object(
                Bucket="test-bucket",
                Key=f"limit-test/file{i}.txt",
                Body=b"content"
            )

        result = service.list_files(prefix="limit-test/", limit=5)

        assert len(result) == 5

    @pytest.mark.unit
    def test_delete_file(self, service, mock_bucket):
        """Test deleting a file."""
        mock_bucket.put_object(
            Bucket="test-bucket",
            Key="delete/file.txt",
            Body=b"to delete"
        )

        service.delete_file("delete/file.txt")

        # Verify file is deleted
        with pytest.raises(Exception):
            mock_bucket.get_object(Bucket="test-bucket", Key="delete/file.txt")

    @pytest.mark.unit
    def test_delete_prefix(self, service, mock_bucket):
        """Test deleting all files with prefix."""
        for i in range(3):
            mock_bucket.put_object(
                Bucket="test-bucket",
                Key=f"delete-prefix/file{i}.txt",
                Body=b"content"
            )

        service.delete_prefix("delete-prefix/")

        # Verify all files are deleted
        response = mock_bucket.list_objects_v2(
            Bucket="test-bucket",
            Prefix="delete-prefix/"
        )
        assert response.get("KeyCount", 0) == 0

    @pytest.mark.unit
    def test_generate_presigned_url(self, service, mock_bucket):
        """Test generating presigned URL."""
        mock_bucket.put_object(
            Bucket="test-bucket",
            Key="presigned/file.txt",
            Body=b"content"
        )

        url = service.generate_presigned_url("presigned/file.txt", expiration=3600)

        assert url is not None
        assert "presigned/file.txt" in url
        assert "test-bucket" in url or "localhost" in url

    @pytest.mark.unit
    def test_copy_file(self, service, mock_bucket):
        """Test copying a file within bucket."""
        mock_bucket.put_object(
            Bucket="test-bucket",
            Key="source/file.txt",
            Body=b"copy me"
        )

        service.copy_file("source/file.txt", "destination/file.txt")

        # Verify copy exists
        response = mock_bucket.get_object(Bucket="test-bucket", Key="destination/file.txt")
        assert response["Body"].read() == b"copy me"

    @pytest.mark.unit
    def test_get_metadata(self, service, mock_bucket):
        """Test retrieving file metadata."""
        mock_bucket.put_object(
            Bucket="test-bucket",
            Key="metadata/file.txt",
            Body=b"content",
            Metadata={"custom-key": "custom-value"},
            ContentType="text/plain"
        )

        metadata = service.get_metadata("metadata/file.txt")

        assert metadata is not None
        assert "content_type" in metadata or "ContentType" in metadata


class TestS3ServiceErrors:
    """Test error handling in S3Service."""

    @pytest.mark.unit
    def test_upload_to_nonexistent_bucket(self):
        """Test uploading to non-existent bucket raises error."""
        from backend.services.s3 import S3Service

        with patch.object(S3Service, "__init__", lambda self, bucket_name: None):
            svc = S3Service.__new__(S3Service)
            svc.bucket_name = "nonexistent-bucket"
            svc.s3 = MagicMock()
            svc.s3.put_object.side_effect = Exception("Bucket does not exist")

            with pytest.raises(Exception):
                svc.upload_file(b"content", "test.txt")

    @pytest.mark.unit
    def test_invalid_json_get(self):
        """Test getting invalid JSON raises error."""
        from backend.services.s3 import S3Service

        with patch.object(S3Service, "__init__", lambda self, bucket_name: None):
            svc = S3Service.__new__(S3Service)
            svc.s3 = MagicMock()
            svc.s3.get_object.return_value = {
                "Body": BytesIO(b"not valid json {{{")
            }

            with pytest.raises(Exception):
                svc.get_json("invalid.json")
