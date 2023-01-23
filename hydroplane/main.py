import argparse
from getpass import getpass
import logging
import os
import sys

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi_utils.tasks import repeat_every
from pydantic import SecretStr
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn
import yaml

from .models.process_spec import ProcessSpec
from .config import Settings
from .runtimes.factory import get_runtime
from .secret_stores.factory import get_secret_store
from .utils.process_culler import ProcessCuller

logger = logging.getLogger('main')

app = FastAPI()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        content={
            'error': exc.status_code,
            'details': exc.detail
        },
        status_code=exc.status_code
    )


@app.on_event('startup')
@repeat_every(seconds=60, raise_exceptions=True)
async def cull_old_processes():
    if hasattr(app.state, 'process_culler'):
        app.state.process_culler.cull_old_processes()


@app.on_event('startup')
@repeat_every(seconds=30, raise_exceptions=True)
async def refresh_api_clients():
    if hasattr(app.state, 'runtime'):
        logger.debug('Refreshing API clients ...')
        app.state.runtime.refresh_api_clients()


@app.on_event('startup')
async def on_startup():
    # Load settings from the YAML file pointed to by the HYDROPLANE_CONF environment variable
    with open(os.getenv('HYDROPLANE_CONF'), 'r') as fp:
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

    if settings.process_culling is not None:
        app.state.process_culler = ProcessCuller(
            runtime=runtime,
            **settings.process_culling.dict()
        )

        logger.info(f'Process culling is enabled: {app.state.process_culler.info()}')
    else:
        logger.info('Process culling is disabled')

    app.state.runtime = runtime


@app.post('/process', status_code=201)
async def launch_process(
        process_spec: ProcessSpec
):
    app.state.runtime.start_process(process_spec)


@app.delete('/process/{process_name}')
async def terminate_process(
        process_name: str
):
    app.state.runtime.stop_process(process_name)


@app.get('/group/{group}')
async def list_processes_in_group(group: str):
    return app.state.runtime.list_processes(group)


@app.delete('/group/{group}')
async def terminate_group(group: str):
    app.state.runtime.stop_group(group)


@app.get('/process')
async def list_processes():
    return app.state.runtime.list_processes(group=None)


def main(args):
    if not os.path.exists(args.conf):
        sys.exit(f'Cannot find config file "{args.conf}" - did you specify the '
                 'right file with --conf?')

    os.environ['HYDROPLANE_CONF'] = args.conf

    uvicorn.run(
        app=app,
        host=args.host,
        port=args.port,
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', '-c', help='path to a Hydroplane config file '
                        '(default: %(default)s)', default='basic-config.yml')
    parser.add_argument('--host', '-H', help='hostname or IP on which to bind '
                        '(default: %(default)s)', default='127.0.0.1')
    parser.add_argument('--port', '-p', help='port on which to bind (default: %(default)s)',
                        type=int, default=8000)
    args = parser.parse_args()

    main(args)
