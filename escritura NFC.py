from smartcard.System import readers
import time


def enviar(conexion, comando):
    datos, sw1, sw2 = conexion.transmit(comando)

    if (sw1, sw2) != (0x90, 0x00):
        raise Exception(f"Error: SW={sw1:02X} {sw2:02X}")

    return datos


# --------------------------------------------------
# Conectar al lector
# --------------------------------------------------

lector = readers()[0]

print("Lector:", lector)
print("Acercá la tarjeta...")

while True:
    conexion = lector.createConnection()

    try:
        conexion.connect()
        break
    except:
        time.sleep(0.2)

print("Tarjeta detectada")


# --------------------------------------------------
# Leer UID
# --------------------------------------------------

uid = enviar(
    conexion,
    [0xFF, 0xCA, 0x00, 0x00, 0x00]
)

print(
    "UID:",
    "".join(f"{x:02X}" for x in uid)
)


# --------------------------------------------------
# Cargar clave
# --------------------------------------------------

clave = [
    0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF
]

enviar(
    conexion,
    [
        0xFF, 0x82,
        0x00, 0x00,
        0x06,
        *clave
    ]
)


# --------------------------------------------------
# Autenticar bloque 4
# --------------------------------------------------

bloque = 4

enviar(
    conexion,
    [
        0xFF, 0x86,
        0x00, 0x00,
        0x05,
        0x01,
        0x00,
        bloque,
        0x60,   # Key A
        0x00
    ]
)

print("Bloque autenticado")


# --------------------------------------------------
# Preparar texto
# --------------------------------------------------

texto = "99-999"

datos = list(texto.encode("utf-8"))

# máximo 16 bytes
datos = datos[:16]

# completar hasta 16 bytes
datos += [0x00] * (16 - len(datos))

print("Datos a escribir:")
print(" ".join(f"{x:02X}" for x in datos))


# --------------------------------------------------
# Escribir bloque
# --------------------------------------------------

enviar(
    conexion,
    [
        0xFF, 0xD6,
        0x00,
        bloque,
        0x10,
        *datos
    ]
)

print("Escritura correcta")


# --------------------------------------------------
# Leer nuevamente
# --------------------------------------------------

datos_leidos = enviar(
    conexion,
    [
        0xFF, 0xB0,
        0x00,
        bloque,
        0x10
    ]
)


print("\nContenido leído:")

print(
    "HEX:",
    " ".join(f"{x:02X}" for x in datos_leidos)
)

texto_leido = bytes(datos_leidos).rstrip(b"\x00").decode(
    "utf-8",
    errors="replace"
)

print("Texto:", texto_leido)


input("\nEnter para cerrar...")
