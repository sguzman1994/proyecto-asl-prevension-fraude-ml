from datetime import time
import model.bd as query

class Cursor:
    pass

def getRulers():
    sql="SELECT * FROM reglasnegocio;"
    query.Cursor.execute(sql)
    reglas = query.Cursor.fetchall()
    query.conn.commit()
    return reglas
