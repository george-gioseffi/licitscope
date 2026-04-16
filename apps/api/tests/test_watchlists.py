def test_watchlist_crud(client):
    # Create
    body = {
        "name": "TI SP",
        "description": "Tecnologia em São Paulo",
        "filters": {"q": "software", "state": "SP", "sort": "published_at_desc"},
    }
    r = client.post("/watchlists", json=body)
    assert r.status_code == 201, r.text
    created = r.json()
    assert created["name"] == "TI SP"
    wid = created["id"]

    # List
    r = client.get("/watchlists")
    assert r.status_code == 200
    assert any(w["id"] == wid for w in r.json())

    # Run (returns matches, empty list is fine)
    r = client.post(f"/watchlists/{wid}/run")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    # Alerts endpoint
    r = client.get(f"/watchlists/{wid}/alerts")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    # Delete
    r = client.delete(f"/watchlists/{wid}")
    assert r.status_code == 204
