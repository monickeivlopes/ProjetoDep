from flask import Flask, render_template, redirect, request, url_for, flash
from flask_mysqldb import MySQL
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'senhadoprojeto'

#configiração página inicial
@app.route('/')
def index():
    return render_template('index.html')

#configuração do banco
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_projetoHotel'

mysql = MySQL(app)

#página de hospedes
@app.route('/hospedes', methods=['GET'])
def hospedes():
    nome_filtro = request.args.get('nome', '')  
    ordem = request.args.get('ordenar', 'asc')  

    if ordem == 'asc':
        order_by = 'ASC'
    else:
        order_by = 'DESC'

    cur = mysql.connection.cursor()

    if nome_filtro:
        cur.execute("SELECT * FROM hospede WHERE nome LIKE %s ORDER BY nome " + order_by, (nome_filtro + '%',))
    else:
        cur.execute("SELECT * FROM hospede ORDER BY nome " + order_by)

    hospedes = cur.fetchall()  
    cur.close()

    return render_template('hospedes.html', hospedes=hospedes)

#página para adicionar hóspedes
@app.route('/add_hospede', methods=['GET', 'POST'])
def add_hospede():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        telefone = request.form['telefone']
        email = request.form['email']

       
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM hospede WHERE cpf = %s",(cpf,))
        existing_cpf = cur.fetchone()

        cur.execute("SELECT * FROM hospede WHERE email = %s", (email,))
        existing_email = cur.fetchone()
        
        if existing_cpf or existing_email:
            texto=('Já existe um hóspede com este CPF ou e-mail. Tente novamente com dados diferentes.')
            return render_template('add_hospedes.html', flash=texto)

        
        cur.execute("INSERT INTO hospede (nome, cpf, telefone, email) VALUES (%s, %s, %s, %s)",
                    (nome, cpf, telefone, email))
        mysql.connection.commit()
        cur.close()

        flash ('Hóspede adicionado com sucesso!', 'success')
        return redirect(url_for('hospedes'))  

    return render_template('add_hospedes.html')  

#página para editar hóspedes
@app.route('/edit_hospede/<int:id>', methods=['GET', 'POST'])
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
        cur.execute("UPDATE hospede SET nome = %s, cpf = %s, telefone = %s, email = %s WHERE id = %s",
                    (nome, cpf, telefone, email, id))
        mysql.connection.commit()
        cur.close()

        flash('Dados do hóspede atualizados com sucesso!', 'success')
        return redirect(url_for('hospedes'))

    return render_template('edit_hospede.html', hospede=hospede)

#página para excluir hóspedes
@app.route('/excluir_hospede/<int:id>', methods=['GET', 'POST'])
def excluir_hospede(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM hospede WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    flash('Hóspede excluído com sucesso!')
    return redirect(url_for('hospedes'))


#página dos quartos
@app.route('/quartos', methods=['GET','POST'])
def quartos():
    numero_filtro = request.args.get('numero', '')  
    ordem = request.args.get('ordenar', 'asc')  

    if ordem == 'asc':
        order_by = 'ASC'
    else:
        order_by = 'DESC'

    cursor = mysql.connection.cursor()

    if numero_filtro:
        cursor.execute("SELECT * FROM quarto WHERE numero LIKE %s ORDER BY numero " + order_by, (numero_filtro + '%',))
    else:
        cursor.execute("SELECT * FROM quarto ORDER BY numero " + order_by)

    quartos = cursor.fetchall()
    cursor.close()
    return render_template('quartos.html', quartos=quartos)

#página pada adicionar novos quartos
@app.route('/add_quartos', methods=['GET','POST'])
def add_quartos():
    if request.method == 'POST':
        numero = request.form['numero']
        tipo = request.form['tipo']
        preco = request.form['preco']
        capacidade = request.form['capacidade']
        descricao = request.form['descricao']

        cursor=mysql.connection.cursor()
        cursor.execute(f"SELECT * FROM quarto WHERE numero = {numero}")
        existing_quarto = cursor.fetchone()
        
        if existing_quarto:
            flash = ('Já existe um quarto com este número. Tente novamente com dados difierentes.')
            return render_template('add_quartos.html', flash=flash)
        
        cursor.execute("INSERT INTO quarto (numero, tipo, preco, capacidade, descricao) VALUES (%s, %s, %s, %s, %s)", (numero, tipo, preco, capacidade, descricao))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('quartos'))
    return render_template('add_quartos.html')

