"""Frame reader entrypoint — publishes JPEG frames to RabbitMQ."""

from app.services.reader_service import run

if __name__ == "__main__":
    run()
