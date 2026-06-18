import os
import requests
from typing import List
from dotenv import load_dotenv
load_dotenv()

from pathlib import Path 
from sys import path 
path.append(str(Path(__file__).resolve().parent.parent))  

from logs_setup.logger import setup_logger
logger = setup_logger("FacebookPublisher")



class FacebookPublisher:

    GRAPH_URL = "https://graph.facebook.com/v23.0"

    def __init__(self, page_id: str, access_token: str):
        self.page_id = page_id
        self.access_token = access_token

    def _make_url(self, endpoint: str):
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

        response = requests.post(url, data=payload)
        response.raise_for_status()

        return response.json()

    ##################################################################
    # IMAGE POST
    ##################################################################

    def post_image(self, image_path: str, caption: str = ""):

        url = self._make_url(f"{self.page_id}/photos")

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

        for image_path in image_paths:

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

            response.raise_for_status()

            media_ids.append(
                response.json()["id"]
            )

        attached_media = []

        for media_id in media_ids:
            attached_media.append(
                {"media_fbid": media_id}
            )

        post_url = self._make_url(
            f"{self.page_id}/feed"
        )

        payload = {
            "message": caption,
            "access_token": self.access_token
        }

        for idx, media in enumerate(attached_media):
            payload[f"attached_media[{idx}]"] = str(media)

        response = requests.post(
            post_url,
            data=payload
        )

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

        url = self._make_url(
            f"{self.page_id}/videos"
        )

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

        url = self._make_url(
            f"{self.page_id}/video_reels"
        )

        with open(video_path, "rb") as video:

            files = {
                "source": video
            }

            data = {
                "description": description,
                "access_token": self.access_token
            }

            response = requests.post(
                url,
                files=files,
                data=data
            )

        response.raise_for_status()

        return response.json()