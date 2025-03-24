import sys
import os
import logging


# Ensure Python finds 'backend' as a module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from backend.routes.EtlUpload import celery_app

# Suppress Celery warning logs
logging.getLogger("celery").setLevel(logging.ERROR)

if __name__ == "__main__":
    print("Starting Celery worker...")
    celery_app.worker_main(["worker", "--loglevel=ERROR"])  # Use ERROR to hide warnings

