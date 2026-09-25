import pytest
import pandas as pd
from src.transform import transform_rates, get_latest_date
from src.validation import validate_dataframe


class TestTransformRates:

    def test_transforms_single_day(self, sample_api_response):
        result = transform_rates(sample_api_response)
        assert len(result) == 3
        assert set(result["currency_code"]) == {"USD", "EUR", "GBP"}

    def test_transforms_two_days(self, sample_api_responses_two_days):
        result = transform_rates(sample_api_responses_two_days)
        assert len(result) == 4  # 2 dni × 2 waluty

    def test_currency_code_is_uppercase(self, sample_api_response):
        result = transform_rates(sample_api_response)
        for code in result["currency_code"]:
            assert code == code.upper()

    def test_rate_is_positive(self, sample_api_response):
        result = transform_rates(sample_api_response)
        assert (result["rate"] > 0).all()

    def test_empty_input_returns_empty_df(self):
        result = transform_rates([])
        assert result.empty

    def test_dates_are_unique_per_currency(self, sample_api_responses_two_days):
        result = transform_rates(sample_api_responses_two_days)
        # Każda para (currency, date) powinna być unikalna
        duplicates = result.duplicated(subset=["currency_code", "effective_date"])
        assert not duplicates.any()

    def test_get_latest_date(self, sample_api_responses_two_days):
        df = transform_rates(sample_api_responses_two_days)
        latest = get_latest_date(df)
        assert str(latest) == "2026-09-23"


class TestValidation:

    def test_valid_data_passes(self, sample_api_response):
        df = transform_rates(sample_api_response)
        result = validate_dataframe(df)
        assert len(result) == len(df)

    def test_missing_column_raises(self):
        df = pd.DataFrame({"currency_code": ["USD"]})
        with pytest.raises(ValueError, match="Brakujące kolumny"):
            validate_dataframe(df)

    def test_invalid_currency_code_raises(self, sample_api_response):
        df = transform_rates(sample_api_response)
        df.loc[0, "currency_code"] = "US"  # 2 znaki zamiast 3
        with pytest.raises(ValueError):
            validate_dataframe(df)

    def test_empty_df_passes(self):
        result = validate_dataframe(pd.DataFrame())
        assert result.empty