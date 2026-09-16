from smartcard.System import readers
from smartcard.Exceptions import NoCardException
import time


def enviar(conexion, comando):
    datos, sw1, sw2 = conexion.transmit(comando)

    print(
        "Respuesta:",
        " ".join(f"{x:02X}" for x in datos),
        f"| SW={sw1:02X} {sw2:02X}"
    )

    return datos, sw1, sw2


# --------------------------------------------------
# Buscar lector
# --------------------------------------------------

lectores = readers()

if not lectores:
    print("No se encontró el ACR122U.")
    input("Enter para salir...")
    exit()

lector = lectores[0]

print("Lector:", lector)
print("Acercá la tarjeta...")


# --------------------------------------------------
# Esperar tarjeta
# --------------------------------------------------

while True:
    conexion = lector.createConnection()

    try:
        conexion.connect()
        break
    except:
        time.sleep(0.2)


print("\nTarjeta detectada")


# --------------------------------------------------
# Leer UID
# --------------------------------------------------

uid, sw1, sw2 = enviar(
    conexion,
    [0xFF, 0xCA, 0x00, 0x00, 0x00]
)

print(
    "UID:",
    "".join(f"{x:02X}" for x in uid)
)


# --------------------------------------------------
# Cargar clave FF FF FF FF FF FF
# --------------------------------------------------

clave = [
    0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF
]

print("\nCargando clave...")

datos, sw1, sw2 = enviar(
    conexion,
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


# --------------------------------------------------
# Autenticar bloque 4
# --------------------------------------------------

bloque = 4

print(f"\nAutenticando bloque {bloque}...")

datos, sw1, sw2 = enviar(
    conexion,
    [
        0xFF, 0x86,
        0x00, 0x00,
        0x05,
        0x01,
        0x00,
        bloque,
        0x60,       # Key A
        0x00
    ]
)

if (sw1, sw2) != (0x90, 0x00):
    print("\nNo se pudo autenticar.")
    print("Es posible que la tarjeta no use la clave por defecto.")
    exit()


print("Autenticación correcta.")


# --------------------------------------------------
# Leer bloque 4
# --------------------------------------------------

print(f"\nLeyendo bloque {bloque}...")

datos, sw1, sw2 = enviar(
    conexion,
    [
        0xFF, 0xB0,
        0x00,
        bloque,
        0x10
    ]
)

if (sw1, sw2) == (0x90, 0x00):

    print("\nContenido HEX:")
    print(" ".join(f"{x:02X}" for x in datos))

    print("\nContenido ASCII:")

    texto = "".join(
        chr(x) if 32 <= x <= 126 else "."
        for x in datos
    )

    print(texto)


input("\nEnter para cerrar...")