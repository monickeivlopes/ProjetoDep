from flask_login import UserMixin
from flask_mysqldb import MySQL


class User(UserMixin):
    def __init__(self, id, nome, email, telefone, senha, tipo, cpf):
        self.id = id
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.senha = senha
        self.tipo = tipo
        self.cpf = cpf

    @staticmethod
    def get(user_id):
        from app import mysql
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, nome, email, telefone, senha, tipo, cpf FROM hospede WHERE id = %s", (user_id,))
        result = cur.fetchone()
        cur.close()
        
        if result:
            return User(*result) 
        return None

    @staticmethod
    def get_by_email(email):
        from app import mysql
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, nome, email, telefone, senha, tipo, cpf FROM hospede WHERE email = %s", (email,))
        result = cur.fetchone()
        cur.close()
        if result:
            return User(*result) 
        return None
    @staticmethod
    def get_by_cpf(cpf):
        from app import mysql
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, nome, cpf, email, telefone, senha, tipo FROM hospede WHERE cpf = %s", (cpf,))
        result = cur.fetchone()
        cur.close()
        if result:
            return User(*result) 
        return None


        
        

    @staticmethod
    def create(nome, email, telefone, senha, tipo, cpf):
        from app import mysql
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO hospede (nome, email, cpf, telefone, senha, tipo) VALUES (%s, %s, %s, %s, %s, %s)",
            (nome, email, cpf, telefone, senha, tipo)
        )
        mysql.connection.commit()
        cur.close()
        
