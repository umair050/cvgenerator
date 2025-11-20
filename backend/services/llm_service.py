import os
from openai import OpenAI
from typing import Dict, Optional
import json


class LLMService:
    """Service for interacting with OpenAI API to convert CV formats"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # Don't raise error on init, allow lazy initialization
            self.client = None
            # gpt-4o is the best current model: fastest, most accurate, cost-effective
            # Alternative: "gpt-4o-2024-08-06" for more consistent results (dated version)
            # For budget: "gpt-4o-mini" (faster, cheaper, slightly less accurate)
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        else:
            self.client = OpenAI(api_key=api_key)
            # gpt-4o is the best current model: fastest, most accurate, cost-effective
            # Alternative: "gpt-4o-2024-08-06" for more consistent results (dated version)
            # For budget: "gpt-4o-mini" (faster, cheaper, slightly less accurate)
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    async def convert_cv_format(
        self,
        cv_data: Dict[str, any],
        target_format: str,
        additional_instructions: Optional[str] = None
    ) -> str:
        """
        Use LLM to convert CV to target format
        Returns formatted CV text
        """
        
        format_prompts = {
            "datamatics": """
            Convert this CV into a professional two-column format matching the Datamatics template structure EXACTLY.
            
            CRITICAL FORMATTING REQUIREMENTS:
            - Use EXACT section markers: [HEADER], [LEFT_COLUMN_START], [LEFT_COLUMN_END], [RIGHT_COLUMN_START], [RIGHT_COLUMN_END], [PROJECTS_EXPERIENCE]
            - Section headers must be EXACTLY: "Technical Skills:", "Functional Skills:", "Industry Experience:", "Summary:", "Education/Qualifications/Certifications:"
            - Use bullet points with "- " prefix for all list items
            - Dates must be in format: "MM/YYYY – MM/YYYY" or "MM/YYYY – Present"
            
            HEADER SECTION:
            - Format: "Full Name | Job Title" (use pipe separator)
            - Example: "FAROOQ RAZI | DevOps Engineer"
            
            TWO-COLUMN LAYOUT:
            
            LEFT COLUMN ([LEFT_COLUMN_START] to [LEFT_COLUMN_END]):
            1. Technical Skills: - Extract ALL technical skills, tools, technologies, platforms that are ACTUALLY MENTIONED in the CV. Be comprehensive and thorough - extract every technology, tool, software, platform, and technical capability mentioned. Group them into logical, meaningful categories based on skill types. Format as "Category Name: skill1, skill2, skill3" (one category per line, skills comma-separated within each category). Aim to create at least 5-8 skill categories with multiple skills in each category.
            
            CRITICAL RULES FOR TECHNICAL SKILLS CATEGORIZATION:
            - ALWAYS group skills into categories - NEVER list skills without categories
            - ONLY create categories when there are ACTUAL skills to list in that category
            - DO NOT create empty categories or categories with "None mentioned"
            - DO NOT create categories if no skills exist for that category in the CV
            - Create categories based ONLY on the actual skills found in the CV
            - Use descriptive category names that reflect the content
            - Each category should have 2-10 related skills (minimum 2 skills per category)
            - Common category types (ONLY use if skills exist in CV):
              * ERP Systems (SAP modules, Oracle, Microsoft Dynamics, etc.)
              * Cloud & Infrastructure (AWS, Azure, GCP, cloud services)
              * DevOps & CI/CD Tools (Jenkins, Docker, Kubernetes, Ansible, etc.)
              * Databases & Data Management (SQL Server, Oracle, MySQL, MongoDB, SAP HANA, etc.)
              * Programming & Scripting (Python, Java, JavaScript, PowerShell, Bash, etc.)
              * Version Control (Git, GitHub, Bitbucket, SVN, etc.)
              * Operating Systems (Windows Server, Linux, Unix, etc.)
              * Monitoring & Analytics (Zabbix, Grafana, Splunk, etc.)
              * SAP Tools & Methodologies (Activate, FIORI, Solution Manager, SAP MII, etc.)
              * Integration & Middleware (MuleSoft, Dell Boomi, API Gateway, T.CON, etc.)
              * Other Technical Skills (any remaining skills that don't fit above categories)
            
            Example of CORRECT categorization (only categories with actual skills):
            ERP Systems: SAP S/4HANA, SAP PP, SAP QM, SAP PM, SAP FIORI, SAP MII, Oracle PP
            SAP Tools & Methodologies: Activate Methodology, Solution Manager, Data Migration
            Databases: SAP HANA, Oracle 11g
            Cloud & Infrastructure: SAP Cloud Platform, Microsoft Azure
            
            Example of WRONG format (DO NOT DO THIS):
            Programming & Scripting: None mentioned
            Version Control: Not found in CV
            Operating Systems: None
            
            OR (also WRONG - no categories):
            SAP S/4HANA
            SAP ECC 6.0
            Microsoft Azure
            
            CRITICAL: Only include categories that have at least 1 skill from the CV. Skip categories with no skills.
            2. Functional Skills: - Extract ALL soft skills, management skills, leadership skills, interpersonal skills, and professional competencies mentioned or demonstrated in the CV. Be thorough and comprehensive. Look for skills in responsibilities, achievements, and descriptions. Aim to identify at least 10-15 functional skills. Include skills like: Leadership, Project Management, Stakeholder Management, Communication, Problem Solving, Team Collaboration, Analytical Thinking, Strategic Planning, Change Management, Conflict Resolution, Time Management, Training & Mentoring, Business Analysis, etc.
            3. Industry Experience: - Extract ALL industries/sectors worked in or mentioned in the CV (e.g., Finance, Telecom, Banking, Healthcare, Manufacturing, Retail, etc.). Be comprehensive - look for industry mentions in work experience, projects, and context. Aim to identify at least 5-10 different industries or sectors. Include both specific industries (e.g., "Pharmaceuticals") and broader sectors (e.g., "Healthcare").
            
            RIGHT COLUMN ([RIGHT_COLUMN_START] to [RIGHT_COLUMN_END]):
            1. Summary: - Write ONE LONG comprehensive professional paragraph in FIRST PERSON, starting with "I am". CRITICAL LENGTH REQUIREMENT: The summary MUST be LONG and DETAILED - minimum 150 words, ideally 200-250 words (8-15 sentences). Create a comprehensive narrative that fully captures the professional's profile. The summary should cover ALL of these in detail: years of experience (specific number) and role/specialization, core technical expertise with all systems/modules/technologies (be comprehensive - list many), industries and sectors served (mention 5-8 industries), key achievements and project types with examples, business process expertise and domain knowledge, methodologies used (Agile, SAP Activate, SDLC, etc.), leadership and team collaboration, value delivered with metrics/impact, professional qualities and soft skills, and commitment to continuous learning. Write as if the person is confidently presenting their complete professional story in one substantive, flowing paragraph.
            2. Education/Qualifications/Certifications: - List ALL certifications, licenses, and training programs FIRST (one per bullet point with "- " prefix), then list ONLY THE MOST RECENT/HIGHEST educational qualification LAST. 
            
            CRITICAL EDUCATION FORMATTING:
            - Education MUST be on a SINGLE LINE with ALL information combined
            - Format: "Degree Name | Institution Name, Location | Year" (all on ONE line)
            - Alternative format: "Degree Name | Institution Name | Year" (if no location)
            - DO NOT split education into multiple lines
            - CORRECT: "- Bachelor of Technology in Information Technology | JNTU, Hyderabad | 2009"
            - WRONG: "- Bachelor of Technology in Information Technology | JNTU" followed by "- Hyderabad | 2009" on separate line
            - Example order: all certifications first, then education degree last (one line only).
            
            FULL WIDTH SECTION ([PROJECTS_EXPERIENCE]):
            Projects Experience - Convert work experience into project format:
            - Format option 1: "Job Title / Company Name | MM/YYYY – MM/YYYY | Location" (all on ONE line, use forward slash between role and company, en-dash for dates, include location ONLY if explicitly mentioned in CV)
            - Format option 2: "Job Title, Company Name, Location | MM/YYYY – MM/YYYY" (comma-separated format, include location in title line if present)
            - Dates can be in format "MM/YYYY - MM/YYYY" or "YYYY-PRESENT" or "MM/YYYY – MM/YYYY" (hyphen or en-dash both acceptable)
            - IMPORTANT: Only include location if it is explicitly mentioned in the CV. Do not infer or add location if it's not present.
            - Use format option 1 if location is separate, use format option 2 if location is part of the company line
            
            - CRITICAL FORMATTING: After the job title line, add individual bullet points (use "- " prefix) for EACH responsibility, one per line
            - DO NOT combine multiple responsibilities into a single "Technologies:" line
            - DO NOT put responsibilities as a comma-separated list
            - Each responsibility MUST be on its own line with "- " prefix
            
            - Then bullet points for key responsibilities and achievements (8-15 per project, focus on detailed explanations)
            - OPTIONAL BUT RECOMMENDED: If there are many responsibilities (8+ bullet points), you can categorize them into logical groups. Use category headers like:
              * "ETL Development:" / "Development & Implementation:"
              * "Project Management & Delivery:" / "Project Leadership:"
              * "Collaboration & Requirements Analysis:" / "Stakeholder Engagement:"
              * "Quality Assurance:" / "Testing & Validation:"
              * "Technical Leadership:" / "System Administration:"
              * "Support & Maintenance:" / "Production Support:"
              
              Format with categories (OPTIONAL):
              ETL Development:
              - Detailed responsibility 1 explaining what, how, why, and results
              - Detailed responsibility 2 with technical context and impact
              
              Project Management & Delivery:
              - Detailed responsibility 3 with comprehensive explanation
              - Detailed responsibility 4 with specific achievements
              
              OR simple format (if categories not needed):
              - Detailed responsibility 1
              - Detailed responsibility 2
              - Detailed responsibility 3
            
            - CRITICAL: Each responsibility should be VERY DETAILED, EXPLANATORY, and EXTREMELY LENGTHY. Write comprehensive, thorough descriptions that explain:
              * What was done (specific actions and tasks with concrete, detailed examples)
              * How it was done (methodologies, tools, approaches, processes, and step-by-step details)
              * Why it was done (business context, objectives, requirements, and business value)
              * Results and impact (outcomes, improvements, achievements, metrics, and quantifiable results)
              * Technical details and implementations (specific technologies, configurations, architectures, solutions)
              * Collaboration and team interactions (stakeholders, cross-functional work, team dynamics)
              * Process improvements and optimizations (efficiency gains, quality improvements, innovations)
              * Challenges faced and solutions implemented (problem-solving approaches)
              * Scale and scope (data volumes, system sizes, user counts, complexity levels)
              
              CRITICAL LENGTH REQUIREMENT: Each bullet point MUST be 4-8 sentences (60-120 words). Make them substantive, detailed, and comprehensive. Write as if explaining the work to someone who needs to fully understand the scope, complexity, and impact. Include specific examples, metrics, and technical details whenever possible. Avoid short, one-line descriptions. Be EXTREMELY descriptive and provide COMPLETE context with all relevant details.
              
              Example of CORRECT format WITH categories (NOTE THE LENGTH - 4-8 sentences per bullet):
              ETL Development:
              - Enhanced data integration capabilities by designing, developing, and implementing highly efficient ETL processes using Informatica PowerCenter 10.6, which enabled seamless bidirectional data flow from over 25 heterogeneous source systems including Oracle ERP, SAP S/4HANA, SQL Server databases, and cloud-based applications to enterprise-scale target data warehouses supporting 500+ concurrent users. The solution incorporated advanced data transformation logic, data quality rules, and real-time validation mechanisms to ensure 99.9% data accuracy and consistency across the entire enterprise ecosystem. Implemented comprehensive error handling and recovery procedures, automated monitoring and alerting systems, and detailed logging mechanisms to track data lineage and maintain full audit trails for regulatory compliance. This initiative reduced data processing time by 45% and manual intervention requirements by 70%, while supporting data volumes exceeding 2TB daily across multiple business units.
              - Developed and deployed over 150 complex mappings, 80+ reusable workflows, and 200+ sessions to meet aggressive project objectives and strict deadlines, incorporating sophisticated error handling mechanisms, data validation rules, business logic transformations, slowly changing dimension (SCD) implementations, and comprehensive exception management to maintain data quality, integrity, and consistency throughout the entire ETL pipeline. Worked closely with business analysts, data architects, and database administrators to understand complex business requirements, translate them into technical specifications, design optimal data flow architectures, and implement scalable solutions that could handle peak loads of 5 million records per hour. Conducted thorough unit testing, integration testing, and performance testing for each component, created detailed technical documentation including data mapping specifications and transformation rules, and provided knowledge transfer sessions to support teams to ensure smooth handover and ongoing maintenance.
              - Optimized ETL performance and system efficiency by conducting in-depth analysis to identify bottlenecks in existing ETL processes, analyzing execution logs and performance metrics, profiling slow-running workflows, and implementing comprehensive solutions including partition-based parallel processing, pushdown optimization to leverage database processing power, efficient join strategies, index optimization, and caching mechanisms. These performance enhancements resulted in a remarkable 40% reduction in overall processing time, 60% improvement in resource utilization, 30% decrease in infrastructure costs, and the ability to process end-of-month financial close activities within a 4-hour window instead of the previous 12-hour timeframe. Additionally, implemented proactive monitoring dashboards using custom scripts and third-party tools to continuously track performance metrics, identify potential issues before they impact production, and maintain service level agreements (SLAs) with 99.5% success rate.
              
              Project Management & Delivery:
              - Successfully led and executed the end-to-end migration of 200+ legacy ETL processes from outdated platforms to Informatica PowerCenter, managing a cross-functional team of 12 members including ETL developers, testers, and database administrators across multiple time zones. The migration initiative resulted in 50% increase in operational efficiency, 65% reduction in maintenance effort through standardized code practices, 35% decrease in system downtime, and annual cost savings of $500K through infrastructure consolidation and improved resource utilization. Developed comprehensive migration strategy and detailed project plan covering all phases including assessment, design, development, testing, and deployment, established clear governance processes and quality gates, conducted risk assessments and created mitigation plans, ensured zero data loss through careful data validation and reconciliation procedures, and maintained minimal business disruption by executing phased rollouts during planned maintenance windows. Coordinated extensively with business stakeholders to communicate progress, manage expectations, address concerns, and ensure alignment with strategic objectives throughout the 8-month migration program.
              - Maintained strict adherence to established coding standards, development best practices, and architectural guidelines while consistently delivering high-quality deliverables on time and within budget, achieving 98% on-time delivery rate across 50+ releases. Coordinated seamlessly with geographically distributed offshore development teams in India and onshore teams in the US, conducting daily stand-up meetings, weekly progress reviews, and monthly stakeholder presentations to ensure smooth execution of project milestones, effective communication across teams, and timely resolution of impediments. Implemented robust code review processes with peer reviews and senior architect sign-offs, established automated unit testing frameworks achieving 85% code coverage, created comprehensive technical documentation including design specifications and runbooks, and mentored 5 junior developers on ETL best practices and Informatica features. Successfully delivered 3 major releases and 15 minor enhancements while maintaining quality metrics with less than 2% defect rate in production.
              
              Technologies: Informatica PowerCenter 9.x, 10.6, Oracle 11g/12c, SQL Server 2016/2019, Unix Shell Scripting, Autosys, Control-M, HP Quality Center, JIRA
              
              Example of CORRECT format WITHOUT categories (NOTE THE LENGTH - 4-8 sentences per bullet):
              - Enhanced data integration capabilities by designing, developing, and implementing highly efficient ETL processes using Informatica PowerCenter 10.6, which enabled seamless bidirectional data flow from over 25 heterogeneous source systems to enterprise-scale target data warehouses supporting 500+ concurrent users, incorporating advanced data transformation logic and real-time validation mechanisms to ensure 99.9% data accuracy across the enterprise ecosystem. Implemented comprehensive error handling and recovery procedures with automated monitoring systems to track data lineage and maintain full audit trails, reducing data processing time by 45% and manual intervention by 70% while supporting data volumes exceeding 2TB daily across multiple business units.
              - Developed and deployed over 150 complex mappings, 80+ reusable workflows, and 200+ sessions to meet aggressive project objectives and strict deadlines, incorporating sophisticated error handling mechanisms, data validation rules, business logic transformations, and exception management to maintain data quality throughout the ETL pipeline. Worked closely with business analysts and data architects to translate complex business requirements into technical specifications, conducted thorough testing for each component, created detailed technical documentation, and provided knowledge transfer sessions to ensure smooth handover and ongoing maintenance.
              - Optimized ETL performance by conducting in-depth analysis to identify bottlenecks, analyzing execution logs, profiling slow-running workflows, and implementing comprehensive solutions including partition-based parallel processing, pushdown optimization, efficient join strategies, and caching mechanisms that resulted in 40% reduction in processing time, 60% improvement in resource utilization, and 30% decrease in infrastructure costs. Implemented proactive monitoring dashboards to continuously track performance metrics and maintain 99.5% SLA compliance.
              - Successfully led the end-to-end migration of 200+ legacy ETL processes to Informatica PowerCenter, managing a cross-functional team of 12 members across multiple time zones and achieving 50% increase in operational efficiency, 65% reduction in maintenance effort, and annual cost savings of $500K through infrastructure consolidation. Developed comprehensive migration strategy with detailed project plans, established quality gates, conducted risk assessments, ensured zero data loss through careful validation, and maintained minimal business disruption through phased rollouts during maintenance windows.
              Technologies: Informatica PowerCenter 9.x, 10.6, Oracle 11g/12c, SQL Server 2016/2019, Unix Shell Scripting
              
              Example of WRONG format (DO NOT DO THIS):
              Technologies: - Installed, configured Informatica. Conducted parameter movements. Created user folders. Informatica 9x, Oracle 11g
              
            - ONLY if technologies/tools are mentioned separately, add them as a final line: "Technologies: Tech1, Tech2, Tech3" (comma-separated)
            - Technologies should ONLY include tools, software versions, platforms - NOT responsibilities
            - For each role, extract and format as separate bullet points:
              * Key achievements with metrics/numbers when possible
              * Technical implementations and solutions
              * Team leadership or collaboration activities
              * Process improvements or optimizations
              * Project outcomes and business impact
              * Detailed explanations of daily tasks and responsibilities
              * Context and background for each responsibility
            
            EXACT OUTPUT STRUCTURE (copy this format exactly):
            [HEADER]
            Full Name | Job Title
            
            [LEFT_COLUMN_START]
            Technical Skills: 
            Category Name 1: skill1, skill2, skill3
            Category Name 2: skill4, skill5, skill6
            Category Name 3: skill7, skill8
            (ONLY include categories with actual skills - DO NOT add empty categories)
            
            Functional Skills:
            - Project Management & Planning
            - Stakeholder Management & Communication
            - Business Process Analysis & Re-engineering
            - Change Management & Implementation
            - Team Leadership & Mentoring
            - Problem Solving & Troubleshooting
            - Strategic Planning & Execution
            - Cross-functional Collaboration
            - Requirements Gathering & Documentation
            - Training & Knowledge Transfer
            - Analytical Thinking & Decision Making
            - Time Management & Prioritization
            - Conflict Resolution & Negotiation
            - Quality Assurance & Compliance
            - Continuous Improvement & Innovation
            (Generate 15-20 functional skills minimum - be thorough)
            
            Industry Experience:
            - Pharmaceuticals & Healthcare
            - Textiles & Manufacturing
            - Plastics & Molding
            - BOPET Film & Process Industry
            - Chemicals & Process Industry
            - Consumer Goods & Retail
            - Food & Beverage
            - Rubber & Tyre
            - Automotive & Engineering
            - Technology & Innovation
            (Generate 10-15 industries minimum - GROUP related industries together using " & ")
            [LEFT_COLUMN_END]
            
            [RIGHT_COLUMN_START]
            Summary:
            [Write ONE LONG comprehensive professional paragraph in FIRST PERSON, starting with "I am". Write as if the person is presenting themselves. CRITICAL: Make this paragraph LONG and DETAILED - minimum 150 words, ideally 200-250 words (8-15 sentences). Cover: specific years of experience, role/specialization, extensive technical expertise (list many systems/modules/technologies), industries served (5-8), key achievements with examples, business process expertise, methodologies, leadership experience, value delivered with metrics, professional qualities, and commitment to growth. Create a comprehensive narrative that fully captures the professional profile. Do not use bullet points for summary - write one flowing, substantive paragraph.]
            
            Education/Qualifications/Certifications: (list ALL certifications FIRST, then education LAST)
            - Certification 1
            - Certification 2
            - Certification 3 (generate maximum number of certifications and trainings from CV)
            - Degree Name | Institution Name | Year (ONLY the most recent/highest degree - ONE entry only, placed LAST)
            [RIGHT_COLUMN_END]
            
            [PROJECTS_EXPERIENCE]
            Projects Experience (only if mentioned in the CV and generate maximum number of projects and experiences)
            
            Job Title / Company Name | MM/YYYY – MM/YYYY | Location (only if present)
            OR
            Job Title, Company Name, Location | MM/YYYY – MM/YYYY
            - Responsibility 1 ( with detailed explanation and context and bullet points)
            - Responsibility 2 ( with detailed explanation and context and bullet points)
            - Responsibility 3 ( with detailed explanation and context and bullet points)
            - Responsibility 4 ( with detailed explanation and context and bullet points)
            - Responsibility 5 ( with detailed explanation and context and bullet points)
            - Responsibility 6 ( with detailed explanation and context and bullet points)
            Technologies: Tech1, Tech2
            
            [Next project...]
            """,
            "modern": """
            Convert this CV into a modern format with:
            - Clean, professional layout
            - Emphasis on achievements with metrics
            - Skills section prominently displayed
            - Use action verbs and quantifiable results
            - Modern section ordering: Contact Info, Professional Summary, Skills, Experience, Education
            """,
            "traditional": """
            Convert this CV into a traditional format with:
            - Chronological format
            - Conservative styling
            - Standard section ordering: Contact Info, Objective/Summary, Experience, Education, Skills
            - Professional language
            - Suitable for corporate and government positions
            """,
            "academic": """
            Convert this CV into an academic format with:
            - Emphasis on publications, research, and academic achievements
            - Detailed education section
            - Research experience highlighted
            - Publications, presentations, and grants sections
            - Professional associations and certifications
            """,
            "ats-friendly": """
            Convert this CV into an ATS-friendly format with:
            - Simple, clean formatting without complex tables or graphics
            - Standard section headers (Experience, Education, Skills)
            - Keyword optimization based on job descriptions
            - Chronological format
            - Standard fonts and formatting
            - No headers/footers or special characters
            """,
            "creative": """
            Convert this CV into a creative format with:
            - Bold design elements
            - Unique layout while maintaining readability
            - Emphasis on portfolio and creative projects
            - Visual hierarchy with creative section names
            - Suitable for design, marketing, and creative industries
            """
        }
        
        base_prompt = format_prompts.get(target_format, format_prompts["modern"])
        
        if additional_instructions:
            base_prompt += f"\n\nAdditional Instructions: {additional_instructions}"
        
        system_prompt = """You are an expert CV writer and formatter with exceptional attention to detail. Your task is to convert CVs into specific formats while:

1. Preserving ALL information - do not omit any experience, skills, education, or achievements
2. Maintaining 100% accuracy of dates, job titles, company names, qualifications, and contact information
3. Following the EXACT format structure with precise section markers
4. Using professional language and proper grammar
5. Ensuring complete information extraction from the source CV

CRITICAL REQUIREMENTS:
- Use EXACT section markers as specified: [HEADER], [LEFT_COLUMN_START], [LEFT_COLUMN_END], [RIGHT_COLUMN_START], [RIGHT_COLUMN_END], [PROJECTS_EXPERIENCE]
- Section headers must match EXACTLY (case-sensitive): "Technical Skills:", "Functional Skills:", "Industry Experience:", "Summary:", "Education/Qualifications/Certifications:"
- Use "- " (dash and space) for ALL bullet points
- Dates must be in format: "MM/YYYY – MM/YYYY" or "MM/YYYY – Present"
- Do NOT add any extra formatting, markdown, or special characters beyond what is specified
- Extract and include ALL skills, experiences, and achievements from the source CV"""

        user_prompt = f"""
        {base_prompt}
        
        Original CV Content:
        {cv_data.get('full_text', cv_data.get('raw_text', ''))}
        
        Please convert this CV according to the format requirements above. Maintain all key information while reformatting it appropriately.
        """
        
        try:
            # Initialize client if not already done
            if not self.client:
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY environment variable is not set")
                self.client = OpenAI(api_key=api_key)
                # Update model if it was set via env
                # Recommended models (best to good):
                # 1. "gpt-4o" - Best: fastest, most accurate, cost-effective (RECOMMENDED)
                # 2. "gpt-4o-2024-08-06" - More consistent results (dated version)
                # 3. "gpt-4-turbo" - Previous generation, still excellent
                # 4. "gpt-4o-mini" - Budget option: faster, cheaper, slightly less accurate
                self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Lower temperature for more consistent and accurate formatting
                max_tokens=16000,  # Significantly increased for very detailed, lengthy CVs (gpt-4o supports up to 16,384 output tokens)
                top_p=0.95,  # Nucleus sampling for better quality
                frequency_penalty=0.1,  # Reduce repetition
                presence_penalty=0.1  # Encourage diverse content
            )
            
            converted_cv = response.choices[0].message.content.strip()
            
            # Log response statistics for debugging
            finish_reason = response.choices[0].finish_reason
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 'unknown'
            logger.info(f"CV generation completed. Finish reason: {finish_reason}, Tokens used: {tokens_used}, Response length: {len(converted_cv)} chars")
            
            if finish_reason == 'length':
                logger.warning("⚠️ Response was truncated due to max_tokens limit. Consider increasing max_tokens or simplifying the CV.")
            
            return converted_cv
        
        except Exception as e:
            raise Exception(f"LLM conversion failed: {str(e)}")
    
    async def improve_text(
        self,
        text: str,
        instruction: str,
        section_type: str = "general"
    ) -> str:
        """
        Improve or enhance text using LLM
        """
        try:
            # Initialize client if not already done
            if not self.client:
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY environment variable is not set")
                self.client = OpenAI(api_key=api_key)
                self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
            
            # Determine output format based on section type
            format_instructions = ""
            if section_type == "technical_skills":
                format_instructions = """
CRITICAL OUTPUT FORMAT REQUIREMENTS:
- Return skills grouped by categories, format: "Category Name: skill1, skill2, skill3"
- NO markdown formatting (no **, no #, no bullets)
- NO descriptions or explanations
- One category per line with comma-separated skills within each category
- ALWAYS group skills into categories - NEVER list skills without categories
- ONLY create categories when there are ACTUAL skills to list in that category
- DO NOT create empty categories or categories with "None mentioned"
- DO NOT create categories if no skills exist for that category
- Create categories based ONLY on the actual skills found in the input text
- Use descriptive category names that reflect the content
- Each category should have 2-10 related skills (minimum 2 skills per category)
- Common category types (ONLY use if skills exist in input):
  * ERP Systems (SAP modules, Oracle, Microsoft Dynamics, etc.)
  * Cloud & Infrastructure (AWS, Azure, GCP, cloud services)
  * DevOps & CI/CD Tools (Jenkins, Docker, Kubernetes, Ansible, etc.)
  * Databases & Data Management (SQL Server, Oracle, MySQL, MongoDB, SAP HANA, etc.)
  * Programming & Scripting (Python, Java, JavaScript, PowerShell, Bash, etc.)
  * Version Control (Git, GitHub, Bitbucket, SVN, etc.)
  * Operating Systems (Windows Server, Linux, Unix, etc.)
  * Monitoring & Analytics (Zabbix, Grafana, Splunk, etc.)
  * SAP Tools & Methodologies (Activate, FIORI, Solution Manager, SAP MII, etc.)
  * Integration & Middleware (MuleSoft, Dell Boomi, API Gateway, T.CON, etc.)
  * Data Integration Tools (Informatica, Talend, SSIS, etc.)
  * Other Technical Skills (any remaining skills that don't fit above categories)

Example of CORRECT format (only categories with actual skills):
ERP Systems: SAP S/4HANA, SAP PP, SAP QM, SAP PM, SAP FIORI, SAP MII, Oracle PP
SAP Tools & Methodologies: Activate Methodology, Solution Manager
Databases: SAP HANA, Oracle 11g
Cloud & Infrastructure: SAP Cloud Platform

Example of WRONG format (DO NOT DO THIS):
Programming & Scripting: None mentioned
Version Control: Not found
Operating Systems: None

OR (also WRONG - no categories):
SAP S/4HANA
SAP ECC 6.0

CRITICAL: Only include categories that have at least 1 skill from the input. Skip categories with no skills."""
            elif section_type == "industry_experience":
                format_instructions = """
CRITICAL: Return ONLY a simple list format, one industry per line. Do NOT use markdown or formatting.

GROUPING RULES:
- GROUP related or complementary industries together using " & " (space-ampersand-space)
- Combine industries that are typically related or often work together
- Each line should contain either a single industry OR a group of 2-3 related industries

Example format:
Banking & Financial Services
Insurance & Risk Management
Defense & Government
Pharmaceuticals & Healthcare
Textiles & Manufacturing
Food & Beverage
Rubber & Tyre
Logistics & Supply Chain
Enterprise Content Management
Data Warehousing & Data Integration

Return just the industry names (grouped where appropriate), one per line, nothing else."""
            elif section_type == "functional_skills":
                format_instructions = """
CRITICAL: Return ONLY a simple list format, one skill per line. Do NOT use markdown, bold text, or descriptions.

GROUPING RULES:
- GROUP related or complementary skills together using " & " (space-ampersand-space)
- Combine skills that are typically related or naturally go together
- Each line should contain either a single skill OR a group of 2-3 related skills

Example format:
Project Management & Planning
Stakeholder Management & Communication
Business Process Analysis & Re-engineering
Change Management & Implementation
Team Leadership & Mentoring
Problem Solving & Troubleshooting
Strategic Planning & Execution
Requirements Gathering & Documentation
Training & Knowledge Transfer
Quality Assurance & Compliance
Time Management & Prioritization
Conflict Resolution & Negotiation
Analytical Thinking & Decision Making
Continuous Improvement & Innovation

Return just the skill names (grouped where appropriate), one per line, nothing else."""
            elif section_type == "certifications":
                format_instructions = """
CRITICAL: Return ONLY a simple list format, one certification per line. Do NOT use markdown or formatting.
Example format:
Microsoft Azure Administrator Associate
Microsoft Azure Solutions Architect Expert
Cisco Certified Network Associate (CCNA)

Return just the certification names, one per line, nothing else."""
            elif section_type == "education":
                format_instructions = """
CRITICAL: Return ONLY a simple list format, one education entry per line. 
Format as "Degree Name | Institution Name | Year" (if year available) OR "Degree Name | Institution Name" (if no year).

IMPORTANT FORMATTING RULES:
- Always use pipe (|) to separate Degree, Institution, and Year
- Include full degree name (e.g., "Bachelor of Science in Computer Science", "Master of Business Administration")
- Include institution name exactly as written in original CV
- Include graduation year if available (4-digit year like 2016, 2020)
- If multiple degrees, list each on a separate line
- Do NOT use bullets, dashes, or other markers

Example format:
Bachelor of Science in Computer Science | Mohammad Ali Jinnah University | 2016
Master of Business Administration | Karachi University | 2020
Bachelor of Engineering | Institution Name

Return just the education entries, one per line, nothing else."""
            elif section_type == "summary":
                format_instructions = """
CRITICAL: Return ONLY ONE LONG comprehensive paragraph in FIRST PERSON, starting with "I am". Write as if the person is presenting themselves.

LENGTH REQUIREMENT: The paragraph MUST be LONG and DETAILED - minimum 150 words, ideally 200-250 words (8-15 sentences). This is CRITICAL.

Do NOT use markdown, bullet points, or formatting.

Return a single, well-structured, LENGTHY paragraph that comprehensively covers ALL of these elements:
- Specific years of experience and role/specialization
- Extensive technical expertise: list many systems, modules, technologies, platforms (be comprehensive)
- Industries and sectors served: mention 5-8 different industries
- Key achievements and project types with specific examples
- Business process expertise and domain knowledge depth
- Methodologies and frameworks used (Agile, SAP Activate, SDLC, etc.)
- Leadership experience and team collaboration details
- Value delivered: metrics, efficiency gains, cost savings, quality improvements
- Professional qualities and soft skills demonstrated
- Commitment to continuous learning and professional growth

Example structure (note the LENGTH): "I am a highly motivated and results-driven [specific role] with [X] years of extensive hands-on experience in [list 4-5 specific technical areas/systems]. Throughout my professional journey, I have successfully delivered [number/types] of complex projects across diverse industries including [industry 1], [industry 2], [industry 3], [industry 4], [industry 5], and [industry 6], where I have consistently demonstrated [achievements with metrics]. I specialize in [specialization 1], [specialization 2], and [specialization 3], with deep expertise in [list many technical skills/tools/technologies]. My professional expertise extends to [additional areas], and I am proficient in [methodologies]. I have led and collaborated with cross-functional teams of [details], working closely with [stakeholders] to [outcomes]. I take pride in my ability to [value propositions], having achieved [specific results]. With a proven track record of [accomplishments], I bring [unique qualities]. I am deeply committed to [commitment] and strive to [goals]."

No formatting, just one comprehensive, LONG paragraph in first person. Make it substantive and detailed - aim for 200+ words."""
            
            system_prompt = f"""You are an expert CV writer and editor. Your task is to improve and enhance CV content for the {section_type} section while:
1. Preserving all important information
2. Making the text more professional and impactful
3. Improving clarity and conciseness
4. Using industry-standard terminology
5. Maintaining accuracy of all facts, dates, and names

CRITICAL OUTPUT REQUIREMENTS:
- Return ONLY plain text
- NO markdown formatting (no **, no #, no -, no bullets)
- NO category headers or labels
- NO descriptions or explanations
- Just the content itself in the specified format

{format_instructions}"""

            user_prompt = f"""{instruction}

Original content:
{text}

IMPORTANT: Return ONLY the improved content in the specified format. Do NOT use any markdown, bold text, bullet points, or category headers. Return clean, simple text that can be directly pasted into a form field.

Example of WRONG format:
**Technical Skills**
- **Category:** Description with technologies

Example of CORRECT format:
Microsoft Azure
AWS
Terraform
Docker"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=8000  # Increased for detailed, lengthy descriptions and comprehensive content
            )
            
            improved_text = response.choices[0].message.content.strip()
            
            # Log response statistics for debugging
            finish_reason = response.choices[0].finish_reason
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 'unknown'
            logger.info(f"Text improvement completed ({section_type}). Finish reason: {finish_reason}, Tokens used: {tokens_used}, Response length: {len(improved_text)} chars")
            
            if finish_reason == 'length':
                logger.warning(f"⚠️ Text improvement for {section_type} was truncated due to max_tokens limit. Consider increasing max_tokens.")
            
            # Clean up any markdown that might still be present
            improved_text = self._clean_markdown(improved_text, section_type)
            
            return improved_text
        
        except Exception as e:
            raise Exception(f"Text improvement failed: {str(e)}")
    
    def _clean_markdown(self, text: str, section_type: str) -> str:
        """Remove markdown formatting and extract skills from descriptions"""
        import re
        
        # Remove markdown headers
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        # Remove bold markers
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        
        # For technical_skills, preserve category format
        if section_type == "technical_skills":
            lines = text.split('\n')
            cleaned_items = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Remove markdown bullet points
                line = re.sub(r'^[-•*▪]\s*', '', line)
                
                # Check if line has category format (contains colon)
                if ':' in line:
                    # Check if it's a category with skills or a description
                    parts = line.split(':', 1)
                    category = parts[0].strip()
                    content = parts[1].strip() if len(parts) > 1 else ""
                    
                    # If content after colon is short and comma-separated, it's category format - preserve it
                    if content and len(content) < 200 and (',' in content or len(content.split()) < 20):
                        # This is category format: "Category: skill1, skill2, skill3"
                        cleaned_items.append(line)
                    elif len(line) > 50:
                        # This is a categorized description - extract skills from it
                        # Handle categorized descriptions like "Cloud & Infrastructure Management: Proficient in Microsoft Azure..."
                        category_part = line.split(':', 1)[0].strip()
                        description = line.split(':', 1)[1].strip() if ':' in line else ""
                        
                        # Extract individual skills/technologies from description
                        # Common patterns to extract
                        tech_patterns = [
                            r'\bMicrosoft Azure\b',
                            r'\bAzure\b',
                            r'\bAWS\b',
                            r'\bEC2\b',
                            r'\bS3\b',
                            r'\bRDS\b',
                            r'\bLambda\b',
                            r'\bTerraform\b',
                            r'\bCloudFormation\b',
                            r'\bInfrastructure as Code\b',
                            r'\bLinux\b',
                            r'\bUnix\b',
                            r'\bWindows\b',
                            r'\bAzure DevOps\b',
                            r'\bAzure DevOps Pipelines\b',
                            r'\bJenkins\b',
                            r'\bGitHub Actions\b',
                            r'\bBitbucket Pipelines\b',
                            r'\bAnsible\b',
                            r'\bDocker\b',
                            r'\bKubernetes\b',
                            r'\bGit\b',
                            r'\bGitHub\b',
                            r'\bBitbucket\b',
                            r'\bBash\b',
                            r'\bPowerShell\b',
                            r'\bSQL Server\b',
                            r'\bMySQL\b',
                            r'\bZabbix\b',
                            r'\bAgile\b',
                            r'\bScrum\b',
                            r'\bEDW Development Lifecycle\b',
                            r'\bProject Management\b',
                            r'\bStakeholder Management\b',
                            r'\bProject Commercials\b',
                            r'\bData Architecture\b',
                            r'\bData Quality\b',
                            r'\bData Visualization\b',
                            r'\bData Governance\b'
                        ]
                        
                        # Extract mentioned technologies from description
                        found_techs = []
                        for pattern in tech_patterns:
                            matches = re.findall(pattern, description, re.IGNORECASE)
                            for match in matches:
                                if isinstance(match, tuple):
                                    match = match[0] if match[0] else match[1] if len(match) > 1 else None
                                if match and match not in found_techs:
                                    found_techs.append(match)
                        
                        # Extract from "including X, Y, and Z" patterns
                        including_pattern = r'(?:including|such as|like)\s+([A-Z][^,]+(?:,\s*(?:and\s+)?[A-Z][^,]+)*)'
                        including_matches = re.findall(including_pattern, description, re.IGNORECASE)
                        for match in including_matches:
                            # Split by comma and "and"
                            items = re.split(r',\s*(?:and\s+)?', match)
                            for item in items:
                                item = item.strip().rstrip('.')
                                if item and len(item) < 100:
                                    found_techs.append(item)
                        
                        # Extract from parenthetical mentions like "(EC2, S3, RDS, Lambda)"
                        paren_pattern = r'\(([A-Z][^)]+(?:,\s*[A-Z][^)]+)*)\)'
                        paren_matches = re.findall(paren_pattern, description)
                        for match in paren_matches:
                            items = re.split(r',\s*', match)
                            for item in items:
                                item = item.strip()
                                if item and len(item) < 50:
                                    found_techs.append(item)
                        
                        # Add all found technologies - format as category
                        if found_techs:
                            # Group into category format: "Category: skill1, skill2, skill3"
                            skills_str = ', '.join([tech.strip() for tech in found_techs if tech.strip()])
                            if category_part and skills_str:
                                cleaned_items.append(f"{category_part}: {skills_str}")
                            else:
                                # Fallback: preserve the line as-is if it has category format
                                cleaned_items.append(line)
                        else:
                            # Fallback: preserve the line as-is if it has category format
                            cleaned_items.append(line)
                    else:
                        # Simple line with category format, preserve it
                        cleaned_items.append(line)
                else:
                    # Line without colon - might be a skill without category, keep it
                    if line and len(line) > 3:
                        cleaned_items.append(line)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_items = []
            for item in cleaned_items:
                item_lower = item.lower().strip()
                if item_lower and item_lower not in seen:
                    seen.add(item_lower)
                    unique_items.append(item.strip())
            
            text = '\n'.join(unique_items)
        else:
            # For other sections (summary, etc.), just remove markdown
            # Remove markdown headers
            text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
            # Remove bold markers
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
            text = re.sub(r'\*([^*]+)\*', r'\1', text)
            # Remove bullet points (for summary, keep paragraphs)
            if section_type != "summary":
                text = re.sub(r'^[-•*]\s*', '', text, flags=re.MULTILINE)
        
        return text.strip()

