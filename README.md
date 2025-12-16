🎯 Career Cortex - AI-Powered Job Intelligence System

An intelligent job matching system that scrapes job listings, extracts structured data using AI, and matches candidates with opportunities based on their skills.

🚀 What It Does

Career Cortex transforms the job search process by:

- Scraping job listings automatically from remote.com
- Extracting structured data (company, location, skills, seniority) from messy job descriptions using AI
- Matching your skills against job requirements with percentage scores
- Identifying exactly which skills you're missing for each role

Stop wasting time on jobs you're only 30-40% qualified for. Get brutally honest feedback about your chances.

✨ Features

Current Features
- ✅ Automated web scraping from remote.com with customizable filters
- ✅ AI-powered extraction using Ollama + LLaMA 3 (8B model)
- ✅ Smart skill matching algorithm (0-100% scores)
- ✅ Skill gap analysis - see exactly what you're missing
- ✅ MySQL database for structured storage
- ✅ Duplicate job detection

🛠️ Tech Stack

- Python 3.8+
- Selenium - Web scraping
- BeautifulSoup4 - HTML parsing
- MySQL - Database
- Ollama + LLaMA 3 - AI extraction
- Streamlit - Frontend (coming soon)

📋 Prerequisites

Before you begin, ensure you have:

1. Python 3.8 or higher installed
2. MySQL Server running locally
3. Ollama installed ([Download here](https://ollama.ai))
4. Chrome Browser (for Selenium)
5. ChromeDriver compatible with your Chrome version

🔧 Installation

1. Clone the Repository
```bash
git clone https://github.com/IBM07/HireWire.git
cd HireWire
```

2. Install Python Dependencies
```bash
pip install selenium beautifulsoup4 mysql-connector-python ollama
```

3. Set Up MySQL Database

Create a database and table:

```sql
CREATE DATABASE job_agent;

USE job_agent;

CREATE TABLE job_openings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    search_query VARCHAR(255),
    job_url VARCHAR(500) UNIQUE,
    job_title VARCHAR(255),
    raw_description LONGTEXT,
    company VARCHAR(255),
    location_scraped VARCHAR(255),
    is_remote BOOLEAN,
    job_type VARCHAR(100),
    seniority VARCHAR(100),
    required_skills JSON,
    is_extracted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

4. Configure Database Connection

Update the database credentials in all three Python files:

```python
db = mysql.connector.connect(
    host="127.0.0.1",
    user="your_username",      # Change this
    password="your_password",  # Change this
    database="job_agent"
)
```

5. Install Ollama and Pull LLaMA 3

```bash
# Install Ollama from https://ollama.ai

# Pull the LLaMA 3 model (8B version)
ollama pull llama3:8b
```

🚀 Usage

Step 1: Scrape Jobs

Run the scraper to collect job listings:

```bash
python job_agent.py
```

You'll be prompted for:
- Job title (e.g., "data analyst")
- Country code (e.g., "USA", "IND")
- Employment types (full_time, part_time, contractor)
- Workplace locations (remote, hybrid, on_site)
- Seniority levels (entry_level, mid_level, senior, etc.)

Example interaction:
```
Enter job title: python developer
Enter 3-letter country code: USA
Enter employment types: full_time, contractor
Enter workplace locations: remote
Enter seniority levels: mid_level, senior
```

Step 2: Extract Structured Data

Process the scraped jobs with AI:

```bash
python extractor.py
```

This will:
- Read raw job descriptions from the database
- Use Ollama/LLaMA 3 to extract structured data
- Update the database with parsed information
- Mark jobs as processed

Step 3: Find Your Matches

Search for jobs matching your skills:

```bash
python agent.py
```

Example:
```
Enter your skills: python, docker, aws, sql
```

Output:
```
--- Your Smart Job Matches ---

Score: 92%
Title: Senior Backend Engineer
Company: TechCorp
Skills Gap: kubernetes
URL: https://remote.com/jobs/...
--------------------

Score: 75%
Title: DevOps Engineer
Company: StartupXYZ
Skills Gap: terraform, jenkins
URL: https://remote.com/jobs/...
--------------------
```

📊 How It Works

1. Web Scraping (`job_agent.py`)
- Uses Selenium to navigate remote.com
- Applies user-defined filters (location, seniority, etc.)
- Extracts job titles, URLs, and full page text
- Stores raw data in MySQL

2. AI Extraction (`extractor.py`)
- Fetches unprocessed jobs from database
- Sends raw text to Ollama (LLaMA 3)
- Extracts structured fields:
  - Company name
  - Location
  - Remote status (boolean)
  - Job type (Full-time, Contract, etc.)
  - Seniority level
  - **Required skills** (normalized and sorted)
- Updates database with clean data

3. Smart Matching (`agent.py`)
- Takes user's skills as input
- Compares against each job's requirements
- Calculates match score: `(matching_skills / total_required) × 100`
- Lists missing skills for each job
- Sorts results by match percentage

🧠 AI Extraction Logic

The system uses a deterministic prompt (temperature=0.0) to ensure consistent extraction:

What it extracts:
- Company name
- Location (normalized format)
- Remote/hybrid/on-site status
- Employment type
- Seniority level
- Technical skills (canonicalized: "Postgres" → "PostgreSQL", "Power BI" → "PowerBI")

Normalization examples:
- "Google Analytics 4" → "GA4"
- "Amazon Web Services" → "AWS"
- "Big Query" → "BigQuery"

📁 Project Structure

```
HireWire/
├── job_agent.py      # Web scraper
├── extractor.py      # AI-powered data extraction
├── agent.py          # Job matching engine
└── README.md         # This file
```

⚙️ Configuration Options

Scraper Filters (job_agent.py)

Employment Types:
- `full_time`
- `part_time`
- `contractor`

Workplace Locations:
- `remote`
- `hybrid`
- `on_site`

Seniority Levels:
- `entry_level`
- `mid_level`
- `senior`
- `manager`
- `director`
- `executive`

AI Model (extractor.py)

Currently uses `llama3:8b`. You can change to other Ollama models:

```python
response = ollama.chat(
    model='llama3:8b',  # Change model here
    ...
)
```

🐛 Troubleshooting

Database Connection Error
```
❌ DATABASE ERROR: Access denied for user
```
Solution: Update MySQL credentials in all three Python files.

Ollama Not Running
```
❌ OLLAMA ERROR: Connection refused
```
Solution: Start Ollama service:
```bash
ollama serve
```

ChromeDriver Issues
```
selenium.common.exceptions.WebDriverException
```
Solution: Update ChromeDriver to match your Chrome version or use webdriver-manager:
```bash
pip install webdriver-manager
```

No Jobs Found
```
No processed jobs found in the database.
```
Solution: Run `job_agent.py` first to scrape jobs, then `extractor.py` to process them.

🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Ideas for contributions:
- Add support for more job boards (LinkedIn, Indeed, etc.)
- Improve skill extraction accuracy
- Add resume parsing
- Build the Streamlit frontend
- Add automated testing

👤 Author

Ibrahim
- GitHub: [@IBM07](https://github.com/IBM07)
- LinkedIn: [Connect with me](https://www.linkedin.com/in/mohammedibrahimaejaz/)

🌟 Show Your Support

If you find this project helpful, please give it a ⭐️!

Currently building the Streamlit frontend - follow for updates!


