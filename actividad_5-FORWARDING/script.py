
import socket
import sys


def create_packet(parsed_IP_packet):
    address_bytes = parsed_IP_packet["address"].encode()
    port_bytes = str(parsed_IP_packet["IP_port"]).encode()
    message_bytes = parsed_IP_packet["IP_message"]

    return address_bytes + b";" + port_bytes + b";" + message_bytes


def main():
    if len(sys.argv) != 6:
        print("Uso: python sender.py IP_final puerto_final mensaje IP_envio puerto_envio")
        sys.exit(1)

    # Obtener información desde los argumentos
    IP_final = sys.argv[1]
    puerto_final = int(sys.argv[2])
    mensaje = sys.argv[3]

    IP_envio = sys.argv[4]
    puerto_envio = int(sys.argv[5])

    # Construir estructura del paquete
    parsed_packet = {
        "address": IP_final,
        "IP_port": puerto_final,
        "IP_message": mensaje.encode()
    }

    # Crear paquete en bytes
    packet = create_packet(parsed_packet)

    # Crear socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Enviar paquete hacia la dirección indicada
        sock.sendto(packet, (IP_envio, puerto_envio))

        print(f"Paquete enviado hacia {IP_envio}:{puerto_envio}")
        print(f"Destino final: {IP_final}:{puerto_final}")

    finally:
        sock.close()


if __name__ == "__main__":
    main()
