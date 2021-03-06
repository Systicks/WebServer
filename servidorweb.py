#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import socket, select, string, sys, json, datetime, os, argparse, time
import threading

#Introducir la ruta de favicon.ico y de index
path_favicon = '/images/icon.ico'
path_index = './'
#Tiempo en segundos para el mensaje de timeout
TIMEOUT = 300

#Definiciones de códigos de error
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

# client error
BAD_REQUEST = '400 Bad Request'
NOT_FOUND = '404 Not Found'
LENGTH_REQUIRED = '411 Lenght Required'

# server error
INTERNAL_SERVER_ERROR = '500 Internal Server Error'
NOT_IMPLEMENTED = '501 Not Implemented'
HTTP_VERSION_NOT_SUPPORTED = 'HTTP/1.1 505 HTTP Version Not Supported'

#Variables globales
socket_list = []
mutex = threading.Lock()

def main():
	#Obtenemos las opciones mediante argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("-p",help="Asignar el puerto", type = int, default=8000)
	parser.add_argument("-t", help="Activar multithreading", action='store_true' , default=False)
	args = parser.parse_args()
	if args.p:
		port=int(args.p)
	if args.t:
		multithreading = args.t
	else:
		multithreading = False
	#Creación del socket principal y establecimiento del puerto
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("", port))
	s.listen(20)
	socket_list.append(s)

	#Se ejecuta un bucle u otro si hemos decidido usar multithreading
	if multithreading == True:

		while True:
			read_sockets, write_sockets, error_sockets = select.select(socket_list , [], socket_list, TIMEOUT)
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
					try:
						socket_list.remove(sock)
					except:
						print 'El socket ya ha sido eliminado'
					mutex.release()
					#Creación del hilo y llamada a la función que atiende
					t = threading.Thread(target=lectura_socket_hilos, args=(sock,))
					print socket_list
					t.start()
			#Mensaje de servidor inactivo
			if not (read_sockets or write_sockets or error_sockets):
				print 'Servidor web inactivo'

	#Sin multithreading:
	else:

		while True:
			read_sockets, write_sockets, error_sockets = select.select(socket_list , [], socket_list, TIMEOUT)
			for sock in error_sockets:
				print 'Error en socket'
			for sock in read_sockets:
				if sock == s:
					#se recibe una peticion por el socket de escucha, lo aceptamos y lo añadimos a la lista de sockets
					sockfd, addr = s.accept()
					socket_list.append(sockfd)
					print 'nueva conexion'

				else:
					#Llamada a la función que se encarga de atender la petición
					lectura_socket(sock)
			#Mensaje de servidor inactivo
			if not (read_sockets or write_sockets or error_sockets):
				print 'Servidor web inactivo'

	s.close()

#Función para la lectura del socket
def lectura_socket(sock):
	#Recepción de la petición
	peticion = sock.recv(4096)
	print peticion
	#En caso de que sea una cadena vacía se cierra el socket
	if not peticion:
		print 'cadena vacia'
		socket_list.remove(sock)
		sock.close()
	else:
		#Generamos un objeto que crea la cabecera y el mensaje de respuesta a partir de la petición
		respuesta = HTTP (peticion)
		#Si el método es GET:
		if respuesta.get_metodo() == 'GET':
			#Generamos la respuesta a la petición
			cabecera, cuerpo = respuesta.generar_respuesta()
			#Enviamos la respuesta
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
			cabecera, cuerpo = respuesta.generar_respuesta()
			sock.send(cabecera)
			sock.send(cuerpo)
		#Cualquier otro método devolvemos solo una cabecera infirmando con el error
		else:
			cabecera = respuesta.generar_respuesta()
			sock.send(cabecera)
		#En caso de que la versión empleada sea 1.0 cerramos el socket después de cada petición
		if(respuesta.version == 'HTTP/1.0'):
			socket_list.remove(sock)
			sock.close()

	return

