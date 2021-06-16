from flask import Flask, render_template
from pull_city_data import plot_init_grid
from plot_city_results import plot_venues

app = Flask(__name__)


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/plot_init")
def plot_init():
    city_grid, script, div = plot_init_grid('San Francisco', 'california', 'sf')
    return render_template('plot_init.html', script=script, div=div)


@app.route("/plot_full")
def plot_full():
    script, div = plot_venues('San Francisco', 'sf', 'california')
    return render_template('plot_full.html', script=script, div=div)


if __name__ == '__main__':
    # app.run(port=33507)
    app.run(debug=True)
