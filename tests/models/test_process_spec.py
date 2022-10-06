from hydroplane.models.process_spec import ProcessSpec


def test_process_spec_demarshaling_basic():
    spec = ProcessSpec.parse_obj({
        'process_name': 'test',
        'container': {
            'image_uri': 'foo/baz'
        }
    })

    assert spec.process_name == 'test'
    assert spec.container.image_uri == 'foo/baz'
    assert spec.orchestrator_config == {}
