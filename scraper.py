from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from overall_state import OverallState

def scraping_router(state: OverallState) -> dict:
    websites = state.get("websites_to_search", [])
    query = state.get("messages", [])[-1].content
    pages_to_search = state.get("pages_to_search", 1)
    page_depth  = state.get("page_depth", 10)
    ui_container = state.get("ui_container")

    ieee_scraped_articles = {}
    springer_scraped_articles = {}
    mdpi_scraped_artciles = {}

    for website in websites:
        if website == "IEEE":
            ui_container.write("- Scraping IEEE articles...")
            ieee_scraped_articles = scrape_ieee(query, pages_to_search, page_depth, ui_container)
        elif website == "Springer":
            ui_container.write("- Scraping Springer articles...")
            springer_scraped_articles = scrape_springer(query, pages_to_search, page_depth, ui_container)
        elif website == "MDPI":
            ui_container.write("- Scraping MDPI articles...")
            mdpi_scraped_artciles = scrape_mdpi(query, pages_to_search, page_depth, ui_container)

    scraped_articles = {
        "IEEE": ieee_scraped_articles,
        "Springer": springer_scraped_articles,
        "MDPI": mdpi_scraped_artciles
    }

    return {
        "scraped_articles": scraped_articles
    }



def scrape_ieee(query, pages_to_search, page_depth, ui_container):
    """
    Scrapes IEEE Xplore for articles based on a query.

    Args:
        query (str): The search query.
        pages_to_search (int): The number of pages to scrape.

    Returns:
        dict: A dictionary of scraped articles with their links and content.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    wait = WebDriverWait(driver, 20)

    ieee_scraped_articles = {}
    query_encoded = query.replace(" ", "%20")

    for page_no in range(1, pages_to_search + 1):
        try:
            url = f"https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={query_encoded}&highlight=true&returnFacets=ALL&returnType=SEARCH&matchPubs=true&openAccess=true&pageNumber={page_no}"
            driver.get(url)

            elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h3 a.fw-bold")))
            
            links = [elem.get_attribute('href') for elem in elements if elem.get_attribute('href')]

            count = 0

            for link in links:
                if count == page_depth:
                    break
                try:
                    driver.get(link)
                    
                    article = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ArticlePage")))
                    paras = article.find_elements(By.TAG_NAME, "p")

                    new_title = driver.title
                    ui_container.write(f"Scraping {new_title}...")

                    doc_text = ""
                    for p in paras:
                        doc_text = doc_text + " " + p.text 
                    
                    if doc_text:
                        ieee_scraped_articles[new_title] = {
                            "link": link,
                            "content": doc_text
                        }

                    count += 1

                except Exception as e:
                    print(f"Could not process link: {link}. Error: {e}")
                    continue
        except Exception as e:
            print(f"Failed to scrape page {page_no}. Error: {e}")
            continue

    driver.quit()
    ui_container.write("- Scraping for IEEE complete...")
    return ieee_scraped_articles




def scrape_springer(query, pages_to_search, page_depth, ui_container):
    """
    Scrapes Springer Link for articles based on a query.

    Args:
        query (str): The search query.
        pages_to_search (int): The number of pages to scrape.

    Returns:
        dict: A dictionary of scraped articles with their links and content.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    wait = WebDriverWait(driver, 20)
    springer_scraped_articles = {}
    query_encoded = query.replace(" ", "+")

    for page_no in range(1, pages_to_search + 1):
        try:
            url = f"https://link.springer.com/search?query={query_encoded}&openAccess=true&sortBy=relevance&page={page_no}"
            print(f"Scraping page {page_no}: {url}")
            driver.get(url)
            
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-test="search-result-item"]')))
            elements = driver.find_elements(By.CSS_SELECTOR, 'h3[data-test="title"] a')
            
            links = [elem.get_attribute('href') for elem in elements if elem.get_attribute('href')]

            count = 0

            for link in links:
                if count == page_depth:
                    break
                try:
                    driver.get(link)
                    
                    article = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "main-content")))
                    paras = article.find_elements(By.TAG_NAME, "p")
                    
                    new_title = driver.title
                    ui_container.write(f"Scraping {new_title}...")

                    doc_text = " ".join([p.text for p in paras])
                    
                    if doc_text:
                        springer_scraped_articles[new_title] = {
                            "link": link,
                            "content": doc_text
                        }
                    
                    count += 1

                except Exception as e:
                    print(f"Could not process link: {link}. Error: {e}")
                    continue
        except Exception as e:
            print(f"Failed to scrape page {page_no}. Error: {e}")
            continue

    driver.quit()
    ui_container.write("- Scraping for Springer complete...")
    return springer_scraped_articles



def scrape_mdpi(query, pages_to_search, page_depth, ui_container):
    """
    Scrapes MDPI for articles based on a query using regular Selenium.

    Args:
        query (str): The search query.
        pages_to_search (int): The number of pages to scrape.

    Returns:
        dict: A dictionary of scraped articles with their links and content.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    wait = WebDriverWait(driver, 20)
    mdpi_scraped_articles = {}
    query_encoded = query.replace(" ", "+")

    for page_no in range(pages_to_search):
        try:
            url = f"https://www.mdpi.com/search?q={query_encoded}&page_no={page_no + 1}"
            driver.get(url)
            time.sleep(3)
            
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'article-listing')))
            elements = driver.find_elements(By.CLASS_NAME, 'title-link')
            
            links = [elem.get_attribute('href') for elem in elements if elem.get_attribute('href')]

            count = 0

            for link in links:
                if count == page_depth:
                    break
                try:
                    driver.get(link)
                    time.sleep(2)
                    new_title = driver.title
                    ui_container.write(f"Scraping {new_title}...")
                    doc_text = ""

                    article = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "html-article-content")))
                    paras = article.find_elements(By.CLASS_NAME, "html-p")
                    doc_text = " ".join([p.text for p in paras])


                    if doc_text:
                        mdpi_scraped_articles[new_title] = {
                            "link": link,
                            "content": doc_text
                        }

                    count += 1

                except Exception as e:
                    print(f"Could not process link: {link}. Error: {e}")
                    continue
        except Exception as e:
            print(f"Failed to scrape page {page_no}. Error: {e}")
            continue

    driver.quit()
    ui_container.write("- Scraping for MDPI complete...")
    return mdpi_scraped_articles