import socket
import socketTCP

buffer = 21
address = ("localhost", 8000)

if __name__ == "__main__":
    ##socket tipo UDP    
    #socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #while True:

    #    #Test 3ra parte (Añadir headers TCP a los datos por enviar)
    #    tcp_socket = socketTCP.SocketTCP()
   # 
    #    message = input("Ingrese un mensaje: ")



    #    # Modificiar cliente para añadir headers tcp a los datos por enviar...
    #    # para ello, crear un sockettcp y desde el cliente, llamo a las opciones, luego el resultado lo envio.... 
    #    # Se hace modificacion para que se permita siempre que el payload sea de 16 bytes (Restamos 5 bytes para el header... y aumentamos el buffer a 21 bytes)
    #    # Si el tamano del mensaje es mayor al buffer, se divide en partes y se envía cada parte
    #    
    #    if len(message) > buffer - 5:
    #        for i in range(0,len(message), buffer-5):
    #            packet = message[i:i+ buffer-5]

    #            # Usar tcp_socket para crear segmento tcp con flags y numero de secuencia
    #            tcp_segment = tcp_socket.create_segment(ack=False, syn=False, fin=False, seq=i//(buffer-5), payload=packet.encode())

    #            socket.sendto(tcp_segment,address)

    #    # Si el mensaje es menor al buffer, se envia directamente                
    #    else:
    #        tcp_segment = tcp_socket.create_segment(ack=False, syn=False, fin=False, seq=0, payload=message.encode())
    #        socket.sendto(tcp_segment,address)

    # CLIENT
    client_socketTCP = socketTCP.SocketTCP()
    client_socketTCP.connect(address)
    # test 1
    message = "Mensje de len=16".encode()
    client_socketTCP.send(message)
    # test 2
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message)
    # test 3
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message)
    client_socketTCP.recv_close()

