import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


auth = ("henry","henrygok000")
wrong_auth = ("henry",'Henrygok@000')
already_present_db = 'henry_swagger'
random_db = "random_test"
wrong_query = "SELECT * FROM unknown_db limit 1"

wrong_song_name = "~1uufujdef"
wrong_video_id = "12defef4"

def test_auth_header_missing():
    response = client.get("/api/database/create?db_name=test_db")
    assert response.status_code == 400
    assert response.json() == {"status_code": 400, "msg": "Authorization Header Missing"}

def test_wrong_creds():
    response = client.get("/api/database/create?db_name=test_db", auth=wrong_auth)
    assert response.status_code == 401
    assert response.json() == {"status_code": 401, "msg": "Invalid Credentials"}

def test_error_create_db():
    response = client.get(f"/api/database/create?db_name={already_present_db}",auth=auth)
    assert response.status_code == 500
    assert response.json()["success"] == False
    assert isinstance(response.json()["results"], str)

# Not Running this test as there will be atleast 1 db.
'''def test_error_list_db():
    response = client.get(f"/api/database/list",auth=auth)
    assert response.status_code == 500
    assert response.json()["success"] == False
    assert isinstance(response.json()["results"], str)'''

def test_error_del_db():
    response = client.delete(f"/api/database/delete?db_name={random_db}",auth=auth)
    assert response.status_code == 500
    assert response.json()["success"] == False
    assert isinstance(response.json()["results"], str)

def test_error_list_tbl():
    response = client.get(f"/api/tables/list?db_name={random_db}",auth=auth)
    assert response.status_code == 500
    assert response.json()["success"] == False
    assert isinstance(response.json()["results"], str)

def test_execute_query_api():
    query = {"query": wrong_query}
    response = client.post("/api/sql/execute", json=query,auth=auth)
    assert response.status_code == 500
    assert response.json()["success"] == False
    assert isinstance(response.json()["results"], str)

def test_search_songs():
    response = client.get(f"/api/songs/search?query={wrong_song_name}",auth=auth)
    assert response.status_code == 404
    assert response.json()["success"] == False
    assert isinstance(response.json()["results"], str)

def test_get_lyrics():
    response = client.get(f"/api/songs/lyrics?video_id={wrong_video_id}",auth=auth)
    assert response.status_code == 404
    assert response.json()["success"] == False
    assert isinstance(response.json()["results"], str)

def test_get_direct_link():
    response = client.get(f"/api/songs/get_link?video_id={wrong_video_id}",auth=auth)
    assert response.status_code == 404
    assert response.json()["success"] == False
    assert isinstance(response.json()["results"], str)