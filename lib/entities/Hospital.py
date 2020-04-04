# -*- coding:utf8 -*-
#
# Author:
# Christian Barral
#
# Description:
# Representacion de la entidad Hospital


from lib.entities.base import Node


class Plantilla:
    """ Representa el turno de un hospital
    """

    def __init__(self, num_medicos: int, num_celadores: int, num_uci: int):
        self.num_medicos = num_medicos
        self.num_celadores = num_celadores
        self.num_uci = num_uci

    def __len__(self):
        """ Metodo especial para len()"""
        return self.num_medicos + self.num_celadores + self.num_uci


class Turno(Plantilla):
    """ Representa la plantilla de un hospital
    """

    def __init__(self, num_medicos: int, num_celadores: int, num_uci: int):
        super().__init__(num_medicos, num_celadores, num_uci)


class Inventario:
    """ Representa el inventario de un hospital
    """

    def __init__(self, **kwargs):
        self.objetos = {}

        # Carga cada uno de keywords como clave -> valor
        for i, j in kwargs:
            self.objetos[i] = j

    def __len__(self):
        return sum([i for i in self.objetos.values()])

    def __getitem__(self, item):
        try:
            return self.objetos[item]
        except KeyError:
            return []

    def __setitem__(self, key, value):
        self.objetos[key] = value


class Hospital(Node):

    def __init__(self,
                 num_camas: int,
                 num_camas_ocupadas: int,
                 num_pacientes_nuevos_uci: int,
                 inventario: Inventario,
                 trabajadores: Plantilla,
                 turno: Turno,
                 direccion: str):

        self.num_camas = num_camas
        self.num_camas_ocupadas = num_camas_ocupadas
        self.num_pacientes_nuevos_uci = num_pacientes_nuevos_uci

        self.inventario = inventario
        self.trabajadores = trabajadores
        self.turno = turno

        self.direccion = direccion

        # Tasa de ocupacion
        self.tasa_ocupacion = num_camas / num_camas_ocupadas

    def get_demanda(self) -> dict:
        """ Devuelve un diccionario con clave(material) -> valor(cantidad)
        """
        personal_de_turno = len(self.turno)
        demanda = {
            'gorros': 3 * personal_de_turno,
            'gafas': len(self.trabajadores),
            'mascarillas_ffp2': 3 * (self.turno.num_medicos + self.turno.num_celadores),
            'mascarillas_ffp3': 3 * self.turno.num_uci,
            'guantes': 6 * personal_de_turno,
            'batas_impermeables': 6 * personal_de_turno,
            'pijamas': 3 * personal_de_turno,
            'calzas': 6 * personal_de_turno,
            'hidroalcohol': self.num_camas // 8,
            'mascarillas_quirurjicas': self.num_camas_ocupadas,
            'respiradores': self.num_pacientes_nuevos_uci
        }
        for i in demanda:
            x = demanda[i] - self.inventario[i]
            demanda[i] = x if x < 0 else 0

        return demanda
