from decimal import Decimal

from hydroplane.models.container_spec import ContainerSpec
from pydantic import ValidationError
from pytest import raises


def test_container_spec_demarshaling_basic():
    spec = ContainerSpec.parse_obj({
        'image_uri': 'foo/bar'
    })

    assert spec.image_uri == 'foo/bar'
    assert spec.ports == []
    assert spec.env == []
    assert spec.username == None
    assert spec.password == None


def test_container_spec_default_container_port():
    spec = ContainerSpec.parse_obj({
        'image_uri': 'foo/bar',
        'ports': [
            {'container_port': 9090}
        ]
    })

    assert len(spec.ports) == 1
    assert spec.ports[0].container_port == 9090
    assert spec.ports[0].host_port == 9090


def test_container_spec_with_out_of_bounds_port_raises():
    with raises(ValidationError):
        ContainerSpec.parse_obj({
            'image_uri': 'whacky_ports',
            'ports': [
                {'container_port': 8675309}
            ]
        })


def test_container_spec_with_missing_host_port_raises():
    with raises(ValidationError):
        ContainerSpec.parse_obj({
            'image_uri': 'missing_port',
            'ports': [{}]
        })


def test_resource_spec_in_bounds():
    spec = ContainerSpec.parse_obj({
        'image_uri': 'foo/baz',
        'resource_request': {
            'cpu_vcpu': '0.5',
            'memory_mib': 256
        }
    })

    assert spec.resource_request is not None
    assert spec.resource_request.cpu_vcpu == Decimal("0.5")
    assert spec.resource_request.memory_mib == 256


def test_partial_resource_limit():
    spec = ContainerSpec.parse_obj({
        'image_uri': 'foo/baz',
        'resource_request': {
            'cpu_vcpu': '2.5'
        },
        'resource_limit': {
            'cpu_vcpu': '3.5'
        }
    })

    assert spec.resource_limit.cpu_vcpu == Decimal('3.5')
    assert spec.resource_limit.memory_mib is None

    spec = ContainerSpec.parse_obj({
        'image_uri': 'foo/baz',
        'resource_request': {
            'cpu_vcpu': '2.0'
        },
        'resource_limit': {
            'memory_mib': 256
        }
    })

    assert spec.resource_limit.cpu_vcpu is None
    assert spec.resource_limit.memory_mib == 256


def test_resource_spec_out_of_bounds_raises():
    with raises(ValidationError):
        spec = ContainerSpec.parse_obj({
            'image_uri': 'foo/baz',
            'resource_request': {
                'cpu_vcpu': '-1.0',
                'memory_mib': 256
            }
        })

    with raises(ValidationError):
        spec = ContainerSpec.parse_obj({
            'image_uri': 'foo/baz',
            'resource_request': {
                'cpu_vcpu': '2.0',
                'memory_mib': -256
            }
        })


def test_resource_request_greater_than_limit_raises():
    with raises(ValidationError):
        spec = ContainerSpec.parse_obj({
            'image_uri': 'foo/baz',
            'resource_request': {
                'cpu_vcpu': '1.0',
                'memory_mib': 512
            },
            'resource_limit': {
                'cpu_vcpu': '1.0',
                'memory_mib': 256
            }
        })

    with raises(ValidationError):
        spec = ContainerSpec.parse_obj({
            'image_uri': 'foo/baz',
            'resource_request': {
                'cpu_vcpu': '2.0',
                'memory_mib': 512
            },
            'resource_limit': {
                'cpu_vcpu': '1.0',
                'memory_mib': 512
            }
        })
