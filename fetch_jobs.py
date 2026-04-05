"""
JobHunter - fetch_jobs.py
Run: python fetch_jobs.py
Get free Adzuna keys: https://developer.adzuna.com
"""
import json, os, sys, time, hashlib
from datetime import datetime, timedelta
import requests

ADZUNA_APP_ID  = os.getenv("ADZUNA_APP_ID",  "YOUR_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "YOUR_APP_KEY")
ANTHROPIC_KEY  = os.getenv("ANTHROPIC_API_KEY", "")
OUTPUT_FILE    = os.path.join("docs", "jobs.json")
MAX_JOBS       = 200
PAGES          = 2

ROLES = [
    "data analyst", "business analyst", "BI analyst",
    "MIS analyst", "reporting analyst", "analytics analyst",
]
CITIES = ["Bangalore", "Pune", "Hyderabad", "Chennai", "Mumbai"]

MUST   = ["sql","python","data analyst","business analyst","analytics","power bi",
          "excel","reporting","dashboard","bi analyst","mis","pandas","insights"]
BONUS  = ["xgboost","scikit","machine learning","numpy","streamlit","kpi",
          "etl","visualization","mysql","data quality","data validation"]
JUNIOR = ["0-2","0-3","1-3","fresher","entry level","junior","associate"]
SKIP   = ["senior","lead","principal","manager","director","vp ","head of",
          "5+ years","7+ years","8+ years","10+ years","devops","android","ios"]

def score_keywords(title, desc):
    t = (title + " " + desc).lower()
    if any(k in t for k in SKIP): return 0
    s = 40
    s += min(sum(1 for k in MUST  if k in t) * 6, 36)
    s += min(sum(1 for k in BONUS if k in t) * 3, 15)
    if any(k in t for k in JUNIOR): s += 9
    return min(s, 100)

def score_claude(title, desc):
    if not ANTHROPIC_KEY:
        return score_keywords(title, desc)
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
        resume = ("Sunil Kumar, Data Research Analyst 1.7yr. "
                  "Skills: SQL, Python, Power BI, Pandas, Scikit-learn, XGBoost, Streamlit, RAG/LLM, Excel. "
                  "Target: Data/Business/BI/MIS Analyst, 0-3yr roles.")
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=8,
            messages=[{"role":"user","content":
                f"Score 0-100 fit of this job for this candidate. Reply integer only.\n"
                f"CANDIDATE:{resume}\nJOB:{title}\n{desc[:400]}"}])
        return int(msg.content[0].text.strip())
    except:
        return score_keywords(title, desc)

def tier(score):
    return "high" if score >= 78 else "mid" if score >= 58 else "low"

def jid(title, company):
    return hashlib.md5(f"{title.lower()}{company.lower()}".encode()).hexdigest()[:10]

def fetch(role, city, page):
    try:
        r = requests.get(
            f"https://api.adzuna.com/v1/api/jobs/in/search/{page}",
            params={"app_id":ADZUNA_APP_ID,"app_key":ADZUNA_APP_KEY,
                    "results_per_page":20,"what":role,"where":city,"sort_by":"date"},
            timeout=15)
        r.raise_for_status()
        return r.json().get("results", [])
    except Exception as e:
        print(f"  Error [{role}/{city}/p{page}]: {e}")
        return []

def main():
    os.makedirs("docs", exist_ok=True)
    existing = {}
    if os.path.exists(OUTPUT_FILE):
        try:
            data = json.load(open(OUTPUT_FILE))
            existing = {j["id"]: j for j in data.get("jobs", [])}
        except: pass

    print(f"Existing: {len(existing)} jobs")
    new_jobs, seen = [], set(existing.keys())

    for city in CITIES:
        for role in ROLES:
            print(f"  {role} / {city}...")
            for page in range(1, PAGES + 1):
                for r in fetch(role, city, page):
                    title   = r.get("title","").strip()
                    company = r.get("company",{}).get("display_name","").strip()
                    uid     = jid(title, company)
                    if uid in seen: continue
                    seen.add(uid)
                    desc  = r.get("description","")
                    score = score_claude(title, desc)
                    if score < 30: continue
                    new_jobs.append({
                        "id":         uid,
                        "title":      title,
                        "company":    company,
                        "location":   r.get("location",{}).get("display_name", city),
                        "city":       city,
                        "description":desc[:350],
                        "url":        r.get("redirect_url",""),
                        "source":     "Adzuna",
                        "score":      score,
                        "tier":       tier(score),
                        "posted":     r.get("created","")[:10],
                        "salary_min": r.get("salary_min",""),
                        "salary_max": r.get("salary_max",""),
                        "status":     "new",
                        "applied_at": "",
                        "notes":      "",
                        "referral":   "",
                        "referrer":   "",
                        "fetched_at": datetime.now().isoformat()[:16],
                    })
                time.sleep(0.4)

    print(f"New: {len(new_jobs)}")
    all_jobs = (new_jobs + list(existing.values()))[:MAX_JOBS]
    all_jobs.sort(key=lambda j: -j["score"])

    cutoff = (datetime.now() - timedelta(days=14)).date().isoformat()
    reminders = [
        {"job_id":j["id"],"title":j["title"],"company":j["company"],"applied_at":j["applied_at"]}
        for j in all_jobs
        if j.get("status") == "applied" and j.get("applied_at","") < cutoff and j.get("applied_at","")
    ]

    json.dump({
        "generated_at": datetime.now().isoformat()[:16],
        "total":        len(all_jobs),
        "new_count":    len(new_jobs),
        "reminders":    reminders,
        "jobs":         all_jobs,
    }, open(OUTPUT_FILE,"w"), indent=2)

    print(f"Saved {len(all_jobs)} jobs to {OUTPUT_FILE}")

if __name__ == "__main__":
    if "YOUR_APP_ID" in ADZUNA_APP_ID:
        print("ERROR: Set ADZUNA_APP_ID and ADZUNA_APP_KEY")
        print("Free keys: https://developer.adzuna.com")
        sys.exit(1)
    main()
