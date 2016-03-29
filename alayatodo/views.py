from alayatodo import app
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    flash,
    json
    )

# Check if no special characters, no long string
def username_ok(string):
    if ( (string.isalnum()) and (len(string) < 64 ) ) :
       return True
    else:
       return False


# Truncate long text for displaying
def trunc_string(max_len, string):
    if len(string) > max_len:
       trunc_string = string[0:max_len-3]+"..."
    else:
       trunc_string = string
    return trunc_string



@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')
    if username_ok(username): 
       sql = "SELECT * FROM users WHERE username = '%s' AND password = '%s'";
       cur = g.db.execute(sql % (username, password))
       user = cur.fetchone()
       if user:
           session['user'] = dict(user)
           session['logged_in'] = True
           return redirect('/todo')
    else: 
       flash("Wrong username format")
    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s'" % id)
    todo = cur.fetchone()
    return render_template('todo.html', todo=todo)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')
    cur = g.db.execute("SELECT * FROM todos")
    todos = cur.fetchall()
    return render_template('todos.html', todos=todos)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')
    if not request.form.get('description', ''):
        flash("Please, enter description.")
    else:
        g.db.execute(	
        "INSERT INTO todos (user_id, description) VALUES ('%s', '%s')"
        % (session['user']['id'], request.form.get('description', ''))
        )
        g.db.commit()
        descrip = trunc_string(32,request.form.get('description')) # string len to display : 32 char
        flash('Description "%s" is successfully added, by User id : %s' % (descrip, session['user']['id']))
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')    
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s'" % id)
    todo = cur.fetchone()
    descrip = trunc_string(32, todo['description']) # string len to display : 32 char
    flash("Task #%s [User id : %s, Description : \"%s\"] has been deleted" % (id,todo['user_id'],descrip))
    g.db.execute("DELETE FROM todos WHERE id ='%s'" % id)
    g.db.commit()
    return redirect('/todo')

@app.route('/todo/<id>/json', methods=['GET'])
def todo_json(id):
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s'" % id)
    todo = cur.fetchone()
    todo_dict = {'Id' : todo['id'], 'user_id': todo['user_id'],'description': todo['description']}
    return json.dumps(todo_dict)
    
    
    
@app.route('/todo/<id>/complete', methods=['POST'])
def todo_complete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    cur = g.db.execute("SELECT status FROM todos WHERE id = '%s'" % id)
    todo = cur.fetchone()
    if todo['status'] == 1:
       g.db.execute("UPDATE todos SET status = 0 WHERE id = '%s'" % id)
    else:
       g.db.execute("UPDATE todos SET status = 1 WHERE id = '%s'" % id)
    g.db.commit()    
    return redirect('/todo')
