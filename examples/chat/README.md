# Chat Example

The JSON files in this directory describe three processes: a **server** and two **clients**. Details of how the client and server work can be found [in the hydroflow repo](https://github.com/hydro-project/hydroflow/tree/main/hydroflow/examples/chat).

## How to Launch the Processes

```bash
# Launch the server
curl -s -X POST -H "Content-Type: application/json" -d @server.json http://<hydroplane instance address>/process

# Give the server some time to warm up
sleep 5

# Start the clients
curl -s -X POST -H "Content-Type: application/json" -d @chat-client-alice.json http://<hydroplane instance address>/process
curl -s -X POST -H "Content-Type: application/json" -d @chat-client-bob.json http://<hydroplane instance address>/process
```


## How to Destroy the Processes

```bash
curl -s -X DELETE http://localhost:8000/process/chat-server
curl -s -X DELETE http://localhost:8000/process/chat-client-alice
curl -s -X DELETE http://localhost:8000/process/chat-client-bob
```
