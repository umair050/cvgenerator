from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uuid
import traceback
import logging
import re
from typing import Optional
from dotenv import load_dotenv
from services.cv_parser import CVParser
from services.cv_generator import CVGenerator
from services.llm_service import LLMService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(title="CV Converter API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (LLM service will initialize lazily to avoid errors if API key not set)
cv_parser = CVParser()
llm_service = LLMService()
cv_generator = CVGenerator()

# Ensure uploads directory exists
UPLOADS_DIR = "uploads"
OUTPUTS_DIR = "outputs"
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)


class FormatRequest(BaseModel):
    format_type: str  # e.g., "academic", "modern", "traditional", "ats-friendly"
    additional_instructions: Optional[str] = None


class CVSections(BaseModel):
    name: Optional[str] = ""
    designation: Optional[str] = ""
    technical_skills: Optional[str] = ""
    summary: Optional[str] = ""
    industry_experience: Optional[str] = ""
    functional_skills: Optional[str] = ""
    certifications: Optional[str] = ""
    education: Optional[str] = ""
    projects_experience: Optional[str] = ""  # Work history/projects


class ImproveTextRequest(BaseModel):
    text: str
    section_type: str  # e.g., "technical_skills", "summary", etc.


def preprocess_projects_experience(projects_content: str) -> str:
    """
    Preprocess projects experience text to handle unformatted input.
    Converts long paragraphs and ALL CAPS text into properly formatted bullet points.
    """
    if not projects_content or not projects_content.strip():
        return "Projects Experience"
    
    # Split into lines for processing
    lines = projects_content.strip().split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            processed_lines.append('')
            continue
        
        # Check if this line is likely a long, unformatted paragraph (no bullets, very long, all caps)
        is_unformatted_paragraph = (
            len(line) > 200 and  # Very long line
            not line.startswith('-') and 
            not line.startswith('•') and 
            not line.startswith('▪') and
            line.isupper()  # All caps
        )
        
        if is_unformatted_paragraph:
            # Split this long paragraph into sentences and add bullet points
            # Split by period, exclamation, or question mark followed by space and capital letter
            sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', line)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and len(sentence) > 15:
                    # Add bullet point if not present
                    if not sentence.startswith('-'):
                        processed_lines.append(f"- {sentence}")
                    else:
                        processed_lines.append(sentence)
        else:
            # Line is already formatted or short enough - keep as-is
            # But ensure it has a bullet point if it looks like a responsibility
            if len(line) > 20 and not line.startswith('-') and not line.startswith('•') and not line.startswith('▪'):
                # Check if it's NOT a title/header line (doesn't have dates, pipe, or slash)
                is_title = ('|' in line or ' / ' in line or re.search(r'\d{1,2}/\d{4}', line))
                if not is_title:
                    # This might be a responsibility without bullet - add one
                    processed_lines.append(f"- {line}")
                else:
                    processed_lines.append(line)
            else:
                processed_lines.append(line)
    
    projects_content = '\n'.join(processed_lines)
    
    # Ensure projects_experience has proper format - add "Projects Experience" header if missing
    if not projects_content.strip().lower().startswith("projects experience"):
        projects_content = f"Projects Experience\n\n{projects_content}"
    
    return projects_content


@app.get("/")
async def root():
    return {"message": "CV Converter API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/convert")
