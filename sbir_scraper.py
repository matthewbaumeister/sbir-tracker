import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrape_sbir_topics():
    """
    Scrape SBIR/STTR topics using Selenium
    """
    url = "https://www.dodsbirsttr.mil/topics-app/"
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Comment out for debugging
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        logger.info(f"Opening {url}")
        driver.get(url)
        driver.maximize_window()
        
        # Wait for page to load
        logger.info("Waiting for page to load...")
        time.sleep(10)  # Initial wait for React app to load
        
        # Take screenshot for debugging
        driver.save_screenshot('debug_screenshot.png')
        
        # Try to find and click on "Active Topics" or similar filter
        logger.info("Looking for active topics filter...")
        
        filter_clicked = False
        filter_selectors = [
            "//button[contains(text(), 'Active')]",
            "//span[contains(text(), 'Active')]",
            "//label[contains(text(), 'Active')]",
            "//input[@type='checkbox' and @value='active']",
            "//div[contains(@class, 'filter')]//span[contains(text(), 'Active')]"
        ]
        
        for selector in filter_selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                if element:
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(1)
                    element.click()
                    filter_clicked = True
                    logger.info(f"Clicked filter: {selector}")
                    time.sleep(3)
                    break
            except:
                continue
        
        # Method 1: Try to select all data if there's a transpose/select all option
        logger.info("Looking for data selection options...")
        
        try:
            # Look for transpose or select all buttons
            select_all_selectors = [
                "//button[contains(text(), 'Select All')]",
                "//button[contains(text(), 'Transpose')]",
                "//button[contains(@class, 'select-all')]",
                "//input[@type='checkbox' and contains(@class, 'select-all')]"
            ]
            
            for selector in select_all_selectors:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    element.click()
                    logger.info(f"Clicked: {selector}")
                    time.sleep(2)
                except:
                    continue
        except:
            pass
        
        # Method 2: Scroll to load all data
        logger.info("Starting scroll process...")
        
        # Find scrollable container
        scroll_script = """
        function findScrollContainer() {
            const elements = document.querySelectorAll('*');
            for (let el of elements) {
                const style = window.getComputedStyle(el);
                if ((style.overflowY === 'auto' || style.overflowY === 'scroll') && 
                    el.scrollHeight > el.clientHeight) {
                    return el;
                }
            }
            return document.documentElement;
        }
        return findScrollContainer();
        """
        
        scroll_container = driver.execute_script(scroll_script)
        
        # Perform scrolling
        last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
        scroll_count = 0
        max_scrolls = 50
        
        while scroll_count < max_scrolls:
            # Scroll down
            if scroll_container == driver.find_element(By.TAG_NAME, "html"):
                driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            else:
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
            
            # Wait for new content
            time.sleep(2)
            
            # Check if new content loaded
            new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
            
            if new_height == last_height:
                logger.info("No new content loaded")
                break
                
            last_height = new_height
            scroll_count += 1
            logger.info(f"Scroll {scroll_count}: Height = {new_height}")
        
        # Extract data
        logger.info("Extracting data...")
        
        # Method 1: Try to find table data
        topics_data = []
        
        # Common selectors for data rows
        row_selectors = [
            "//tr[position()>1]",  # Table rows excluding header
            "//div[@role='row']",  # ARIA grid rows
            "//div[contains(@class, 'topic')]",
            "//div[contains(@class, 'row') and contains(@class, 'data')]",
            "//article",
            "//div[contains(@class, 'MuiDataGrid-row')]",
            "//div[contains(@class, 'ag-row')]"
        ]
        
        for selector in row_selectors:
            try:
                rows = driver.find_elements(By.XPATH, selector)
                if rows:
                    logger.info(f"Found {len(rows)} rows with selector: {selector}")
                    
                    for row in rows:
                        try:
                            text = row.text.strip()
                            if text and len(text) > 10:
                                topics_data.append(text)
                        except:
                            continue
                    
                    if topics_data:
                        break
            except:
                continue
        
        # If no structured data found, get all text content
        if not topics_data:
            logger.info("No structured data found, extracting all text...")
            
            # Get all text from the page body
            body_text = driver.find_element(By.TAG_NAME, "body").text
            lines = [line.strip() for line in body_text.split('\n') if line.strip()]
            
            # Filter out navigation/header elements
            topics_data = []
            for line in lines:
                # Look for patterns that indicate topic data
                if any(pattern in line for pattern in ['AF', 'N', 'A', 'DHA', 'CBD', 'MDA', 'SOCOM', 'DARPA']) and '-' in line:
                    topics_data.append(line)
                elif len(line) > 20 and not any(skip in line.lower() for skip in ['menu', 'login', 'search', 'filter']):
                    topics_data.append(line)
        
        # Process the extracted data
        if topics_data:
            logger.info(f"Processing {len(topics_data)} items...")
            
            # Parse into structured format
            parsed_topics = []
            current_topic = {}
            
            for item in topics_data:
                # Check if this is a topic number
                if any(agency in item for agency in ['AF', 'N', 'A', 'DHA', 'CBD', 'MDA']) and '-' in item and any(c.isdigit() for c in item):
                    if current_topic:
                        parsed_topics.append(current_topic)
                    
                    # Extract topic number
                    topic_parts = item.split()
                    topic_num = None
                    for part in topic_parts:
                        if '-' in part and any(c.isdigit() for c in part):
                            topic_num = part
                            break
                    
                    current_topic = {
                        'Topic Number': topic_num or item.split()[0],
                        'Full Text': item
                    }
                    
                    # Try to extract title (usually after topic number)
                    remaining_text = item.replace(topic_num or '', '').strip() if topic_num else item
                    if remaining_text:
                        current_topic['Title'] = remaining_text
                        
                elif current_topic:
                    # Add to current topic
                    current_topic['Full Text'] += '\n' + item
                    
                    # Try to extract structured fields
                    if ':' in item:
                        key, value = item.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if key and value and len(key) < 50:
                            current_topic[key] = value
            
            if current_topic:
                parsed_topics.append(current_topic)
            
            # Create DataFrame
            if parsed_topics:
                df = pd.DataFrame(parsed_topics)
            else:
                # Fallback: just save raw data
                df = pd.DataFrame(topics_data, columns=['Raw Content'])
            
            # Add metadata
            df['scrape_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            df['source_url'] = url
            
            # Save to CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'active_sbir_topics_{timestamp}.csv'
            df.to_csv(filename, index=False)
            df.to_csv('active_sbir_topics.csv', index=False)
            
            logger.info(f"Successfully saved {len(df)} topics to {filename}")
            
            # Print summary
            print(f"\nScraping completed successfully!")
            print(f"Total topics found: {len(df)}")
            print(f"Columns: {', '.join(df.columns.tolist())}")
            print(f"\nFirst 5 entries:")
            print(df.head())
            
            return df
            
        else:
            raise Exception("No data could be extracted from the page")
            
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        
        # Save page source for debugging
        with open('debug_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info("Saved page source to debug_page_source.html")
        
        raise
        
    finally:
        driver.quit()

def main():
    """
    Main function
    """
    try:
        df = scrape_sbir_topics()
        return df
    except Exception as e:
        logger.error(f"Scraper failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
