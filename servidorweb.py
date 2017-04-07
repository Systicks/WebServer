#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import socket, select, string, sys, json, datetime

def analizar_peticion(peticion):

	if not peticion:
		print 'cadena vacia'
	#print peticion
	lista_peticion = peticion.splitlines()#Hacemos una lista con cada una de las lineas recibidas
	metodo, url, version =lista_peticion[0].split()#Dividimos el primer string y guardamos cada campo en una variable
	#En caso de no especificar el archivo se devuelve la página principal
	if url == '/':
		url = '/index.html'
	return './index' + url #añadimos el ./index para indicar el directorio donde buscar

def generar_respuesta(url):
	punto, ruta, extension = url.split('.')
	#identificamos el tipo de extensión del archivo a enviar
	if extension == 'css':
		tipo_contenido = 'Content-type: text/css; charset=utf-8' 
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
	else:
	 	tipo_contenido = 'Content-type: text/html; charset=utf-8'

	try:
		archivo = open(url, "r")
	except IOError:
		print 'Ese archivo no existe'
		codigo = 'HTTP/1.0 404 No encontrado'
		return codigo
	
	contenido = archivo.read()
	archivo.close()


	codigo = 'HTTP/1.0 200 OK'
	format = "%A, %d-%b-%y %H:%M:%S"
	fecha = 'Date: ' + datetime.datetime.today().strftime(format) + ' GMT'
	servidor = 'Server: Python'
	longitud = 'Content-lenght: ' + str(len(contenido))
	#conexion = 'Connection: keep-alive'
	cabecera = [codigo,fecha, servidor,tipo_contenido, longitud, '\r\n']#creamos una lista con los campos de la cabecera
	separador= '\r\n'
	cabecera = separador.join(cabecera)#Juntamos los campos de la cabecera

	mensaje = cabecera + contenido
	return mensaje


cabecera = 'HTTP/1.0 200 OK\r\nDate: Friday, 6-May-11 15:40:00 GMT\r\nServer: Apache/1.1.1\r\nContent-type: text/html\r\nContent-length: 460\r\nConnection: keep-alive\r\n'

if __name__ == "__main__":
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	port = int(sys.argv[1])
	s.bind(("", port))
	s.listen(5)
	socket_list = [s]

	while True:
		print 'en select'
		read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
		print 'saliendo select'

		for sock in read_sockets:
			if sock == s:
				#se recibe una peticion por el socket de escucha, lo aceptamos y lo añadimos a la lista de sockets
				sockfd, addr = s.accept()
				sockfd.setblocking(0)
				socket_list.append(sockfd)
				print 'nueva conexion'
			else:
				recibido = sock.recv(4096)
				print recibido
				url = analizar_peticion(recibido)
				#Recibimos una petición de un navegador, hay que responder
				mensaje = generar_respuesta(url)
				#print mensaje
				sock.send(mensaje)
				socket_list.remove(sock)
				sock.close()

	s.close()

