from fastapi import FastAPI

from .models.process_spec import ProcessSpec
from .config import get_settings

app = FastAPI()


@app.on_event('startup')
async def on_startup():
    # Make sure settings are warmed up before we start
    get_settings()


@app.get('/')
async def root():
    return {
        "message": "Hello world!"
    }


@app.post('/launch')
async def launch(process_spec: ProcessSpec):
    return process_spec


@app.post('/terminate')
async def terminate(process_name: str):
    return process_name
