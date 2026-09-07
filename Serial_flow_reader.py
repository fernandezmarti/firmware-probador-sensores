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


class FluxmedDevice:

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
                            