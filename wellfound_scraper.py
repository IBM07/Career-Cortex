from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import mysql.connector
import re

# Configuration constants
WELLFOUND_URL = "https://wellfound.com/jobs"
SCROLL_PAUSE_TIME = 2
MAX_SCROLLS = 20  # Additional scrolls for Wellfound's slower loading

def get_db_connection():
    """Establish database connection for job storage"""
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Ibrahim@321",
        database="job_agent"
    )

def clean_wellfound_text(raw_text):
    """
    Remove Wellfound-specific navigation and UI elements from scraped text
    Returns clean job description content
    """
    # Wellfound page elements that aren't part of job descriptions
    site_noise = [
        "Wellfound",
        "Overview",
        "Jobs",
        "About us",
        "Reviews",
        "Recommended for you",
        "Apply now",
        "Save",
        "Share",
        "Recruiters from this company",
        "Browse by:",
        "Hiring now",
        "Login",
        "Sign Up"
    ]
    
    cleaned_text = raw_text
    for noise in site_noise:
        cleaned_text = cleaned_text.replace(noise, " ")
    
    # Normalize whitespace
    return " ".join(cleaned_text.split())

def scrape_wellfound():
    """
    Main function to scrape Wellfound job listings
    Requires manual login due to anti-bot protections
    """
    print("Starting Wellfound scraper...")

    # Browser configuration with anti-detection measures
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(options=options)
    
    # Manual login phase - Wellfound requires human interaction
    driver.get("https://wellfound.com/login")
    print("\n" + "=" * 50)
    print("Manual login required:")
    print("1. Log into Wellfound in the browser window")
    print("2. Solve any CAPTCHA challenges")
    print("3. Navigate to the Jobs page")
    print("4. Press ENTER here when ready to continue")
    print("=" * 50 + "\n")
    input("Press ENTER to continue...")

    # Reconnect to the active browser session after manual login
    try:
        window_handles = driver.window_handles
        if not window_handles:
            print("Error: Browser window not available")
            return

        # Switch to most recent window/tab
        driver.switch_to.window(window_handles[-1])
        print(f"Connected to browser window: {driver.title}")
        
    except Exception as connection_error:
        print(f"Browser connection error: {connection_error}")
        return

    # Scroll to load all available job listings
    print("Loading job listings via scrolling...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    for scroll_count in range(MAX_SCROLLS):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # Check for and click "Show more" button if present
        try:
            show_more_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Show more')]")
            if show_more_button:
                show_more_button.click()
                time.sleep(2)
        except:
            pass  # Button not found, continue with scrolling

        # Check if we've reached the bottom of the page
        if new_height == last_height:
            # Final scroll attempt to ensure all content is loaded
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight + 1000);")
            time.sleep(2)
            if driver.execute_script("return document.body.scrollHeight") == last_height:
                print("All content loaded")
                break
        
        last_height = new_height
        print(f"Scroll iteration {scroll_count + 1}/{MAX_SCROLLS}")

    # Extract job links from the loaded page
    print("Parsing job links from HTML...")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    job_links = []
    processed_urls = set()
    
    # Target job roles to scrape
    target_roles = ["engineer", "developer", "backend", "frontend", "full stack", "python", "ai", "machine learning", "data"]

    # Find and filter job links
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        
        # Filter for job URLs (contain /jobs/ path)
        if "/jobs/" not in href:
            continue
            
        # Convert relative URLs to absolute
        if href.startswith("http"):
            full_url = href
        else:
            full_url = f"https://wellfound.com{href}"
            
        # Remove query parameters and check for duplicates
        full_url = full_url.split('?')[0]
        if full_url in processed_urls:
            continue
        
        # Extract job title
        title = link.get_text(strip=True)
        if not title:
            continue
        
        # Filter by target roles
        title_lower = title.lower()
        if not any(role in title_lower for role in target_roles):
            continue

        processed_urls.add(full_url)
        job_links.append((title, full_url))

    print(f"Found {len(job_links)} valid job listings")

    # Process each job listing
    conn = get_db_connection()
    cursor = conn.cursor()

    for job_title, job_url in job_links:
        print(f"Processing: {job_title[:40]}...")
        
        try:
            # Navigate to individual job page
            driver.get(job_url)
            time.sleep(3)  # Wait for React components to render
            
            # Parse job description page
            desc_soup = BeautifulSoup(driver.page_source, "html.parser")
            
            if desc_soup.body:
                # Extract and clean job description text
                raw_text = desc_soup.body.get_text(separator=' ', strip=True)
                clean_text = clean_wellfound_text(raw_text)
                
                # Validate content length after cleaning
                if len(clean_text) < 500:
                    print("Content too short after cleaning - skipping")
                    continue

                # Save to database
                try:
                    insert_query = """
                    INSERT INTO job_openings 
                    (search_query, job_url, job_title, raw_description) 
                    VALUES (%s, %s, %s, %s)
                    """
                    values = ("Wellfound Scraper", job_url, job_title, clean_text)
                    cursor.execute(insert_query, values)
                    conn.commit()
                    print("Successfully saved to database")
                except mysql.connector.Error as db_error:
                    if db_error.errno == 1062:  # Handle duplicate entries
                        print("Duplicate entry - skipping")
                    else:
                        print(f"Database error: {db_error}")
            else:
                print("No page content available")

        except Exception as processing_error:
            print(f"Error processing {job_url}: {processing_error}")

    # Cleanup resources
    driver.quit()
    cursor.close()
    conn.close()
    print("Wellfound scraping completed")

if __name__ == "__main__":
    scrape_wellfound()
