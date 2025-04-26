from flask import Flask, render_template, request
import psycopg2

app = Flask(__name__)

# Параметры подключения к PostgreSQL
DB_CONFIG = {
    'dbname': 'mydatabase',
    'user': 'myuser',
    'password': 'mypassword',
    'host': 'localhost',
    'port': 5432
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def search_pages(query):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, snippet
        FROM pages
        WHERE search_vector @@ plainto_tsquery('russian', %s)
        ORDER BY ts_rank(search_vector, plainto_tsquery('russian', %s)) DESC;
    """, (query, query))
    results = cursor.fetchall()
    conn.close()
    return results

def get_page_by_id(page_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pages WHERE id = %s', (page_id,))
    page = cursor.fetchone()
    conn.close()
    return page

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('query')
    if query:
        results = search_pages(query)
        return render_template('results.html', results=results, query=query)
    return "Введите поисковый запрос", 400

@app.route('/page/<int:page_id>')
def show_page(page_id):
    page = get_page_by_id(page_id)
    if page:
        return render_template('page.html', title=page[1], content=page[2])
    return "Страница не найдена", 404

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
