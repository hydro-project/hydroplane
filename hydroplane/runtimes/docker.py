import json
from typing import Literal, List

import docker
from fastapi import HTTPException
from pydantic import BaseModel

from ..models.process_info import ProcessInfo, SocketAddress
from ..models.process_spec import ProcessSpec
from ..models.secret import SecretValue
from ..secret_stores.secret_store import SecretStore
from .runtime import Runtime


RUNTIME_TYPE = 'docker'
HYDROPLANE_PROCESS_LABEL = 'hydroplane/process-id'


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

        if process_spec.has_public_ip:
            host_ip = '0.0.0.0'
        else:
            host_ip = '127.0.0.1'

        client.containers.run(
            image=container_spec.image_uri,
            name=process_spec.process_name,
            ports={str(p.container_port): (host_ip, p.host_port) for p in container_spec.ports},
            environment=container_env,
            command=container_spec.command,
            labels={HYDROPLANE_PROCESS_LABEL: process_spec.process_name},
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

    def list_processes(self) -> List[ProcessInfo]:
        client = docker.from_env()

        containers = client.containers.list(filters={
            'status': 'running',
            'label': HYDROPLANE_PROCESS_LABEL
        })

        process_infos = []

        for container in containers:
            socket_addresses = []

            for _, host_ifaces in container.attrs['NetworkSettings']['Ports'].items():
                for host_iface in host_ifaces:
                    socket_addresses.append(
                        SocketAddress(
                            host=host_iface['HostIp'],
                            port=int(host_iface['HostPort']),
                            is_public=(host_iface['HostIp'] == '0.0.0.0')
                        )
                    )

            process_infos.append(
                ProcessInfo(
                    process_name=container.name,
                    socket_addresses=socket_addresses
                )
            )

        return process_infos

    def refresh_api_clients():
        # Local Docker is fast enough that we don't really need to keep clients refreshed
        pass
