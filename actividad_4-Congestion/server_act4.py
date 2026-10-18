import socket
import socketTCP_CONGESTION

server_address = ("localhost", 8000)


# APARTADO DE PRUEBAS

# # SERVER

# server_socketTCP = socketTCP_CONGESTION.SocketTCP()
# server_socketTCP.bind(server_address)
# connection_socketTCP, new_address = server_socketTCP.accept()

# # test 1
# buff_size = 16
# full_message = connection_socketTCP.recv(buff_size, mode= "go_back_n")
# print("Test 1 received:", full_message)
# if full_message == "Mensje de len=16".encode(): print("Test 1: Passed")
# else: print("Test 1: Failed")

# # test 2
# buff_size = 19
# full_message = connection_socketTCP.recv(buff_size, mode= "go_back_n")
# print("Test 2 received:", full_message)
# if full_message == "Mensaje de largo 19".encode(): print("Test 2: Passed")
# else: print("Test 2: Failed")

# # test 3
# buff_size = 14
# message_part_1 = connection_socketTCP.recv(buff_size, mode= "go_back_n")
# message_part_2 = connection_socketTCP.recv(buff_size, mode= "go_back_n")
# print("Test 3 received:", message_part_1 + message_part_2)
# if (message_part_1 + message_part_2) == "Mensaje de largo 19".encode(): print("Test 3: Passed")
# else: print("Test 3: Failed")#
# connection_socketTCP.close()

####################

# tests para debuugger:


# server_address = ("localhost", 8000)

# # Crear e iniciar el servidor
# server_socket = socketTCP_CONGESTION.SocketTCP()
# server_socket.bind(server_address)

# print("[SERVIDOR] Escuchando en", server_address)
# connection_socket, client_addr = server_socket.accept()
# print(f"[SERVIDOR] Conexión establecida desde: {client_addr}")

# # Recibir el mensaje largo
# buff_size = 1024
# print("\n[SERVIDOR] Recibiendo mensaje...")
# received_message = connection_socket.recv(buff_size, mode="go_back_n")

# print("\n[SERVIDOR] Resultado de recepción:")
# print("Mensaje:", received_message.decode(errors="ignore"))

# # Cierre de conexión
# print("\n[SERVIDOR] Esperando cierre de conexión...")
# connection_socket.recv_close()
# print("[SERVIDOR] Conexión cerrada.")

#######################

#TEST PARA 3.6 final

import socketTCP_CONGESTION

def run_server():
    server_address = ("localhost", 8000)
    server_socket = socketTCP_CONGESTION.SocketTCP()
    server_socket.bind(server_address)

    print("[SERVIDOR] Escuchando en", server_address)
    connection_socket, client_addr = server_socket.accept()
    print(f"[SERVIDOR] Conexión establecida desde: {client_addr}")

    buff_size = 2048
    print("\n[SERVIDOR] Recibiendo mensaje...")
    received_message = connection_socket.recv(buff_size, mode="go_back_n")

    print("\n[SERVIDOR] Resultado de recepción:")
    print("Mensaje:", received_message.decode(errors="ignore"))

    print("\n[SERVIDOR] Esperando cierre de conexión...")
    connection_socket.recv_close()
    print("[SERVIDOR] Conexión cerrada exitosamente.")

if __name__ == "__main__":
    run_server()





#######################


# if __name__ == "__main__":

#     # Crear socket TCP
#     server_socketTCP = socketTCP_CONGESTION.SocketTCP()

#     # Bind al puerto 8000
#     server_socketTCP.bind(server_address)

#     # Esperar conexión
#     connection_socketTCP, new_address = server_socketTCP.accept()

#     # Recibir el archivo completo
#     message = b""

#     while True:

#         part = connection_socketTCP.recv(1024, mode= "go_back_n")

#         if not part:
#             break

#         message += part

#         # Si se recibió menos que el buffer solicitado,
#         # probablemente ya recibimos todo.
#         if len(part) < 1024:
#             break

#     print(message.decode())

#     # Cerrar conexión
#     connection_socketTCP.recv_close()