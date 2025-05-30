import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from app.services.intent_processor import IntentProcessor
from app.models import AssistantResponse, IntentCategory, EntityModel, WebSearchResult

class TestIntentProcessor:
    """Test cases for IntentProcessor class"""
    
    @pytest.fixture
    def mock_azure_client(self):
        """Mock Azure OpenAI client"""
        with patch('app.services.intent_processor.AzureOpenAI') as mock_client:
            yield mock_client
    
    @pytest.fixture
    def mock_web_search(self):
        """Mock web search service"""
        with patch('app.services.intent_processor.WebSearchService') as mock_search:
            yield mock_search
    
    @pytest.fixture
    def intent_processor(self, mock_azure_client, mock_web_search):
        """Create IntentProcessor instance with mocked dependencies"""
        return IntentProcessor(
            azure_endpoint="https://test.openai.azure.com/",
            azure_api_key="test-key",
            azure_deployment="test-deployment",
            api_version="2023-12-01-preview"
        )
    
    def test_initialization(self, mock_azure_client):
        """Test IntentProcessor initialization"""
        processor = IntentProcessor(
            azure_endpoint="https://test.openai.azure.com/",
            azure_api_key="test-key",
            azure_deployment="test-deployment"
        )
        
        mock_azure_client.assert_called_once_with(
            azure_endpoint="https://test.openai.azure.com/",
            api_key="test-key",
            api_version="2023-12-01-preview"
        )
        assert processor.deployment_name == "test-deployment"
    
    def test_dining_intent_classification(self, intent_processor, mock_azure_client):
        """Test dining intent classification"""
        # Mock response from Azure OpenAI
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "intent_category": "dining",
            "entities": {
                "party_size": 2,
                "dietary_restrictions": ["gluten-free"],
                "additional_requirements": ["sunset-view"]
            },
            "confidence_score": 0.95,
            "follow_up_questions": [
                "What time would you prefer for your reservation?",
                "Which city or area are you looking for restaurants in?"
            ],
            "reasoning": "Clear dining intent with specific requirements"
        })
        
        mock_azure_client.return_value.chat.completions.create.return_value = mock_response
        
        user_input = "Need a sunset-view table for two tonight; gluten-free menu a must"
        result = intent_processor.process_user_input(user_input)
        
        assert result.intent_category == IntentCategory.DINING
        assert result.entities.party_size == 2
        assert "gluten-free" in result.entities.dietary_restrictions
        assert result.confidence_score == 0.95
        assert len(result.follow_up_questions) == 2
    
    def test_travel_intent_classification(self, intent_processor, mock_azure_client):
        """Test travel intent classification"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "intent_category": "travel",
            "entities": {
                "destination": "Paris",
                "party_size": 3,
                "duration": "weekend"
            },
            "confidence_score": 0.92,
            "follow_up_questions": [
                "What are your preferred travel dates?",
                "What is your budget for this trip?"
            ],
            "reasoning": "Travel intent for Paris vacation planning"
        })
        
        mock_azure_client.return_value.chat.completions.create.return_value = mock_response
        
        user_input = "Planning a weekend trip to Paris for 3 people next month"
        result = intent_processor.process_user_input(user_input)
        
        assert result.intent_category == IntentCategory.TRAVEL
        assert result.entities.destination == "Paris"
        assert result.entities.party_size == 3
        assert result.entities.duration == "weekend"
        assert result.confidence_score == 0.92
    
    def test_gifting_intent_classification(self, intent_processor, mock_azure_client):
        """Test gifting intent classification"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "intent_category": "gifting",
            "entities": {
                "recipient": "25-year-old sister",
                "gift_type": "art-related",
                "additional_requirements": ["loves art"]
            },
            "confidence_score": 0.88,
            "follow_up_questions": [
                "What is your budget for this gift?",
                "What type of art does she prefer?"
            ],
            "reasoning": "Gift recommendation request for art-loving sister"
        })
        
        mock_azure_client.return_value.chat.completions.create.return_value = mock_response
        
        user_input = "Need a birthday gift for my 25-year-old sister who loves art"
        result = intent_processor.process_user_input(user_input)
        
        assert result.intent_category == IntentCategory.GIFTING
        assert result.entities.recipient == "25-year-old sister"
        assert result.entities.gift_type == "art-related"
        assert result.confidence_score == 0.88
    
    def test_cab_booking_intent_classification(self, intent_processor, mock_azure_client):
        """Test cab booking intent classification"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "intent_category": "cab_booking",
            "entities": {
                "destination": "airport",
                "time": "morning",
                "vehicle_type": "large vehicle"
            },
            "confidence_score": 0.94,
            "follow_up_questions": [
                "What time do you need to be picked up?",
                "What is your pickup location?"
            ],
            "reasoning": "Clear cab booking request for airport transport"
        })
        
        mock_azure_client.return_value.chat.completions.create.return_value = mock_response
        
        user_input = "Book a cab to the airport tomorrow morning, need a large vehicle"
        result = intent_processor.process_user_input(user_input)
        
        assert result.intent_category == IntentCategory.CAB_BOOKING
        assert result.entities.destination == "airport"
        assert result.entities.vehicle_type == "large vehicle"
        assert result.confidence_score == 0.94
    
    def test_other_intent_with_web_search(self, intent_processor, mock_azure_client, mock_web_search):
        """Test other intent classification with web search"""
        # Mock intent classification response
        intent_response = Mock()
        intent_response.choices = [Mock()]
        intent_response.choices[0].message.content = json.dumps({
            "intent_category": "other",
            "entities": {},
            "confidence_score": 0.85,
            "follow_up_questions": [],
            "reasoning": "General information query requiring web search"
        })
        
        # Mock search query generation response
        search_response = Mock()
        search_response.choices = [Mock()]
        search_response.choices[0].message.content = "Aadhar card address update online\nAadhar address change process"
        
        mock_azure_client.return_value.chat.completions.create.side_effect = [
            intent_response, search_response
        ]
        
        # Mock web search results
        mock_search_results = [
            WebSearchResult(
                title="How to Update Address in Aadhar Card Online",
                url="https://example.com/aadhar-update",
                snippet="Step by step guide to update address in Aadhar card online..."
            )
        ]
        mock_web_search.return_value.multi_search.return_value = mock_search_results
        
        user_input = "How to update address in Aadhar card online"
        result = intent_processor.process_user_input(user_input)
        
        assert result.intent_category == IntentCategory.OTHER
        assert result.web_search_results is not None
        assert len(result.web_search_results) == 1
        assert "Aadhar" in result.web_search_results[0].title
    
    def test_invalid_json_response_handling(self, intent_processor, mock_azure_client):
        """Test handling of invalid JSON response from LLM"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Invalid JSON response"
        
        mock_azure_client.return_value.chat.completions.create.return_value = mock_response
        
        user_input = "Test input"
        result = intent_processor.process_user_input(user_input)
        
        # Should return fallback response
        assert result.intent_category == IntentCategory.OTHER
        assert result.confidence_score == 0.0
        assert "I'm sorry, I couldn't understand your request" in result.follow_up_questions[0]
    
    def test_api_error_handling(self, intent_processor, mock_azure_client):
        """Test handling of API errors"""
        mock_azure_client.return_value.chat.completions.create.side_effect = Exception("API Error")
        
        user_input = "Test input"
        result = intent_processor.process_user_input(user_input)
        
        # Should return fallback response
        assert result.intent_category == IntentCategory.OTHER
        assert result.confidence_score == 0.0
        assert result.reasoning == "Error occurred during processing"
    
    def test_json_parsing_with_code_blocks(self, intent_processor, mock_azure_client):
        """Test JSON parsing when response is wrapped in code blocks"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''```json
        {
            "intent_category": "dining",
            "entities": {"party_size": 4},
            "confidence_score": 0.9,
            "follow_up_questions": ["What cuisine do you prefer?"],
            "reasoning": "Dining request identified"
        }
        ```'''
        
        mock_azure_client.return_value.chat.completions.create.return_value = mock_response
        
        user_input = "Book a table for 4"
        result = intent_processor.process_user_input(user_input)
        
        assert result.intent_category == IntentCategory.DINING
        assert result.entities.party_size == 4
        assert result.confidence_score == 0.9
    
    def test_web_search_query_generation_error(self, intent_processor, mock_azure_client, mock_web_search):
        """Test web search when query generation fails"""
        # Mock intent classification response for "other" category
        intent_response = Mock()
        intent_response.choices = [Mock()]
        intent_response.choices[0].message.content = json.dumps({
            "intent_category": "other",
            "entities": {},
            "confidence_score": 0.8,
            "follow_up_questions": [],
            "reasoning": "General query"
        })
        
        # Mock search query generation to fail
        mock_azure_client.return_value.chat.completions.create.side_effect = [
            intent_response,
            Exception("Query generation failed")
        ]
        
        # Mock web search with fallback query
        mock_web_search.return_value.multi_search.return_value = []
        
        user_input = "Test query"
        result = intent_processor.process_user_input(user_input)
        
        assert result.intent_category == IntentCategory.OTHER
        # Should still attempt web search with original input as fallback
        mock_web_search.return_value.multi_search.assert_called_once_with(["Test query"])
    
    def test_empty_entities_handling(self, intent_processor, mock_azure_client):
        """Test handling of empty entities in response"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "intent_category": "dining",
            "entities": {},
            "confidence_score": 0.7,
            "follow_up_questions": ["Could you provide more details?"],
            "reasoning": "Insufficient information provided"
        })
        
        mock_azure_client.return_value.chat.completions.create.return_value = mock_response
        
        user_input = "restaurant"
        result = intent_processor.process_user_input(user_input)
        
        assert result.intent_category == IntentCategory.DINING
        assert result.entities.party_size is None
        assert result.entities.cuisine is None
        assert result.confidence_score == 0.7

# Integration tests (require actual Azure OpenAI setup)
class TestIntentProcessorIntegration:
    """Integration tests for IntentProcessor (requires Azure OpenAI setup)"""
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not all([
            os.getenv("AZURE_OPENAI_ENDPOINT"),
            os.getenv("AZURE_OPENAI_API_KEY"),
            os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        ]),
        reason="Azure OpenAI credentials not available"
    )
    def test_real_azure_openai_integration(self):
        """Test with real Azure OpenAI API (requires valid credentials)"""
        processor = IntentProcessor(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            azure_api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
        )
        
        user_input = "Planning a weekend trip to Paris for 3 people next month"
        result = processor.process_user_input(user_input)
        
        assert result.intent_category == IntentCategory.TRAVEL
        assert result.confidence_score >0.5
        assert result.entities.party_size == 3
        assert result.entities.destination == "Paris"

# Pytest configuration for running specific test groups
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (deselect with '-m \"not integration\"')"
    )