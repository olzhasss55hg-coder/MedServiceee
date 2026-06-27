from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
import os

def run_parsers_and_index():
    print("Running scheduled parsers...")
    try:
        # We run them via subprocess so they execute in their own isolated environment and don't block the async loop
        import sys
        
        # Run MCK parser (our working fallback for MVP)
        mck_path = os.path.join(os.path.dirname(__file__), "parser", "mck_parser.py")
        subprocess.run([sys.executable, mck_path], check=False)
        
        # Run KDL parser
        kdl_path = os.path.join(os.path.dirname(__file__), "parser", "kdl_parser.py")
        subprocess.run([sys.executable, kdl_path], check=False)
        
        # Index data into MeiliSearch after parsing
        search_path = os.path.join(os.path.dirname(__file__), "search.py")
        subprocess.run([sys.executable, search_path], check=False)
        
        print("Scheduled parsers and indexing completed successfully.")
    except Exception as e:
        print(f"Error during scheduled parsing: {e}")

scheduler = BackgroundScheduler()

def start_scheduler():
    # Schedule to run every day at 3:00 AM
    scheduler.add_job(run_parsers_and_index, 'cron', hour=3, minute=0)
    scheduler.start()
    print("APScheduler started: Parsers will run daily at 03:00.")

def stop_scheduler():
    scheduler.shutdown()
    print("APScheduler stopped.")
