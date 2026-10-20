import socket
import random
from socketUDP import SocketUDP
from slidingWindowCC import SlidingWindowCC
import CongestionControl

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

        # Variable para casos borde de transmicion de fin segments
        self.fin_segment_received = None


        # nueva variable segun 3.2:
        self.congestion_control_on = False
        self.debug = False  # Modo debug desactivado por defecto


    # ya con todo eso, partamos, recibamos en create segment bools para ACK, SYN, FIN y un int para n° secuencia, y creemos un segmento TCP con ello.
    # digamos que el primer bit del primer byte es ACK, el segundo bit es SYN y el tercer bit es FIN, y los 4 bytes restantes son para el n° de secuencia.
    # bit prendido -> flag activada

    def create_segment(self, ack: bool, syn: bool, fin: bool, seq: int, payload: bytes):

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

    # Parte 4 Implementar 3-way handshake:

    # - bind(address) : Función que se encarga de que el objeto socketTCP escuche en la dirección address.
    def bind(self, address):
        self.sock.bind(address)

    # Función que inicia la conexión desde un objeto socketTCP con otro que se encuentra escuchando en la dirección address. 
    # Por simplicidad, haga que su número de secuencia inicial sea elegido aleatoriamente entre 0 y 100.
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
        new_port = int(SYN_ACK_info["payload"].decode())

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

    def send(self, message, mode="stop_and_wait"):
        if mode == "stop_and_wait":
            return self.send_using_stop_and_wait(message)

        if mode == "go_back_n":
            self.send_using_go_back_n(message)
    
    def recv(self, buff_size, mode="stop_and_wait"):

        if mode == "stop_and_wait":
            return self.recv_using_stop_and_wait(buff_size)

        if mode == "go_back_n":
            return self.recv_using_go_back_n(buff_size)



    # Parte 6: Fin de conexion para liberar recursos...

    # La función close() debe implementar el cierre de conexión desde el lado del "Host A" según lo visto en el video.
    # HOST A --> manda fin seq z, recibe fin+ack z+1 y devuelve ack z+2
    def close(self):
        # Obtener el socket UDP nativo directamente (evita activar timers de SocketUDP)
        udp_socket = self.sock.socket_udp if hasattr(self.sock, "socket_udp") else self.sock

        # Primero creamos el mensaje FIN
        FIN_segment = self.create_segment(ack=False, syn=False, fin=True, seq=self.seq_num, payload=b"")

        # Esperar 3 veces recepcionar mensaje FIN+ACK
        for intento in range(3):
            udp_socket.sendto(FIN_segment, self.dest_adr)

            # Esperar FIN+ACK en timeout
            udp_socket.settimeout(self.timeout)

            try:
                mensaje, address = udp_socket.recvfrom(self.buffer_size_UDP)
                mensaje_parseado = self.parse_segment(mensaje)

                if (mensaje_parseado["FIN"] and mensaje_parseado["ACK"] and mensaje_parseado["seq"] == self.seq_num + 1):
                    # Recibimos correctamente FIN+ACK
                    ACK_segment = self.create_segment(ack=True, syn=False, fin=False, seq=self.seq_num + 2, payload=b"")

                    # Mandar el ACK 3 veces usando el socket interno
                    for _ in range(3):
                        udp_socket.sendto(ACK_segment, self.dest_adr)

                        # Esperar timeout entre cada envío
                        udp_socket.settimeout(self.timeout)

                        try:
                            udp_socket.recvfrom(self.buffer_size_UDP)
                        except (socket.timeout, ConnectionResetError):
                            pass

                    self.sock.close()
                    print("conexion cerrada")
                    return

            except socket.timeout:
                print("Timeout: reenviando FIN")

        print("No se recibio FIN+ACK despues de 3 timeouts")
        print("Asumiendo que la contraparte se cerro")

        self.sock.close()


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

            # Esperar ACK seq=z+2 hasta 3 timeouts
            for intento in range(3):

                self.sock.settimeout(10)

                try:
                    mensaje, address = self.sock.recvfrom(self.buffer_size_UDP)
                    mensaje_parseado = self.parse_segment(mensaje)

                    if (mensaje_parseado["ACK"] and mensaje_parseado["seq"] == seq_fin + 2):
                        # Cierre completado
                        self.sock.close()
                        print("conexion cerrada")
                        return

                except socket.timeout:
                    print(f"Timeout {intento + 1}/3 esperando ACK final")

        # Después del tercer timeout asumimos que la contraparte se cerró
        print("No se recibio ACK final. Asumiendo que la contraparte se cerro.")

        self.sock.close()


    #2.2
    def send_using_go_back_n(self, message: bytes):
    
            # 1. Transición a SocketUDP y manejo de ACK pendiente de handshake (caso borde)
            if not isinstance(self.sock, SocketUDP):
                self.sock.settimeout(self.timeout)
                try:
                    mensaje, direccion = self.sock.recvfrom(self.buffer_size_UDP)
                    mensaje_parseado = self.parse_segment(mensaje)
                    if mensaje_parseado["SYN"] and mensaje_parseado["ACK"] and direccion == self.handshake_addr:
                        ACK_segment = self.create_segment(ack=True, syn=False, fin=False, seq=self.seq_num, payload=b"")
                        self.sock.sendto(ACK_segment, self.handshake_addr)
                except (socket.timeout, Exception):
                    pass        

                local_address = self.sock.getsockname()
                self.sock.close()       

                new_socket_udp = SocketUDP()
                new_socket_udp.bind(local_address)
                self.sock = new_socket_udp  

            # 2. Envío de cabecera con el tamaño total del mensaje
            message_length = len(message)
            self.sock.settimeout(5.0)   

            first_message = self.create_segment(
                ack=False, syn=False, fin=False, seq=self.seq_num, payload=message_length.to_bytes(4, byteorder="big")) 

            while True:
                self.sock.sendto(first_message, self.dest_adr, timer_index=0)
                if self.debug:
                    print(self.parse_segment(first_message))    

                ack_recibido = False
                while True:
                    try:
                        mensaje, direccion = self.sock.recvfrom(self.buffer_size_UDP)
                        mensaje_parseado = self.parse_segment(mensaje)  

                        if mensaje_parseado["ACK"] and mensaje_parseado["seq"] == self.seq_num:
                            self.safe_stop_timer(0)
                            ack_recibido = True
                            break
                    except (TimeoutError, socket.timeout):
                        print("Timeout o respuesta inválida para mensaje inicial. Reenviando...")
                        self.safe_stop_timer(0)
                        break   

                if ack_recibido:
                    break   

            if message_length == 0:
                return  

            # 3. Fragmentación del mensaje en trozos de MSS bytes
            MSS = 8
            data_list = [message[i : i + MSS] for i in range(0, message_length, MSS)]
            total_chunks = len(data_list)   

            # 4. Inicialización de CongestionControl, window_size y SlidingWindowCC 

            if self.congestion_control_on:
                congestion_controller = CongestionControl.CongestionControl(MSS=MSS)
                window_size = max(1, int(congestion_controller.get_MSS_in_cwnd()))      # Calcular cuantos segmentos caben en la vantana    

            else:
                congestion_controller = None
                window_size = 8 

            data_window = SlidingWindowCC(window_size=window_size,data_list=data_list,initial_seq=self.seq_num) 

            sent = [False] * total_chunks
            chunks_acked = 0
            self.sock.settimeout(5.0)   

            # 5. Bucle principal de transmisión Go Back-N
            while chunks_acked < total_chunks:  

                # Sincronizar data_window con el window_size actual
                data_window.update_window_size(window_size) 

                self.print_debug_cc(congestion_controller, "INICIO VENTANA",data_window)    

                # Garantizar que el arreglo de rastreo 'sent' tenga capacidad suficiente
                while len(sent) < data_window.window_size:
                    sent.append(False)  

                # Enviar consecutivamente todos los elementos no enviados dentro de la ventana
                for i in range(data_window.window_size):
                    data = data_window.get_data(i)
                    if data is None:
                        break   

                    if not sent[i]:
                        seq = data_window.get_sequence_number(i)
                        tcp_segment = self.create_segment(ack=False, syn=False, fin=False, seq=seq, payload=data)
                        self.sock.sendto(tcp_segment, self.dest_adr, timer_index=0)
                        if self.debug:
                            print(self.parse_segment(tcp_segment))
                        sent[i] = True  

                # Esperar confirmación (ACK) o Timeout
                try:
                    mensaje, direccion = self.sock.recvfrom(self.buffer_size_UDP)
                    mensaje_parseado = self.parse_segment(mensaje)  

                    if mensaje_parseado["ACK"]:
                        ack_seq = mensaje_parseado["seq"]   

                        # Bucle para procesar el ACK, incluyendo cuando el ACK excede el límite de la ventana reducida por el CC
                        while chunks_acked < total_chunks:
                            current_wnd_size = data_window.window_size
                            steps_to_move = 0   

                            for i in range(current_wnd_size):
                                data_i = data_window.get_data(i)
                                if data_i is None:
                                    break   

                                seq_i = data_window.get_sequence_number(i)
                                expected_ack = seq_i + len(data_i)  

                                if ack_seq >= expected_ack:
                                    steps_to_move = i + 1   

                            if steps_to_move == 0:
                                break  # El ACK no confirma ningún paquete adicional en la ventana actual   

                            # Desplazar la ventana según las confirmaciones
                            data_window.move_window(steps_to_move)
                            chunks_acked += steps_to_move
                            sent = sent[steps_to_move:] + [False] * steps_to_move
                            self.seq_num = ack_seq
                            self.safe_stop_timer(0) 

                            # Si el Control de Congestión está activo, procesar eventos y actualizar window_size
                            if self.congestion_control_on and congestion_controller is not None:
                                for _ in range(steps_to_move):
                                    congestion_controller.event_ack_received()  

                                window_size = max(1, int(congestion_controller.get_MSS_in_cwnd()))
                                data_window.update_window_size(window_size)
                                self.print_debug_cc(congestion_controller, "ACK RECIBIDO", data_window) 

                            # CASO BORDE: si el ACK cayó dentro del rango de la ventana previa
                            # (no superó el final de la ventana completa), finalizar el procesamiento del ACK
                            if steps_to_move < current_wnd_size:
                                break   

                except (TimeoutError, socket.timeout):
                    print("Timeout en Go-Back-N. Reenviando...")
                    self.safe_stop_timer(0) 

                    # Evento Timeout en Control de Congestión
                    if self.congestion_control_on and congestion_controller is not None:
                        congestion_controller.event_timeout()
                        window_size = max(1, int(congestion_controller.get_MSS_in_cwnd()))
                        data_window.update_window_size(window_size)
                        self.print_debug_cc(congestion_controller, "TIMEOUT", data_window)  

                    # Reiniciar banderas de envío para retransmitir la ventana actual
                    sent = [False] * total_chunks


    # Para mantener una consistencia de como funcionan los send y recover, el n° seq ira incrementando con el largo del mensaje => mensaje de 16 bits => se devuelve un ack con seq == y + 16
    # en el expected_seq en el paso 3, ese sera por ejemplo Y (Q representara el n°seq inicial) luego al recibir el primer paquete, que no sea el del largo total, el n°seq igualmente sera Y 
    # eso porque no se considero en la creacion de la slidingwindow
    # Lo hice asi porque me ahorra el cacho de aumentar en un paquete mas la sliding window y no añadir el mensaje del largo como segmento en el conjunto de segmentos por enviar...

    def recv_using_go_back_n(self, buff_size: int) -> bytes:

        # 1. Transición a SocketUDP conservando la dirección/puerto si aún no se ha realizado
        if not isinstance(self.sock, SocketUDP):
            local_address = self.sock.getsockname()
            self.sock.close()

            new_socket_udp = SocketUDP()
            new_socket_udp.bind(local_address)
            self.sock = new_socket_udp

        # 2. Recepción del mensaje de tamaño total
        if self.remaining_bytes == 0:
            if self.fin_segment_received is not None:
                return b""

            while True:
                mensaje, address = self.sock.recvfrom(self.buffer_size_UDP)
                mensaje_parseado = self.parse_segment(mensaje)

                if mensaje_parseado["FIN"]:
                    self.fin_segment_received = (mensaje_parseado, address)
                    return b""

                # Validar que sea el paquete de largo esperado (seq correcto y 4 bytes)
                if mensaje_parseado["seq"] == self.seq_num and len(mensaje_parseado["payload"]) == 4:
                    self.remaining_bytes = int.from_bytes(mensaje_parseado["payload"], byteorder="big")
                    self.seq_num = mensaje_parseado["seq"]

                    print("enviando segmento ack")
                    first_ack = self.create_segment(ack=True, syn=False, fin=False, seq=self.seq_num, payload=b"")
                    self.sock.sendto(first_ack, address)
                    break
                else:
                    # Paquete basurita/duplicado de una transmisión previa: descartar y responder ACK
                    ack_segment = self.create_segment(ack=True, syn=False, fin=False, seq=self.seq_num, payload=b"")
                    self.sock.sendto(ack_segment, address)


        # 3. Configuración de buffer y secuencia esperada (Receptor N=1)
        target = min(self.remaining_bytes + len(self.pending_data), buff_size)
        payload_buffer = self.pending_data
        self.pending_data = b""

        expected_seq = self.seq_num


        # 4. Bucle de recepción estricta en orden
        while len(payload_buffer) < target and self.remaining_bytes > 0:


            mensaje, address = self.sock.recvfrom(self.buffer_size_UDP)
            mensaje_parseado = self.parse_segment(mensaje)


            if mensaje_parseado["FIN"]:
                self.fin_segment_received = (mensaje_parseado, address)
                break

            seq = mensaje_parseado["seq"]
            payload = mensaje_parseado["payload"]


            if seq == expected_seq:
                payload_buffer += payload
                self.remaining_bytes -= len(payload)
                expected_seq += len(payload)
                self.seq_num = expected_seq

                ack_segment = self.create_segment(ack=True, syn=False, fin=False, seq=self.seq_num, payload=b"")
                self.sock.sendto(ack_segment, address)
            else:

                # llega un duplicado o no en orden de lo q se esperaba => descartar y no mandar nada...


                ack_segment = self.create_segment(ack=True, syn=False, fin=False, seq=self.seq_num, payload=b"")
                self.sock.sendto(ack_segment, address)


        if len(payload_buffer) > target:
            self.pending_data = payload_buffer[target:]
            payload_buffer = payload_buffer[:target]

        return payload_buffer





    

    def safe_stop_timer(self, timer_index=0):
        try:
            if hasattr(self.sock, 'stop_timer'):
                self.sock.stop_timer(timer_index)
        except (AttributeError, Exception):
            pass

    # Función setter para modificar la variable congestion_control_on
    def set_congestion_control_on(self, value: bool) -> None:
        """Permite activar (True) o desactivar (False) el control de congestión."""
        self.congestion_control_on = bool(value)

    def set_debug(self, value: bool) -> None:
        """Activa o desactiva las impresiones de depuración de la ventana de congestión."""
        self.debug = bool(value)


    def print_debug_cc(self, controller, evento: str, data_window=None):
        """Imprime el estado detallado de la ventana de congestión y su contenido en modo debug."""
        if self.debug and controller is not None:
            cwnd_bytes = controller.get_cwnd()
            cwnd_mss = controller.get_MSS_in_cwnd()
            state = controller.current_state
            ssthresh = controller.get_ssthresh()
            
            print("=" * 60)
            print(f"[DEBUG CC - {evento}]")
            print(f"  • Estado    : {state}")
            print(f"  • cwnd      : {cwnd_bytes} bytes ({cwnd_mss} MSS)")
            print(f"  • ssthresh  : {ssthresh if ssthresh is not None else 'N/A'}")
            
            if data_window is not None:
                seqs = [
                    data_window.get_sequence_number(i)
                    for i in range(data_window.window_size)
                    if data_window.get_data(i) is not None
                ]
                print(f"  • Secuencias en Ventana: {seqs}")
            print("=" * 60)