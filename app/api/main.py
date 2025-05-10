import os
import logging
import random
import time
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yfinance as yf

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if we're running in local development mode
USE_MOCK_RESPONSES = os.environ.get("USE_MOCK_RESPONSES", "false").lower() == "true"
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")

# Try to import Google AI Platform client libraries - with graceful fallback
try:
    if not USE_MOCK_RESPONSES:
        from google.cloud import aiplatform
        logger.info("Successfully imported Google Cloud AI Platform libraries")
    else:
        logger.info("Running in mock mode - skipping Google Cloud imports")
except ImportError as e:
    logger.warning(f"Google Cloud AI Platform libraries not available: {str(e)}")
    logger.info("Will use mock responses for all AI interactions")
    USE_MOCK_RESPONSES = True

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

# Initialize AI Platform if not in mock mode
if not USE_MOCK_RESPONSES:
    try:
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        logger.info(f"Successfully initialized AI Platform with project {PROJECT_ID}")
    except Exception as e:
        logger.error(f"Error initializing AI Platform: {str(e)}")
        logger.info("Using mock responses due to AI Platform initialization failure")
        USE_MOCK_RESPONSES = True
else:
    logger.info("Running in mock mode - using mock responses for all AI interactions")

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

# Mock response function for fallback or local development
def get_mock_response(message: str) -> str:
    # This is a mock function - in production this would call your LLM
    responses = [
        f"I understand you're saying '{message}'. How can I help you further?",
        f"That's interesting about '{message}'. Let me think about that.",
        f"I see you mentioned '{message}'. Would you like to know more about this topic?",
        f"Regarding '{message}', I have some thoughts that might help you.",
        f"I've processed your message about '{message}'. Here's what I think..."
    ]
    
    # Simulate processing time
    time.sleep(0.5)
    
    current_time = datetime.now().strftime("%H:%M:%S")
    return f"[{current_time}] {random.choice(responses)}"

# AI interaction function - uses Vertex AI in production, mock responses in development
def get_llm_response(message: str, user_id: str) -> str:
    """Get response from AI model or mock"""
    # If we're in mock mode, always use mock responses
    if USE_MOCK_RESPONSES:
        logger.info("Using mock response due to mock mode being enabled")
        return get_mock_response(message)
        
    try:
        if not PROJECT_ID:
            # Fall back to mock responses if AI Platform is not configured
            logger.warning("AI Platform not configured, using mock response")
            return get_mock_response(message)
            
        # In a real implementation, you would use the appropriate Vertex AI endpoint here
        # For now, we'll use mock responses until properly implementing Vertex AI
        logger.warning("Vertex AI integration not fully implemented yet, using mock response")
        return get_mock_response(message)
            
    except Exception as e:
        logger.error(f"Error calling AI service: {str(e)}")
        # Fallback to a basic response in case of error
        return get_mock_response(message)

# API Routes
@app.get("/")
def read_root():
    env_info = "local development" if ENVIRONMENT == "local" else "production"
    mode_info = "mock responses" if USE_MOCK_RESPONSES else "AI Platform integration"
    return {
        "message": f"Welcome to the Like Her API - Running in {env_info} mode with {mode_info}",
        "status": "operational"
    }

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

        # Add moving averages
        hist['MA5'] = hist['Close'].rolling(window=5).mean()
        hist['MA20'] = hist['Close'].rolling(window=20).mean()

        # Replace inf/-inf with 0 and fill NaNs with 0 for JSON compliance
        hist = hist.replace([float('inf'), float('-inf')], 0).fillna(0)

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
            "MA5": hist['MA5'].tolist(),
            "MA20": hist['MA20'].tolist(),
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
    logger.info(f"Mock responses: {USE_MOCK_RESPONSES}")
    
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