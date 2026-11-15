# reading-shelves

Native Python3.11–3.13 application; intended acceptance runtime3.12.
Install `python -m pip install -r requirements.txt` in an isolated environment.
Run `python -m pytest`. Start `uvicorn reading_shelves.app:app --host 0.0.0.0 --port 8203`.
Requires DATABASE_URL; migrate with `python -m reading_shelves.migrate`. This only applies source-owned versioned DDL within the assigned database; no database creation/reset or startup auto-migration.


POST /tags {name}; POST /books {reference,title,tag_ids}; GET /books/:uuid; GET /books?tags=a,b uses intersection. Readiness /health/ready checks native tables.
Tests are source-native development checks. The PostgreSQL repository is replaced by a test double; no real schema/persistence is proved.
AI-assisted researcher-created source; no deployment files or runtime credentials.
