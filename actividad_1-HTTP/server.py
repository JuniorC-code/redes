import socket
import json
import sys


def parse_HTTP_message(http_message: bytes):
    message = http_message.decode()

    head, body = message.split("\r\n\r\n", 1)

    lines = head.split("\r\n")

    request_line = lines[0]

    method, path, version = request_line.split(" ", 2)

    headers = {}

    for line in lines[1:]:
        name, value = line.split(":", 1)
        headers[name] = value.strip()

    return {
        "method": method,
        "path": path,
        "version": version,
        "headers": headers,
        "body": body
    }


def create_HTTP_message(http):
    request_line = (
        http["method"] + " " +
        http["path"] + " " +
        http["version"]
    )

    headers = ""

    for name, value in http["headers"].items():
        headers += name + ": " + value + "\r\n"

    message = (
        request_line + "\r\n" +
        headers + "\r\n" +
        http["body"]
    )

    return message.encode()


def is_blocked(host, path, blocked):

    if ":" in host:
        host = host.split(":", 1)[0]

    if host in blocked:
        return True

    if host + path in blocked:
        return True

    return False


def create_403_response():

    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Acceso bloqueado</title>
</head>
<body>
    <h1>403 Forbidden</h1>
    <p>Esta página está bloqueada.</p>
    <img src="gato.jpg">
</body>
</html>
"""

    content_length = len(html.encode())

    response = (
        "HTTP/1.1 403 Forbidden\r\n"
        "Content-Type: text/html\r\n"
        f"Content-Length: {content_length}\r\n"
        "Connection: close\r\n"
        "\r\n"
        + html
    )

    return response.encode()


def replace_forbidden_words(response, forbidden_words):

    response_text = response.decode(errors="replace")

    for word in forbidden_words:

        for string_a, string_b in word.items():

            response_text = response_text.replace(
                string_a,
                string_b
            )

    return response_text.encode()


filename = sys.argv[1]

with open(filename, "r") as file:
    config = json.load(file)

blocked = config["blocked"]

forbidden_words = config["forbidden_words"]


server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server_socket.bind(("0.0.0.0", 8000))

server_socket.listen(5)

print("Proxy esperando conexiones en el puerto 8000...")


while True:

    client_socket, client_address = server_socket.accept()

    print("Cliente conectado:", client_address)

    request = client_socket.recv(4096)

    if not request:
        client_socket.close()
        continue

    print(request.decode(errors="replace"))

    http = parse_HTTP_message(request)

    host = http["headers"].get("Host")

    if host is None:
        client_socket.close()
        continue

    if ":" in host:

        host_without_port, port = host.rsplit(":", 1)

        try:
            port = int(port)
            host = host_without_port
        except ValueError:
            port = 80

    else:
        port = 80

    print("Servidor:", host)
    print("Puerto:", port)
    print("Path:", http["path"])


    if is_blocked(host, http["path"], blocked):

        print("Página bloqueada.")

        response = create_403_response()

        client_socket.sendall(response)

        client_socket.close()

        continue


    http["headers"]["X-ElQuePregunta"] = "Seba"

    request = create_HTTP_message(http)


    destination_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    destination_socket.connect((host, port))

    destination_socket.sendall(request)

    response = destination_socket.recv(4096)

    print("Response recibida:")
    print(response[:500])


    response = replace_forbidden_words(
        response,
        forbidden_words
    )


    client_socket.sendall(response)


    destination_socket.close()

    client_socket.close()

    print("Conexión terminada.")