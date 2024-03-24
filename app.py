from flask import Flask, render_template, request, redirect, jsonify, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app = Flask(__name__, static_folder='templates/static')

app.config['SECRET_KEY'] = 'kalash' 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'voice_finance'
app.config['MYSQL_HOST'] = 'localhost'

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('voice.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s and password = %s", (email, password))
        result = cur.fetchone()
        cur.close()

        if result:
            session['id'] = result[0]
            session['username'] = result[1]
            session['email'] = result[2]
            session['mobile'] = result[4]
            return redirect('/dashboard') 
        else:
            return "Credentials Incorrect"
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
    name = str(session.get('username'))
    return render_template('dashboard.html', name = name)

@app.route('/budgets')
def budgets():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM budgets order by bid desc")
    budgets = cursor.fetchall()
    cursor.close()
    print(budgets)
    return render_template('budgets.html', budgets = budgets)

@app.route('/budget')
def budget():
    return render_template('budget.html')

@app.route('/goals')
def goals():
    return render_template('goals.html')

@app.route('/goal')
def goal():
    return render_template('goal.html')

@app.route('/investments')
def investments():
    return render_template('investments.html')

@app.route('/investment')
def investment():
    return render_template('investment.html')

@app.route('/transactions')
def transactions():
    return render_template('transactions.html')

@app.route('/transaction')
def transaction():
    return render_template('transaction.html')

@app.route('/create', methods=['POST'])
def create():
    name = request.json.get('name')
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO budgets (name) VALUES (%s)",(name,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Creating..."}), 200

@app.route('/createBudget', methods=['POST'])
def createBudget():
    data = request.json
    name = data.get('name')
    amount = data.get('amount')

    if name is None or amount is None:
        return jsonify({'error': 'Name and amount are required parameters'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO budgets (name, amount, remaining) VALUES (%s, %s, %s)", (name, amount, amount))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": f"Creating budget '{name}' with amount {amount}"}), 200

@app.route('/addAmount', methods=['POST'])
def addAmount():
    data = request.json
    name = data.get('name')
    amount = data.get('amount')

    if name is None or amount is None:
        return jsonify({'error': 'Name and amount are required parameters'}), 400

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Amount must be a number'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM budgets WHERE name = %s", (name,))
    budget = cursor.fetchone()

    if budget is None:
        return jsonify({'error': 'Budget does not exist'}), 404

    new_amount = float(budget[2]) + amount 

    cursor.execute("UPDATE budgets SET amount = %s WHERE name = %s", (new_amount, name))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": f"Amount updated for budget '{name}' to {new_amount}"}), 200

@app.route('/deductAmount', methods=['POST'])
def deductAmount():
    data = request.json
    name = data.get('name')
    amount = data.get('amount')

    if name is None or amount is None:
        return jsonify({'error': 'Name and amount are required parameters'}), 400

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Amount must be a number'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM budgets WHERE name = %s", (name,))
    budget = cursor.fetchone()

    if budget is None:
        return jsonify({'error': 'Budget does not exist'}), 404

    new_amount = float(budget[2]) - amount 

    cursor.execute("UPDATE budgets SET amount = %s WHERE name = %s", (new_amount, name))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": f"Amount updated for budget '{name}' to {new_amount}"}), 200

if __name__ == '__main__':
    app.run(debug=True)