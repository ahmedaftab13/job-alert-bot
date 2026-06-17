import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime

# ---------------------------
# CONFIGURATION
# ---------------------------

KEYWORDS = [
    "store officer", "store in charge", "store supervisor",
    "data entry", "field supervisor", "manager",
    "assistant manager", "administrative officer",
    "operations manager", "hr", "marketing",
    "tehsil coordinator", "enumerator"
]

LOCATIONS = [
    "islamabad", "rawalpindi", "lahore", "jhelum", "punjab", "pakistan"
]

EXPERIENCE_KEYWORDS = ["4 years", "5 years", "4-5 years", "3-5 years", "experience"]

CACHE_FILE = "jobs_seen.json"


# ---------------------------
# LOAD PREVIOUS JOBS
# ---------------------------

def load_seen_jobs():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen_jobs(seen):
    with open(CACHE_FILE, "w") as f:
        json.dump(list(seen), f)


# ---------------------------
# UTILITY FUNCTIONS
# ---------------------------

def is_valid_job(text):
    text_lower = text.lower()

    keyword_match = any(k in text_lower for k in KEYWORDS)
    location_match = any(l in text_lower for l in LOCATIONS)
    exp_match = any(e in text_lower for e in EXPERIENCE_KEYWORDS)

    return keyword_match and location_match and exp_match


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------
# SCRAPERS
# ---------------------------

def scrape_mustakbil():
    jobs = []
    url = "https://mustakbil.com/jobs?search=manager"

    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        for item in soup.find_all("div", class_="job-tile"):
            title = clean_text(item.get_text())
            link_tag = item.find("a")

            if link_tag:
                link = "https://mustakbil.com" + link_tag.get("href")
            else:
                link = ""

            if is_valid_job(title):
                jobs.append({
                    "title": title,
                    "company": "Mustakbil",
                    "location": "Pakistan",
                    "link": link
                })

    except Exception as e:
        print("Mustakbil error:", e)

    return jobs


def scrape_njp():
    jobs = []
    url = "https://njp.gov.pk/jobs"

    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        for item in soup.find_all("tr"):
            text = clean_text(item.get_text())

            if is_valid_job(text):
                link_tag = item.find("a")
                link = link_tag.get("href") if link_tag else ""

                jobs.append({
                    "title": text,
                    "company": "National Job Portal",
                    "location": "Pakistan",
                    "link": link
                })

    except Exception as e:
        print("NJP error:", e)

    return jobs


def scrape_punjab_jobs():
    jobs = []
    url = "https://jobs.punjab.gov.pk"

    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        for item in soup.find_all("div"):
            text = clean_text(item.get_text())

            if is_valid_job(text):
                jobs.append({
                    "title": text,
                    "company": "Punjab Job Portal",
                    "location": "Punjab",
                    "link": url
                })

    except Exception as e:
        print("Punjab Jobs error:", e)

    return jobs


def scrape_indeed_like():
    """
    Lightweight search-based scraping (no login).
    Works only for public search pages.
    """
    jobs = []

    query = "https://pk.indeed.com/jobs?q=store+manager+data+entry+supervisor&l=Pakistan"

    try:
        r = requests.get(query, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        for item in soup.find_all("a"):
            text = clean_text(item.get_text())

            if is_valid_job(text):
                link = "https://pk.indeed.com" + item.get("href", "")

                jobs.append({
                    "title": text,
                    "company": "Indeed",
                    "location": "Pakistan",
                    "link": link
                })

    except Exception as e:
        print("Indeed error:", e)

    return jobs


# ---------------------------
# MAIN SCRAPER
# ---------------------------

def get_all_jobs():
    seen = load_seen_jobs()
    new_seen = set()

    all_jobs = []

    sources = [
        scrape_mustakbil,
        scrape_njp,
        scrape_punjab_jobs,
        scrape_indeed_like
    ]

    for source in sources:
        jobs = source()

        for job in jobs:
            job_id = job["title"] + job.get("link", "")

            if job_id not in seen:
                all_jobs.append(job)
                new_seen.add(job_id)

    save_seen_jobs(seen.union(new_seen))

    return all_jobs


# ---------------------------
# TEST RUN
# ---------------------------

if __name__ == "__main__":
    jobs = get_all_jobs()
    print(f"\nFound {len(jobs)} new jobs:\n")

    for j in jobs:
        print(j["title"])
        print(j["link"])
        print("-" * 40)
