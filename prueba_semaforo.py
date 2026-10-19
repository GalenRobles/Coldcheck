import serial, time

PUERTO = "COM8"   # el COM del Uno clásico

with serial.Serial(PUERTO, 115200, timeout=2) as s:
    time.sleep(2)   # la placa se reinicia al abrir el puerto
    for letra in "GYR":
        s.write(letra.encode())
        print(letra, "->", s.readline().decode(errors="ignore").strip())
        time.sleep(2)