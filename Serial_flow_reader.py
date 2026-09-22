import serial
import time
from collections import deque
import numpy as np

PORT="/dev/ttyUSB0"
BAUDRATE = 115200

START_BYTE = 0x55
FRAME_SIZE = 15

def calibrate():

    buffer = bytearray()
    calibrating=True

    with serial.Serial(
        PORT,
        BAUDRATE,
        timeout=0.01) as ser:
        ser.write(b'\x63')
        ser.flush()
        print("calibrando")

        while calibrating:

            # Leer chunk grande
            data = ser.read(64)

            if data:
                buffer.extend(data)

            # Parsear frames
            while True:

                # Buscar start byte
                try:
                    idx = buffer.index(START_BYTE)
                except ValueError:
                    buffer.clear()
                    break

                # Descartar basura antes del start
                if idx > 0:
                    del buffer[:idx]

                # Esperar frame completo
                if len(buffer) < FRAME_SIZE:
                    break

                # Extraer frame
                frame = buffer[:FRAME_SIZE]
                
                # Sacarlo del buffer
                del buffer[:FRAME_SIZE]
                if frame[1]==4:
                    checksum_rx = frame[-1]

                    checksum_calc = (
                        sum(frame[:-1])
                    ) & 0xFF

                    if checksum_calc == checksum_rx:

                        if frame[2]==255 and frame[3]==255:
                            print("Calibracion exitosa")
                            calibrating=False
                            #break
                        elif frame[2]==254 and frame[3]==255:
                            print("Fallo la calibracion \nCalibrando...")
                            ser.write(b'\x63')
                            ser.flush()

                   

def serial_task(data_list, stop_event):

    buffer = bytearray()

    with serial.Serial(
        PORT,
        BAUDRATE,
        timeout=0.01) as ser:

        while not stop_event.is_set():

            # Leer chunk grande
            data = ser.read(64)

            if data:
                buffer.extend(data)

            # Parsear frames
            while True:

                # Buscar start byte
                try:
                    idx = buffer.index(START_BYTE)
                except ValueError:
                    buffer.clear()
                    break

                # Descartar basura antes del start
                if idx > 0:
                    del buffer[:idx]

                # Esperar frame completo
                if len(buffer) < FRAME_SIZE:
                    break

                # Extraer frame
                frame = buffer[:FRAME_SIZE]

                # Sacarlo del buffer
                del buffer[:FRAME_SIZE]

                checksum_rx = frame[-1]

                checksum_calc = (
                    sum(frame[:-1])
                ) & 0xFF

                if checksum_calc == checksum_rx:

                    valor = (
                        int.from_bytes(
                            frame[4:6],
                            "little",
                            signed=True
                        ) / 16.0
                    )
                   
                    data_list.append(valor)




def detect_sensor(stop_event):
    buffer = bytearray()

    with serial.Serial(
        PORT,
        BAUDRATE,
        timeout=0.01) as ser:
        
        while not stop_event.is_set():

            # Leer chunk grande
            data = ser.read(64)

            if data:
                buffer.extend(data)

            # Parsear frames
            while True:

                # Buscar start byte
                try:
                    idx = buffer.index(START_BYTE)
                except ValueError:
                    buffer.clear()
                    break

                # Descartar basura antes del start
                if idx > 0:
                    del buffer[:idx]

                # Esperar frame completo
                if len(buffer) < FRAME_SIZE:
                    break

                # Extraer frame
                frame = buffer[:FRAME_SIZE]

                # Sacarlo del buffer
                del buffer[:FRAME_SIZE]

                checksum_rx = frame[-1]

                checksum_calc = (
                    sum(frame[:-1])
                ) & 0xFF

                if checksum_calc == checksum_rx:

                    valor = (
                        int.from_bytes(
                            frame[4:6],
                            "little",
                            signed=True
                        ) / 16.0
                    )
                    return False if -5<valor<5 else True
                
                   
                    
def read_frame(ser, buffer):

    data = ser.read(64)

    if data:
        buffer.extend(data)

    while True:

        try:
            idx = buffer.index(START_BYTE)

        except ValueError:
            buffer.clear()
            return None

        if idx > 0:
            del buffer[:idx]

        if len(buffer) < FRAME_SIZE:
            return None

        frame = buffer[:FRAME_SIZE]
        del buffer[:FRAME_SIZE]

        checksum_rx = frame[-1]

        checksum_calc = (
            sum(frame[:-1])
        ) & 0xFF

        if checksum_calc == checksum_rx:
            return frame
        else:
            return None
        
