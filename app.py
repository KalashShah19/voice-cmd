from flask import Flask, render_template, request, redirect, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)
app = Flask(__name__, static_folder='templates/static')

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'voice_finance'
app.config['MYSQL_HOST'] = 'localhost'

mysql = MySQL(app)

@app.route('/')
def index():
    # cur = mysql.connection.cursor()
    # cur.execute("select * from users")
    # data = cur.fetchall()
    # cur.close()
    # return render_template('voice.html', data = data)
    return render_template('voice.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/registration', methods=['POST'])
def registration():
    data = request.form
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO users (name,email,password,mobile) VALUES (%s, %s, %s, %s)",(data['name'],data['email'],data['password'],data['mobile']))
    mysql.connection.commit()
    cursor.close()
    print("User Registered")
    return jsonify({"message": "Redirecting..."}), 200

@app.route('/ai')
def ai():
    return render_template('ai.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/budgets')
def budgets():
    return render_template('budgets.html')

@app.route('/goals')
def goals():
    return render_template('goals.html')

@app.route('/investments')
def investments():
    return render_template('investments.html')

@app.route('/transactions')
def transactions():
    return render_template('transactions.html')

@app.route('/create', methods=['POST'])
def create():
    name = request.json.get('name')
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO budget (name) VALUES (%s)",(name,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Creating..."}), 200

if __name__ == '__main__':
    app.run(debug=True)
