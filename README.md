# TCP-Client-Server

Implementation of the TCP protocol using UDP protocol in Python.

The cliente_main.py file should be run alongside the server_main.py file.

As soon as cliente_main.py (client side) starts running, it will start sending packages to the server, which, in turn, will send response packages back to the client.

Each package can be successfully sent or it can be lost.

The behavior of each side of the application follows the basic TCP workflow.

The application ends when the client side sends all the pakages and receives a proper response for each one.
Then, on the client side, some execution statistics are shown.
