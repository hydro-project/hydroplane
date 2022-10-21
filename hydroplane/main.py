import logging
import os

from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
import uvicorn

from .models.process_spec import ProcessSpec
from .config import get_settings
from .runtimes.factory import get_runtime
from .secret_stores.factory import get_secret_store

logger = logging.getLogger('main')

app = FastAPI()


@app.on_event('startup')
@repeat_every(seconds=30, raise_exceptions=True)
async def refresh_api_clients():
    if hasattr(app.state, 'runtime'):
        logger.debug('Refreshing API clients ...')
        app.state.runtime.refresh_api_clients()


@app.on_event('startup')
async def on_startup():
    # Make sure settings are warmed up before we start, so we can prompt for any secret settings
    # before we fully come online in dev mode.
    settings = get_settings()

    secret_store = get_secret_store()
    runtime = get_runtime(secret_store, settings)
    runtime.refresh_api_clients()

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


if __name__ == '__main__':
    uvicorn.run(
        app=app,
        port=8000,
        log_config={
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s - %(levelname)s - [%(name)s] %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard',
                    'stream': 'ext://sys.stdout'
                }
            },
            'loggers': {
                'uvicorn': {
                    'error': {
                        'propagate': True
                    }
                }
            },
            'root': {
                'handlers': ['console'],
                'propagate': False,
                'level': os.getenv('LOG_LEVEL', 'INFO').upper()
            }
        }
    )
