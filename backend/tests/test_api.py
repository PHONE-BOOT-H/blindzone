# backend/tests/test_api.py
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True
    assert body["features_loaded"] is True
    assert body["feature_count"] > 0


def test_features_list():
    resp = client.get("/api/features")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) >= 200
    assert {"sgg_code", "sgg_name", "lon", "lat", "risk_index"}.issubset(body[0].keys())


def test_feature_detail_known_sgg():
    list_resp = client.get("/api/features").json()
    sample_code = list_resp[0]["sgg_code"]
    resp = client.get(f"/api/features/{sample_code}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["sgg_code"] == sample_code
    assert "shap_top" in body


def test_feature_detail_unknown():
    resp = client.get("/api/features/99999")
    assert resp.status_code == 404


def test_top10():
    resp = client.get("/api/top10")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 10


def test_simulate_empty():
    resp = client.post("/api/simulate", json={"virtual_ems": []})
    assert resp.status_code == 200
    body = resp.json()
    assert body["improved_count"] == 0


def test_simulate_with_virtual_ems():
    resp = client.post("/api/simulate", json={"virtual_ems": [[127.0, 37.5]]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["improved_count"] >= 0
    assert len(body["items"]) > 0


def test_contrast():
    resp = client.get("/api/contrast")
    assert resp.status_code == 200
    body = resp.json()
    assert body["blindzone_top10_not_in_accident_top10"] >= 0
    assert len(body["items"]) >= 10
