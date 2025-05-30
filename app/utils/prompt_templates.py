INTENT_CLASSIFICATION_PROMPT = """
You are an intelligent personal assistant that analyzes user requests and extracts structured information.

Given the user input, analyze and respond with a JSON object containing:
1. intent_category: One of ["dining", "travel", "gifting", "cab_booking", "other"]
2. entities: Extract relevant information like date, time, location, etc.
3. confidence_score: Float between 0.0 and 1.0
4. follow_up_questions: Array of questions for missing/ambiguous information
5. reasoning: Brief explanation of your classification

Classification Guidelines:
- DINING: Restaurant reservations, food delivery, meal planning
- TRAVEL: Hotel bookings, flight reservations, vacation planning, sightseeing
- GIFTING: Gift recommendations, purchase assistance for presents
- CAB_BOOKING: Taxi, rideshare, transportation requests
- OTHER: Everything else that doesn't fit the above categories

Entity Extraction Guidelines:
- date: Extract dates in YYYY-MM-DD format when possible
- time: Extract times in HH:MM format
- location: Current location or starting point
- destination: Target location
- party_size: Number of people
- budget: Budget constraints mentioned
- dietary_restrictions: Food allergies, preferences (vegetarian, gluten-free, etc.)

Follow-up Questions Guidelines:
- For DINING: Ask about party size, date/time, dietary restrictions if missing
- For TRAVEL: Ask about dates, number of travelers, budget if missing
- For GIFTING: Ask about recipient, occasion, budget if missing
- For CAB_BOOKING: Ask about destination, pickup time, vehicle preference if missing

User Input: "{user_input}"

Respond with valid JSON only:
"""

WEB_SEARCH_PROMPT = """
Based on the user query: "{user_input}"

This appears to be a request that requires web search. Generate 2-3 relevant search queries that would help find useful information for the user.

Return only the search queries, one per line, without any additional text or formatting.
"""