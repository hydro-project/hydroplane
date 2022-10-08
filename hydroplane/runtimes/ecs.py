from typing import Literal, Optional, Tuple

import boto3
from pydantic import BaseModel, Field

from ..models.aws import AWSCredentials
from ..models.process_spec import ProcessSpec, ResourceSpec
from ..models.secret import SecretValue, SecretSource
from ..secret_stores.secret_store import SecretStore
from .runtime import Runtime
from ..utils.aws import boto3_client_from_creds

RUNTIME_TYPE = 'ecs'

# Size of a gibibyte in mibibytes
GIBIBYTE = 2 ** 10

# Valid memory unit values for each supported CPU unit value in ECS
VALID_RESOURCE_UNIT_COMBOS = {
    256: (512, 1024, 2048),
    512: {x for x in range(1 * GIBIBYTE, 4 * GIBIBYTE + 1, GIBIBYTE)},
    1024: {x for x in range(2 * GIBIBYTE, 8 * GIBIBYTE + 1, GIBIBYTE)},
    2048: {x for x in range(4 * GIBIBYTE, 16 * GIBIBYTE + 1, GIBIBYTE)},
    4096: {x for x in range(8 * GIBIBYTE, 30 * GIBIBYTE + 1, GIBIBYTE)},
    8192: {x for x in range(16 * GIBIBYTE, 60 * GIBIBYTE + 1, 4 * GIBIBYTE)},
    16384: {x for x in range(32 * GIBIBYTE, 120 * GIBIBYTE + 1, 8 * GIBIBYTE)}
}


class TaskDefinitionName(BaseModel):
    """The unique identifier for a task definition"""
    family: str
    revision: Optional[str] = Field('ACTIVE')


class OrchestratorConfig(BaseModel):
    cluster: str
    task_definition = TaskDefinitionName
    create_task_definition_if_not_exists: bool = True


class Settings(BaseModel):
    runtime_type: Literal[RUNTIME_TYPE] = RUNTIME_TYPE

    credentials: AWSCredentials


def resource_spec_to_ecs_units(resource_spec: ResourceSpec) -> Tuple[str, str]:
    # One vCPU = 1024 CPU units
    cpu_units = int(resource_spec.cpu_vcpu * 1024)

    # Memory units are already specified in MiBs, so no conversion is necessary here.
    memory_units = resource_spec.memory_mib

    if cpu_units not in VALID_RESOURCE_UNIT_COMBOS.keys():
        raise ValueError(
            f'ECS cannot create tasks with {cpu_units} CPU units ({resource_spec.cpu_vcpu} vCPUs). '
            f"Valid values are {', '.join(sorted(VALID_RESOURCE_UNIT_COMBOS.keys()))}"
        )

    if memory_units not in VALID_RESOURCE_UNIT_COMBOS[cpu_units]:
        raise ValueError(
            f"ECS cannot create tasks with {cpu_units} CPU units ({resource_spec.cpu_vcpu} vCPUs) "
            f"and {memory_units} MiB of memory. Valid values for memory at {cpu_units} CPU units "
            f"are {', '.join(f'{x} MiB' for x in VALID_RESOURCE_UNIT_COMBOS[cpu_units])}"
        )

    # Both units are specified as strings in ECS's task definitions, so we'll return them as strings
    return (str(cpu_units), str(memory_units))


def process_spec_to_task_definition(process_spec: ProcessSpec, secret_store: SecretStore) -> dict:
    orchestrator_config = OrchestratorConfig.parse_obj(
        process_spec.orchestrator_config
    )

    container_spec = process_spec.container

    cpu_units, memory_units = resource_spec_to_ecs_units(container_spec.resource_request)

    if container_spec.resource_limit is not None:
        _, memory_limit = resource_spec_to_ecs_units(container_spec.resource_limit)
    else:
        memory_limit = None

    # TODO: configure repositoryCredentials for private repo access

    container_definition = {
        'name': process_spec.process_name,
        'image': container_spec.image_uri,
        'cpu': cpu_units,
        'memory': memory_units,
        'memoryReservation': memory_limit,
        'portMappings': [
            {'containerPort': p.container_port, 'hostPort': p.host_port}
            for p in container_spec.ports
        ],
        'environment': [
            {
                'name': e.name,
                'value': e.value
            }
            for e in container_spec.env
            if isinstance(e, str)
        ],
        # We can only pass secrets to the container that are stored in an AWS secret store
        'secrets': [
            {
                'name': e.name,
                'value': e.value.secret_name
            }
            for e in container_spec.env
            if isinstance(e, SecretValue) and
            e.source in (SecretSource.AWS_SSM, SecretSource.AWS_SECRETS_MANAGER)
        ]
    }

    task_definition = {
        'family': orchestrator_config.task_definition.family,
        'containerDefinitions': [container_definition],
        'requiresCompatibilities': ['FARGATE'],
        'networkMode': 'awsvpc',
    }

    return task_definition


class ECSRuntime(Runtime):
    def __init__(self, settings: Settings, secret_store: SecretStore):
        self.settings = settings
        self.secret_store = secret_store


    def start_process(self, process_spec: ProcessSpec):
        client = self.get_boto3_client('ecs')

        task_definition = process_spec_to_task_definition(process_spec)

        family = orchestrator_config.task_definition.family
        revision = orchestrator_config.task_definition.revision



        if isinstance(orchestrator_config.task_definition, TaskDefinition):
            # Caller has supplied a new task definition rather than a pointer to an existing
            # one. We'll need to create a task definition if one doesn't already exist.

            client = boto3_client_from_creds(self.settings.credentials)

            task_definition_paginator = client.get_paginator('list_task_definitions')

            for task_definition_page in task_definition_paginator.paginate(familyPrefix=family):
                for task_definition_arn in task_definition_page['taskDefinitionArns']:
                    task_definition = client.describe_task_definition(
                        taskDefinition=task_definition_arn
                    )






    def stop_process(self, process_name: str):
        client = boto3.client('ecs')
