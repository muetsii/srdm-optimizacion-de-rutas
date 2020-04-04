# -*- coding:utf8 -*-
#
# Author:
# Christian Barral
#
# Description:
# Script principal de la aplicacion

import sys
import os

import lib.helpers.os_utils as ou

from lib.web_service import WebServer


def is_python_3() -> bool:
    """ Comprueba si la version actual es python 3
    """
    return sys.version_info[0] == 3


def main():
    """ Aquí debe ir el código principal de la aplicación
    """

    if not is_python_3():
        print('ERROR: Se requiere Python 3')
        sys.exit(-1)

    if not ou.exists_dir('/opt/reparto_material'):
        os.mkdir('/opt/reparto_material')

    WebServer.WebServer(8081).launcher_server()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrumpido por el usuario.')