import requests
from typing import Optional


class LinkedInPublisher:
    """
    Upload and publish posts to a LinkedIn Company Page.
    """

    BASE_URL = "https://api.linkedin.com/v2"

    def __init__(
        self,
        access_token: str,
        organization_id: str
    ):
        self.access_token = access_token
        self.organization_id = organization_id

        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

    def create_text_post(self, text: str) -> dict:
        """
        Publish text-only post.
        """

        payload = {
            "author": f"urn:li:organization:{self.organization_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        response = requests.post(
            f"{self.BASE_URL}/ugcPosts",
            headers=self.headers,
            json=payload
        )

        response.raise_for_status()

        return response.json() if response.text else {
            "status": "success"
        }

    def register_image_upload(self) -> dict:
        """
        Register image upload.
        """

        payload = {
            "registerUploadRequest": {
                "recipes": [
                    "urn:li:digitalmediaRecipe:feedshare-image"
                ],
                "owner": f"urn:li:organization:{self.organization_id}",
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }

        response = requests.post(
            "https://api.linkedin.com/v2/assets?action=registerUpload",
            headers=self.headers,
            json=payload
        )

        response.raise_for_status()

        return response.json()

    def upload_image(
        self,
        image_path: str
    ) -> str:

        registration = self.register_image_upload()

        upload_url = registration["value"]["uploadMechanism"][
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
        ]["uploadUrl"]

        asset = registration["value"]["asset"]

        with open(image_path, "rb") as image_file:

            upload_response = requests.put(
                upload_url,
                data=image_file
            )

        upload_response.raise_for_status()

        return asset

    def create_image_post(
        self,
        text: str,
        image_path: str
    ) -> dict:

        asset = self.upload_image(image_path)

        payload = {
            "author": f"urn:li:organization:{self.organization_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "media": asset
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        response = requests.post(
            f"{self.BASE_URL}/ugcPosts",
            headers=self.headers,
            json=payload
        )

        response.raise_for_status()

        return response.json() if response.text else {
            "status": "success"
        }

if __name__ == "__main__":
    import os 
    from dotenv import load_dotenv
    load_dotenv()
    linkedin_publisher = LinkedInPublisher(access_token=os.environ.get("LINKEDIN_CLIENT_SECRET"), organization_id=os.environ.get("LINKEDIN_CLIENT_ID"))
    linkedin_publisher.create_image_post(text="Test Post", image_path="person Output.jpg")