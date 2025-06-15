# app/services/ai_synthesis_service.py
import os
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Import the ContentFetchService class
from app.services.content_fetch_service import ContentFetchService

logger = logging.getLogger(__name__)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class AISynthesisService:
    _instance = None # For optional singleton pattern

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AISynthesisService, cls).__new__(cls)
        return cls._instance

    def __init__(self, content_fetch_service: ContentFetchService = None): # Receives dependency
        if hasattr(self, '_initialized') and self._initialized:
            return

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("AISynthesisService initialized.")

        if content_fetch_service is None:
            raise RuntimeError("ContentFetchService instance must be provided to AISynthesisService.")
        self.content_fetch_service = content_fetch_service
        
        # Initialize OpenAI client
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            self.logger.warning("OPENAI_API_KEY not found in environment variables. AI synthesis will use fallback responses.")
            self.openai_client = None
        else:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            
        # Rate limiting
        self.last_api_call = None
        self.api_call_interval = timedelta(seconds=1)  # Minimum 1 second between calls
        
        self._initialized = True


    def _enforce_rate_limit(self):
        """Enforce rate limiting between API calls."""
        if self.last_api_call:
            time_since_last_call = datetime.now() - self.last_api_call
            if time_since_last_call < self.api_call_interval:
                sleep_time = (self.api_call_interval - time_since_last_call).total_seconds()
                self.logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                import time
                time.sleep(sleep_time)
        self.last_api_call = datetime.now()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    def _call_openai_api(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Make a call to OpenAI API with retry logic and error handling.
        """
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized")
            
        self._enforce_rate_limit()
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a wise and insightful astrological advisor. Provide meaningful, personalized astrological interpretations that are both mystical and practical. Keep responses concise but profound."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {str(e)}")
            raise

    def _generate_fallback_summary(self, user_data: Dict, dashboard_content: Dict) -> str:
        """Generate a fallback summary when AI is not available."""
        summary_text = "Based on your recent activities and cosmic influences, your dashboard highlights:\n"
        
        if dashboard_content and "featured_insight_content" in dashboard_content:
            summary_text += f"- Today's Insight: {dashboard_content['featured_insight_content']}\n"
        
        # Add some dynamic elements based on user data
        birth_date = user_data.get('birth_date')
        if birth_date:
            summary_text += "- Your natal chart influences are particularly strong today\n"
            
        summary_text += "- Focus on harmonious interactions and personal growth\n"
        summary_text += "- The cosmic energies support new beginnings and creative endeavors"
        
        return summary_text

    def generate_dashboard_summary(self, user_data: Dict) -> Dict[str, Any]:
        """
        Generates a summary for the user's dashboard based on various data.
        """
        self.logger.info(f"Generating AI dashboard summary for user: {user_data.get('user_id', 'N/A')}")
        
        # Access content fetch service methods via the instance
        dashboard_content = self.content_fetch_service.get_dashboard_content()
        
        # Prepare context for AI
        context = self._prepare_astrological_context(user_data, dashboard_content)
        
        # Try to generate AI-powered summary
        try:
            if self.openai_client:
                prompt = f"""
                Create a personalized astrological dashboard summary for a user based on the following information:
                
                User Context: {context}
                
                Provide insights about:
                1. Current cosmic influences affecting them
                2. Practical guidance for today
                3. Areas of focus for personal growth
                
                Keep the tone mystical yet practical, and make it feel personalized.
                """
                
                ai_summary = self._call_openai_api(prompt, max_tokens=300)
                summary_text = ai_summary
                
            else:
                summary_text = self._generate_fallback_summary(user_data, dashboard_content)
                
        except Exception as e:
            self.logger.error(f"Failed to generate AI summary: {str(e)}")
            summary_text = self._generate_fallback_summary(user_data, dashboard_content)
        
        generated_summary = {
            "title": "Your Cosmic Dashboard Summary",
            "summary_text": summary_text,
            "dynamic_tip": self._generate_dynamic_tip(user_data),
            "source_data_loaded": True if dashboard_content else False,
            "ai_powered": self.openai_client is not None
        }
        
        return generated_summary

    def _prepare_astrological_context(self, user_data: Dict, dashboard_content: Dict) -> str:
        """Prepare contextual information for AI processing."""
        context_parts = []
        
        # Add user birth information if available
        if user_data.get('birth_date'):
            context_parts.append(f"Birth date: {user_data['birth_date']}")
        if user_data.get('birth_location'):
            context_parts.append(f"Birth location: {user_data['birth_location']}")
            
        # Add current featured content
        if dashboard_content and dashboard_content.get('featured_insight_content'):
            context_parts.append(f"Today's featured insight: {dashboard_content['featured_insight_content']}")
            
        # Add current date for temporal context
        context_parts.append(f"Current date: {datetime.now().strftime('%Y-%m-%d')}")
        
        return " | ".join(context_parts) if context_parts else "General astrological guidance requested"

    def _generate_dynamic_tip(self, user_data: Dict) -> str:
        """Generate a quick dynamic tip."""
        try:
            if self.openai_client:
                prompt = f"Give a brief, actionable astrological tip for someone born on {user_data.get('birth_date', 'unknown date')} for today. Maximum 20 words."
                return self._call_openai_api(prompt, max_tokens=50)
        except Exception as e:
            self.logger.error(f"Failed to generate dynamic tip: {str(e)}")
            
        # Fallback tips
        fallback_tips = [
            "Trust your intuition in decision-making today.",
            "Focus on harmonious interactions with others.",
            "Channel your energy into creative pursuits.",
            "Practice mindfulness to align with cosmic rhythms.",
            "Embrace change as an opportunity for growth."
        ]
        
        import random
        return random.choice(fallback_tips)

    def generate_astrological_interpretation(self, chart_data: Dict, interpretation_type: str = "general") -> Dict[str, Any]:
        """
        Generate detailed astrological interpretations based on chart data.
        
        Args:
            chart_data: Dictionary containing astrological chart information
            interpretation_type: Type of interpretation ("general", "transit", "compatibility")
        """
        self.logger.info(f"Generating {interpretation_type} astrological interpretation")
        
        try:
            if self.openai_client:
                prompt = self._create_interpretation_prompt(chart_data, interpretation_type)
                interpretation = self._call_openai_api(prompt, max_tokens=800)
                
                return {
                    "interpretation": interpretation,
                    "type": interpretation_type,
                    "generated_at": datetime.now().isoformat(),
                    "ai_powered": True,
                    "confidence": "high"
                }
            else:
                return self._generate_fallback_interpretation(chart_data, interpretation_type)
                
        except Exception as e:
            self.logger.error(f"Failed to generate interpretation: {str(e)}")
            return self._generate_fallback_interpretation(chart_data, interpretation_type)

    def _create_interpretation_prompt(self, chart_data: Dict, interpretation_type: str) -> str:
        """Create a detailed prompt for astrological interpretation."""
        base_prompt = f"""
        As an expert astrologer, provide a detailed {interpretation_type} interpretation based on the following astrological data:
        
        Chart Data: {chart_data}
        
        Please provide insights covering:
        """
        
        if interpretation_type == "general":
            base_prompt += """
            - Personality traits and characteristics
            - Life themes and potential challenges
            - Strengths and areas for development
            - Career and relationship tendencies
            """
        elif interpretation_type == "transit":
            base_prompt += """
            - Current planetary influences
            - Timing for important decisions
            - Opportunities and challenges ahead
            - Specific guidance for the next 30 days
            """
        elif interpretation_type == "compatibility":
            base_prompt += """
            - Relationship dynamics and compatibility
            - Areas of harmony and potential conflict
            - Communication styles and needs
            - Long-term relationship potential
            """
            
        base_prompt += "\nProvide practical, actionable guidance while maintaining the mystical and insightful tone of traditional astrology."
        
        return base_prompt

    def _generate_fallback_interpretation(self, chart_data: Dict, interpretation_type: str) -> Dict[str, Any]:
        """Generate fallback interpretation when AI is not available."""
        fallback_interpretations = {
            "general": "Your chart reveals a complex and fascinating personality with unique gifts and challenges. Focus on understanding your core motivations and expressing your authentic self.",
            "transit": "Current planetary movements suggest a time of transformation and growth. Pay attention to new opportunities presenting themselves over the next few weeks.",
            "compatibility": "This relationship has the potential for deep understanding and mutual growth. Focus on open communication and respecting each other's individual paths."
        }
        
        return {
            "interpretation": fallback_interpretations.get(interpretation_type, "The stars offer guidance for your journey ahead."),
            "type": interpretation_type,
            "generated_at": datetime.now().isoformat(),
            "ai_powered": False,
            "confidence": "medium"
        }