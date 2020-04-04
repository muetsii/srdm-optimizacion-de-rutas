# -*- coding:utf8 -*-
#
# Author:
# Christian Barral
#
# Description:
# Servidor Web que implementa la lógica y hace uso de URIDispatcher

import cgi
import ssl
import os
import json
import http.server as hts
import http.cookies as hck
import logging

from lib.db.sqlite import DAO
from lib.web_service.URIDispatcher import URIDispatcher


class CustomRequestHandler(hts.BaseHTTPRequestHandler):
    """ Define el comportamiento de la aplicacion REST.

    Contiene el URI dispatcher para procesar las rutas y todas las funciones callback a ejecutar para cada una de las
    peticiones. Tambien hay una serie de decoradores para ayudar a crear dichas funciones callback, seguir viendo
    mas abajo para ver cuales son.

    """
    def __init__(self, request, client_address, server):
        self.dao = DAO()
        self.dispatcher = URIDispatcher()
        # Definicion de verbo + ruta + callback
        self.dispatcher.mappings = [
            ('GET', '/example', self.hello_rest)
        ]
        # Directorio actual
        self.cwd = os.getcwd()
        # Log a /var/log
        logging.basicConfig(filename='/var/log/reparto_material.log', level=logging.DEBUG)
        super().__init__(request, client_address, server)

    def log_message(self, format_f: 'Funcion de formato', *args: 'Argumentos adicionales de formato'):
        """ Define el formato de logging
        """
        logging.debug(''"%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format_f%args))

    def composed(*decs):
        """ Este docorador simplemente permite ejecutar varios decoradores en una sola linea
        """

        def deco(f):
            for dec in reversed(decs):
                f = dec(f)
            return f
        return deco

    def html(func):
        """ Define codigo 200 y respuesta de tipo HTML
        """
        def put_headers(self, *args, **kwargs):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            func(self, *args, **kwargs)

        return put_headers

    def json(func):
        """ Define codigo 200 y respuesta de tipo JSON
        """
        def put_headers(self, *args, **kwargs):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=UTF-8')
            self.end_headers()
            func(self, *args, **kwargs)

        return put_headers

    def recibe_json(func):
        """ Comprueba si la peticion tiene content-type: application/json
        """

        def check_headers(self, *args, **kwargs):
            ctype, pdict = cgi.parse_header(self.headers.get('Content-Type'))

            if ctype != 'application/json':
                self.send_response(400)
                self.end_headers()
                return
            func(self, *args, **kwargs)

        return check_headers

    def requiere_auth(func):
        """ RELLENAR CON EL CODIGO DE AUTENTICACION DE CLIENTE
        """

        def check_auth(self, *args, **kwargs):
            # Cookies es un diccionario con clave(cookie) -> valor(valor de cookie)
            cookies = hck.SimpleCookie(self.headers.get('Cookie'))

            # Escribir código aquí: Si no se autentica, se debe poner codigo 401 y un return debajo.
            func(self, *args, **kwargs)

        return check_auth

    def get_json(self):
        """ Recoge el JSON enviado en la petición. Requiere que la funcion que llame a esta funcion esté decorada
        por @recibe_json
        """
        length = int(self.headers.get('content-length'))
        return json.loads(self.rfile.read(length))

    def stdout_write(self, info: (dict)):
        """ Escribe en el <body> de la respuesta. Acepta un diccionario que será convertido a un JSON.
        """
        self.wfile.write(json.dumps(info).encode('utf8'))


    ################################
    # INICIO: Funciones de ejemplo #
    ################################
    @json
    def hello_rest(self):
        self.stdout_write({'status': 1, 'msg': 'Hello REST!'})

    ################################
    # FIN: Funciones de ejemplo ####
    ################################

    def do_GET(self):
        """ Rutina que responde a TODAS las peticiones GET
        """
        callback_func = self.dispatcher.dispatch_request('GET', self.path)
        if not callback_func:
            self.send_response(404, 'Recurso no encontrado')
            return
        else:
            callback_func()

    def do_POST(self):
        """ Rutina que responde a TODAS las peticiones POST
        """
        callback_func = self.dispatcher.dispatch_request('POST', self.path)
        if not callback_func:
            self.send_response(404, 'Recurso no encontrado')
            return
        else:
            callback_func()

    def do_PUT(self):
        """ Rutina que responde a TODAS las peticiones PUT
        """
        callback_func = self.dispatcher.dispatch_request('PUT', self.path)
        if not callback_func:
            self.send_response(404, 'Recurso no encontrado')
            return
        else:
            callback_func()

    def do_DELETE(self):
        """ Rutina que responde a TODAS las peticiones DELETE
        """
        callback_func = self.dispatcher.dispatch_request('DELETE', self.path)
        if not callback_func:
            self.send_response(404, 'Recurso no encontrado')
            return
        else:
            callback_func()


class WebServer:
    """ Representa el servidor web
    """
    def __init__(self, port):
        self.port = port

        # Tupla para iniciar HTTP server
        self._address = ('', port)

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, port):
        self._port = port
        assert isinstance(port, int) and 0 < port < 65536

    def launcher_server(self):
        """ Inicia HTTP server
        """
        server = hts.HTTPServer(self._address, CustomRequestHandler)
        # DESCOMENTAR ESTA LINEA PARA CUANDO TENGAMOS UN CERTIFICADO Y CLAVE PRIVADA.
        '''
        server.socket = ssl.wrap_socket(server.socket,
                                        server_side=True,
                                        certfile=os.path.join(os.getcwd(), 'web_conf/cert.pem'),
                                        keyfile=os.path.join(os.getcwd(), 'web_conf/key.pem'),
                                        ssl_version=ssl.PROTOCOL_TLSv1_2)
                                        '''

        print('API REST levantada en http://localhost:{}'.format(self._address[1]))
        server.serve_forever()