def serial_taskV2(data_list, stop_event):

    buffer = bytearray()

    with serial.Serial(
        PORT,
        BAUDRATE,
        timeout=0.01
    ) as ser:

        while not stop_event.is_set():

            frame = read_frame(
                ser,
                buffer
            )

            if frame is None:
                continue

            valor = (
                int.from_bytes(
                    frame[4:6],
                    "little",
                    signed=True
                ) / 16.0
            )

            data_list.append(valor)

def detect_sensor(n=64, threshold=7):
    
    buffer = bytearray()
    #connected=True #se puede hacer algo asi xon un flag
    last_n_samples= []
    with serial.Serial(
        PORT,
        BAUDRATE,
        timeout=0.01
    ) as ser:
        while len(last_n_samples)<n:
            frame = read_frame(
                ser,
                buffer
            )

            if frame is None:
                continue

            valor = (
                int.from_bytes(
                    frame[4:6],
                    "little",
                    signed=True
                ) / 16.0
            )
            last_n_samples.append(valor)
        if -threshold<np.mean(np.array(last_n_samples))<threshold:
            return False
        else:
            return True


def calibrateV2():

    buffer = bytearray()
    calibrating=True

    with serial.Serial(
        PORT,
        BAUDRATE,
        timeout=0.01) as ser:
        ser.write(b'\x63')
        ser.flush()
        print("calibrando")

        while calibrating:

            frame=read_frame(ser,buffer)
            if frame is None:
                continue
            elif frame[2]==255 and frame[3]==255:
                print("Calibracion exitosa")
                calibrating=False
                #break
            elif frame[2]==254 and frame[3]==255:
                print("Fallo la calibracion \nCalibrando...")
                ser.write(b'\x63')
                ser.flush()

import serial


START_BYTE = 0x55


class FluxmedDevice_NO_USAR:

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        frame_size: int = 15,
        timeout: float = 0.01
    ):
        self.port = port
        self.baudrate = baudrate
        self.frame_size = frame_size
        self.timeout = timeout

        self.ser = None

        # Buffer persistente de recepción
        self.buffer = bytearray()

    def open(self):
        if self.ser is not None and self.ser.is_open:
            return

        self.ser = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
        )

    def read_frame(self):
        """
        Extrae un frame del buffer.

        Devuelve:
            frame -> si hay un frame válido
            None  -> si todavía no hay un frame completo
                     o si el checksum es incorrecto
        """

        # Buscar START_BYTE
        try:
            idx = self.buffer.index(START_BYTE)

        except ValueError:
            self.buffer.clear()
            return None

        # Eliminar basura antes del START
        if idx > 0:
            del self.buffer[:idx]

        # Esperar frame completo
        if len(self.buffer) < self.frame_size:
            return None

        # Extraer frame
        frame = self.buffer[:self.frame_size]

        # Sacarlo del buffer
        del self.buffer[:self.frame_size]

        # Verificar checksum
        checksum_rx = frame[-1]
        checksum_calc = sum(frame[:-1]) & 0xFF

        if checksum_calc != checksum_rx:
            return None

        return frame

    def read_frames(self):
        """
        Lee nuevos datos del puerto y extrae todos los frames
        completos disponibles.

        Devuelve un generador de frames.
        """

        # Leer nuevos bytes
        data = self.ser.read(64)

        if data:
            self.buffer.extend(data)

        # Procesar todos los frames disponibles
        while True:

            frame = self.read_frame()

            if frame is None:
                break

            yield frame

    def read_flow(self):
        """
        Lee datos del puerto y genera los valores de flow
        uno por uno.

        Ejemplo:

            for flow in device.read_flow():
                queue.put(flow)
        """

        for frame in self.read_frames():

            flow = (
                int.from_bytes(
                    frame[4:6],
                    "little",
                    signed=True
                ) / 16.0
            )

            yield flow

    def calibrate(self):

        # Limpiar datos anteriores
        self.buffer.clear()

        calibrating = True

        self.ser.write(b'\x63')
        self.ser.flush()

        print("Calibrando")

        while calibrating:

            for frame in self.read_frames():

                # Solo nos interesan frames de calibración
                if frame[1] != 4:
                    continue

                # Calibración exitosa
                if frame[2] == 255 and frame[3] == 255:

                    print("Calibración exitosa")

                    calibrating = False
                    break

                # Falló la calibración
                elif frame[2] == 254 and frame[3] == 255:

                    print("Falló la calibración")
                    print("Calibrando...")

                    self.ser.write(b'\x63')
                    self.ser.flush()

    def close(self):

        if self.ser is not None and self.ser.is_open:
            self.ser.close()


