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
        id = session.get("id")
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM accounts where id = %s", (id,))  
        account = cursor.fetchone()
        
        cursor.execute("SELECT * FROM budgets where id = %s", (id,))  
        budget = cursor.fetchone()
        
        cursor.execute("SELECT * FROM goals where id = %s", (id,))  
        goal = cursor.fetchone()    
        if goal[3] > 0:
            percentage = (goal[4] / goal[3]) * 100
            percentage = int(percentage)
        else:
            percentage = 0    
        
        cursor.execute("SELECT * FROM records where id = %s order by rid DESC", (id,))  
        record = cursor.fetchone()        
        
        cursor.execute("SELECT * FROM investments where id = %s", (id,))  
        investment = cursor.fetchone()        
        
        name = str(session.get('username'))
        return render_template('dashboard.html', name = name, account = account, budget = budget, goal = goal, record = record, investment = investment, perc = percentage)
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
    id = session.get("id")
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM goals where id = %s", (id,))
    goals = cursor.fetchall()
    print(goals)
    cursor.close()
    goals_with_percentage = []
    
    for goal in goals:

        if goal[3] > 0:
            percentage = (goal[4] / goal[3]) * 100
            percentage = int(percentage)
        else:
            percentage = 0

        goals_with_percentage.append({
            'id': goal[0],
            'name': goal[1],
            'amount': goal[3],
            'achieved': goal[4],
            'percentage': percentage
        })

    return render_template('goals.html', goals=goals_with_percentage)

@app.route('/editGoal')
def editGoal():
    gid = int(request.args.get('gid'))
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM goals where gid = %s", (gid,))
    goal = cursor.fetchone()
    cursor.close()
    if goal:
        return render_template('editGoal.html', goal = goal)
    else:  
        alert_script = "<script>alert('Goal Not Found!');  window.history.back();</script>"
        return render_template_string(alert_script)

@app.route('/goalEdit', methods=['POST'])
def goalEdit():
    data = request.json
    name = data.get('name')
    amount = data.get('amount')
    achieved = data.get('achieved')
    gid = data.get('gid')


    if name is None or amount is None:
        return jsonify({'error': 'Name and amount are required parameters'}), 400

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Amount must be a number'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM goals WHERE name = %s", (name,))
    goal = cursor.fetchone()

    if goal is None:
        return jsonify({'error': 'Goal does not exist'}), 404

    new_amount = float(goal[4]) + amount 

    cursor.execute("UPDATE goals SET name = %s, amount = %s, achieved = %s WHERE gid = %s", (name, amount, achieved, gid))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": f"Amount updated for budget '{name}' to {new_amount}"}), 200

@app.route('/investments')
def investments():
    id = session.get("id")
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM investments where id = %s", (id,))
    investments = cursor.fetchall()
    cursor.close()
    return render_template('investments.html', investments = investments)

@app.route('/investment')
def investment():
    return render_template('investment.html')

@app.route('/transactions')
def transactions():
    id = session.get("id")
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM records WHERE id = %s ORDER BY rid DESC", (id,))
    transactions = cursor.fetchall()
    cursor.close()
    return render_template('transactions.html', transactions = transactions)

@app.route('/transaction')
def transaction():
    return render_template('transaction.html')

@app.route('/newBudget')
def newBudget():
    return render_template('newBudget.html')

@app.route('/create', methods=['POST'])
def create():
    name = request.json.get('name')
    print("creating name =", name)
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
    id = session.get("id")
    cursor.execute("SELECT * FROM budgets WHERE name = %s", (data['budget'],))
    budget = cursor.fetchone()
    
    cursor.execute("INSERT INTO records (bid,type,name,amount,id) VALUES (%s, %s, %s, %s,%s)",(budget[0],data['type'],data['name'],data['amount'], id))

    cursor.execute("SELECT remaining FROM budgets WHERE bid = %s", (budget[0],))
    remaining_amount = cursor.fetchone()[0]
    remaining_amount = float(remaining_amount)
        
    if data['type'] == 'expense':
        new_remaining_amount = remaining_amount - float(data['amount'])
    
    else:
        new_remaining_amount = remaining_amount + float(data['amount'])

    cursor.execute("UPDATE budgets SET remaining = %s WHERE bid = %s", (new_remaining_amount, budget[0]))
    mysql.connection.commit()

        
    cursor.close()
    return jsonify({'message': 'Record added successfully'}), 200

@app.route('/deleteRecord')
def deleteRecord():
    rid = int(request.args.get('id'))
    cursor = mysql.connection.cursor()
    
    cursor.execute("SELECT bid FROM records WHERE rid = %s", (rid,))
    rec = cursor.fetchone()
    bid = rec[0]
    
    cursor.execute("DELETE FROM records WHERE rid = %s", (rid,))
    mysql.connection.commit()
    
    cursor.execute("SELECT sum(amount) FROM records WHERE bid = %s and type = 'expense'", (bid,))
    exp = cursor.fetchone()
    exp = exp[0]
    
    cursor.execute("SELECT sum(amount) FROM records WHERE bid = %s and type = 'income'", (bid,))
    inc = cursor.fetchone()
    inc = inc[0]
    
    remaining = inc - exp    
    
    cursor.execute("update budgets set remaining = %s where bid = %s", (remaining, bid,))
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
    bid = request.form['bid']

    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE records SET name=%s, amount=%s, type=%s WHERE rid=%s', (name, amount, record_type, record_id))
    mysql.connection.commit()
    
    cursor.execute("SELECT sum(amount) FROM records WHERE bid = %s and type = 'expense'", (bid,))
    exp = cursor.fetchone()
    exp = exp[0]
    
    cursor.execute("SELECT sum(amount) FROM records WHERE bid = %s and type = 'income'", (bid,))
    inc = cursor.fetchone()
    inc = inc[0]
    
    remaining = inc - exp    
    
    cursor.execute("update budgets set remaining = %s where bid = %s", (remaining, bid,))
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

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/accounts')
def accounts():
    id = session.get("id")
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM accounts where id = %s", (id,))
    accounts = cursor.fetchall()
    cursor.close()
    return render_template('accounts.html', accounts = accounts)

