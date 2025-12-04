import mysql.connector
import ollama
import json

# Connecting to the Database!
try:
    db = mysql.connector.connect(
        host="127.0.0.1",
        user="root", 
        password="Ibrahim@321", 
        database="job_agent"
    )
    cursor = db.cursor(dictionary=True)
    print("✅ Database connected successfully.")
except mysql.connector.Error as err:
    print(f"❌ DATABASE ERROR: {err}")
    print("Please ensure MySQL is running and credentials are correct.")
    exit()

# Connecting to Ollama
try:
    ollama.list() # Test connection
    print("✅ Ollama connection successful.")
except Exception as e:
    print(f"❌ OLLAMA ERROR: {e}")
    print("Please ensure Ollama is running.")
    exit()

# --- EXTRACTION PROMPT (Updated to match your schema) ---
extraction_prompt = """
You are an expert job data extraction agent. Extract ONLY these fields from job postings and return a valid JSON object. Use the exact keys and rules below.

CRITICAL LOCATION EXTRACTION RULES:
- Search for ANY location mentions: cities (New York), countries (USA), states (California), regions (Europe)
- Look for patterns like "based in", "located in", "from [location]", "must be in [location]"
- If you see "Remote", "Work from Home", "Anywhere", "Global", set location_scraped = "Remote" AND is_remote = true
- If you see "Hybrid", set location_scraped to the actual location mentioned AND is_remote = true
- If multiple locations: use "Location1 + Location2" format
- Only use "Not specified" if absolutely no location clues exist

REMOTE STATUS DETECTION:
- is_remote = true if you see: "Remote", "Work from Home", "WFH", "Anywhere", "Global", "Virtual", "Telecommute"
- is_remote = true for "Hybrid" roles (partially remote)
- is_remote = false for on-site only roles with specific office locations

EXACT OUTPUT FORMAT (minified JSON, no extra text):
{
    "company": "string",
    "location_scraped": "string", 
    "is_remote": boolean,
    "job_type": "string",
    "seniority": "string",
    "required_skills": ["array", "of", "strings"]
}

FALLBACK VALUES:
- company: "Not specified" if no company name found
- location_scraped: "Not specified" if no location clues
- is_remote: false if no remote indicators
- job_type: "Full-time" (most common default)
- seniority: Infer from title/requirements: "Entry-level" (0-2y), "Mid-level" (3-5y), "Senior" (5+y)
- required_skills: [] empty array if none found

SKILL NORMALIZATION EXAMPLES:
- "Python programming" → "Python"
- "React.js" → "React"
- "Amazon Web Services" → "AWS"
- "Google Cloud Platform" → "GCP"
- "SQL database" → "SQL"
- "Docker containers" → "Docker"
- "Figma design" → "Figma"
- "Agile methodology" → "Agile"

STRICT EXAMPLES:
Input: "Join TechCorp as Senior Python Developer working remotely from anywhere. Must know AWS, Docker."
Output: {"company":"TechCorp","location_scraped":"Remote","is_remote":true,"job_type":"Full-time","seniority":"Senior","required_skills":["AWS","Docker","Python"]}

Input: "Python Developer needed in New York office. Requires 3+ years experience with React."
Output: {"company":"Not specified","location_scraped":"New York","is_remote":false,"job_type":"Full-time","seniority":"Mid-level","required_skills":["Python","React"]}

Return only the JSON object. No explanations.
"""

def extract_data(raw_text):
    """
    Uses Ollama to extract structured data from raw text.
    """
    try:
        response = ollama.chat(
            model='qwen2.5:14b',
            messages=[
                {'role': 'system', 'content': extraction_prompt},
                {'role': 'user', 'content': raw_text}
            ],
            options={'temperature': 0.0},
            format='json'
        )
        
        json_data_string = response['message']['content']
        data_dict = json.loads(json_data_string)
        return data_dict

    except Exception as e:
        print(f"❌ LLM EXTRACTION FAILED: {e}")
        return None

# --- MAIN PROCESSING LOOP (Fixed to match your schema) ---
def main():
    print("\nStarting extraction process...")
    
    # Find all jobs that have NOT been processed yet
    cursor.execute("SELECT id, raw_description FROM job_openings WHERE is_extracted = FALSE;")
    jobs_to_process = cursor.fetchall()
    
    if not jobs_to_process:
        print("No new jobs to process. Exiting.")
        return

    print(f"Found {len(jobs_to_process)} jobs to process.")
    
    for job in jobs_to_process:
        job_id = job["id"]
        raw_text = job['raw_description']
        
        print(f"\n--- Processing Job ID: {job_id} ---")
        
        # Get structured data from LLM
        structured_data = extract_data(raw_text)
        
        if structured_data:
            print(f"   Extracted: {structured_data}")
            
            # Update database with corrected column names
            # SIMPLER VERSION - Direct conversion
        try:
            skills_list = structured_data.get('required_skills', [])
            skills_json = json.dumps(skills_list)
            
            # Convert Python boolean to MySQL integer
            is_remote_int = 1 if structured_data.get('is_remote', False) else 0
            
            sql = """
            UPDATE job_openings 
            SET 
                company = %s,
                location_scraped = %s,
                is_remote = %s,
                job_type = %s,
                seniority = %s,
                required_skills = %s,
                is_extracted = TRUE
            WHERE id = %s
            """
            vals = (
                structured_data.get('company', 'Not specified'),
                structured_data.get('location_scraped', 'Not specified'),
                is_remote_int,  # Integer 1 or 0
                structured_data.get('job_type', 'Full-time'),
                structured_data.get('seniority', 'Not specified'),
                skills_json,
                job_id
            )
            
            cursor.execute(sql, vals)
            db.commit()
            print(f"✅ Job ID {job_id} updated.")
            
        except mysql.connector.Error as err:
            print(f"❌ DB UPDATE FAILED: {err}")
            db.rollback()

    cursor.close()
    db.close()
    print("✅ Database connection closed.")

if __name__ == "__main__":
    main()
