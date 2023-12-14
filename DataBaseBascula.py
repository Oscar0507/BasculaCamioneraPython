import sqlite3
from tkinter import messagebox

class BaseDeDatos:
    def __init__(self, nombre_base_datos):
        self.conn = sqlite3.connect(nombre_base_datos)
        self.cursor = self.conn.cursor()

    def obtener_placas(self):
        self.cursor.execute("SELECT placa FROM registros WHERE estado = 0") # Placas en transito
        return self.cursor.fetchall()
    
    def verificar_placa_enTransito(self, placa):
        self.cursor.execute("SELECT * FROM registros WHERE estado = 0 and placa = ?",(placa,)) # Placas en transito
        resultado= self.cursor.fetchone()
        if resultado is not None:
            return True
        else:
            return False
    
    def abrir_reg_conplacaEntransito(self,placa):
        self.cursor.execute("SELECT * FROM registros WHERE estado = 0 and placa = ?",(placa,))
        #print(self.cursor.fetchone())
        return self.cursor.fetchone()
        
    def verificar_exist_regist(self,registro):
        self.cursor.execute("SELECT * FROM registros WHERE registro = ?", (registro,))
        resultado=self.cursor.fetchone()
        print(resultado)
        if resultado is not None:
            return True
        else:
            return False
    
    def obtener_clientes(self):
        self.cursor.execute("SELECT cliente FROM clientes")
        clientes = [row[0] for row in self.cursor.fetchall()]
        return clientes
    
    def obtener_productos(self):
        self.cursor.execute("SELECT producto, FactorConv FROM productos")
        productos = self.cursor.fetchall()
        return productos
    
    def obtener_obras(self):
        self.cursor.execute("SELECT obra FROM obras")
        obras = self.cursor.fetchall()
        return obras

    def consulta_por_parametros(self,valor,param):
    
        match param:
            case 'fecha':
                self.cursor.execute("SELECT fecha_inicio,registro,placa,cliente,producto,volumen FROM registros WHERE\
                             fecha= ?",(valor,))
            case 'registro':
                self.cursor.execute("SELECT fecha_inicio,registro,placa,cliente,producto,volumen FROM registros WHERE\
                             registro= ?",(valor,))
            case 'placa':
                self.cursor.execute("SELECT fecha_inicio,registro,placa,cliente,producto,volumen FROM registros WHERE\
                             placa= ?",(valor,))
        resultados=self.cursor.fetchall()
        return resultados

    def consulta_total_por_registro(self,registro):
        self.cursor.execute("SELECT registro,fecha,fecha_inicio,fecha_fin,estado,placa,producto,factor\
                                ,cliente,humedad,pesoEntrada,pesoSalida,PesoAgua,PesoBruto,PesoNeto\
                                ,Volumen,obra,ubicacion,observacion FROM registros WHERE\
                             registro= ?",(registro,))
        resultados=self.cursor.fetchall()
        return resultados
    
    def obtener_ubicaciones(self):
        self.cursor.execute("SELECT ubicacion FROM ubicaciones")
        ubicacion = self.cursor.fetchall()
        return ubicacion

    def obtener_registro_max(self):
        self.cursor.execute("SELECT MAX(registro) FROM registros")
        registro = self.cursor.fetchone()[0]

        if registro is None:
            registro=0;   
        return registro

    def grabar_1er_registro(self, registro, fecha, fecha_inicio, estado, placa, producto, factor, cliente, humedad,\
                            pesoEntrada, pesoSalida,pesoAgua,pesoBruto,pesoNeto,volumen,obra,ubicacion,observacion):
        print(registro, fecha_inicio, estado, placa, producto, factor, cliente, humedad,pesoEntrada, pesoSalida,\
              pesoAgua,pesoBruto,pesoNeto,volumen,obra,ubicacion,observacion,sep="#")
        try:
            self.cursor.execute("INSERT INTO registros (registro,fecha,fecha_inicio,estado,placa,producto,factor\
                                ,cliente,humedad,pesoEntrada,pesoSalida,PesoAgua,PesoBruto,PesoNeto\
                                ,Volumen,obra,ubicacion,observacion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", \
                                (registro, fecha,fecha_inicio, estado, placa, producto, factor, cliente, humedad, \
                                pesoEntrada, pesoSalida,pesoAgua,pesoBruto,pesoNeto,volumen, obra, ubicacion, observacion)) 
            #"\" Para continura una instruccion
            self.conn.commit()
            messagebox.showinfo("Éxito", "Registro almacenado con éxito.")
            return True
    
        except sqlite3.Error as e:
            messagebox.showinfo("Fallo", f"Error de almacenamiento: {str(e)}")
            self.conn.rollback()
            return False
        
    def grabar_2do_registro(self, registro, estado, fecha_fin, humedad, pesoSalida, pesoBruto, pesoAgua, pesoNeto, volumen,\
                             obra, ubicacion, observacion):
        print(registro, estado, fecha_fin, humedad, pesoSalida, pesoBruto, pesoAgua, pesoNeto, volumen, obra,\
              ubicacion,observacion,sep="#")
        try:
            self.cursor.execute("UPDATE registros SET fecha_fin = ?,estado= ?,humedad = ?,pesoSalida =? ,pesoBruto = ?,pesoAgua= ?,pesoNeto =?,\
                                volumen= ?,obra= ?,ubicacion= ?,observacion= ? WHERE (registro = ?)", \
                        (fecha_fin,estado,humedad,pesoSalida,pesoBruto,pesoAgua,pesoNeto,volumen,obra,ubicacion,observacion, registro)) 
            self.conn.commit()
            messagebox.showinfo("Éxito", "Registro almacenado con éxito.")
            return True
    
        except sqlite3.Error as e:
            messagebox.showinfo("Fallo", f"Error de almacenamiento: {str(e)}")
            self.conn.rollback()
            return False
    
    def actualizar_estado(self,registro,estado):
        try:
            self.cursor.execute("UPDATE registros SET estado= ?WHERE (registro = ?)",(estado, registro)) 
            self.conn.commit()
            messagebox.showinfo("Éxito", "Registro actualizado con éxito.")
    
        except sqlite3.Error as e:
            messagebox.showinfo("Fallo", f"Error de acatualización: {str(e)}")
            self.conn.rollback()

    def insertarCliente(self,cliente):
        try:
            self.cursor.execute("INSERT INTO Clientes(cliente) VALUES (?)",(cliente,))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Registro almacenado con éxito.")
        except sqlite3.Error as e:
            messagebox.showinfo("Fallo", f"Error de almacenamiento: {str(e)}")
            self.conn.rollback()

    def insertarProducto(self,producto,factor,precio):
        try:
            self.cursor.execute("INSERT INTO Productos(producto,FactorConv,Precio_m3) VALUES (?,?,?)",(producto,factor,precio))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Registro almacenado con éxito.")
        except sqlite3.Error as e:
            messagebox.showinfo("Fallo", f"Error de almacenamiento: {str(e)}")
            self.conn.rollback()

    def insertarObra(self,obra,encargado):
        try:
            self.cursor.execute("INSERT INTO Obras(Obra,Encargado) VALUES (?,?)",(obra,encargado))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Registro almacenado con éxito.")
        except sqlite3.Error as e:
            messagebox.showinfo("Fallo", f"Error de almacenamiento: {str(e)}")
            self.conn.rollback()

    def insertarUbicacion(self,ubicacion,region):
        try:
            self.cursor.execute("INSERT INTO Ubicaciones(Ubicacion,Region) VALUES (?,?)",(ubicacion,region))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Registro almacenado con éxito.")
        except sqlite3.Error as e:
            messagebox.showinfo("Fallo", f"Error de almacenamiento: {str(e)}")
            self.conn.rollback()

    def consulta_totalRegistros(self,fecha_ini,fecha_fin):
        try:
            self.cursor.execute("SELECT * FROM Registros WHERE fecha BETWEEN ? AND ?",(fecha_ini,fecha_fin))
            resultados=self.cursor.fetchall()
            # Obtener los nombres de las columnas
            nombres_columnas = [descripcion[0] for descripcion in self.cursor.description]
            # Agregar encabezados al principio de la lista de datos
            resultados.insert(0, nombres_columnas)
        except sqlite3.Error as e:
            messagebox.showinfo("Fallo", f"Error en la consulta: {str(e)}")
        else:
            return resultados        
