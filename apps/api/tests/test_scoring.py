from datetime import UTC, datetime, timedelta

from app.enrichment.scoring import NoticeScores, price_anomaly_score, score_notice
from app.models.opportunity import Opportunity


def make(**kwargs) -> Opportunity:
    base = dict(
        source="fixture", source_id="x",
        title="Aquisição de medicamentos",
        object_description="Contratação de fornecedores de medicamentos diversos conforme RENAME.",
        modality="pregao_eletronico", status="published",
        estimated_value=500_000.0,
    )
    base.update(kwargs)
    return Opportunity(**base)


def test_score_notice_returns_clipped_values():
    s = score_notice(make())
    assert isinstance(s, NoticeScores)
    for v in (s.complexity, s.effort, s.risk):
        assert 0.0 <= v <= 1.0


def test_dispensa_bumps_risk():
    baseline = score_notice(make(modality="pregao_eletronico"))
    risky = score_notice(make(modality="dispensa"))
    assert risky.risk > baseline.risk


def test_short_deadline_bumps_risk():
    now = datetime.now(UTC)
    short = score_notice(
        make(published_at=now, proposals_close_at=now + timedelta(days=3))
    )
    long = score_notice(
        make(published_at=now, proposals_close_at=now + timedelta(days=60))
    )
    assert short.risk > long.risk


def test_price_anomaly_score_too_few_observations():
    assert price_anomaly_score([10.0, 11.0]) == 0.0


def test_price_anomaly_score_tight_dispersion_low():
    assert price_anomaly_score([10.0, 10.1, 10.2, 10.3]) < 0.3


def test_price_anomaly_score_wild_dispersion_high():
    assert price_anomaly_score([10.0, 50.0, 1.0, 300.0, 20.0]) > 0.5
