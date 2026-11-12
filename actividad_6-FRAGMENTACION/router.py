import sys
import socket
import ipaddress




# #Modifique su funciones parse_packet y create_packet para que ahora pueda manejar un header IP que contenga la siguiente información:


#  Dirección IP, Puerto, TTL, ID, Offset, Tamaño y FLAG.




#  - Tamaño: Se refiere al tamaño de [mensaje] en bytes sin considerar el tamaño del header. Almacene este dato en 4 bytes.

#  - FLAG: La etiqueta FLAG, tal como se vio en la clase de fragmentación, toma el valor 1 si quedan fragmentos después del fragmento actual,
#  y toma el valor 0 si este es el último fragmento del datagrama original. Este header siempre contiene 1 dígito. Usted puede decidir cómo 
# almacenar este campo en bytes (puede ser un caracter, un int, o un bit único).

#  - ID: El ID es un campo númerico que nos permite identificar todos los fragmentos que forman parte de un mismo paquete IP. Usted 
# deberá decidir cuántos bytes dedicarle a este campo.


#  - Offset: El offset indica el lugar de inicio de la secuencia de bytes contenido en mensaje relativo al datagrama IP original. 
# Usted deberá decidir cuántos bytes dedicarle a este campo. Importante: por simplicidad en esta actividad consideraremos que el offset se calcula en bytes y no en octetos.

# AHORA SON 7 CAMPOS. ENTONCES HACEMOS UN SPLIT POR ";", 6    yyy de ahi obtenemos cada cosa...

def parse_packet(IP_packet: bytes):

    IP_address, IP_port, IP_TTL,   IP_ID ,    IP_OFFSET,      IP_SIZE,     IP_FLAG,   IP_message = IP_packet.split(b";",8)

    return {
        "address": IP_address.decode(),
        "IP_port": int(IP_port.decode()),
        "TTL": int(IP_TTL.decode()),
        "ID": int(IP_ID.decode()),
        "OFFSET": int(IP_OFFSET.decode()),
        "SIZE": int(IP_SIZE.decode()),
        "FLAG": int(IP_FLAG.decode()),
        "IP_message": IP_message,
    }

#Además cree la función create_packet(parsed_IP_packet) que recibe como entrada la estructura de datos conveniente (parsed_IP_packet) 
# y, a partir de ella, crea un paquete IP de acuerdo a la estructura que usted definió.

# Recibe un diccionario con address, IP_port y IP-message
def create_packet(parsed_IP_packet):

    address_bytes = parsed_IP_packet["address"].encode()
    port_bytes = str(parsed_IP_packet["IP_port"]).encode()
    TTL_bytes = str(parsed_IP_packet["TTL"]).encode()
    ID_bytes = str(parsed_IP_packet["ID"]).encode()
    OFFSET_bytes = str(parsed_IP_packet["OFFSET"]).encode()
    SIZE_bytes = str(parsed_IP_packet["SIZE"]).encode()
    FLAG_bytes = str(parsed_IP_packet["FLAG"]).encode()
    message_bytes = parsed_IP_packet["IP_message"]

    return address_bytes + b";" + port_bytes + b";" + TTL_bytes + b";" + ID_bytes + b";" + OFFSET_bytes + b";" + SIZE_bytes + b";" + FLAG_bytes + b";" + message_bytes



# # Test de parse_packet y create_packet

# # Creamos manualmente un paquete IP siguiendo nuestra estructura
# IP_packet_v1 = b"192.168.1.10;8080;64;12345;0;1024;0"

# # Convertimos el paquete de bytes a un diccionario
# parsed_IP_packet = parse_packet(IP_packet_v1)

# # Volvemos a convertir el diccionario a bytes
# IP_packet_v2 = create_packet(parsed_IP_packet)

# # Mostramos los resultados
# print("Paquete original:", IP_packet_v1)
# print("Paquete parseado:", parsed_IP_packet)
# print("Paquete reconstruido:", IP_packet_v2)

# # Comprobamos que ambos paquetes sean iguales
# print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))








# PARTE 6: Crear funcion check_routes(routes_file_name: str, destination_address: tuple[str, int])-> tuple[str, int]

#se deberá encargar de revisar en orden la tabla de rutas para indicar la dirección del siguiente salto. Para el formato de la tabla de 
# rutas puede utilizar directamente la estructura que se muestra en la sección Simulando un mini-Internet. 

# La función check_routes recibe 
# como parámetros el nombre del archivo que contiene las rutas routes_file_name y la dirección de destino destination_address. Esta función debe 
# retornar el par (next_hop_IP, next_hop_puerto) que indica por dónde se debe enviar un paquete que se dirige a la dirección de destino destination_address. 
# Si al recorrer la tabla de rutas no encuentra una ruta apropiada, la función deberá retornar None. 


#Como recibe solamente el nombre de la ruta hacia la tabla de rutas, cambie eso en el main.




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


