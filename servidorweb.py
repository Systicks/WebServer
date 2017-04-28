#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import socket, select, string, sys, json, datetime, os
import threading

#Introducir la ruta de favicon.ico y de index.html
path_favicon = '/images/icon.ico'
path_index = '/index.html'

# successful
OK = '200 OK'
CREATED = '201 Created'
ACCEPTED = '202 Accepted'
NON_AUTHORITATIVE_INFORMATION = '203 Non Authoritative Information'
NO_CONTENT = '204 No Content'
RESET_CONTENT = '205 Reset Content'
PARTIAL_CONTENT = '206 Partial Content'

# redirection
MULTIPLE_CHOICES = '300 Multiple Choices'
MOVED_PERMANENTLY = '301 Moved Permanently'
FOUND = '302 Found'
SEE_OTHER = '303 See Other'
NOT_MODIFIED = '304 Not Modified'
USE_PROXY = '305 Use Proxy'
TEMPORARY_REDIRECT = 307

# client error
BAD_REQUEST = '400 Bad Request'
UNAUTHORIZED = 401
PAYMENT_REQUIRED = 402
FORBIDDEN = 403
NOT_FOUND = '404 Not Found'
METHOD_NOT_ALLOWED = 405
NOT_ACCEPTABLE = 406
PROXY_AUTHENTICATION_REQUIRED = 407
REQUEST_TIMEOUT = 408
CONFLICT = 409
GONE = 410
LENGTH_REQUIRED = 411
PRECONDITION_FAILED = 412
REQUEST_ENTITY_TOO_LARGE = 413
REQUEST_URI_TOO_LONG = 414
UNSUPPORTED_MEDIA_TYPE = 415
REQUESTED_RANGE_NOT_SATISFIABLE = 416
EXPECTATION_FAILED = 417

# server error
INTERNAL_SERVER_ERROR = '500 Internal Server Error'
NOT_IMPLEMENTED = '501 Not Implemented'
BAD_GATEWAY = 502
SERVICE_UNAVAILABLE = 503
GATEWAY_TIMEOUT = 504
HTTP_VERSION_NOT_SUPPORTED = 'HTTP/1.1 505 HTTP Version Not Supported'

#Variables globales
socket_list = []
mutex = threading.Lock()

def main():

	timeout = 300
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	port = int(sys.argv[1])
	s.bind(("", port))
	s.listen(20)
	socket_list.append(s)
	while True:

		read_sockets, write_sockets, error_sockets = select.select(socket_list , [], socket_list, timeout)

		for sock in error_sockets:
			print 'Error en socket'
		for sock in read_sockets:
			if sock == s:
				#se recibe una peticion por el socket de escucha, lo aceptamos y lo añadimos a la lista de sockets
				sockfd, addr = s.accept()
				socket_list.append(sockfd)
				print 'nueva conexion'
		
			else:
				#Eliminamos el socket de la lista para que dos hilos no puedan atender la misma petición usando exclusión mutua
				mutex.acquire()
				socket_list.remove(sock)
				mutex.release()
				t = threading.Thread(target=worker, args=(sock,))
				print socket_list
				t.start()

		if not (read_sockets or write_sockets or error_sockets):
			print 'Servidor web inactivo'

	s.close()

#Función ejecutada por los hilos
def worker(sock):

	peticion = sock.recv(4096)
	print peticion
	if not peticion:
		print 'cadena vacia'
		sock.close()
	else:
		mutex.acquire()#En exclusión mutua volvemos a añadir el socket a la lista para que se vuelvan a atender sus peticiones
		socket_list.append(sock)
		mutex.release()
		respuesta = HTTP (peticion)#Generamos un objeto que crea la cabecera y el mensaje de respuesta a partir de la petición

		#Si el método es GET:
		if respuesta.get_metodo() == 'GET':
			#Generamos la respuesta a la petición
			cabecera, cuerpo = respuesta.generar_respuesta()
			#print mensaje
			sock.send(cabecera)
			sock.send(cuerpo)
		#Si el método es HEAD solo enviamos la cabecera
		elif respuesta.get_metodo() == 'HEAD':
			cabecera = respuesta.generar_respuesta()
			sock.send(cabecera)
		#Si se trata de un post recibimos el contenido y lo guardamos
		elif respuesta.get_metodo() == 'POST':
			print 'Es un post'
			respuesta.guardar_post(peticion)#Metodo que guarda el post
			cabecera = respuesta.generar_respuesta()
			sock.send(cabecera)
		#Cualquier otro método devolvemos solo una cabecera infirmando con el error
		else:
			cabecera = respuesta.generar_respuesta()
			sock.send(cabecera)

		if(respuesta.version == 'HTTP/1.0'):
			mutex.acquire()
			socket_list.remove(sock)
			mutex.release()
			sock.close()
	return

