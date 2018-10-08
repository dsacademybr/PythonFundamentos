from flask import Flask, render_template, json, request
from werkzeug import generate_password_hash, check_password_hash
# pip install flask-mysql (Mac/Linux)
# pip install Flask-MySQL (Windows)
from flaskext.mysql import MySQL


mysql = MySQL()
app = Flask(__name__)

# MySQL setup
app.config['MYSQL_DATABASE_USER'] = 'appuser'
app.config['MYSQL_DATABASE_PASSWORD'] = 'app9872#'
app.config['MYSQL_DATABASE_DB'] = 'appdb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # Valida os dados recebidos
        if _name and _email and _password:
            
            with closing(mysql.connect()) as conn:
                with closing(conn.cursor()) as cursor:
            
                    _hashed_password = generate_password_hash(_password)
                    cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
                    data = cursor.fetchall()

                    if len(data) is 0:
                        conn.commit()
                        return json.dumps({'message':'User criado com sucesso!'})
                    else:
                        return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>preencha os campos requeridos</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})

if __name__ == "__main__":
    app.run(port=5002)
