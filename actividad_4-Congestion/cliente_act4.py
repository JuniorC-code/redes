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
# message = "Mensaje de largo 19".encode()
# client_socketTCP.send(message, mode= "go_back_n")

# print("se cierra conexion?")
# client_socketTCP.recv_close()

###############################

# Pruebas para debugger


# server_address = ("localhost", 8000)

# # Crear e iniciar el cliente
# client = socketTCP_CONGESTION.SocketTCP()

# # Habilitar Control de Congestión y Modo Debug
# client.set_congestion_control_on(True)
# client.set_debug(True)

# print("[CLIENTE] Conectando al servidor...")
# client.connect(server_address)

# # Mensaje largo para enviar varios MSS (8 bytes cada uno)
# message = "Este es un mensaje de prueba largo para observar el control de congestión en acción!".encode()

# print(f"\n[CLIENTE] Enviando mensaje de {len(message)} bytes...")
# client.send(message, mode="go_back_n")

# # Cierre de conexión
# print("\n[CLIENTE] Cerrando conexión...")
# client.close()
# print("[CLIENTE] Finalizado.")

##############################

# Test final parte 3.6

# import socketTCP_CONGESTION

# def run_client():
#     server_address = ("localhost", 8000)
#     client = socketTCP_CONGESTION.SocketTCP()

#     # Habilitar Control de Congestión y Modo Debug
#     client.set_congestion_control_on(True)
#     client.set_debug(True)

#     print("[CLIENTE] Conectando al servidor...")
#     client.connect(server_address)

#     # Mensaje largo: 160 bytes = 20 fragmentos de 8 bytes
#     message = ("Este es un mensaje largo de prueba diseñado para observar la evolucion "
#                "completa de la ventana de congestion de Slow Start a Congestion Avoidance.").encode()

#     print(f"\n[CLIENTE] Enviando mensaje de {len(message)} bytes...")
#     client.send(message, mode="go_back_n")

#     print("\n[CLIENTE] Cerrando conexión...")
#     client.close()
#     print("[CLIENTE] Finalizado.")

# if __name__ == "__main__":
#     run_client()






##############################


if __name__ == "__main__":

    # Obtener argumentos:
    # python3 cliente.py localhost 8000 < archivo.txt
    # En caso de no seguir estos pasos, el programa fallara por fallo en los argumentos...
    # Mi forma de usarlo fue el abrir un terminal de Command Prompt donde usaba <---- python cliente.py localhost 8000 < archivo.txt ---->

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