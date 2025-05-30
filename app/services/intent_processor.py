import json
import logging
from typing import Dict, Any, List
from openai import AzureOpenAI
from app.models import AssistantResponse, IntentCategory, EntityModel, WebSearchResult
from app.utils.prompt_templates import INTENT_CLASSIFICATION_PROMPT, WEB_SEARCH_PROMPT
from app.services.web_search import WebSearchService

logger = logging.getLogger(__name__)

class IntentProcessor:
    def __init__(self, azure_endpoint: str, azure_api_key: str, azure_deployment: str, api_version: str = "2023-12-01-preview"):
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=azure_api_key,
            api_version=api_version
        )
        self.deployment_name = azure_deployment
        self.web_search_service = WebSearchService()
    
    def process_user_input(self, user_input: str) -> AssistantResponse:
        """
        Process user input and return structured response
        """
        try:
            # Get intent classification and entity extraction
            llm_response = self._classify_intent(user_input)
            
            # Parse LLM response
            parsed_response = self._parse_llm_response(llm_response)
            
            # If intent is "other", perform web search
            if parsed_response.intent_category == IntentCategory.OTHER:
                search_results = self._perform_web_search(user_input)
                parsed_response.web_search_results = search_results
            
            return parsed_response
        
        except Exception as e:
            logger.error(f"Error processing user input: {str(e)}")
            # Return fallback response
            return AssistantResponse(
                intent_category=IntentCategory.OTHER,
                entities=EntityModel(),
                confidence_score=0.0,
                follow_up_questions=["I'm sorry, I couldn't understand your request. Could you please rephrase it?"],
                reasoning="Error occurred during processing"
            )
    
    def _classify_intent(self, user_input: str) -> str:
        """
        Use Azure OpenAI to classify intent and extract entities
        """
        prompt = INTENT_CLASSIFICATION_PROMPT.format(user_input=user_input)
        
        response = self.client.chat.completions.create(
            model=self.deployment_name,  # Use deployment name instead of model name
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured information from user requests. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("OpenAI returned no content")
        return content
    
    def _parse_llm_response(self, llm_response: str) -> AssistantResponse:
        """
        Parse LLM response into structured format
        """
        try:
            # Clean the response to extract JSON
            json_str = llm_response.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:-3]
            elif json_str.startswith("```"):
                json_str = json_str[3:-3]
            
            data = json.loads(json_str)
            
            # Create EntityModel
            entities = EntityModel(**data.get("entities", {}))
            
            # Create AssistantResponse
            response = AssistantResponse(
                intent_category=IntentCategory(data.get("intent_category", "other")),
                entities=entities,
                confidence_score=data.get("confidence_score", 0.5),
                follow_up_questions=data.get("follow_up_questions", []),
                reasoning=data.get("reasoning", "")
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            raise e
    
    def _perform_web_search(self, user_input: str) -> List[WebSearchResult]:
        """
        Perform web search for queries that don't fit standard categories
        """
        try:
            # Generate search queries using LLM
            search_queries = self._generate_search_queries(user_input)
            
            # Perform web search
            search_results = self.web_search_service.multi_search(search_queries)
            
            return search_results
        
        except Exception as e:
            logger.error(f"Error performing web search: {str(e)}")
            return []
    
    def _generate_search_queries(self, user_input: str) -> List[str]:
        """
        Generate relevant search queries for the user input
        """
        try:
            prompt = WEB_SEARCH_PROMPT.format(user_input=user_input)
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,  # Use deployment name instead of model name
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("OpenAI returned no content for search query generation")

            queries = content.strip().split('\n')
            return [q.strip() for q in queries if q.strip()]
        
        except Exception as e:
            logger.error(f"Error generating search queries: {str(e)}")
            return [user_input]  # Fallback to original input