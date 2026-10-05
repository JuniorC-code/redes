import socket


# Ahora vamos a crear la clase  SocketTCP (guarde la clase en un tercer archivo distinto al cliente y el servidor). El constructor de esta clase deberá ser capaz 
#de almacenar todos los recursos que va a necesitar para la comunicación (socket UDP, dirección de destino, número de secuencia, todo lo que usted considere necesario).
#Su constructor no debe recibir parámetros, es decir, se invoca como:


class SocketTCP():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dest_adr = None
        self.seq_num = 0
        self.timeout = 1.0  # Timeout para retransmisión

    # Inicialmente queria que SocketTCP tuviera en sus atributos ACK SYN FIN y n°secuencia, pero socketTCP representa un socket,
    # osea la via de comunicacion, mientras que el segmento TCP es el paquete q se envia, por ello es mejor que sean los propios segmentos los que tengan dichos atributos.
    # y ademas, como se trata de simplemente un indicador de flag, basta con representarlos como bytes, donde podemos usar el primer byte y sus bits para los flags.
    # Luego podemos usar el resto de bytes para el numero de secuencia, que por temas de largo basta con que sea de largo 4 bytes
    # esto implica que finalmente para los headers usaremos 5 bytes. 

    # ya con todo eso, partamos, recibamos en create segment bools para ACK, SYN, FIN y un int para n° secuencia, y creemos un segmento TCP con ello.
    # digamos que el primer bit del primer byte es ACK, el segundo bit es SYN y el tercer bit es FIN, y los 4 bytes restantes son para el n° de secuencia.
    # bit prendido -> flag activada
    def create_segment(self, ack: bool, syn: bool, fin: bool, seq: int, payload: bytes):

        # Enseguida crearemos los bits segun flags y lo añadiremos a el byte que representa a estos.

        flags = 0b00000000

        if ack:
            flags |= 0b00000001

        if syn:
            flags |= 0b00000010

        if fin:
            flags |= 0b00000100

        header = flags.to_bytes(1, byteorder="big") + seq.to_bytes(4, byteorder="big")

        # Devolvemos el segmento TCP como la concatenación del header y el payload

        return header + payload

    def parse_segment(self, segment: bytes):
        # Extraemos el header y el payload del segmento
        header = segment[:5]
        payload = segment[5:]

        # Obtenemos los flags y el número de secuencia del header
        flags = header[0]
        seq = int.from_bytes(header[1:5], byteorder="big")

        # Determinamos el estado de cada flag
        ack = bool(flags & 0b00000001)
        syn = bool(flags & 0b00000010)
        fin = bool(flags & 0b00000100)

        # Devolvemos un diccionario con la información del segmento
        return {
            "ACK": ack,
            "SYN": syn,
            "FIN": fin,
            "seq": seq,
            "payload": payload
        }