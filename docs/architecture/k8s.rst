How Hydroplane Interacts with Kubernetes
========================================

At this point, Hydroplane has a couple backends that are managed offerings of Kubernetes (:doc:`EKS</runtimes/eks>` and :doc:`GKE</runtimes/gke>`, at time of writing). This document provides some more details on the way that Hydroplane reifies processes into Kubernetes' various primitives.

Each Hydroplane process is run in Kubernetes as a single-pod deployment and an associated service. The service is there to give Kubernetes something to expose to the Internet when a process has a public IP address, and to give processes an easy way to name one another without relying on any kind of third-party service discovery mechanism. The deployment is there to ensure that something is keeping a process's pod scheduled even if the pod is preempted or evicted. The pod contains the actual container that the process is running.

If you want to familiarize yourself with Kubernetes' services, pods and deployments, I'd recommend this `article by Matthew Palmer <https://matthewpalmer.net/kubernetes-app-developer/articles/service-kubernetes-example-tutorial.html>`_.

Public and Private Processes Use Different Services
---------------------------------------------------

Private services only need to be routable and discoverable within the cluster, so their associated services are ``ClusterIP`` services. Public services need to be routable from outside the cluster, so we have to handle them separately.

In a typical Kubernetes service where you have one service backing an auto-scaling collection of pods, you'd put a ``LoadBalancer`` service in front of the pods that load-balances traffic between them. In our case, we're expecting something higher-level than Hydroplane to do things like load balancing, so we want each process to be named and exposed individually. If we were to create a ``LoadBalancer`` service per process, we'd also be creating a separate **load balancer** per process, and load balancers in public clouds (particularly in AWS) are really expensive.

To avoid the cost overhead of having a load balancer per process, we create a ``NodePort`` service for each process that routes only to that process's pod. A ``NodePort`` service exposes a high-numbered port on every node in the cluster, and all traffic to that port on any cluster node is transparently routed to the pod by Kubernetes' overlay network.

Using ``NodePort`` services does what we want without additional cloud resources, but it also makes it look from the client's perspective as though the process is running on every node in the cluster at once. This is inconsistent with the abstraction that Hydroplane's list operation presents. To maintain the illusion that the process is only accessible from one node, we do some introspection to determine the cluster node that the pod is actually running on, and treat that cluster node's IP address as the process' IP address when listing running processes.

Process Status
--------------

Kubernetes can create ``ClusterIP`` and ``NodePort`` services very quickly, but sometimes it may take a while for a deployment's pod to start after Hydroplane successfully submits the deployment's spec. Usually, delays in pod creation are caused by resource pressure: if Kubernetes doesn't have enough remaining resources to accommodate the pod, it may have to scale up to acquire those resources.

When listing processes, Hydroplane provides an associated **status** for each process. If a process's status is ``RUNNING``, this means that all the process's resources are ready and the process should be able to accept connections. If the status is ``STARTING``, some of those resources are ready and others are not.

Node Selectors
--------------

A process spec can contain **node selectors**, which are translated by Hydroplane directly into Kubernetes node selectors. Node selectors constrain which node(s) the process is allowed to run on. Each node selector is a label name/label value pair, and only those nodes that have a label whose name and value both match the selector will be available for the node to execute upon.

This can be a great way to force a process to run on a specific node, or on a node with a specific kind of resource. For instance, `examples/nginx-advanced.json <https://github.com/hydro-project/hydroplane/blob/main/examples/nginx-advanced.json>`_ uses the ``kubernetes.io/hostname`` label to constrain its process to a particular node.
