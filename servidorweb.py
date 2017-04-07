import socket, select, string, sys, json

cabecera = 'HTTP/1.0 200 OK\r\nDate: Friday, 6-May-11 15:40:00 GMT\r\nServer: Apache/1.1.1\r\nContent-type: text/html\r\nContent-length: 450\r\nConnection: close\r\n'


if __name__ == "__main__":
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("", 8000))
	s.listen(20)
	sc, addr = s.accept()
	recibido = sc.recv(500)
	print recibido

	archivo = open("index.html", "r") 
	contenido = archivo.read()
	
	mensaje = cabecera + contenido
	print mensaje
	sc.send(mensaje)

	sc.close()
	s.close()
