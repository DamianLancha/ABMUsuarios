from flask import Flask, request, session, redirect, url_for, render_template, flash

from psycopg import connect

 
app = Flask(__name__)
app.secret_key = 'fdgfgdfgdsgs'
 
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = '1234'

host = DB_HOST
database = DB_NAME
username = DB_USER
password = DB_PASSWORD
port = DB_PORT

def get_db_connection():
    conn = connect(host=host, dbname=database,
                   user=username, password=password, port=port)
    return conn

conn = get_db_connection()

@app.route('/')
def home():
    # Si el usuario está logueado, muestro la página de inicio
    if 'loggedin' in session:       
        return render_template('home.html', username=session['username'])

    # Si no está logueado, muestro la página de login
    return redirect(url_for('login'))
 
@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor()

    # Al presionar el botón login, si están completos los campos
    if request.method == 'POST' and 'usuario' in request.form and 'contraseña' in request.form:

        # Obtengo los datos que ingresó el usuario
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']        
 
        # Verifico que el dni existe en la base de datos
        if usuario.isdigit():
            cursor.execute('SELECT * FROM users WHERE dni = %s', (usuario,))
            account = cursor.fetchone()
        else:
            flash('Datos Incorrectos')
            return render_template('login.html')
        
   

        # Si existe y el usuario = contraseña = dni, inicio sesión
        if account and usuario == contraseña:
            # Creo datos de sesión para poder utilizarlos en otras rutas
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            session['dni'] = account[2]
            return redirect(url_for('home'))
        else:
            flash('Datos Incorrectos')
 
    return render_template('login.html')
  
@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor()
 
    # Al presionar el botón registrar, si están completos los campos
    if request.method == 'POST' and 'apellidoynombre' in request.form and 'dni' in request.form :

        # Obtengo los datos que ingresó el usuario
        apellidoynombre = request.form['apellidoynombre']
        dni = request.form['dni']
    
        # Verifico si el dni está formado por dígitos y si existe en la base de datos
        if dni.isdigit():
            cursor.execute('SELECT * FROM users WHERE dni = %s', (dni,))
            account = cursor.fetchone()

            # Si el dni existe, no permito que se registre nuevamente
            if account:
                flash('Ya existe el DNI')
            else:
                # Si el dni no existía, lo registro en la base de datos
                cursor.execute("INSERT INTO users (apellidoynombre, dni) VALUES (%s,%s)", (apellidoynombre, dni))
                conn.commit()
                flash('Registro exitoso')
                return render_template('login.html')
        else:
            flash('DNI inválido')
    elif request.method == 'POST':
        # Si algún campo no está completo
        flash('Completar todos los campos')

    # Muestro nuevamente la página de registro
    return render_template('register.html')   
   
@app.route('/logout')
def logout():
    # Borro los datos de sesión
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirijo a la página de login
   return redirect(url_for('login'))
  
@app.route('/edit', methods=['GET', 'POST'])
def edit(): 
    cursor = conn.cursor()
   
    # Al presionar el botón guardar, si están completos los campos
    if request.method == 'POST' and 'apellidoynombre' in request.form and 'dni' in request.form :
        
        # Obtengo los datos que ingresó el usuario
        apellidoynombreNuevo = request.form['apellidoynombre']
        dniNuevo = request.form['dni']

        # Obtengo los datos de la sesión actual
        apellidoynombre = session['username']
        dni = session['dni']
    
        # Verifico si el dni ingresado existe en la base de datos
        cursor.execute('SELECT * FROM users WHERE dni = %s', (dniNuevo,))
        account = cursor.fetchone()

        # Si el dni ingresado existe y es distinto al dni de la sesión actual, no permito cambiarlo
        if account and str(dniNuevo) != str(dni):
            flash('Ya existe el DNI')
        else:
            # Actualizo los datos solo si el dni ingresado no existe o es igual al dni de la sesión actual
            cursor.execute("UPDATE users SET apellidoynombre=%s, dni=%s WHERE dni=%s", (apellidoynombreNuevo, dniNuevo, dni))
            conn.commit()

            # Redirijo a la página de login
            flash('Guardado exitoso')
            return redirect(url_for('login'))
            

        # Vuelvo a mostrar la página de edición
        return render_template('edit.html', session=session)

    elif request.method == 'POST':
        # Si algún campo no está completo
        flash('Completar todos los campos')

    else:
        # Si está iniciada la sesión
        if 'loggedin' in session:
            cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
            account = cursor.fetchone()
            # Muestro la página de edición con los datos de la sesión actual
            return render_template('edit.html', session=session)

    # Si no hay sesión iniciada, redirijo a la página de login
    return redirect(url_for('login'))

@app.route('/delete', methods=['GET', 'POST'])
def delete(): 
    cursor = conn.cursor()
   
   # Al presionar el botón eliminar, si están completos los campos
    if request.method == 'POST' and 'apellidoynombre' in request.form and 'dni' in request.form :

        # Obtengo los datos que ingresó el usuario
        apellidoynombreNuevo = request.form['apellidoynombre']
        dniNuevo = request.form['dni']
        dni = session['dni']
    
        # Verifico si el dni y apellidoynombre ingresados existen en la base de datos
        cursor.execute('SELECT * FROM users WHERE dni = %s AND apellidoynombre = %s', (dniNuevo,apellidoynombreNuevo,))
        account = cursor.fetchone()

        # Si existe
        if account:           

            # Elimino el registro de la base de datos      
            cursor.execute("DELETE FROM users WHERE dni=%s and apellidoynombre=%s", (dniNuevo, apellidoynombreNuevo))
            conn.commit()
            flash('Se eliminó correctamente')

            # Si el dni ingresado es igual al dni de la sesión actual 
            if str(dniNuevo) == str(dni): 
                # Redirijo a la página de login
                return redirect(url_for('login'))
            else:
                # Redirijo nuevamente a la página de eliminar
                return redirect(url_for('delete'))            

        # Si no existe vuelvo a mostrar la página de eliminar
        flash('Datos incorrectos')
        return render_template('delete.html')

    elif request.method == 'POST':
        # Si algún campo no está completo
        flash('Completar todos los campos')

    else:
        # Si está iniciada la sesión
        if 'loggedin' in session:
            cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
            account = cursor.fetchone()
             # Muestro la página de eliminar con los datos de la sesión actual
            return render_template('delete.html', session=session)

    # Si no hay sesión iniciada, redirijo a la página de login
    return redirect(url_for('login'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    cursor = conn.cursor()
 
    # Al presionar el botón buscar, si está completo el campo
    if request.method == 'POST' and 'apellidoynombre' in request.form:
        # Obtengo el dato que ingresó el usuario
        apellidoynombre = request.form['apellidoynombre']

        # Busco en la base de datos los registros que coincidan con el apellidoynombre
        cursor.execute('SELECT * FROM users WHERE apellidoynombre = %s', (apellidoynombre,))
        data = cursor.fetchall()

        # Vuelvo a mostrar la página de búsqueda
        return render_template('search.html', data=data)     

    elif request.method == 'POST':
        # Si algún campo no está completo
        flash('Completar todos los campos')
    else:
        # Muestro la página de búsqueda
        return render_template('search.html')

@app.route('/userslist')
def userslist():

    # Busco en la base de datos todos los registros
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY dni")
    data = cursor.fetchall()
    
    return render_template('userslist.html', data=data)

if __name__ == "__main__":
    app.run(debug=True)