@app.route('/setAmount', methods=['POST'])
def setAmount():
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

    cursor.execute("UPDATE budgets SET amount = %s WHERE name = %s", (amount, name))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": f"Amount updated for budget '{name}' to {amount}"}), 200

@app.route('/getAmount')
def getAmount():
    name = request.args.get('name')
    if name is None:
        return jsonify({'error': 'Name is required parameters'}), 400
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM budgets WHERE name = %s", (name,))
    budget = cursor.fetchone()
    if budget is None:
        return jsonify({'error': 'Budget does not exist'}), 404
    amount = budget[2] 
    return jsonify({"amount": amount}), 200

@app.route('/link', methods=['POST'])
def link():
    data = request.form
    cursor = mysql.connection.cursor()
    
    cursor.execute("INSERT INTO `accounts`(`number`, `id`, `name`, `balance`, `type`) VALUES (%s, %s, %s, %s, %s)",(data['number'],session.get("id"),data["bank"],data['amount'],data['type'],))
    
    mysql.connection.commit()
    cursor.close()
    
    return jsonify({'message': 'Account Linked successfully'}), 200

@app.route('/unlink')
def unlink():
    id = session.get('id')
    number = request.args.get('number')
    
    if number:  
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM accounts WHERE number = %s and id = %s", (number, id,))
        mysql.connection.commit()
        cursor.close()
        js = "<script> alert('Account Unlinked Successfully !'); window.location.href='accounts'; </script>"
        return js
    
    name = request.args.get('name')
    if name: 
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM accounts WHERE name = %s and id = %s", (name,id,))
        mysql.connection.commit()
        cursor.close()
        js = "<script> alert('Account Unlinked Successfully !'); window.location.href='accounts'; </script>"
        return js

@app.route('/Stocks')
def Stocks():
    return render_template("stocks.html")

@app.route('/MF')
def MF():
    return render_template("MF.html")

@app.route('/FD')
def FD():
    return render_template("FD.html")

@app.route('/chart')
def chart():
    return render_template("chart.html")

@app.route('/newGoal')
def newGoal():
    return render_template("newGoal.html")

@app.route('/createGoal', methods=['POST'])
def createGoal():
    data = request.json
    name = data.get('name')
    amount = data.get('amount')
    id = session.get('id')  

    if name is None or amount is None:
        return jsonify({'error': 'Name and amount are required parameters'}), 404

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO goals (name, amount, achieved, id) VALUES (%s, %s, %s,%s)", (name, amount, 0, id,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'Goal Created successfully'}), 200

@app.route('/deleteGoal', methods=['POST'])
def deleteGoal():
    data = request.json
    name = data.get('name')
    
    if name is None:
        return jsonify({'error': 'Name is required parameters'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("delete from goals where name = %s",(name,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'Goal Created successfully'}), 200

@app.route('/addGoal', methods=['POST'])
def addGoal():
    data = request.json
    name = data.get('name')
    amount = data.get('amount')
    print("goal")
    print(name)
    print(amount)

    if name is None or amount is None:
        return jsonify({'error': 'Name and amount are required parameters'}), 400

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Amount must be a number'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM goals WHERE name = %s", (name,))
    goal = cursor.fetchone()

    if goal is None:
        return jsonify({'error': 'Goal does not exist'}), 404

    new_amount = float(goal[4]) + amount 

    cursor.execute("UPDATE goals SET achieved = %s WHERE name = %s", (new_amount, name))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": f"Amount updated for budget '{name}' to {new_amount}"}), 200

@app.route('/goalDelete')
def goalDelete():
    gid = request.args.get('gid')
    cursor = mysql.connection.cursor()
    cursor.execute("delete from goals where gid = %s",(gid,))
    mysql.connection.commit()
    cursor.close()
    alert_script = "<script>alert('Goal Deleted!');  window.history.back();</script>"
    return render_template_string(alert_script)

@app.route('/balance')
def balance():
    cursor = mysql.connection.cursor()
    id = session.get("id")

    try:
        cursor.execute("SELECT * FROM accounts where id = %s", (id,))
        accounts = cursor.fetchall()

        if not accounts:
            return jsonify([]) 

        account_details = []
        for account in accounts:
            account_details.append({
                'id': account[0],
                'name': account[1],
                'balance': account[2],
                'account_type': account[3]
            })

        return jsonify(account_details)

    except Exception as e:
        cursor.close()
        return str(e), 500  

if __name__ == '__main__':
    app.run(debug=True)