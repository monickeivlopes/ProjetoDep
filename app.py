from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_mysqldb import MySQL
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


hash_senha = generate_password_hash("admin123")
print(hash_senha)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'senhadoprojeto'

# Configuração do banco
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_projetoHotel'

mysql = MySQL(app)

# ----------------- DECORATORS -----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            flash('Você precisa estar logado.', 'warning')
            return redirect(url_for('login'))
        cur = mysql.connection.cursor()
        cur.execute("SELECT role FROM usuarios WHERE id = %s", (session['usuario'],))
        user_role = cur.fetchone()
        cur.close()
        if not user_role or user_role[0] != 'ADM':
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ----------------- ROTAS -----------------

@app.route('/')
def index():
    return render_template('index.html')

# ----------------- CADASTRO -----------------
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        senha_hash = generate_password_hash(senha)

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        existing_user = cur.fetchone()
        if existing_user:
            flash('Este e-mail já está cadastrado.', 'danger')
            cur.close()
            return redirect(url_for('cadastro'))

        # Role padrão: USR
        cur.execute("INSERT INTO usuarios (nome, email, senha, role) VALUES (%s, %s, %s, %s)",
                    (nome, email, senha_hash, 'USR'))
        mysql.connection.commit()
        cur.close()

        flash('Cadastro realizado com sucesso! Faça o login.', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro.html')

# ----------------- LOGIN -----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], senha):  
            session['usuario'] = user[0]  
            session['usuario_role'] = user[4]  
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('E-mail ou senha inválidos.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# ----------------- LOGOUT -----------------
@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da sessão.', 'info')
    return redirect(url_for('login'))

# ----------------- HÓSPEDES -----------------
@app.route('/hospedes', methods=['GET'])
@login_required
def hospedes():
    nome_filtro = request.args.get('nome', '')
    ordem = request.args.get('ordenar', 'asc')
    order_by = 'ASC' if ordem == 'asc' else 'DESC'

    cur = mysql.connection.cursor()
    if nome_filtro:
        cur.execute("SELECT * FROM hospede WHERE nome LIKE %s ORDER BY nome " + order_by, (nome_filtro+'%',))
    else:
        cur.execute("SELECT * FROM hospede ORDER BY nome " + order_by)
    hospedes = cur.fetchall()
    cur.close()
    return render_template('hospedes.html', hospedes=hospedes)

@app.route('/add_hospede', methods=['GET', 'POST'])
@admin_required
def add_hospede():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        telefone = request.form['telefone']
        email = request.form['email']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM hospede WHERE cpf = %s OR email = %s", (cpf, email))
        existing = cur.fetchone()
        if existing:
            flash('Já existe um hóspede com este CPF ou e-mail.', 'danger')
            cur.close()
            return render_template('add_hospedes.html')

        cur.execute("INSERT INTO hospede (nome, cpf, telefone, email) VALUES (%s,%s,%s,%s)",
                    (nome, cpf, telefone, email))
        mysql.connection.commit()
        cur.close()
        flash('Hóspede adicionado com sucesso!', 'success')
        return redirect(url_for('hospedes'))

    return render_template('add_hospedes.html')

@app.route('/edit_hospede/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_hospede(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM hospede WHERE id = %s", (id,))
    hospede = cur.fetchone()
    cur.close()

    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        telefone = request.form['telefone']
        email = request.form['email']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE hospede SET nome=%s, cpf=%s, telefone=%s, email=%s WHERE id=%s",
                    (nome, cpf, telefone, email, id))
        mysql.connection.commit()
        cur.close()

        flash('Dados do hóspede atualizados com sucesso!', 'success')
        return redirect(url_for('hospedes'))

    return render_template('edit_hospede.html', hospede=hospede)

@app.route('/excluir_hospede/<int:id>', methods=['GET', 'POST'])
@admin_required
def excluir_hospede(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM hospede WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Hóspede excluído com sucesso!', 'success')
    return redirect(url_for('hospedes'))

# ----------------- QUARTOS -----------------
@app.route('/quartos', methods=['GET','POST'])
@login_required
def quartos():
    numero_filtro = request.args.get('numero', '')
    ordem = request.args.get('ordenar', 'asc')
    order_by = 'ASC' if ordem == 'asc' else 'DESC'

    cur = mysql.connection.cursor()
    if numero_filtro:
        cur.execute("SELECT * FROM quarto WHERE numero LIKE %s ORDER BY numero " + order_by, (numero_filtro+'%',))
    else:
        cur.execute("SELECT * FROM quarto ORDER BY numero " + order_by)
    quartos = cur.fetchall()
    cur.close()
    return render_template('quartos.html', quartos=quartos)

@app.route('/add_quartos', methods=['GET','POST'])
@admin_required
def add_quartos():
    if request.method == 'POST':
        numero = request.form['numero']
        tipo = request.form['tipo']
        preco = request.form['preco']
        capacidade = request.form['capacidade']
        descricao = request.form['descricao']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM quarto WHERE numero = %s", (numero,))
        existing_quarto = cur.fetchone()
        if existing_quarto:
            flash('Já existe um quarto com este número.', 'danger')
            cur.close()
            return render_template('add_quartos.html')

        cur.execute("INSERT INTO quarto (numero, tipo, preco, capacidade, descricao) VALUES (%s,%s,%s,%s,%s)",
                    (numero, tipo, preco, capacidade, descricao))
        mysql.connection.commit()
        cur.close()
        flash('Quarto adicionado com sucesso!', 'success')
        return redirect(url_for('quartos'))

    return render_template('add_quartos.html')

@app.route('/excluir_quarto/<int:id>', methods=['GET', 'POST'])
@admin_required
def excluir_quarto(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM quarto WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Quarto excluído com sucesso!', 'success')
    return redirect(url_for('quartos'))

# ----------------- RESERVAS -----------------
@app.route('/reservas', methods=['GET','POST'])
@login_required
def reservas():
    checkin_filter = request.values.get('checkin_filter')
    ordem = request.values.get('ordem', 'asc')
    cur = mysql.connection.cursor()
    query = """
        SELECT r.id, h.nome AS hospede, q.numero AS quarto, checkin, checkout, total
        FROM reserva r
        JOIN hospede h ON r.hos_id = h.id
        JOIN quarto q ON r.quarto_id = q.id
    """
    conditions = []
    params = []
    if checkin_filter:
        conditions.append("checkin=%s")
        params.append(checkin_filter)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += f" ORDER BY checkin {ordem}"
    cur.execute(query, tuple(params))
    reservas = cur.fetchall()
    cur.close()

    reservas_formatadas = []
    for reserva in reservas:
        checkin = reserva[3].strftime('%d/%m/%Y')
        checkout = reserva[4].strftime('%d/%m/%Y')
        reservas_formatadas.append(reserva[:3] + (checkin, checkout, reserva[5]))

    return render_template('reservas.html', reservas=reservas_formatadas, checkin_filter=checkin_filter, ordem=ordem)

@app.route('/add_reserva', methods=['GET', 'POST'])
@login_required
def add_reserva():
    if request.method == 'POST':
        hos_id = request.form['hos_id']
        quarto_id = request.form['quarto_id']
        checkin = request.form['checkin']
        checkout = request.form['checkout']

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT * FROM reserva
            WHERE quarto_id=%s AND
            ((checkin BETWEEN %s AND %s) OR
            (checkout BETWEEN %s AND %s) OR
            (checkin<=%s AND checkout>=%s))
        """, (quarto_id, checkin, checkout, checkin, checkout, checkin, checkout))
        conflito = cur.fetchone()
        if conflito:
            flash('O quarto já está reservado para o período selecionado.', 'danger')
            cur.close()
            return redirect(url_for('add_reserva'))

        checkin_date = datetime.strptime(checkin, '%Y-%m-%d')
        checkout_date = datetime.strptime(checkout, '%Y-%m-%d')
        dias = (checkout_date - checkin_date).days
        if dias <= 0:
            flash('A data de check-out deve ser posterior à data de check-in.', 'danger')
            cur.close()
            return redirect(url_for('add_reserva'))

        cur.execute("SELECT preco FROM quarto WHERE id=%s", (quarto_id,))
        preco_quarto = cur.fetchone()
        if not preco_quarto:
            flash('Quarto inválido.', 'danger')
            cur.close()
            return redirect(url_for('add_reserva'))

        total = preco_quarto[0]*dias
        cur.execute("INSERT INTO reserva (hos_id, quarto_id, checkin, checkout, total) VALUES (%s,%s,%s,%s,%s)",
                    (hos_id, quarto_id, checkin, checkout, total))
        mysql.connection.commit()
        cur.close()
        flash('Reserva adicionada com sucesso!', 'success')
        return redirect(url_for('reservas'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nome FROM hospede")
    hospedes = cur.fetchall()
    cur.execute("SELECT id, numero FROM quarto")
    quartos = cur.fetchall()
    cur.close()
    return render_template('add_reserva.html', hospedes=hospedes, quartos=quartos)

@app.route('/excluir_reserva/<int:id>', methods=['GET','POST'])
@admin_required
def excluir_reserva(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM reserva WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Reserva excluída com sucesso!', 'success')
    return redirect(url_for('reservas'))

# ----------------- RELATÓRIOS -----------------
@app.route('/relatorios')
@admin_required
def relatorios():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nome FROM hospede")
    hospedes = cur.fetchall()
    cur.close()
    return render_template('relatorios.html', hospedes=hospedes)

@app.route('/total_reservas', methods=['GET','POST'])
@admin_required
def total_reservas():
    if request.method=='POST':
        data1 = request.form['data1']
        data2 = request.form['data2']
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT nome, SUM(total) 
            FROM hospede as h JOIN reserva as r ON h.id=r.hos_id 
            WHERE checkin BETWEEN %s and %s 
            GROUP BY nome
        """, (data1,data2))
        totais = cur.fetchall()
        cur.close()
        return render_template('total_reservas.html', totais=totais)
    return render_template('total_reservas.html')

@app.route('/reservas_acima', methods=['GET','POST'])
@admin_required
def reservas_acima():
    cur = mysql.connection.cursor()
    cur.execute("SELECT nome, total FROM hospede as h JOIN reserva as r ON h.id = r.hos_id WHERE total>='2000'")
    totais = cur.fetchall()
    cur.close()
    return render_template('reservas_acima.html', totais=totais)

@app.route('/quartos_reservados', methods=['GET','POST'])
@admin_required
def quartos_reservados():
    if request.method=='POST':
        dias = int(request.form['tempo'])
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT numero, COUNT(r.quarto_id) AS quartos
            FROM quarto AS q
            JOIN reserva AS r ON q.id = r.quarto_id
            WHERE checkin BETWEEN NOW() - INTERVAL %s DAY AND NOW()
            GROUP BY numero
            ORDER BY quartos DESC LIMIT 10
        """, (dias,))
        totais = cur.fetchall()
        cur.close()
        return render_template('quartos_reservados.html', totais=totais, dias=dias)
    return render_template('quartos_reservados.html')

@app.route('/nao_reservados', methods=['GET','POST'])
@admin_required
def nao_reservados():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT numero FROM quarto WHERE id NOT IN (SELECT quarto_id FROM reserva)
    """)
    totais = cur.fetchall()
    cur.close()
    return render_template('nao_reservados.html', totais=totais)

# ----------------- RODAR -----------------
if __name__ == '__main__':
    app.run(debug=True)
