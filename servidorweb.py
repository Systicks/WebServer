#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import socket, select, string, sys, json, datetime

class HTTP:
	#Prueba github
	url = './index/index.html'
	version = 'HTTP/1.0'

	def __init__(self, peticion):

		lista_peticion = peticion.splitlines()#Hacemos una lista con cada una de las lineas recibidas
		metodo, url, version =lista_peticion[0].split()#Dividimos el primer string y guardamos cada campo en una variable
		#En caso de no especificar el archivo se devuelve la página principal
		if url == '/':
			url = '/index.html'
		
		self.version = version
		self.url = './index' + url #añadimos el ./index para indicar el directorio donde buscar


	def generar_respuesta(self):
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
		elif extension == 'mp3':
			tipo_contenido = 'Content-type: audio/mp3'
		else:
		 	tipo_contenido = 'Content-type: text/html; charset=UTF-8'

		try:
			archivo = open(self.url, "r")
		except IOError:
			print 'Ese archivo no existe'
			codigo = 'HTTP/1.0 404 No encontrado'
			return codigo
		
		contenido = archivo.read()
		archivo.close()

		if(self.version == 'HTTP/1.0'):

			codigo = self.version + ' ' + '200 OK'
			print codigo
			format = "%A, %d-%b-%y %H:%M:%S"
			fecha = 'Date: ' + datetime.datetime.today().strftime(format) + ' GMT'
			servidor = 'Server: Python'
			longitud = 'Content-lenght: ' + str(len(contenido))
			#conexion = 'Connection: keep-alive'
			cabecera = [codigo,fecha, servidor,tipo_contenido, longitud, '\r\n']#creamos una lista con los campos de la cabecera
			separador= '\r\n'
			cabecera = separador.join(cabecera)#Juntamos los campos de la cabecera
			mensaje = cabecera + contenido

		elif(self.version == 'HTTP/1.1'):
			rango = 'Accept-Ranges: bytes'
			codigo = self.version + ' ' + '200 OK'
			print codigo
			format = "%A, %d-%b-%y %H:%M:%S"
			fecha = 'Date: ' + datetime.datetime.today().strftime(format) + ' GMT'
			servidor = 'Server: Python'
			longitud = 'Content-lenght: ' + str(len(contenido))
			conexion = 'Connection: keep-alive\r\nKeep-Alive: timeout=5, max=1000'
			cabecera = [codigo, rango, fecha, servidor,tipo_contenido, longitud, conexion,'\r\n']#creamos una lista con los campos de la cabecera
			separador= '\r\n'
			cabecera = separador.join(cabecera)#Juntamos los campos de la cabecera
			mensaje = cabecera + contenido
			print 'Inicio' + cabecera + 'Fin'

		return mensaje

class HTTP1(HTTP):
	def analizar_peticion(self, sock):
		peticion = sock.recv(4096)
		print 'peticion'
		if not peticion:
			print 'cadena vacia'
		#print peticion
		lista_peticion = peticion.splitlines()#Hacemos una lista con cada una de las lineas recibidas
		metodo, url, version =lista_peticion[0].split()#Dividimos el primer string y guardamos cada campo en una variable
		#En caso de no especificar el archivo se devuelve la página principal
		if url == '/':
			url = '/index.html'
		return './index' + url #añadimos el ./index para indicar el directorio donde buscar

if __name__ == "__main__":
	timeout = 300
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	port = int(sys.argv[1])
	s.bind(("", port))
	s.listen(20)
	socket_list = [s]

	while True:
		print 'en select'
		read_sockets, write_sockets, error_sockets = select.select(socket_list , [], socket_list, timeout)
		print 'saliendo select'
		for sock in error_sockets:
			print 'Error en socket'
		for sock in read_sockets:
			if sock == s:
				#se recibe una peticion por el socket de escucha, lo aceptamos y lo añadimos a la lista de sockets
				sockfd, addr = s.accept()
				#sockfd.setblocking(0)
				socket_list.append(sockfd)
				print 'nueva conexion'
				
			else:
				peticion = sock.recv(4096)
				print peticion
				if not peticion:
					print 'cadena vacia'
					socket_list.remove(sock)
					sock.close()
				else:
					respuesta = HTTP (peticion)#Generamos un objeto que crea la cabecera y el mensaje de respuesta a partir de la petición

					#Generamos la respuesta a la petición
					mensaje = respuesta.generar_respuesta()
					#print mensaje
					sock.send(mensaje)
					if(respuesta.version == 'HTTP/1.0'):
						socket_list.remove(sock)
						sock.close()
					#Lo suyo sería permitir conexiones persistentes al usar HTTP 1.1, pero no se completan las peticiones por algún motivo
					if(respuesta.version == 'HTTP/1.1'):
						socket_list.remove(sock)
						sock.close()
				

		if not (read_sockets or write_sockets or error_sockets):
			print 'Servidor web inactivo'

	s.close()

