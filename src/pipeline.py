import logging
from src.extract import extract_historical, extract_latest
from src.transform import transform_rates, get_latest_date
from src.validation import validate_dataframe
from src.load import DatabaseConnection, load_rates
from src.config_loader import BASE_DIR

logger = logging.getLogger(__name__)


def run_pipeline(config: dict, mode: str = "latest"):
    """
    Uruchamia pipeline.
    mode = 'latest' — tylko najnowsze kursy
    mode = 'backfill' — historia z ostatnich `backfill_days` dni
    """
    api_cfg = config["api"]
    base_url = api_cfg["base_url"]
    table = api_cfg["table"]
    timeout = api_cfg.get("timeout", 10)

    if mode == "backfill":
        days = api_cfg.get("backfill_days", 365)
        logger.info(f"=== TRYB: BACKFILL ({days} dni) ===")
        responses = extract_historical(base_url, table, days, timeout)
    else:
        logger.info("=== TRYB: LATEST ===")
        latest = extract_latest(base_url, table, timeout)
        responses = [latest] if latest else []

    if not responses:
        logger.warning("Brak danych z API.")
        return

    # Transform
    df = transform_rates(responses)
    if df.empty:
        logger.warning("Transformacja zwróciła pusty DataFrame.")
        return

    # Validate
    df = validate_dataframe(df)

    # Load
    with DatabaseConnection(config["database"]) as db:
        rows_loaded = load_rates(db, df)

    logger.info(f"Pipeline zakończony. Załadowano: {rows_loaded} wierszy.")