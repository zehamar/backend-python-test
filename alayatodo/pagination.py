from flask import (
    g,
    session
    )
    
import pdb
todo_per_page = 2

class Pagination:
    def page_count(self):
        cur = g.db.execute("SELECT COUNT(*) FROM todos WHERE user_id = ?", [session['user']['id']])
        vect = cur.fetchone()
        return int(round(vect[0] / todo_per_page) + 1)

    def page(self, number):
        cur = g.db.execute("SELECT * FROM todos WHERE user_id = ? LIMIT ? OFFSET ?", [session['user']['id'], todo_per_page, (number-1)*todo_per_page])
        return cur.fetchall() 

db = Pagination()
