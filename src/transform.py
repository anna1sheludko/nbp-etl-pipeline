import pandas as pd
import logging

logger = logging.getLogger(__name__)


def transform_rates(api_responses: list) -> pd.DataFrame:
    """
    Zamienia listę odpowiedzi z API NBP na jedną tabelę Pandas.
    Każdy wiersz = jeden kurs (waluta + data).
    """
    if not api_responses:
        logger.warning("Brak danych do transformacji.")
        return pd.DataFrame()

    rows = []
    for day_data in api_responses:
        effective_date = day_data.get("effectiveDate")
        table_no = day_data.get("no")
        rates = day_data.get("rates", [])

        for rate in rates:
            rows.append({
                "currency_code": rate.get("code"),
                "currency_name": rate.get("currency"),
                "rate": rate.get("mid"),
                "effective_date": effective_date,
                "table_no": table_no,
            })

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # Konwersje typów
    df["effective_date"] = pd.to_datetime(df["effective_date"]).dt.date
    df["rate"] = pd.to_numeric(df["rate"], errors="coerce")

    # Usuwanie duplikatów (jeśli API zwróciło ten sam dzień dwukrotnie)
    before = len(df)
    df = df.drop_duplicates(subset=["currency_code", "effective_date"])
    if len(df) < before:
        logger.info(f"Usunięto {before - len(df)} duplikatów")

    # Usuwanie wierszy z błędnymi danymi
    df = df.dropna(subset=["currency_code", "rate", "effective_date"])
    df = df[df["rate"] > 0]

    df = df.sort_values(["effective_date", "currency_code"]).reset_index(drop=True)

    logger.info(f"Transformacja zakończona: {len(df):,} wierszy")
    return df


def get_latest_date(df: pd.DataFrame):
    """Zwraca najnowszą datę w DataFrame (do incremental load)."""
    if df.empty:
        return None
    return df["effective_date"].max()