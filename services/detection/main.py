"""Detection service entrypoint — consumes frames, runs YOLO, publishes results."""

from app.services.detection_service import run

if __name__ == "__main__":
    run()
