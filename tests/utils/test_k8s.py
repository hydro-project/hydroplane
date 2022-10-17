from decimal import Decimal

from hydroplane.models.container_spec import (ContainerSpec, EnvironmentVariable, PortMapping,
                                              ResourceSpec)
from hydroplane.models.process_spec import ProcessSpec
from hydroplane.models.secret import SecretValue, SecretSource
from hydroplane.utils.k8s import process_spec_to_pod_manifest, resource_spec_to_manifest


def test_process_spec_to_pod_manifest_basic():
    spec = ProcessSpec(
        process_name='basic',
        container=ContainerSpec(
            image_uri='foo/bar'
        )
    )

    manifest = process_spec_to_pod_manifest(spec)

    assert manifest == {
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {
            'name': 'basic'
        },
        'spec': {
            'containers': [
                {
                    'image': 'foo/bar',
                    'name': 'basic',
                    'env': [],
                    'ports': []
                }
            ],
            'restartPolicy': 'Never'
        }
    }


def test_process_spec_to_pod_manifest_env_vars():
    spec = ProcessSpec(
        process_name='has_env_vars',
        container=ContainerSpec(
            image_uri='foo/bar',
            env=[
                EnvironmentVariable(
                    name='SOME_PROPERTY',
                    value='here is a cleartext property'
                ),
                EnvironmentVariable(
                    name='SECRET',
                    value=SecretValue(
                        secret_name='my_secret_name',
                        source=SecretSource.K8S_SECRET
                    )
                ),
                EnvironmentVariable(
                    name='NESTED_SECRET',
                    value=SecretValue(
                        secret_name='nested_secret',
                        key='my_key',
                        source=SecretSource.K8S_SECRET
                    )
                )
            ]
        )
    )

    manifest = process_spec_to_pod_manifest(spec)

    assert manifest['spec']['containers'][0]['env'] == [
        {
            'name': 'SOME_PROPERTY',
            'value': 'here is a cleartext property'
        },
        {
            'name': 'SECRET',
            'valueFrom': {
                'secretRef': {
                    'name': 'my_secret_name'
                }
            }
        },
        {
            'name': 'NESTED_SECRET',
            'valueFrom': {
                'secretRef': {
                    'name': 'nested_secret',
                    'key': 'my_key'
                }
            }
        }
    ]


def test_process_spec_to_pod_manifest_ports():
    spec = ProcessSpec(
        process_name='testing-ports',
        container=ContainerSpec(
            image_uri='foo/bar',
            ports=[
                PortMapping(
                    container_port=7080
                ),
                PortMapping(
                    container_port=9090,
                    host_port=12345
                ),
                PortMapping(
                    container_port=53,
                    name='dns'
                )
            ]
        )
    )

    manifest = process_spec_to_pod_manifest(spec)

    assert manifest['spec']['containers'][0]['ports'] == [
        {
            'containerPort': 7080
        },
        {
            'containerPort': 9090
        },
        {
            'containerPort': 53,
            'name': 'dns'
        }
    ]


def test_process_spec_to_pod_manifest_resource_limits():
    spec = ProcessSpec(
        process_name='just_requests',
        container=ContainerSpec(
            image_uri='foo/bar',
            resource_request=ResourceSpec(
                cpu_vcpu=Decimal('1.5')
            )
        )
    )

    manifest = process_spec_to_pod_manifest(spec)

    assert manifest['spec']['containers'][0]['resources'] == {
        'requests': {
            'cpu': '1.5'
        }
    }

    spec = ProcessSpec(
        process_name='requests_and_limits',
        container=ContainerSpec(
            image_uri='foo/bar',
            resource_request=ResourceSpec(
                cpu_vcpu=Decimal('1.5')
            ),
            resource_limit=ResourceSpec(
                cpu_vcpu=Decimal('3.0'),
                memory_mib=256
            )
        )
    )

    manifest = process_spec_to_pod_manifest(spec)

    assert manifest['spec']['containers'][0]['resources'] == {
        'requests': {
            'cpu': '1.5'
        },
        'limits': {
            'cpu': '3.0',
            'memory': '256Mi'
        }
    }

    spec = ProcessSpec(
        process_name='just_limits',
        container=ContainerSpec(
            image_uri='foo/bar',
            resource_limit=ResourceSpec(
                cpu_vcpu=Decimal('3.0'),
                memory_mib=256
            )
        )
    )

    manifest = process_spec_to_pod_manifest(spec)

    assert manifest['spec']['containers'][0]['resources'] == {
        'limits': {
            'cpu': '3.0',
            'memory': '256Mi'
        }
    }


def test_resource_spec_to_manifest():
    assert resource_spec_to_manifest(ResourceSpec(
        cpu_vcpu=Decimal("2.5"),
        memory_mib=230
    )) == {
        'cpu': '2.5',
        'memory': '230Mi'
    }

    assert resource_spec_to_manifest(ResourceSpec(
        cpu_vcpu=Decimal("2.5")
    )) == {
        'cpu': '2.5'
    }

    assert resource_spec_to_manifest(ResourceSpec(
        memory_mib=230
    )) == {
        'memory': '230Mi'
    }

    assert resource_spec_to_manifest(ResourceSpec()) == {}
