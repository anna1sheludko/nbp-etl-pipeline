import pandas as pd
import logging
import psycopg2
from io import StringIO
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    pass


class DatabaseConnection:
    def __init__(self, config: dict):
        self.config = config
        self.conn = None

    def __enter__(self):
        try:
            self.conn = psycopg2.connect(
                host=self.config["host"],
                port=self.config["port"],
                dbname=self.config["name"],
                user=self.config["user"],
                password=self.config["password"],
                connect_timeout=10,
            )
            logger.debug("Połączenie z bazą ustanowione.")
            return self
        except psycopg2.OperationalError as e:
            logger.error(f"Błąd połączenia: {e}")
            raise DatabaseError(f"Błąd połączenia: {e}") from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
            logger.debug("Połączenie zamknięte.")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(psycopg2.OperationalError),
    )
    def get_last_loaded_date(self, table: str = "currency_rates"):
        """Zwraca najnowszą datę w tabeli — do incremental load."""
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT MAX(effective_date) FROM {table};")
            result = cur.fetchone()
            return result[0] if result else None


def load_rates(db: DatabaseConnection, df: pd.DataFrame, table: str = "currency_rates"):
    """
    Ładuje DataFrame do PostgreSQL używając COPY.
    Pomija duplikaty (ON CONFLICT DO NOTHING nie działa z COPY,
    więc filtrujemy po stronie Pythona i wstawiamy tylko nowe).
    """
    if df.empty:
        logger.warning("Pusty DataFrame — pomijam ładowanie.")
        return 0

    # Incremental load — pobierz najnowszą datę z bazy
    last_date = db.get_last_loaded_date(table)
    if last_date:
        before = len(df)
        df = df[df["effective_date"] > last_date]
        logger.info(f"Incremental load: pominięto {before - len(df)} starych wierszy (last_date={last_date})")

    if df.empty:
        logger.info("Brak nowych danych do załadowania.")
        return 0

    # Przygotuj bufor CSV
    buffer = StringIO()
    df_to_load = df[["currency_code", "currency_name", "rate", "effective_date", "table_no"]]
    df_to_load.to_csv(buffer, index=False, header=False, sep="\t", na_rep="\\N")
    buffer.seek(0)

    try:
        with db.conn.cursor() as cur:
            cur.copy_expert(
                f"""COPY {table} (currency_code, currency_name, rate, effective_date, table_no)
                    FROM STDIN WITH (FORMAT CSV, DELIMITER E'\\t', NULL '\\N')""",
                buffer,
            )
            db.conn.commit()
        logger.info(f"Załadowano {len(df):,} wierszy do {table}")
        return len(df)
    except psycopg2.Error as e:
        db.conn.rollback()
        logger.error(f"Błąd COPY: {e}")
        raise DatabaseError(f"Błąd ładowania: {e}") from e