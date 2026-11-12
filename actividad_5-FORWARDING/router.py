import sys
import socket
import ipaddress

# Codigo que recibe parametros la IP y el puerto donde escuchara un router... Y nombre de archivo con tablas de ruta.
# Usar sys

#Para esta actividad usaremos la siguiente estructura para nuestros paquetes IP:
#[Dirección IP];[Puerto];[mensaje]

#PARTE 4: crear estructura de datos para paquetes IP:
#notar que los ";" usan un byte tambien, asi que no hay q tomarlos en cuenta....
def parse_packet(IP_packet: bytes):

    IP_address, IP_port, IP_TTL, IP_message = IP_packet.split(b";", 3)

    return {
        "address": IP_address.decode(),
        "IP_port": int(IP_port.decode()),
        "TTL": int(IP_TTL.decode()),
        "IP_message": IP_message
    }


# Recibe un diccionario con address, IP_port, TTL y IP-message
def create_packet(parsed_IP_packet):

    address_bytes = parsed_IP_packet["address"].encode()
    port_bytes = str(parsed_IP_packet["IP_port"]).encode()
    TTL_bytes = str(parsed_IP_packet["TTL"]).encode()
    message_bytes = parsed_IP_packet["IP_message"]

    return address_bytes + b";" + port_bytes + b";" + TTL_bytes + b";" + message_bytes


# PARTE 6: Crear funcion check_routes(routes_file_name: str, destination_address: tuple[str, int])-> tuple[str, int]

#  Indica cuántos bits del principio de la dirección IP corresponden a la parte de red (la porción fija). El resto de los bits se utiliza para
#  identificar a los dispositivos individuales u hosts dentro de esa red.

#• Ejemplo (192.168.1.0/24): El /24 significa que los primeros 24 bits son de red y los últimos 8 bits (32 - 24 = 8) quedan para las direcciones 
# de los equipos, lo que permite hasta 256 direcciones IP posibles en ese bloque

# #+----------------------------------------------+-----------------------------------------------+
# | Destination Network                          | Gateway                                       |
# +----------------------------------------------+-----------------------------------------------+
# | [Red (CIDR)] [Puerto_Inicial] [Puerto_final] | [IP_siguiente_salto] [Puerto_siguiente_salto] |
# +----------------------------------------------+-----------------------------------------------+

#EJEMPLO DE TABLA: 

# 127.0.0.1/24         8882            8882                  127.0.0.1                    8882
 
# Donde la línea "127.0.0.1/24 8882 8882 127.0.0.1 8882" 
#indica que si recibo un mensaje que se dirige al grupo de IPs 127.0.0.1/24 con un puerto en el conjunto {8882} (equivalente al rango (8882,8882)), entonces debe reenviarlo o hacer forward hacia la dirección (127.0.0.1,8882). 

rutas_utilizadas = {}

def check_routes(routes_file_name: str, destination_address: tuple[str, int]) -> tuple[str, int] | None:

    destination_IP = ipaddress.ip_address(destination_address[0])
    rutas_posibles = []

    with open(routes_file_name, "r") as tabla_de_rutas:
        for linea_ruta in tabla_de_rutas:

            line = linea_ruta.split()

            if not line:
                continue

            network = ipaddress.ip_network(line[0], strict=False)

            if (destination_IP in network
                and int(line[1]) <= destination_address[1] <= int(line[2])):

                siguiente_salto = (line[3], int(line[4]))

                # Guardamos el prefijo y el siguiente salto.
                rutas_posibles.append((network.prefixlen, siguiente_salto))

    if not rutas_posibles:
        return None

    # Buscamos el prefijo más específico.
    prefijo_maximo = max(ruta[0] for ruta in rutas_posibles)

    # Nos quedamos solamente con las rutas de ese prefijo.
    rutas_especificas = [
        ruta[1] for ruta in rutas_posibles
        if ruta[0] == prefijo_maximo
    ]

    # Round Robin entre las rutas más específicas.
    indice = rutas_utilizadas.get(destination_address, 0)

    siguiente_salto = rutas_especificas[indice]

    rutas_utilizadas[destination_address] = (
        indice + 1
    ) % len(rutas_especificas)

    return siguiente_salto


# Haga que el código de su router pueda recibir paquetes en un loop. En caso de recibir un mensaje, haga que su router primero 
# chequee si el paquete es para él. 
# 
# Si es para él, haga que este imprima el contenido del paquete (sin headers). 
# 
# Si el paquete no es para él, llame a la función check_routes y use la dirección que esta retorna para hacer forward del paquete. 
# Haga que su router imprima el mensaje "redirigiendo paquete [paquete_ip] con destino final [destination_address] desde [dirección_router_actual] "
# "hacia [dirección_next_hop]" donde [dirección_next_hop] es la dirección que obtuvo de la función check_routes. En caso de que su función 
# retorne None simplemente ignore el paquete e imprima "No hay rutas hacia [destination_address] para paquete [paquete_ip]".

# crear socket del router y asignarle con sys.args la ip y el puerto donde escuchara
router_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

# Obtener ip y puerto
router_ip = sys.argv[1]
router_port = int(sys.argv[2])
router_dir = (router_ip,router_port)

# Obtener tabla de rutas del router

archivo_rutas = sys.argv[3]

#bindear direccion a socket de router

router_socket.bind(router_dir)
while True:

    # Recibimos un paquete en bytes, pasarlo a nuestra estructura de datos y comparar con nuestra direccion.
    mensaje_recuperado, direccion_origen = router_socket.recvfrom(4096)
    mensaje_parseado = parse_packet(mensaje_recuperado)
    direccion_a_enviar = (mensaje_parseado["address"], mensaje_parseado["IP_port"])

    print(router_port)
    print(mensaje_parseado['IP_port'] )

    if mensaje_parseado['address'] == router_ip and mensaje_parseado['IP_port'] == router_port:
        print(f"mensaje recibido: {mensaje_parseado['IP_message']}")

    elif mensaje_parseado['TTL'] == 0:
        print(f"Se recibió paquete {mensaje_parseado['IP_message']} con TTL 0")
     
    else:
        resultado = check_routes(archivo_rutas,direccion_a_enviar)
        if resultado is not None:
            print(f"redirigiendo paquete {mensaje_parseado['IP_message']} con destino final {mensaje_parseado['address']} desde {router_ip} hacia {resultado[0]};puerto {resultado[1]}")
            print(f"TTL actual: {mensaje_parseado['TTL']}")
            
            # Disminuir en 1 TTl para el mensaje que sera reenviado
            
            mensaje_parseado["TTL"] -= 1
            nuevo_paquete = create_packet(mensaje_parseado)
            router_socket.sendto(nuevo_paquete, resultado )

        else: 
            
            print(f"No hay rutas hacia {mensaje_parseado['address']} para paquete {mensaje_parseado['IP_message']}")







# # -------------------------------
# # TEST parte 2.1 (funciona perfect c:)
# # -------------------------------

# # Creamos manualmente un paquete en bytes
# IP_packet_v1 = b"127.0.0.1;8082;10;Hola r2"

# # Convertimos el paquete a un diccionario
# parsed_IP_packet = parse_packet(IP_packet_v1)

# # Reconstruimos el paquete
# IP_packet_v2 = create_packet(parsed_IP_packet)

# # Mostramos resultados
# print("Paquete original:", IP_packet_v1)
# print("Paquete parseado:", parsed_IP_packet)
# print("Paquete reconstruido:", IP_packet_v2)

# print("IP_packet_v1 == IP_packet_v2 ? {}".format(
#     IP_packet_v1 == IP_packet_v2
# ))