from smbus2 import SMBus, i2c_msg
import time
I2C_BUS = 1
SENSOR_ADDR = 0x40  

bus = SMBus(I2C_BUS)

def _calculate_crc(msb, lsb):
    crc = 0x00
    for byte in [msb, lsb]:
        crc ^= byte

        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x31
            else:
                crc <<= 1

            crc &= 0xFF
    return crc

def decode(msg, type='int'): # no se si poner el type, puede ser mas como la posicion y tener un diccionario que asigne un type a cada posicion
    if type== 'int':
        decoded_msg = int.from_bytes(msg, byteorder='big')

    return decoded_msg

def read_flow_no_usar(comando):
    """
    Lee 2 bytes + CRC desde el sensor usando smbus2
    """

    # comando de 16 bits -> MSB / LSB
    msb = (comando >> 8) & 0xFF
    lsb = comando & 0xFF

    # mensaje de escritura
    bus.write_i2c_block_data(SENSOR_ADDR, None, [lsb,msb])
    """time.sleep(0.1)
    # mensaje de lectura (2 bytes datos + 1 CRC)
    read = bus.read_i2c_block_data(SENSOR_ADDR, 0, 3)

    rx_msb = read[0]
    rx_lsb = read[1]
    rx_crc = read[2]

    calc_crc = _calculate_crc(rx_msb, rx_lsb)

    if rx_crc == calc_crc:
        valor= (rx_msb, rx_lsb)
        return valor"""

def read_flow_chad(comando):

    msb = (comando >> 8) & 0xFF
    lsb = comando & 0xFF

    read= bus.read_i2c_block_data(0x40, 0x10, 2)

    # repeated start automático

    data = list(read)

    rx_msb = data[0]
    rx_lsb = data[1]
    rx_crc = data[2]

    calc_crc = _calculate_crc(rx_msb, rx_lsb)

    if rx_crc != calc_crc:
        raise ValueError("CRC incorrecto")

    return bytearray([rx_msb, rx_lsb])



"""with SMBus(1) as bus:

    # start measurement

    write = i2c_msg.write(0x40, [0x10, 0x00])

    read = i2c_msg.read(0x40, 3)

    bus.i2c_rdwr(write, read)

print(list(read))
"""

def _delay_us(us):
    start = time.perf_counter()

    while (time.perf_counter() - start) < (us / 1_000_000):
        pass


def init_flowmeter():
    with SMBus(I2C_BUS) as bus:
       
        write = i2c_msg.write(0x40, [0x10, 0x00])
        bus.i2c_rdwr(write)

        time.sleep(0.1000)

        read = i2c_msg.read(0x40, 3)
        bus.i2c_rdwr(read)
        

def read_flow():
    with SMBus(I2C_BUS) as bus:
        write = i2c_msg.write(0x40, [0x10, 0x00])
        bus.i2c_rdwr(write)

        _delay_us(1000)

        read = i2c_msg.read(0x40, 3)
        bus.i2c_rdwr(read)
        data=list(read)
        rx_msb = data[0]
        rx_lsb = data[1]
        rx_crc = data[2]

        calc_crc = _calculate_crc(rx_msb, rx_lsb)

        if rx_crc == calc_crc:
            value= (rx_msb << 8) | rx_lsb
            return round((value - 32000)/140,4)

def i2c_task(data, stop_event, contrast):
    if contrast:
        fs=249
    else:
        fs = 256
    while not stop_event.is_set():
        tsart= time.perf_counter()
        value= read_flow()
        data.append(value)
        while(time.perf_counter()-tsart < 1/fs):
            pass



from smbus2 import SMBus, i2c_msg
import time


class SensirionDevice:

    def __init__(
        self,
        bus_number=1,
        address=0x40,
        read_delay=0.001,
    ):
        self.bus_number = bus_number
        self.address = address
        self.read_delay = read_delay

        self.bus = None

        self.crc_errors = 0
        self.samples_ok = 0


    # ==========================================================
    # CONNECTION
    # ==========================================================

    def open(self):

        if self.bus is not None:
            return

        self.bus = SMBus(
            self.bus_number
        )


    def close(self):

        if self.bus is not None:

            self.bus.close()
            self.bus = None


    @property
    def is_open(self):
        return self.bus is not None


    def _check_open(self):

        if not self.is_open:

            raise RuntimeError(
                "SensirionDevice: "
                "I2C bus is not open"
            )


    # ==========================================================
    # CRC
    # ==========================================================

    @staticmethod
    def _calculate_crc(msb, lsb):

        crc = 0x00

        for byte in (msb, lsb):

            crc ^= byte

            for _ in range(8):

                if crc & 0x80:
                    crc = (
                        (crc << 1)
                        ^ 0x31
                    )

                else:
                    crc <<= 1

                crc &= 0xFF

        return crc


    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def initialize(self):

        self._check_open()

        write = i2c_msg.write(
            self.address,
            [0x10, 0x00],
        )

        self.bus.i2c_rdwr(
            write
        )

        time.sleep(0.1)

        # Primera lectura para comprobar
        # que el sensor responde
        read = i2c_msg.read(
            self.address,
            3,
        )

        self.bus.i2c_rdwr(
            read
        )


    # ==========================================================
    # READ
    # ==========================================================

    def read_flow(self):

        self._check_open()

        write = i2c_msg.write(
            self.address,
            [0x10, 0x00],
        )

        self.bus.i2c_rdwr(
            write
        )

        time.sleep(
            self.read_delay
        )

        read = i2c_msg.read(
            self.address,
            3,
        )

        self.bus.i2c_rdwr(
            read
        )

        data = list(read)

        rx_msb = data[0]
        rx_lsb = data[1]
        rx_crc = data[2]

        crc = self._calculate_crc(
            rx_msb,
            rx_lsb,
        )

        if crc != rx_crc:

            self.crc_errors += 1

            return None

        raw = (
            (rx_msb << 8)
            | rx_lsb
        )

        flow = (
            raw - 32000
        ) / 140

        self.samples_ok += 1

        return round(
            flow,
            4,
        )


    # ==========================================================
    # ACQUISITION
    # ==========================================================

    def acquisition_task(
        self,
        data_list,
        stop_event,
        sample_rate=250,
    ):

        period = (
            1.0 / sample_rate
        )

        next_sample = (
            time.perf_counter()
        )

        while not stop_event.is_set():

            flow = self.read_flow()

            timestamp = (
                time.perf_counter_ns()
            )

            if flow is not None:

                data_list.append(
                    #(
                        #timestamp,
                    flow#,   # sacar todos los # y sumar un tab aca
                    #)
                )

            next_sample += period

            remaining = (
                next_sample
                - time.perf_counter()
            )

            if remaining > 0:

                stop_event.wait(
                    remaining
                )

            else:

                next_sample = (
                    time.perf_counter()
                )


    # ==========================================================
    # DIAGNOSTICS
    # ==========================================================

    def get_stats(self):

        return {
            "samples_ok":
                self.samples_ok,

            "crc_errors":
                self.crc_errors,
        }


    # ==========================================================
    # CONTEXT MANAGER
    # =========================================================

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