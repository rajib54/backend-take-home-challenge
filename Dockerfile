FROM python:3.12-slim

# Install build dependencies and PostgreSQL client (for pg_isready)
RUN apt-get update && apt-get install -y build-essential libpq-dev postgresql-client

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

# Wait for DB, run migration, then start app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
