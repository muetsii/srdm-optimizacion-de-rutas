# -*- coding:utf8 -*-
#
# Author:
# Christian Barral
#
# Description:
# Clase para asignar métodos y URIs a callbacks


# -*-coding:utf8-*-
#
# Author:
# Christian
#
# Description:
# Web server routing
#

import re


class URIDispatcher:
    """ Clase empleada para manejar las URIs a las que responde el servicio REST.

    Una petición REST está caracterizada por dos cosas:
        - URI: /esto/es/un/ejemplo
        - Verbo: GET; POST, PUT, DELETE

    Esta clase tiene dos atributos principales:
        - mappings es una lista de tuplas, en las que cada tupla viene definida por tres elementos:
            (verbo: str, patron_uri: str, callback: function)
            El patron_uri es un string que define la URI a la que se va a responder, pero acepta tokens, lo que quiere
            decir que podremos ponder $<num> en aquellos sitios de la URI que sean variables. Ej:
                /api/hospital/$1 -> Aqui, $1 puede ser cualquier valor referente a un ID, así que ponemos un token
        - stored_args es un diccionario que se va reescribiendo por cada URI procesada. Si la URI coincide con un patron
            y ese patron lleva tokens, el valor real que se ha mandado en ese momento se almacenara bajo
            self.stored_args[<token>]. Por ejemplo
                /api/hospital/$1 -> Un cliente hace peticion a /api/hospital/354 -> self.stored_args['$1'] es '354'

    Debe ser instanciada en la clase del servidor Web.
    """

    TOKEN_REGEX = re.compile('\$([0-9]+?)')

    def __init__(self):
        self.mappings = []
        self.stored_args = {}

    @property
    def mappings(self):
        return self._mappings

    @mappings.setter
    def mappings(self, v: list):
        """ Afirma que es una lista de tuplas, en la que cada tupla tiene 3 elementos, donde los dos primeros son
        strings y el tercero es una funcion callback.
         """
        self._mappings = v

        assert isinstance(v, list)
        assert all([isinstance(i, tuple) for i in self.mappings])
        assert all(len(i) == 3 for i in self.mappings)
        assert all([isinstance(i[0], str) and isinstance(i[1], str) and callable(i[2]) for i in self.mappings])

    def dispatch_request(self, method: str, path: str) -> (False, 'Callback function'):
        """ Para un método y una petición concreta, comprueba si matchean y devuelve la funcion callback correspondiente
        """
        self.stored_args = {}
        for m_method, pattern, callback in self.mappings:
            if m_method == method.upper():
                if self.match_request(path, pattern):
                    return callback

        return False

    def match_request(self, path: str, url_pattern: str) -> bool:
        """ Comprueba si un path coincide con un patron definido.
        """

        # Parte tanto la peticion real como el patron por /
        path_tokens = path.split('/')
        pattern_tokens = url_pattern.split('/')

        # Si no coinciden en longitud, ya no coinciden
        if len(path_tokens) != len(pattern_tokens):
            return False

        # Comprueba si cada una de las partes son iguales, o si una de ellas es un token. En caso afirmativo,
        # mete el valor que coincide con el token en stored_args
        self.stored_args = {}
        for i, j in zip(path_tokens, pattern_tokens):
            if i != j:
                if URIDispatcher.TOKEN_REGEX.match(j):
                    self.stored_args[j] = i
                else:
                    return False

        # Ordena stored_args por el numero que va despues de $
        if len(self.stored_args):
            sorted(self.stored_args)

        return True
