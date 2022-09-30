from fastapi import FastAPI

from .models.process_spec import ProcessSpec

app = FastAPI()


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
