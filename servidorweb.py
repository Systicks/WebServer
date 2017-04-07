#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import socket, select, string, sys, json, datetime

def analizar_peticion(peticion):
	lista_peticion = peticion.splitlines()#Hacemos una lista con cada una de las lineas recibidas
	metodo, url, version =lista_peticion[0].split()#Dividimos el primer string y guardamos cada campo en una variable
	#En caso de no especificar el archivo se devuelve la página principal
	if url == '/':
		url = '/index.html'
	return './index' + url #añadimos el ./index para indicar el directorio donde buscar

def generar_respuesta(url):
	try:
		archivo = open(url, "r")
	except IOError:
		print 'Ese archivo no existe'
		codigo = 'HTTP/1.0 404 No encontrado'
	
	contenido = archivo.read()
	archivo.close()


	codigo = 'HTTP/1.0 200 OK'
	format = "%A, %d-%b-%y %H:%M:%S"
	fecha = 'Date: ' + datetime.datetime.today().strftime(format) + ' GMT'
	servidor = 'Server: Python'
	tipo_contenido = 'Content-type: text/html'
	longitud = 'Content-lenght: ' + str(len(contenido))
	conexion = 'Connection: keep-alive'
	cabecera = [codigo,fecha, servidor,tipo_contenido, longitud, conexion, '\r\n\r\n']#creamos una lista con los campos de la cabecera
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

		read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

		for sock in read_sockets:
			if sock == s:
				#se recibe una peticion por el socket de escucha, lo aceptamos y lo añadimos a la lista de sockets
				sockfd, addr = s.accept()
				socket_list.append(sockfd)
			else:
				recibido = sock.recv(4096)
				#print recibido
				url = analizar_peticion(recibido)
				#Recibimos una petición de un navegador, hay que responder
				mensaje = generar_respuesta(url)
				print mensaje
				sock.send(mensaje)
				#socket_list.remove(sock)
				#sock.close()

	s.close()

