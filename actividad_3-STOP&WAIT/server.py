import socket
import socketTCP

server_address = ("localhost", 8000)
buffer_size = 21


if __name__ == "__main__":
    ## crear socket UDP
    #socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#
    ## test 3 crear socketTCP para parsear los segmentos TCP recibidos
    #tcp_socket = socketTCP.SocketTCP()
#
    ## bindear socket a direccion y puerto de servidor
    #socket.bind(server_address)
#
    ## loop para recibir mensajes del cliente
    #while True:
    #    # recibir mensajes con funcion receive_full_message 
    #    message, client_address = socket.recvfrom(buffer_size)
    #    tcp_segment = tcp_socket.parse_segment(message)
    #    print(tcp_segment)

    # SERVER
    server_socketTCP = socketTCP.SocketTCP()
    server_socketTCP.bind(server_address)
    connection_socketTCP, new_address = server_socketTCP.accept()

    # test 1
    buff_size = 16
    full_message = connection_socketTCP.recv(buff_size)
    print("Test 1 received:", full_message)
    if full_message == "Mensje de len=16".encode(): print("Test 1: Passed")
    else: print("Test 1: Failed")

    # test 2
    buff_size = 19
    full_message = connection_socketTCP.recv(buff_size)
    print("Test 2 received:", full_message)
    if full_message == "Mensaje de largo 19".encode(): print("Test 2: Passed")
    else: print("Test 2: Failed")

    # test 3
    buff_size = 14
    message_part_1 = connection_socketTCP.recv(buff_size)
    message_part_2 = connection_socketTCP.recv(buff_size)
    print("Test 3 received:", message_part_1 + message_part_2)
    if (message_part_1 + message_part_2) == "Mensaje de largo 19".encode(): print("Test 3: Passed")
    else: print("Test 3: Failed")

    connection_socketTCP.close()


        