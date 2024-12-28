# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from pymongo import MongoClient
# from time import sleep
# import time
# import uuid
# import requests

# client = MongoClient('MONGODB_URL')
# db = client['twitter_trends']
# collection = db['top_5_trends']

# # ProxyMesh setup
# proxy_mesh_url = 'http://pghuyqwr-rotate:z76m5o0a28lj@p.webshare.io:9999'

# # Unique ID
# unique_id = str(uuid.uuid4())

# # Twitter credentials
# username = 'twitter-username'
# password = 'twitter-password'

# def fetch_trending_topics():
#     # options = webdriver.ChromeOptions()
#     # options.add_argument('--proxy-server=%s' % proxy_mesh_url)
#     driver = webdriver.Chrome()
#     # driver.maximize_window()
    
#     driver.get("https://twitter.com/login")
    
#     # Login to Twitter
#     sleep(4)
#     driver.find_element(By.XPATH,"//input[@name='text']").send_keys(username)
#     driver.find_element(By.XPATH, "//span[contains(text(),'Next')]").click()

#     sleep(4)
#     driver.find_element(By.XPATH,"//input[@name='password']").send_keys(password)
#     driver.find_element(By.XPATH, "//span[contains(text(),'Log in')]").click()
    
#     sleep(4)
#     # Fetch trending topics    
#     driver.find_element(By.XPATH,"//*[@id='react-root']/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[4]/div/section/div/div/div[8]/div/a").click()
    
#     sleep(4)
#     trends = driver.find_elements(By.XPATH,"//span[@dir='ltr']")
#     top_5_trends = [trend.text for trend in trends[:5] if trend.text.strip()]

    
    
#     # Record the IP address used
#     ip_address = requests.get("http://api.ipify.org").text
    
#     # Record the date and time of the end of the Selenium script
#     end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    
#     # Insert into MongoDB
#     record = {
#         "_id": unique_id,
#         "trend1": top_5_trends[0],
#         "trend2": top_5_trends[1],
#         "trend3": top_5_trends[2],
#         "trend4": top_5_trends[3],
#         "trend5": top_5_trends[4],
#         "end_time": end_time,
#         "ip_address": ip_address
#     }
#     collection.insert_one(record)

#     driver.close()

# if __name__ == "__main__":
#     fetch_trending_topics()




#updated
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
from time import sleep
import time
import uuid
import requests

client = MongoClient('MONGODB_URL')
db = client['twitter_trends']
collection = db['top_5_trends']

unique_id = str(uuid.uuid4())

username = 'twitter-username'
password = 'twitter-password'


def wait_and_find_element(driver, by, value, timeout=40):
    """Wait for element to be visible and return it"""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, value))
    )

def scroll_to_bottom(driver):
    """Scroll to the bottom of the page to load all dynamic content"""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def fetch_trending_topics():
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 40)  
    
    try:
        print("Starting the scraping process...")
        
        driver.get("https://twitter.com/login")
        print("Navigated to Twitter login page")
        
        # Login to Twitter
        username_input = wait_and_find_element(driver, By.XPATH, "//input[@name='text']")
        username_input.send_keys(username)
        print("Entered username")
        
        next_button = wait_and_find_element(driver, By.XPATH, "//span[contains(text(),'Next')]")
        next_button.click()
        print("Clicked next button")
        
        password_input = wait_and_find_element(driver, By.XPATH, "//input[@name='password']")
        password_input.send_keys(password)
        print("Entered password")
        
        login_button = wait_and_find_element(driver, By.XPATH, "//span[contains(text(),'Log in')]")
        login_button.click()
        print("Clicked login button")
        
        # Wait after login for all dynamic content to load
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']")))  # Wait for main content to load
        
        print("Waited for page load")
        
        driver.get("https://twitter.com/explore")
        print("Navigated to Explore page")
        
        scroll_to_bottom(driver)
        
        # Wait for the trends to appear with a longer timeout
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Trending']")))
        
        trend_xpath = "//div[contains(@aria-label, 'Trending')]/ancestor::div[contains(@data-testid, 'trend')]//span[@dir='auto']"
        
        trends = wait.until(EC.presence_of_all_elements_located((By.XPATH, trend_xpath)))
        if not trends:
            raise Exception("Could not find any trending topics")
        
        # Extraction
        top_5_trends = []
        seen_trends = set()
        print("\nFound trends:")
        for trend in trends:
            try:
                trend_text = trend.text.strip()
                print(f"- {trend_text}")
                if trend_text and trend_text not in seen_trends:
                    top_5_trends.append(trend_text)
                    seen_trends.add(trend_text)
                    if len(top_5_trends) == 5:
                        break
            except Exception as e:
                print(f"Error extracting trend text: {str(e)}")
        
        print(f"\nCollected {len(top_5_trends)} unique trends")
        
        if len(top_5_trends) < 5:
            raise Exception(f"Only found {len(top_5_trends)} trends, needed 5")
        
        ip_address = requests.get("http://api.ipify.org").text
        end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        
        #in MongoDB
        record = {
            "_id": unique_id,
            "trend1": top_5_trends[0],
            "trend2": top_5_trends[1],
            "trend3": top_5_trends[2],
            "trend4": top_5_trends[3],
            "trend5": top_5_trends[4],
            "end_time": end_time,
            "ip_address": ip_address
        }
        collection.insert_one(record)
        print("Successfully saved trends to database")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        print("Closing browser")
        driver.quit()

if __name__ == "__main__":
    fetch_trending_topics()