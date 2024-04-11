from flask import Flask, render_template, request, redirect, jsonify, session, render_template_string
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
    if 'id' in session:
        name = str(session.get('username'))
        return render_template('dashboard.html', name = name)
    else :
        js = "<script> alert('Do Login First!'); window.location.href='login'; </script>"
        return js 


@app.route('/budgets')
def budgets():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM budgets order by bid desc")
    budgets = cursor.fetchall()
    cursor.close()
    return render_template('budgets.html', budgets = budgets)

@app.route('/open', methods=['POST'])
def open():
    name = request.json.get('name')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM budgets WHERE name = %s", (name,))
    budget = cursor.fetchone()
    cursor.close()

    if budget is None:
        return jsonify({'message': 'Budget not Found'}), 404
    else:
        return jsonify({'message': 'Opening Budget'}), 200
 
@app.route('/budget')
def budget():
    name = request.args.get('name')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM budgets WHERE name = %s", (name,))
    budget = cursor.fetchone()
    cursor.execute("SELECT * FROM records WHERE bid = %s and type = 'expense'", (budget[0],))
    expenses = cursor.fetchall()
    cursor.execute("SELECT * FROM records WHERE bid = %s and type = 'income'", (budget[0],))
    incomes = cursor.fetchall()
    
    if len(expenses) == 0 and len(incomes) != 0 :
        exp = 0
        cursor.execute("SELECT sum(amount) FROM records WHERE bid = %s and type = 'income'", (budget[0],))
        inc = cursor.fetchone()
        inc = int(inc[0])
        cursor.close()
        return render_template('budget.html', budget = budget, expenses = expenses, incomes = incomes, exp = exp, inc = inc )
        
    if len(incomes) == 0 and len(expenses) != 0:
        inc = 0
        cursor.execute("SELECT sum(amount) FROM records WHERE bid = %s and type = 'expense'", (budget[0],))
        exp = cursor.fetchone()
        exp = int(exp[0])
        cursor.close()
        return render_template('budget.html', budget = budget, expenses = expenses, incomes = incomes, exp = exp, inc = inc )
        
    if len(expenses) == 0 and len(incomes) == 0:
        return redirect('/record?name=%s' % name)
    
    else:
        cursor.execute("SELECT sum(amount) FROM records WHERE bid = %s and type = 'income'", (budget[0],))
        inc = cursor.fetchone()
        inc = int(inc[0])
        cursor.execute("SELECT sum(amount) FROM records WHERE bid = %s and type = 'expense'", (budget[0],))
        exp = cursor.fetchone()
        exp = int(exp[0])
        cursor.close()
        return render_template('budget.html', budget = budget, expenses = expenses, incomes = incomes, exp = exp, inc = inc )

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

@app.route('/newBudget')
def newBudget():
    return render_template('newBudget.html')

@app.route('/create', methods=['POST'])
def create():
    name = request.json.get('name')
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO budgets (name) VALUES (%s)",(name,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Creating..."}), 200

@app.route('/deleteBudget', methods=['POST'])
def deleteBudget():
    name = request.json.get('name')
    cursor = mysql.connection.cursor()
    cursor.execute("delete from budgets where name = %s",(name,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Creating..."}), 200

@app.route('/createBudget', methods=['POST'])
def createBudget():
    data = request.json
    print("data")
    print(data)
    name = data.get('name')
    amount = data.get('amount')

    if name is None or amount is None:
        return jsonify({'error': 'Name and amount are required parameters'}), 400

    print("name = " + name + " amount = "  + amount)
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO budgets (name, amount, remaining) VALUES (%s, %s, %s)", (name, amount, amount))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'Budget Created successfully'}), 200

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


@app.route('/record')
def record():
    return render_template('record.html')

@app.route('/newRecord', methods=['POST'])
def newRecord():
    data = request.form
    cursor = mysql.connection.cursor()
    
    cursor.execute("SELECT * FROM budgets WHERE name = %s", (data['budget'],))
    budget = cursor.fetchone()
    
    cursor.execute("INSERT INTO records (bid,type,name,amount) VALUES (%s, %s, %s, %s)",(budget[0],data['type'],data['name'],data['amount']))
    
    mysql.connection.commit()
    cursor.close()
    
    return jsonify({'message': 'Record added successfully'}), 200

@app.route('/deleteRecord')
def deleteRecord():
    rid = int(request.args.get('id'))
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM records WHERE rid = %s", (rid,))
    mysql.connection.commit()
    cursor.close()
    js = "<script> alert('Record Deleted Successfully !'); window.history.back(); </script>"
    return js

@app.route('/editRecord')
def editRecord():
    rid = int(request.args.get('id'))
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM records where rid = %s", (rid,))
    record = cursor.fetchone()
    cursor.close()
    if record :
        return render_template('edit.html', record = record)
    else:  
        alert_script = "<script>alert('Record Not Found!');  window.history.back();</script>"
    return render_template_string(alert_script)

@app.route('/edit', methods=['POST'])
def edit():
    name = request.form['name']
    amount = float(request.form['amount'])
    record_type = request.form['type']
    record_id = request.form['rid']

    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE records SET name=%s, amount=%s, type=%s WHERE rid=%s', (name, amount, record_type, record_id))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'Record Updated successfully'}), 200

@app.route('/budgetDelete')
def budgetDelete():
    name = request.args.get('name')
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM budgets WHERE name = %s", (name,))
    mysql.connection.commit()
    cursor.close()
    js = "<script> alert('Budget Deleted Successfully !'); window.history.back(); </script>"
    return js

@app.route('/profile')
def profile():
    id = session.get('id')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
    user = cursor.fetchone()
    cursor.close()
    if user :
        print(user)
        return render_template('profile.html', user = user)
    else:
        js = "<script> alert('Do Login First!'); window.location.href='login'; </script>"
        return js 

@app.route('/editProfile', methods=['POST'])
def editProfile():
    id = session.get('id')
    data = request.form
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE users SET name = %s, email = %s, mobile = %s WHERE id = %s",(data['name'], data['email'],data['mobile'], id))
    mysql.connection.commit()
    cursor.close()
    print("Profile updated")
    return jsonify({"message": "Updated"}), 200

@app.route('/change')
def change():
    return render_template('change.html')

@app.route('/changePassword', methods=['POST'])
def change_password():
    id = session.get('id')
    new_password = request.json.get('password')

    if not new_password:
        return jsonify({'error': 'New password is missing'}), 400
    
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_password, id,))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Password updated successfully'}), 200

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/login")

if __name__ == '__main__':
    app.run(debug=True)