#Función ejecutada por los hilos si usamos multithreading
def lectura_socket_hilos(sock):
	#Recepción de la petición
	try:
		peticion = sock.recv(4096)
	except:
		print 'Error en la recepción'
		return
	#En exclusión mutua volvemos a añadir el socket a la lista para que se vuelvan a atender sus peticiones
	mutex.acquire()
	socket_list.append(sock)
	mutex.release()
	print peticion
	#En caso de que sea una cadena vacía se cierra el socket
	if not peticion:
		print 'cadena vacia'
		mutex.acquire()
		try:
			socket_list.remove(sock)
		except:
			print 'El socket ya ha sido eliminado'
			mutex.release()
			return
		mutex.release()
		sock.close()

	else:
		#Generamos un objeto que crea la cabecera y el mensaje de respuesta a partir de la petición
		respuesta = HTTP (peticion)

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
			cabecera, cuerpo = respuesta.generar_respuesta()
			sock.send(cabecera)
			sock.send(cuerpo)
		#Cualquier otro método devolvemos solo una cabecera infirmando con el error
		else:
			cabecera = respuesta.generar_respuesta()
			sock.send(cabecera)
		#En caso de que la versión empleada sea 1.0 cerramos el socket después de cada petición
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
		lista_peticion.pop(0)#Eliminamos la primera línea que ya ha sido analiazda
		#Obtenemos el resto de campos que nos interesen de la petición:
		for linea in lista_peticion:
			titulo = linea.split(':')
			if titulo[0] == 'Content-Length':
				self.longitud = titulo [1]

		#En caso de no especificar el archivo se devuelve la página principal
		if url == '/':
			url = '/index.html'
		#Si nos pide el favicon insertamos la ruta donde está nuestro icono
		elif url == '/favicon.ico':
			url = path_favicon

		#En caso de que la petición contenga datos en la URL los tenemos en cuenta
		try:
			url, datos = url.split('?')
		except:
			url = url
		#Guardamos los datos obtenidos en los atributos del objeto
		self.version = version
		self.url = path_index + 'index' + url #añadimos el ./index para indicar el directorio donde buscar
		self.metodo = metodo

	#Devuelve el método que se está usando
	def get_metodo(self):
		return self.metodo

	#Guarda el contenido de una petición POST con nombre la fecha en la carpeta especificada
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
		elif extension == 'http':
			tipo_contenido = 'Content-type: text/html; charset=UTF-8'
		else:
			tipo_contenido = 'Content-type: text; charset=UTF-8'

		return tipo_contenido

	#Método que abre el archivo pedido con el método GET u otro
	def leer_archivo(self):
		#Intentamos abrir el archivo pedido, en caso de no existir devolvemos un error 404 y el documento html diseñado para este error
		try:
			archivo = open(self.url, "r")
		except IOError:
			print 'Ese archivo no existe'
			codigo = NOT_FOUND
			archivo = open(self.NotFound, "r")
			contenido = archivo.read()
			archivo.close()
			longitud = 'Content-length: ' + str(os.path.getsize(self.NotFound))
			modificado = 'Last-Modified: ' + time.ctime(os.path.getmtime(self.NotFound))
			return codigo, contenido, longitud, modificado

		contenido = archivo.read()
		archivo.close()
		codigo =  OK
		longitud = 'Content-length: ' + str(os.path.getsize(self.url))
		modificado = 'Last-Modified: ' + time.ctime(os.path.getmtime(self.url))
		#Devolvemos el código generado, el contenido del obeto, la longitud del mismo y la fecha de modificación
		return codigo, contenido, longitud, modificado

	def generar_respuesta(self):
		
		#Campos que se envían siempre:
		format = "%A, %d-%b-%y %H:%M:%S"
		fecha = 'Date: ' + datetime.datetime.today().strftime(format) + ' GMT'
		servidor = 'Server: Python'
		cache = 'Cache-Control: public, max-age=3'#max-age, tiempo en segundos (3 segundos para pruebas)
		rango = ''
		tipo_contenido = ''
		longitud = ''
		#Campos que son distintos en diferentes versiones de HTTP:
		if(self.version == 'HTTP/1.0'):
			conexion = ''

		elif(self.version == 'HTTP/1.1'):
			conexion = 'Connection: keep-alive'

		#Si la versión de HTTP no es soportada:
		else:
			codigo = HTTP_VERSION_NOT_SUPPORTED

		#Campos que dependen del método:
		#Método GET, devolvemos el objeto que se nos pide
		if self.metodo == 'GET':
			#Empezamos a crear los campos de la cabecera y a insertarlos:
			tipo_contenido = self.extension()#Devuelve el tipo de contenido
			codigo, contenido, longitud, modificado = self.leer_archivo()#Abrimos el archivo y nos devuelve el código correspondiente y el contenido y la longitud
			rango = 'Accept-Ranges: bytes'
		#Método HEAD, devolvemos solo la cabecera
		elif self.metodo == 'HEAD':
			tipo_contenido = self.extension()
			codigo, contenido, longitud, modificado = self.leer_archivo()
		#Método POST, mandamos el código OK si se han podido guardar los datos y enviamos la página nuevamente
		elif self.metodo == 'POST':
			codigo = self.post
			tipo_contenido = self.extension()
			codigo, contenido, longitud, modificado = self.leer_archivo()
			rango = 'Accept-Ranges: bytes'

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

		#Concatenamos la versión con el código de estado
		estado = self.version + ' ' + codigo
		#Construcción de la cabecera con todos los campos incluidos:
		cabecera = [estado, rango, fecha, servidor,tipo_contenido, cache, longitud, conexion, modificado, '\r\n']#creamos una lista con los campos de la cabecera
		#Quitamos los campos vacíos de la cabecera si alguno no se ha usado
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
			return cabecera, contenido
		else:
			return cabecera


if __name__ == "__main__":
	main()