# Esta línea se traduce como: "Todo lo que reciba en el rango de direcciones IP =[Red (CIDR)] y el rango de puertos =([Puerto_Inicial],[Puerto_final]) 
# debo enviarlo al par ([IP_siguiente_salto],[Puerto_siguiente_salto])para que continúe su camino". El área de Destination Network es la red de destino
#  y el área de Gateway corresponde al siguiente salto para llegar a la red de destino. En nuestro mini-Internet el rango de direcciones IP [Red (CIDR)] 
# corresponde a dirección: 127.0.0.1/24 o direcciones asociadas a localhost# .

# Notemos que el [Puerto_Inicial] y el [Puerto_final] no son el origen y destino, sino la forma que tenemos de agrupar los hosts de la red que pertenecen
#  a la misma IP pero que están escuchando en distintos puertos. Luego si tenemos  [Puerto_Inicial]=8881 y  [Puerto_final]=8883, tenemos que la ruta considera
#  el rango de puertos de destino  {8881,8882,# 8883



#Parte 8: Cambio de funcion check_route para manejar caso donde hay mas de una ruta posible.

# Notemos primero que 
# La idea es tener una variable global que 


# Guarda el índice de la última ruta utilizada para cada destino.
# Ejemplo: 127.0.0.2/24: 3 --> La ultima ruta usada fue la tercera 
# leida de la tabla de rutas dada al router.
rutas_utilizadas = {}


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
                MTU = int(line[5])

                # Guardamos el prefijo y el siguiente salto.
                rutas_posibles.append((network.prefixlen, siguiente_salto, MTU))

    if not rutas_posibles:
        return None

    # Buscamos el prefijo más específico.
    prefijo_maximo = max(ruta[0] for ruta in rutas_posibles)

    # Nos quedamos solamente con las rutas de ese prefijo.
    rutas_especificas = [
        (ruta[1], ruta[2]) for ruta in rutas_posibles
        if ruta[0] == prefijo_maximo
    ]

    # Round Robin entre las rutas más específicas.
    indice = rutas_utilizadas.get(destination_address, 0)

    siguiente_salto = rutas_especificas[indice]

    rutas_utilizadas[destination_address] = (
        indice + 1
    ) % len(rutas_especificas)


    # Retornamos el siguiente salto y el MTU como una tupla para evitar cambiar tanto el codigo siguiente.
    return siguiente_salto[0], siguiente_salto[1]


















def fragment_IP_packet(IP_packet: bytes, MTU: int):

    # Caso 1: El paquete cabe por el enlace.
    if len(IP_packet) <= MTU:
        return [IP_packet]

    # Convertimos el paquete a diccionario.
    parsed_packet = parse_packet(IP_packet)

    mensaje = parsed_packet["IP_message"]

    fragmentos = []
    offset_actual = 0

    # Fragmentamos mientras queden bytes del mensaje.
    while offset_actual < len(mensaje):

        bytes_restantes = len(mensaje) - offset_actual

        # Buscamos el trozo más grande que quepa en el MTU.
        for cantidad in range(bytes_restantes, 0, -1):

            quedan_fragmentos = cantidad < bytes_restantes

            nuevo_fragmento = parsed_packet.copy()

            nuevo_fragmento["OFFSET"] = (
                parsed_packet["OFFSET"] + offset_actual
            )

            nuevo_fragmento["SIZE"] = cantidad

            nuevo_fragmento["FLAG"] = (
                1 if quedan_fragmentos else 0
            )

            nuevo_fragmento["IP_message"] = (
                mensaje[offset_actual:offset_actual + cantidad]
            )

            paquete_bytes = create_packet(nuevo_fragmento)

            # Comprobamos el tamaño COMPLETO, incluyendo header.
            if len(paquete_bytes) <= MTU:
                fragmentos.append(paquete_bytes)
                offset_actual += cantidad
                break

        else:
            raise ValueError("El MTU es demasiado pequeño para el header IP")

    return fragmentos
