#Clase que define los métodos y constructor que analizan la petición y generan la respuesta
class HTTP:

	#Atributos
	url = './index/index.html'
	version = 'HTTP/1.0'
	metodo = ''
	NotFound = './index/404.html'
	longitud = 0
	post = OK
	#Métodos
	#Constructor
	def __init__(self, peticion):

		lista_peticion = peticion.splitlines()#Hacemos una lista con cada una de las lineas recibidas
		metodo, url, version =lista_peticion[0].split()#Dividimos el primer string y guardamos cada campo en una variable
		lista_peticion.pop(0)
		#Obtenemos el resto de campos que nos interesen de la petición:
		for linea in lista_peticion:
			titulo = linea.split(':')
			if titulo[0] == 'Content-Length':
				self.longitud = titulo [1]

		#En caso de no especificar el archivo se devuelve la página principal
		if url == '/':
			url = path_index
		elif url == '/favicon.ico':
			url = path_favicon
		
		self.version = version
		self.url = './index' + url #añadimos el ./index para indicar el directorio donde buscar
		self.metodo = metodo

	#Devuelve el método que se está usando
	def get_metodo(self):
		return self.metodo

	#Guarda el contenido de una petición POST
	def guardar_post(self, peticion):
		datos = peticion.split('\r\n\r\n')
		try:
			archivo = open('./index/forms/' + str(datetime.datetime.today()), "w")
			archivo.write(datos[1])
		except IOError:
			print 'Error al crear el archivo'
			self.post = INTERNAL_SERVER_ERROR

	#Análisis de la extensión del archivo, se genera el campo Content-type
	def extension(self):
		punto, ruta, extension = self.url.split('.')
		#identificamos el tipo de extensión del archivo a enviar
		if extension == 'css':
			tipo_contenido = 'Content-type: text/css; charset=UTF-8' 
		elif extension == 'jpeg':
			tipo_contenido = 'Content-type: image/jpeg'
		elif extension == 'jpg':
			tipo_contenido = 'Content-type: image/jpg'
		elif extension == 'png':
			tipo_contenido = 'Content-type: image/png'
		elif extension == 'ico':
			tipo_contenido = 'Content-type: image/ico'
		elif extension == 'js':
			tipo_contenido = 'Content-type: text/javascript'
		elif extension == 'xml':
			tipo_contenido = 'Content-type: text/xml'
		elif extension == 'mp3':
			tipo_contenido = 'Content-type: audio/mp3'
		elif extension == 'webm':
			tipo_contenido = 'Content-type: video/webm'
		elif extension == 'appcache':
			tipo_contenido = 'Content-type: text/cache-manifes'
		else:
			tipo_contenido = 'Content-type: text/html; charset=UTF-8'
		#Insertamos este campo en la cabecera
		return tipo_contenido

	#Método que abre el archivo pedido con el método GET
	def leer_archivo(self):
		#Intentamos abrir el archivo pedido, en caso de no existir devolvemos un error 404
		try:
			archivo = open(self.url, "r")
		except IOError:
			print 'Ese archivo no existe'
			codigo = NOT_FOUND
			archivo = open(self.NotFound, "r")
			contenido = archivo.read()
			archivo.close()
			longitud = 'Content-length: ' + str(os.path.getsize(self.NotFound))
			return codigo, contenido, longitud

		contenido = archivo.read()
		archivo.close()
		codigo =  OK
		longitud = 'Content-length: ' + str(os.path.getsize(self.url))

		return codigo, contenido, longitud

	def generar_respuesta(self):
		
		#Campos que se envían siempre:
		format = "%A, %d-%b-%y %H:%M:%S"
		fecha = 'Date: ' + datetime.datetime.today().strftime(format) + ' GMT'
		servidor = 'Server: Python'
		rango = ''
		tipo_contenido = ''
		#Campos que son distintos en diferentes versiones de HTTP:
		if(self.version == 'HTTP/1.0'):
			conexion = ''

		elif(self.version == 'HTTP/1.1'):
			conexion = 'Connection: keep-alive'

		#Si la versión de HTTP no es soportada:
		else:
			codigo = HTTP_VERSION_NOT_SUPPORTED

		#Campos que dependen del método:
		if self.metodo == 'GET':
			#Empezamos a crear los campos de la cabecera y a insertarlos:
			tipo_contenido = self.extension()#Devuelve el tipo de contenido
			codigo, contenido, longitud = self.leer_archivo()#Abrimos el archivo y nos devuelve el código correspondiente y el contenido y la longitud
			rango = 'Accept-Ranges: bytes'
			
		elif self.metodo == 'HEAD':
			tipo_contenido = self.extension()#Devuelve el tipo de contenido
			codigo, contenido, longitud = self.leer_archivo()#Abrimos el archivo y nos devuelve el código correspondiente, el contenido y la longitud

		elif self.metodo == 'POST':
			codigo = self.post
		elif self.metodo == 'PUT':
			codigo = NOT_IMPLEMENTED
		elif self.metodo == 'OPTIONS':
			codigo = NOT_IMPLEMENTED
		elif self.metodo == 'DELETE':
			codigo = NOT_IMPLEMENTED
		elif self.metodo == 'TRACE':
			codigo = NOT_IMPLEMENTED
		elif self.metodo == 'CONNECT':
			codigo = NOT_IMPLEMENTED
		else:
			codigo = BAD_REQUEST

		estado = self.version + ' ' + codigo
		#Construcción de la cabecera con todos los campos incluidos:
		cabecera = [estado, rango, fecha, servidor,tipo_contenido, longitud,conexion,'\r\n']#creamos una lista con los campos de la cabecera
		#Quitamos los campos vacíos de la cabecera (si es http 1.1 conexión estará vacío)
		for campo in cabecera:
			if campo == '':
				cabecera.remove(campo)

		#Juntamos los campos de la cabecera separados por un salto de línea
		separador= '\r\n'
		cabecera = separador.join(cabecera)
		#mensaje = cabecera + contenido
		print cabecera
		
		#Dependiendo del método empleado se devuelven distintas cosas:
		if self.metodo == 'GET':
			return cabecera, contenido
		elif self.metodo == 'HEAD':
			return cabecera
		elif self.metodo == 'POST':
			return cabecera
		else:
			return cabecera


if __name__ == "__main__":
	main()