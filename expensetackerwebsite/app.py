from flask import Flask,request,redirect,session,url_for
from flask import render_template
import mysql.connector
from mysql.connector import Error
import pandas as pd
import io
from flask import send_file


app = Flask(__name__)

app.secret_key = "jai mata di"

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="ROOT",
            database="finance"
       )
        return conn
    except Error as e:
        print("connection failed : ", e)
        return None

    
conn = get_connection()
if conn:
    cursor = conn.cursor()                                                                                                                                                                            
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS USER (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        password VARCHAR(255),
        contact_no VARCHAR( 15),
        created_at DATE
    )
    """)    

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS INCOME (
        income_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        source VARCHAR(100),
        amount DECIMAL(10,2),
        date DATE,
        FOREIGN KEY (user_id) REFERENCES USER(user_id)
    )
    """)    

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS EXPENSE (
        expense_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        category VARCHAR(100),
        amount DECIMAL(10,2),
        date DATE,
        FOREIGN KEY (user_id) REFERENCES USER(user_id)
    )
    """)  

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(20),          -- 'income' या 'expense'
    category VARCHAR(50),
    amount DECIMAL(10,2),
    date DATE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS CATEGORY (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    category_type ENUM('income','expense') NOT NULL,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES USER(user_id),
    UNIQUE(category_name, category_type)
    )
    """)
    

# ---------------- login ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('Email')
        password = request.form.get('Password')

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM USER WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            print("Session after login:", session)
            return redirect(url_for('dashboard'))
        else:
            return render_template("login.html", message="Invalid email or password")

    return render_template("login.html")


# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('FullNAME')
        email = request.form.get('Email')
        password = request.form.get('Password')

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO USER (name, email, password, created_at) VALUES (%s, %s, %s, CURDATE())",
                (name, email, password)
            )
            conn.commit()
            message = "Signup successful! Please login."
        except Exception as e:
            message = f"Error: {e}"
        cursor.close()
        conn.close()
        return render_template("signup.html", message=message)

    return render_template("signup.html")

# ---------------- dashboard ----------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT SUM(amount) AS total_income FROM INCOME WHERE user_id=%s", (session['user_id'],))
    total_income = cursor.fetchone()["total_income"] or 0

    cursor.execute("SELECT SUM(amount) AS total_expense FROM EXPENSE WHERE user_id=%s", (session['user_id'],))
    total_expense = cursor.fetchone()["total_expense"] or 0

    total_balance = total_income - total_expense

    cursor.execute("""
        SELECT type, category, amount, date 
        FROM transactions 
        WHERE user_id=%s 
        ORDER BY date DESC LIMIT 7
    """, (session['user_id'],))
    recent_txn = cursor.fetchall()

    user = cursor.fetchone()
    if user:
        session['user_id'] = user['user_id']
        session['name'] = user['name']
        

    

    cursor.close()
    conn.close()

    return render_template("index.html",
                           total_income=total_income,
                           total_expense=total_expense,
                           total_balance=total_balance,
                           recent_txn=recent_txn,
                           active="dashboard",
                           name=session['name'])

# ---------------- income ----------------
@app.route('/income', methods=['GET', 'POST'])
def income():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    message = None
    # Fetch only income categories
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT category_name FROM CATEGORY WHERE category_type='income' AND user_id=%s",
                   (session['user_id'],))
    categories = cursor.fetchall()
    cursor.close()
    conn.close()

    if request.method == 'POST':
        if request.form.get('delete_id'):
            delete_id = request.form['delete_id']
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM INCOME WHERE income_id=%s AND user_id=%s",
                           (delete_id, session['user_id']))
            conn.commit()
            cursor.close()
            conn.close()
            message = "Income deleted successfully!"
        elif request.form.get('source') and request.form.get('amount') and request.form.get('date'):
            source = request.form['source']
            amount = request.form['amount']
            date = request.form['date']
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT IGNORE INTO CATEGORY (category_name, category_type, user_id) VALUES (%s, %s, %s)", (source, 'income', session['user_id']))
            
                cursor.execute("INSERT INTO INCOME (user_id, source, amount, date) VALUES (%s, %s, %s, %s)",
                           (session['user_id'], source, amount, date))
           
                cursor.execute("INSERT INTO transactions (user_id, type, category, amount, date) VALUES (%s, %s, %s, %s, %s)",
                           (session['user_id'], "income", source, amount, date))
            
            
            # cursor.execute("SELECT income_id, source, amount, date FROM INCOME WHERE user_id=%s", (session['user_id'],))
                conn.commit()
                message = "Income added successfully!"
            except Exception as e:
                 message = f"Error: {e}"
            finally:
                cursor.close()
                conn.close()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT income_id, source, amount, date FROM INCOME WHERE user_id=%s ORDER BY date DESC LIMIT 5",
                   (session['user_id'],))
    incomes = cursor.fetchall()
    cursor.close()
    conn.close()
    chart_labels = [row['date'].strftime("%Y-%m-%d") for row in incomes][::-1]
    chart_values = [float(row['amount']) for row in incomes][::-1]
    return render_template("income.html",
                            categories=categories,
                            message=message,
                            incomes=incomes,
                            chart_labels=chart_labels,
                            chart_values=chart_values,
                            active="income")

        
       


