import socket

server_address = ("localhost", 8000)
buffer_size = 16


if __name__ == "__main__":
    # crear socket UDP
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # bindear socket a direccion y puerto de servidor
    socket.bind(server_address)

    # loop para recibir mensajes del cliente
    while True:
        # recibir mensajes con funcion receive_full_message 
        message, client_address = socket.recvfrom(buffer_size)
        print(f"Mensaje recibido de {client_address}: {message.decode()}")

        