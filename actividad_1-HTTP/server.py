import socket
import json
import sys

#parte 2

def create_image_response(filename):
    with open(filename, "rb") as file:
        image = file.read()

    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: image/jpeg\r\n"
        f"Content-Length: {len(image)}\r\n"
        "\r\n"
    ).encode() + image

    return response

###############################################

body_403 = """<html>
<body>
<h1>403 Forbidden</h1>
<p>You don't have permission to access this resource.</p>
<img src="/images.jpeg">
</body>
</html>"""

respuesta_403 = (
    "HTTP/1.1 403 Forbidden\r\n"
    "Content-Type: text/html\r\n"
    f"Content-Length: {len(body_403.encode())}\r\n"
    "\r\n"
    + body_403
)


#parte 1
#crear servidor http que pueda entender head y body de un mensaje:

# Debido a que trabajamos ahora con http, esta funcion debera de cambiar...
# La funcion debera de entonces:  
# Crear un buffer, y empezar a guardar cada rcv ahi. 
# Cuando añadimos el mensaje, mirar si es que en el existe un (\r\n\r\n) pues tendremos q mirar cuando salir debido al content length

def read_config(filename):
    with open(filename,"r") as file:
        config = json.load(file)    
    return config

# FUncion cambiada debido a tipo de encoding como chunked (Daba problemas a la hora de recibir la peticion por completo.)
# ESto porque al no encontrar un content-lenght el algoritmo pensaba que el cuerpo estaba vacio.
# Sin embargo, al tener un type-encoding : chunked solo se reciben paquetes y cada uno tiene su propio content-lenght

def receive_full_message(connection_socket, buff_size):
    buffer = b""

    # Primero necesitamos recibir todos los headers.
    while b"\r\n\r\n" not in buffer:
        datos = connection_socket.recv(buff_size)

        if not datos:
            return buffer

        buffer += datos

    end_header = buffer.find(b"\r\n\r\n")
    headers = buffer[:end_header]
    body_start = end_header + 4
    
    # Caso 1: el servidor indica exactamente cuánto mide el body.
    content_length = get_content_length(headers)

    if content_length > 0:
        while len(buffer) - body_start < content_length:
            datos = connection_socket.recv(buff_size)

            if not datos:
                break

            buffer += datos

        return buffer[:body_start + content_length]

    # Caso 2: el servidor utiliza Transfer-Encoding: chunked.
    if has_chunked_encoding(headers):
        print("recibi chunk")
        while not chunked_message_complete(buffer, body_start):
            datos = connection_socket.recv(buff_size)

            if not datos:
                print("server cerro conexion")
                break

            buffer += datos
            print("recibi:", repr(datos))

        print("termino as intended")
        return buffer

    # Caso 3: no hay body indicado.
    return buffer
 

# ============================================================

def get_content_length(headers):
    for line in headers.split(b"\r\n")[1:]:
        key, value = line.split(b":", 1)

        if key.lower() == b"content-length":
            return int(value.strip())

    return 0


# ============================================================

def has_chunked_encoding(headers):
    for line in headers.split(b"\r\n")[1:]:
        key, value = line.split(b":", 1)

        if key.lower() == b"transfer-encoding":
            if b"chunked" in value.lower():
                return True

    return False


# ============================================================

def chunked_message_complete(buffer, body_start):
    position = body_start

    while True:

        # Buscamos el \r\n que termina la línea con el tamaño.
        end_line = buffer.find(b"\r\n", position)

        if end_line == -1:
            return False

        chunk_size_line = buffer[position:end_line]

        # El tamaño puede venir acompañado de extensiones.
        chunk_size_line = chunk_size_line.split(b";", 1)[0]

        try:
            chunk_size = int(chunk_size_line, 16)
        except ValueError:
            return False

        chunk_data_start = end_line + 2
        chunk_data_end = chunk_data_start + chunk_size

        # Todavía no hemos recibido todo el chunk.
        if len(buffer) < chunk_data_end + 2:
            return False

        # Cada chunk debe terminar en \r\n.
        if buffer[chunk_data_end:chunk_data_end + 2] != b"\r\n":
            return False

        # Un chunk de tamaño 0 indica el final del body.
        if chunk_size == 0:
            return True

        # Pasamos al siguiente chunk.
        position = chunk_data_end + 2


# Trabajare aca con la nueva funcion por crear parse_HTTP_message(http_message: bytes):
#debe encargarse de simplemente desencodear y parsear el mensaje... nada mas.

###################################################################

# ============================================================