async def convert_cv(
    file: UploadFile = File(...),
    format_type: str = "modern",
    additional_instructions: Optional[str] = None
):
    """
    Convert CV to a specific format using LLM
    """
    try:
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOADS_DIR, f"{file_id}_{file.filename}")
        output_path = os.path.join(OUTPUTS_DIR, f"{file_id}_converted.docx")
        
        # Save uploaded file
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse CV
        cv_data = await cv_parser.parse_cv(input_path)
        
        if not cv_data:
            raise HTTPException(status_code=400, detail="Could not parse CV. Please ensure it's a valid PDF or DOCX file.")
        
        # Convert using LLM
        converted_text = await llm_service.convert_cv_format(
            cv_data=cv_data,
            target_format=format_type,
            additional_instructions=additional_instructions
        )
        
        # Generate output file
        await cv_generator.generate_docx(converted_text, output_path, format_type=format_type)
        
        # Clean up input file
        os.remove(input_path)
        
        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"converted_cv_{format_type}.docx"
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the full error for debugging
        error_trace = traceback.format_exc()
        logger.error(f"Conversion error: {str(e)}\n{error_trace}")
        
        # Clean up on error
        if 'input_path' in locals() and os.path.exists(input_path):
            try:
                os.remove(input_path)
            except:
                pass
        
        # Return detailed error message
        error_message = str(e)
        if "OPENAI_API_KEY" in error_message:
            error_message = "OpenAI API key is not set. Please configure it in the .env file."
        elif "LLM conversion failed" in error_message:
            error_message = f"AI conversion error: {error_message}"
        
        raise HTTPException(status_code=500, detail=f"Conversion failed: {error_message}")


