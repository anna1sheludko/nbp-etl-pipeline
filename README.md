# NBP Currency Rates ETL Pipeline

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-✓-blue?logo=docker)
![Tests](https://img.shields.io/badge/tests-11_passing-brightgreen)

A daily ETL pipeline that fetches official currency exchange rates from the
**National Bank of Poland (NBP) API** and loads them into PostgreSQL with
incremental loading — so you always have the latest data without duplicates.

---

## What problem does it solve?

Businesses that operate in multiple currencies need up-to-date exchange rates
to calculate prices, invoices, and reports. Manual updates are slow and error-prone.

This pipeline automates the whole process:
- Fetches rates from the official NBP API (table A — 30+ currencies)
- Validates the data before loading
- Loads only new records (incremental load — no duplicates)
- Can backfill up to 12 months of history on first run
- Runs automatically twice a day via scheduler

---

## Architecture

```
┌──────────────────┐
│   NBP REST API   │   ← official exchange rates, 30+ currencies
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   EXTRACT        │   requests + tenacity retries
│   (Python)       │   handles weekends & holidays (404)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   TRANSFORM      │   Pandas: cleaning, type casting
│   + VALIDATION   │   validate currency codes, positive rates
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  INCREMENTAL     │   only new rows (WHERE date > last_loaded)
│  LOAD            │   PostgreSQL COPY protocol
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   PostgreSQL     │   table: currency_rates
│                  │   unique constraint (currency_code, effective_date)
└──────────────────┘
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| **Python 3.12** | Core language |
| **requests** | HTTP client for NBP API |
| **Tenacity** | Retries with exponential backoff |
| **Pandas** | Data transformation |
| **psycopg2** | PostgreSQL driver |
| **PostgreSQL 15** | Target database |
| **Docker & Compose** | Reproducibility |
| **schedule** | Daily cron-like scheduler |
| **pytest** | Unit testing |
| **GitHub Actions** | CI/CD |

---

## Project Structure

```
nbp-etl-pipeline/
├── .github/workflows/       # GitHub Actions (tests on push)
├── config/
│   └── config.yaml          # DB + API configuration
├── data/raw/                # (not in repo)
├── docs/
│   ├── architecture.png
│   └── screenshots/
├── sql/
│   ├── 01_init_schema.sql   # table + indexes
│   └── 02_analytics.sql     # example queries
├── src/
│   ├── cli.py               # argparse CLI
│   ├── config_loader.py     # YAML + .env loader
│   ├── extract.py           # API client with retries
│   ├── transform.py         # Pandas transformations
│   ├── validation.py        # data validation rules
│   ├── load.py              # incremental load via COPY
│   ├── pipeline.py          # orchestration
│   ├── scheduler.py         # daily runs at 08:00 & 15:00
│   └── logging_config.py    # rotating file logger
├── tests/
│   ├── conftest.py          # pytest fixtures
│   └── test_transform.py    # 11 unit tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## How to Run

### Prerequisites
- Python 3.12+
- Docker Desktop
- Git

### 1. Clone the repository

```bash
git clone https://github.com/anna1sheludko/nbp-etl-pipeline.git
cd nbp-etl-pipeline
```

### 2. Set up the environment

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env if needed
```

### 4. Start PostgreSQL

```bash
docker compose up -d postgres
```

### 5. First run — backfill 30 days of history

```bash
python -m src.cli --mode backfill --log-level INFO
```

### 6. Daily updates (only new rows)

```bash
python -m src.cli --mode latest
```

### 7. Run the scheduler (optional)

```bash
python -m src.scheduler
```

Runs the pipeline automatically at **08:00** and **15:00** daily.

---

## Example Results

### Table `currency_rates`

| currency_code | currency_name | rate | effective_date | table_no |
|---|---|---|---|---|
| USD | dolar amerykański | 3.8404 | 2026-09-25 | 187/A/NBP/2026 |
| EUR | euro | 4.2810 | 2026-09-25 | 187/A/NBP/2026 |
| GBP | funt szterling | 4.9812 | 2026-09-25 | 187/A/NBP/2026 |
| UAH | hrywna | 0.0855 | 2026-09-25 | 187/A/NBP/2026 |

### Sample queries

```sql
-- 30-day average rate for EUR
SELECT
    currency_code,
    ROUND(AVG(rate)::numeric, 4) AS avg_rate,
    MIN(rate) AS min_rate,
    MAX(rate) AS max_rate
FROM currency_rates
WHERE currency_code = 'EUR'
  AND effective_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY currency_code;

-- Latest USD rate
SELECT effective_date, rate
FROM currency_rates
WHERE currency_code = 'USD'
ORDER BY effective_date DESC
LIMIT 1;
```

---

## Testing

```bash
pytest tests/ -v
```

11 unit tests covering:
- Transformation of single/multiple API responses
- Currency code validation (3 uppercase letters)
- Positive rate validation
- Duplicate detection per (currency, date)
- Empty input handling

GitHub Actions runs tests on every push.

---

## What This Project Demonstrates

- **REST API integration** — HTTP client with retry logic and error handling
- **Incremental loading** — only new rows, no duplicates
- **Backfill strategy** — first run fills history, next runs are fast
- **Data validation** — before data reaches the database
- **Scheduling** — daily automated runs
- **PostgreSQL COPY** — high-performance bulk loading
- **Docker Compose** — reproducible environment
- **Unit testing** — 11 tests, GitHub Actions CI

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

## Author

**Anna Sheludko**
- GitHub: [@anna1sheludko](https://github.com/anna1sheludko)
- Portfolio: [anna1sheludko.github.io](https://anna1sheludko.github.io)