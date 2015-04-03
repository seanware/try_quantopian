#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# try_quantopian.py
import os
import pg8000
import urlparse
from flask import Flask, g, render_template, request

app = Flask(__name__)
urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

def connect_db():
	return pg8000.connect(
			database=url.path[1:],
			host=url.hostname,
			post=url.port,
			user=url.username,
			password=url.password,
			ssl=True)
			

def get_db():
  """Set the flask 'g' value for _database, and return it."""
  db = getattr(g, "_database", None)
  if db is None:
	  db = g._database = connect_db()
  return db


@app.teardown_appcontext
def close_connection(exception):
  """Set the flask 'g' value for _database, and return it."""
  db = getattr(g, '_database', None)
  if db is not None:
      db.close()
      g._database = None      
      
      

def db_select(query, args=None, columns=None):
  """Return the result of a select query as an array of dictionaries.

  Each dictionary has keys taken from the 'columns' argument, or else
  'col0' ... 'colN-1' for the N columns returned.

  If there is an error with the query, return None.

  Keyword arguments
  args -- passed to pg8000.cursor.execute() for a secure
  parameterized query.
  We use the default format: SELECT * FROM TABLE WHERE col1 = '%s'
  """
  cur = db_query(query, args=args)
  if cur is None:
	  return None
  try:
	  results = cur.fetchall()
  except pg8000.ProgrammingError as e:
	get_db().rollback()
	cur.close()
	return None
  cur.close()
  if len(results) == 0:
	  return None
  elif len(results[0]) > len(columns):
	  columns = list(columns) + ["col%d" % i for i in range(len(columns),len(results))]
  elif len(results[0]) < len(columns):
	  columns = columns[0:len(results[0])]

  return [dict(zip(columns, result)) for result in results]


def db_select_one(query, args=None, columns=None):
  """Return the one-row result of a select query as a dictionary.

  If there are more than one rows, return only the contents of the first one.
  If there are no rows, return None.
  """
  rows = db_select(query, args=args, columns=columns)
  if rows is None or len(rows) == 0:
	  return {}
  return rows[0]
    
  
def db_query(query, args=None, commit=False):

  """Perform a query returning the database cursor if success else None.

  Use db_select for SELECT queries.
  Wrap the query with a try/except, catch the error, and return
  False if the query fails.
  """
  db = get_db()
  cur = db.cursor()
  try:
	  cur.execute(query, args)
	  if commit:
		  db.commit()
  except pg8000.ProgrammingError as e:
	  return None
  return cur

			
@app.route("/")
def index():
	"""Index page."""
	apple_march_2005 = db_select("""
		SELECT dt, aapl FROM spread
		WHERE dt BETWEEN %s AND %s;
	""",
		args=('2003-03-05', '2003-03-08'), columns=('date', 'aapl'))
	return render_template('index.html', stock=apple_march_2005)


@app.route("/graph")
def linechart():
	stock_data = []
	if 'stocks' in request.form:
		stocks = request.form['stocks']
		stocks = [s.lower() for s in stock.strip().split(",")]
	else:
		stocks = ['aapl', 'goog', 'yhoo']
	 
	query = """
		SELECT EXTRACT ( EPOCH FROM dt), {} FROM close
		WHERE dt between '2001-01-01' AND '2001-12-31';
		
	
	for s in stocks:
		data = db_select(query.format(s), columns=('x','y'))
		stock_data.append(dict(name=s, data=data, color="palette.color()"))
	return render_template('graph.html', stock_data=stock_data)


if __name__ == "__main__":
    app.run(debug=True)
