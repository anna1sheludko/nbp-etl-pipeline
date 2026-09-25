import pandas as pd
import logging

logger = logging.getLogger(__name__)


REQUIRED_COLUMNS = ["currency_code", "currency_name", "rate", "effective_date", "table_no"]


def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Podstawowa walidacja DataFrame z kursami."""
    if df.empty:
        logger.warning("Pusty DataFrame — pomijam walidację.")
        return df

    # Sprawdź kolumny
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Brakujące kolumny: {missing}")

    # Walidacja wartości
    invalid_codes = df[~df["currency_code"].str.len().eq(3)]
    if not invalid_codes.empty:
        raise ValueError(f"Nieprawidłowe kody walut: {invalid_codes['currency_code'].unique()}")

    invalid_rates = df[df["rate"] <= 0]
    if not invalid_rates.empty:
        raise ValueError(f"Znaleziono {len(invalid_rates)} wierszy z rate <= 0")

    logger.info(f"Walidacja zakończona pomyślnie: {len(df):,} wierszy")
    return df