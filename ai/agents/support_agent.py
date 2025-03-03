# ai/agents/support_agent.py
import logging
import json
from typing import Tuple, List, Dict, Any
import asyncio
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from config.settings import (
    CLAUDE_API_KEY,
    OPENAI_API_KEY,
    DEFAULT_AI_PROVIDER,
    CLAUDE_MODEL,
    OPENAI_MODEL
)

logger = logging.getLogger(__name__)

# Initialize AI clients
claude_client = AsyncAnthropic(api_key=CLAUDE_API_KEY)
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

class SupportAgent:
    """AI agent for handling support requests"""
    
    SUPPORT_PROMPT = """
    You are an AI support assistant for a Telegram bot that provides job updates and resume customization services. 
    Your task is to help users with their questions and issues related to the bot's services.

    Available Services:
    1. Job Updates - Users receive personalized job listings based on their resume
    2. Resume Customization - AI generates tailored resumes for specific job applications
    3. Subscription Management - Users can subscribe to different plans

    Common Issues:
    - Subscription payment problems
    - Resume upload failures
    - Questions about job matching
    - Account management
    - Technical issues with the bot

    Guidelines:
    - Be helpful, friendly, and professional
    - Provide clear and concise answers
    - If you don't know the answer, say so and offer to escalate to a human agent
    - For payment issues, always suggest contacting human support
    - For complex technical problems, offer to escalate to a human agent
    - Use markdown formatting for better readability

    User Message:
    {user_message}

    Conversation History:
    {conversation_history}
    
    Your response should be helpful and concise. At the end of your response, include one line with your assessment on whether this query needs human escalation. Format it as: NEEDS_HUMAN: true or NEEDS_HUMAN: false
    """
    
    @staticmethod
    async def get_support_response(
        user_message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Tuple[str, bool]:
        """
        Get support response from AI
        
        Args:
            user_message: User's message
            conversation_history: Previous conversation history
            
        Returns:
            Tuple of (response_text, needs_human_escalation)
        """
        try:
            # Format conversation history for prompt
            history_text = ""
            
            if conversation_history:
                history_text = "\n".join([
                    f"{msg['role'].capitalize()}: {msg['content']}"
                    for msg in conversation_history
                ])
            
            # Build prompt
            prompt = SupportAgent.SUPPORT_PROMPT.format(
                user_message=user_message,
                conversation_history=history_text
            )
            
            # Get AI response
            response_text = await SupportAgent._get_ai_response(prompt)
            
            # Extract the needs_human flag
            needs_human = False
            
            if "NEEDS_HUMAN: true" in response_text.lower():
                needs_human = True
                # Remove the flag from the response
                response_text = response_text.replace("NEEDS_HUMAN: true", "").strip()
                response_text = response_text.replace("NEEDS_HUMAN: True", "").strip()
            else:
                # Remove the flag from the response
                response_text = response_text.replace("NEEDS_HUMAN: false", "").strip()
                response_text = response_text.replace("NEEDS_HUMAN: False", "").strip()
            
            return response_text, needs_human
        
        except Exception as e:
            logger.error(f"Error getting support response: {str(e)}")
            return (
                "I'm having trouble processing your request right now. "
                "Please try again later or contact our support team directly.",
                True
            )
    
    @staticmethod
    async def _get_ai_response(prompt: str) -> str:
        """Get response from AI service"""
        if DEFAULT_AI_PROVIDER == "claude":
            return await SupportAgent._get_claude_response(prompt)
        else:
            return await SupportAgent._get_openai_response(prompt)
    
    @staticmethod
    async def _get_claude_response(prompt: str) -> str:
        """Get response from Claude API"""
        try:
            response = await claude_client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
        
        except Exception as e:
            logger.error(f"Error getting Claude response: {str(e)}")
            
            # Fallback to OpenAI if Claude fails
            logger.info("Falling back to OpenAI")
            return await SupportAgent._get_openai_response(prompt)
    
    @staticmethod
    async def _get_openai_response(prompt: str) -> str:
        """Get response from OpenAI API"""
        try:
            response = await openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error getting OpenAI response: {str(e)}")
            raise