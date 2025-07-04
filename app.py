from flask import Flask, render_template, redirect, request, url_for, flash
from flask_mysqldb import MySQL
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from MySQLdb._exceptions import IntegrityError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'senhadoprojeto'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(usuario_id):
    return User.get(usuario_id)


#configiração página inicial
@app.route('/index')
def index():
    user = current_user
    if user.tipo == 'administrador':
        barra = True
        return render_template('index.html', barra=barra)
    else: 
        return render_template('index.html')

#configuração do banco
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_projetoHotel'

mysql = MySQL(app)

#página login
@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        senha = request.form['senha']
        
        user = User.get_by_email(email)

        if not user:
            
            flash("E-mail não cadastrado!", "error")
            return render_template('login.html')

        if not user.senha==senha:
            
            flash("Senha incorreta!", "error")
            return render_template('login.html')

        login_user(user, remember=True)

        if user.tipo == 'usuario':
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))

  
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        email = request.form['email']
        telefone = request.form['telefone']
        nome = request.form['nome']
        senha = request.form['senha']
        tipo = 'usuario'
        cpf = request.form['cpf']
        

        existing_user_email = User.get_by_email(email)
        existing_user_cpf = User.get_by_cpf(cpf)
        if existing_user_email:
            flash("E-mail já está em uso!", "error")
            return render_template('registro.html')
        elif existing_user_cpf:
            flash("Cpf já está em uso!", "error")
            return render_template('registro.html')
        


        

        User.create(nome=nome, email=email, telefone=telefone, senha=senha,tipo=tipo,cpf=cpf)

        
        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for('login'))
    return render_template('registro.html')
