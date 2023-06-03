from flask import Flask, render_template, g, redirect, request, flash
# import os
import sqlite3
import datetime
app = Flask(__name__)
app.secret_key = str(1234567890)
class DatabaseManager:
    def __init__(self, database):
        self.database = database

    def __enter__(self): #initializes and acquires resources
        self.db = sqlite3.connect(self.database)
        self.cursor = self.db.cursor()
        return self.db, self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb): #cleans up resources
        self.db.commit()
        self.cursor.close()

def get_db():
    if 'db' not in g:
        g.db = DatabaseManager('budgetcon_ayadb.sqlite3')
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.__exit__(exception, None, None)
        
@app.route('/')
def home():
    return render_template('landpage.html')
## redirectings
@app.route('/AddUserbtn_clicked')
def handlecreatebtnclicked():
    return redirect('/create')

@app.route('/Deletebtn_clicked')
def handledeletebtnclicked():
    return redirect('/delete')

@app.route('/create', methods=['POST', 'GET'])
def createUser():
    if request.method == 'POST':
        print(f'Data recieved from{request.form}')
        submit()
        # return redirect('/')
    return render_template('templat.html')

@app.route('/delete', methods=['POST', 'GET', 'DELETE'])
def DeleteUser():
    return render_template('delete_user.html')     
    
def excute_query(query, values):
    with get_db() as (db, cursor):
        cursor.execute(query, values)
        db.commit()
        return 'operation done successfully'
def search_element(table, column, element):
    try:
        with get_db() as (db, cursor):
            query = f"SELECT COUNT(*) FROM {table} WHERE {column} = ?"
            cursor.execute(query, (element,))
            count = cursor.fetchone()[0]
            if count > 0:
                return True  # Element exists
            else:
                return False  # Element does not exist

    except Exception as e:
        return f'An error occurred: {str(e)}'

@app.route('/submit', methods=['POST', 'GET'])
def submit():
    try:
        month = request.form.get('month')
        name = request.form.get('name')
        income = request.form.get('income')
        print(month)
        if all([month, name, income]):
            query_add = ('INSERT INTO Budget (month, name, income) VALUES (?, ?, ?)')
            values_add=(month, name, income)
            excute_query(query_add, values_add)
            success = 'Data saved successfully'
            timestamp = datetime.datetime.now()
            creation_time = timestamp.strftime('month %b day %d, %H:%M')
            return render_template('templat.html', success = success, creation_time=creation_time)
        else :
            return render_template('templat.html', success = 'error')
             
    except Exception as e:
        return f'An error occurred: {str(e)}'
    
@app.route('/DeleteUser', methods=['POST'])
def delete_user():
    thename = request.form.get('inputText')
    print(request.form)
    if search_element('Budget', 'name', thename):
        query_delete = ("DELETE FROM Budget WHERE name=?")
        values_delete = (thename,)
        excute_query(query_delete, values_delete)
        flash('Name has been deleted successfully', 'success')
    else:
        flash('Name not found', 'error')
    return redirect('/delete')

if __name__ == '__main__':
    app.run()