import flask
import main

app = flask.Flask(__name__)

@app.route('/')
def main_page():
    return flask.render_template("main.html")

@app.route('/less', methods=['POST'])
def less_page():
    query = flask.request.form['query']
    results = main.the_output_is_less_than_price(query)
    return flask.render_template("index.html", name="Товары, цена которых меньше: " + query + " рублей", result=results)

@app.route('/all')
def all_page():
    results = main.print_all()
    return flask.render_template("index.html", name="Все товары", result=results)

@app.route('/search', methods=['POST'])
def search():
    query = flask.request.form['query']
    results = main.search_func(query)
    return flask.render_template('index.html', name="Результаты поиска по запросу: " + query, result=results)

@app.route('/keywords', methods=['POST'])
def keywords_page():
    keywords = flask.request.form['keywords']
    results = main.find_items_with_keywords(keywords)
    return flask.render_template('index.html', name="Товары по ключевым словам: " + keywords, result=results)

if __name__ == "__main__":
    app.run(debug=True)
