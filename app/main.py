import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.models import UserRequest, AssistantResponse
from app.services.intent_processor import IntentProcessor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Personal Assistant Bot API",
    description="API for processing fuzzy user inputs and converting them to structured responses",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize intent processor
try:
    # Get Azure OpenAI configuration from environment variables
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
    
    # Validate required environment variables
    if not azure_endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
    if not azure_api_key:
        raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
    if not azure_deployment:
        raise ValueError("AZURE_OPENAI_DEPLOYMENT_NAME environment variable is required")
    
    intent_processor = IntentProcessor(
        azure_endpoint=azure_endpoint,
        azure_api_key=azure_api_key,
        azure_deployment=azure_deployment,
        api_version=api_version
    )
    logger.info("Intent processor initialized successfully with Azure OpenAI")
except Exception as e:
    logger.error(f"Failed to initialize intent processor: {str(e)}")
    intent_processor = None

@app.get("/")
async def root():
    return {"message": "Personal Assistant Bot API is running with Azure OpenAI!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "personal-assistant-bot", "ai_provider": "Azure OpenAI"}

@app.post("/process", response_model=AssistantResponse)
async def process_user_input(request: UserRequest) -> AssistantResponse:
    """
    Process user input and return structured response
    """
    if not intent_processor:
        raise HTTPException(status_code=500, detail="Service not properly initialized")
    
    try:
        logger.info(f"Processing user input: {request.user_input}")
        response = intent_processor.process_user_input(request.user_input)
        logger.info(f"Successfully processed input with intent: {response.intent_category}")
        return response
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)