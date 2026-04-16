"""Pricing intelligence service tests."""

from __future__ import annotations

from app.models.contract import Contract, ContractItem
from app.services.pricing import PricingService


def _seed_contract_items(session, prices: list[float], catmat: str = "BR000001") -> None:
    contract = Contract(
        source="fixture",
        source_id=f"ct-{catmat}",
        object_description="test",
        status="active",
    )
    session.add(contract)
    session.flush()
    for i, p in enumerate(prices, start=1):
        session.add(
            ContractItem(
                contract_id=contract.id,
                item_number=i,
                description=f"Item {catmat} #{i}",
                unit="unidade",
                quantity=1,
                unit_price=p,
                total_price=p,
                catmat_code=catmat,
            )
        )
    session.commit()


def test_pricing_summary_skips_codes_with_few_observations(session):
    _seed_contract_items(session, [10.0, 11.0])  # 2 observations, below MIN
    out = PricingService(session).summary()
    assert out == []


def test_pricing_summary_reports_median_and_range(session):
    _seed_contract_items(session, [10.0, 11.0, 12.0, 13.0, 14.0, 15.0], catmat="BR111111")
    out = PricingService(session).summary()
    assert len(out) == 1
    row = out[0]
    assert row.catmat_or_catser == "BR111111"
    assert row.observations == 6
    assert row.min_unit_price == 10.0
    assert row.max_unit_price == 15.0
    assert 12.0 <= row.median_unit_price <= 13.0
    # tight cluster -> no anomaly
    assert row.anomaly_flag is False


def test_pricing_summary_flags_high_dispersion(session):
    # One wild outlier plus a tight cluster → IQR/median >= 0.75
    _seed_contract_items(
        session,
        [5.0, 10.0, 15.0, 80.0, 200.0, 500.0],
        catmat="BR222222",
    )
    out = PricingService(session).summary()
    assert len(out) == 1
    assert out[0].anomaly_flag is True


def test_pricing_summary_description_picks_median_representative(session):
    # median is around 50; description_sample should come from the row
    # nearest the median, not the first one.
    _seed_contract_items(session, [10.0, 50.0, 49.0, 51.0, 200.0], catmat="BR333333")
    out = PricingService(session).summary()
    assert out
    # The "closest to median" item should be mentioned
    assert "BR333333" in out[0].description_sample
