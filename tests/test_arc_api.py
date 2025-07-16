def test_get_arcs(client):
    response = client.get("/api/arcs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_symbolic_memory(client):
    response = client.get("/api/symbolic-memory")
    assert response.status_code == 200
    assert isinstance(response.json(), list) 