import socket
import random


# Ahora vamos a crear la clase  SocketTCP (guarde la clase en un tercer archivo distinto al cliente y el servidor). El constructor de esta clase deberá ser capaz 
#de almacenar todos los recursos que va a necesitar para la comunicación (socket UDP, dirección de destino, número de secuencia, todo lo que usted considere necesario).
#Su constructor no debe recibir parámetros, es decir, se invoca como:


class SocketTCP():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dest_adr = None
        self.seq_num = 0
        self.timeout = 1.0  # Timeout para retransmisión
        self.buffer_size_UDP = 21  # Tamaño del buffer para recibir mensajes

        # parte 5 
        self.remaining_bytes = 0
        self.pending_data = b""

        # parte 7 --> Añadir memoria de la direccion donde llegaban los handshake, cosa de poder 
        # mirar cuando falle el caso borde ultimo seg ACK no llega.

        self.handshake_addr = None
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
            "payload": payload.decode()
        }

# Anotar esto DONDE CORRESPONDE: 
# ---> PAYLOAD SI USA INTS PARA MARCAR ALGUNN LARGO, POR LA NATURALEZA DE LA FUNCION DECODE() -> str debemos de usar int(parsed_message["payload"])



    # Parte 4 Implementar 3-way handshake:

    # - bind(address) : Función que se encarga de que el objeto socketTCP escuche en la dirección address.
    def bind(self, address):
        self.sock.bind(address)

    # - connect(address): Función que inicia la conexión desde un objeto socketTCP con otro que se encuentra escuchando en la dirección address. 
    # Dentro de esta función deberá implementar el lado del cliente del 3-way handshake. Por simplicidad, haga que su número de secuencia inicial
    #  sea elegido aleatoriamente entre 0 y 100.

    # Por comodidad, al hacer la conexion el seq_num simplemente se aumenta en 1 con cada segmento recibido.

    # Cambio en funcion parte 6: Implementar stop & wait...

    def connect(self, address):
        self.dest_adr = address
        self.seq_num = random.randint(0, 100)

        # primero debemos de mandar un segmento SYN al server 
        SYN_segment = self.create_segment(ack=False, syn=True, fin=False, seq=self.seq_num, payload=b"")

        # STOP & WAIT para SYN
        while True:

            self.sock.sendto(SYN_segment, self.dest_adr)
            self.sock.settimeout(5)

            try:

                SYN_ACK_segment, server_address = self.sock.recvfrom(self.buffer_size_UDP)
                SYN_ACK_info = self.parse_segment(SYN_ACK_segment)

                if (SYN_ACK_info["SYN"]and SYN_ACK_info["ACK"]and SYN_ACK_info["seq"] == self.seq_num + 1):
                    break

            except socket.timeout:
                print("No se recibio SYN-ACK, reenviando SYN")
        
        #obtener nuevo puerto que vendra en el payload del SYN-ACK, como decode nos devuelve str, debemos pasarlo a int, al final del codigo, recien cambiamos self.dest_address cosa que mandemos el ultimo ACK a la dir correcta
        new_port = int(SYN_ACK_info["payload"])

        # parte 7: guardar como nuevo atributo la direccion de handshake en caso que no llegue ACK
        self.handshake_addr = self.dest_adr

        # Finalmente mandamos un ACK de vuelta al server 
        ACK_segment = self.create_segment(ack=True, syn=False, fin=False, seq=self.seq_num + 2, payload=b"")
        self.sock.sendto(ACK_segment, self.dest_adr)

        self.seq_num += 2
        self.dest_adr = ("localhost", new_port)

        



