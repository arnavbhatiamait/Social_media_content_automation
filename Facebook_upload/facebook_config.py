import os
import requests
from typing import List
from dotenv import load_dotenv
load_dotenv()

from pathlib import Path 
from sys import path 
path.append(str(Path(__file__).resolve().parent.parent))  

from logs_setup.logger import Logger
logger = Logger(name="FacebookPublisher", log_file="logs/facebook_publisher.log").get_logger()




class FacebookPublisher:

    GRAPH_URL = "https://graph.facebook.com/v23.0"

    def __init__(self, page_id: str, access_token: str):
        self.page_id = page_id
        self.access_token = access_token
        logger.info("FacebookPublisher initialized")

    def _make_url(self, endpoint: str):
        logger.debug(f"Constructing URL for endpoint: {endpoint}")
        return f"{self.GRAPH_URL}/{endpoint}"

    ##################################################################
    # TEXT POST
    ##################################################################

    def post_text(self, message: str):

        url = self._make_url(f"{self.page_id}/feed")

        payload = {
            "message": message,
            "access_token": self.access_token
        }

        logger.debug(f"Sending text post request to {url}")
        response = requests.post(url, data=payload)
        response.raise_for_status()
        logger.info("Text post successful")

        return response.json()

    ##################################################################
    # IMAGE POST
    ##################################################################

    def post_image(self, image_path: str, caption: str = ""):

        url = self._make_url(f"{self.page_id}/photos")
        logger.debug(f"Sending image post request to {url} with image {image_path}")
        
        if image_path.startswith("http://") or image_path.startswith("https://"):
            data = {
                "url": image_path,
                "caption": caption,
                "access_token": self.access_token
            }
            response = requests.post(url, data=data)
        else:
            with open(image_path, "rb") as image:
                files = {
                    "source": image
                }
                data = {
                    "caption": caption,
                    "access_token": self.access_token
                }
                response = requests.post(
                    url,
                    files=files,
                    data=data
                )

        logger.debug(f"Image post response: {response.json()}")
        response.raise_for_status()

        return response.json()

    ##################################################################
    # CAROUSEL / ALBUM POST
    ##################################################################

    def post_carousel(
        self,
        image_paths: List[str],
        caption: str = ""
    ):

        media_ids = []
        logger.debug(f"Uploading {len(image_paths)} images for carousel post")

        for image_path in image_paths:

            logger.debug(f"Uploading image {image_path} for carousel post")
            upload_url = self._make_url(
                f"{self.page_id}/photos"
            )

            with open(image_path, "rb") as image:

                files = {
                    "source": image
                }

                data = {
                    "published": "false",
                    "access_token": self.access_token
                }

                response = requests.post(
                    upload_url,
                    files=files,
                    data=data
                )
                logger.debug(f"Image upload response: {response.json()}")

            response.raise_for_status()

            media_ids.append(
                response.json()["id"]
            )

        attached_media = []

        for media_id in media_ids:
            attached_media.append(
                {"media_fbid": media_id}
            )

        logger.debug(f"Creating carousel post with media IDs: {media_ids}")
        post_url = self._make_url(
            f"{self.page_id}/feed"
        )

        payload = {
            "message": caption,
            "access_token": self.access_token
        }
        logger.debug(f"Payload for carousel post: {payload}")
        for idx, media in enumerate(attached_media):
            payload[f"attached_media[{idx}]"] = str(media)

        response = requests.post(
            post_url,
            data=payload
        )
        logger.debug(f"Carousel post response: {response.json()}")
        response.raise_for_status()

        return response.json()

    ##################################################################
    # LONG VIDEO
    ##################################################################

    def upload_video(
        self,
        video_path: str,
        title: str = "",
        description: str = ""
    ):
        logger.debug(f"Uploading video {video_path} with title '{title}' and description '{description}'")
        url = self._make_url(
            f"{self.page_id}/videos"
        )
        logger.debug(f"Constructed video upload URL: {url}")
        with open(video_path, "rb") as video:

            files = {
                "source": video
            }

            data = {
                "title": title,
                "description": description,
                "access_token": self.access_token
            }

            response = requests.post(
                url,
                files=files,
                data=data
            )

        logger.debug(f"Video upload response: {response.json()}")
        response.raise_for_status()

        return response.json()

    ##################################################################
    # REEL
    ##################################################################

    def upload_reel(
        self,
        video_path: str,
        description: str = ""
    ):
        url = self._make_url(f"{self.page_id}/video_reels")
        logger.debug(f"Constructed reel upload URL: {url}")

        # Step 1: START
        logger.info("Initializing Reel upload (START phase)...")
        init_res = requests.post(
            url,
            data={
                "upload_phase": "START",
                "access_token": self.access_token
            }
        )
        init_res.raise_for_status()
        init_data = init_res.json()
        video_id = init_data.get("video_id")
        upload_url = init_data.get("upload_url")

        if not video_id or not upload_url:
            raise RuntimeError(f"Failed to initialize Facebook Reel upload: {init_data}")

        # Step 2: Upload Video File bytes
        logger.info(f"Uploading Reel file bytes ({os.path.getsize(video_path)} bytes)...")
        file_size = os.path.getsize(video_path)
        headers = {
            "Authorization": f"OAuth {self.access_token}",
            "offset": "0",
            "file_size": str(file_size),
            "Content-Type": "application/octet-stream"
        }

        with open(video_path, "rb") as f:
            upload_res = requests.post(upload_url, headers=headers, data=f)
        upload_res.raise_for_status()
        
        # Step 3: FINISH (Publish)
        logger.info("Finishing Reel upload (FINISH phase)...")
        publish_res = requests.post(
            url,
            data={
                "upload_phase": "FINISH",
                "video_id": video_id,
                "video_state": "PUBLISHED",
                "description": description,
                "access_token": self.access_token
            }
        )
        publish_res.raise_for_status()
        
        # Format return payload to include the generated post/video ID for logging consistency
        result = publish_res.json()
        if "post_id" in result:
            result["id"] = result["post_id"]
        elif "video_id" in result:
            result["id"] = result["video_id"]
            
        logger.info(f"Facebook Reel published successfully. ID: {result.get('id')}")
        return result