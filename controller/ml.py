import pandas as pd
from decouple import config
import model.val as val
import controller.sms as send

def motorMachineLearning():
    id = config("IDCLIENTE")
    datos = pd.DataFrame(val.queryMachineLearning(id))
    ultimo_registro = datos.tail(1)
    datos = datos.drop(datos.index[-1])
    datos[['hora', 'minutos','segundos']] = datos[5].str.split(':', expand=True)

    # Asignación de etiquetas categóricas "dia" o "noche" según el rango de horario
    datos['horario'] = datos['hora'].astype(int).apply(lambda x: 'dia' if x >= 6 and x < 18 else 'noche')

    # Eliminar las columnas no usadas: hora, minutos, segundos
    datos = datos.drop(columns=['hora'])
    datos = datos.drop(columns=['minutos'])
    datos = datos.drop(columns=['segundos'])
    datos = datos.drop(columns=[5])

    # Visualiza los primeros registros del DataFrame
    print("\nMuestra de datos cargados desde el tabla:\n",datos.head())

    # La variable a predecir en regresion logistica debe ser true o false, 1 o 0 -> Fraude o No Fraude
    datos['cliente'] = datos[1]
    datos = datos.drop(columns=[1])

    datos['monto'] = datos[6]
    datos = datos.drop(columns=[6])

    datos['entidad'] = datos[4]
    datos = datos.drop(columns=[4])

    datos['tipo'] = datos[3]
    datos = datos.drop(columns=[3])

    datos['tipoFraude'] = datos[7]
    datos = datos.drop(columns=[7])

    # Codificación de variables categóricas
    datos_codificados = pd.get_dummies(datos, columns=['entidad','horario'])
    print("Muestra los datos codificados\n",datos_codificados)

    # Variables predictoras (X) y variable objetivo (y)
    x = datos_codificados[['cliente','monto','entidad_falabella','entidad_ripley','entidad_entre cuentas','entidad_interbancaria','tipo','horario_dia','horario_noche']]
    y = datos_codificados['tipoFraude']
    print(datos.head())
    from sklearn.linear_model import LogisticRegression
    # Crear y entrenar el modelo de Regresión Logística
    modelo = LogisticRegression(max_iter=1000)
    modelo.fit(x, y)

    # Realizar predicciones en los datos existentes
    predicciones = modelo.predict(x)

    # Calcular la precisión del modelo
    from sklearn.metrics import accuracy_score
    accuracy = accuracy_score(y, predicciones)

    # Calcular el porcentaje de error
    error = 1 - accuracy
    # Mostrar el porcentaje de error
    print("\nExactitud de prediccion: ", 100 - int(error * 100), "%\n")

    # Agregar las predicciones al DataFrame original
    datos['prediccion'] = predicciones

    # Visualizar los resultados de la predicción
    print("Datos existentes predecidos: -> variable nueva informativa 'prediccion'\n",datos[['cliente','monto','entidad','tipo','horario', 'tipoFraude', 'prediccion']])

    # Datos para predecir una nueva transacción 
    nueva_transaccion = pd.DataFrame({
        'cliente' : ultimo_registro[1],
        'monto': ultimo_registro[6],
        'entidad': ultimo_registro[4],
        'tipo': ultimo_registro[3],
        'horario': ultimo_registro[5]
    })

    # Codificar las variables categóricas del nuevo movimiento
    nueva_transaccion_codificada = pd.get_dummies(nueva_transaccion, columns=['cliente','monto','entidad','tipo','horario'])

    # Reindexar el DataFrame del nuevo movimiento
    nueva_transaccion_codificada = nueva_transaccion_codificada.reindex(columns=x.columns, fill_value=0)

    print("\nDatos de la nueva transaccion:\n",nueva_transaccion)
    # Realizar la predicción con el nuevo movimiento
    prediccion_nueva_transaccion = modelo.predict(nueva_transaccion_codificada)

    #categorizar variables del nuevo movimiento
    cliente = nueva_transaccion['cliente'].iloc[0]
    monto = nueva_transaccion['monto'].iloc[0]
    tipo = nueva_transaccion['tipo'].iloc[0]

    resultado = "Fraude"
    # Imprimir el resultado de la predicción
    if prediccion_nueva_transaccion[0] == 1:
        val.bloquearUsuario(cliente)
        val.updateFraude(ultimo_registro[0].iloc[0])
        send.correoEncriptado()
        print("\nLa nueva transaccion fue categorizada por IA como posible: " + resultado)
        resultado = "La nueva transaccion fue categorizada por IA como posible: Fraude"
    else:
        if (val.obtenerListaNegra(cliente,monto,tipo)>=1):
            val.updateFraude(ultimo_registro[0].iloc[0])
            print("\nLa transaccion fue: Bloqueada, por lista negra del usuario")
            resultado = "La transaccion fue: Bloqueada, por lista negra del usuario"
        else:
            resultado = "No Fraude"
            print("\nLa nueva transaccion fue categorizada por IA como posible: " + resultado)
    return resultado        