#página para excluir quartos
@app.route('/excluir_quarto/<int:id>', methods=['GET', 'POST'])
def excluir_quarto(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM quarto WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    flash('Hóspede excluído com sucesso!')
    return redirect(url_for('quartos'))

#página de reservas
@app.route('/reservas', methods=['GET', 'POST'])
def reservas():
    checkin_filter = request.form.get('checkin_filter')  
    ordem = request.form.get('ordem', 'asc')  

    cur = mysql.connection.cursor()
    
    query = """
        SELECT r.id, h.nome AS hospede, q.numero AS quarto, checkin, 
        checkout, total 
        FROM reserva r
        JOIN hospede h ON r.hos_id = h.id
        JOIN quarto q ON r.quarto_id = q.id
    """

    conditions = []
    params = []

    if checkin_filter:
        conditions.append("checkin = %s")
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


#página para adicionar reservas
@app.route('/add_reserva', methods=['GET', 'POST'])
def add_reserva():
    if request.method == 'POST':
        hos_id = request.form['hos_id']
        quarto_id = request.form['quarto_id']
        checkin = request.form['checkin']
        checkout = request.form['checkout']

        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT * FROM reserva 
            WHERE quarto_id = %s AND 
            (
                (checkin BETWEEN %s AND %s) OR 
                (checkout BETWEEN %s AND %s) OR 
                (checkin <= %s AND checkout >= %s)
            )
        """, (quarto_id, checkin, checkout, checkin, checkout, checkin, checkout))
        conflito = cur.fetchone()

        if conflito:
            flash('O quarto já está reservado para o período selecionado. Escolha outras datas ou outro quarto.', 'error')
            cur.close()
            return redirect(url_for('add_reserva'))

        checkin_date = datetime.strptime(checkin, '%Y-%m-%d')
        checkout_date = datetime.strptime(checkout, '%Y-%m-%d')
        dias = (checkout_date - checkin_date).days

        if dias <= 0:
            flash('A data de check-out deve ser posterior à data de check-in.', 'error')
            cur.close()
            return redirect(url_for('add_reserva'))


        cur.execute("SELECT preco FROM quarto WHERE id = %s", (quarto_id,))
        preco_quarto = cur.fetchone()

        if not preco_quarto:
            flash('Quarto inválido selecionado. Tente novamente.', 'error')
            cur.close()
            return redirect(url_for('add_reserva'))

        total = preco_quarto[0] * dias

        cur.execute("""
            INSERT INTO reserva (hos_id, quarto_id, checkin, checkout, total) 
            VALUES (%s, %s, %s, %s, %s)
        """, (hos_id, quarto_id, checkin, checkout, total))
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


#página para excluir reservas
@app.route('/excluir_reserva/<int:id>', methods=['GET', 'POST'])
def excluir_reserva(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM reserva WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    flash('Reserva excluída com sucesso!')
    return redirect(url_for('reservas'))

if __name__ == '__main__':
    app.run(debug=True)  

#página dos relátorios avançados
@app.route('/relatorios')
def relatorios():
    cur = mysql.connection.cursor()
    cur.execute('SELECT id,nome FROM hospede')
    hospedes = cur.fetchall()
    cur.close()

    return render_template('relatorios.html', hospedes=hospedes)

#página para relátorio total de reservas
@app.route('/total_reservas', methods=['GET','POST'])
def total_reservas():
    if request.method=='POST':
        data1 = request.form['data1']
        data2 = request.form['data2']
        cur = mysql.connect.cursor()
        cur.execute('SELECT nome, SUM(total) FROM hospede as h JOIN reserva as r ON h.id=r.hos_id WHERE checkin BETWEEN %s and %s GROUP BY nome ',(data1,data2))
        totais = cur.fetchall()
        cur.close()
        
        return render_template('total_reservas.html',totais=totais) 
    return render_template('total_reservas.html')

#página para relátorio de reservas acima de 2000,00
@app.route('/reservas_acima', methods=['GET','POST'])
def reservas_acima():
    cur = mysql.connect.cursor()
    cur.execute("SELECT nome, total FROM hospede as h JOIN reserva as r ON h.id = r.hos_id WHERE total>='2000' ")
    totais = cur.fetchall()
    cur.close()
    return render_template('reservas_acima.html',totais=totais)

#página para relátorio de quartos mais reservados
@app.route('/quartos_reservados', methods=['GET','POST'])
def quartos_reservados():
     if request.method=='POST':
        dias = request.form['tempo']
        cur = mysql.connect.cursor()
        dias = int(dias)  
        query = '''
        SELECT numero, COUNT(r.quarto_id) AS quartos
        FROM quarto AS q
        JOIN reserva AS r ON q.id = r.quarto_id
        WHERE checkin BETWEEN NOW() - INTERVAL %s DAY AND NOW()
        GROUP BY numero
        ORDER BY quartos DESC LIMIT 10
        '''
        cur.execute(query, (dias,))
        totais = cur.fetchall()
        cur.close()
        return render_template('quartos_reservados.html',totais=totais, dias=dias)

#página para relátorio de quartos não reservados
@app.route('/nao_reservados', methods=['GET','POST'])
def nao_reservados():
    cur = mysql.connect.cursor()
    query = '''
        SELECT q.numero FROM quarto as q
        WHERE q.id NOT IN (SELECT r.quarto_id FROM reserva r)
        '''
    
    cur.execute(query)
    totais = cur.fetchall()
    cur.close()
    if request.method=='POST':
        return render_template('nao_reservados.html',totais=totais)
    return render_template('nao_reservados.html',totais=totais)

