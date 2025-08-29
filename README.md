# Portscan

Portscan is a lightweight **web-based port scanner** that helps you identify exposed services on both local and external networks.  
Unlike traditional command-line scanners, it provides a clean web interface, real-time results, and exportable reports.  

---

## Features
- Scan any IP range and ports  
- Automatic banner grabbing (HTTP, MySQL, Redis, PostgreSQL, MongoDB, and more)  
- Real-time web interface with progress tracking  
- Export results as **CSV** or **JSONL** with filters (by service, by country)  
- Integrated SQLite database for history and session comparison  
- GeoIP enrichment (country, city, ASN, organization)  

---

## Requirements
- Python 3.10+  
- pip  
- geoip (`pip install geoip`)  

---

## Installation and Usage


# Clone the repository
git clone https://github.com/OfficialPapotti/portscan
cd portscan

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\Activate.ps1

# Install dependencies
pip install flask geoip

# Run the web application
python app.py

# Open your browser at:
# http://127.0.0.1:5000

# Example:
# Enter IP/range (192.168.0.0/24) and ports (80,443,3306)
# Results stored in portscan.db
# Export as CSV or JSONL with filters

---


##  Troubleshooting:

# If geoip not found
pip install geoip

# If port 5000 already in use
flask run --port 8001

# If no banners are shown:
# Some services require specific payloads, check payloads directory.

---

About this project
Portscan is a project I’m developing solo. Every bit of support helps me invest more time and energy into improving the tool.

My goal is to take Portscan beyond a simple port scanner and turn it into a complete solution with visual reports, robust databases, and features that make life easier for pentesters and sysadmins.

This project is personal to me because it started from the idea of turning technical knowledge into something practical and accessible.
Your support motivates me to keep releasing updates, improving features, and pushing the project forward.

## Support the project with Crypto:
BTC (BTC): 1HiKDjNoLLdSqFLR8c9R694RLC9R1V7EQQ
ETH  (ERC-20): 0xf05d5e3f21d763310ed65d9cab84d37730030e66
USDT (TRC-20): TPAqCWxDdibPDKpC1TqffaKR5oxommurcp
USDT (TON): UQArbX0DPYvkEUgF9e-0ReM0oDl10PtaJEoT1v56kZXZbBwd
