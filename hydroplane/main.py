from fastapi import FastAPI

from .models.process_spec import ProcessSpec
from .config import get_settings
from .runtimes.factory import get_runtime
from .secret_stores.factory import get_secret_store

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
    settings = get_settings()
    secret_store = get_secret_store()
    runtime = get_runtime(secret_store, settings)

    runtime.start_process(process_spec)


# FIXME doesn't quite work yet

# @app.post('/terminate')
# async def terminate(process_name: str):
#     settings = get_settings()
#     secret_store = get_secret_store()
#     runtime = get_runtime(secret_store, settings)

#     runtime.stop_process(process_name)
