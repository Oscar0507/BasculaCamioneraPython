import serial

class InterfazSerial:
    def __init__(self, Baud, Port):
        self.puerto_serial=serial.Serial(Port,Baud,timeout=1)   # Configuración de puerto serie
    
    def leer_datos(self):
        print("ENTRÓ A FUNCIÓN DE LECTURA")
        # envío de datos de prueba para recepción
        dato_a_enviar= b'456KGBZ ST,GS,+1234567KGBZ ST123'   # Convierte tu cadena a bytes si es necesario
        self.puerto_serial.write(dato_a_enviar)
        trama = self.puerto_serial.read(40)
        print("Trama leída",trama)
        # Buscar el índice del inicio de trama "ST"
        indice_st = trama.find(b'ST')
        print("indice de ST",indice_st)
        peso=0
        # Verificar si se encontró "ST" y hay al menos 12 caracteres después
        if indice_st != -1 and len(trama) > indice_st + 14:
        # Capturar los 12 caracteres siguientes después de "ST"
            datos_capturados = trama[indice_st + 2 : indice_st + 14]
            print("Datos capturados:", datos_capturados)
            tipo_pesaje=datos_capturados[1:2]
            print("tipo Pesaje",tipo_pesaje)
            signo=datos_capturados[4]
            print("Signo",signo)
            cadena_peso=datos_capturados[5:11]
            print("PESO_cadena",cadena_peso)
            cadena_peso=cadena_peso.decode('utf-8')
            peso=int(cadena_peso)
            print("Peso_int",peso)
        else:
            print("No se encontró el inicio de trama o no hay suficientes caracteres después.")
        return peso    