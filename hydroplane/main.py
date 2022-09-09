from fastapi import FastAPI

from .models.process_spec import ProcessSpec

app = FastAPI()

@app.get('/')
async def root():
    return {
        "message": "Hello world!"
    }

@app.post('/start_process')
async def launch(process_spec: ProcessSpec):
    # TODO: this is a simple echo for now, just to test that things parse
    return process_spec
