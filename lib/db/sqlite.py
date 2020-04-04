# -*-coding:utf8-*-
#
# Author:
# Christian Barral
#
# Description:
# Abstraccion de base de datos SQLite
#

import os
import re

import sqlite3 as sql3
import lib.helpers.os_utils as ou


class _SQLiteConnector:
    """ Representa el conector a la base de datos. Cada entrada de SQL_CREATE_TABLE es un string para
    crear cada una de las tablas.'.

    Cuando se intenta acceder a la base de datos, primero se comprueba que le archivo exista, si no es así
    ejecuta las sentencias de creación de tablase.
    """

    SQL_CREATE_TABLE = ['''
        CREATE TABLE EJEMPLO(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );''']

    def __init__(self, output_dir: str, filename: str):
        self.output_dir = output_dir
        self.filename = filename
        self.filetype = 'db'
        self.__connector = None
        self._cursor = None

    def __enter__(self) -> 'SQLite3 cursor de la base de datos':
        """ Entrada para 'with'
        """
        return self.get_sql3_cursor()

    def __exit__(self, exc_type, exc_val, exc_tb) -> 'Cerrar el cursor al salir de with':
        """ Salida de 'with'
        """
        return self.close_connection()

    def create_filename(self) -> str:
        """ Crea el nombre de archivo
        """
        processed_filename = re.sub('\.*', '', self.filename)

        return '{}.{}'.format(processed_filename, self.filetype)

    def create_db(self):
        """ Crea la base de datos SQLite
        """

        try:
            conn = sql3.connect('{}/{}'.format(self.output_dir, self.create_filename()))
        except sql3.Error as e:
            print('No se pudo conectar a la base de datos:\n{}'.format(e))
            return

        try:
            for i in _SQLiteConnector.SQL_CREATE_TABLE:
                conn.execute(i)
        except sql3.Error as e:
            print('Error creando tablas. SQLite dice:\n{}'.format(e))
            conn.close()

    def get_sql3_cursor(self) -> 'Cursor':
        """ Returns the database cursor for further query executions.
        """

        if not ou.exists_dir(self.output_dir):
            os.mkdir(self.output_dir)

        # Test database
        db_file = os.path.join(self.output_dir, self.create_filename())
        if not ou.exists_file(db_file):
            self.create_db()

        # Connect to get the cursor
        self.__connector = sql3.connect('{}/{}'.format(self.output_dir, self.create_filename()))
        self._cursor = self.__connector.cursor()
        return self.__connector.cursor()

    def close_connection(self):
        """ Close the SQLite connection
        """

        self.__connector.commit()
        if self._cursor is not None:
            self._cursor.close()


class DAO:
    """ Clase Data Access Object que implementa CRUD de forma genérnica para cualquier
    tabla.
    """

    def __init__(self):
        # COMPLETAR CON LOS PARAMETROS QUE SE QUIERA:
        # Primero el directorio, luego el nombre del archivo
        self.cursor = _SQLiteConnector('/opt/reparto_material', 'database.db')

    def read_all(self, table: str) -> list:
        """ Recupera todas las tuplas de una base de datos
        """
        with self.cursor as c:
            c.execute("SELECT * FROM {}".format(table))
            return c.fetchall()

    def read(self, table: str, attrs: (list,tuple), values:tuple) -> list:
        """ Recupera una tupla concreta. El programador DEBE pasar solamente las PKs.
        """
        with self.cursor as c:
            c.execute('SELECT * FROM {} WHERE {}'.format(table, ' AND '.join(['{} = ?'.format(x) for x in attrs])),
                      values)
            return c.fetchall()

    def insert(self, table: str, attrs: (tuple, list), values: tuple):
        """ Inserta para una tabla concreta, con unos atributos datos, los valores
        concretos
        """
        with self.cursor as c:
            c.execute('INSERT INTO {} ({}) VALUES ({})'
                      .format(table, ', '.join(attrs), ','.join(['?' for _ in values])), values)

    def delete(self, table: str, attrs: (tuple, list), values: tuple):
        """ Borra una(s) tuplas concretas de la BD
        """
        with self.cursor as c:
            c.execute('DELETE FROM {} WHERE {}'.format(table, ' AND '.join(['{} = ?'.format(x) for x in attrs])),
                      values)


