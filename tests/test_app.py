from fastapi.testclient import TestClient
from urllib.parse import quote
from src.app import app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # basic sanity check: known activity present
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "testuser@example.com"
    encoded_activity = quote(activity, safe="")

    # Ensure clean state: if present remove first
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    if email in participants:
        client.post(f"/activities/{encoded_activity}/unregister", params={"email": email})

    # Signup should succeed
    resp = client.post(f"/activities/{encoded_activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant appears
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Duplicate signup should fail (400)
    resp_dup = client.post(f"/activities/{encoded_activity}/signup", params={"email": email})
    assert resp_dup.status_code == 400

    # Unregister should succeed
    resp_un = client.post(f"/activities/{encoded_activity}/unregister", params={"email": email})
    assert resp_un.status_code == 200

    # Verify removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]
*** End Patch