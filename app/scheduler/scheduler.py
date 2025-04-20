import os
import time
import schedule
import requests
import logging
import json
from datetime import datetime
import pandas as pd
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
API_URL = os.environ.get("API_URL", "http://api:8000")
DATA_DIR = os.environ.get("DATA_DIR", "/data")

# Ensure data directories exist
os.makedirs(f"{DATA_DIR}/news", exist_ok=True)
os.makedirs(f"{DATA_DIR}/papers", exist_ok=True)
os.makedirs(f"{DATA_DIR}/stocks", exist_ok=True)

def fetch_ai_news():
    """Fetch AI news from the API and store the results"""
    logger.info("Running scheduled task: Fetch AI news")
    try:
        # Call the API to trigger news fetching
        response = requests.post(f"{API_URL}/tasks/fetch-news")
        response.raise_for_status()
        
        logger.info(f"News fetching API call successful: {response.status_code}")
        
        # In a real implementation, we might do more post-processing here
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"{DATA_DIR}/news/fetch_log_{timestamp}.json", "w") as f:
            json.dump({"timestamp": timestamp, "status": "completed"}, f)
            
    except Exception as e:
        logger.error(f"Error fetching AI news: {str(e)}")

def fetch_research_papers():
    """Fetch research papers and store the results"""
    logger.info("Running scheduled task: Fetch research papers")
    try:
        # Call the API to trigger paper fetching
        response = requests.post(f"{API_URL}/tasks/fetch-papers")
        response.raise_for_status()
        
        logger.info(f"Research papers fetching API call successful: {response.status_code}")
        
        # In a real implementation, we might do more post-processing here
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"{DATA_DIR}/papers/fetch_log_{timestamp}.json", "w") as f:
            json.dump({"timestamp": timestamp, "status": "completed"}, f)
            
    except Exception as e:
        logger.error(f"Error fetching research papers: {str(e)}")

def fetch_stock_data():
    """Fetch stock data for AI companies and indices"""
    logger.info("Running scheduled task: Fetch stock data")
    try:
        # In a real implementation, this would use yfinance or another API
        # For now, just log that it ran
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"{DATA_DIR}/stocks/fetch_log_{timestamp}.json", "w") as f:
            json.dump({"timestamp": timestamp, "status": "completed"}, f)
            
        logger.info("Stock data fetching completed")
    except Exception as e:
        logger.error(f"Error fetching stock data: {str(e)}")

def main():
    """Main function to set up and run the scheduler"""
    logger.info("Starting scheduler")
    
    # Schedule daily news fetching at 3:00 AM
    schedule.every().day.at("03:00").do(fetch_ai_news)
    
    # Schedule weekly research papers fetching on Friday at 8:00 PM
    schedule.every().friday.at("20:00").do(fetch_research_papers)
    
    # Schedule stock data fetching every 6 hours
    schedule.every(6).hours.do(fetch_stock_data)
    
    # Run the tasks once at startup for testing
    logger.info("Running tasks at startup")
    fetch_ai_news()
    fetch_research_papers()
    fetch_stock_data()
    
    # Keep the scheduler running
    logger.info("Scheduler running, waiting for scheduled tasks...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()