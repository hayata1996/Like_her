import os
import logging
import random
import time
import json
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import aiplatform
from pydantic import BaseModel
import yfinance as yf
from vertexai.preview.agent import AgentBuilder

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if we're running in local development mode
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")
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

# AI Platform configuration
PROJECT_ID = os.environ.get("PROJECT_ID")
LOCATION = os.environ.get("LOCATION", "us-central1")
AGENT_ID = os.environ.get("AGENT_ID")

# Initialize AI Platform
try:
    aiplatform.init(project=PROJECT_ID, location=LOCATION)
    logger.info(f"Successfully initialized AI Platform with project {PROJECT_ID}")
except Exception as e:
    logger.error(f"Error initializing AI Platform: {str(e)}")
    raise

# Ensure data directories exist
os.makedirs(f"{DATA_DIR}/news", exist_ok=True)
os.makedirs(f"{DATA_DIR}/health", exist_ok=True)
os.makedirs(f"{DATA_DIR}/stocks", exist_ok=True)
os.makedirs(MODEL_PATH, exist_ok=True)

# API Models
class ChatMessage(BaseModel):
    message: str
    user_id: str = "default_user"
    history: Optional[List[dict]] = []

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

# AI interaction function - always use Vertex AI Agent Builder
def get_llm_response(message: str, history: List[dict], user_id: str) -> str:
    """Get response from AI model"""
    # build and run Vertex AI Agent
    agent = AgentBuilder()\
        .set_agent_id(AGENT_ID)\
        .set_chat_model("chat-bison@001")\
        .build()
    # prepare history messages
    msgs = []
    for item in history or []:
        msgs.append({"author": item.get("role"), "content": item.get("content")})
    msgs.append({"author": "user", "content": message})
    result = agent.run(msgs)
    return result.content

# API Routes
@app.get("/")
def read_root():
    env_info = "local development" if ENVIRONMENT == "local" else "production"
    return {
        "message": f"Welcome to the Like Her API - Running in {env_info} mode with AI Platform integration",
        "status": "operational"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    try:
        logger.info(f"Received message from {message.user_id}: {message.message}")
        
        # Get response from LLM with history
        response = get_llm_response(message.message, message.history, message.user_id)
        
        # Log the response
        logger.info(f"Response for {message.user_id}: {response}")
        
        return ChatResponse(
            response=response,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream_endpoint(message: ChatMessage):
    """Stream AI response as Server-Sent Events (SSE)"""
    from fastapi.responses import StreamingResponse
    import time

    async def event_generator():
        # Get full response synchronously
        response_text = get_llm_response(message.message, message.history, message.user_id)
        # Stream character by character
        for char in response_text:
            yield f"data: {char}\n\n"
            time.sleep(0.01)
        # Signal end of stream
        yield 'data: [DONE]\n\n'

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/news", response_model=List[NewsItem])
async def get_news():
    try:
        news_dir = f"{DATA_DIR}/news"
        files = sorted([f for f in os.listdir(news_dir) if f.endswith('.json')])
        news_items = []
        for file in files:
            with open(os.path.join(news_dir, file)) as fp:
                data = json.load(fp)
                news_items.extend(data if isinstance(data, list) else [data])
        return news_items
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", response_model=HealthData)
async def get_health_data(user_id: str = "default_user"):
    try:
        health_dir = f"{DATA_DIR}/health"
        files = sorted([f for f in os.listdir(health_dir) if f.endswith('.json')])
        if not files:
            raise HTTPException(status_code=404, detail="No health data found")
        latest_file = files[-1]
        with open(os.path.join(health_dir, latest_file)) as fp:
            data = json.load(fp)
        return HealthData(**data)
    except Exception as e:
        logger.error(f"Error fetching health data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks")
async def get_stock_data(symbol: str = "7974.T", period: str = "1mo"):
    # Fetch and process stock data
    logger.info(f"Fetching stock data for symbol: {symbol} with period: {period}")
    try:
        # Use yfinance to get real stock data
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        logger.info(f"Fetched stock data for {symbol}: {hist.head()}")

        # Reset index to make date a column
        hist.reset_index(inplace=True)

        # Convert datetime to string for JSON serialization
        hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')

        # # Add moving averages
        # hist['MA5'] = hist['Close'].rolling(window=5).mean()
        # hist['MA20'] = hist['Close'].rolling(window=20).mean()

        # # Replace inf/-inf with 0 and fill NaNs with 0 for JSON compliance
        # hist = hist.replace([float('inf'), float('-inf')], 0).fillna(0)

        # Get company name
        info = stock.info
        company_name = info.get('shortName', symbol)

        # Convert to dict for JSON response
        data = {
            "Date": hist['Date'].tolist(),
            "Open": hist['Open'].tolist(),
            "High": hist['High'].tolist(),
            "Low": hist['Low'].tolist(),
            "Close": hist['Close'].tolist(),
            "Volume": hist['Volume'].tolist(),
            # "MA5": hist['MA5'].tolist(),
            # "MA20": hist['MA20'].tolist(),
            "Symbol": symbol,
            "Name": company_name
        }
        logger.info(f"Fetched stock data for {symbol}: {data}")
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
    import sys
    
    # More detailed logging for startup
    logger.info("Starting API service")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Environment: {ENVIRONMENT}")
    
    # Get the port from environment variable
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Port configuration: Using port {port} (from environment: {os.environ.get('PORT')})")
    
    try:
        logger.info(f"Starting server on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        # Print to stderr as well for Cloud Run logs
        print(f"ERROR: Failed to start server: {str(e)}", file=sys.stderr)
        raise