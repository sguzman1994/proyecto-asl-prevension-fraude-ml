import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from PIL import Image, ImageDraw, ImageFont
from email import encoders
from decouple import config
import app as query

def correoEncriptado():
    id = config("IDCLIENTE")
    documentoCliente = ""
    apellidoCliente = ""
    nombreCliente = ""
    correoCliente = ""
    tokenCliente = ""
    query.Cursor.execute("SELECT * FROM cliente WHERE idCliente =%s",(id))
    tranzacciones = query.Cursor.fetchall()
    
    for fila in tranzacciones:
        documentoCliente = fila[1]
        nombreCliente = fila[2]
        apellidoCliente = fila[3]
        correoCliente = fila[6]
        tokenCliente = fila[7]

    query.conn.commit()

    #Configuración del servidor SMTP y las credenciales
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    username = 'aarodriva@gmail.com'
    password = 'tveounykcfhtuykw'

    #Crear el objeto del mensaje
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = correoCliente
    msg['Subject'] = 'Deteccion de posible Fraude'

    #Crear una imagen con el contenido del cuerpo del mensaje
    image_width = 700 # Ancho
    image_height = 150 # Alto
    background_color = (255, 255, 255)  # Blanco
    text_color = (0, 0, 0)  # Negro

    image = Image.new('RGB', (image_width, image_height), background_color)
    draw = ImageDraw.Draw(image)

    font_path = 'arial.ttf'  # Ruta de la fuente que deseas utilizar
    font_size = 15
    font = ImageFont.truetype(font_path, font_size)

    #Texto de la imagen
    text = 'Access Token generado por el posible Fraude: '+str(tokenCliente)+', solicitado para desbloquearse'
    #Obtener las dimensiones del texto utilizando textbbox
    text_bbox = draw.textbbox((0, 0), text, font=font)
    # Obtener el ancho y alto del texto
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((image_width - text_width) // 2, (image_height - text_height) // 2)
    draw.text(text_position, text, font=font, fill=text_color)

    #Guardar la imagen en un archivo temporal
    image_temp_path = 'temp_image.png'
    image.save(image_temp_path)

    #Comprimir y encriptar el archivo adjunto en un archivo ZIP con contraseña
    import pyminizip
    archivo_zip = 'adjunto.zip'
    clave_zip = documentoCliente
    pyminizip.compress(image_temp_path, None, archivo_zip, clave_zip, 0)

    #Adjuntar el archivo ZIP al mensaje
    with open(archivo_zip, 'rb') as adjunto:
        parte_adjunta = MIMEBase('application', 'zip')
        parte_adjunta.set_payload(adjunto.read())
        encoders.encode_base64(parte_adjunta)
        parte_adjunta.add_header('Content-Disposition', f'attachment; filename="{archivo_zip}"')

    #Archivo adjunto del mensaje
    msg.attach(parte_adjunta)

    #Cuerpo del mensaje #VARIABLE:
    body = f'<p>Buenas tardes, cliente: '+nombreCliente+' '+apellidoCliente+'<br>ha saltado la alerta por posible <strong>\"FRAUDE\"</strong><br> por favor llamenos para desbloquear su aplicacion al: 0800-55555<br><br><strong>NOTA:</strong> tener en cuenta que necesitara el codigo de transaccion adjunto en el archivo zip el cual le pedirá su documento de identidad para ser visualizado</p>'
    msg.attach(MIMEText(body, 'html'))

    #Establecer conexión con el servidor SMTP
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(username, password)

    #Enviar el correo electrónico
    server.send_message(msg)

    #Cerrar la conexión
    server.quit()