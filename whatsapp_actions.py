import time
import random
import unicodedata
from hashlib import sha256
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

MIN_INTERVAL = 0.15
BASE_INTERVAL = 0.3
JITTER = 0.05
MAX_HISTORY = 500

def sanitize_text(text):
    return ''.join(c for c in text if unicodedata.category(c)[0] != 'C')

def get_message_hash(message):
    return sha256(message.encode('utf-8')).hexdigest()

def open_group(driver, group_name):
    print(f"\n🔍 Opening group: {group_name}")
    try:
        search_bar = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
        )
        search_bar.click()
        search_bar.send_keys(Keys.CONTROL + "a" + Keys.BACKSPACE)
        time.sleep(0.5 + random.random() / 2)

        sanitized_name = sanitize_text(group_name)
        for char in sanitized_name:
            search_bar.send_keys(char)
            time.sleep(0.05)

        time.sleep(1 + random.random())
        group = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[@title='{sanitized_name}']"))
        )
        group.click()
        print(f"✅ Successfully opened: {sanitized_name}")
        time.sleep(1 + random.random() / 2)
        return True

    except Exception as e:
        print(f"❌ Failed to open group: {e}")
        return False

def get_last_message(driver):
    try:
        messages = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@role='row']"))
        )
        if not messages:
            return None, None, None

        last_msg = messages[-1]
        sender, main_text, quoted_text = "Unknown", "", None

        try:
            sender_element = last_msg.find_element(By.XPATH, ".//span[contains(@class, 'copyable-text')][@dir='ltr']")
            sender = sender_element.get_attribute("title") or "Unknown"
        except:
            pass

        try:
            main_text_element = last_msg.find_element(
                By.XPATH, ".//span[contains(@class, 'selectable-text') and contains(@class, 'copyable-text')]/span"
            )
            main_text = main_text_element.text.strip()
        except:
            main_text = ""

        try:
            quoted_element = last_msg.find_element(By.XPATH, ".//span[contains(@class, 'quoted-mention')]")
            quoted_text = quoted_element.text.strip()
        except:
            quoted_text = None

        if main_text:
            print(f"📩 Message from {sender}: {main_text} | Reply to: {quoted_text or 'None'}")
            return sanitize_text(main_text), sender, sanitize_text(quoted_text) if quoted_text else None

        return None, None, None

    except Exception as e:
        print(f"❌ Error getting message: {e}")
        return None, None, None

def try_reply_to_quoted_message(driver, quoted_text):
    try:
        messages = driver.find_elements(By.XPATH, "//div[@role='row']")
        for msg in reversed(messages[-50:]):
            try:
                text_element = msg.find_element(By.XPATH, ".//span[contains(@class, 'selectable-text') and @dir='ltr']")
                if quoted_text.strip() == text_element.text.strip():
                    ActionChains(driver).move_to_element(msg).perform()
                    time.sleep(0.5)

                    menu_btn = msg.find_element(By.XPATH, ".//span[@data-icon='down-context']")
                    menu_btn.click()
                    time.sleep(0.5)

                    reply_option = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Reply']"))
                    )
                    reply_option.click()
                    print("✅ Reply initiated via dropdown.")
                    return True
            except:
                continue
    except Exception as e:
        print(f"⚠️ Quoted reply error: {e}")
    return False

def send_message(driver, message, quoted_text=None):
    try:
        message = sanitize_text(message)

        if quoted_text:
            if not try_reply_to_quoted_message(driver, quoted_text):
                print("⚠️ Could not match quoted message in target group.")

        input_box = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Type a message']"))
        )
        input_box.click()
        driver.execute_script("arguments[0].innerHTML = '';", input_box)
        time.sleep(0.2 + random.random() / 5)

        for char in message:
            input_box.send_keys(char)
            if random.random() < 0.1:
                time.sleep(0.02 + random.random() / 100)

        input_box.send_keys(Keys.RETURN)
        time.sleep(0.3)
        return True

    except Exception as e:
        print(f"❌ Send error: {e}")
        return False

def monitor_and_forward(driver, source_group, target_group):
    message_history = set()
    last_activity = time.time()
    active_mode = False

    if not open_group(driver, source_group):
        return

    last_msg, _, quoted = get_last_message(driver)
    if last_msg:
        message_history.add(get_message_hash(last_msg + (quoted or "")))

    print(f"\n🔍 Monitoring '{source_group}' → '{target_group}'")

    while True:
        try:
            loop_start = time.time()
            current_msg, sender, quoted = get_last_message(driver)

            if current_msg:
                msg_hash = get_message_hash(current_msg + (quoted or ""))
                if msg_hash not in message_history and sender != "You":
                    print(f"🔄 Forwarding message from {sender}...")

                    if open_group(driver, target_group) and send_message(driver, current_msg, quoted_text=quoted):
                        message_history.add(msg_hash)
                        if len(message_history) > MAX_HISTORY:
                            message_history.pop()
                        last_activity = time.time()
                        active_mode = True

                    open_group(driver, source_group)

            elapsed = time.time() - loop_start
            base_delay = MIN_INTERVAL if active_mode else BASE_INTERVAL
            jitter = (random.random() * 2 - 1) * JITTER
            time.sleep(max(MIN_INTERVAL, base_delay - elapsed + jitter))

            if active_mode and (time.time() - last_activity > 30):
                active_mode = False

        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
            break
        except Exception as e:
            print(f"⚠️ System error: {e}")
            time.sleep(5)
            open_group(driver, source_group)
