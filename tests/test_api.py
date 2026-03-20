from __future__ import annotations


def test_settings_roundtrip(client):
    response = client.get("/api/settings")
    assert response.status_code == 200
    assert response.json()["library_name"] == "easy_kicad"

    updated = response.json()
    updated["overwrite"] = True
    save_response = client.put("/api/settings", json=updated)
    assert save_response.status_code == 200
    assert save_response.json()["overwrite"] is True


def test_inspect_endpoint_returns_previews(client):
    response = client.post("/api/parts/inspect", json={"lcscId": "C2040"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["part"]["lcscId"] == "C2040"
    assert "<svg" in payload["symbolSvg"]
    assert "<svg" in payload["footprintSvg"]
    assert payload["model3d"]["available"] is True


def test_import_endpoint_returns_paths(client):
    response = client.post("/api/parts/import", json={"lcscId": "C2040"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["symbolLibrary"].endswith(".kicad_sym")
    assert payload["footprintFile"].endswith(".kicad_mod")


def test_model_route_returns_wrl(client):
    response = client.get("/api/parts/C2040/model.wrl")
    assert response.status_code == 200
    assert response.text.startswith("#VRML")


def test_connection_check(client):
    response = client.post("/api/settings/test-connection")
    assert response.status_code == 200
    assert response.json()["success"] is True