def parse_HTTP_message(http_message):
    
    # Los headers HTTP son texto, pero el body puede ser binario.
    end_header = http_message.find(b"\r\n\r\n")

    if end_header == -1:
        return None

    head = http_message[:end_header]
    body = http_message[end_header + 4:]

    # Los headers se pueden decodificar como texto.
    head_decoded = head.decode()
    body_decoded = body.decode()

    head_lines = head_decoded.split("\r\n")

    start_line = head_lines[0]

    headers = {}

    for line in head_lines[1:]:
        key, value = line.split(":", 1)
        headers[key] = value.strip()

    datos = {
        "start line": start_line,
        "headers": headers,
        "body": body_decoded
    }
    return datos


###################################################################

def create_HTTP_message(datos):
    message = datos["start line"] + "\r\n"

    for key, value in datos["headers"].items():
        message += key + ": " + value + "\r\n"

    message += "\r\n"
    message += datos["body"]

    return message.encode()

# Funcion para devolver respuesta a clientes.

def create_HTTP_response(preguntador):
    html = (
        "<!DOCTYPE html>\r\n"
        "<html>\r\n"
        "<head>\r\n"
        "<title>Mi servidor</title>\r\n"
        "</head>\r\n"
        "<body>\r\n"
        "<h1>Hola desde mi servidor HTTP</h1>\r\n"
        "<p>Esta respuesta fue creada por mi servidor.</p>\r\n"
        "</body>\r\n"
        "</html>\r\n"
    )

    body = html.encode()

    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html\r\n"
        f"X-ElQuePregunta: {preguntador}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "\r\n"
    ).encode() + body

    return response


########################################


if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        sys.exit(1)
    
    filename = sys.argv[1]
    config = read_config(filename)
    blocked_sites = config["blocked"]
    forbidden_words = config["forbidden_words"]
    


    buff_size = 50
    end_of_message = "\n"
    server_socket_address = ('10.0.2.15', 8000)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(server_socket_address)
    server_socket.listen(3)

    # nos quedamos esperando a que llegue una petición de conexión
    print('... Esperando clientes')
    while True:
        new_socket, new_socket_address = server_socket.accept()
        recv_message = receive_full_message(new_socket, buff_size)
        http_parseado = parse_HTTP_message(recv_message)

        print("request recibida de cliente")

        print("enviando el mismo mensaje a servidor destino.")

        addr_destino = http_parseado["headers"]["Host"]



        # Permite remover prefijo para casos donde el host no contiene la direccion exacta y necesitamos de la start line.
        start_line_addr = http_parseado["start line"].split()[1].removeprefix("http://")

        if start_line_addr.endswith("/images.jpeg"):
            respuesta_imagen = create_image_response("images.jpeg")
            new_socket.sendall(respuesta_imagen)
            new_socket.close()
            continue

        #CASO ESPECIAL: SE INTENTA CONECTAR A SITIO PROHIBIDO:
        
        bloqueado = False

        print (blocked_sites)
        print(addr_destino)
        print(start_line_addr)
        for blocked_site in blocked_sites:
            if addr_destino == blocked_site or start_line_addr == blocked_site:
                new_socket.send(respuesta_403.encode())
                new_socket.close()
                bloqueado = True
                break

        if bloqueado:
            continue

        # Crear nuevo socket que se conecte al destino.
        destino_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        destino_socket.connect((addr_destino, 80))
        
        #######################
        #añadir header X-ElQuePregunta

        posicion = recv_message.find(b"\r\n")

        recv_message = (
            recv_message[:posicion + 2]
            + "X-ElQuePregunta: seba\r\n".encode()
            + recv_message[posicion + 2:]
        )

        #######################

        #mandando mensaje a destino (se envia recv_message aprovechando que esta encodeado)
        destino_socket.send(recv_message)
        print("envio de mensaje a server destino")

        #Esperamos mensaje de vuelta por parte del servidor
        mensaje_servidor_destino = receive_full_message(destino_socket, buff_size)
        mensaje_servidor_destino_parseado = parse_HTTP_message(mensaje_servidor_destino)
        
        # BLOCKEAR PALABRAS.

        for forbidden_key_value in forbidden_words:
            for key, value in forbidden_key_value.items():
                mensaje_servidor_destino_parseado["body"] = (
                mensaje_servidor_destino_parseado["body"]
                .replace(key, value)
                )

        mensaje_servidor_destino_parseado["headers"]["Content-Length"] = str(
        len(mensaje_servidor_destino_parseado["body"])
        )

        print("Servidor contesto, ahora enviar de vuelta a cliente")


        # creamos el mensaje HTTP correspondiente a los datos del parseo que hicimos
        new_socket.send(create_HTTP_message(mensaje_servidor_destino_parseado))
        
        destino_socket.close()
        new_socket.close()
        
        print(f"conexión con {destino_socket} ha sido cerrada")
        print(f"conexión con {new_socket_address} ha sido cerrada")
        
         