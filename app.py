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


#página de hospedes
@app.route('/hospedes', methods=['GET'])
@login_required
def hospedes():
    nome_filtro = request.args.get('nome', '')  
    ordem = request.args.get('ordenar', 'asc')  

    if ordem == 'asc':
        order_by = 'ASC'
    else:
        order_by = 'DESC'

    cur = mysql.connection.cursor()

    if nome_filtro:
        cur.execute("SELECT * FROM hospede WHERE nome LIKE %s and tipo = 'usuario' ORDER BY nome  " + order_by, (nome_filtro + '%',))
    else:
        cur.execute("SELECT * FROM hospede WHERE tipo = 'usuario' ORDER BY nome  " + order_by)

    hospedes = cur.fetchall()  
    cur.close()

    user = current_user


    if not user:
        flash("Usuário não encontrado.", "error")
        return redirect(url_for("login"))

    if user.tipo == 'usuario':
        flash('Você não permissão para entrar')
        return render_template('quartos.html')
    else:
        barra = True
        return render_template('hospedes.html', hospedes=hospedes, barra=barra)

#página para adicionar hóspedes
@app.route('/add_hospede', methods=['GET', 'POST'])
@login_required
def add_hospede():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        telefone = request.form['telefone']
        email = request.form['email']
        tipo = request.form['tipo']
        senha = request.form['senha']

       
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM hospede WHERE cpf = %s",(cpf,))
        existing_cpf = cur.fetchone()

        cur.execute("SELECT * FROM hospede WHERE email = %s", (email,))
        existing_email = cur.fetchone()
        
        if existing_cpf or existing_email:
            texto=('Já existe um hóspede com este CPF ou e-mail. Tente novamente com dados diferentes.')
            return render_template('add_hospedes.html', flash=texto)

        
        cur.execute("INSERT INTO hospede (nome, cpf, telefone, email,senha, tipo) VALUES (%s, %s, %s, %s, %s, %s)",
                    (nome, cpf, telefone, email, senha, tipo))
        mysql.connection.commit()
        cur.close()

        
        return redirect(url_for('hospedes'))  

    user = current_user


    if not user:
        flash("Usuário não encontrado.", "error")
        return redirect(url_for("login"))

    if user.tipo == 'usuario':
        flash('Você não permissão para adicionar', 'error')
        return render_template('quartos.html')
    else:
        return render_template('add_hospedes.html')   
