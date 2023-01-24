import os
import json
from typing import Dict, List, Optional

from fastapi import HTTPException
from kubernetes.client.exceptions import ApiException

from ..models.process_info import ProcessInfo, SocketAddress
from ..models.container_spec import ResourceSpec
from ..models.process_spec import ProcessSpec
from ..models.secret import ProcessSecret


HYDROPLANE_PROCESS_LABEL = 'hydroplane/process-id'
HYDROPLANE_GROUP_LABEL = 'hydroplane/group-id'


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
        if isinstance(e.value, ProcessSecret):
            secret_value = e.value

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
            env.append({'name': e.name, 'value': e.value})

    ports = []

    for i, p in enumerate(container_spec.ports):
        # Ignoring the port mapping's host port here, since k8s will handle binding container ports
        # to host ports for us
        container_port = {
            'containerPort': p.container_port,
            'protocol': p.protocol.value.upper()
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

    if container_spec.command is not None:
        main_container_manifest['command'] = container_spec.command

    labels = {
        HYDROPLANE_PROCESS_LABEL: process_spec.process_name,
    }

    if process_spec.group is not None:
        labels[HYDROPLANE_GROUP_LABEL] = process_spec.group

    pod_manifest = {
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {
            'name': process_spec.process_name,
            'labels': labels
        },
        'spec': {
            'containers': [main_container_manifest],
            'restartPolicy': 'Always'
        }
    }

    return pod_manifest


def process_spec_to_service_manifest(process_spec: ProcessSpec) -> dict:
    # We're going to expose the pod as a NodePort service, so that it's visible externally
    # without a load balancer sitting in the middle. This is a bit unorthodox (a lot of k8s
    # assumes that you've got fungible pods fronted by a load balancer), but for our purposes
    # it'll work just fine.

    container_spec = process_spec.container

    labels = {
        HYDROPLANE_PROCESS_LABEL: process_spec.process_name
    }

    if process_spec.group is not None:
        labels[HYDROPLANE_GROUP_LABEL] = process_spec.group

    service_manifest = {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': process_spec.process_name,
            'labels': labels
        },
        'spec': {
            'type': 'NodePort' if process_spec.has_public_ip else 'ClusterIP',
            'selector': {
                HYDROPLANE_PROCESS_LABEL: process_spec.process_name
            },
            'ports': [
                {'port': p.container_port, 'protocol': p.protocol.name}
                for p in container_spec.ports
            ]
        }
    }

    return service_manifest


def resource_spec_to_manifest(spec: ResourceSpec) -> dict:
    manifest = {}

    if spec.cpu_vcpu is not None:
        manifest['cpu'] = str(spec.cpu_vcpu)

    if spec.memory_mib is not None:
        manifest['memory'] = f"{spec.memory_mib}Mi"

    return manifest


def k8s_api_exception_to_http_exception(e: ApiException) -> HTTPException:
    return HTTPException(
        status_code=e.status,
        detail=f"{e.reason}: {e.body}"
    )


def k8s_start_process(k8s_client, namespace: str, process_spec: ProcessSpec):
    pod_manifest = process_spec_to_pod_manifest(process_spec)

    try:
        k8s_client.create_namespaced_pod(
            body=pod_manifest,
            namespace=namespace
        )
    except ApiException as e:
        if e.status == 409 and e.reason == 'Conflict':
            raise HTTPException(
                status_code=409,
                detail=f'A pod named "{process_spec.process_name}" already exists'
            )
        else:
            raise k8s_api_exception_to_http_exception(e)

    service_manifest = process_spec_to_service_manifest(process_spec)

    try:
        k8s_client.create_namespaced_service(
            body=service_manifest,
            namespace=namespace
        )
    except ApiException as e:
        if e.status == 409 and e.reason == 'Conflict':
            raise HTTPException(
                status_code=409,
                detail=f'A service named "{process_spec.process_name}" already exists'
            )
        else:
            raise k8s_api_exception_to_http_exception(e)


