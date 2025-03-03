# ai/prompts/resume_prompts.py

"""
This module contains prompt templates for AI resume processing.
"""

# Prompt for parsing resume text into structured data
RESUME_PARSING_PROMPT = """
You are an expert resume parser. Your task is to extract structured information from the provided resume text.

Resume text:
```
{resume_text}
```

Extract the following information and return it in the specified JSON format:

1. Contact Information:
   - Name
   - Email
   - Phone
   - Location
   - LinkedIn (if available)
   - Website/Portfolio (if available)

2. Summary/Objective (if available)

3. Skills:
   - Technical Skills
   - Soft Skills
   - Languages (programming and spoken)
   - Tools & Technologies

4. Work Experience:
   - For each position:
     - Company Name
     - Job Title
     - Start Date (YYYY-MM format if available, otherwise YYYY)
     - End Date (YYYY-MM format, "Present" for current jobs)
     - Location
     - Responsibilities and Achievements (as bullet points)

5. Education:
   - For each institution:
     - Institution Name
     - Degree/Certificate
     - Field of Study
     - Start Date (YYYY-MM format if available, otherwise YYYY)
     - End Date (YYYY-MM format if available, otherwise YYYY)
     - GPA (if available)

6. Projects (if available):
   - For each project:
     - Project Name
     - Description
     - Technologies Used
     - URL (if available)
     - Start/End Date (if available)

7. Certifications (if available):
   - For each certification:
     - Certification Name
     - Issuing Organization
     - Date Obtained
     - Expiration Date (if applicable)

Return the extracted information in the following JSON format:

```json
{
  "contact_info": {
    "name": "",
    "email": "",
    "phone": "",
    "location": "",
    "linkedin": "",
    "website": ""
  },
  "summary": "",
  "skills": {
    "technical": [],
    "soft": [],
    "languages": [],
    "tools": []
  },
  "work_experience": [
    {
      "company": "",
      "title": "",
      "start_date": "",
      "end_date": "",
      "location": "",
      "responsibilities": []
    }
  ],
  "education": [
    {
      "institution": "",
      "degree": "",
      "field": "",
      "start_date": "",
      "end_date": "",
      "gpa": ""
    }
  ],
  "projects": [
    {
      "name": "",
      "description": "",
      "technologies": [],
      "url": "",
      "date": ""
    }
  ],
  "certifications": [
    {
      "name": "",
      "organization": "",
      "date": "",
      "expiration": ""
    }
  ]
}
```

Important guidelines:
1. If a section is not available in the resume, include the section with empty values.
2. If you're uncertain about a value, leave it blank rather than guessing.
3. For dates, use YYYY-MM format if month is available, otherwise use YYYY.
4. Make sure the JSON is valid and properly formatted.
5. Extract as much detail as possible while maintaining accuracy.
"""

# Prompt for customizing resume for a specific job
RESUME_CUSTOMIZATION_PROMPT = """
You are an expert resume writer specializing in tailoring resumes for specific job applications. Your task is to create a customized resume for a job applicant based on their original resume and the details of the job they're applying for.

JOB DETAILS:
- Title: {job_title}
- Company: {company}
- Required Skills: {required_skills}
- Job Description:
```
{job_description}
```

APPLICANT'S RESUME DATA:
```
{resume_data}
```

Your task is to:

1. Create a customized, ATS-friendly resume that highlights the most relevant skills and experiences for this specific job.
2. Emphasize experiences and skills that match the job requirements.
3. Use keywords from the job description where appropriate.
4. Quantify achievements where possible.
5. Remove or downplay irrelevant information.
6. Format the resume in a clean, professional way.

RETURN GUIDELINES:
1. Return the complete customized resume in Markdown format.
2. Include all standard resume sections (contact info, summary, experience, skills, education, etc.).
3. The resume should be ready for the applicant to save as a PDF and submit with their application.
4. Include a brief section at the beginning titled "CUSTOMIZATION NOTES" that explains the key changes made and why they improve the applicant's chances.

Remember that the goal is to present the applicant as an ideal candidate for this specific position while remaining truthful and authentic to their actual experience.
"""

