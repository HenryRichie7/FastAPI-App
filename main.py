import uvicorn

from typing import Annotated

from fastapi import FastAPI, Response,Request, Depends, Body, HTTPException
from fastapi.security import HTTPBasic
from fastapi.responses import JSONResponse, RedirectResponse

from Utils.db_utils import *
from Models.ResponseModel import SingleResponseModel, ListResponseModel, DictResponseModel
from Models.PostModels import QueryExecuteModel
from Extras.YoutubeMusicApi import YoutubeMusicApi

import sqlite3
from base64 import b64decode

auth_header = HTTPBasic()

def get_creds(username,password):
    """
    This function will fetch the given username and password in sqlite3 db
    and will return boolean based on the availability of the given creds.

    params:
    @username: The username
    @password: The Password

    return:
    type(<boolean>)
    """
    CONNECTION = "creds.db"
    connection = sqlite3.connect(CONNECTION)

    cursor = connection.cursor()
    result = cursor.execute(f"SELECT * FROM creds WHERE username = '{username}' and password = '{password}'")

    # Converting Iterable Cursor Object to List.
    result = [x for x in result]

    # If the length of the result is Greater than 0 returns True else False
    if result:
        return True
    else:
        return False

description = """
A simple API project created using FastAPI.
"""

app = FastAPI(debug=True,
              title="Henry's API",
              description=description,
              responses={
        400: {
            "description": "Authorization header is missing",
            "content":{"application/json":{"example":{"status_code":400,'msg':"Authorization Header Missing"}}},
            
        },
        401: {
            "description": "Invalid Credentials",
            "content":{"application/json":{"example":{"status_code":401,'msg':"Invalid Credentials"}}},
        },
        500: {
            "description": "Internal Server Error",
            "content":{"application/json":{"example":{"success":False,'msg':"Error Details....."}}},
        },
    },
              )

# Creating instance of YoutubeMusicApi class
youtube_music_api_instance = YoutubeMusicApi()

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"success": False,'results':exc.detail})

@app.middleware("http")
async def check_auth(request: Request, call_next):
    """
    ## The Middlware uses BASIC Auth to check the Authorization of the request.
    ## The Middleware is applied only to /api routes.

    ## The Middleware checks for Authorization header
        ### If Authorization header is Missing it will return Status Code 400 and with a response "Authorization Header Missing"
        ### If the provided Basic Auth Creds is invalid it will return Status Code 401 and with a response "Invalid Credentials"

        ### If the provided creds is valid the middleware allows the request along with a custom header "Requested-By" which has
            the username of the user who requested it.
    """

    # Skipping middleware for non /api routes.
    if "/api" not in request.url.path:
        response = await call_next(request)
        return response

    # Applying Middleware for /api routes.
    elif request.headers.get('Authorization'):
        creds = request.headers.get('Authorization').split(" ")[-1]
        decoded_creds = b64decode(creds).decode()

        username, password_ = decoded_creds.split(":")

        if get_creds(username,password_):
            response = await call_next(request)
            response.headers['Requested-By'] = username
            return response
        else:
            return JSONResponse(content={"status_code":401,'msg':"Invalid Credentials"},status_code=401)
    else:
        return JSONResponse(content={"status_code":400,'msg':"Authorization Header Missing"},status_code=400)

@app.get("/",include_in_schema=False)
def redirect_docs():
    # Redirecting users to /docs route when users open root route "/"

    return RedirectResponse(url='/docs')

@app.get("/api/database/create",response_model=SingleResponseModel,tags=["database"])
async def create_db(db_name,response:Response,auth_header = Depends(auth_header)):
    """
    This Endpoint will create a database in Mysql server.
    """
    resp = create_database(db_name)

    if resp.success:
        response.status_code = 200
        return resp
    else:
        raise HTTPException(status_code=500, detail=resp.msg)
    
@app.get("/api/database/list",response_model=ListResponseModel,tags=["database"])
async def list_db(response:Response,auth_header: str = Depends(auth_header)):
    """
    This Endpoint will list all database in Mysql server.
    """
    resp = show_databases()

    if resp.success:
        response.status_code = 200
        return resp
    
    else:
        raise HTTPException(status_code=500, detail=resp.msg)
    
@app.delete("/api/database/delete",response_model=SingleResponseModel,tags=["database"])
async def del_db(db_name,response:Response,auth_header: str = Depends(auth_header)):
    """
    This Endpoint will delete the given database in Mysql server.
    """
    resp = drop_database(db_name)

    if resp.success:
        response.status_code = 200
        return resp
    
    else:
        raise HTTPException(status_code=500, detail=resp.msg)
    
@app.get("/api/tables/list",response_model=ListResponseModel,tags=["tables"])

async def list_tbl(db_name,response:Response,auth_header: str = Depends(auth_header)):
    """
    This Endpoint will list all tables in a database in Mysql server.
    """

    resp = list_tables(db_name)

    if resp.success:
        response.status_code = 200
        return resp
    
    else:
        raise HTTPException(status_code=500, detail=resp.msg)
    
@app.post("/api/sql/execute",response_model=ListResponseModel,tags=["sql"])
async def execute_query_api(query:Annotated[QueryExecuteModel,Body(example={"query":"SELECT current_date"})], response:Response,auth_header: str = Depends(auth_header)):
    """
    This Endpoint will execute given SELECT query in Mysql Server.
    """

    resp = execute_query(query.query)

    if resp.success:
        response.status_code = 200
        return resp
    
    else:
        raise HTTPException(status_code=500, detail=resp.msg)
    
@app.get("/api/songs/search",response_model=ListResponseModel,tags=["YouTube Music"],responses={404: {
            "description": "Not Found",
            "content":{"application/json":{"example":{"status_code":404,'msg':"No results found."}}},
        }})
async def search_songs(query,response:Response,auth_header: str = Depends(auth_header)):
    """
    This endpoint will search the given song name in YouTube Music.
    """
    resp = youtube_music_api_instance.search(query)

    if resp['success']:
        response.status_code = 200
        return resp
    
    else:
        raise HTTPException(status_code=404, detail="No results found.")
    
@app.get("/api/songs/lyrics",response_model=SingleResponseModel,tags=["YouTube Music"],responses={404: {
            "description": "Not Found",
            "content":{"application/json":{"example":{"status_code":404,'msg':"No results found."}}},
        }})
async def get_lyrics(video_id,response:Response,auth_header: str = Depends(auth_header)):
    """
    This endpoint will fetch the lyrics of the song from YouTube Music.
    """

    resp = youtube_music_api_instance.fetch_lyrics(video_id)

    if resp['success']:
        response.status_code = 200
        return resp
    
    else:
        raise HTTPException(status_code=404, detail="No results found.")
    
@app.get("/api/songs/get_link",response_model=DictResponseModel,tags=["YouTube Music"],responses={404: {
            "description": "Not Found",
            "content":{"application/json":{"example":{"status_code":404,'msg':"No results found."}}},
        }})
async def get_dircet_link(video_id,response:Response,auth_header: str = Depends(auth_header)):
    """
    This endpoint will get the direct stream link for a song from YouTube Music.
    """

    resp = youtube_music_api_instance.get_direct_link(video_id)

    if resp['success']:
        response.status_code = 200
        return resp
    
    else:
        raise HTTPException(status_code=404, detail="No results found.")
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)