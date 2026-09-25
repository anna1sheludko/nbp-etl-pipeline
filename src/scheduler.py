"""
Scheduler — uruchamia pipeline cyklicznie.
Używa biblioteki `schedule` do uruchamiania zadania codziennie o 08:00.
W Dockerze można też użyć crona, ale ten scheduler działa w Pythonie.
"""
import time
import logging
import schedule
from src.pipeline import run_pipeline
from src.config_loader import load_config

logger = logging.getLogger(__name__)


def job():
    """Zadanie uruchamiane o wyznaczonej porze."""
    logger.info("=" * 60)
    logger.info("SCHEDULER: uruchamiam pipeline (tryb latest)")
    logger.info("=" * 60)
    try:
        config = load_config()
        run_pipeline(config, mode="latest")
        logger.info("SCHEDULER: pipeline zakończony sukcesem.")
    except Exception as e:
        logger.exception(f"SCHEDULER: błąd w pipeline: {e}")


def main():
    """Uruchamia scheduler — codziennie o 08:00 i 15:00 (po publikacjach NBP)."""
    logger.info("Scheduler uruchomiony.")
    logger.info("Zadanie: codziennie o 08:00 i 15:00")

    # NBP publikuje kursy około 11:30 i 14:30, więc odpalamy chwilę po
    schedule.every().day.at("08:00").do(job)
    schedule.every().day.at("15:00").do(job)

    # Uruchom raz na start
    job()

    while True:
        schedule.run_pending()
        time.sleep(60)  # sprawdzaj co minutę


if __name__ == "__main__":
    from src.logging_config import setup_logging
    from src.config_loader import BASE_DIR
    setup_logging(BASE_DIR / "logs", "INFO")
    main()