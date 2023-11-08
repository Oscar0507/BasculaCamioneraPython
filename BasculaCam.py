from interfazGraf import Interfaz
from DataBaseBascula import BaseDeDatos
import tkinter as tk


def main():
    ventana = tk.Tk()
    app = Interfaz(ventana)     # Llama la clase Interfaz y ajusta toda la interfaz gráfica
    lista_clientes=app.Base_de_datos.obtener_clientes()
    lista_productos=app.Base_de_datos.obtener_productos()
    lista_obras=app.Base_de_datos.obtener_obras()
    lista_ubicaciones=app.Base_de_datos.obtener_ubicaciones()
    
    app.actualizar_cliente_list(lista_clientes)
    app.actualizar_producto(lista_productos)
    app.actualizar_obras(lista_obras)
    app.actualizar_ubicaciones(lista_ubicaciones)

    registro_disponible = app.Base_de_datos.obtener_registro_max()+1
    app.actualizar_registro(registro_disponible)
    app.Placas_pend=app.Base_de_datos.obtener_placas()
    app.actualizar_lista_placas()
    ventana.mainloop()


if __name__ == "__main__":
    main()