import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.ttk import Combobox
from tkinter import simpledialog,messagebox
from tkinter.simpledialog import askstring
import re
import json

from DataBaseBascula import BaseDeDatos
from InterfaceSerial import InterfazSerial
from serial.serialutil import SerialException
import time

import win32print
import win32ui


class Interfaz:
    def __init__(self,ventana):
        self.ventana=ventana
        self.ventana.title("Bascula Camionera")
        self.ventana.geometry("1020x800")

        self.Fuente=("Calibri", 12)
        self.inicializacion()
        self.cargar_parametros()
        self.crear_interfaz()
        self.actualizar_registro(self.registro)
        self.establecerConn_Serial()
        
    def Imprimir(self):
        impresora_def=win32print.GetDefaultPrinter()    #Obtener impresora predeterminada
        h_impresora=win32print.OpenPrinter(impresora_def)   #Crear un objeto de impresión
        impresora_info=win32print.GetPrinter(h_impresora,2)
        pdc = win32ui.CreateDC()
        pdc.CreatePrinterDC(impresora_def)
        pdc.StartDoc(f'Recibo {self.registro}')
        pdc.StartPage()

        #Configurando texto a imprimir
        # Configurar la fuente
        #fuente = win32ui.CreateFont({"name": "Calibri","height": 32,"weight": 400,})
        #pdc.SelectObject(fuente)

        pdc.TextOut(100,100,f"Registro: {self.registro}")
        pdc.TextOut(1800,100,"INGENIERIA DE VIAS")
        pdc.TextOut(3400,100,f"Numero de tiquete: {self.registro}")
        pdc.TextOut(100,250,"_______________________________________________________________________________________________")
        pdc.TextOut(100,400,f"Fecha de Entrada: {self.fecha_entrada}")
        pdc.TextOut(1800,400,f"Fecha de Salida: {self.fecha_salida}")
        pdc.TextOut(3400,400,f"Placa: {self.placa.get()}")
        
            
        pdc.TextOut(100,600,f"Cliente: {self.Cliente.get()}")
        pdc.TextOut(1800,600,f"Producto: {self.Producto.get()}")
        pdc.TextOut(3400,600,f"Humedad: {self.Humedad.get()} %" )

        pdc.TextOut(100,800,f"Obra: {self.Obra.get()}" )
        pdc.TextOut(1800,800,f"Ubicación: {self.Ubicacion.get()}" )

        pdc.TextOut(100,1000,f"Peso Entrada: {self.PesoEntrada.get()} Kg")
        pdc.TextOut(1800,1000,f"Peso Salida: {self.PesoSalida.get()} Kg")
        pdc.TextOut(3400,1000,f"Peso del Agua: {self.PesoAgua.get()} Kg")

        pdc.TextOut(100,1200,f"Peso Bruto: {self.PesoBruto.get()} Kg")
        pdc.TextOut(1800,1200,f"Peso Neto: {self.PesoNeto.get()} Kg")
        pdc.TextOut(3400,1200,f"Volumen: {self.Volumen.get()} m3")

        pdc.TextOut(100,1400,f"Observaciones: {self.Observacion.get()}")

        pdc.TextOut(280,1800,"__________________________")
        pdc.TextOut(300,1900,"Firma Operador báscula")
        pdc.TextOut(2680,1800,"_________________________")
        pdc.TextOut(2700,1900,"Nombre y firma conductor")
     
        #Finalizar el trabajo de impresión
        pdc.EndPage()
        pdc.EndDoc()

        #Cerrar la impresora
        win32print.ClosePrinter(h_impresora)

        if self.estatus<2:
            self.Base_de_datos.actualizar_estado(self.registro,2)
        valores=self.Base_de_datos.consulta_total_por_registro(self.registro)[0]
        self.cargar_datos_registro_consulta(valores)

    def inicializacion(self):

        self.fecha_hora_actual=time.strftime("%Y-%m-%d %H:%M:%S")
        self.fecha=time.strftime("%Y-%m-%d")
        self.hora=time.strftime("%H:%M:%S")


        #Verificación de Contraseña
        self.password=tk.IntVar()

        self.HabilitarIngresoManual=tk.BooleanVar()
        self.Puerto=tk.StringVar()
        self.Baudios=tk.IntVar()
        self.Protocolo=tk.StringVar()

        self.listPuertos=["COM1","COM2","COM3","COM4","COM5","COM6","COM7"]
        self.listBaudios=["2400","9600","19200","115200"]
        self.listProtocolos=["Protocolo1","Protocolo2","Protocolo3"]

        self.tablas=["Clientes","Productos","Obras","Ubicaciones"]
        self.tabla=tk.StringVar()
        self.label_parametro1=tk.StringVar()
        self.label_parametro2=tk.StringVar()
        self.label_parametro3=tk.StringVar()

        self.parametro1=tk.StringVar()
        self.parametro2=tk.StringVar()
        self.parametro3=tk.StringVar()

        self.lectura_serie=[]

        self.ParamConsulta=tk.StringVar()
        self.ValorConsulta=tk.StringVar()

        self.fecha_entrada=" "
        self.fecha_salida=" "
        self.estatus=0      #0  Nuevo registro
                            #1  Registro en transito
                            #2  Registro guardado completo
                            #3  Registro impreso
                            #4  Registro eliminado 
        #Creación de BasedeDatos
        self.Base_de_datos=BaseDeDatos("D:\Developer\Python\VirtualEnv\BaseDeDatos.db")
        #Crear una etiqueta con el número de registro con variable registro    
        #self.etiqueta_estado_reg.config(text="Estado: Ingreso")
        self.Producto=tk.StringVar()
        self.placa=tk.StringVar(value="XXX000")
        self.Cliente=tk.StringVar()
        self.Obra=tk.StringVar()
        self.Ubicacion=tk.StringVar()
        self.Observacion=tk.StringVar()
        #self.registro = tk.IntVar(value=0)
        self.registro =0
        self.Factor_Conv= tk.DoubleVar(value=0.0)
        self.Humedad=tk.DoubleVar(value=0.0)
        self.PesoEntrada=tk.IntVar(value=0)
        self.PesoSalida=tk.IntVar(value=0)
        self.PesoNeto=tk.IntVar(value=0)
        self.Volumen=tk.IntVar(value=0)
        self.PesoAgua=tk.IntVar(value=0)
        self.PesoBruto=tk.IntVar(value=0)
        
        self.Clientes=[]
        self.Productos_fact=[]
        self.Productos=[]
        self.Obras=[]
        self.Ubicaciones=[]
        self.Factores=[]
        self.Placas_pend=[]

    def cargar_parametros(self):
        try: 
            with open("parametros_bascula.json","r") as archivo:
                parametros_guardados=json.load(archivo)
                self.password.set(parametros_guardados.get("password",None))
                self.Puerto.set(parametros_guardados.get("Puerto",None))
                self.Baudios.set(int(parametros_guardados.get("Baudios",None)))
                self.Protocolo.set(parametros_guardados.get("Protocolo",None))
                self.HabilitarIngresoManual.set(parametros_guardados.get("HabilitarIngresoManual",None))
                print(self.password.get())

        except(FileNotFoundError,json.JSONDecodeError):
            self.password.set(1234)
            messagebox.showerror("Error","No se pudo abrir archivo de parámetros")

    def crear_interfaz(self):   
        #Definición de label de hora y fecha
        self.Fecha_hora = tk.Label(self.ventana, text="", font=("Calibri", 10))
        self.Fecha_hora.grid(row=0,column=1,columnspan=2,padx=1,pady=1,sticky="e")  # Anclar en la esquina superior derecha
        self.actualizar_hora()
        # Crear una etiqueta de título centrada en la parte superior
        self.titulo = tk.Label(self.ventana, text="BÁSCULA CAMIONERA - INGENIERÍA DE VÍAS", font=("Calibri", 18), background="white")
        self.titulo.grid(row=1,column=0,columnspan=2,padx=1,pady=1,sticky="nsew")
      
        # Crear un Frame de acceso a registros pendientes
        self.frame_listPlacas_pend=Frame(self.ventana,background="white",width=400,height=800)
        self.frame_listPlacas_pend.grid(row=2,column=0,padx=5,pady=5)
        self.listframePlacas=LabelFrame(self.frame_listPlacas_pend,text="En transito",font=self.Fuente,bg='white',width=200,height=500)
        self.listframePlacas.pack(fill='both',expand=True,padx=3,pady=3)
        self.listBoxPlacas=Listbox(self.listframePlacas,width=25,height=27)
        self.listBoxPlacas.pack(fill="both",expand=True)
        self.listBoxPlacas.bind("<<ListboxSelect>>", self.on_double_click_listaPlacas)
        
        # Crear un Frame contenedor de LableFrames
        self.frame_contenedor=Frame(self.ventana,background="white",width=800,height=800)
        self.frame_contenedor.grid(row=2,column=1,padx=5,pady=5)

        # Crear etiqueta de registro
        self.etiqueta_registro = tk.Label(self.frame_contenedor, text="Registro:", font=self.Fuente, background="white")
        self.etiqueta_registro.grid(row=0,column=0,padx=5,pady=5,sticky="w")
        self.etiqueta_fecha_ent_reg= tk.Label(self.frame_contenedor, text=" ", font=self.Fuente, background="white")    
        self.etiqueta_fecha_ent_reg.grid(row=0,column=1,padx=5,pady=5,sticky="w")
        self.etiqueta_estado_reg=tk.Label(self.frame_contenedor, text="Estado: Ingreso", font=self.Fuente, background="white")
        self.etiqueta_estado_reg.grid(row=1,column=0,padx=5,pady=5,sticky="w")
        self.etiqueta_fecha_sal_reg= tk.Label(self.frame_contenedor, text=" ", font=self.Fuente, background="white")    
        self.etiqueta_fecha_sal_reg.grid(row=1,column=1,padx=5,pady=5,sticky="w")

        # Crear un LabelFrame "Cliente"
        self.frame_cliente = LabelFrame(self.frame_contenedor, text="Cliente", font=self.Fuente,width=400,height=200)
        self.frame_cliente.grid(row=2,column=0,padx=5,pady=5,sticky="w")
        self.labelPlaca=Label(self.frame_cliente,text="Placa:", font=self.Fuente)
        self.EntryPlaca=Entry(self.frame_cliente,textvariable=self.placa)
        self.labelCliente=Label(self.frame_cliente,text="Cliente:", font=self.Fuente)
        self.ComboCliente=Combobox(self.frame_cliente, textvariable=self.Cliente, values=self.Clientes)
        self.labelPlaca.grid(row=0,column=0,padx=5,pady=5,sticky="w")
        self.EntryPlaca.grid(row=0,column=1,padx=5,pady=5,sticky="w")
        self.labelCliente.grid(row=1,column=0,padx=5,pady=5,sticky="w")
        self.ComboCliente.grid(row=1,column=1,padx=5,pady=5,sticky="w")

        self.labelObra=Label(self.frame_cliente,text="Obra destino:", font=self.Fuente)
        self.labelObra.grid(row=2,column=0,padx=10,pady=10,sticky="w")
        self.ComboObra=Combobox(self.frame_cliente, textvariable=self.Obra, font=self.Fuente)
        self.ComboObra.grid(row=2,column=1,padx=10,pady=10,sticky="w")

        self.labelUbicacion=Label(self.frame_cliente,text="Ubicacion obra:", font=self.Fuente)
        self.labelUbicacion.grid(row=3,column=0,padx=10,pady=10,sticky="w")
        self.ComboUbicacion=Combobox(self.frame_cliente, textvariable=self.Ubicacion, font=self.Fuente)
        self.ComboUbicacion.grid(row=3,column=1,padx=10,pady=10,sticky="w")

        # Crear LableFrame "Datos del producto"
        self.frame_producto= LabelFrame(self.frame_contenedor,text="Datos del Producto", font=self.Fuente,width=400,height=200)
        self.frame_producto.grid(row=2,column=1,padx=5,pady=5,sticky="w")
        self.label_producto=Label(self.frame_producto,text="Producto:", font=self.Fuente)
        self.label_factor_conv=Label(self.frame_producto,text="Factor de Conversión: ", font=self.Fuente)
        self.entry_factor_conv=Entry(self.frame_producto, textvariable=self.Factor_Conv,state="disabled", font=self.Fuente)
        self.label_humedad=Label(self.frame_producto,text="Humedad: ", font=self.Fuente)
        self.Entry_Humedad=Entry(self.frame_producto,textvariable=self.Humedad)

        self.ComboProducto=Combobox(self.frame_producto, textvariable=self.Producto, values=self.Productos)
        self.ComboProducto.bind("<<ComboboxSelected>>", self.actualizar_etiqueta_factorConv)

        self.label_producto.grid(row=0,column=0,padx=10,pady=10,sticky="w")
        self.ComboProducto.grid(row=0,column=1,padx=10,pady=10,sticky="w")
        self.label_humedad.grid(row=1,column=0,padx=10,pady=10,sticky="w")
        self.Entry_Humedad.grid(row=1,column=1,padx=10,pady=10,sticky="w")
        self.label_factor_conv.grid(row=2,column=0,padx=10,pady=10,sticky="w")
        self.entry_factor_conv.grid(row=2,column=1,padx=10,pady=10,sticky="w")
        

        # Crear LableFrame "Datos de Pesaje"
        self.frame_pesaje= LabelFrame(self.frame_contenedor,text="Datos de Pesaje", font=self.Fuente,width=600,height=400)
        self.frame_pesaje.grid(row=3,column=0,padx=10,pady=10,sticky="w")
        self.label_pesoEntrada=Label(self.frame_pesaje,text="Peso de Entrada:", font=self.Fuente)
        self.entry_pesoEnt=Entry(self.frame_pesaje,textvariable=self.PesoEntrada,font=self.Fuente)
        self.entry_pesoSal=Entry(self.frame_pesaje,textvariable=self.PesoSalida,font=self.Fuente)
        self.label_pesoSalida=Label(self.frame_pesaje,text="Peso de Salida:", font=self.Fuente)
        self.boton_AdquirirPeso=Button(self.frame_pesaje,text="Adquirir Peso", font=self.Fuente,activebackground="green",command=self.leer_datos_seriales)

        self.label_pesoEntrada.grid(row=0,column=0,padx=10,pady=10,sticky="w")
        self.entry_pesoEnt.grid(row=0,column=1,padx=10,pady=10,sticky="w")
        self.boton_AdquirirPeso.grid(row=0,column=2,padx=10,pady=10,sticky="w")

        self.label_pesoSalida.grid(row=1,column=0,padx=10,pady=10,sticky="w")
        self.entry_pesoSal.grid(row=1,column=1,padx=10,pady=10,sticky="w")
        self.label_observacion=Label(self.frame_pesaje,text="Observaciones: ",font=self.Fuente)
        self.label_observacion.grid(row=2,column=0,columnspan=3,sticky='w',padx=10,pady=10)
        self.text_observacion=Text(self.frame_pesaje,width=50,height=3)
        self.text_observacion.grid(row=3,column=0,columnspan=3,padx=5,pady=5)


        # Crear LableFrame "Cálculos volumétricos"
        self.frame_calculos= LabelFrame(self.frame_contenedor,text="Cálculos Volumétricos", font=self.Fuente,width=600,height=400)
        self.frame_calculos.grid(row=3,column=1,padx=10,pady=10,sticky="w")
        self.boton_calcular=Button(self.frame_calculos,text="Calcular", font=self.Fuente,activebackground="green",command=self.calcular_volumen )
        self.label_pesoNeto=Label(self.frame_calculos,text="Peso Neto: ", font=self.Fuente)
        self.entry_pesoNeto=Entry(self.frame_calculos,textvariable=self.PesoNeto,state="readonly",font=self.Fuente)
        self.label_volumen=Label(self.frame_calculos,text="Volumen: ", font=self.Fuente)
        self.entry_volumen=Entry(self.frame_calculos,textvariable=self.Volumen,state="readonly",font=self.Fuente)
        self.label_pesoAgua=Label(self.frame_calculos,text="Peso del Agua:", font=self.Fuente)
        self.entry_pesoAgua=Entry(self.frame_calculos,textvariable=self.PesoAgua,state="readonly",font=self.Fuente)
        self.label_pesoBruto=Label(self.frame_calculos,text="Peso Bruto:", font=self.Fuente)
        self.entry_pesoBruto=Entry(self.frame_calculos,textvariable=self.PesoBruto,state="readonly",font=self.Fuente)

        self.label_pesoNeto.grid(row=0,column=0,padx=10,pady=10,sticky="w")
        self.entry_pesoNeto.grid(row=0,column=1,padx=10,pady=10,sticky="w")

        self.label_volumen.grid(row=1,column=0,padx=10,pady=10,sticky="w")
        self.entry_volumen.grid(row=1,column=1,padx=10,pady=10,sticky="w")

        self.label_pesoAgua.grid(row=2,column=0,padx=10,pady=10,sticky="w")
        self.entry_pesoAgua.grid(row=2,column=1,padx=10,pady=10,sticky="w")

        self.label_pesoBruto.grid(row=3,column=0,padx=10,pady=10,sticky="w")
        self.entry_pesoBruto.grid(row=3,column=1,padx=10,pady=10,sticky="w")

        self.boton_calcular.grid(row=4,column=0,columnspan=2,padx=10,pady=10,sticky="n")

        # Cuadro de botones
        self.frame_botones=LabelFrame(self.ventana,text="Botones de registro",font=self.Fuente,width=800,height=100)
        self.frame_botones.grid(row=3,column=0,columnspan=2,padx=10,pady=10)
        self.boton_grabar=Button(self.frame_botones,text="Grabar", font=self.Fuente,activebackground="green",command=self.grabar_dato)
        self.boton_eliminar=Button(self.frame_botones,text="Eliminar", font=self.Fuente,activebackground="green", command=self.eliminar_registro)
        self.boton_imprimir=Button(self.frame_botones,text="Imprimir", font=self.Fuente,activebackground="green",command=self.Imprimir)
        self.boton_imprimir.config(state="disabled")
        self.boton_cargar=Button(self.frame_botones,text="Cargar", font=self.Fuente,activebackground="green",command=self.cargar_registro)
        self.boton_nuevo=Button(self.frame_botones,text="Nuevo", font=self.Fuente,activebackground="green",command=self.reset_planilla)
        self.boton_config=Button(self.frame_botones,text="Configuración", font=self.Fuente,activebackground="green", command=self.configuraciones)
        self.boton_salir=Button(self.frame_botones,text="Salir", font=self.Fuente,activebackground="green", command=self.salir)

        self.boton_grabar.grid(row=0,column=0,padx=10,pady=10,sticky="w")
        self.boton_eliminar.grid(row=0,column=1,padx=10,pady=10,sticky="w")
        self.boton_imprimir.grid(row=0,column=2,padx=10,pady=10,sticky="w")
        self.boton_cargar.grid(row=0,column=3,padx=10,pady=10,sticky="w")
        self.boton_nuevo.grid(row=0,column=4,padx=10,pady=10,sticky="w")
        self.boton_config.grid(row=0,column=5,padx=10,pady=10,sticky="w")
        self.boton_salir.grid(row=0,column=6,padx=10,pady=10,sticky="w")
    
    #   Eventos
    def on_double_click_listaPlacas(self,event):        # Al dar doble click sobre una placa del listbox
        placa_select_ind=self.listBoxPlacas.curselection()
        if placa_select_ind:
            placa_select=self.listBoxPlacas.get(placa_select_ind)
            datos_registro=[]
            datos_registro=self.Base_de_datos.abrir_reg_conplacaEntransito(placa_select)
            print(datos_registro)
            self.borar_datos_calculo()
            self.cargar_datos_registro(datos_registro)

    def on_click_tabla(self,event):                     # Al dar click en un ítem de la tabla
        item= self.tablaConsulta.selection()[0]
        registro=self.tablaConsulta.item(item,'values')[1]
        valores=self.Base_de_datos.consulta_total_por_registro(registro)[0]
        self.cargar_datos_registro_consulta(valores)

    # Eventos de botones:
    def establecerConn_Serial(self):
        ventana_activa=self.ventana.focus_get()
        #self.ventana_activa.grab_set()
        try:
            self.IntSerial=InterfazSerial(self.Baudios.get(),self.Puerto.get())      # Interfaz Serial
        except SerialException as e:
            messagebox.showerror("Error", "No se logró abrir el puerto serial.")
        else:
            messagebox.showinfo("Info","Conexión Establecida")
        #self.ventana_activa.grab_release()   #Libera el foco

    def calcular_volumen(self):                         # Botón Calcular
        if self.Base_de_datos.verificar_exist_regist(self.registro):
            try:
                self.Humedad.set(round(float(self.Entry_Humedad.get()),2))
            except ValueError:
                messagebox.showerror("Error","Se debe ingresar un valor valido tipo decimal en humedad")

            self.PesoSalida.set(self.entry_pesoSal.get())
            print("PesoSalida:",self.PesoSalida.get())
            self.PesoBruto.set(self.PesoSalida.get()-self.PesoEntrada.get())
            print("PesoBruto:",self.PesoBruto.get())
            self.PesoAgua.set(round(self.PesoBruto.get()*self.Humedad.get()/100,2))
            print("PesoAgua:",self.PesoAgua.get())
            self.PesoNeto.set(self.PesoBruto.get()-self.PesoAgua.get())
            print("PesoNeto:",self.PesoNeto.get())
            self.Volumen.set(round(self.PesoNeto.get()/self.Factor_Conv.get(),2))
            print("Volumen:",self.Volumen.get())   

    def grabar_dato(self):                              # Botón Grabar
    
        if self.Base_de_datos.verificar_exist_regist(self.registro):
            self.segunda_grab_regist()
        else:
            self.primera_grab_regist()

    def reset_planilla(self):                           # Botón Nuevo
        self.registro=self.Base_de_datos.obtener_registro_max()+1
        self.actualizar_registro(self.registro)
        self.placa.set("XXX000")
        self.etiqueta_fecha_ent_reg.config(text="")
        self.etiqueta_fecha_sal_reg.config(text="")
        self.etiqueta_estado_reg.config(text="Estado: Ingreso")

        self.Cliente.set("")
        self.Obra.set("")
        self.Ubicacion.set("")
        self.Producto.set("")
        self.Humedad.set(0.0)
        self.Factor_Conv.set("")
        self.PesoEntrada.set(0)
        self.PesoSalida.set(0)
        self.PesoNeto.set(0)
        self.Volumen.set(0.0)
        self.PesoAgua.set(0)
        self.PesoBruto.set(0)
        self.text_observacion.delete('1.0','end')

    def salir(self):                                    # Botón Salir
        self.ventana.destroy()

    def cargar_registro(self):                          # Botón Cargar
        self.abrir_ventana_consultas()

    def leer_datos_seriales(self):                      # Botón Adquirir peso
        print("Entró a función de lectura")
        self.lectura_serie=self.IntSerial.leer_datos()
        print(self.lectura_serie)
        print(self.estatus)
        print("Registro actual",self.registro)
        if  self.Base_de_datos.verificar_exist_regist(self.registro)==FALSE:
            self.PesoEntrada.set(self.lectura_serie)
        else:
            if self.estatus==0:
                self.PesoSalida.set(self.lectura_serie)

    def configuraciones(self):                          # Botón configuraciones
        self.solicitar_contraseña()

    def eliminar_registro(self):                        # Botón Eliminar
                                
        match self.estatus:
            case 0: # 3 Eliminado en transito
                self.Base_de_datos.actualizar_estado(self.registro,3)   
                self.eliminar_placa_list(self.placa.get())
                self.estatus=3
                self.actualizar_registro(self.registro)
            case 1: # 4 Eliminado procesado
                self.Base_de_datos.actualizar_estado(self.registro,4)   
                self.eliminar_placa_list(self.placa.get())
                self.estatus=4
                self.actualizar_registro(self.registro)
            case 2: # 5 Eliminado procesado e impreso
                self.Base_de_datos.actualizar_estado(self.registro,5)   
                self.eliminar_placa_list(self.placa.get())
                self.estatus=5
                self.actualizar_registro(self.registro)
            case _:
                messagebox().showerror("Error", "El registro ya está eliminado o no se ha guardado por primera vez.")

    def borar_datos_calculo(self):
        self.PesoNeto.set(0)
        self.PesoAgua.set(0)
        self.PesoBruto.set(0)
        self.Volumen.set(0)
    
    def cargar_datos_registro_consulta(self,datos):
        reg=datos[0]
        fecha=datos[1]
        fecha_inicio=datos[2]
        fecha_salida=datos[3]
        estatus=datos[4]
        placa=datos[5]
        product=datos[6]
        fact_conv=datos[7]
        client=datos[8]
        humed=datos[9]
        pesoEnt=datos[10]
        pesoSal=datos[11]
        pesoAgua=datos[12]
        pesoBruto=datos[13]
        pesoNeto=datos[14]
        volum=datos[15]
        obra=datos[16]
        ubica=datos[17]
        observ=datos[18]
             
        self.etiqueta_fecha_ent_reg.config(text=f"Fecha_entrada_vehículo: {fecha_inicio}")
        self.etiqueta_fecha_sal_reg.config(text=f"Fecha_salida_vehículo: {fecha_salida}")
        
        self.fecha=fecha
        self.fecha_entrada=fecha_inicio
        self.fecha_salida=fecha_salida
        self.estatus=estatus
        
        self.placa.set(placa)
        self.Producto.set(product)
        self.Factor_Conv.set(fact_conv)
        self.Cliente.set(client)
        self.Humedad.set(humed)
        self.PesoEntrada.set(pesoEnt)
        self.Obra.set(obra)
        self.Ubicacion.set(ubica)
        #------------------------
        self.PesoSalida.set(pesoSal)
        self.PesoAgua.set(pesoAgua)
        self.PesoBruto.set(pesoBruto)
        self.PesoNeto.set(pesoNeto)
        self.Volumen.set(volum)
        self.Observacion.set(observ)
        self.text_observacion.delete('1.0','end')
        self.text_observacion.insert('1.0',observ)
        self.actualizar_registro(reg)
              
    def cargar_datos_registro(self,datos):
        reg=datos[0]
        fecha=datos[1]
        fecha_inicio=datos[2]
        fecha_salida=datos[3]
        estatus=datos[4]
        placa=datos[5]
        product=datos[6]
        fact_conv=datos[7]
        client=datos[8]
        humed=datos[9]
        pesoEnt=datos[10]
        pesoSal=datos[11]
        pesoAgua=datos[12]
        pesoBruto=datos[13]
        pesoNeto=datos[14]
        volum=datos[15]
        obra=datos[16]
        ubica=datos[17]
        observ=datos[18]
             
        self.etiqueta_fecha_ent_reg.config(text=f"Fecha_entrada_vehículo: {fecha_inicio}")
        self.etiqueta_fecha_sal_reg.config(text="")
        
        self.fecha=fecha
        self.fecha_entrada=fecha_inicio
        self.fecha_salida=fecha_salida
        self.estatus=estatus
        self.placa.set(placa)
        self.Producto.set(product)
        self.Factor_Conv.set(fact_conv)
        self.Cliente.set(client)
        self.Humedad.set(humed)
        self.PesoEntrada.set(pesoEnt)
        if not obra:
            self.ComboObra.set("")
        else:
            self.Obra.set(obra)

        if not ubica:
            self.ComboUbicacion.set("")
        else:
            self.Ubicacion.set(ubica)
        #------------------------
        self.PesoSalida.set(pesoSal)
        self.PesoAgua.set(pesoAgua)
        self.PesoBruto.set(pesoBruto)
        self.PesoNeto.set(pesoNeto)
        self.Volumen.set(volum)

        self.text_observacion.delete('1.0','end')
        if not observ:
            self.text_observacion.insert('1.0'," ")
        else:
            self.text_observacion.insert('1.0',observ)
        self.actualizar_registro(reg)  

    def abrir_ventana_consultas(self):
        consultasVentana=tk.Toplevel()
        consultasVentana.title("Consultas")
        self.configurarVentanaConsultas(consultasVentana)
        
    def configurarVentanaConsultas(self,ventana):
        labelTitulo=Label(ventana,text="Consultas",font=self.Fuente)
        labelTitulo.grid(row=0,column=0,columnspan=3,sticky="n")
        labelParametroSelect=Label(ventana,text="Seleccion de parametro de busqueda:")
        labelParametroSelect.grid(row=1,column=0,sticky="n")
        ComboSelectParam=Combobox(ventana,values=['fecha','registro','placa'],textvariable=self.ParamConsulta)
        ComboSelectParam.grid(row=1,column=1,sticky="n")
        labelValorConsulta=Label(ventana,text="Ingrese el valor de busqueda:")
        labelValorConsulta.grid(row=1,column=2,padx=10,pady=10,sticky="n")       
        entryParamSelec=Entry(ventana,textvariable=self.ValorConsulta,state="normal")
        entryParamSelec.grid(row=1,column=3,padx=10,pady=10,sticky="n")
        ButtonConsultar=Button(ventana,text="Consultar",command=self.consultar)
        ButtonConsultar.grid(row=2,column=0,padx=10,pady=10,sticky="n")
        self.tablaConsulta=ttk.Treeview(ventana,columns=('Fecha','Registro','Placa','Cliente','Producto','Volum'))
        self.tablaConsulta['show']='headings'
        self.tablaConsulta.heading("#1",text="Fecha")
        self.tablaConsulta.heading("#2",text="Registro")
        self.tablaConsulta.heading("#3",text="Placa")
        self.tablaConsulta.heading("#4",text="Cliente")
        self.tablaConsulta.heading("#5",text="Producto")
        self.tablaConsulta.heading("#6",text="Volumen")
        self.tablaConsulta.grid(row=3,column=0,columnspan=5,padx=10,pady=10)
        self.tablaConsulta.bind('<ButtonRelease-1>',self.on_click_tabla)

    def solicitar_contraseña(self):
        contraseña_ingresada=simpledialog.askinteger("Contraseña","Ingrese la contraseña:" )
        if contraseña_ingresada==self.password.get():
            self.abrir_ventana_configuraciones()
        else:
            messagebox.showerror("Error","Contraseña incorrecta")
    
    def abrir_ventana_configuraciones(self):
        configuracionVentana=tk.Toplevel()
        configuracionVentana.title("Configuraciones")
        self.configurarVentanaConfiguraciones(configuracionVentana)

    def configurarVentanaConfiguraciones(self,ventana):
        # Row=0 Column 0:
        LableTituloConfig=Label(ventana,text="Configuraciones",font=self.Fuente)
        LableTituloConfig.grid(row=0,column=0,columnspan=2,sticky="n")
        # Row=1 Column 0:
        CheckIngresoManual=Checkbutton(ventana,text="Permitir ingreso de pesos manuales",variable=self.HabilitarIngresoManual)
        CheckIngresoManual.grid(row=1,column=0,sticky="w",padx=10,pady=10)
        # Row=2 Column 0:
        # Frame de configuracion de comunicaciones 
        LableFrameComm=LabelFrame(ventana,text="Config Comunicaciones",padx=10,pady=10) #Frame
        LableFrameComm.grid(row=2,column=0)
        LableNomPuerto=Label(LableFrameComm,text="Puerto serial:") #(row,column) (0,0)
        LableNomPuerto.grid(row=0,column=0)
        ComboPuerto=Combobox(LableFrameComm,textvariable=self.Puerto,values=self.listPuertos)         #(row,column) (0,1)
        ComboPuerto.grid(row=0,column=1)

        LableBaudios=Label(LableFrameComm,text="Baudios:")         #(row,column) (1,0)
        LableBaudios.grid(row=1,column=0)
        ComboBaud=Combobox(LableFrameComm,values=self.listBaudios,textvariable=self.Baudios)           #(row,column) (1,1)
        ComboBaud.grid(row=1,column=1)
        
        LableProtocol=Label(LableFrameComm,text="Protocolo:")         #(row,column) (2,0)
        LableProtocol.grid(row=2,column=0)
        ComboProtocol=Combobox(LableFrameComm,values=self.listProtocolos,textvariable=self.Protocolo) #(row,column) (2,1)
        ComboProtocol.grid(row=2,column=1)
        ButtonTestComm=Button(LableFrameComm,text="Test Comm",activebackground="green",command=self.establecerConn_Serial)
        ButtonTestComm.grid(row=3,column=0,columnspan=2)

        # Row=2, Column 1:
        # Frame de ingresos nuevos a tablas 
        LableFrameIngresos=LabelFrame(ventana,text="Ingresos de tablas",padx=10,pady=10) #Frame
        LableFrameIngresos.grid(row=2,column=1,padx=10,pady=10)

        LableSelectTablaIngresos=Label(LableFrameIngresos,text="Seleccionar Tabla:") #(row,column) (0,0)
        LableSelectTablaIngresos.grid(row=0,column=0,padx=10, pady=2)
        ComboSelectTabla=Combobox(LableFrameIngresos,values=self.tablas,textvariable=self.tabla) #(row,column) (0,1)
        ComboSelectTabla.grid(row=0,column=1,padx=10, pady=2)

        ButtonInsertarDato=Button(LableFrameIngresos,text="Ingresar",activebackground="green",command=self.IngresarDataTablas) #(row,column) (1,1)
        ButtonInsertarDato.grid(row=1,column=0,columnspan=2,padx=10, pady=2)

        self.EntryLabelIngresoParam1=Entry(LableFrameIngresos,textvariable=self.label_parametro1,state="disabled",relief="flat") #(row,column) (1,0)
        self.EntryLabelIngresoParam1.grid(row=2,column=0,padx=10, pady=2)
        self.EntryParam1=Entry(LableFrameIngresos,textvariable=self.parametro1)
        self.EntryParam1.grid(row=2,column=1,padx=10,pady=10)
        self.EntryLabelIngresoParam1.grid_forget()
        self.EntryParam1.grid_forget()

        self.EntryLableIngresoParam2=Entry(LableFrameIngresos,textvariable=self.label_parametro2,state="disabled",relief="flat")
        self.EntryLableIngresoParam2.grid(row=3,column=0,padx=10, pady=2)
        self.EntryParam2=Entry(LableFrameIngresos,textvariable=self.parametro2)
        self.EntryParam2.grid(row=3,column=1,padx=10,pady=10)
        self.EntryLableIngresoParam2.grid_forget()
        self.EntryParam2.grid_forget()

        self.EntryLableIngresoParam3=Entry(LableFrameIngresos,textvariable=self.label_parametro3,state="disabled",relief="flat")
        self.EntryLableIngresoParam3.grid(row=4,column=0,padx=10, pady=2)
        self.EntryParam3=Entry(LableFrameIngresos,textvariable=self.parametro3)
        self.EntryParam3.grid(row=4,column=1,padx=10,pady=10)
        self.EntryLableIngresoParam3.grid_forget()
        self.EntryParam3.grid_forget()

        self.ButtonAceptarIngreso=Button(LableFrameIngresos,text="Aceptar Ingreso",activebackground="green",command=self.EscribirDatosEnBaseDeDatos)
        self.ButtonAceptarIngreso.grid(row=5,column=0,columnspan=2)
        self.ButtonAceptarIngreso.grid_forget()

        # Row 3, Column 0:
        # Frame de ingresos nuevos a tablas 
        LableFramePassword=LabelFrame(ventana,text="Cambio de contraseña",padx=10,pady=10) #Frame
        LableFramePassword.grid(row=3,column=0,padx=10,pady=10)

        EntryCambioPassword=Entry(LableFramePassword,textvariable=self.password) #(row,column) (0,1)
        EntryCambioPassword.grid(row=0,column=0,padx=10, pady=2)
        LabelAdvertenciaPassword=Label(LableFramePassword,text="El password debe ser un numero entero",padx=2,pady=2)
        LabelAdvertenciaPassword.grid(row=1,column=0)

        # Row 3, Column 1:
        # Frame de ingresos nuevos a tablas 
        LableFrameObtenerConsulta=LabelFrame(ventana,text="Obtener consulta Registros (*.csv)",padx=10,pady=10) #Frame
        LableFrameObtenerConsulta.grid(row=3,column=1,padx=10,pady=10)

        ButtonObtenerConsulta=Button(LableFrameObtenerConsulta,text="Obtener",activebackground="green") #(row,column) (0,1)
        ButtonObtenerConsulta.grid(row=0,column=0,padx=10, pady=2)

        #Row 4, Column 0: Botón de acepatr modificaciones
        ButtonAceptarCambios=Button(ventana,text="Aceptar cambios de parámetros",padx=2,pady=2,activebackground="green",command=self.grabar_parametros)
        ButtonAceptarCambios.grid(row=4,columnspan=2)

    def IngresarDataTablas(self):
        if self.tabla.get() is not None:
            tabla_select=self.tabla.get()
            match tabla_select:
                case "Clientes":
                    self.EntryLabelIngresoParam1.grid(row=2,column=0,padx=10, pady=2)
                    self.label_parametro1.set("Nombre del Cliente:")
                    self.EntryParam1.grid(row=2,column=1,padx=10,pady=10)

                    self.ButtonAceptarIngreso.grid(row=5,column=0,columnspan=2)

                    self.EntryLableIngresoParam2.grid_forget()
                    self.EntryParam2.grid_forget()
                    self.EntryLableIngresoParam3.grid_forget()
                    self.EntryParam3.grid_forget()
                    
                case "Productos":
                    self.EntryLabelIngresoParam1.grid(row=2,column=0,padx=10, pady=2)
                    self.label_parametro1.set("Nombre del Producto:")
                    self.EntryParam1.grid(row=2,column=1,padx=10,pady=10)

                    self.EntryLableIngresoParam2.grid(row=3,column=0,padx=10, pady=2)
                    self.label_parametro2.set("Factor de Conversión:")
                    self.EntryParam2.grid(row=3,column=1,padx=10,pady=10)

                    self.EntryLableIngresoParam3.grid(row=4,column=0,padx=10, pady=2)
                    self.label_parametro3.set("Precio por m3:")
                    self.EntryParam3.grid(row=4,column=1,padx=10,pady=10)

                    self.ButtonAceptarIngreso.grid(row=5,column=0,columnspan=2)


                case "Obras":
                    self.EntryLabelIngresoParam1.grid(row=2,column=0,padx=10, pady=2)
                    self.label_parametro1.set("Nombre de Obra:")
                    self.EntryParam1.grid(row=2,column=1,padx=10,pady=10)

                    self.EntryLableIngresoParam2.grid(row=3,column=0,padx=10, pady=2)
                    self.label_parametro2.set("Encargado de Obra:")
                    self.EntryParam2.grid(row=3,column=1,padx=10,pady=10)

                    self.ButtonAceptarIngreso.grid(row=5,column=0,columnspan=2)

                    self.EntryLableIngresoParam3.grid_forget()
                    self.EntryParam3.grid_forget()


                case "Ubicaciones":
                    self.EntryLabelIngresoParam1.grid(row=2,column=0,padx=10, pady=2)
                    self.label_parametro1.set("Nombre de Ubicación:")
                    self.EntryParam1.grid(row=2,column=1,padx=10,pady=10)

                    self.EntryLableIngresoParam2.grid(row=3,column=0,padx=10, pady=2)
                    self.label_parametro2.set("Región de ubicación:")
                    self.EntryParam2.grid(row=3,column=1,padx=10,pady=10)

                    self.ButtonAceptarIngreso.grid(row=5,column=0,columnspan=2)

                    self.EntryLableIngresoParam3.grid_forget()
                    self.EntryParam3.grid_forget()

    def EscribirDatosEnBaseDeDatos(self):
        tabla=self.tabla.get()
        match tabla:
            case "Clientes":
                cliente=self.parametro1.get()
                if cliente is not None:
                    self.Base_de_datos.insertarCliente(cliente)
                else:
                    messagebox.showerror("Error","Debe insertar un cliente")
            case "Productos":
                producto=self.parametro1.get()
                factor=self.parametro2.get()
                precio=self.parametro3.get()
                if producto is None:
                    messagebox.showerror("Error","Debe insertar un cliente")
                else:
                    if self.No_es_float(factor):
                        messagebox.showerror("Error","El Factor de conversión, no es un flotante")
                    else:
                        if self.No_es_float(precio):
                            messagebox.showerror("Error","El Precio, no es un flotante")
                        else:
                            self.Base_de_datos.insertarProducto(producto,factor,precio)
                    
            case "Obras":
                obra=self.parametro1.get()
                encargado=self.parametro2.get()
                if obra is None:
                    messagebox.showerror("Error","Debe insertar una obra")
                else:
                    if encargado is None:
                        messagebox.showerror("Error","Debe insertar un encargado")
                    else:
                        self.Base_de_datos.insertarObra(obra,encargado)

            case "Ubicaciones":
                ubicacion=self.parametro1.get()
                region=self.parametro2.get()
                if ubicacion is None:
                    messagebox.showerror("Error","Debe insertar una ubicación")
                else:
                    if region is None:
                        messagebox.showerror("Error","Debe insertar una región")
                    else:
                        self.Base_de_datos.insertarUbicacion(ubicacion,region) 

    def grabar_parametros(self):
        try:
            datos_a_guardar={"Puerto":self.Puerto.get(),"Baudios":self.Baudios.get(),\
                    "Protocolo":self.Protocolo.get(),"HabilitarIngresoManual":self.HabilitarIngresoManual.get(),\
                    "password":self.password.get() }
            with open("parametros_bascula.json","w") as archivo:
                json.dump(datos_a_guardar,archivo)
            messagebox.showinfo("Aviso","Parámetros Cambiados con Éxito")
            self.actualizar_registro(self.registro)
            ventana_activa=self.ventana.focus_get()
            if isinstance(ventana_activa,tk.Toplevel):
                ventana_activa.destroy()         
        except:
            messagebox.showerror("Error","Valor de password incorrecto\n Debe ser un numero entero")
   
    def consultar(self):
            
        match self.ParamConsulta.get():
            case 'fecha':
                print("fecha",self.ValorConsulta.get())
                valores=self.Base_de_datos.consulta_por_parametros(self.ValorConsulta.get(),'fecha')
            case 'registro':
                print("registro",self.ValorConsulta.get())
                valores=self.Base_de_datos.consulta_por_parametros(self.ValorConsulta.get(),'registro')
            case 'placa':
                print("placa",self.ValorConsulta.get())
                valores=self.Base_de_datos.consulta_por_parametros(self.ValorConsulta.get(),'placa')
            case _:
                print("Opción no valida")

        if not valores:
            messagebox.showinfo("Advertencia","No arrojo datos la consulta")
            for row in self.tablaConsulta.get_children():
                self.tablaConsulta.delete(row)
        else:
            for row in self.tablaConsulta.get_children():
                self.tablaConsulta.delete(row)
            for valor in valores:
                self.tablaConsulta.insert("","end",values=valor)

    def carga_formulario_nuevo(self):

        if self.HabilitarIngresoManual.get():
            self.entry_pesoEnt.configure(state="normal")
        else:
            self.entry_pesoEnt.configure(state="readonly")

        self.EntryPlaca.configure(state="normal")
        self.Entry_Humedad.configure(state="normal")
         
        self.entry_pesoSal.configure(state="readonly")  #Deshabilitando el Entry de Peso de Salida
        self.ComboObra.configure(state="normal")
        self.ComboUbicacion.configure(state="normal")

        self.ComboCliente.configure(state="readonly")
        self.ComboProducto.configure(state="readonly")
        self.boton_AdquirirPeso.configure(state="normal")
        self.boton_calcular.configure(state="normal")
        self.text_observacion.configure(state="normal")
        self.boton_imprimir.config(state="disabled")
        self.boton_grabar.config(state="normal")       

    def carga_formulario_EnTransito(self):
        if self.HabilitarIngresoManual.get():
            self.entry_pesoSal.configure(state="normal")
        else:
            self.entry_pesoSal.configure(state="readonly")

        self.EntryPlaca.configure(state="readonly")
        self.Entry_Humedad.configure(state="normal")
        self.entry_pesoEnt.configure(state="readonly")  #Deshabilitando el Entry de Peso de Entrada

        self.ComboObra.configure(state="normal")
        self.ComboUbicacion.configure(state="normal")

        self.ComboCliente.configure(state="disabled")
        self.ComboProducto.configure(state="normal")
        self.boton_AdquirirPeso.configure(state="normal")
        self.boton_calcular.configure(state="normal")
        self.text_observacion.configure(state="normal")
        self.boton_imprimir.config(state="disabled")
        self.boton_grabar.config(state="normal")
        
    def carga_formulario_procesado(self):
        self.EntryPlaca.configure(state="readonly")
        self.Entry_Humedad.configure(state="readonly")
        self.entry_pesoEnt.configure(state="readonly")  #Deshabilitando el Entry de Peso de Entrada
        self.entry_pesoSal.configure(state="readonly")
        self.ComboObra.configure(state="disabled")
        self.ComboUbicacion.configure(state="disabled")

        self.ComboCliente.configure(state="disabled")
        self.ComboProducto.configure(state="disabled")
        self.boton_AdquirirPeso.configure(state="disabled")
        self.boton_calcular.configure(state="disabled")
        self.text_observacion.configure(state="disabled")
        self.boton_imprimir.config(state="normal")
        self.boton_grabar.config(state="disabled")

    def primera_grab_regist(self):
        self.Cliente.set(self.ComboCliente.get())
        self.Producto.set(self.ComboProducto.get())
        self.Obra.set(self.ComboObra.get())
        self.Ubicacion.set(self.ComboUbicacion.get())
        self.Observacion.set(self.text_observacion.get("1.0","end-1c"))
        # Validaciones de datos
        if not self.Entry_Humedad.get():
            self.Entry_Humedad.set(0.0)
            self.Humedad.set(self.Entry_Humedad.get())
        else:
            try:
                self.Humedad.set(float(self.Entry_Humedad.get()))
            except ValueError:
                messagebox.showerror("Error","Valor incorrecto en humedad")
                return

        if self.validar_formato():
            self.placa.set(self.EntryPlaca.get())
        else:
            messagebox.showerror("Error", "Debes ingresar un placa válida.")
            return
        
        if self.Base_de_datos.verificar_placa_enTransito(self.placa.get()):
            messagebox.showerror("Error","Esta placa ya se encuentra en transito,\
                                  verificar placa entrante")
            return
        
        if not self.Cliente.get():
            messagebox.showerror("Error", "Debes seleccionar un cliente.")
            return
        
        if not self.Producto.get():
            messagebox.showerror("Error", "Debes seleccionar un producto.")
            return
        
        self.PesoEntrada.set(self.entry_pesoEnt.get())
        if self.PesoEntrada.get()<=0:
            messagebox.showerror("Error", "Peso de entrada incorrecto")
            return

        self.PesoSalida.set(self.entry_pesoSal.get())
        if self.PesoSalida.get()>0:
            messagebox.showerror("Error", "Peso de salida debe ser 0")
            return
        else:
            estado=0    # 0 Estado de registro en transito 
            if self.Base_de_datos.grabar_1er_registro(self.registro,self.fecha,self.fecha_hora_actual,estado,self.placa.get()\
                                    ,self.Producto.get(),self.Factor_Conv.get(),\
                                    self.Cliente.get(),self.Humedad.get(),\
                                    self.PesoEntrada.get(),self.PesoSalida.get(),\
                                    self.PesoAgua.get(),self.PesoBruto.get(),self.PesoNeto.get(),\
                                    self.Volumen.get(),self.Obra.get(),self.Ubicacion.get(),self.Observacion.get()):
                self.registro=self.Base_de_datos.obtener_registro_max()+1
                self.actualizar_registro(self.registro)
                self.Placas_pend=self.Base_de_datos.obtener_placas()
                self.actualizar_lista_placas()

    def segunda_grab_regist(self):
        if self.Volumen.get()<=0:
            messagebox.showerror("Error","Falta calcular los pesos")
        else:
            self.fecha_salida=self.fecha_hora_actual
            print(self.fecha_salida)
            self.Obra.set(self.ComboObra.get())
            self.Ubicacion.set(self.ComboUbicacion.get())
            self.Observacion.set(self.text_observacion.get("1.0","end-1c"))
            estado=1
            if self.Base_de_datos.grabar_2do_registro(self.registro,estado,self.fecha_salida,self.Humedad.get(),self.PesoSalida.get(),\
                    self.PesoBruto.get(),self.PesoAgua.get(),self.PesoNeto.get(),self.Volumen.get(),self.Obra.get(),\
                    self.Ubicacion.get(),self.Observacion.get()):
                self.eliminar_placa_list(self.placa.get())
                self.estatus=estado
                self.actualizar_registro(self.registro)
                #self.reset_planilla()
                
    def eliminar_placa_list(self,placa):
        # Recorre los elementos del Listbox para encontrar el índice
        for i in range(self.listBoxPlacas.size()):
            elemento = self.listBoxPlacas.get(i)
            if elemento == placa:
                self.listBoxPlacas.delete(i)
                break  # Termina el bucle después de eliminar el primer valor coincidente

    def actualizar_cliente_list(self,lista_clientes):
        self.ComboCliente["values"] = lista_clientes
        self.Clientes=lista_clientes

    def actualizar_cliente(self,cliente):
        self.Cliente.set(cliente)
        self.ComboCliente.set(cliente)
    
    def actualizar_producto(self,lista_productos_fact):
        self.Productos_fact=lista_productos_fact
        self.Productos=[producto for producto,_ in lista_productos_fact]
        self.Factores=[factor for _,factor in lista_productos_fact]
        self.ComboProducto["values"] = self.Productos

    def actualizar_obras(self,lista_obras):
        self.Obras=lista_obras
        self.ComboObra["values"] = self.Obras

    def actualizar_ubicaciones(self,lista_ubic):
        self.Ubicaciones=lista_ubic
        self.ComboUbicacion["values"] = self.Ubicaciones
    
    def actualizar_etiqueta_factorConv(self,event):
        seleccion_producto=self.ComboProducto.get()
        self.Producto.set(seleccion_producto)
        
        if seleccion_producto:
            print(seleccion_producto)
            print(self.Productos_fact)
            self.ComboProducto.set(seleccion_producto)
            FactorConv=None
            for product,fact in self.Productos_fact:
                if product==seleccion_producto:
                    FactorConv=fact
                    break
            if FactorConv is not None:
                self.Factor_Conv.set(FactorConv)
            else:
               self.Factor_Conv.set("Sin selección")
  
    def actualizar_registro(self,registro):

        # Elección de carga de un formulario nuevo, existente o procesado
        if self.Base_de_datos.verificar_exist_regist(registro):
            if self.estatus == 0:       #En Transito
                self.carga_formulario_EnTransito()
                self.etiqueta_estado_reg.config(text="Estado: Registro en transito")
                print('registro en transito',registro)
                print('estado',self.estatus)

            if self.estatus >= 1:
                self.carga_formulario_procesado()
                match self.estatus:
                    case 1:     #Grabado
                        self.etiqueta_estado_reg.config(text="Estado: Procesado")
                    case 2:     #Grabado e impreso
                        self.etiqueta_estado_reg.config(text="Estado: Procesado e impreso")
                    case 3:     #Eliminado en transito
                        self.etiqueta_estado_reg.config(text="Estado: Eliminado en transito")
                    case 4:     #Eliminado grabado
                        self.etiqueta_estado_reg.config(text="Estado: Eliminado procesado")
                    case 5:     #Eliminado procesado e impreso
                        self.etiqueta_estado_reg.config(text="Estado: Eliminado procesado e impreso")

                print('registro procesado',registro)
                print('estado',self.estatus)
        else:
            self.carga_formulario_nuevo()

        self.registro=registro
        self.etiqueta_registro.config(text=f"Registro: {self.registro}") 
    
    def actualizar_lista_placas(self):        
        self.listBoxPlacas.delete(0, tk.END)    # Limpia el Listbox antes de agregar nuevos elementos
        for placa in self.Placas_pend:
            self.listBoxPlacas.insert(tk.END, placa[0])

    def actualizar_hora(self):
        self.fecha_hora_actual=time.strftime("%Y-%m-%d %H:%M:%S")
        self.fecha=time.strftime("%Y-%m-%d")
        self.hora=time.strftime("%H:%M:%S")
        self.Fecha_hora.config(text=self.fecha_hora_actual)
        self.ventana.after(1000, self.actualizar_hora)
    
    def validar_formato(self):
        # Utilizamos una expresión regular para verificar el formato
        patron = r'^[A-Za-z]{3}\d{3}$'
        cadena = self.EntryPlaca.get()
        print(cadena)
        if re.match(patron, cadena) and len(cadena) == 6:
            return True
        else:
            return False
        
    def No_es_float(self,cadena):
        try:
            float_value = float(cadena)
            return False
        except ValueError:
            return True