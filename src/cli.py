import argparse
import logging
from src.pipeline import run_pipeline
from src.logging_config import setup_logging
from src.config_loader import load_config, BASE_DIR

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbp-etl",
        description="Pipeline ETL dla kursów walut NBP.",
    )
    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=["latest", "backfill"],
        default="latest",
        help="Tryb: 'latest' (najnowsze) lub 'backfill' (historia).",
    )
    parser.add_argument(
        "--log-level", "-l",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Poziom logowania.",
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default=None,
        help="Ścieżka do pliku konfiguracyjnego YAML.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    log_dir = BASE_DIR / "logs"
    setup_logging(log_dir, args.log_level)

    logger.info("=" * 60)
    logger.info("START PIPELINE'U NBP — KURSY WALUT")
    logger.info(f"Tryb: {args.mode}")
    logger.info("=" * 60)

    try:
        config = load_config(args.config)
        run_pipeline(config, mode=args.mode)
        logger.info("Pipeline zakończony sukcesem.")
    except Exception as e:
        logger.exception("Pipeline zakończony niepowodzeniem:")
        raise SystemExit(1)


if __name__ == "__main__":
    main()