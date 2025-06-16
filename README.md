# 🤖 WhatsApp Group Chatbot Automation

This is a Python-based WhatsApp chatbot that uses Selenium to automate group message forwarding and quoted replies between WhatsApp groups through WhatsApp Web.

---

## 🚀 Features

- 🔁 **Auto-Forwards** new messages from a source group to a target group
- 💬 **Preserves Quoted Replies**: Matches the quoted message in the target group and replies with correct context
- 🧠 **Message Deduplication** using SHA256 hashing
- 👁️ Runs in **headless Chrome** to simulate real-user behaviour
- ⏱️ Checks for updates every few seconds, simulating near-real-time sync

---

## 🧰 Tech Stack

- **Python 3**
- **Selenium** (WebDriver for Chrome)
- **WhatsApp Web**
- `psycopg2` (optional if PostgreSQL logging is used)
- `cloudinary` (optional for media uploads)

---

## 🛠 Requirements

- Google Chrome installed
- ChromeDriver installed (match version to your Chrome)
- Python dependencies:

```bash
pip install selenium cloudinary requests


