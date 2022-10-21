from fastapi import FastAPI

from .models.process_spec import ProcessSpec
from .config import get_settings
from .runtimes.factory import get_runtime
from .secret_stores.factory import get_secret_store

app = FastAPI()


@app.on_event('startup')
async def on_startup():
    # Make sure settings are warmed up before we start, so we can prompt for any secret settings
    # before we fully come online in dev mode.
    settings = get_settings()

    secret_store = get_secret_store()
    runtime = get_runtime(secret_store, settings)

    app.state.runtime = runtime


@app.post('/launch')
async def launch(
        process_spec: ProcessSpec
):
    app.state.runtime.start_process(process_spec)


@app.post('/terminate/process/{process_name}')
async def terminate(
        process_name: str
):
    app.state.runtime.stop_process(process_name)


@app.get('/list')
async def list():
    return app.state.runtime.list_processes()
