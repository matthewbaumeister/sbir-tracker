import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from datetime import datetime
import logging
import json
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def scrape_sbir_topics():
    """
    Scrape active SBIR/STTR topics from the DoD SBIR/STTR Topics App
    Handles lazy loading by scrolling to load all 31 topics
    """
    url = "https://www.dodsbirsttr.mil/topics-app/"
    
    async with async_playwright() as p:
        logger.info("Launching browser...")
        browser = await p.chromium.launch(
            headless=True,  # Set to False for debugging
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        try:
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until='networkidle', timeout=60000)
            
            # Wait for the table to load
            logger.info("Waiting for topics table to load...")
            await page.wait_for_timeout(5000)
            
            # Look for the topic count in the header
            topic_count_text = await page.text_content('text=/Number of Topics:/')
            if topic_count_text:
                total_topics = int(re.search(r'Number of Topics:\s*(\d+)', topic_count_text).group(1))
                logger.info(f"Total topics to load: {total_topics}")
            else:
                total_topics = 50  # Default max if we can't find the count
            
            # Scroll to load all topics
            logger.info("Scrolling to load all topics...")
            previous_count = 0
            scroll_attempts = 0
            max_scroll_attempts = 20
            
            while scroll_attempts < max_scroll_attempts:
                # Count current visible topics
                # Look for topic rows - they have the pattern A254-XXX
                topic_elements = await page.query_selector_all('text=/A254-\\d{3}/')
                current_count = len(topic_elements)
                
                logger.info(f"Currently loaded: {current_count} topics")
                
                # If we've loaded all topics or no new topics loaded, stop
                if current_count >= total_topics or current_count == previous_count:
                    logger.info(f"All topics loaded: {current_count}")
                    break
                
                previous_count = current_count
                
                # Scroll to bottom of the page
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                
                # Wait for new content to load
                await page.wait_for_timeout(2000)
                
                scroll_attempts += 1
            
            # Extract the table data
            logger.info("Extracting topic data...")
            
            # Get all rows from the table
            topics_data = await page.evaluate('''
                () => {
                    const topics = [];
                    
                    // Find all rows in the table
                    // First, try to find the table container
                    const rows = document.querySelectorAll('tr, [role="row"], div[class*="row"]');
                    
                    rows.forEach(row => {
                        const text = row.innerText || row.textContent || '';
                        
                        // Check if this row contains a topic number (A254-XXX pattern)
                        if (text.includes('A254-') && text.length > 20) {
                            // Split the row text by tabs or multiple spaces
                            const parts = text.split(/\\t+|\\s{2,}/);
                            
                            // Clean up the parts
                            const cleanParts = parts.map(p => p.trim()).filter(p => p.length > 0);
                            
                            if (cleanParts.length >= 4) {
                                const topic = {
                                    'Topic_Number': cleanParts[0],
                                    'Title': cleanParts[1],
                                    'Open_Date': cleanParts[2],
                                    'Close_Date': cleanParts[3]
                                };
                                
                                // Add status if present
                                if (cleanParts.length > 4) {
                                    topic['Status'] = cleanParts[4];
                                }
                                
                                topics.push(topic);
                            }
                        }
                    });
                    
                    // If no structured data found, try getting all topic numbers and their rows
                    if (topics.length === 0) {
                        // Find all elements containing A254-XXX
                        const topicElements = Array.from(document.querySelectorAll('*')).filter(el => {
                            const text = el.textContent || '';
                            return /A254-\\d{3}/.test(text) && el.children.length === 0;
                        });
                        
                        topicElements.forEach(el => {
                            let row = el;
                            // Find the parent row element
                            while (row && !row.matches('tr, [role="row"], div[class*="row"]')) {
                                row = row.parentElement;
                            }
                            
                            if (row) {
                                const rowText = row.innerText || row.textContent || '';
                                const parts = rowText.split(/\\t+|\\s{2,}/).map(p => p.trim()).filter(p => p);
                                
                                if (parts.length >= 2) {
                                    topics.push({
                                        'Topic_Number': parts[0],
                                        'Title': parts[1],
                                        'Open_Date': parts[2] || '',
                                        'Close_Date': parts[3] || '',
                                        'Status': parts[4] || 'Open'
                                    });
                                }
                            }
                        });
                    }
                    
                    return topics;
                }
            ''')
            
            if not topics_data or len(topics_data) == 0:
                # Fallback: Get all text content and parse it
                logger.info("Trying fallback extraction method...")
                
                all_text = await page.evaluate('() => document.body.innerText')
                lines = all_text.split('\n')
                
                topics_data = []
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    # Look for topic number pattern
                    if re.match(r'A254-\d{3}', line):
                        topic = {'Topic_Number': line}
                        
                        # Next line should be title
                        if i + 1 < len(lines):
                            topic['Title'] = lines[i + 1].strip()
                        
                        # Look for dates in next few lines
                        for j in range(i + 2, min(i + 5, len(lines))):
                            if '/' in lines[j]:  # Likely a date
                                if 'Open_Date' not in topic:
                                    topic['Open_Date'] = lines[j].strip()
                                elif 'Close_Date' not in topic:
                                    topic['Close_Date'] = lines[j].strip()
                        
                        # Look for Open/Closed status
                        for j in range(i, min(i + 6, len(lines))):
                            if lines[j].strip() in ['Open', 'Closed']:
                                topic['Status'] = lines[j].strip()
                                break
                        
                        if 'Status' not in topic:
                            topic['Status'] = 'Open'  # Default
                        
                        topics_data.append(topic)
                        i += 5  # Skip past this topic
                    else:
                        i += 1
            
            # Create DataFrame
            if topics_data:
                df = pd.DataFrame(topics_data)
                
                # Add metadata
                df['scrape_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                df['source_url'] = url
                
                # Ensure we have all expected columns
                expected_columns = ['Topic_Number', 'Title', 'Open_Date', 'Close_Date', 'Status']
                for col in expected_columns:
                    if col not in df.columns:
                        df[col] = ''
                
                # Reorder columns
                column_order = ['Topic_Number', 'Title', 'Open_Date', 'Close_Date', 'Status', 'scrape_timestamp', 'source_url']
                df = df[column_order]
                
                # Save to CSV
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'active_sbir_topics_{timestamp}.csv'
                df.to_csv(filename, index=False)
                df.to_csv('active_sbir_topics.csv', index=False)
                
                logger.info(f"Successfully saved {len(df)} topics")
                logger.info(f"Columns: {', '.join(df.columns.tolist())}")
                
                # Print summary
                print(f"\n{'='*60}")
                print(f"SCRAPING COMPLETED SUCCESSFULLY")
                print(f"{'='*60}")
                print(f"Total topics scraped: {len(df)}")
                print(f"File saved as: {filename}")
                print(f"\nFirst 5 topics:")
                print(df[['Topic_Number', 'Title', 'Status']].head().to_string())
                print(f"{'='*60}\n")
                
                return df
            else:
                raise Exception("No topics could be extracted from the page")
                
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            
            # Save screenshot for debugging
            await page.screenshot(path='error_screenshot.png')
            logger.info("Saved error screenshot to error_screenshot.png")
            
            # Save page content
            content = await page.content()
            with open('error_page_content.html', 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("Saved page content to error_page_content.html")
            
            raise
            
        finally:
            await browser.close()

def main():
    """
    Main function to run the scraper
    """
    try:
        df = asyncio.run(scrape_sbir_topics())
        return df
    except Exception as e:
        logger.error(f"Scraper failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
