from driver_setup import setup_driver
from whatsapp_actions import monitor_and_forward

if __name__ == "__main__":
    source = "Data main docs"
    target = "Data main docs Teams"
    
    driver = setup_driver()
    
    try:
        monitor_and_forward(driver, source, target)
    except Exception as e:
        print(f"❌ Critical failure: {e}")
    finally:
        driver.quit()
        print("🛑 Session ended")
