from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, ContentSettings
from datetime import datetime, timedelta
from typing import Optional, BinaryIO
from config import settings
import logging
import os
import uuid

logger = logging.getLogger(__name__)


class BlobStorageClient:
    def __init__(self):
        self.blob_service_client = BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string
        )
        self.container_name = settings.blob_container_name
        self.container_client = None

    def initialize(self):
        """Initialize blob container"""
        try:
            # Create container if it doesn't exist
            self.container_client = (
                self.blob_service_client.get_container_client(self.container_name)
            )
            if not self.container_client.exists():
                self.container_client.create_container()
                logger.info(f"Container '{self.container_name}' created")
            else:
                logger.info(f"Container '{self.container_name}' already exists")
        except Exception as e:
            logger.error(f"Failed to initialize blob storage: {e}")
            raise

    def upload_file(
        self, file: BinaryIO, user_id: str, original_filename: str, content_type: str
    ) -> tuple[str, str]:
        """
        Upload file to blob storage
        Returns: (blob_name, blob_url)
        """
        try:
            # Generate unique filename
            file_extension = os.path.splitext(original_filename)[1]
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            blob_name = f"{user_id}/{timestamp}_{unique_id}{file_extension}"

            # Upload to blob storage
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=blob_name
            )

            blob_client.upload_blob(
                file,
                content_settings=ContentSettings(content_type=content_type),
                overwrite=True,
            )

            # Generate URL with SAS token
            blob_url = self._generate_blob_url_with_sas(blob_name)

            logger.info(f"File uploaded successfully: {blob_name}")
            return blob_name, blob_url

        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise

    def delete_file(self, blob_name: str) -> bool:
        """Delete file from blob storage"""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=blob_name
            )
            blob_client.delete_blob()
            logger.info(f"File deleted successfully: {blob_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False

    def _generate_blob_url_with_sas(
        self, blob_name: str, expiry_hours: int = 24 * 365
    ) -> str:
        """Generate blob URL with SAS token"""
        try:
            # Get account name and key from connection string
            connection_parts = {
                part.split("=", 1)[0]: part.split("=", 1)[1]
                for part in settings.azure_storage_connection_string.split(";")
                if "=" in part
            }
            account_name = connection_parts.get("AccountName")
            account_key = connection_parts.get("AccountKey")

            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=account_name,
                account_key=account_key,
                container_name=self.container_name,
                blob_name=blob_name,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=expiry_hours),
            )

            # Construct URL
            blob_url = f"https://{account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas_token}"
            return blob_url

        except Exception as e:
            logger.error(f"Failed to generate SAS URL: {e}")
            # Return URL without SAS as fallback
            return f"https://{account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"

    def get_blob_url(self, blob_name: str) -> str:
        """Get blob URL with SAS token"""
        return self._generate_blob_url_with_sas(blob_name)


# Global instance
blob_storage = BlobStorageClient()
