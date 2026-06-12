import os
import json
from datetime import datetime, timezone
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from logs_setup.logger import Logger
logger = Logger(name="YoutubeUploader", log_file="logs/youtube_uploader.log").get_logger()

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
]

# Paths are at project root (one level above this file)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")
CLIENT_SECRET_PATH = os.path.join(BASE_DIR, "client_secret.json")


class YoutubeUploader:

    def __init__(self):
        self.youtube = self._get_youtube_service()

    # ------------------------------------------------------------------ #
    #  Authentication
    # ------------------------------------------------------------------ #

    def _get_youtube_service(self):
        """Authenticate and return an authorised YouTube API client."""
        credentials = None
        logger.info("Authenticating with YouTube API")

        # Load existing token (JSON format, as saved by yt_auth.py)
        if os.path.exists(TOKEN_PATH):
            credentials = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        else:
            logger.warning("No existing token found, starting new authentication flow")

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                logger.info("Refreshing expired credentials")
                credentials.refresh(Request())
                # Persist refreshed token
                with open(TOKEN_PATH, "w") as f:
                    f.write(credentials.to_json())
            else:
                logger.info("Running OAuth flow to obtain new credentials")
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRET_PATH,
                    SCOPES,
                )
                credentials = flow.run_local_server(port=0)
                with open(TOKEN_PATH, "w") as f:
                    f.write(credentials.to_json())

        logger.info("Authentication successful")
        return build("youtube", "v3", credentials=credentials)

    # ------------------------------------------------------------------ #
    #  Internal helper — chunked upload with progress
    # ------------------------------------------------------------------ #

    def _execute_upload(self, request) -> dict:
        """Drive a resumable upload, printing progress, and return the response."""
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"Uploaded {int(status.progress() * 100)}%")
        return response

    # ------------------------------------------------------------------ #
    #  Short upload
    # ------------------------------------------------------------------ #

    def upload_short(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list[str],
        privacy: str = "public",
    ) -> str:
        """Upload a YouTube Short and return its video ID.

        Shorts are vertical videos ≤ 60 s. The #Shorts hashtag is
        automatically appended to the description if not already present.
        """
        logger.info(f"Uploading Short: {video_path}")
        if "#shorts" not in description.lower():

            description = description.rstrip() + "\n\n#Shorts"
            logger.info(f"Appended #Shorts hashtag to description: {description}")


        try:
            request = self.youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": "22",
                },
                "status": {
                    "privacyStatus": privacy,
                    "selfDeclaredMadeForKids": False,
                },
            },
            media_body=MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True,
            ),
            )
            logger.info(f"Created upload request for {video_path}")
        except Exception as e:
            logger.exception(f"Failed to create upload request for {video_path}: {e}")
            raise
        response = self._execute_upload(request)
        video_id = response["id"]
        logger.info(f"Short uploaded ▶  https://youtu.be/{video_id}")
        return video_id

    # ------------------------------------------------------------------ #
    #  Regular / long-form video upload
    # ------------------------------------------------------------------ #

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list[str],
        category_id: str = "22",
        privacy: str = "public",
        made_for_kids: bool = False,
        publish_at: Optional[datetime] = None,
    ) -> str:
        """Upload a regular (long-form) video and return its video ID.

        Args:
            video_path:    Local path to the video file.
            title:         Video title (max 100 chars).
            description:   Video description.
            tags:          List of keyword tags.
            category_id:   YouTube category ID (default "22" = People & Blogs).
            privacy:       "public" | "private" | "unlisted".
            made_for_kids: Mark as made for kids (COPPA).
            publish_at:    If provided (and privacy="private"), schedule the
                           video to go public at this UTC datetime.
        """
        status_body: dict = {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": made_for_kids,
        }

        # Scheduled publishing — YouTube requires RFC 3339 UTC timestamp
        if publish_at is not None:
            if publish_at.tzinfo is None:
                publish_at = publish_at.replace(tzinfo=timezone.utc)
            status_body["privacyStatus"] = "private"
            status_body["publishAt"] = publish_at.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        request = self.youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": category_id,
                },
                "status": status_body,
            },
            media_body=MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True,
            ),
        )

        logger.info(f"Executing upload for {video_path}")
        response = self._execute_upload(request)
        video_id = response["id"]
        logger.info(f"Video uploaded ▶  https://youtu.be/{video_id}")
        return video_id

    # ------------------------------------------------------------------ #
    #  Community Post
    # ------------------------------------------------------------------ #

    def create_community_post(
        self,
        text: str,
        image_path: Optional[str] = None,
        video_id: Optional[str] = None,
    ) -> str:
        """Create a Community (Posts) tab entry and return its post ID.

        You can attach either an image OR a video reference (not both).
        Requires the channel to have Community Posts enabled (500+ subs).

        Args:
            text:       The post body text.
            image_path: Local path to an image to attach (optional).
            video_id:   A YouTube video ID to reference in the post (optional).

        Returns:
            The community post ID.
        """
        body: dict = {
            "snippet": {
                "type": "textPost",
                "textOriginal": text,
            }
        }

        if image_path:
            body["snippet"]["type"] = "imagePost"
            body["snippet"]["imageUrl"] = image_path  # see note below

        if video_id:
            body["snippet"]["type"] = "videoPost"
            body["snippet"]["videoId"] = video_id

        response = self.youtube.communityPosts().insert(
            part="snippet",
            body=body,
        ).execute()
        logger.info("Community post created")

        post_id = response.get("id", "")
        logger.info(f"Community post created: {post_id}")
        return post_id

    # ------------------------------------------------------------------ #
    #  Thumbnail
    # ------------------------------------------------------------------ #

    def upload_thumbnail(self, video_id: str, image_path: str) -> None:
        """Set a custom thumbnail for an already-uploaded video."""
        self.youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(image_path),
        ).execute()
        logger.info("Thumbnail uploaded")


# ------------------------------------------------------------------ #
#  Quick test
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    uploader = YoutubeUploader()

    # --- Upload a Short ---
    short_id = uploader.upload_short(
        video_path="short.mp4",
        title="AI News Today #Shorts",
        description="Daily AI news.\n\n#shorts #ai",
        tags=["AI", "Shorts", "News"],
    )
    uploader.upload_thumbnail(short_id, "thumbnail.jpg")

    # --- Upload a regular video (scheduled) ---
    # from datetime import datetime, timezone
    # scheduled_time = datetime(2025, 1, 20, 14, 0, 0, tzinfo=timezone.utc)
    # vid_id = uploader.upload_video(
    #     video_path="video.mp4",
    #     title="My Full Video",
    #     description="Full video description.",
    #     tags=["AI", "Tech"],
    #     publish_at=scheduled_time,
    # )

    # --- Community post ---
    # uploader.create_community_post(
    #     text="New video dropping soon! 🚀",
    #     video_id=short_id,
    # )