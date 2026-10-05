import socket

buffer = 16
address = ("localhost", 8000)

if __name__ == "__main__":
    #socket tipo UDP    
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        message = input("Ingrese un mensaje: ")

        # Si el tamano del mensaje es mayor al buffer, se divide en partes y se envía cada parte
        if len(message) > buffer:
            for i in range(0,len(message), buffer):
                packet = message[i:i+ buffer]
                socket.sendto(packet.encode(),address)
        # Si el mensaje es menor al buffer, se envia directamente                
        else:
            socket.sendto(message.encode(),address)


