"""
database.py
-----------
Central database operations class for the automated-posts pipeline.

Env variables that control behaviour
-------------------------------------
USE_DATABASE=TRUE      → connect to PostgreSQL via DATABASE_URL
USE_DATABASE=FALSE     → no-database mode (all DB methods are no-ops / return None)
USE_CLOUD_SAVE=True    → upload files to GCP bucket after generation
USE_CLOUD_SAVE=False   → skip GCP upload
"""

import os
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from logs_setup.logger import Logger

load_dotenv()

logger = Logger(
    name="DatabaseOperations",
    log_file="logs/database.log",
).get_logger()

# ------------------------------------------------------------------ #
#  Feature flags from .env
# ------------------------------------------------------------------ #

USE_DATABASE: bool = os.getenv("USE_DATABASE", "FALSE").strip().upper() == "TRUE"
USE_CLOUD_SAVE: bool = os.getenv("USE_CLOUD_SAVE", "FALSE").strip().upper() == "TRUE"

# ------------------------------------------------------------------ #
#  SQLAlchemy setup (only when DB is enabled)
# ------------------------------------------------------------------ #

engine = None
SessionLocal = None

if USE_DATABASE:
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("USE_DATABASE=TRUE but DATABASE_URL is not set in .env")

    engine = create_engine(DATABASE_URL)

    # Import here so the models are only required when DB is actually used
    from schemas_n_db.schema import (
        Base,
        videos_on_demand,
        images_on_demand,
        Video_God,
        Images_God,
    )

    Base.metadata.create_all(engine)
    
    # Run auto-migrations to add Facebook columns if they do not exist
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            # Check and add fb_posted to images_god
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='images_god' AND column_name='fb_posted'"))
            if not res.fetchone():
                conn.execute(text("ALTER TABLE images_god ADD COLUMN fb_posted BOOLEAN DEFAULT FALSE"))
                conn.commit()
                logger.info("Auto-migration: Added fb_posted column to images_god table.")

            # Check and add fb_posted to videos_god
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='videos_god' AND column_name='fb_posted'"))
            if not res.fetchone():
                conn.execute(text("ALTER TABLE videos_god ADD COLUMN fb_posted BOOLEAN DEFAULT FALSE"))
                conn.commit()
                logger.info("Auto-migration: Added fb_posted column to videos_god table.")

            # Check and add fb_post to videos_on_demand
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='videos_on_demand' AND column_name='fb_post'"))
            if not res.fetchone():
                conn.execute(text("ALTER TABLE videos_on_demand ADD COLUMN fb_post BOOLEAN DEFAULT FALSE"))
                conn.commit()
                logger.info("Auto-migration: Added fb_post column to videos_on_demand table.")

            # Check and add fb_post to images_on_demand
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='images_on_demand' AND column_name='fb_post'"))
            if not res.fetchone():
                conn.execute(text("ALTER TABLE images_on_demand ADD COLUMN fb_post BOOLEAN DEFAULT FALSE"))
                conn.commit()
                logger.info("Auto-migration: Added fb_post column to images_on_demand table.")
    except Exception as migration_err:
        logger.error(f"Auto-migration failed (could be sqlite/non-postgres or permission issue): {migration_err}")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database connected and tables ensured.")
else:
    logger.warning(
        "USE_DATABASE=FALSE — running in no-database mode. "
        "All DB operations will be skipped."
    )


# ------------------------------------------------------------------ #
#  GCP uploader (lazy-initialised, only when USE_CLOUD_SAVE=TRUE)
# ------------------------------------------------------------------ #

def _get_gcp_uploader():
    """Return a GCPBucketUpload instance, or None if cloud save is disabled."""
    if not USE_CLOUD_SAVE:
        return None
    try:
        from gcp_upload.gcp_bucket_upload import GCPBucketUpload
        return GCPBucketUpload()
    except Exception as exc:
        logger.error(f"Could not initialise GCP uploader: {exc}")
        return None


# ================================================================== #
#  DatabaseOperations
# ================================================================== #

