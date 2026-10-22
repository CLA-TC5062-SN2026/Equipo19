def test_salud(cliente):
    r = cliente.get("/api/salud")
    assert r.status_code == 200