# Prompt for extracting skills from resume data
RESUME_SKILLS_EXTRACTION_PROMPT = """
You are an expert in skills analysis for job matching. Your task is to extract and categorize skills from a resume, then organize them based on relevance and expertise level.

RESUME DATA:
```
{resume_data}
```

Your task is to:

1. Extract all skills mentioned in the resume data (explicitly stated skills, as well as skills implied by work experience, projects, etc.)
2. Categorize these skills into the following groups:
   - Technical Skills (programming, software, hardware, etc.)
   - Domain Knowledge (industry-specific knowledge)
   - Soft Skills (communication, leadership, etc.)
   - Tools & Platforms (specific tools, software, platforms used)
3. Rate each skill's proficiency level based on the resume content:
   - Expert: Strong evidence of extensive experience and deep knowledge
   - Proficient: Clear evidence of regular application and good understanding
   - Familiar: Some evidence of usage or knowledge
   - Mentioned: Skill is listed but no clear evidence of level
4. Identify the top 5 most marketable skills based on current job market demand

Return the results in the following JSON format:

```json
{
  "technical_skills": [
    {"skill": "Python", "level": "Expert", "evidence": "5+ years experience, led development of multiple projects"},
    {"skill": "JavaScript", "level": "Proficient", "evidence": "Used in frontend development for 3 years"}
  ],
  "domain_knowledge": [
    {"skill": "Financial Analysis", "level": "Expert", "evidence": "Worked as financial analyst for 4 years"}
  ],
  "soft_skills": [
    {"skill": "Team Leadership", "level": "Proficient", "evidence": "Led team of 5 developers"}
  ],
  "tools_platforms": [
    {"skill": "AWS", "level": "Familiar", "evidence": "Mentioned experience with EC2 and S3"}
  ],
  "top_marketable_skills": [
    {"skill": "Python", "market_relevance": "High demand in data science and backend development"},
    {"skill": "AWS", "market_relevance": "Growing demand for cloud expertise"}
  ]
}
```

Make sure to be thorough in extracting skills, including those that may be implied but not explicitly stated. Base your assessment on concrete evidence from the resume.
"""

# Prompt for generating interview questions based on resume and job
INTERVIEW_PREP_PROMPT = """
You are an expert career coach helping a job candidate prepare for an interview. Based on their resume and the job they're applying for, generate tailored interview preparation materials.

JOB DETAILS:
- Title: {job_title}
- Company: {company}
- Required Skills: {required_skills}
- Job Description:
```
{job_description}
```

CANDIDATE'S RESUME:
```
{resume_data}
```

Please provide the following interview preparation materials:

1. LIKELY INTERVIEW QUESTIONS:
   - 5 technical/skill-based questions specific to the role and the candidate's background
   - 5 behavioral questions based on the job requirements
   - 3 questions about potential gaps or mismatches between the resume and job requirements

2. SUGGESTED ANSWERS:
   - For each question, provide a framework or outline for an effective answer based on the candidate's actual experience
   - Include specific examples from their resume that they can reference
   - Where appropriate, suggest how they can address potential weaknesses or gaps

3. QUESTIONS FOR THE INTERVIEWER:
   - Suggest 5 thoughtful questions the candidate can ask the interviewer that demonstrate their understanding of the role and company

4. INTERVIEW STRATEGY:
   - Identify key strengths in the candidate's background that align with the job requirements
   - Suggest specific experiences or achievements to emphasize
   - Note any potential concerns and how to address them proactively

Format your response in a clear, organized manner using Markdown formatting. Make the preparation materials practical and actionable, ready for the candidate to use in their interview preparation.
"""

# Prompt for job matching between resume and job listings
JOB_MATCHING_PROMPT = """
You are an AI assistant specializing in matching job candidates with suitable job opportunities. Your task is to analyze a candidate's resume and a set of job listings to determine the most suitable matches.

CANDIDATE'S RESUME:
```
{resume_data}
```

JOB LISTINGS:
```
{job_listings}
```

For each job listing, evaluate the match based on the following criteria:
1. Skills match: How well do the candidate's technical and soft skills align with the job requirements?
2. Experience match: Does the candidate have relevant experience in terms of roles, responsibilities, and industry?
3. Education match: Does the candidate meet the educational requirements?
4. Location compatibility: Is the job location compatible with the candidate's current location?
5. Career trajectory: Is this job a logical next step in the candidate's career path?

For each job, provide:
1. A match score from 0-100%
2. A brief explanation of why this score was given
3. Key strengths that make the candidate suitable
4. Any potential gaps or areas of concern
5. Suggestions for how the candidate could position themselves for this role

Return your analysis in the following JSON format:

```json
[
  {
    "job_id": "job1",
    "job_title": "Software Engineer",
    "company": "TechCorp",
    "match_score": 85,
    "reasoning": "Strong technical skills match with 3+ years of relevant experience",
    "strengths": ["Python expertise", "Cloud computing experience", "Relevant industry background"],
    "gaps": ["No experience with specific framework mentioned in requirements"],
    "recommendations": ["Emphasize previous work with similar frameworks", "Highlight adaptability and fast learning"]
  }
]
```

Rank the jobs from highest to lowest match score. Be objective and thorough in your assessment, focusing on concrete evidence from both the resume and job listings.
"""