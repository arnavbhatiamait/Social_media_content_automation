from google.cloud import storage
from pathlib import Path
import os
import dotenv
dotenv.load_dotenv()

from logs_setup.logger import Logger
logger = Logger(name="GCPBucketUpload",log_file="logs/gcp_bucket_upload.log").get_logger()

GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_CREDENTIALS_PATH

class GCPBucketUpload:
    def __init__(self):
        self.client = storage.Client()
        self.bucket_name = os.getenv('GCP_BUCKET_NAME')

    def get_signed_url(self, blob_name: str, expiration_time: int = 3600) -> str:
        try:
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(blob_name)
            url = blob.generate_signed_url(expiration=expiration_time)
            logger.info(f"Generated signed URL for {blob_name}")
            return url
        except Exception as e:
            logger.error(f"Failed to generate signed URL for {blob_name}: {e}")
            raise
    def upload_file(self, local_file_path: str, destination_blob_name: str,make_public: bool = True):

        try:
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(local_file_path)
            if make_public:
                blob.make_public()
                logger.info(f"File {local_file_path} uploaded to {destination_blob_name} and made public.")
                return blob.public_url
            logger.info(f"File {local_file_path} uploaded to {destination_blob_name}.")
            return blob.public_url
        except Exception as e:
            logger.error(f"Failed to upload file {local_file_path} to GCP bucket: {e}")
            raise

    async def upload_file_async(self, local_file_path: str, destination_blob_name: str, make_public: bool = True):

        return self.upload_file(local_file_path, destination_blob_name, make_public)