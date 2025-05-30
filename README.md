# Personal Assistant Bot

A sophisticated personal assistant bot that converts fuzzy natural language inputs into structured JSON responses with intent classification, entity extraction, and web search capabilities.
![image](https://github.com/user-attachments/assets/3c35c946-d724-4369-a85e-bca159f8c4ce)


## Features

- **Intent Classification**: Categorizes requests into dining, travel, gifting, cab booking, or other
- **Entity Extraction**: Extracts relevant information like dates, locations, budgets, etc.
- **Confidence Scoring**: Provides confidence level for intent classification
- **Follow-up Questions**: Asks clarifying questions when information is missing
- **Web Search Integration**: Searches the web for queries outside standard categories
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Interactive Frontend**: Streamlit web interface for easy testing

## Tech Stack

- **Backend**: FastAPI, Python 3.8+
- **AI/ML**: Azure OpenAI, LangChain
- **Web Search**: DuckDuckGo Search API
- **Frontend**: Streamlit
- **Data Validation**: Pydantic

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Azure OpenAI API key, endpoint, and deployment name

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ananyadixit28/personal-assistant-bot.git
   cd personal-assistant-bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   Create a `.env` file in the root directory:
   ```
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here
   AZURE_OPENAI_API_VERSION=2023-12-01-preview
   ```

5. **Run the backend API**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Run the frontend (in a new terminal)**
   ```bash
   streamlit run frontend/streamlit_app.py
   ```

7. **Access the application**
   - API Documentation: http://localhost:8000/docs
   - Frontend Interface: http://localhost:8501

## Azure OpenAI Configuration

To use this application with Azure OpenAI, you need:

1. **Azure OpenAI Resource**: Create an Azure OpenAI resource in the Azure portal
2. **Deployment**: Deploy a model (e.g., GPT-3.5-turbo or GPT-4) in your Azure OpenAI resource
3. **Credentials**: Get your endpoint URL and API key from the Azure portal

### Getting Azure OpenAI Credentials

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure OpenAI resource
3. Go to "Keys and Endpoint" section
4. Copy the endpoint URL and one of the keys
5. Go to "Model deployments" to get your deployment name

## API Endpoints

### POST /process
Process user input and return structured response.

**Request Body:**
```json
{
  "user_input": "Need a sunset-view table for two tonight; gluten-free menu a must"
}
```

**Response:**
```json
{
  "intent_category": "dining",
  "entities": {
    "date": "2024-01-15",
    "time": null,
    "location": null,
    "party_size": 2,
    "dietary_restrictions": ["gluten-free"],
    "additional_requirements": ["sunset-view"]
  },
  "confidence_score": 0.95,
  "follow_up_questions": [
    "What time would you prefer for your reservation?",
    "Which city or area are you looking for restaurants in?"
  ],
  "reasoning": "Clear dining intent with specific requirements mentioned"
}
```

## Sample Test Cases

### Dining Example
**Input:** "Need a sunset-view table for two tonight; gluten-free menu a must"
**Output:** See samples/dining_examples.json

## Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

## Project Structure

```
personal-assistant-bot/
├── README.md
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── intent_processor.py  # Main processing logic
│   │   └── web_search.py        # Web search functionality
│   └── utils/
│       ├── __init__.py
│       └── prompt_templates.py  # LLM prompts
├── frontend/
│   └── streamlit_app.py     # Streamlit interface
├── samples/                 # Example inputs/outputs
│   ├── dining_examples.json
│   ├── travel_examples.json
│   ├── gifting_examples.json
│   ├── cab_booking_examples.json
│   └── other_examples.json
└── tests/
    └── test_intent_processor.py
```

## Troubleshooting

### Common Azure OpenAI Issues

1. **Authentication Error**: Verify your API key and endpoint are correct
2. **Deployment Not Found**: Ensure your deployment name matches exactly
3. **Rate Limiting**: Azure OpenAI has rate limits; implement retry logic if needed
4. **API Version**: Make sure you're using a supported API version

### Environment Variables Check

```bash
# Check if environment variables are loaded correctly
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Endpoint:', os.getenv('AZURE_OPENAI_ENDPOINT')); print('Deployment:', os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'))"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request
