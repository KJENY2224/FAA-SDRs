"""
FAA Service Difficulty Reports (SDRs) Web Scraper

This script scrapes the FAA SDR database (https://sdrs.faa.gov/Query.aspx)
searching for reports mentioning: Odor, Fume, Sulfur, Dirty Sock, Dirty Smell, or Decontamination

Output: CSV file with extracted report data
"""

import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('faa_sdr_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Keywords to search for
KEYWORDS = ['Odor', 'Fume', 'Sulfur', 'Dirty Sock', 'Dirty Smell', 'Decontamination']
FAA_URL = 'https://sdrs.faa.gov/Query.aspx'
OUTPUT_FILE = 'faa_sdr_results.csv'

class FAAScraper:
    def __init__(self):
        self.driver = None
        self.reports = set()  # Using set to avoid duplicates
        self.all_data = []
        
    def setup_driver(self):
        """Initialize Chrome WebDriver"""
        try:
            chrome_options = Options()
            # Uncomment the line below to run in headless mode (no visible browser)
            # chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def navigate_to_site(self):
        """Navigate to FAA SDR website"""
        try:
            self.driver.get(FAA_URL)
            logger.info(f"Navigated to {FAA_URL}")
            time.sleep(3)  # Allow page to fully load
        except Exception as e:
            logger.error(f"Failed to navigate to FAA website: {e}")
            raise
    
    def search_keyword(self, keyword):
        """Search for a specific keyword on the FAA website"""
        try:
            logger.info(f"Searching for keyword: {keyword}")
            
            # Wait for search input field to be present
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_txtSearch"))
            )
            
            # Clear previous search and enter new keyword
            search_input.clear()
            search_input.send_keys(keyword)
            logger.info(f"Entered keyword '{keyword}' in search field")
            
            # Find and click search button
            search_button = self.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btnSearch")
            search_button.click()
            logger.info(f"Clicked search button for '{keyword}'")
            
            # Wait for results to load
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error searching for keyword '{keyword}': {e}")
    
    def extract_results(self, keyword):
        """Extract report data from search results"""
        try:
            # Wait for results table to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "GridViewStyle"))
            )
            
            # Parse HTML content
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find results table
            table = soup.find('table', {'class': 'GridViewStyle'})
            
            if not table:
                logger.warning(f"No results table found for keyword '{keyword}'")
                return 0
            
            rows = table.find_all('tr')[1:]  # Skip header row
            count = 0
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    try:
                        report_number = cols[0].text.strip()
                        date = cols[1].text.strip()
                        aircraft_type = cols[2].text.strip()
                        description = cols[3].text.strip() if len(cols) > 3 else ""
                        
                        # Use report number as unique identifier
                        if report_number not in self.reports:
                            self.reports.add(report_number)
                            self.all_data.append({
                                'Report Number': report_number,
                                'Date': date,
                                'Aircraft Type': aircraft_type,
                                'Description': description,
                                'Keyword Searched': keyword,
                                'Scraped Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            })
                            count += 1
                    except Exception as e:
                        logger.warning(f"Error parsing row: {e}")
                        continue
            
            logger.info(f"Extracted {count} new reports for keyword '{keyword}'")
            return count
        
        except Exception as e:
            logger.error(f"Error extracting results for keyword '{keyword}': {e}")
            return 0
    
    def scrape_all_keywords(self):
        """Scrape all keywords"""
        total_reports = 0
        
        for keyword in KEYWORDS:
            try:
                self.search_keyword(keyword)
                count = self.extract_results(keyword)
                total_reports += count
                
                # Respectful delay between searches
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error processing keyword '{keyword}': {e}")
                continue
        
        logger.info(f"Total unique reports found: {total_reports}")
        return total_reports
    
    def save_to_csv(self):
        """Save collected data to CSV file"""
        try:
            if not self.all_data:
                logger.warning("No data to save")
                return False
            
            df = pd.DataFrame(self.all_data)
            df.to_csv(OUTPUT_FILE, index=False)
            logger.info(f"Data successfully saved to {OUTPUT_FILE}")
            logger.info(f"Total records: {len(df)}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            return False
    
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")
    
    def run(self):
        """Execute the scraping process"""
        try:
            logger.info("=" * 60)
            logger.info("FAA SDR Web Scraper Starting")
            logger.info("=" * 60)
            
            self.setup_driver()
            self.navigate_to_site()
            self.scrape_all_keywords()
            self.save_to_csv()
            
            logger.info("=" * 60)
            logger.info("FAA SDR Web Scraper Completed Successfully")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Fatal error during scraping: {e}")
            raise
        
        finally:
            self.close_driver()

def main():
    """Main entry point"""
    scraper = FAAScraper()
    scraper.run()

if __name__ == "__main__":
    main()
