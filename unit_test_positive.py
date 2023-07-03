import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

db_name = "test_db"
auth = ("henry","henrygok000")
test_db = "nse"
test_query = "SELECT * FROM nse.nse_historical_data limit 5"
video_id="CcAqoRmQWhA"

song_search_query = "BTS"

def test_create_db():
    response = client.get(f"/api/database/create?db_name={db_name}",auth=auth)
    assert response.status_code == 200
    assert response.json() == {"success": True, "results": f"Database {db_name} is Created!."}

def test_list_db():
    response = client.get("/api/database/list",auth=auth)
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_del_db():
    response = client.delete(f"/api/database/delete?db_name={db_name}",auth=auth)
    assert response.status_code == 200
    assert response.json() == {"success": True, "results": f"Database {db_name} is deleted!."}

def test_list_tbl():
    response = client.get(f"/api/tables/list?db_name={test_db}",auth=auth)
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_execute_query_api():
    query = {"query": test_query}
    response = client.post("/api/sql/execute", json=query,auth=auth)
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_search_songs():
    response = client.get(f"/api/songs/search?query={song_search_query}",auth=auth)
    assert response.status_code == 200
    assert len(response.json()['results']) > 0

def test_get_lyrics():
    response = client.get(f"/api/songs/lyrics?video_id={video_id}",auth=auth)
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_get_direct_link():
    response = client.get(f"/api/songs/get_link?video_id={video_id}",auth=auth)
    assert response.status_code == 200
    assert response.json()["success"] == True