@app.post("/api/parse-cv")
async def parse_cv(file: UploadFile = File(...)):
    """
    Parse CV and extract structured sections
    """
    try:
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOADS_DIR, f"{file_id}_{file.filename}")
        
        # Save uploaded file
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse CV
        cv_data = await cv_parser.parse_cv(input_path)
        
        if not cv_data:
            raise HTTPException(status_code=400, detail="Could not parse CV. Please ensure it's a valid PDF or DOCX file.")
        
        # Extract sections using LLM
        full_text = cv_data.get('full_text', cv_data.get('raw_text', ''))
        
        # Use LLM to extract structured sections
        extraction_prompt = """Extract the following sections from this CV and return them in a structured format:

1. Technical Skills - Extract ALL technical skills, tools, technologies, platforms that are ACTUALLY MENTIONED in the CV. Group them into logical categories ONLY if the CV already groups them or if similar skills naturally belong together. Format each category as "Category Name: skill1, skill2, skill3" (one category per line, skills comma-separated within each category).

   CRITICAL: 
   - ONLY extract categories that are explicitly present in the CV or can be clearly inferred from how skills are grouped in the CV
   - DO NOT create categories unless the CV explicitly mentions category
   - DO NOT infer or add categories that are not present in the source CV
   - If skills are listed without categories in the CV, you may group similar skills together, but use category names that reflect the actual content (e.g., if the CV mentions SAP tools, use "SAP Tools" not "ERP Systems" unless ERP is mentioned)
   - If the CV lists skills without any grouping, you may create minimal categories based on the actual skills present, but be conservative
   
   Examples of valid categories (only if present in CV):
   - ERP Systems: SAP S/4HANA, SAP ECC 6.0, Oracle E-Business Suite
   - SAP Tools & Methodologies: Activate Methodology, SAP FIORI, SAP Solution Manager
   - Integration & Add-ons: SAP MII Module, T.CON Integration, Machine Online Integration
   - Manufacturing & Planning Expertise: Production Planning, MRP, Variant Configuration
   - Cloud & Infrastructure: Microsoft Azure, AWS, Terraform, Docker
   - Other Technical Skills: Lean Manufacturing, Master Data Management, SAP Reporting, MS Office

   
   OR (also WRONG - no categories):
   SAP S/4HANA
   SAP ECC 6.0
   Microsoft Azure
   
   CRITICAL: Only include categories that have at least 1 skill from the CV. Skip categories with no skills.
   
   IMPORTANT: Be comprehensive and thorough in extraction - aim for 5-8 technical skill categories with multiple skills per category.

2. Summary - Professional summary/objective (one comprehensive paragraph). MUST start with "I am" and be written in first person, as if the person is presenting themselves. The summary should be a single, well-structured paragraph covering: years of experience and specialization, technical expertise and modules worked with, industries served, key achievements and project types, business process expertise, and value delivered. Example format: "I am a highly motivated and results-driven [role] with [X] years of extensive experience in [areas]. Throughout my career, I have worked across diverse industries including [industries], where I have successfully delivered [achievements]. I specialize in [specializations]. My professional expertise extends to [expertise areas]. I take pride in [value proposition]. With a proven track record of [track record], I am deeply committed to [commitment]."

3. Industry Experience - Extract ALL industries/sectors worked in or mentioned in the CV. Be comprehensive - look for industry mentions in work experience, projects, company names, and context. Aim to identify at least 10-15 different industries or sectors. Include both specific industries (e.g., "Pharmaceuticals", "Textiles") and broader sectors (e.g., "Manufacturing", "Healthcare"). Consider industries from all work experiences and projects mentioned.

4. Functional Skills - Extract ALL soft skills, management skills, leadership skills, interpersonal skills, and professional competencies mentioned or demonstrated in the CV. Be thorough and comprehensive. Look for skills in responsibilities, achievements, descriptions, and implied from activities. Aim to identify at least 15-20 functional skills. Include skills like: Project Management, Stakeholder Management, Communication, Problem Solving, Team Leadership, Analytical Thinking, Strategic Planning, Change Management, Conflict Resolution, Time Management, Training & Mentoring, Business Analysis, Requirements Gathering, Documentation, Quality Assurance, Process Improvement, Negotiation, Decision Making, etc.
5. Certification & Trainings - All certifications, licenses, training programs
6. Education - Extract ONLY THE MOST RECENT/HIGHEST educational qualification. Do NOT include all education entries, only the last one (most recent degree or highest level).
   - Format: "Degree Name | Institution Name | Year" (if year available)
   - Format: "Degree Name | Institution Name" (if no year)
   - Include degree level (Bachelor's, Master's, PhD, Diploma, etc.)
   - Include major/specialization if mentioned
   - Include institution name (full or abbreviated as in original)
   - Include graduation year if available
   - Return ONLY ONE entry (the most recent/highest)
   
   Example (only return one entry):
   Master of Business Administration | University Name | 2020
7. Projects Experience / Work History - Extract ALL work experience in the following format for EACH position:

For each job/position, extract:
- Format option 1: "Job Title / Company Name | Dates: MM/YYYY – MM/YYYY | Location" (use forward slash, en-dash for dates, include location ONLY if explicitly mentioned)
- Format option 2: "Job Title, Company Name, Location | Dates: MM/YYYY – MM/YYYY" (comma-separated format, include location in the title line if present)

CRITICAL FORMATTING RULES:
- After the job title line, add individual bullet points (use "- " prefix) for EACH responsibility, one per line
- DO NOT combine multiple responsibilities into a single "Technologies:" line
- DO NOT put responsibilities as a comma-separated list after "Technologies:"
- Each responsibility MUST be on its own separate line with "- " prefix
- Technologies should ONLY be listed as a separate final line containing tools, software, platforms

- Key responsibilities and achievements (as bullet points starting with "- ")
  CRITICAL: Each responsibility should be DETAILED, EXPLANATORY, and LENGTHY. Write comprehensive descriptions that explain:
  * What was done (specific actions and tasks)
  * How it was done (methodologies, tools, approaches)
  * Why it was done (business context and objectives)
  * Results and impact (outcomes, improvements, achievements)
  * Technical details and implementations
  * Collaboration and team interactions
  * Process improvements and optimizations
  
  Each bullet point should be a complete, well-explained sentence or multiple sentences (2-4 sentences per bullet point is ideal). Avoid short, one-line descriptions. Be descriptive and provide context.
  
  Example of GOOD detailed description:
  - "Managed end-to-end project lifecycle, ensuring successful execution and delivery of technical initiatives within diverse industries. Gathered and analyzed project requirements, collaborating closely with stakeholders to define project scope, objectives, and deliverables. Implemented and maintained quality assurance processes to ensure project deliverables meet established standards."
  
  Example of WRONG format (DO NOT DO THIS):
  INFORMATICA ADMINISTRATOR – CES LTD | 06/2023 – PRESENT
  Technologies: - Installed, configured Informatica. Conducted parameter movements. Created user folders. Informatica 9x, Oracle 11g
  
- Technologies used (if mentioned as separate from responsibilities): Technologies: Tech1, Tech2, Tech3

IMPORTANT: 
- Only include location if it is explicitly mentioned in the CV. Do not infer or add location if it's not present.
- Dates can be in format "MM/YYYY - MM/YYYY" or "YYYY-PRESENT" or "MM/YYYY – MM/YYYY" (en-dash or hyphen both acceptable)
- Use format option 1 (forward slash) if location is separate, use format option 2 (comma-separated) if location is part of the company line

Format each position as:
Position Title / Company Name | MM/YYYY – MM/YYYY | Location (only if present)
- Responsibility 1 (detailed, 2-4 sentences)
- Responsibility 2 (detailed, 2-4 sentences)
- Responsibility 3 (detailed, 2-4 sentences)
- Responsibility 4 (detailed, 2-4 sentences)
Technologies: Tech1, Tech2, Tech3

[Separate each position with a blank line]

Return ONLY the content for each section, not the section headers. If a section is not found, return empty string.

Format your response as:
TECHNICAL_SKILLS:
[content here]

SUMMARY:
[content here]

INDUSTRY_EXPERIENCE:
[content here]

FUNCTIONAL_SKILLS:
[content here]

CERTIFICATIONS:
[content here]

EDUCATION:
[content here]

PROJECTS_EXPERIENCE:
[work history content here - each position formatted as shown above]"""

        extracted_text = await llm_service.improve_text(
            text=full_text,
            instruction=extraction_prompt,
            section_type="extraction"
        )
        
        # Parse the extracted sections
        sections = {
            "name": "",
            "designation": "",
            "technical_skills": "",
            "summary": "",
            "industry_experience": "",
            "functional_skills": "",
            "certifications": "",
            "education": "",
            "projects_experience": ""  # Work history/projects
        }
        
        # Try to extract name and designation from header or first lines
        lines_for_header = full_text.split('\n')[:10]  # First 10 lines
        for line in lines_for_header:
            line = line.strip()
            if not line or len(line) > 100:
                continue
            # Look for name (usually first substantial line, might be all caps or title case)
            if not sections.get('name') and len(line) > 3 and len(line) < 100:
                # Check if it looks like a name (no special chars except spaces, hyphens)
                if re.match(r'^[A-Za-z\s\-\.]+$', line) and not any(keyword in line.lower() for keyword in ['email', 'phone', 'linkedin', 'summary', 'experience', 'skills']):
                    sections['name'] = line
            # Look for designation (often after name, might contain keywords like "Engineer", "Manager", etc.)
            if sections.get('name') and not sections.get('designation') and len(line) > 3 and len(line) < 100:
                if any(keyword in line.lower() for keyword in ['engineer', 'manager', 'developer', 'analyst', 'consultant', 'specialist', 'lead', 'director', 'architect']):
                    sections['designation'] = line
                    break
        
        current_section = None
        for line in extracted_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('TECHNICAL_SKILLS:'):
                current_section = 'technical_skills'
                continue
            elif line.startswith('SUMMARY:'):
                current_section = 'summary'
                continue
            elif line.startswith('INDUSTRY_EXPERIENCE:'):
                current_section = 'industry_experience'
                continue
            elif line.startswith('FUNCTIONAL_SKILLS:'):
                current_section = 'functional_skills'
                continue
            elif line.startswith('CERTIFICATIONS:'):
                current_section = 'certifications'
                continue
            elif line.startswith('EDUCATION:'):
                current_section = 'education'
                # Reset education list to only keep the last entry
                sections['education'] = []
                continue
            elif line.startswith('PROJECTS_EXPERIENCE:') or line.startswith('WORK_HISTORY:') or line.startswith('EXPERIENCE:'):
                current_section = 'projects_experience'
                continue
            
            if current_section and current_section in sections:
                if sections[current_section]:
                    sections[current_section] += "\n" + line
                else:
                    sections[current_section] = line
        
        # Clean up input file
        os.remove(input_path)
        
        return sections
    
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Parse error: {str(e)}\n{error_trace}")
        
        if 'input_path' in locals() and os.path.exists(input_path):
            try:
                os.remove(input_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")


@app.post("/api/improve-text")
async def improve_text(request: ImproveTextRequest):
    """
    Improve text using AI (magic button)
    """
    try:
        # Create specific instructions based on section type
        section_instructions = {
            "technical_skills": "Extract and list ALL technical skills, tools, technologies, and platforms mentioned. Be comprehensive and thorough - extract every technology, tool, software, and platform. ALWAYS group them into logical categories - NEVER list skills without categories. ONLY create categories when there are ACTUAL skills to list. DO NOT create empty categories with 'None mentioned'. Format as 'Category Name: skill1, skill2, skill3' (one category per line, skills comma-separated). Create meaningful categories based on skill types (e.g., ERP Systems, Cloud & Infrastructure, DevOps & CI/CD Tools, Databases, Data Integration Tools, Programming & Scripting, Operating Systems, Monitoring Tools, etc.). Each category should have 2-10 related skills (minimum 2 per category). Skip categories that have no skills. Aim to create at least 5-8 skill categories.",
            "industry_experience": "Extract and list ALL industries and sectors worked in or mentioned. Be comprehensive - look for industry mentions in work experience, projects, and context. Return one industry per line in simple format (no markdown). Aim to identify at least 10-15 different industries or sectors. Include both specific industries (e.g., 'Pharmaceuticals', 'Textiles') and broader sectors (e.g., 'Manufacturing', 'Healthcare').",
            "functional_skills": "Extract and list ALL soft skills, management skills, leadership skills, interpersonal skills, and professional competencies mentioned or demonstrated. Be thorough and comprehensive - look for skills in responsibilities, achievements, and descriptions. Return one skill per line in simple format (no categories, no markdown). Aim to identify at least 15-20 functional skills. Include skills like: Project Management, Stakeholder Management, Communication, Problem Solving, Team Leadership, Analytical Thinking, Strategic Planning, Change Management, etc.",
            "certifications": "Extract and list all certifications, licenses, and training programs. Return one certification per line in simple format (no markdown).",
            "education": "Extract and format ONLY THE MOST RECENT/HIGHEST educational qualification. Do NOT include all education entries, only the last one (most recent degree or highest level). Format as 'Degree Name | Institution Name | Year' (if year available) or 'Degree Name | Institution Name'. Include full degree name and institution name. Return only ONE entry.",
            "summary": "Write ONE comprehensive professional paragraph in FIRST PERSON, starting with 'I am'. Write as if the person is presenting themselves. The paragraph should cover: years of experience and specialization, technical expertise and modules/technologies, industries served, key achievements and project types, business process expertise, and value delivered. Example: 'I am a highly motivated and results-driven [role] with [X] years of extensive experience in [areas]. Throughout my career, I have worked across diverse industries including [industries], where I have successfully delivered [achievements]. I specialize in [specializations]. My professional expertise extends to [expertise]. I take pride in [value]. With a proven track record of [track record], I am deeply committed to [commitment].' Use plain text, no markdown or formatting."
        }
        
        instruction = section_instructions.get(
            request.section_type,
            f"Improve and enhance the following {request.section_type} content. Make it more professional, concise, and impactful while preserving all key information."
        )
        
        improved_text = await llm_service.improve_text(
            text=request.text,
            instruction=instruction,
            section_type=request.section_type
        )
        
        # Clean up markdown formatting and parse into proper format
        cleaned_text = improved_text.strip()
        
        # Remove markdown bold (**text**)
        cleaned_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned_text)
        
        # Handle technical_skills differently to preserve category format
        if request.section_type == 'technical_skills':
            # Preserve category format: "Category: skill1, skill2, skill3"
            lines = cleaned_text.split('\n')
            items = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Remove markdown bullets (-, *, •) but preserve category format
                line = re.sub(r'^[-*•]\s+', '', line)
                # For technical_skills, preserve lines with colon (categories)
                if ':' in line:
                    # This is a category line, keep as-is
                    items.append(line)
                elif line and len(line) > 3:
                    # Might be a skill without category, keep it
                    items.append(line)
            cleaned_text = '\n'.join(items)
        # For other list sections, extract individual items
        elif request.section_type in ['industry_experience', 'functional_skills', 'certifications', 'education']:
            lines = cleaned_text.split('\n')
            items = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Remove markdown bullets (-, *, •)
                line = re.sub(r'^[-*•]\s+', '', line)
                # Remove category headers (lines ending with colon that are short)
                if line.endswith(':') and len(line) < 50:
                    continue
                # Skip empty lines after cleaning
                if line:
                    items.append(line)
            cleaned_text = '\n'.join(items)
        else:
            # For summary, just clean markdown but keep paragraphs
            cleaned_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned_text)
            cleaned_text = re.sub(r'^[-*•]\s+', '', cleaned_text, flags=re.MULTILINE)
        
        return {"improved_text": cleaned_text.strip()}
    
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Improve text error: {str(e)}\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Text improvement failed: {str(e)}")


