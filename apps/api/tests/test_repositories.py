"""Repository-level behavior tests."""

from __future__ import annotations

from datetime import UTC, datetime

from app.repositories.agencies import AgencyRepository
from app.repositories.opportunities import OpportunityRepository
from app.schemas.opportunity import OpportunityFilters


def _minimal_opp(source_id: str, **overrides) -> dict:
    base = dict(
        source="fixture",
        source_id=source_id,
        title="Aquisição teste",
        object_description="Objeto exemplo para teste.",
        modality="pregao_eletronico",
        status="published",
        category="Saúde",
        estimated_value=100_000.0,
        state="SP",
        city="São Paulo",
        published_at=datetime(2026, 4, 10, tzinfo=UTC),
        proposals_close_at=datetime(2026, 4, 30, tzinfo=UTC),
    )
    base.update(overrides)
    return base


def test_opportunity_upsert_is_idempotent(session):
    repo = OpportunityRepository(session)
    first = repo.upsert(_minimal_opp("x-1"))
    session.commit()
    second = repo.upsert(_minimal_opp("x-1", title="Novo título"))
    session.commit()
    assert first.id == second.id
    assert second.title == "Novo título"


def test_opportunity_upsert_respects_items_replacement(session):
    repo = OpportunityRepository(session)
    opp = repo.upsert(
        _minimal_opp("x-2"),
        items=[{"item_number": 1, "description": "A", "quantity": 10}],
    )
    session.commit()
    assert len(opp.items) == 1

    repo.upsert(
        _minimal_opp("x-2"),
        items=[
            {"item_number": 1, "description": "A'", "quantity": 20},
            {"item_number": 2, "description": "B", "quantity": 5},
        ],
    )
    session.commit()
    refreshed = repo.get(opp.id)
    assert refreshed is not None
    descs = {i.description for i in refreshed.items}
    assert descs == {"A'", "B"}


def test_agency_upsert_updates_existing_fields(session):
    repo = AgencyRepository(session)
    a = repo.upsert({"cnpj": "11111111000199", "name": "Órgão Inicial", "state": "SP"})
    session.commit()
    assert a.id is not None
    updated = repo.upsert({"cnpj": "11111111000199", "name": "Órgão Renomeado"})
    assert updated.id == a.id
    assert updated.name == "Órgão Renomeado"
    # state should be preserved since None is skipped
    assert updated.state == "SP"


def test_opportunity_search_sort_variants(session):
    repo = OpportunityRepository(session)
    for i, v in enumerate([50_000, 200_000, 5_000]):
        repo.upsert(_minimal_opp(f"sort-{i}", estimated_value=v))
    session.commit()

    items, _total = repo.search(OpportunityFilters(sort="value_desc"), limit=10)
    values = [o.estimated_value for o in items]
    assert values == sorted(values, reverse=True)

    items, _total = repo.search(OpportunityFilters(sort="value_asc"), limit=10)
    values = [o.estimated_value for o in items]
    assert values == sorted(values)


def test_opportunity_search_paginates(session):
    repo = OpportunityRepository(session)
    for i in range(25):
        repo.upsert(_minimal_opp(f"pag-{i:03d}"))
    session.commit()
    first_page, total = repo.search(OpportunityFilters(), limit=10, offset=0)
    second_page, _ = repo.search(OpportunityFilters(), limit=10, offset=10)
    assert total >= 25
    assert len(first_page) == 10
    assert len(second_page) == 10
    assert {o.id for o in first_page} & {o.id for o in second_page} == set()


def test_opportunity_search_applies_value_bounds(session):
    repo = OpportunityRepository(session)
    repo.upsert(_minimal_opp("v-low", estimated_value=1_000.0))
    repo.upsert(_minimal_opp("v-mid", estimated_value=50_000.0))
    repo.upsert(_minimal_opp("v-high", estimated_value=500_000.0))
    session.commit()
    items, _ = repo.search(OpportunityFilters(min_value=10_000, max_value=100_000), limit=10)
    assert {o.source_id for o in items} == {"v-mid"}
