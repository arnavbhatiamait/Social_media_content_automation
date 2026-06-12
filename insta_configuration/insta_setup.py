import requests
import time
import os
from logs_setup.logger import Logger

logger=Logger("insta_setup",log_file="logs/insta_setup.log").get_logger()

ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
IG_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")

BASE_URL = "https://graph.facebook.com/v23.0"
class InstaSetup:
    def __init__(self):
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.ig_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
        self.base_url = "https://graph.facebook.com/v23.0"
        self.reels_publish_url = f"{self.base_url}/{self.ig_account_id}/media_publish"
        self.post_publish_url = f"{self.base_url}/{self.ig_account_id}/media_publish"

    
    def make_api_request(self, endpoint, params=None, method="GET"):
        url = f"{self.base_url}{endpoint}"
        logger.info(f"Making API request to {url}")

    # ! image 
    def publish_image(self, image_url: str, caption: str):
        create_url = f"{self.base_url}/{self.ig_account_id}/media"

        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token
        }

        container = requests.post(create_url, data=payload).json()

        creation_id = container["id"]

        try:
            result = requests.post(
            self.post_publish_url,
            data={
                "creation_id": creation_id,
                "access_token": self.access_token
            }
            )
            logger.info(f"Image published successfully")
        except Exception as e:
            logger.error(f"Image published failed {e}")

        return result.json()

    # ! reels ---------------------------------------------------------

    def publish_reel(self, video_url: str, caption: str):
        logger.info("Reel is being published")
        create_url = f"{self.base_url}/{self.ig_account_id}/media"
        payload = {
            "media_type": "REELS",
            "video_url": video_url, 
            "caption": caption,
            "share_to_feed": "true",
            "access_token": self.access_token
        }
        container = requests.post(create_url, data=payload).json()
        container_id = container["id"]
        status_url = (
            f"{self.base_url}/{container_id}"
            f"?fields=status_code&access_token={self.access_token}"        )

        while True:
            status = requests.get(status_url).json()
            if status["status_code"] == "FINISHED":
                break
            if status["status_code"] == "ERROR":
                raise Exception("Reel processing failed")
            time.sleep(10)
        try:
            result = requests.post(
            self.reels_publish_url,
            data={
                "creation_id": container_id,
                "access_token": self.access_token
            }
            )
            logger.info("Reel published successfully")
        except Exception as e:
            logger.error(f"Reel published failed {e}")

        return result.json()
    # ! story ---------------------------------------------------------
    def publish_story_image(self, image_url: str):
        logger.info("Story is being published")
        create_url = f"{self.base_url}/{self.ig_account_id}/media"
        payload = {
            "media_type": "STORIES",
            "image_url": image_url,
            "access_token": self.access_token
        }
        container = requests.post(create_url, data=payload).json()
        creation_id = container["id"]
        try:
            result = requests.post(
            self.post_publish_url,
            data={
                "creation_id": creation_id,
                "access_token": self.access_token
            }
            )
            logger.info("Story published successfully")
        except Exception as e:
            logger.error(f"Story published failed {e}")

        return result.json()
    
    def publish_story_video(self, video_url: str):
        logger.info("Story is being published")
        create_url = f"{self.base_url}/{self.ig_account_id}/media"
        payload = {
            "media_type": "STORIES",
            "video_url": video_url,
            "access_token": self.access_token
        }
        container = requests.post(create_url, data=payload).json()
        creation_id = container["id"]
        try:
            result = requests.post(
            self.post_publish_url,
            data={
                "creation_id": creation_id,
                "access_token": self.access_token
            }
            )
            logger.info("Story published successfully")
        except Exception as e:
            logger.error(f"Story published failed {e}")

        return result.json()

    