@app.post("/api/generate-cv")
async def generate_cv_from_sections(
    sections: CVSections,
    format_type: str = Query(default="datamatics")
):
    """
    Generate final CV from form sections
    """
    try:
        # Format skills sections - convert to bullet format
        def format_bullet_list(text):
            if not text or not text.strip():
                return ""
            # Split by newlines or commas, then format as bullets
            items = [item.strip() for item in text.replace(',', '\n').split('\n') if item.strip()]
            return '\n'.join([f"- {item}" for item in items])
        
        # Format technical skills - preserve category format
        def format_technical_skills(text):
            if not text or not text.strip():
                return ""
            # For technical skills, preserve category format: "Category: skill1, skill2"
            # Don't add bullets, just return lines as-is if they have colons (categories)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            formatted_lines = []
            for line in lines:
                if ':' in line:
                    # This is a category line, keep as-is
                    formatted_lines.append(line)
                else:
                    # No category, might be from old format, keep as-is
                    formatted_lines.append(line)
            return '\n'.join(formatted_lines)
        
        # Format header: Name | Designation
        header_text = ""
        if sections.name and sections.designation:
            header_text = f"{sections.name} | {sections.designation}"
        elif sections.name:
            header_text = sections.name
        elif sections.designation:
            header_text = sections.designation
        else:
            header_text = "Name | Designation"
        
        # Handle projects experience - include if provided
        projects_content = sections.projects_experience if hasattr(sections, 'projects_experience') and sections.projects_experience else ""
        
        # Preprocess projects_experience to handle unformatted text
        projects_content = preprocess_projects_experience(projects_content)
        
        # Convert sections to datamatics format text
        cv_text = f"""[HEADER]
{header_text}

[LEFT_COLUMN_START]
Technical Skills:
{format_technical_skills(sections.technical_skills)}

Industry Experience:
{format_bullet_list(sections.industry_experience)}

Functional Skills:
{format_bullet_list(sections.functional_skills)}
[LEFT_COLUMN_END]

[RIGHT_COLUMN_START]
Summary:
{sections.summary or ''}

Education/Qualifications/Certifications:
{format_bullet_list(sections.certifications)}
{format_bullet_list(sections.education)}
[RIGHT_COLUMN_END]

[PROJECTS_EXPERIENCE]
{projects_content}
"""
        
        # Generate output file
        file_id = str(uuid.uuid4())
        output_path = os.path.join(OUTPUTS_DIR, f"{file_id}_converted.docx")
        
        await cv_generator.generate_docx(cv_text, output_path, format_type=format_type)
        
        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"cv_{format_type}.docx"
        )
    
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Generate CV error: {str(e)}\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"CV generation failed: {str(e)}")