def k8s_stop_process(k8s_client, namespace: str, process_name: str):
    try:
        k8s_client.delete_namespaced_pod(
            name=process_name,
            namespace=namespace
        )
    except ApiException as e:
        if e.status == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Process '{process_name}' not found"
            )
        else:
            raise k8s_api_exception_to_http_exception(e)

    service_list = k8s_client.list_namespaced_service(
        label_selector=f'{HYDROPLANE_PROCESS_LABEL}={process_name}',
        namespace=namespace
    )

    for service in service_list.items:
        k8s_client.delete_namespaced_service(
            name=service.metadata.name,
            namespace=namespace
        )


def k8s_stop_group(k8s_client, namespace: str, group: str):
    pods = k8s_client.list_namespaced_pod(
        label_selector=f'{HYDROPLANE_GROUP_LABEL}={group}',
        namespace=namespace
    )

    services = k8s_client.list_namespaced_service(
        label_selector=f'{HYDROPLANE_GROUP_LABEL}={group}',
        namespace=namespace
    )

    for pod in pods.items:
        k8s_client.delete_namespaced_pod(
            name=pod.metadata.name,
            namespace=namespace
        )

    for service in services.items:
        k8s_client.delete_namespaced_service(
            name=service.metadata.name,
            namespace=namespace
        )


def k8s_list_processes(k8s_client, namespace: str, group: str) -> List[ProcessInfo]:
    # Pods will tell us the internal IP addresses of the nodes they're running on, but
    # not what the external IP addresses of those nodes are (or if they have them at all). We
    # need this information to tell the caller which node to talk to, so we'll list the
    # cluster's nodes and establish a map from internal to external IPs from that.
    nodes = k8s_client.list_node()

    node_private_to_public_ip: Dict[str, Optional[str]] = {}

    for node in nodes.items:
        external_ip = None
        internal_ip = None
        hostname = None

        for address in node.status.addresses:
            if address.type == 'ExternalIP':
                external_ip = address.address
            elif address.type == 'InternalIP':
                internal_ip = address.address
            elif address.type == 'Hostname':
                hostname = address.address

        if internal_ip is None:
            raise RuntimeError(f'Unable to determine internal IP for node {hostname}')

        node_private_to_public_ip[internal_ip] = external_ip

    if group is not None:
        label_selector = f"{HYDROPLANE_GROUP_LABEL}={group}"
    else:
        label_selector = HYDROPLANE_PROCESS_LABEL

    services = k8s_client.list_namespaced_service(
        label_selector=label_selector,
        namespace=namespace
    )

    pods = k8s_client.list_namespaced_pod(
        label_selector=label_selector,
        namespace=namespace
    )

    pods_by_name = {pod.metadata.labels[HYDROPLANE_PROCESS_LABEL]: pod for pod in pods.items}

    process_infos = []

    for service in services.items:
        process_name = service.metadata.labels[HYDROPLANE_PROCESS_LABEL]
        process_group = service.metadata.labels.get(HYDROPLANE_GROUP_LABEL)

        pod = pods_by_name[process_name]

        service_type = service.spec.type

        socket_addresses = []

        for port_spec in service.spec.ports:
            # For public services, node_port will be specified and will be the same on each
            # port. For private services, it will be None and port will be specified instead.
            port = port_spec.node_port or port_spec.port

            pod_private_ip = pod.status.host_ip

            if service_type == 'NodePort':
                # We're exposing a NodePort service, so this process is public
                socket_ip = node_private_to_public_ip[pod_private_ip]

                if socket_ip is None:
                    raise RuntimeError(
                        f"We expected the public process {process_name} to be running on a "
                        "node with an external IP address, but the node it's running on "
                        f"({pod_private_ip}) doesn't have one."
                    )

                is_public = True
            else:
                # We're exposing a ClusterIP service, so this process is private
                socket_ip = service.spec.cluster_ip
                is_public = False

            socket_addresses.append(
                SocketAddress(
                    host=socket_ip,
                    port=port,
                    is_public=is_public
                )
            )

        process_infos.append(ProcessInfo(
            process_name=process_name,
            group=process_group,
            socket_addresses=socket_addresses,
            created=service.metadata.creation_timestamp
        ))

    return process_infos
