import os
import json

from ..models.container_spec import ResourceSpec
from ..models.process_spec import ProcessSpec
from ..models.secret import SecretValue, SecretSource


def discover_k8s_api_version():
    """Figure out what version of the k8s API we should be using.

    Taking a page from awscli's book, we'll look at the KUBERNETES_EXEC_INFO environment variable to
    find the k8s API version we're supposed to use, and fall back to v1beta1 if it's not
    specified. v1beta1 should be supported in k8s up to 1.29 (which should GA around December of
    2023).
    """

    exec_info_raw = os.environ.get('KUBERNETES_EXEC_INFO', '')

    if not exec_info_raw:
        return 'client.authentication.k8s.io/v1beta1'

    try:
        exec_info = json.loads(exec_info_raw)
    except json.JSONDecodeError:
        raise ValueError(
            "The contents of the KUBERNETES_EXEC_INFO environment variable is "
            "malformed, so we can't the version of the Kubernetes API we're "
            "supposed to use from it."
        )

    if 'apiVersion' not in exec_info:
        raise ValueError('Unable to extract API version number from KUBERNETES_EXEC_INFO')

    return exec_info['apiVersion']


def process_spec_to_pod_manifest(process_spec: ProcessSpec) -> dict:
    """Converts a Hydroplane process spec into a Kubernetes pod definition.
    """
    container_spec = process_spec.container

    env = []

    for e in container_spec.env:
        if isinstance(e.value, SecretValue):
            secret_value = e.value

            if secret_value.source == SecretSource.K8S_SECRET:
                secret_ref = {
                    'name': secret_value.secret_name
                }

                if e.value.key is not None:
                    secret_ref['key'] = secret_value.key

                env.append({
                    'name': e.name,
                    'valueFrom': {
                        'secretRef': secret_ref
                    }
                })
            else:
                raise ValueError(f"Secret values with source {e.source} currently unsupported")
        else:
            env.append({'name': e.name, 'value': e.value})

    ports = []

    for i, p in enumerate(container_spec.ports):
        # Ignoring the port mapping's host port here, since k8s will handle binding container ports
        # to host ports for us
        container_port = {
            'containerPort': p.container_port
        }

        if p.name is not None:
            container_port['name'] = p.name

        ports.append(container_port)

    main_container_manifest = {
        'image': container_spec.image_uri,
        'name': process_spec.process_name,
        'env': env,
        'ports': ports
    }

    if container_spec.resource_request is not None:
        if 'resources' not in main_container_manifest:
            main_container_manifest['resources'] = {}

        main_container_manifest['resources']['requests'] = resource_spec_to_manifest(
            container_spec.resource_request
        )

    if container_spec.resource_limit is not None:
        if 'resources' not in main_container_manifest:
            main_container_manifest['resources'] = {}

        main_container_manifest['resources']['limits'] = resource_spec_to_manifest(
            container_spec.resource_limit
        )

    pod_manifest = {
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {
            'name': process_spec.process_name
        },
        'spec': {
            'containers': [main_container_manifest],
            'restartPolicy': 'Never'
        }
    }

    return pod_manifest


def resource_spec_to_manifest(spec: ResourceSpec) -> dict:
    manifest = {}

    if spec.cpu_vcpu is not None:
        manifest['cpu'] = str(spec.cpu_vcpu)

    if spec.memory_mib is not None:
        manifest['memory'] = f"{spec.memory_mib}Mi"

    return manifest
