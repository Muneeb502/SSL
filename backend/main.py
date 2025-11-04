# # backend/main.py
# from fastapi import FastAPI, HTTPException
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# import json
# import os

# from checker import check_ssl
# from datetime import datetime
# import logging
# logging.basicConfig(level=logging.INFO)
# log = logging.getLogger(__name__)

# app = FastAPI()

# DATA_DIR = os.path.dirname(__file__)
# DOMAINS_FILE = os.path.join(DATA_DIR, "domains.json")
# STATUS_FILE = os.path.join(DATA_DIR, "status.json")

# # Initialize files
# if not os.path.exists(DOMAINS_FILE):
#     with open(DOMAINS_FILE, "w") as f:
#         json.dump([], f)

# if not os.path.exists(STATUS_FILE):
#     with open(STATUS_FILE, "w") as f:
#         json.dump([], f)

# @app.get("/domains")
# def get_domains():
#     with open(DOMAINS_FILE, "r") as f:
#         return json.load(f)

# @app.post("/domains")
# def add_domain(domain: dict):
#     domain_name = domain.get("domain", "").strip()
#     if not domain_name:
#         raise HTTPException(400, "Domain required")
    
#     with open(DOMAINS_FILE, "r") as f:
#         domains = json.load(f)
    
#     if domain_name not in domains:
#         domains.append(domain_name)
#         with open(DOMAINS_FILE, "w") as f:
#             json.dump(domains, f, indent=2)
    
#     return {"message": "Added", "domain": domain_name}

# @app.post("/test-all")
# def test_all():
#     with open(DOMAINS_FILE, "r") as f:
#         domains = json.load(f)
    
#     results = []
#     for d in domains:
#         info = check_ssl(d)
#         results.append(info)
    
#     with open(STATUS_FILE, "w") as f:
#         json.dump(results, f, indent=2)
    
#     return results

# @app.post("/domains")
# def add_domain(domain: dict):
#     domain_name = domain.get("domain", "").strip().lower()
#     if not domain_name:
#         raise HTTPException(400, "Domain required")

#     # ---------- 1. Save to domains.json ----------
#     with open(DOMAINS_FILE, "r") as f:
#         domains = json.load(f)

#     added = False
#     if domain_name not in domains:
#         domains.append(domain_name)
#         with open(DOMAINS_FILE, "w") as f:
#             json.dump(domains, f, indent=2)
#         added = True
#         log.info(f"Domain added: {domain_name}")
#     else:
#         log.info(f"Domain already exists: {domain_name}")

#     # ---------- 2. Immediately check SSL ----------
#     result = check_ssl(domain_name)
#     log.info(f"SSL result for {domain_name}: {result['status']} ({result['days_remaining']} days)")

#     # ---------- 3. Load current status.json (robust) ----------
#     status_data = []
#     if os.path.exists(STATUS_FILE):
#         try:
#             with open(STATUS_FILE, "r") as f:
#                 raw = f.read().strip()
#                 if raw:                              # not empty
#                     status_data = json.loads(raw)
#         except json.JSONDecodeError as e:
#             log.error(f"Corrupted status.json – resetting. Error: {e}")
#             status_data = []                     # start fresh
#         except Exception as e:
#             log.error(f"Unexpected error reading status.json: {e}")
#             status_data = []

#     # Remove any previous entry for this domain
#     status_data = [d for d in status_data if d.get("domain") != domain_name]

#     # Append fresh result
#     status_data.append(result)

#     # ---------- 4. Write back status.json ----------
#     try:
#         with open(STATUS_FILE, "w") as f:
#             json.dump(status_data, f, indent=2)
#         log.info(f"status.json updated with {domain_name}")
#     except Exception as e:
#         log.error(f"Failed to write status.json: {e}")
#         raise HTTPException(500, "Failed to save status")

#     return {
#         "message": "Added & checked" if added else "Already exists – refreshed",
#         "result": result
#     }

# @app.get("/status")
# def get_status():
#     with open(STATUS_FILE, "r") as f:
#         return json.load(f)

# # Serve frontend
# app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")



""""
WITH FULL LOGS# 
"""

# backend/main.py
import os
import json
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from checker import check_ssl

# Enable detailed logs
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("SSL-MONITOR")

app = FastAPI()

BASE_DIR = os.path.dirname(__file__)
DOMAINS_FILE = os.path.join(BASE_DIR, "domains.json")
STATUS_FILE  = os.path.join(BASE_DIR, "status.json")

# Initialize files
for path, default in [(DOMAINS_FILE, []), (STATUS_FILE, [])]:
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f)
        log.info(f"Created file: {os.path.basename(path)}")

# Safe JSON loader
def load_json(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return []
    try:
        with open(path, "r") as f:
            data = json.load(f)
        log.info(f"Loaded {len(data)} items from {os.path.basename(path)}")
        return data
    except json.JSONDecodeError as e:
        log.error(f"Corrupted JSON in {path}: {e} → Resetting")
        return []
    except Exception as e:
        log.error(f"Failed to read {path}: {e}")
        return []

# Safe JSON saver
def save_json(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        log.info(f"Saved {len(data)} items to {os.path.basename(path)}")
    except Exception as e:
        log.error(f"Failed to save {path}: {e}")
        raise

# GET: List domains
@app.get("/api/domains")
def get_domains():
    data = load_json(DOMAINS_FILE)
    return data

# POST: Add domain + check SSL
@app.post("/api/domains")
def add_domain(domain: dict):
    domain_name = domain.get("domain", "").strip().lower()
    if not domain_name:
        log.warning("Add domain failed: Empty domain")
        raise HTTPException(400, "Domain required")

    log.info(f"Adding domain: {domain_name}")

    # 1. Load & update domains.json
    domains = load_json(DOMAINS_FILE)
    was_new = domain_name not in domains

    if was_new:
        domains.append(domain_name)
        save_json(DOMAINS_FILE, domains)
        log.info(f"Domain ADDED to domains.json")
    else:
        log.info(f"Domain already exists in domains.json")

    # 2. Run checker.py
    log.info(f"Running SSL check via checker.py for {domain_name}")
    result = check_ssl(domain_name)
    log.info(f"checker.py RESULT: {domain_name} → {result['status']} "
             f"({result['days_remaining']} days left)")

    # 3. Update status.json
    status_data = load_json(STATUS_FILE)
    status_data = [d for d in status_data if d["domain"] != domain_name]  # remove old
    status_data.append(result)
    save_json(STATUS_FILE, status_data)
    log.info(f"status.json UPDATED with {domain_name}")

    return {
        "message": "Added & checked" if was_new else "Already exists – refreshed",
        "result": result
    }

# Test all
@app.post("/api/test-all")
def test_all():
    log.info("Test All triggered")
    domains = load_json(DOMAINS_FILE)
    results = []
    for d in domains:
        log.info(f"Checking {d}...")
        results.append(check_ssl(d))
    save_json(STATUS_FILE, results)
    log.info("Test All completed")
    return results

# Get status
@app.get("/api/status")
def get_status():
    return load_json(STATUS_FILE)

# Serve frontend

app.mount("/api/", StaticFiles(directory="../frontend", html=True), name="frontend")
