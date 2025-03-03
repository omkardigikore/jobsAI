# ai/agents/resume_agent.py
import logging
import json
import os
from datetime import datetime
import aiohttp
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
from ai.prompts.resume_prompts import (
    RESUME_PARSING_PROMPT,
    RESUME_CUSTOMIZATION_PROMPT,
    RESUME_SKILLS_EXTRACTION_PROMPT
)
from models.resume import ResumeRequest
from utils.db import get_db
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Initialize AI clients
claude_client = AsyncAnthropic(api_key=CLAUDE_API_KEY)
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

class ResumeAgent:
    """AI agent for resume parsing and customization"""
    
    @staticmethod
    async def parse_resume(file_path: str) -> dict:
        """
        Parse a resume file and extract structured information
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            dict: Structured resume data
        """
        try:
            # Extract text from resume file
            resume_text = await ResumeAgent._extract_text_from_file(file_path)
            
            if not resume_text:
                logger.error(f"Failed to extract text from resume: {file_path}")
                return None
            
            # Build prompt for resume parsing
            prompt = RESUME_PARSING_PROMPT.format(resume_text=resume_text)
            
            # Get AI response
            response_text = await ResumeAgent._get_ai_response(prompt)
            
            # Parse JSON from response
            try:
                # Extract JSON from response (might be wrapped in markdown code blocks)
                json_text = ResumeAgent._extract_json_from_text(response_text)
                resume_data = json.loads(json_text)
                
                # Validate required fields
                required_fields = ["contact_info", "skills", "work_experience", "education"]
                for field in required_fields:
                    if field not in resume_data:
                        logger.warning(f"Missing required field in resume data: {field}")
                        resume_data[field] = []
                
                return resume_data
            
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from AI response: {str(e)}")
                logger.debug(f"AI response: {response_text}")
                return None
        
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            return None
    
    @staticmethod
    async def customize_resume(user_id: int, job_data: dict, resume_data: dict) -> str:
        """
        Customize a resume for a specific job
        
        Args:
            user_id: User ID
            job_data: Job data
            resume_data: Resume data
            
        Returns:
            str: Customized resume text
        """
        try:
            # Create a resume request record
            async with get_db() as db:
                resume_request = ResumeRequest(
                    user_id=user_id,
                    job_id=job_data["id"],
                    status="processing",
                    original_resume=json.dumps(resume_data)
                )
                
                db.add(resume_request)
                await db.commit()
                await db.refresh(resume_request)
                
                request_id = resume_request.request_id
            
            # Extract job details
            job_title = job_data.get("title", "")
            job_description = job_data.get("description", "")
            company = job_data.get("company", {}).get("name", "")
            required_skills = job_data.get("skills", [])
            
            # Build prompt for resume customization
            prompt = RESUME_CUSTOMIZATION_PROMPT.format(
                job_title=job_title,
                job_description=job_description,
                company=company,
                required_skills=", ".join(required_skills),
                resume_data=json.dumps(resume_data, indent=2)
            )
            
            # Get AI response
            start_time = datetime.now()
            response_text = await ResumeAgent._get_ai_response(prompt, max_tokens=4000)
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Update resume request record
            async with get_db() as db:
                result = await db.execute(
                    select(ResumeRequest).where(ResumeRequest.request_id == request_id)
                )
                resume_request = result.scalar_one_or_none()
                
                if resume_request:
                    resume_request.status = "completed"
                    resume_request.customized_resume = response_text
                    resume_request.processing_time = int(processing_time)
                    resume_request.ai_model_used = CLAUDE_MODEL if DEFAULT_AI_PROVIDER == "claude" else OPENAI_MODEL
                    
                    await db.commit()
            
            # Send customized resume to user
            await ResumeAgent._send_customized_resume(user_id, request_id)
            
            return request_id
        
        except Exception as e:
            logger.error(f"Error customizing resume: {str(e)}")
            
            # Update resume request status to failed
            try:
                async with get_db() as db:
                    result = await db.execute(
                        select(ResumeRequest).where(ResumeRequest.user_id == user_id)
                        .order_by(ResumeRequest.created_at.desc())
                    )
                    resume_request = result.scalar_one_or_none()
                    
                    if resume_request:
                        resume_request.status = "failed"
                        await db.commit()
            except Exception as db_error:
                logger.error(f"Error updating resume request status: {str(db_error)}")
            
            return None
    
    @staticmethod
    async def extract_skills(resume_data: dict) -> list:
        """
        Extract and categorize skills from resume data
        
        Args:
            resume_data: Resume data
            
        Returns:
            list: List of categorized skills
        """
        try:
            # Build prompt for skills extraction
            prompt = RESUME_SKILLS_EXTRACTION_PROMPT.format(
                resume_data=json.dumps(resume_data, indent=2)
            )
            
            # Get AI response
            response_text = await ResumeAgent._get_ai_response(prompt)
            
            # Parse JSON from response
            try:
                # Extract JSON from response
                json_text = ResumeAgent._extract_json_from_text(response_text)
                skills_data = json.loads(json_text)
                
                return skills_data
            
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from AI response: {str(e)}")
                logger.debug(f"AI response: {response_text}")
                return []
        
        except Exception as e:
            logger.error(f"Error extracting skills: {str(e)}")
            return []
    
    @staticmethod
    async def _extract_text_from_file(file_path: str) -> str:
        """Extract text from resume file (PDF, DOC, DOCX)"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                return await ResumeAgent._extract_text_from_pdf(file_path)
            elif file_ext in ['.doc', '.docx']:
                return await ResumeAgent._extract_text_from_docx(file_path)
            else:
                logger.error(f"Unsupported file format: {file_ext}")
                return None
        
        except Exception as e:
            logger.error(f"Error extracting text from file: {str(e)}")
            return None
    
    @staticmethod
    async def _extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                
                return text
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            
            # Fallback to AI extraction if PyPDF2 fails
            return await ResumeAgent._extract_text_with_ai(file_path)
    
    @staticmethod
    async def _extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            import docx
            
            doc = docx.Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text
        
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            
            # Fallback to AI extraction if docx fails
            return await ResumeAgent._extract_text_with_ai(file_path)
    
    @staticmethod
    async def _extract_text_with_ai(file_path: str) -> str:
        """Extract text from file using AI"""
        # This is a placeholder for a more robust solution using OCR or other AI services
        logger.warning(f"Using AI fallback for text extraction from {file_path}")
        return "Failed to extract text from file."
    
    @staticmethod
    async def _get_ai_response(prompt: str, max_tokens: int = 2000) -> str:
        """Get response from AI service"""
        if DEFAULT_AI_PROVIDER == "claude":
            return await ResumeAgent._get_claude_response(prompt, max_tokens)
        else:
            return await ResumeAgent._get_openai_response(prompt, max_tokens)
    
    @staticmethod
    async def _get_claude_response(prompt: str, max_tokens: int = 2000) -> str:
        """Get response from Claude API"""
        try:
            response = await claude_client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
        
        except Exception as e:
            logger.error(f"Error getting Claude response: {str(e)}")
            
            # Fallback to OpenAI if Claude fails
            logger.info("Falling back to OpenAI")
            return await ResumeAgent._get_openai_response(prompt, max_tokens)
    
    @staticmethod
    async def _get_openai_response(prompt: str, max_tokens: int = 2000) -> str:
        """Get response from OpenAI API"""
        try:
            response = await openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
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
    async def _send_customized_resume(user_id: int, request_id: str) -> None:
        """Send customized resume to user via Telegram"""
        try:
            from services.notification_service import send_resume_notification
            
            async with get_db() as db:
                # Get user's telegram ID
                from sqlalchemy.future import select
                from models.user import User
                
                result = await db.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()
                
                if not user:
                    logger.error(f"User not found: {user_id}")
                    return
                
                # Get resume request
                result = await db.execute(
                    select(ResumeRequest).where(ResumeRequest.request_id == request_id)
                )
                resume_request = result.scalar_one_or_none()
                
                if not resume_request or not resume_request.customized_resume:
                    logger.error(f"Resume request not found or incomplete: {request_id}")
                    return
                
                # Send notification
                await send_resume_notification(
                    user.telegram_id,
                    resume_request.customized_resume,
                    resume_request.job_id
                )
        
        except Exception as e:
            logger.error(f"Error sending customized resume: {str(e)}")