import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Personal Assistant Bot",
    page_icon="🤖",
    layout="wide"
)

# Title and description
st.title("🤖 Personal Assistant Bot")
st.markdown("Enter any fuzzy request and get structured information with follow-up questions!")

# Sidebar for API configuration
st.sidebar.title("Configuration")
api_url = st.sidebar.text_input("API URL", value="http://localhost:8000")

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Input")
    
    # Sample inputs for quick testing
    sample_inputs = {
        "Dining": "Need a sunset-view table for two tonight",
        "Travel": "Planning a weekend trip to Paris for 3 people next month",
        "Gifting": "Need a birthday gift for my 25-year-old sister who loves art",
        "Cab Booking": "Book a cab to the airport tomorrow morning, need a large vehicle",
        "Other": "How to update address in Aadhar card online"
    }
    
    selected_sample = st.selectbox("Quick Examples:", [""] + list(sample_inputs.keys()))
    
    if selected_sample:
        user_input = st.text_area("Your Request:", value=sample_inputs[selected_sample], height=100)
    else:
        user_input = st.text_area("Your Request:", height=100, placeholder="Type your request here...")
    
    process_button = st.button("Process Request", type="primary")

with col2:
    st.header("Structured Response")
    
    if process_button and user_input:
        try:
            # Make API request
            with st.spinner("Processing your request..."):
                response = requests.post(
                    f"{api_url}/process",
                    json={"user_input": user_input},
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                
                # Display intent category with emoji
                intent_emoji = {
                    "dining": "🍽️",
                    "travel": "✈️",
                    "gifting": "🎁",
                    "cab_booking": "🚗",
                    "other": "❓"
                }
                
                st.success(f"**Intent Category:** {intent_emoji.get(result['intent_category'], '❓')} {result['intent_category'].title()}")
                
                # Display confidence score
                confidence = result['confidence_score']
                st.metric("Confidence Score", f"{confidence:.2f}", delta=f"{confidence-0.5:.2f}")
                
                # Display entities
                if result['entities']:
                    st.subheader("🔍 Extracted Information")
                    entities = result['entities']
                    
                    for key, value in entities.items():
                        if value is not None and value != [] and value != "":
                            if isinstance(value, list):
                                st.write(f"**{key.replace('_', ' ').title()}:** {', '.join(map(str, value))}")
                            else:
                                st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                
                # Display follow-up questions
                if result['follow_up_questions']:
                    st.subheader("❓ Follow-up Questions")
                    for i, question in enumerate(result['follow_up_questions'], 1):
                        st.write(f"{i}. {question}")
                
                # Display web search results if available
                if result.get('web_search_results'):
                    st.subheader("🌐 Web Search Results")
                    for i, search_result in enumerate(result['web_search_results'], 1):
                        with st.expander(f"{i}. {search_result['title']}"):
                            st.write(search_result['snippet'])
                            st.write(f"**URL:** {search_result['url']}")
                
                # Display reasoning
                if result.get('reasoning'):
                    st.subheader("💭 AI Reasoning")
                    st.write(result['reasoning'])
                
                # Raw JSON response
                with st.expander("📄 Raw JSON Response"):
                    st.json(result)
            
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
        
        except requests.exceptions.RequestException as e:
            st.error(f"Connection Error: {str(e)}")
            st.info("Make sure the API server is running on the specified URL")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Built with using FastAPI, OpenAI, and Streamlit by Ananya")

# Instructions
with st.expander("📖 Instructions"):
    st.markdown("""
    ### How to use:
    1. **Start the API server**: Run `uvicorn app.main:app --reload` from the project root
    2. **Enter your request**: Type any fuzzy request in natural language
    3. **Get structured response**: The AI will categorize your request and extract relevant information
    4. **Answer follow-up questions**: If information is missing, the AI will ask clarifying questions
    
    ### Supported Categories:
    - **🍽️ Dining**: Restaurant reservations, food delivery
    - **✈️ Travel**: Hotel bookings, flights, vacation planning
    - **🎁 Gifting**: Gift recommendations and purchases
    - **🚗 Cab Booking**: Transportation and rideshare requests
    - **❓ Other**: Everything else (includes web search)
    
    ### Examples:
    - "Book a romantic dinner for two at an Italian restaurant tomorrow"
    - "Need a flight to Tokyo for next week, budget under $1000"
    - "Anniversary gift for wife who loves gardening, budget $200"
    - "Airport pickup at 6 AM, need SUV for 4 people"
    - "How to apply for passport renewal in India"
    """)
