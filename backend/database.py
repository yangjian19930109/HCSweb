# -*- coding: utf-8 -*-
import pymysql
from backend.config import DB_CONFIG

class Database:
    def __init__(self):
        self.conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.conn.cursor()
    def execute(self, sql, params=None):
        self.cursor.execute(sql, params)
    def fetchall(self):
        return self.cursor.fetchall()
    def fetchone(self):
        return self.cursor.fetchone()
    def commit(self):
        self.conn.commit()
    def close(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None
    @property
    def lastrowid(self):
        return self.cursor.lastrowid

def get_db():
    return Database()

