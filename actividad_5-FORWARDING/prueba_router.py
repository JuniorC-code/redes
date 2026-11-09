
import sys
import socket


# Archivo que contiene los mensajes que queremos enviar
ARCHIVO = "mensajes.txt"


def create_packet(parsed_IP_packet):

    address_bytes = parsed_IP_packet["address"].encode()
    port_bytes = str(parsed_IP_packet["IP_port"]).encode()
    TTL_bytes = str(parsed_IP_packet["TTL"]).encode()
    message_bytes = parsed_IP_packet["IP_message"]

    return (
        address_bytes + b";" +
        port_bytes + b";" +
        TTL_bytes + b";" +
        message_bytes
    )


# Obtener argumentos
if len(sys.argv) != 4:
    print("Uso: python3 prueba_router.py headers IP_router_inicial puerto_router_inicial")
    sys.exit(1)


# Obtener headers
headers = sys.argv[1].split(";")

if len(headers) != 3:
    print("Error: los headers deben tener el formato IP;puerto;TTL")
    sys.exit(1)

IP_destino = headers[0]
puerto_destino = int(headers[1])
TTL = int(headers[2])

# Obtener dirección del router inicial
IP_router_inicial = sys.argv[2]
puerto_router_inicial = int(sys.argv[3])

direccion_router = (IP_router_inicial, puerto_router_inicial)


# Crear socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


try:
    # Abrir archivo y leerlo línea por línea
    with open(ARCHIVO, "rb") as archivo:

        for linea in archivo:

            # Crear estructura del paquete
            paquete = {
                "address": IP_destino,
                "IP_port": puerto_destino,
                "TTL": TTL,
                "IP_message": linea.rstrip(b"\r\n")
            }

            # Crear paquete en bytes
            paquete_bytes = create_packet(paquete)

            # Enviar al router inicial
            sock.sendto(paquete_bytes, direccion_router)

            print(
                f"Paquete enviado hacia {direccion_router}: "
                f"destino final {IP_destino}:{puerto_destino}, "
                f"TTL {TTL}"
            )

finally:
    sock.close()
