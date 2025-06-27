import sys
import os
from app import app

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

client = app.test_client()

def test_status():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"

def test_evaluate():
    payload = {
        "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
        "move": "f1c4"
    }
    response = client.post("/evaluate", json=payload)
    assert response.status_code == 200
    assert "is_blunder" in response.get_json()

if __name__ == "__main__":
    test_status()
    test_evaluate()
    print("✅ All API tests passed!")