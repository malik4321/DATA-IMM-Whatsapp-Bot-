import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def setup_driver():
    chrome_path = os.path.join(os.getcwd(), 'chromedriver.exe')
    options = Options()
    options.add_experimental_option("detach", True)
    service = Service(chrome_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://web.whatsapp.com")
    input("📷 Scan the QR code and press Enter to continue...")
    print("🚀 Bot initialized successfully!")
    return driver
