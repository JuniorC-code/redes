import sys
import socketTCP_CONGESTION
import time

buffer = 21
address = ("localhost", 8000)


#APARTADO DE PRUEBAS ANTERIORES

# CLIENT

# client_socketTCP = socketTCP_CONGESTION.SocketTCP()
# client_socketTCP.connect(address)

# # test 1
# message = "Mensje de len=16".encode()
# client_socketTCP.send(message, mode= "go_back_n")


# # test 2

# message = "Mensaje de largo 19".encode()
# print("mandaondo cosas")
# client_socketTCP.send(message, mode= "go_back_n")

# # test 3
# print("test3")
# message = "Mensaje de largo 19".encode()
# client_socketTCP.send(message, mode= "go_back_n")

# print("se cierra conexion?")
# client_socketTCP.recv_close()

###############################


if __name__ == "__main__":

    # Obtener argumentos:
    # python3 cliente.py localhost 8000 < archivo.txt
    host = sys.argv[1]
    port = int(sys.argv[2])

    address = (host, port)

    # Crear SocketTCP
    client_socketTCP = socketTCP_CONGESTION.SocketTCP()

    # Conectarse al servidor
    client_socketTCP.connect(address)

    # Leer todo el archivo desde stdin
    message = sys.stdin.buffer.read()

    # Enviar el contenido utilizando nuestro protocolo
    client_socketTCP.send(message, mode= "go_back_n")

    # Cerrar conexión
    client_socketTCP.close()