############################ ANOTACION
    # Hay algo muy tricky en estas 2 funciones, si cambio la direccion de destino, tan pronto como se haga un send por parte del emisor, si la parte que uso accept no esta preparada con su nuevo socket, no se escuchara nada pues
    # se habra enviado un paquete a un lugar donde no habia nada escuchando.
    # => Antes de enviar el paquete ACK-SYN, ya se debe de crear el nuevo socket bindeado a su respectiva nueva direccion....



    # Cambio en accept() parte 6: Añadir Stop & Wait
    # Funcion de lado server
    def accept(self):
        # esperar para segmento SYN por parte del cliente
        SYN_segment, client_address = self.sock.recvfrom(self.buffer_size_UDP)
        #verificar que el segmento recibido sea un SYN
        SYN_info = self.parse_segment(SYN_segment)
        if not SYN_info["SYN"]:
            raise ValueError("Segmento SYN inválido")

        
        # Crear nuevo socket antes de enviar el segmento SYN-ACK
        new_socket = SocketTCP()
        new_address = ("localhost", 8001)  # Nueva dirección para el nuevo socket
        new_socket.bind(new_address)  # Bindear a una nueva dirección


        ##############################
        # Añadido de la parte 5 (Note que send usa como número de secuencia inicial el último número de secuencia almacenado.)
        new_socket.seq_num = SYN_info["seq"] + 2
        # Añadir dest_adress altiro a nuevo socket
        new_socket.dest_adr = client_address  


        # en caso de ser correcto, enviar un segmento SYN-ACK de vuelta al cliente, con n° secuencia igual al n° de secuencia del SYN recibido + 1 yyyy payload con el nuevo puerto al q se conectara el cliente
        SYN_ACK_segment = self.create_segment(ack=True, syn=True, fin=False, seq=SYN_info["seq"] + 1, payload= b"8001")

        # STOP & WAIT para el ACK final
        while True:

            self.sock.sendto(SYN_ACK_segment, client_address)
            self.sock.settimeout(5)

            try:
                ACK_segment, _ = self.sock.recvfrom(self.buffer_size_UDP)
                ACK_info = self.parse_segment(ACK_segment)

                if (ACK_info["ACK"]and ACK_info["seq"] == SYN_info["seq"] + 2):
                    break

            except socket.timeout:
                print("No se recibio ACK, reenviando SYN-ACK")

        return new_socket, new_address

    # Parte 5 STOP & WAIT

    # Optimizable el codigo, esta bien feito y tiene varios codigos duplicados pero creo que sirve...
    # modo de uso: despues de ser creado un objeto socketTCP por accept(...) este tendra ya bindeada la dest_address y el atributo dest_address como el nuevo
    #  y para enviar mensajes solo usaremos sendto()

    # Para manejo de primer mensaje, por simplicidad de ahora solo hare que el payload diga: "primer mensaje, largo total es x bytes"

    def send(self, message: bytes):

        #Parte 7: Refactor: esperar si llega mensaje SYN-ACK porque se perdio el ultimo paquete ACK de connect  
        self.sock.settimeout(5)
        try:
            
            #caso si llega: verificar que sea SYN_ACK y de ahi enviar ultimo ACK
            mensaje, direccion = self.sock.recvfrom(self.buffer_size_UDP)
            mensaje_parseado = self.parse_segment(mensaje)

            if (mensaje_parseado["SYN"]and mensaje_parseado["ACK"]and direccion == self.handshake_addr):

                ACK_segment = self.create_segment(ack=True,syn=False,fin=False,seq=self.seq_num,payload=b"")
                self.sock.sendto(ACK_segment, self.handshake_addr)

        except socket.timeout:

            # Caso no llega nada --> llego correctamente el ACK final.
            pass

        # Añadir al largo tambien el primer 
        message_lenght = len(message) 

        # Esperar confirmacion por parte de receptor con 5 segundos
        # Ademas, actualizar el numero de secuencia al que el receptor nos devolvio...

            ############################################ CASO ESPECIAL: PRIMER MENSAJE######################################################
        while True:

            # mandar primer mensaje con el largo del mensaje (este queda como caso aparte pues el receptor devolvera el mismo n°secuencia para no enredarnos con el largo del mensaje+largo primer mensaje)
            first_message = self.create_segment(ack=False, syn=False, fin=False, seq=self.seq_num, payload= message_lenght.to_bytes(4, byteorder="big"))
            self.sock.sendto(first_message,self.dest_adr)

            self.sock.settimeout(5)
            try:
                mensaje, direccion = self.sock.recvfrom(21)
                mensaje_parseado = self.parse_segment(mensaje)

                # revisar si mensaje que llego es de tipo ACK  (caso que no, volver a mandar mensaje noma...)
                if mensaje_parseado["ACK"] and mensaje_parseado["seq"] == self.seq_num:
                    self.seq_num = mensaje_parseado["seq"]
                    break

            except socket.timeout:
                print("No se recibio confirmacion, reenviando mensaje")


            ############################################ CASO: RESTO DE MENSAJES ######################################################
        # iteracion con while para enviar resto de mensajes y separarlos segun corresponda. (en conjunto con su respectivo n° secuencia...)
        for i in range(0,len(message), 16):
           packet = message[i:i+16]
           tcp_segment = self.create_segment(ack=False, syn=False, fin=False, seq=self.seq_num , payload=packet)
           # enviar mensajes y ver si son confirmados...
           # usando logica de esperar confirmacion y en caso que si, terminar el ciclo para ese segmento en especifico, actualizando el n° de secuencia al que devolvio el receptor
           while True:
               # enviar mensaje
               self.sock.sendto(tcp_segment, self.dest_adr)
               #timeout para confirmacion
               self.sock.settimeout(5)
               try:
                   mensaje, direccion = self.sock.recvfrom(21)
                   mensaje_parseado = self.parse_segment(mensaje)
                   # revisar si mensaje que llego es de tipo ACK  (caso que no, volver a mandar mensaje noma...)
                   if mensaje_parseado["ACK"] and mensaje_parseado["seq"] == self.seq_num + len(packet):
                       self.seq_num = mensaje_parseado["seq"]
                       break
               except socket.timeout:
                   print("No se recibio confirmacion, reenviando mensaje")
                
            



    # manejo de stop & wait desde receptor.....

    # Primer mensaje que recibe son solamente headers y literal el largo del mensaje que llegara...

    # buff_size solo afecta a SOCKETTCP y no debe ser necesariamente el mismo que el del socket UDP.
    # ----> Eso implica que si ponemos un buff_size mayor a 21 que hacemos? Si buff_size = 50, por ejemplo, no hacer recvfrom(50). Hacer varios recvfrom(buff_size_udp) hasta acumular 50 bytes de datos.
    def recv(self, buff_size):

        # if inicial en caso que ya se haya retornado anteriormente la misma funcion recv, asi podemos seguir trabajando sin perder bytes guardados del ultimo paquete UDP que llego al recv anterior
        if self.remaining_bytes == 0:

            #obtener primer mensaje y mandar confirmacion a quien nos lo mando.
            mensaje, address = self.sock.recvfrom(self.buffer_size_UDP)
            mensaje_parseado = self.parse_segment(mensaje)

            # Obtener message_lenght, guardar los bytes restantes... (queda horrible porque parse_segment lo decodea, quizas cambiar despues cuando tenga mas tiempo....)
            self.remaining_bytes = self.remaining_bytes = int.from_bytes(mensaje_parseado["payload"].encode(),byteorder="big")
            self.seq_num = mensaje_parseado["seq"]

            # Devolver mensaje de confirmacion a emisor
            first_message = self.create_segment(ack=True, syn=False, fin=False, seq=mensaje_parseado["seq"], payload= b"")
            self.sock.sendto(first_message,address)

        #ok, con eso tenemos el primer mensaje listo.

        # variable para el momento donde debemos parar la iteracion:
        target = min(self.remaining_bytes + len(self.pending_data), buff_size)

        # definimos nuestro payload_buffer con la data que quedo de recv's anteriores y la volvemos a dejar vacia
        payload_buffer = self.pending_data
        self.pending_data = b""

        while len(payload_buffer) < target:

            # obtener mensaje del emisor
            mensaje, address =  self.sock.recvfrom(self.buffer_size_UDP)
            mensaje_parseado = self.parse_segment(mensaje)
            
            # revisar n°secuencia (por la implementacion del send de arriba, el 1er y segundo mensaje tendran mismo n°secuencia => como ya obtuvimos 1er n°, podemos comprobar que llego el segundo 
            # verificando que el n° secuencia sea el mismo que el de nuestro objeto c:)
            if mensaje_parseado["seq"] == self.seq_num:

                # recepecion de paquete nuevo, sumar largo a nuestro seq_num, guardar nueva data en payload_buffer y restar de los bytes que nos faltan por leer
                self.seq_num += len(mensaje_parseado["payload"])
                payload_buffer += mensaje_parseado["payload"].encode()
                self.remaining_bytes -= len(mensaje_parseado["payload"])

                #enviar confirmacion a emisor
                ACK_segment = self.create_segment(ack=True, syn=False, fin=False, seq=self.seq_num, payload=b"")
                self.sock.sendto( ACK_segment,address)

            # caso donde llega mensje q no corresponde --> Mandar confirmacion anterior solamente
            else: 
                ACK_segment = self.create_segment(ack=True, syn=False, fin=False, seq=self.seq_num, payload=b"")
                self.sock.sendto(ACK_segment,address)
        
        # Caso donde tenemos el payload completo pero sobraron datos pues 
        # los datos que nos faltaban eran menos a lo que una llamada a recvfrom nos da

        if len(payload_buffer) > target:
            self.pending_data = payload_buffer[target:]
            payload_buffer = payload_buffer[:target]

        return payload_buffer


    # Parte 6: Fin de conexion para liberar recursos...

    # La función close() debe implementar el cierre de conexión desde el lado del "Host A" según lo visto en el video.
    # HOST A --> manda fin seq z, ecibe fin+ack z+1 y devuelve ack z+2
    def close(self):
        # primero creemos el mensaje FIN,  El FIN usa el seq_num actual como z
        FIN_segment = self.create_segment(ack=False, syn=False, fin=True, seq=self.seq_num, payload=b"")
        self.sock.sendto(FIN_segment, self.dest_adr)

        # Recepcionar mensaje FIN+ACK
        mensaje , address = self.sock.recvfrom(self.buffer_size_UDP)
        mensaje_parseado = self.parse_segment(mensaje)

        if mensaje_parseado["FIN"] == True and mensaje_parseado["ACK"] == True and mensaje_parseado["seq"] == self.seq_num + 1:
            # mandar un mensaje de vuelta ACK:
            ACK_segment = self.create_segment(ack=True, syn=False, fin=False, seq=self.seq_num + 2, payload=b"")
            self.sock.sendto(ACK_segment, self.dest_adr)
            self.sock.close()
            print("conexion cerrada")

        else: 
            raise Exception("No llego mensaje FIN+ACK")

    def recv_close(self):

    # Recibir FIN seq=z
        mensaje, address = self.sock.recvfrom(self.buffer_size_UDP)
        mensaje_parseado = self.parse_segment(mensaje)

        if mensaje_parseado["FIN"]:

           # Guardamos el seq del FIN recibido
           seq_fin = mensaje_parseado["seq"]

           # HOST B: responder FIN+ACK seq=z+1
           FIN_ACK_segment = self.create_segment(ack=True,syn=False,fin=True,seq=seq_fin + 1,payload=b"")
           self.sock.sendto(FIN_ACK_segment, self.dest_adr)

           # Recibir ACK seq=z+2
           mensaje, address = self.sock.recvfrom(self.buffer_size_UDP)
           mensaje_parseado = self.parse_segment(mensaje)

           if (mensaje_parseado["ACK"] and mensaje_parseado["seq"] == seq_fin + 2):
               # Cierre completado
               self.sock.close()
               print("conexion cerrada")


# La idea es que aquí **no usas `self.seq_num` para calcular `z+1`**. Usas el `seq` que llegó en el FIN:
# 
# ```python
# seq_fin = mensaje_parseado["seq"]
# ```
# 
# porque ese valor es `z`.
# 
# Entonces:
# 
# ```text
# FIN recibido:       z
# FIN+ACK enviado:    z + 1
# ACK recibido:       z + 2
# ```
# 
# Esto además hace que `recv_close()` funcione independientemente de cuál sea el `self.seq_num` actual del Host B, siguiendo exactamente la convención simplificada del protocolo de tu tarea.
# 
# Una diferencia importante respecto de `close()` es que en `close()` tú **inicias** el cierre, por eso partes desde tu propio `self.seq_num`. En `recv_close()` tú **recibes** el inicio del cierre, por eso partes desde el `seq` recibido.


