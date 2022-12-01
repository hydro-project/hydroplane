# Chat Example

The JSON files in this directory describe three processes: a **server** and two **clients**. Details of how the client and server work can be found [in the hydroflow repo](https://github.com/hydro-project/hydroflow/tree/main/hydroflow/examples/chat).

## How to Launch the Processes

```bash
# Launch the server (from the root of this repo)
bin/hpctl start examples/chat/chat-server.json

# Give the server some time to warm up
sleep 5

# Start the clients
bin/hpctl start examples/chat/chat-client-alice.json
bin/hpctl start examples/chat/chat-client-bob.json
```

## Checking If It Worked

In the ``docker`` runtime:

```
docker ps
docker logs chat-server
docker logs chat-client-alice
docker logs chat-client-bob
```

In the ``eks`` runtime:

```
kubectl logs pod/chat-server
kubectl logs pod/chat-client-alice
kubectl logs pod/chat-client-bob
```

## How to Destroy the Processes

```bash
bin/hpctl stop -g chat-clients
bin/hpctl stop chat-server
```
