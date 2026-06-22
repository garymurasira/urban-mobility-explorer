# AI Usage Log — David (Backend API & Algorithm)

**Project:** Urban Mobility Explorer  
**Role:** Backend API & Custom Algorithm  

---

## 1. Diagnosing the MySQL connection error

**What I asked AI:** Why is my Flask app throwing `InterfaceError: Can't connect to MySQL server`?

**What AI did:** Identified that the Aiven free-tier MySQL service was powered off due to storage limits, and that the `.env` file still had the old Aiven credentials pointing to a dead server.

**What I verified and changed:** I confirmed the Aiven dashboard showed the service as "Powered off". I then set up a local MySQL instance and updated both `.env` files (`database/.env` and `backend/.env`) manually with my local credentials.

---

## 2. Setting up local MySQL and loading the database

**What I asked AI:** How do I set up MySQL locally and load the data?

**What AI did:** Provided the sequence of commands to install MySQL via Homebrew, create the database, apply `schema.sql`, and run `load_data.py`.

**What I verified and changed:** I ran each command myself, confirmed MySQL started correctly, and verified the load script output showed `1000 rows loaded, 0 rows failed` before trusting the data was in the database.

---

## 3. Understanding the pipeline and data flow

**What I asked AI:** How does the pipeline connect to my API endpoints?

**What AI did:** Explained that `pipeline.py` produces `trips_clean_sample.csv` and `zones_reference.csv`, which `load_data.py` then inserts into MySQL, which my Flask API queries.

**What I verified and changed:** I traced the file paths in `load_data.py` myself to confirm they matched where the sample files were placed, and tested each endpoint in the browser to confirm real data was returned.

---

## 4. Git workflow and protecting credentials

**What I asked AI:** How do I push my changes to GitHub without committing the `.env` file?

**What I verified and changed:** I ran `cat .gitignore` myself to confirm `.env` and `**/.env` were already listed before pushing. I chose which files to stage based on what VS Code showed as modified (`M`), not blindly following AI suggestions.

---


*All AI suggestions were reviewed, tested,*