@app.post("/api/preview-cv")
async def preview_cv(sections: CVSections, format_type: str = Query(default="datamatics")):
    """
    Generate CV preview (returns DOCX file for preview)
    """
    try:
        # Format skills sections - convert to bullet format
        def format_bullet_list(text):
            if not text or not text.strip():
                return ""
            # Split by newlines or commas, then format as bullets
            items = [item.strip() for item in text.replace(',', '\n').split('\n') if item.strip()]
            return '\n'.join([f"- {item}" for item in items])
        
        # Format technical skills - preserve category format
        def format_technical_skills(text):
            if not text or not text.strip():
                return ""
            # For technical skills, preserve category format: "Category: skill1, skill2"
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            formatted_lines = []
            for line in lines:
                if ':' in line:
                    # This is a category line, keep as-is
                    formatted_lines.append(line)
                else:
                    # No category, might be from old format, keep as-is
                    formatted_lines.append(line)
            return '\n'.join(formatted_lines)
        
        # Format header: Name | Designation
        header_text = ""
        if sections.name and sections.designation:
            header_text = f"{sections.name} | {sections.designation}"
        elif sections.name:
            header_text = sections.name
        elif sections.designation:
            header_text = sections.designation
        else:
            header_text = "Name | Designation"
        
        # Handle projects experience - include if provided
        projects_content = sections.projects_experience if hasattr(sections, 'projects_experience') and sections.projects_experience else ""
        
        # Preprocess projects_experience to handle unformatted text
        projects_content = preprocess_projects_experience(projects_content)
        
        # Convert sections to datamatics format text
        cv_text = f"""[HEADER]
{header_text}

[LEFT_COLUMN_START]
Technical Skills:
{format_technical_skills(sections.technical_skills)}

Industry Experience:
{format_bullet_list(sections.industry_experience)}

Functional Skills:
{format_bullet_list(sections.functional_skills)}
[LEFT_COLUMN_END]

[RIGHT_COLUMN_START]
Summary:
{sections.summary or ''}

Education/Qualifications/Certifications:
{format_bullet_list(sections.certifications)}
{format_bullet_list(sections.education)}
[RIGHT_COLUMN_END]

[PROJECTS_EXPERIENCE]
{projects_content}
"""
        
        # Generate output file
        file_id = str(uuid.uuid4())
        output_path = os.path.join(OUTPUTS_DIR, f"{file_id}_preview.docx")
        
        await cv_generator.generate_docx(cv_text, output_path, format_type=format_type)
        
        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"cv_preview.docx"
        )
    
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Preview CV error: {str(e)}\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"CV preview failed: {str(e)}")


@app.get("/api/formats")
async def get_formats():
    """
    Get available CV formats
    """
    return {
        "formats": [
            {
                "id": "datamatics",
                "name": "Datamatics Professional",
                "description": "Two-column professional format with technical/functional skills on left, summary and certifications on right, plus detailed projects experience"
            },
            {
                "id": "modern",
                "name": "Modern",
                "description": "Clean, contemporary design with emphasis on skills and achievements"
            },
            {
                "id": "traditional",
                "name": "Traditional",
                "description": "Classic format suitable for conservative industries"
            },
            {
                "id": "academic",
                "name": "Academic",
                "description": "Format optimized for academic positions and research roles"
            },
            {
                "id": "ats-friendly",
                "name": "ATS-Friendly",
                "description": "Optimized for Applicant Tracking Systems with keyword optimization"
            },
            {
                "id": "creative",
                "name": "Creative",
                "description": "Bold design for creative industries"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