class FluxmedDevice:

    START_BYTE = 0x55
    CALIBRATION_COMMAND = b"\x63"

    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 115200,
        frame_size: int = 15,
        timeout: float = 0.01,
        read_chunk_size: int = 64,
    ):
        self.port = port
        self.baudrate = baudrate
        self.frame_size = frame_size
        self.timeout = timeout
        self.read_chunk_size = read_chunk_size

        self.ser = None
        self.buffer = bytearray()

        # Diagnóstico
        self.frames_ok = 0
        self.checksum_errors = 0
        self.discarded_bytes = 0

    # ==========================================================
    # CONEXIÓN
    # ==========================================================

    def open(self):
        """Abre el puerto serie si todavía no está abierto."""

        if self.ser is not None and self.ser.is_open:
            return

        self.ser = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
        )

        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.buffer.clear()

    def close(self):
        """Cierra el puerto serie."""

        if self.ser is not None and self.ser.is_open:
            self.ser.close()

    @property
    def is_open(self):
        return self.ser is not None and self.ser.is_open

    def _check_open(self):
        if not self.is_open:
            raise RuntimeError(
                "FluxmedDevice: el puerto serie no está abierto"
            )

    # ==========================================================
    # BUFFER / FRAMES
    # ==========================================================

    def _read_serial_data(self):
        """
        Lee bytes disponibles del puerto y los agrega
        al buffer interno.
        """

        self._check_open()

        data = self.ser.read(self.read_chunk_size)

        if data:
            self.buffer.extend(data)

    def _extract_frame(self):
        """
        Busca y devuelve el próximo frame válido disponible
        en el buffer.

        Retorna:
            bytes/bytearray -> frame válido
            None            -> faltan datos

        Si encuentra un checksum incorrecto, descarta UN byte
        y vuelve a buscar START_BYTE.

        Esto evita perder un frame completo si hubo
        desincronización.
        """

        while True:

            # --------------------------------------------------
            # Buscar START_BYTE
            # --------------------------------------------------

            try:
                idx = self.buffer.index(self.START_BYTE)

            except ValueError:

                self.discarded_bytes += len(self.buffer)
                self.buffer.clear()

                return None

            # Eliminar basura previa al start byte
            if idx > 0:

                self.discarded_bytes += idx
                del self.buffer[:idx]

            # --------------------------------------------------
            # Esperar frame completo
            # --------------------------------------------------

            if len(self.buffer) < self.frame_size:
                return None

            frame = self.buffer[:self.frame_size]

            # --------------------------------------------------
            # Verificar checksum
            # --------------------------------------------------

            checksum_rx = frame[-1]
            checksum_calc = sum(frame[:-1]) & 0xFF

            if checksum_calc == checksum_rx:

                # Frame válido
                del self.buffer[:self.frame_size]

                self.frames_ok += 1

                return frame

            # --------------------------------------------------
            # Checksum incorrecto
            # --------------------------------------------------
            #
            # NO eliminamos los 15 bytes.
            #
            # Sacamos solamente el START_BYTE actual y
            # volvemos a buscar otro 0x55.
            # --------------------------------------------------

            self.checksum_errors += 1
            self.discarded_bytes += 1

            del self.buffer[0]

    def read_frames(self):
        """
        Lee nuevos bytes del puerto y devuelve todos los
        frames válidos que actualmente se puedan extraer.

        Uso:

            for frame in device.read_frames():
                ...
        """

        self._read_serial_data()

        while True:

            frame = self._extract_frame()

            if frame is None:
                break

            yield frame

    # ==========================================================
    # DECODIFICACIÓN
    # ==========================================================

    @staticmethod
    def decode_flow(frame):
        """
        Convierte un frame válido en flujo.

        El protocolo actual utiliza:
            bytes 4:6
            little endian
            signed
            escala /16
        """

        raw = int.from_bytes(
            frame[4:6],
            byteorder="little",
            signed=True,
        )

        return raw / 16.0

    def read_flow(self):
        """
        Generador de valores de flujo disponibles.

        Uso:

            for flow in device.read_flow():
                print(flow)
        """

        for frame in self.read_frames():

            yield self.decode_flow(frame)

    def read_flow_timestamped(self):
        """
        Igual que read_flow(), pero devuelve:

            timestamp, flow

        El timestamp utiliza perf_counter_ns(), útil para
        sincronizar esta señal con el Sensirion.
        """

        for frame in self.read_frames():

            timestamp = time.perf_counter_ns()
            flow = self.decode_flow(frame)

            yield timestamp, flow

    # ==========================================================
    # CALIBRACIÓN
    # ==========================================================

    def calibrate(
        self,
        timeout: float = 5.0,
        max_attempts: int = 5,
    ):
        """
        Calibra el sensor Fluxmed.

        Devuelve:
            True -> calibración exitosa

        Lanza:
            TimeoutError
            RuntimeError
        """

        self._check_open()

        self.buffer.clear()
        self.ser.reset_input_buffer()

        for attempt in range(1, max_attempts + 1):

            print(
                f"Calibrando... "
                f"intento {attempt}/{max_attempts}"
            )

            self.ser.write(self.CALIBRATION_COMMAND)
            self.ser.flush()

            start = time.perf_counter()

            while time.perf_counter() - start < timeout:

                for frame in self.read_frames():

                    # Solo frames correspondientes
                    # a calibración
                    if frame[1] != 4:
                        continue

                    # Calibración exitosa
                    if (
                        frame[2] == 255
                        and frame[3] == 255
                    ):
                        print("Calibración exitosa")
                        return True

                    # El sensor informó fallo
                    if (
                        frame[2] == 254
                        and frame[3] == 255
                    ):
                        print(
                            "Falló la calibración"
                        )

                        # salir del while para
                        # intentar nuevamente
                        break

                else:
                    # El for terminó normalmente:
                    # seguir esperando frames
                    continue

                # Se recibió fallo de calibración
                break

        raise RuntimeError(
            "No se pudo calibrar el Fluxmed "
            f"después de {max_attempts} intentos"
        )

    # ==========================================================
    # DETECCIÓN DE SENSOR
    # ==========================================================

    def detect_sensor(
        self,
        n: int = 64,
        threshold: float = 7,
        timeout: float = 2.0,
    ):
        """
        Evalúa si el sensor está conectado usando el mismo
        criterio que tu código actual:

            abs(mean(flow)) >= threshold

        Devuelve:
            True  -> sensor detectado
            False -> sensor no detectado

        Si no consigue suficientes muestras dentro del
        timeout, lanza TimeoutError.
        """

        self._check_open()

        samples = []

        start = time.perf_counter()

        while len(samples) < n:

            if time.perf_counter() - start > timeout:

                raise TimeoutError(
                    "Timeout esperando muestras "
                    "para detectar el sensor"
                )

            for flow in self.read_flow():

                samples.append(flow)

                if len(samples) >= n:
                    break

        mean_flow = np.mean(samples)

        return abs(mean_flow) >= threshold

    # ==========================================================
    # THREAD DE ADQUISICIÓN
    # ==========================================================

    def acquisition_task(
        self,
        data_list,
        stop_event,
    ):
        """
        Función pensada para ejecutarse en un Thread.

        Reemplaza directamente tu serial_task().
        """

        self._check_open()

        while not stop_event.is_set():

            for flow in self.read_flow():

                data_list.append(flow)

                if stop_event.is_set():
                    break

    def acquisition_task_timestamped(
        self,
        data_list,
        stop_event,
    ):
        """
        Variante recomendada para comparación de sensores.

        Guarda:

            (timestamp_ns, flow)
        """

        self._check_open()

        while not stop_event.is_set():

            for timestamp, flow in self.read_flow_timestamped():

                data_list.append(
                    (timestamp, flow)
                )

                if stop_event.is_set():
                    break

    # ==========================================================
    # DIAGNÓSTICO
    # ==========================================================

    def get_stats(self):
        """
        Devuelve información útil para debug.
        """

        return {
            "frames_ok": self.frames_ok,
            "checksum_errors": self.checksum_errors,
            "discarded_bytes": self.discarded_bytes,
            "buffer_size": len(self.buffer),
        }

    def reset_stats(self):

        self.frames_ok = 0
        self.checksum_errors = 0
        self.discarded_bytes = 0

    # ==========================================================
    # CONTEXT MANAGER
    # ==========================================================

    def __enter__(self):
        self.open()
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.close()