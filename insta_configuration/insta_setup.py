import requests
import time
import os
try:
    from logs_setup.logger import Logger
except ImportError:
    from sys import path
    from pathlib import Path
    path.append(str(Path(__file__).parent.parent))
    from logs_setup.logger import Logger
logger=Logger("insta_setup",log_file="logs/insta_setup.log").get_logger()

from dotenv import load_dotenv
load_dotenv()
ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
IG_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
print(os.getenv("INSTAGRAM_ACCOUNT_ID"))
print(os.getenv("INSTAGRAM_ACCESS_TOKEN"))
BASE_URL = "https://graph.facebook.com/v25.0"
class InstaSetup:
    def __init__(self):
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.ig_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
        self.base_url = "https://graph.facebook.com/v25.0"
        self.reels_publish_url = f"{self.base_url}/{self.ig_account_id}/media_publish"
        self.post_publish_url = f"{self.base_url}/{self.ig_account_id}/media_publish"

    
    def make_api_request(self, endpoint, params=None, method="GET"):
        url = f"{self.base_url}{endpoint}"
        logger.info(f"Making API request to {url}")
        try:
            if method == "GET":
                response = requests.get(url, params=params)
            else:
                response = requests.post(url, data=params)
            response.raise_for_status()
            logger.info(f"API request successful: {response.status_code}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    # ! image 
    def publish_image(self, image_url: str, caption: str):
        create_url = f"{self.base_url}/{self.ig_account_id}/media"

        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token
        }

        container = requests.post(create_url, data=payload).json()
        logger.info(f"Instagram image container response: {container}")

        if "id" not in container:
            error = container.get("error", container)
            raise RuntimeError(f"Instagram API error: {error}")

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
        logger.info(f"Instagram reel container response: {container}")

        if "id" not in container:
            error = container.get("error", container)
            raise RuntimeError(f"Instagram API error: {error}")

        container_id = container["id"]
        status_url = (
            f"{self.base_url}/{container_id}"
            f"?fields=status_code,status&access_token={self.access_token}"        )

        while True:
            status = requests.get(status_url).json()
            if status["status_code"] == "FINISHED":
                break
            if status["status_code"] == "ERROR":
                logger.error(f"Reel processing failed: {status}")
                raise Exception(f"Reel processing failed: {status}")
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

    # ! Carousel
    def create_carousel_item(self, image_url: str):
        logger.info("Carousel item is being created")
        payload = {
            "image_url": image_url,
            "is_carousel_item": True,
            "access_token": self.access_token
        }
        try:
            request = requests.post(
            f"{self.base_url}/{self.ig_account_id}/media",
            data=payload
        )
            logger.info("Carousel item created successfully")
            return request.json()["id"]
        except Exception as e:
            logger.error(f"Carousel item creation failed {e}")
            return None
    

    def publish_carousel(self, images, caption):
        children = [self.create_carousel_item(i) for i in images]

        payload = {
            "media_type": "CAROUSEL",
            "children": ",".join(children),
            "caption": caption,
            "access_token": self.access_token
        }
        try:
            container = requests.post(
                f"{self.base_url}/{self.ig_account_id}/media",
                data=payload
            ).json()
            logger.info("Carousel container created")
        except Exception as e:
            logger.error(f"Carousel container creation failed {e}")
        try:
            requests.post(
            f"{self.base_url}/{self.ig_account_id}/media_publish",
            data={
                "creation_id": container["id"],
                "access_token": self.access_token
            }
            )
            logger.info("Carousel published successfully")
        except Exception as e:
            logger.error(f"Carousel published failed {e}")

if __name__=="__main__":
    insta_setup = InstaSetup()
    # result = insta_setup.publish_image("https://example.com/image.jpg", "Caption for the image")
    # result = insta_setup.publish_reel("https://example.com/video.mp4", "Caption for the reel")
    # result = insta_setup.publish_story_image("https://example.com/story_image.jpg")
    # result = insta_setup.publish_story_video("https://example.com/story_video.mp4")
    result = insta_setup.publish_image("person Output.jpg", "Caption for the image")
    print(result)
    # insta_setup.make_api_request("/me", params={"fields": "id,name"})