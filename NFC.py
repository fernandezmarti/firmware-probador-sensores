from smartcard.System import readers
from smartcard.Exceptions import NoCardException
import time


class NFCReader:
    def __init__(self):


        lectores = readers()

        if not lectores:
            print("No se encontró el ACR122U.")
            # raise?
            return

        else:
            self.lector = lectores[0]
            self.conexion = self.lector.createConnection()
            return



    def wait4card(self):
        while True:
            try:
                self.conexion.connect()
                break
            except:
                time.sleep(0.2)

    def send(self, comando):
        datos, sw1, sw2 = self.conexion.transmit(comando)

        print(
            "Respuesta:",
            " ".join(f"{x:02X}" for x in datos),
            f"| SW={sw1:02X} {sw2:02X}"
        )

        return datos, sw1, sw2

    def show_UID(self):

        uid, sw1, sw2 = self.send(
            [0xFF, 0xCA, 0x00, 0x00, 0x00]
        )

        print(
            "UID:",
            "".join(f"{x:02X}" for x in uid)
        )

    def load_password(self):
        clave = [
            0xFF, 0xFF, 0xFF,
            0xFF, 0xFF, 0xFF
        ]

        print("\nCargando clave...")

        datos, sw1, sw2 = self.send(
            [
                0xFF, 0x82,
                0x00, 0x00,
                0x06,
                *clave
            ]
        )

        if (sw1, sw2) != (0x90, 0x00):
            print("Error cargando la clave")
            exit()

    def authenticate_block(self, block=4):

        print(f"\nAutenticando bloque {block}...")

        datos, sw1, sw2 = self.send(
            [
                0xFF, 0x86,
                0x00, 0x00,
                0x05,
                0x01,
                0x00,
                block,
                0x60,       # Key A
                0x00
            ]
        )

        if (sw1, sw2) != (0x90, 0x00):
            print("\nNo se pudo autenticar.")
            return False
        else:
            return True

    def read_block(self, block):

        datos, sw1, sw2 = self.send(
            [
                0xFF, 0xB0,
                0x00,
                block,
                0x10
            ]
        )

        if (sw1, sw2) == (0x90, 0x00):

            #print("\nContenido HEX:")
            #print(" ".join(f"{x:02X}" for x in datos))

            #print("\nContenido ASCII:")

            texto = "".join(
                chr(x) if 32 <= x <= 126 else ""
                for x in datos
            )

            print(texto)

lectorNFC=NFCReader()
lectorNFC.wait4card()
lectorNFC.show_UID()
#lectorNFC.load_password()
lectorNFC.authenticate_block(4)
lectorNFC.read_block(4)