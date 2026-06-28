"""Scheduled background tasks for automated data collection and indexing."""

from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
import os
import sys
from logger import scheduler_logger


def run_parsers_and_index() -> None:
    """
    Execute all configured parsers and re-index search data.
    Runs each parser as an isolated subprocess so failures don't cascade.
    """
    scheduler_logger.info("Starting scheduled parser run...")
    try:
        # Run KDL parser
        kdl_path = os.path.join(os.path.dirname(__file__), "parser", "kdl_parser.py")
        result = subprocess.run([sys.executable, kdl_path], check=False, capture_output=True, text=True)
        if result.returncode == 0:
            scheduler_logger.info("KDL parser completed successfully.")
        else:
            scheduler_logger.warning("KDL parser exited with code %d: %s", result.returncode, result.stderr[:200])

        # Run Olymp parser
        olymp_path = os.path.join(os.path.dirname(__file__), "parser", "olymp_parser.py")
        result = subprocess.run([sys.executable, olymp_path], check=False, capture_output=True, text=True)
        if result.returncode == 0:
            scheduler_logger.info("Olymp parser completed successfully.")
        else:
            scheduler_logger.warning("Olymp parser exited with code %d: %s", result.returncode, result.stderr[:200])

        # Re-index MeiliSearch after parsing
        search_path = os.path.join(os.path.dirname(__file__), "search.py")
        result = subprocess.run([sys.executable, search_path], check=False, capture_output=True, text=True)
        if result.returncode == 0:
            scheduler_logger.info("MeiliSearch re-indexing completed.")
        else:
            scheduler_logger.warning("MeiliSearch indexing exited with code %d: %s", result.returncode, result.stderr[:200])

        scheduler_logger.info("All scheduled tasks finished.")
    except Exception as e:
        scheduler_logger.error("Critical error during scheduled parsing: %s", e, exc_info=True)


scheduler = BackgroundScheduler()


def start_scheduler() -> None:
    """Start the APScheduler background scheduler (daily at 03:00)."""
    scheduler.add_job(run_parsers_and_index, 'cron', hour=3, minute=0)
    scheduler.start()
    scheduler_logger.info("APScheduler started: Parsers will run daily at 03:00.")


def stop_scheduler() -> None:
    """Gracefully shut down the APScheduler."""
    scheduler.shutdown()
    scheduler_logger.info("APScheduler stopped.")
