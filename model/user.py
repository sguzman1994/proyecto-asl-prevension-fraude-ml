from datetime import time
import model.bd as query
#import app as query

class Cursor:
    pass

contadorSession = 0

def cambiarContrasenia(contraseniaCliente,documentoCliente,pinSeguridadCliente):
    sql="UPDATE cliente SET ClienteContrasenia = %s WHERE Clientedocumentos = %s AND PinSeguridad= %s;"
    datos = (contraseniaCliente,documentoCliente,pinSeguridadCliente)
    query.Cursor.execute(sql,datos)
    query.conn.commit()

def inicioSession(idUsuario,contraseniaUsuario):
    sql="SELECT * FROM cliente WHERE cliente.ClienteEstado = 1 AND cliente.Clientedocumentos = "+str(idUsuario)+" AND cliente.ClienteContrasenia="+str(contraseniaUsuario)+";"
    query.Cursor.execute(sql)
    tranzacciones = query.Cursor.fetchall()
    query.conn.commit()
    return tranzacciones