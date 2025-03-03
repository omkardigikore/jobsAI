# ai/agents/job_matching_agent.py
import logging
import json
from typing import List, Dict, Any
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

class JobMatchingAgent:
    """AI agent for matching jobs to user resumes"""
    
    JOB_MATCHING_PROMPT = """
    You are an AI assistant that helps match job listings to a candidate's resume. Your task is to:
    
    1. Analyze the candidate's resume
    2. Analyze the job listings provided
    3. Rank the job listings based on how well they match the candidate's skills, experience, and qualifications
    4. For each job, calculate a match percentage (0-100%) and provide a brief explanation of the match
    
    Here is the candidate's resume information in JSON format:
    {resume_json}
    
    Here are the job listings in JSON format:
    {jobs_json}
    
    Please return a ranked list of job matches in the following JSON format:
    
    ```json
    [
      {{
        "job_id": "job_id_here",
        "match_percentage": 85,
        "match_reasons": "Key skills match: Python, React. Experience level matches. Location is suitable.",
        "job_data": {{...original job data...}}
      }},
      {{
        "job_id": "another_job_id",
        "match_percentage": 72,
        "match_reasons": "Skills partially match. More experience required than candidate has.",
        "job_data": {{...original job data...}}
      }}
    ]
    ```
    
    Sort the results by match_percentage in descending order (best matches first).
    """
    
    @staticmethod
    async def match_jobs_to_resume(
        jobs: List[Dict[str, Any]],
        resume_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Match jobs to a user's resume using AI
        
        Args:
            jobs: List of job dictionaries
            resume_data: User's structured resume data
            
        Returns:
            Ranked list of jobs with match information
        """
        try:
            # Prepare prompt with job and resume data
            prompt = JobMatchingAgent.JOB_MATCHING_PROMPT.format(
                resume_json=json.dumps(resume_data, indent=2),
                jobs_json=json.dumps(jobs, indent=2)
            )
            
            # Get AI response
            response_text = await JobMatchingAgent._get_ai_response(prompt)
            
            # Extract JSON from response
            matches_json = JobMatchingAgent._extract_json_from_text(response_text)
            
            try:
                matches = json.loads(matches_json)
                
                # Validate response format
                if not isinstance(matches, list):
                    logger.error("Invalid matches format: not a list")
                    return jobs  # Return original jobs if matching fails
                
                # Ensure each match has required fields
                valid_matches = []
                for match in matches:
                    if all(k in match for k in ["job_id", "match_percentage", "job_data"]):
                        valid_matches.append(match)
                
                if not valid_matches:
                    logger.warning("No valid matches found in AI response")
                    return jobs  # Return original jobs if no valid matches
                
                # Sort by match percentage
                valid_matches.sort(key=lambda x: x.get("match_percentage", 0), reverse=True)
                
                # Return each job with its original data plus match info
                return valid_matches
            
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from AI response: {str(e)}")
                logger.debug(f"AI response: {response_text}")
                return jobs  # Return original jobs if parsing fails
        
        except Exception as e:
            logger.error(f"Error matching jobs to resume: {str(e)}")
            return jobs  # Return original jobs if matching fails
    
    @staticmethod
    async def _get_ai_response(prompt: str) -> str:
        """Get response from AI service"""
        if DEFAULT_AI_PROVIDER == "claude":
            return await JobMatchingAgent._get_claude_response(prompt)
        else:
            return await JobMatchingAgent._get_openai_response(prompt)
    
    @staticmethod
    async def _get_claude_response(prompt: str) -> str:
        """Get response from Claude API"""
        try:
            response = await claude_client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
        
        except Exception as e:
            logger.error(f"Error getting Claude response: {str(e)}")
            
            # Fallback to OpenAI if Claude fails
            logger.info("Falling back to OpenAI")
            return await JobMatchingAgent._get_openai_response(prompt)
    
    @staticmethod
    async def _get_openai_response(prompt: str) -> str:
        """Get response from OpenAI API"""
        try:
            response = await openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error getting OpenAI response: {str(e)}")
            raise
    
    @staticmethod
    def _extract_json_from_text(text: str) -> str:
        """Extract JSON from text (handling markdown code blocks)"""
        import re
        
        # Try to extract JSON from markdown code block
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        
        if json_match:
            return json_match.group(1)
        
        # If no code block, assume the whole text is JSON
        return text
    
    @staticmethod
    async def get_job_application_tips(job_data: Dict[str, Any], resume_data: Dict[str, Any]) -> str:
        """
        Generate job application tips for a specific job based on the user's resume
        
        Args:
            job_data: Job listing data
            resume_data: User's resume data
            
        Returns:
            Tips and suggestions for the job application
        """
        prompt = f"""
        You are a career advisor helping a job seeker prepare for an application. 
        
        Based on the job listing and the candidate's resume below, provide specific tips for:
        1. How to tailor their resume for this specific position
        2. Key skills to emphasize in their application
        3. Potential interview questions they might face
        4. Any gaps or areas they should address or prepare for
        
        JOB LISTING:
        {json.dumps(job_data, indent=2)}
        
        CANDIDATE'S RESUME:
        {json.dumps(resume_data, indent=2)}
        
        Provide your advice in a clear, structured format that would be helpful for the job seeker.
        """
        
        response_text = await JobMatchingAgent._get_ai_response(prompt)
        return response_text