import random
from datetime import time
import model.bd as query
#import app as query

contadorSession = 0


def obtenerListaNegra(id, monto, tipo):
    sql = "SELECT * FROM listanegra WHERE idCliente = %s and montoTransaccion = %s and idTransaccionTipo = %s;"
    datos = (id,monto,tipo)
    query.Cursor.execute(sql,datos)
    tranzacciones = query.Cursor.fetchall()
    query.conn.commit()
    return len(tranzacciones)

def bloquearUsuario(id):
    sql="UPDATE cliente SET ClienteEstado = 0, ClienteToken=%s WHERE idCliente =%s;"
    datos = (generarTokenAccess(),id)
    query.Cursor.execute(sql,datos)
    query.conn.commit()

def generarTokenAccess():
    token = random.randint(1000000000, 9999999999)
    return str(token)

def formato24h(dato):
    parse = dato.split(":")
    horario = time(int(parse[0]), int(parse[1]), int(parse[2])) 
    return horario

def updateFraude(id):
    query.Cursor.execute("UPDATE detalletransaccioncuenta SET tipoFraude =1 WHERE idDetalleTransaccionCuenta =%s",(id))
    query.conn.commit()

def reporteGenerado():
    sql="SELECT count(c.idCliente) As TotalClientes,(SELECT count(*) FROM cliente WHERE ClienteEstado=1) As ClienteActivo,(SELECT count(*) FROM detalletransaccioncuentacomparativa) As TotalTrx,(SELECT count(*) FROM detalletransaccioncuentacomparativa WHERE tipoFraude=1) As DeteccionFraude,(SELECT count(*) FROM detalletransaccioncuenta WHERE tipoFraude=1) As DeteccionFraudeML,(SELECT SUM(d.montoTransaccion) FROM detalletransaccioncuenta d WHERE d.tipoFraude = 1 AND d.idDetalleTransaccionCuenta NOT IN (SELECT dc.idDetalleTransaccionCuenta FROM detalletransaccioncuentacomparativa dc WHERE dc.tipoFraude = 1)) As TotalMontoPP,(Select SUM(montoTransaccion) from detalletransaccioncuenta) AS MontoTotal FROM cliente c;"
    query.Cursor.execute(sql)
    reportes = query.Cursor.fetchall()
    query.conn.commit()
    return reportes

def queryMachineLearning(id):
    sql="SELECT * FROM detalletransaccioncuenta WHERE idCliente ="+str(id)+";"
    query.Cursor.execute(sql)
    tranzacciones = query.Cursor.fetchall()
    query.conn.commit()
    return tranzacciones

def inicioSession(idUsuario,contraseniaUsuario):
    sql="SELECT * FROM cliente WHERE cliente.ClienteEstado = 1 AND cliente.Clientedocumentos = "+str(idUsuario)+" AND cliente.ClienteContrasenia="+str(contraseniaUsuario)+";"
    query.Cursor.execute(sql)
    tranzacciones = query.Cursor.fetchall()
    
    query.conn.commit()
    return tranzacciones

def cambiarContraseniaSS(contraseniaCliente,documentoCliente,pinSeguridadCliente):
    sql="UPDATE cliente SET ClienteContrasenia = %s WHERE Clientedocumentos = %s AND PinSeguridad= %s;"
    datos = (contraseniaCliente,documentoCliente,pinSeguridadCliente)
    query.Cursor.execute(sql,datos)
    query.conn.commit()