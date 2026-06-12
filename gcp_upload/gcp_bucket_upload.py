from google.cloud import storage
from pathlib import Path
import os
import dotenv
import asyncio
dotenv.load_dotenv()

from logs_setup.logger import Logger
logger = Logger(name="GCPBucketUpload",log_file="logs/gcp_bucket_upload.log").get_logger()

GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_CREDENTIALS_PATH
GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH")

if not GCP_CREDENTIALS_PATH:
    raise ValueError("GCP_CREDENTIALS_PATH not set")
class GCPBucketUpload:
    def __init__(self):
        self.client = storage.Client()
        self.bucket_name = os.getenv('GCP_BUCKET_NAME')

        if not self.bucket_name:
            raise ValueError("GCP_BUCKET_NAME not set")

    def get_signed_url(self, blob_name: str, expiration_time: int = 3600) -> str:
        try:
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(blob_name)
            url = blob.generate_signed_url(version="v4", expiration=expiration_time, method="GET")
            logger.info(f"Generated signed URL for {blob_name}")
            return url
        except Exception as e:
            logger.error(f"Failed to generate signed URL for {blob_name}: {e}")
            raise


    def upload_file(
        self,
        local_file_path: str,
        destination_blob_name: str,
        make_public: bool = False
    ) -> dict:
        """
        Upload a file to Google Cloud Storage.

        Returns:
            {
                "bucket": str,
                "blob_name": str,
                "filename": str,
                "public_url": str | None,
                "gs_url": str,
                "size_bytes": int
            }
        """

        try:
            file_path = Path(local_file_path)

            if not file_path.exists():
                raise FileNotFoundError(
                    f"File not found: {local_file_path}"
                )

            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(destination_blob_name)

            import mimetypes
            content_type, _ = mimetypes.guess_type(str(file_path))
            if content_type:
                blob.upload_from_filename(str(file_path), content_type=content_type)
            else:
                blob.upload_from_filename(str(file_path))

            public_url = None

            # if make_public:
            #     blob.make_public()
            #     public_url = blob.public_url

            result = {
                "bucket": self.bucket_name,
                "blob_name": destination_blob_name,
                "filename": file_path.name,
                "public_url": public_url,
                "gs_url": f"gs://{self.bucket_name}/{destination_blob_name}",
                "size_bytes": file_path.stat().st_size,
            }

            logger.info(
                f"Uploaded '{local_file_path}' "
                f"to '{destination_blob_name}'"
            )

            return result

        except Exception as e:
            logger.exception(
                f"Failed to upload '{local_file_path}' "
                f"to '{destination_blob_name}': {e}"
            )
            raise

    async def upload_file_async(self, local_file_path: str, destination_blob_name: str, make_public: bool = True):

        return await asyncio.to_thread(self.upload_file, local_file_path, destination_blob_name, make_public)

    def upload_files(self, files: list):
        urls = []
        for file in files:
            local_file_path = file['local_file_path']
            destination_blob_name = file['destination_blob_name']
            url = self.upload_file(local_file_path, destination_blob_name)
            urls.append(url)
        return urls

    async def upload_files_async(self, files: list):
        tasks = [
            self.upload_file_async(
                file["local_file_path"],
                file["destination_blob_name"]
            )
            for file in files
        ]

        return await asyncio.gather(*tasks)