@app.route('/expense', methods=['GET', 'POST'])
def expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    message = None

    # Fetch categories for dropdown
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT category_name FROM CATEGORY WHERE category_type='expense' AND user_id=%s",
                   (session['user_id'],))
    categories = cursor.fetchall()
    cursor.close()
    conn.close()


        # category = request.form.get('category') 
        # amount = request.form.get('amount')
        # date = request.form.get('date')

        # conn = get_connection()
        # cursor = conn.cursor()

    if request.method == 'POST':
        if request.form.get('delete_id'):
            delete_id = request.form['delete_id']
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM EXPENSE WHERE expense_id=%s AND user_id=%s",
                           (delete_id, session['user_id']))
            conn.commit()
            cursor.close()
            conn.close()
            message = "Expense deleted successfully!"
        # ✅ Insert case (only if category, amount, date present)

        elif request.form.get('category') and request.form.get('amount') and request.form.get('date'):
            category = request.form['category']
            amount = request.form['amount']
            date = request.form['date']
            conn = get_connection()
            cursor = conn.cursor()
            try:
                
                cursor.execute("INSERT IGNORE INTO CATEGORY (category_name, category_type, user_id) VALUES (%s, %s, %s)", (category, 'expense', session['user_id']))
    
              
                cursor.execute("INSERT INTO EXPENSE (user_id, category, amount, date) VALUES (%s, %s, %s, %s)",
                               (session['user_id'], category, amount, date))
    
               
                cursor.execute("INSERT INTO transactions (user_id, type, category, amount, date) VALUES (%s, %s, %s, %s, %s)",
                               (session['user_id'], "expense", category, amount, date))
    
                conn.commit()
                message = "Expense added successfully!"
            except Exception as e:
                message = f"Error: {e}"
            finally:
                cursor.close()
                conn.close()


    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT expense_id, category, amount, date FROM EXPENSE WHERE user_id=%s ORDER BY date DESC LIMIT 5",
                   (session['user_id'],))
    expenses = cursor.fetchall()
    cursor.close()
    conn.close()

    chart_labels = [row['date'].strftime("%Y-%m-%d") for row in expenses][::-1]
    chart_values = [float(row['amount']) for row in expenses][::-1]

    return render_template("expense.html",
                           categories=categories,
                           message=message,
                           expenses=expenses,
                           chart_labels=chart_labels,
                           chart_values=chart_values,
                           active="expense")
                



@app.route("/generate_report", methods=['GET' ,'post'])
def generate_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT source, amount, date FROM INCOME WHERE user_id=%s", (session['user_id'],))
    incomes = cursor.fetchall()
    df_income = pd.DataFrame(incomes)


    cursor.execute("SELECT category, amount, date FROM EXPENSE WHERE user_id=%s", (session['user_id'],))
    expenses = cursor.fetchall()
    df_expense = pd.DataFrame(expenses)

    cursor.close()
    conn.close()

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_income.to_excel(writer, index=False, sheet_name="Income Report")
        df_expense.to_excel(writer, index=False, sheet_name="Expense Report")

    output.seek(0)

    return send_file(output,
                     as_attachment=True,
                     download_name="financial_report.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
  
    cursor.execute("SELECT name, email, contact_no, created_at, password FROM USER WHERE user_id=%s", (session['user_id'],))
    user = cursor.fetchone()

    message = None
    
    if request.method == 'POST':
        if 'update_contact' in request.form:
            new_contact = request.form.get('contact_no')
            cursor.execute("UPDATE USER SET contact_no=%s WHERE user_id=%s", (new_contact, session['user_id']))
            conn.commit()
            message = "Contact updated successfully!"

        elif 'change_password' in request.form:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if user['password'] != current_password:
                message = "Current password is incorrect!"
            elif new_password != confirm_password:
                message = "New passwords do not match!"
            else:
                cursor.execute("UPDATE USER SET password=%s WHERE user_id=%s", (new_password, session['user_id']))
                conn.commit()
                message = "Password changed successfully!"

        
        cursor.execute("SELECT name, email, contact_no, created_at, password FROM USER WHERE user_id=%s", (session['user_id'],))
        user = cursor.fetchone()

    cursor.close()
    conn.close()


    return render_template("profile.html", user=user, message=message, active="profile")





if __name__ == '__main__':
    app.run(debug=True)
