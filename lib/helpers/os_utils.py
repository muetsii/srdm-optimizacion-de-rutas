# -*- coding:utf8 -*-
#
# Author:
# Christian Barral
#
# Description:
# Funciones relacionadas con el SO

import os


def exists_file(file: str) -> bool:
    return os.path.isfile(file)


def exists_dir(direc: str) -> bool:
    return os.path.isdir(direc)
