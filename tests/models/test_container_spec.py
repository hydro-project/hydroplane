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