class DatabaseOperations:
    """
    Single entry-point for all DB and optional GCP operations.

    All public methods are safe to call even when USE_DATABASE=FALSE —
    they log a warning and return None instead of raising.
    """

    def __init__(self):
        self._db_enabled = USE_DATABASE
        self._cloud_enabled = USE_CLOUD_SAVE
        self._gcp: object | None = None  # lazy

        if self._cloud_enabled:
            self._gcp = _get_gcp_uploader()
            if self._gcp:
                logger.info("GCP uploader ready.")
            else:
                logger.warning("USE_CLOUD_SAVE=TRUE but GCP uploader failed to init.")

    # -------------------------------------------------------------- #
    #  Internal helpers
    # -------------------------------------------------------------- #

    def _get_session(self) -> Optional[Session]:
        if not self._db_enabled or SessionLocal is None:
            return None
        return SessionLocal()

    def _no_db_warning(self, method: str):
        logger.warning(f"[NO-DB] {method} called but USE_DATABASE=FALSE — skipping.")

    # -------------------------------------------------------------- #
    #  videos_on_demand
    # -------------------------------------------------------------- #

    def get_pending_videos(self) -> list:
        """
        Return all videos_on_demand rows where generated=False.
        These are the prompts queued for video generation.
        """
        if not self._db_enabled:
            self._no_db_warning("get_pending_videos")
            return []

        session = self._get_session()
        try:
            rows = (
                session.query(videos_on_demand)
                .filter(videos_on_demand.generated == False)
                .all()
            )
            logger.info(f"Found {len(rows)} pending video(s) to generate.")
            return rows
        except Exception as exc:
            logger.exception(f"get_pending_videos failed: {exc}")
            return []
        finally:
            session.close()

    def get_videos_pending_yt_post(self) -> list:
        """Return videos that are generated but not yet posted to YouTube."""
        if not self._db_enabled:
            self._no_db_warning("get_videos_pending_yt_post")
            return []

        session = self._get_session()
        try:
            rows = (
                session.query(videos_on_demand)
                .filter(
                    videos_on_demand.generated == True,
                    videos_on_demand.yt_post == False,
                )
                .all()
            )
            logger.info(f"Found {len(rows)} video(s) pending YT post.")
            return rows
        except Exception as exc:
            logger.exception(f"get_videos_pending_yt_post failed: {exc}")
            return []
        finally:
            session.close()

    def get_videos_pending_insta_post(self) -> list:
        """Return videos that are generated but not yet posted to Instagram."""
        if not self._db_enabled:
            self._no_db_warning("get_videos_pending_insta_post")
            return []

        session = self._get_session()
        try:
            rows = (
                session.query(videos_on_demand)
                .filter(
                    videos_on_demand.generated == True,
                    videos_on_demand.insta_post == False,
                )
                .all()
            )
            logger.info(f"Found {len(rows)} video(s) pending Insta post.")
            return rows
        except Exception as exc:
            logger.exception(f"get_videos_pending_insta_post failed: {exc}")
            return []
        finally:
            session.close()

    def mark_video_generated(self, video_id: int) -> bool:
        """Set generated=True for a videos_on_demand row."""
        if not self._db_enabled:
            self._no_db_warning("mark_video_generated")
            return False

        session = self._get_session()
        try:
            row = session.get(videos_on_demand, video_id)
            if row is None:
                logger.warning(f"videos_on_demand id={video_id} not found.")
                return False
            row.generated = True
            session.commit()
            logger.info(f"videos_on_demand id={video_id} marked as generated.")
            return True
        except Exception as exc:
            session.rollback()
            logger.exception(f"mark_video_generated failed: {exc}")
            return False
        finally:
            session.close()

    def mark_video_yt_posted(self, video_id: int) -> bool:
        """Set yt_post=True for a videos_on_demand row."""
        if not self._db_enabled:
            self._no_db_warning("mark_video_yt_posted")
            return False

        session = self._get_session()
        try:
            row = session.get(videos_on_demand, video_id)
            if row is None:
                logger.warning(f"videos_on_demand id={video_id} not found.")
                return False
            row.yt_post = True
            session.commit()
            logger.info(f"videos_on_demand id={video_id} marked as yt_post=True.")
            return True
        except Exception as exc:
            session.rollback()
            logger.exception(f"mark_video_yt_posted failed: {exc}")
            return False
        finally:
            session.close()

    def mark_video_insta_posted(self, video_id: int) -> bool:
        """Set insta_post=True for a videos_on_demand row."""
        if not self._db_enabled:
            self._no_db_warning("mark_video_insta_posted")
            return False

        session = self._get_session()
        try:
            row = session.get(videos_on_demand, video_id)
            if row is None:
                logger.warning(f"videos_on_demand id={video_id} not found.")
                return False
            row.insta_post = True
            session.commit()
            logger.info(f"videos_on_demand id={video_id} marked as insta_post=True.")
            return True
        except Exception as exc:
            session.rollback()
            logger.exception(f"mark_video_insta_posted failed: {exc}")
            return False
        finally:
            session.close()

    def mark_video_fb_posted(self, video_id: int) -> bool:
        """Set fb_post=True for a videos_on_demand row."""
        if not self._db_enabled:
            self._no_db_warning("mark_video_fb_posted")
            return False

        session = self._get_session()
        try:
            row = session.get(videos_on_demand, video_id)
            if row is None:
                logger.warning(f"videos_on_demand id={video_id} not found.")
                return False
            row.fb_post = True
            session.commit()
            logger.info(f"videos_on_demand id={video_id} marked as fb_post=True.")
            return True
        except Exception as exc:
            session.rollback()
            logger.exception(f"mark_video_fb_posted failed: {exc}")
            return False
        finally:
            session.close()

    # -------------------------------------------------------------- #
    #  images_on_demand
    # -------------------------------------------------------------- #

    def get_pending_images(self) -> list:
        """Return all images_on_demand rows where generated=False."""
        if not self._db_enabled:
            self._no_db_warning("get_pending_images")
            return []

        session = self._get_session()
        try:
            rows = (
                session.query(images_on_demand)
                .filter(images_on_demand.generated == False)
                .all()
            )
            logger.info(f"Found {len(rows)} pending image(s) to generate.")
            return rows
        except Exception as exc:
            logger.exception(f"get_pending_images failed: {exc}")
            return []
        finally:
            session.close()

    def get_images_pending_yt_post(self) -> list:
        """Return images that are generated but not yet posted to YouTube."""
        if not self._db_enabled:
            self._no_db_warning("get_images_pending_yt_post")
            return []

        session = self._get_session()
        try:
            rows = (
                session.query(images_on_demand)
                .filter(
                    images_on_demand.generated == True,
                    images_on_demand.yt_post == False,
                )
                .all()
            )
            logger.info(f"Found {len(rows)} image(s) pending YT post.")
            return rows
        except Exception as exc:
            logger.exception(f"get_images_pending_yt_post failed: {exc}")
            return []
        finally:
            session.close()

    def get_images_pending_insta_post(self) -> list:
        """Return images that are generated but not yet posted to Instagram."""
        if not self._db_enabled:
            self._no_db_warning("get_images_pending_insta_post")
            return []

        session = self._get_session()
        try:
            rows = (
                session.query(images_on_demand)
                .filter(
                    images_on_demand.generated == True,
                    images_on_demand.insta_post == False,
                )
                .all()
            )
            logger.info(f"Found {len(rows)} image(s) pending Insta post.")
            return rows
        except Exception as exc:
            logger.exception(f"get_images_pending_insta_post failed: {exc}")
            return []
        finally:
            session.close()

    def mark_image_generated(self, image_id: int) -> bool:
        """Set generated=True for an images_on_demand row."""
        if not self._db_enabled:
            self._no_db_warning("mark_image_generated")
            return False

        session = self._get_session()
        try:
            row = session.get(images_on_demand, image_id)
            if row is None:
                logger.warning(f"images_on_demand id={image_id} not found.")
                return False
            row.generated = True
            session.commit()
            logger.info(f"images_on_demand id={image_id} marked as generated.")
            return True
        except Exception as exc:
            session.rollback()
            logger.exception(f"mark_image_generated failed: {exc}")
            return False
        finally:
            session.close()

    def mark_image_yt_posted(self, image_id: int) -> bool:
        """Set yt_post=True for an images_on_demand row."""
        if not self._db_enabled:
            self._no_db_warning("mark_image_yt_posted")
            return False

        session = self._get_session()
        try:
            row = session.get(images_on_demand, image_id)
            if row is None:
                logger.warning(f"images_on_demand id={image_id} not found.")
                return False
            row.yt_post = True
            session.commit()
            logger.info(f"images_on_demand id={image_id} marked as yt_post=True.")
            return True
        except Exception as exc:
            session.rollback()
            logger.exception(f"mark_image_yt_posted failed: {exc}")
            return False
        finally:
            session.close()

    def mark_image_insta_posted(self, image_id: int) -> bool:
        """Set insta_post=True for an images_on_demand row."""
        if not self._db_enabled:
            self._no_db_warning("mark_image_insta_posted")
            return False

        session = self._get_session()
        try:
            row = session.get(images_on_demand, image_id)
            if row is None:
                logger.warning(f"images_on_demand id={image_id} not found.")
                return False
            row.insta_post = True
            session.commit()
            logger.info(f"images_on_demand id={image_id} marked as insta_post=True.")
            return True
        except Exception as exc:
            session.rollback()
            logger.exception(f"mark_image_insta_posted failed: {exc}")
            return False
        finally:
            session.close()

    def mark_image_fb_posted(self, image_id: int) -> bool:
        """Set fb_post=True for an images_on_demand row."""
        if not self._db_enabled:
            self._no_db_warning("mark_image_fb_posted")
            return False

        session = self._get_session()
        try:
            row = session.get(images_on_demand, image_id)
            if row is None:
                logger.warning(f"images_on_demand id={image_id} not found.")
                return False
            row.fb_post = True
            session.commit()
            logger.info(f"images_on_demand id={image_id} marked as fb_post=True.")
            return True
        except Exception as exc:
            session.rollback()
            logger.exception(f"mark_image_fb_posted failed: {exc}")
            return False
        finally:
            session.close()

    # -------------------------------------------------------------- #
    #  GCP upload (optional)
    # -------------------------------------------------------------- #

    def upload_to_gcp(
        self,
        local_file_path: str,
        destination_blob_name: str,
        make_public: bool = True,
    ) -> Optional[dict]:
        """
        Upload a file to GCP bucket if USE_CLOUD_SAVE=True.

        Returns the upload result dict on success, or None if cloud
        save is disabled or the upload fails.
        """
        if not self._cloud_enabled:
            logger.info(
                f"[NO-GCP] Skipping cloud upload for '{local_file_path}' "
                "(USE_CLOUD_SAVE=FALSE)."
            )
            return None

        if self._gcp is None:
            logger.error("GCP uploader not available.")
            return None

        try:
            result = self._gcp.upload_file(
                local_file_path,
                destination_blob_name,
                make_public=make_public,
            )
            logger.info(
                f"GCP upload complete: gs://{result['bucket']}/{result['blob_name']}"
            )
            return result
        except Exception as exc:
            logger.exception(f"GCP upload failed for '{local_file_path}': {exc}")
            return None

    # -------------------------------------------------------------- #
    #  Combined: generate → GCP → mark as generated
    # -------------------------------------------------------------- #

    def save_generated_video(
        self,
        db_id: int,
        local_file_path: str,
        blob_name: Optional[str] = None,
    ) -> Optional[str]:
        """
        After generating a video:
          1. Optionally upload to GCP (if USE_CLOUD_SAVE=True).
          2. Mark the videos_on_demand row as generated=True.

        Returns the GCP public URL (or gs:// URL) if uploaded, else None.
        """
        blob = blob_name or f"videos/{os.path.basename(local_file_path)}"
        gcp_result = self.upload_to_gcp(local_file_path, blob)
        self.mark_video_generated(db_id)

        if gcp_result:
            return gcp_result.get("public_url") or gcp_result.get("gs_url")
        return None

    def save_generated_image(
        self,
        db_id: int,
        local_file_path: str,
        blob_name: Optional[str] = None,
    ) -> Optional[str]:
        """
        After generating an image:
          1. Optionally upload to GCP (if USE_CLOUD_SAVE=True).
          2. Mark the images_on_demand row as generated=True.

        Returns the GCP public URL (or gs:// URL) if uploaded, else None.
        """
        blob = blob_name or f"images/{os.path.basename(local_file_path)}"
        gcp_result = self.upload_to_gcp(local_file_path, blob)
        self.mark_image_generated(db_id)

        if gcp_result:
            return gcp_result.get("public_url") or gcp_result.get("gs_url")
        return None


# ------------------------------------------------------------------ #
#  Quick smoke-test
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    db = DatabaseOperations()

    print("=== Pending videos (not yet generated) ===")
    for v in db.get_pending_videos():
        print(f"  id={v.id}  prompt={v.prompt!r}")

    print("\n=== Pending images (not yet generated) ===")
    for i in db.get_pending_images():
        print(f"  id={i.id}  prompt={i.prompt!r}")

    # Test GCP upload path with real test files (no DB row needed)
    print("\n=== GCP upload test ===")
    result = db.upload_to_gcp(
        local_file_path=r"person Output.jpg",
        destination_blob_name="test/person_output.jpg",
        make_public=True,
    )
    print(f"  result: {result}")

    result2 = db.upload_to_gcp(
        local_file_path=r"Recording 2026-06-11 165341.mp4",
        destination_blob_name="test/recording_test.mp4",
        make_public=True,
    )
    print(f"  result: {result2}")