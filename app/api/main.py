from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import requests
from typing import List, Dict, Any, Optional
import random
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Like Her API", description="API for the 'Like Her' AI Assistant")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Base directory for data storage
DATA_DIR = os.environ.get("DATA_DIR", "/data")
MODEL_PATH = os.environ.get("MODEL_PATH", "/data/models")

# Ensure data directories exist
os.makedirs(f"{DATA_DIR}/news", exist_ok=True)
os.makedirs(f"{DATA_DIR}/health", exist_ok=True)
os.makedirs(f"{DATA_DIR}/stocks", exist_ok=True)
os.makedirs(MODEL_PATH, exist_ok=True)

# API Models
class ChatMessage(BaseModel):
    message: str
    user_id: str = "default_user"

class ChatResponse(BaseModel):
    response: str
    timestamp: str

class NewsItem(BaseModel):
    title: str
    summary: str
    source: str
    url: Optional[str] = None
    date: str

class HealthData(BaseModel):
    steps: int
    sleep_hours: float
    heart_rate: int
    last_sync: str

# Mock LLM response function
# In production, this would use the Swallow1.5 model
def get_llm_response(message: str, user_id: str) -> str:
    # This is a mock function - in production this would call your LLM
    responses = [
        f"I understand you're saying '{message}'. How can I help you further?",
        f"That's interesting about '{message}'. Let me think about that.",
        f"I see you mentioned '{message}'. Would you like to know more about this topic?",
        f"Regarding '{message}', I have some thoughts that might help you.",
        f"I've processed your message about '{message}'. Here's what I think..."
    ]
    
    # Simulate processing time
    time.sleep(1)
    
    current_time = datetime.now().strftime("%H:%M:%S")
    return f"[{current_time}] {random.choice(responses)}"

# API Routes
@app.get("/")
def read_root():
    return {"message": "Welcome to the Like Her API", "status": "operational"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    try:
        logger.info(f"Received message from {message.user_id}: {message.message}")
        
        # Get response from LLM
        response = get_llm_response(message.message, message.user_id)
        
        # Log the response
        logger.info(f"Response for {message.user_id}: {response}")
        
        return ChatResponse(
            response=response,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news", response_model=List[NewsItem])
async def get_news():
    try:
        # In production, this would fetch from a real news API
        # For now, return mock data
        news = [
            NewsItem(
                title="Google DeepMind Announces New AI Architecture",
                summary="A breakthrough in AI architecture that improves efficiency by 40%.",
                source="TechCrunch",
                url="https://techcrunch.com/example",
                date="2025-04-20"
            ),
            NewsItem(
                title="Sakana AI Releases Expanded Version of Swallow Model",
                summary="Japanese AI startup Sakana AI has released Swallow 2.0 with improved language capabilities.",
                source="AI News Daily",
                url="https://ainewsdaily.com/example",
                date="2025-04-19"
            ),
            NewsItem(
                title="AI Regulation Framework Proposed in EU",
                summary="New regulations aim to ensure ethical AI development across European markets.",
                source="Reuters",
                url="https://reuters.com/example",
                date="2025-04-18"
            ),
            NewsItem(
                title="OpenAI's New Model Shows Enhanced Reasoning",
                summary="Latest model demonstrates significant improvements in mathematical and logical reasoning tasks.",
                source="MIT Technology Review",
                url="https://technologyreview.mit.edu/example",
                date="2025-04-17"
            )
        ]
        return news
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", response_model=HealthData)
async def get_health_data(user_id: str = "default_user"):
    try:
        # In production, this would fetch from Huawei Health API
        # For now, return mock data
        return HealthData(
            steps=random.randint(3000, 10000),
            sleep_hours=round(random.uniform(5.0, 9.0), 1),
            heart_rate=random.randint(60, 80),
            last_sync=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    except Exception as e:
        logger.error(f"Error fetching health data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks")
async def get_stock_data():
    try:
        # In production, this would fetch real stock data
        # For now, generate random data
        
        # Create date range for the past 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        date_range = pd.date_range(start=start_date, end=end_date)
        
        # Generate random stock data
        values = np.cumsum(np.random.normal(0, 1, len(date_range))) + 100
        
        # Convert to dict for JSON response
        data = {
            "dates": [d.strftime('%Y-%m-%d') for d in date_range],
            "values": values.tolist(),
            "symbol": "AI_INDEX",
            "name": "AI Industry Index"
        }
        
        return data
    except Exception as e:
        logger.error(f"Error fetching stock data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks/fetch-news")
async def fetch_news_task(background_tasks: BackgroundTasks):
    """Endpoint to trigger news fetching, designed to be called by Cloud Scheduler"""
    background_tasks.add_task(fetch_news_background)
    return {"status": "News fetch task scheduled"}

@app.post("/tasks/fetch-papers")
async def fetch_papers_task(background_tasks: BackgroundTasks):
    """Endpoint to trigger research papers fetching, designed to be called by Cloud Scheduler"""
    background_tasks.add_task(fetch_papers_background)
    return {"status": "Research papers fetch task scheduled"}

# Background tasks
def fetch_news_background():
    """Task to fetch and store latest AI news"""
    logger.info("Fetching AI news in background")
    # In production, this would use a real news API
    # For now, just log that it ran
    logger.info("News fetch completed")

def fetch_papers_background():
    """Task to fetch and store latest research papers"""
    logger.info("Fetching research papers in background")
    # In production, this would use an academic paper API
    # For now, just log that it ran
    logger.info("Research papers fetch completed")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)