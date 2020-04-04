# -*- coding:utf8 -*-
#
# Author:
# Christian Barral
#
# Description:
# Script principal de la aplicacion

import sys


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


if __name__ == '__main__':
    main()
