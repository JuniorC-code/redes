class CongestionControl:
    def __init__(self, MSS: int):
        self.current_state = "slow start"
        self.MSS = MSS
        self.cwnd: int = MSS                     # Representa el total de bytes que puede tener la ventana de congestion
        self.ssthresh = None


    # Debe retornar el valor cwnd almacenado en congestionControl, corresponde al tamaño en bytes
    # Como cwnd representa un tamaño en bytes, su valor sigue siendo un entero (int), no un objeto bytes
    def get_cwnd(self) -> bytes:
        return self.cwnd

    # Añada a su clase CongestionControl la función get_MSS_in_cwnd()-> int. Esta función retorna la el tamaño de la ventana expresado como la cantidad de 
    # MSSs completos que caben en cwnd. Por ejemplo si su función get_cwnd() retorna 17 bytes y MSS = 4, entonces get_MSS_in_cwnd() deberá retornar 4.

    def get_MSS_in_cwnd(self) -> int:
         return self.cwnd // self.MSS


    # Añada a su clase CongestionControl la función event_ack_received(). Esta función se encargará de manejar los cambios asociados a la recepción de ACKs. 
    # Por ejemplo, si su current_state es slow start entonces recibir un ACK resultará en el aumento de cwnd en 1 MSS. Similarmente event_ack_received deberá
    # manejar el caso en que current_state sea igual congestion avoidance. Para los aumentos en congestion avoidance, note que cada aumento corresponde a una 
    # fracción (1/self.get_MSS_in_cwnd()) de MSS. No olvide que al aumentar el cwnd 
    # debe checkear si dicho aumento genera un cambio en el estado current_state. Si se genera un cambio de estado recuerde actualizar sus otras variables según sea necesario.
    
    def event_ack_received(self):
        if self.current_state == "slow start":
            self.cwnd += self.MSS

            if self.ssthresh is not None and self.cwnd >= self.ssthresh:
                self.current_state = "congestion avoidance"

        elif self.current_state == "congestion avoidance":
            mss_in_cwnd = self.get_MSS_in_cwnd()
            self.cwnd += self.MSS / mss_in_cwnd


    # Añada a su clase CongestionControl la función event_timeout(). Esta función se encargará de manejar los cambios asociados a que ocurra timeout. 
    # Por ejemplo, si es la primera vez que ocurre timeout dentro de slow start entonces
    # deberá inicializar el valor de ssthresh. Esta función también deberá manejar los cambios de estado, de tamaño de ventana de congestión y de Slow Start threshold.

    # notar que como en ambos casos de cong avoidance como slow start se genera lo mismo, no es necesario usar if's para los diferentes casos...
    def event_timeout(self):
        self.ssthresh = self.cwnd // 2
        self.cwnd = self.MSS
        self.current_state = "slow start"

    def is_state_slow_start(self):
        return self.current_state == "slow start"

    def is_state_congestion_avoidance(self):
        return self.current_state == "congestion avoidance"

    def get_ssthresh(self):
        return self.ssthresh