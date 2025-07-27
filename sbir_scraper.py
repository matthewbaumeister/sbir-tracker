import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def scrape_sbir_topics():
    """
    Scrape active SBIR/STTR topics from the DoD SBIR/STTR Topics App
    """
    url = "https://www.dodsbirsttr.mil/topics-app/"
    
    async with async_playwright() as p:
        logger.info("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until='networkidle')
            
            # Wait for the table to load - adjust selector as needed
            logger.info("Waiting for topics table to load...")
            await page.wait_for_selector('table', timeout=30000)
            
            # Additional wait to ensure dynamic content is loaded
            await page.wait_for_timeout(5000)
            
            # Extract the table HTML
            logger.info("Extracting table data...")
            table_html = await page.evaluate("""
                () => {
                    const table = document.querySelector('table');
                    return table ? table.outerHTML : null;
                }
            """)
            
            if not table_html:
                raise Exception("No table found on the page")
            
            # Parse the table with pandas
            df_list = pd.read_html(table_html)
            
            if not df_list:
                raise Exception("No data extracted from table")
            
            # Take the first table (adjust if there are multiple tables)
            df = df_list[0]
            
            # Add scrape timestamp
            df['scrape_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'active_sbir_topics_{timestamp}.csv'
            
            # Save to CSV
            df.to_csv(filename, index=False)
            logger.info(f"Saved {len(df)} topics to {filename}")
            
            # Also save as latest version
            df.to_csv('active_sbir_topics.csv', index=False)
            logger.info("Saved latest version as active_sbir_topics.csv")
            
            # Print summary
            logger.info(f"Successfully scraped {len(df)} active topics")
            logger.info(f"Columns: {', '.join(df.columns.tolist())}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            raise
        finally:
            await browser.close()

def main():
    """
    Main function to run the scraper
    """
    try:
        # Run the async scraper
        df = asyncio.run(scrape_sbir_topics())
        
        # Print first few rows for verification
        print("\nFirst 5 topics:")
        print(df.head().to_string())
        
        print(f"\nTotal topics scraped: {len(df)}")
        
    except Exception as e:
        logger.error(f"Scraper failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
