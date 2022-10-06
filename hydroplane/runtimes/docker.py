import json
from typing import Literal

import docker
from fastapi import HTTPException
from pydantic import BaseModel

from ..models.process_spec import ProcessSpec
from ..models.secret import SecretValue
from ..secret_stores.secret_store import SecretStore
from .runtime import Runtime


RUNTIME_TYPE = 'docker'


class Settings(BaseModel):
    runtime_type: Literal[RUNTIME_TYPE] = RUNTIME_TYPE


class DockerRuntime(Runtime):
    def __init__(self, settings: Settings, secret_store: SecretStore):
        self.secret_store = secret_store

    def start_process(self, process_spec: ProcessSpec):
        client = docker.from_env()

        container_spec = process_spec.container

        if container_spec.username is not None or container_spec.password is not None:
            client.login(
                username=container_spec.username,
                password=self.secret_store.get_secret(container_spec.password)
            )

        container_env = {}

        for env_var in container_spec.env:
            if type(env_var.value) is SecretValue:
                secret_info = env_var.value

                env_value = self.secret_store.get_secret(secret_info.secret_name)

                if secret_info.key is not None:
                    env_value = json.loads(env_value)[secret_info.key]

                container_env[env_var.name] = env_value
            else:
                container_env[env_var.name] = env_var.value

        client.containers.run(
            image=container_spec.image_uri,
            name=process_spec.process_name,
            ports={str(p.container_port): p.host_port for p in container_spec.ports},
            environment=container_env,
            command=container_spec.command,
            auto_remove=True,
            detach=True,
        )

    def stop_process(self, process_name: str):
        client = docker.from_env()

        try:
            container = client.containers.get(process_name)
        except docker.errors.NotFound:
            raise HTTPException(status_code=404, detail=f"Process '{process_name} not found'")

        container.kill()
