import requests
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import asyncio
from asyncio import WindowsSelectorEventLoopPolicy
import psycopg
from config import token_weather
from weather import get_forecast

app = FastAPI()



async def connect():
    connect_db = await psycopg.AsyncConnection.connect(
        "dbname=db1 user=postgres password=vik")
    return connect_db

@app.get("/names")
async def get_all_names(request: Request):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                sql = '''
                SELECT * FROM names;
                '''
                await cursor.execute(sql)
                result = await cursor.fetchall()
                return result
    except Exception as e:
        return e
@app.get('/weather')
async def get_weather(request:Request):
    return get_forecast(token_weather)