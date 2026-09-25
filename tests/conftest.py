import pytest
from datetime import date


@pytest.fixture
def sample_api_response():
    """Przykładowa odpowiedź z API NBP."""
    return [
        {
            "table": "A",
            "no": "183/A/NBP/2026",
            "effectiveDate": "2026-09-22",
            "rates": [
                {"currency": "dolar amerykański", "code": "USD", "mid": 3.6521},
                {"currency": "euro", "code": "EUR", "mid": 4.2785},
                {"currency": "funt szterling", "code": "GBP", "mid": 4.9812},
            ],
        }
    ]


@pytest.fixture
def sample_api_responses_two_days():
    """Dwie odpowiedzi z API (dwa dni)."""
    return [
        {
            "table": "A",
            "no": "183/A/NBP/2026",
            "effectiveDate": "2026-09-22",
            "rates": [
                {"currency": "dolar amerykański", "code": "USD", "mid": 3.6521},
                {"currency": "euro", "code": "EUR", "mid": 4.2785},
            ],
        },
        {
            "table": "A",
            "no": "184/A/NBP/2026",
            "effectiveDate": "2026-09-23",
            "rates": [
                {"currency": "dolar amerykański", "code": "USD", "mid": 3.6610},
                {"currency": "euro", "code": "EUR", "mid": 4.2810},
            ],
        },
    ]