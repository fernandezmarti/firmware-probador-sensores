import serial
import numpy as np

class TSIDevice:
    """
    Interfaz para TSI Series 4000 / 4100 mediante RS232.

    Funciones:
        - ping()
        - set_sample_period()
        - read_flow()
        - read_flow_continuous()
        - stop()
    """

    def __init__(
        self,
        port: str,
        series: int = 4000,
        timeout: float = 1.0,
        block_size: int = 500,
    ):
        if series not in (4000, 4100):
            raise ValueError("series debe ser 4000 o 4100")

        if not 1 <= block_size <= 1000:
            raise ValueError("block_size debe estar entre 1 y 1000")

        self.port = port
        self.series = series
        self.timeout = timeout
        self.block_size = block_size

        # Factor de conversión de flujo
        # 4000 -> valor transmitido x100
        # 4100 -> valor transmitido x1000
        self.flow_scale = 100 if series == 4000 else 1000

        self.ser = None
        self.running = False

    # ---------------------------------------------------------
    # CONEXIÓN
    # ---------------------------------------------------------

    def open(self):
        """Abre el puerto serie."""

        if self.ser is not None and self.ser.is_open:
            return
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=38400,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False,
            )

            # Limpiar cualquier dato viejo
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
        except Exception:
            return False

    def close(self):
        """Cierra el puerto serie."""

        self.running = False

        if self.ser is not None and self.ser.is_open:
            self.ser.close()

    # ---------------------------------------------------------
    # COMANDOS
    # ---------------------------------------------------------

    def _send_command(self, command: str):
        """
        Envía un comando ASCII terminado en CR.
        """

        if self.ser is None or not self.ser.is_open:
            raise RuntimeError("El puerto serie no está abierto")

        self.ser.write(command.encode("ascii") + b"\r")

    def _read_ascii_response(self) -> str:
        """
        Lee una respuesta ASCII terminada en CR/LF.
        """

        response = self.ser.read_until(b"\r\n")

        return response.decode("ascii", errors="replace").strip()

    # ---------------------------------------------------------
    # PING
    # ---------------------------------------------------------

    def ping(self) -> bool:
        """
        Comprueba si el TSI está respondiendo.

        Retorna:
            True  -> recibió OK
            False -> no recibió OK
        """

        self.ser.reset_input_buffer()

        self._send_command("?")

        response = self._read_ascii_response()

        return response == "OK"

    # ---------------------------------------------------------
    # SAMPLE PERIOD
    # ---------------------------------------------------------

    def set_sample_period(self, period_ms: int):
        """
        Configura el período de muestreo del TSI.

        period_ms:
            1 ... 1000 ms

        Ejemplo:
            set_sample_period(4)

        -> SSR0004
        -> 4 ms
        -> 250 Hz
        """

        if not 1 <= period_ms <= 1000:
            raise ValueError(
                "El período debe estar entre 1 y 1000 ms"
            )

        command = f"SSR{period_ms:04d}"

        self.ser.reset_input_buffer()

        self._send_command(command)

        response = self._read_ascii_response()

        if response != "OK":
            raise RuntimeError(
                f"Error configurando sample period: {response}"
            )

    # ---------------------------------------------------------
    # LECTURA DE UN BLOQUE
    # ---------------------------------------------------------

    def read_flow(self, n_samples):

        command = f"DBFxx{n_samples:04d}\r".encode()
        self.ser.write(command)

        # ACK
        ack = self.ser.read(1)

        if ack != b'\x00':
            raise RuntimeError(f"Error del TSI: {ack.hex()}")

        expected_bytes = n_samples * 2
        buffer = bytearray()

        while len(buffer) < expected_bytes + 2:

            data = self.ser.read(
                expected_bytes + 2 - len(buffer)
            )

            if not data:
                raise TimeoutError("Timeout esperando datos del TSI")

            buffer.extend(data)

        # Los últimos dos bytes deberían ser FF FF
        if buffer[-2:] != b'\xff\xff':
            raise RuntimeError("Terminador incorrecto")

        # Sacar terminador
        buffer = buffer[:-2]

        # Convertir de 2 bytes -> flujo
        # flow = [
        #     int.from_bytes(buffer[i:i+2], "big") / self.flow_scale
        #     for i in range(0, len(buffer), 2)
        # ]
        raw = np.frombuffer(buffer, dtype=">u2")
        flow = raw / self.flow_scale

        return flow
    # -----------------------------------------------
    # LECTURA CONTINUA 
    # -----------------------------------------------

    def read_flow_continuous(self, stop_event):
        flow_data = []

        while not stop_event.is_set():

            block = self.read_flow(self.block_size)

        return block

    # ---------------------------------------------------------
    # STOP
    # ---------------------------------------------------------

    def stop(self):
        """
        Detiene la lectura continua.
        """

        self.running = False


def tsi_acquisition_task(tsi, data_queue, stop_event):

    while not stop_event.is_set():

        try:
            block = tsi.read_flow(500)
            data_queue.put(block)

        except Exception as e:
            print(f"Error en TSI: {e}")
            break

