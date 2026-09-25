import requests
import logging
from datetime import date, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    """Błąd podczas ekstrakcji danych z API."""
    pass


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.RequestException),
    reraise=True,
)
def fetch_rates_for_date(base_url: str, table: str, day: date, timeout: int = 10) -> dict:
    """
    Pobiera kursy walut z API NBP dla konkretnej daty.
    Zwraca dict z odpowiedzi JSON lub None, jeśli brak danych (np. weekend).
    """
    url = f"{base_url}/exchangerates/tables/{table}/{day.isoformat()}/?format=json"
    logger.debug(f"GET {url}")

    try:
        response = requests.get(url, timeout=timeout)

        if response.status_code == 404:
            # NBP zwraca 404 dla dni bez notowań (weekendy, święta)
            logger.debug(f"Brak notowań dla {day.isoformat()}")
            return None

        response.raise_for_status()
        data = response.json()

        if not data or len(data) == 0:
            return None

        return data[0]  # NBP zwraca listę z jednym elementem

    except requests.RequestException as e:
        logger.warning(f"Błąd HTTP dla {day.isoformat()}: {e}")
        raise


def extract_historical(base_url: str, table: str, days_back: int, timeout: int = 10) -> list:
    """
    Pobiera historyczne kursy z ostatnich `days_back` dni.
    Zwraca listę dict-ów (jeden na dzień, gdzie były notowania).
    """
    logger.info(f"Pobieram historię z ostatnich {days_back} dni...")

    today = date.today()
    start = today - timedelta(days=days_back)

    results = []
    current = start
    total = (today - start).days + 1
    success = 0
    skipped = 0

    while current <= today:
        try:
            data = fetch_rates_for_date(base_url, table, current, timeout)
            if data:
                results.append(data)
                success += 1
            else:
                skipped += 1
        except Exception as e:
            logger.warning(f"Pominięto {current.isoformat()}: {e}")

        current += timedelta(days=1)

    logger.info(f"Pobrano {success} dni z notowaniami, pominięto {skipped} dni (weekendy/święta)")
    return results


def extract_latest(base_url: str, table: str, timeout: int = 10) -> dict:
    """Pobiera najnowsze kursy (bez daty = NBP zwraca ostatnie notowanie)."""
    url = f"{base_url}/exchangerates/tables/{table}/?format=json"
    logger.info(f"Pobieram najnowsze kursy z {url}")

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return data[0] if data else None
    except requests.RequestException as e:
        logger.error(f"Błąd HTTP: {e}")
        raise ExtractionError(f"Błąd pobierania z API: {e}") from e