from flask import Flask, render_template, request
from pull_city_data import plot_init_grid
from plot_city_results import plot_venues
from city_name_utils import get_city_state

app = Flask(__name__)


@app.route("/")
def home():
    return render_template('home.html', page="home")


@app.route("/about")
def about():
    chicago_city_grid, chicago_script, chicago_div = plot_init_grid('Chicago', 'illinois', 'chicago')
    return render_template('about.html', script=chicago_script, div=chicago_div, page="about")


@app.route("/plot_init")
def plot_init():
    city_grid, script, div = plot_init_grid('San Francisco', 'california', 'sf')
    return render_template('plot_init.html', script=script, div=div, page="init")


@app.route("/plot_full")
def plot_full():
    city_nickname = request.args.get('city')
    if not city_nickname:
        city_nickname = 'sf'
    city, state = get_city_state(city_nickname)
    script, div = plot_venues(city, city_nickname, state)
    return render_template('plot_full.html', script=script, div=div, page="full")


if __name__ == '__main__':
    # app.run(port=33507)
    app.run(debug=True)
