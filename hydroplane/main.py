from getpass import getpass
import logging
import os

from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from pydantic import SecretStr
import uvicorn
import yaml

from .models.process_spec import ProcessSpec
from .config import Settings
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
    # Load settings from the YAML file pointed to by the CONF environment variable
    with open(os.getenv('CONF'), 'r') as fp:
        settings = Settings.parse_obj(yaml.load(fp.read(), Loader=yaml.FullLoader))

    if settings.secret_store.secret_store_type == 'local':
        settings.secret_store.password = SecretStr(
            getpass('Enter local secret store password: ').strip()
        )
        if len(settings.secret_store.password) == 0:
            raise ValueError('Must provide a password for local secret stores')

    secret_store = get_secret_store(settings)
    runtime = get_runtime(secret_store, settings)
    runtime.refresh_api_clients()

    app.state.runtime = runtime


@app.post('/process', status_code=201)
async def launch(
        process_spec: ProcessSpec
):
    app.state.runtime.start_process(process_spec)


@app.delete('/process/{process_name}')
async def terminate_process(
        process_name: str
):
    app.state.runtime.stop_process(process_name)


@app.delete('/group/{group}')
async def terminate_group(group: str):
    app.state.runtime.stop_group(group)


@app.get('/process')
async def list_processes(group: str = None):
    return app.state.runtime.list_processes(group)


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
