import socket
import dnslib
from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE

root_ip = ("198.41.0.4", 8000)

#  la cual recibe el mensaje de query en bytes obtenido desde el cliente. Dentro de esta función, siga el siguiente procedimiento para obtener la respuesta:

def resolver(mensaje_consulta: bytes, ip_addr=root_ip) -> bytes:
    # Envíe el mensaje query a la IP indicada por ip_addr y espere su respuesta. Note que por defecto la variable ip_addr corresponde a la IP del servidor 
    # raíz. Existen múltiples IPs asociadas al sevidor raíz, para esta actividad puede utilizar la siguiente IP: 198.41.0.4 .

    server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    server_socket.bind(ip_addr)

    server_socket.send(mensaje_consulta)

    while True:
        message = server_socket.recvfrom(4096)
        parsed_message = parse_DNS_message(message)

        #checkear si el mensaje tiene la respuesta a la consulta
        if parsed_message["ANCOUNT"]> 0:
            for answer in parsed_message["answer"]:
                if answer.rtype == 1:
                    return mensaje_consulta


        # PARTE C
        seccion_autoridad = parsed_message["Authority"]
        authority_section_rr_0 = seccion_autoridad[0]
        auth_type = QTYPE.get(authority_section_rr_0.rtype)

# =================================================
def parse_DNS_message(dns_message):
    dns = DNSRecord.parse(dns_message)

    return {
        "Qname": str(dns.q.qname),
        "ANCOUNT": len(dns.rr),
        "NSCOUNT": len(dns.auth),
        "ARCOUNT": len(dns.ar),
        "Answer": dns.rr,
        "Authority": dns.auth,
        "Additional": dns.ar
    }

# =================================================

#Usar socket no orientado a objetos
# Usar while loop creo

# Hacer rapidito y veamos q sucede

if __name__ == "__main__":

    print("iniciando script")
    
    server_socket_address = ("10.0.2.15", 8000)

    server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    server_socket.bind(server_socket_address)
    #Loop para obtener mensajes

    print("se entra a loop\n\n")

    while True:

        data,_ = server_socket.recvfrom(4096)
        
        # Aca recibimos el mensaje DNS... 
        # La dificultad esta en como podemos hacer para dejarlo entendible el mensaje ...
        #Bueno como es DNS nos llega en formato de bytes por pasar a rtavez de  un socket.
        # Y la info tambien debe estar como bytes y no como hexadecimal..
        # ==> Podriamos una vez obtenido el mensaje hacerle una hexificacion...
        # EFECTIAMENTE ERA ESO PEEEERO LO HARE CON DNSRecord xq me hace la vida mas facil.

        data_parsed = parse_DNS_message(data)
        print(f"{data_parsed}\n\n")
        print("JUAN")