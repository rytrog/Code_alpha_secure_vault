# SentinelX - AI-Powered Cloud Secure Data Vault & SQL Injection Defense Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Deployment: Render](https://img.shields.io/badge/Deploy-Render-success.svg)](https://render.com/)

**SentinelX** is an advanced, enterprise-grade cloud secure data vault and SQL injection defense platform designed to protect sensitive information while monitoring real-time database threats. The application is built using a modern, unified tech stack featuring a Python FastAPI backend, a clean Google Cloud Console-inspired HTML/CSS/JS frontend, and a secure SQLite database.

> [!IMPORTANT]
> **Administrative Oversight & Threat Operations Center:** Unlike typical credential vaults that are solely for personal/user storage, SentinelX is designed as a fully-monitored, administrator-controlled security platform. System administrators have complete system authority to oversee user registrations, manage/promote/demote user roles, disable/enable accounts, override configurations, track real-time SQL injection threats, and chat with a Virtual CISO assistant.

At its core, SentinelX acts as a virtual Security Operations Center (SOC). It utilizes custom request-filtering middleware that intercepts incoming transactions, checks for dangerous SQL payloads (such as quote-escaping, comment termination, and time-based delays), blocks malicious actors, and computes a dynamic security score. Security events are instantly logged and aggregated on an administrative dashboard, which auto-refreshes every three seconds for real-time threat telemetry.

Furthermore, SentinelX includes a cryptographically secure vault that encrypts user credentials locally in memory using AES-256 (CBC mode) before database persistence. Admins can view, search, and decrypt credentials, including secure image uploads encoded in Base64.

To assist security teams, SentinelX integrates a conversational Virtual CISO assistant powered by the Groq Cloud AI API using the `llama-3.3-70b` model. This assistant maintains chat history memory and provides detailed breakdowns of blocked attack vectors, risk metrics, and mitigation checklists. It intelligently distinguishes between general inquiries and direct log requests, delivering targeted threat intelligence. SentinelX combines encryption, detection, and conversational AI into a unified platform ready for single-service cloud hosting.

---

## 🚀 Live Demo & Deployment

The application is deployed on Render at:  
👉 **[https://code-alpha-secure-vault.onrender.com](https://code-alpha-secure-vault.onrender.com)**

*(Note: Visiting the GitHub Pages site at this repository's address will automatically redirect you to this live Render link).*

---

## 👤 General User Workflow (Vault Guide)

Standard users have direct access to their private, secure credential vault where they can store passwords, API keys, documents, and images safely.

### Step 1: Account Creation
1. Navigate to the application home page.
2. Click **Sign Up** on the login card.
3. Choose a unique username, enter your email, and create a strong password (minimum 8 characters).
4. Click **Create Account** to register.

### Step 2: Logging In
1. Enter your registered credentials on the login screen.
2. Click **Login**. You will be authenticated and redirected directly to your **Secure Document Vault** page.

### Step 3: Storing Text Credentials
1. Under **Add Secure Record**, enter a **Title** (e.g. `My AWS Access Key`).
2. Set the **Category** to `Password`, `API Key`, `Secure Note`, `Document`, `Banking`, or `Credential`.
3. Type your sensitive data into the **Sensitive Data** field.
4. Click **Encrypt & Store**. The data is immediately encrypted in transit and stored in the database.

### Step 4: Hiding and Encrypting Images (New Feature)
1. Set the **Category** to **Secure Image**.
2. The text area will automatically collapse, and an image file selector will appear.
3. Choose any image file (PNG, JPG, up to 2MB).
4. Click **Encrypt & Store**. The image is read as a Base64 stream, encrypted using AES-256, and saved securely.

### Step 5: Viewing and Decrypting Records
1. In your **Encrypted Vault** grid, select your item.
2. Click **View**:
   - For text records: The decrypted secret text is revealed.
   - For images: The encrypted Base64 stream is decrypted in-memory and renders as a private thumbnail preview.
3. Click **Copy** (for text items) to copy it to your clipboard.
4. Click **View** again to re-mask (re-encrypt) the record.

---

## 👑 System Administrator Guide & Controls

SentinelX operates under administrative control, ensuring the system administrator has complete authority over the entire platform. Standard user vault operations are supervised, and system integrity is continually monitored.

### Admin Credentials
- **Username**: `admin`
- **Password**: `Admin@SentinelX2026`

### Administrative Capabilities & Override Controls
- **Identity Control Panel**: Full access to promote standard users to administrative status, demote admins, reset user passwords, disable compromised accounts, or permanently delete accounts (which cascades to purge their vault items).
- **Live Security Operations Center**: Track total traffic volume, inspect blocked intrusion vectors, monitor failed/successful authentication logs, and read real-time platform security scores updated every 3 seconds.
- **Virtual CISO threat Analyst**: Engage with the AI Security Assistant powered by Groq (Llama-3) or Gemini, asking direct questions about security logs, intrusion history, or general recommendations.
- **Intrusion Logs & AI Explainer**: Analyze SQL injection payloads, and get detailed AI-generated threat explanations and remediation checklists.

---

## 🛠️ Local Development Setup

### Prerequisites
- Python 3.11.x
- Groq Cloud API Key (set in `backend/.env`)

### Option 1: Manual Run
```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Run backend (starts API on port 8000 and serves static frontend)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

### Option 2: Docker Compose
```bash
# Run from the root directory
docker-compose up --build -d
```
Open **[http://localhost:8000](http://localhost:8000)**.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