def reassemble_IP_packet(fragment_list):

    # Caso 1: Lista vacía.
    if len(fragment_list) == 0:
        return None

    # Convertimos todos los fragmentos a diccionarios.
    fragmentos_parseados = [
        parse_packet(fragmento) for fragmento in fragment_list
    ]

    # Caso 2: Solo hay un paquete.
    if len(fragmentos_parseados) == 1:

        fragmento = fragmentos_parseados[0]

        # Si comienza en offset 0 y no quedan más fragmentos,
        # estamos frente a un paquete completo.
        if (fragmento["OFFSET"] == 0
                and fragmento["FLAG"] == 0
                and fragmento["SIZE"] == len(fragmento["IP_message"])):

            return fragment_list[0]

        # En caso contrario, la lista está incompleta.
        return None

    # Caso 3: Hay varios fragmentos.
    
    # Comprobamos que todos pertenezcan al mismo paquete.
    primer_fragmento = fragmentos_parseados[0]

    for fragmento in fragmentos_parseados:

        if (fragmento["ID"] != primer_fragmento["ID"]
                or fragmento["address"] != primer_fragmento["address"]
                or fragmento["IP_port"] != primer_fragmento["IP_port"]):

            return None

    # Ordenamos los fragmentos según su OFFSET.
    fragmentos_parseados.sort(key=lambda x: x["OFFSET"])

    # El primer fragmento debe comenzar en offset 0.
    if fragmentos_parseados[0]["OFFSET"] != 0:
        return None

    mensaje_reconstruido = b""
    offset_esperado = 0

    for i, fragmento in enumerate(fragmentos_parseados):

        mensaje = fragmento["IP_message"]

        # Comprobamos que el tamaño declarado sea correcto.
        if fragmento["SIZE"] != len(mensaje):
            return None

        # Comprobamos que no existan espacios ni superposiciones.
        if fragmento["OFFSET"] != offset_esperado:
            return None

        mensaje_reconstruido += mensaje
        offset_esperado += len(mensaje)

        # Todos los fragmentos anteriores al último
        # deben indicar que quedan más fragmentos.
        if i < len(fragmentos_parseados) - 1:

            if fragmento["FLAG"] != 1:
                return None

        # El último fragmento debe indicar que no quedan más.
        else:

            if fragmento["FLAG"] != 0:
                return None

    # Reconstruimos el paquete original.
    paquete_reconstruido = primer_fragmento.copy()

    paquete_reconstruido["OFFSET"] = 0
    paquete_reconstruido["SIZE"] = len(mensaje_reconstruido)
    paquete_reconstruido["FLAG"] = 0
    paquete_reconstruido["IP_message"] = mensaje_reconstruido

    return create_packet(paquete_reconstruido)







# Creamos un paquete original.
mensaje = b"Este es un mensaje para probar el reensamblado IP."

parsed_packet = {
    "address": "192.168.1.10",
    "IP_port": 8080,
    "TTL": 64,
    "ID": 12345,
    "OFFSET": 0,
    "SIZE": len(mensaje),
    "FLAG": 0,
    "IP_message": mensaje
}

IP_packet = create_packet(parsed_packet)

# Fragmentamos el paquete.
fragmentos = fragment_IP_packet(IP_packet, 45)

print("Cantidad de fragmentos:", len(fragmentos))

# Caso 1: Reensamblar fragmentos ordenados.
resultado = reassemble_IP_packet(fragmentos)

print("\nCaso 1: Fragmentos ordenados")
print("¿Son iguales?", resultado == IP_packet)

# Caso 2: Reensamblar fragmentos desordenados.
fragmentos.reverse()

resultado = reassemble_IP_packet(fragmentos)

print("\nCaso 2: Fragmentos desordenados")
print("¿Son iguales?", resultado == IP_packet)

# Caso 3: Lista incompleta.
fragmentos_incompletos = fragmentos[:-1]

resultado = reassemble_IP_packet(fragmentos_incompletos)

print("\nCaso 3: Lista incompleta")
print("Resultado:", resultado)









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



fragmentos_recibidos = {}

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

        #caso fragmentos:
         # Almacenar paquete o fragmento recibido
        id_paquete = mensaje_parseado["ID"]

        if id_paquete not in fragmentos_recibidos:
            fragmentos_recibidos[id_paquete] = []

        fragmentos_recibidos[id_paquete].append(mensaje_recuperado)

        # Intentar reensamblar los fragmentos asociados al ID
        paquete_reensamblado = reassemble_IP_packet(
            fragmentos_recibidos[id_paquete]
        )

        if paquete_reensamblado is not None:
            # El datagrama se pudo reconstruir
            mensaje_final = parse_packet(paquete_reensamblado)

            print(f"mensaje recibido: {mensaje_final['IP_message'].decode()}")

            # Eliminar los fragmentos ya ensamblados
            del fragmentos_recibidos[id_paquete]


    elif mensaje_parseado['TTL'] == 0:
        print(f"Se recibió paquete {mensaje_parseado['IP_message']} con TTL 0")
     
    else:
        resultado_addr, MTU = check_routes(archivo_rutas, direccion_a_enviar)

        if resultado_addr is not None:

            siguiente_salto = resultado_addr
            MTU = MTU

            print(
                f"redirigiendo paquete {mensaje_parseado['IP_message']} "
                f"con destino final {mensaje_parseado['address']} "
                f"desde {router_ip} hacia {siguiente_salto}"
            )

            # Disminuimos el TTL antes de fragmentar.
            mensaje_parseado["TTL"] -= 1

            # Reconstruimos el paquete con el TTL actualizado.
            nuevo_paquete = create_packet(mensaje_parseado)

            # Fragmentamos el paquete utilizando el MTU de la ruta.
            fragmentos = fragment_IP_packet(nuevo_paquete, MTU)

            print(f"Cantidad de fragmentos: {len(fragmentos)}")

            # Enviamos cada fragmento al siguiente salto.
            for fragmento in fragmentos:
                router_socket.sendto(fragmento, siguiente_salto)

        else:
            print(
                f"No hay rutas hacia {mensaje_parseado['address']} "
                f"para paquete {mensaje_parseado['IP_message']}"
            )








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