from pull_city_data import define_city_geometry, geometry2patch
from coordinate_utils import gen_wgs2merc, find_avg_city_mile
import json
from bokeh.io import output_file, save
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.embed import components
from bokeh.models import ColumnDataSource, Slider, CheckboxGroup, CustomJS, CDSView, HoverTool
from bokeh.models.filters import CustomJSFilter
from bokeh.tile_providers import get_provider, Vendors


def make_dataset(city_venues_results, top_cats):

    unique_ids = set()

    city_data = {
        'latitudes': [],
        'longitudes': [],
        'x_coords': [],
        'y_coords': [],
        'categories': [],
        'names': []
    }

    for venue in city_venues_results:
        items_list = venue['response']['groups'][0]['items']
        for item in items_list:
            item_id = item['venue']['id']
            item_category = item['venue']['categories'][0]['name']
            if item_id in unique_ids or item_category not in top_cats:
                continue
            else:
                unique_ids.add(item_id)
                city_data['categories'].append(item_category)
                city_data['latitudes'].append(item['venue']['location']['lat'])
                city_data['longitudes'].append(item['venue']['location']['lng'])
                city_data['names'].append(item['venue']['name'])

    wgs2merc = gen_wgs2merc()
    for lat, lon in zip(city_data['latitudes'], city_data['longitudes']):
        x, y = wgs2merc(lat, lon)
        city_data['x_coords'].append(x)
        city_data['y_coords'].append(y)

    return ColumnDataSource(city_data)


def style(p):
    p.title.align = 'center'
    p.title.text_font_size = '14pt'

    p.xaxis.axis_label_text_font_style = 'bold'
    p.yaxis.axis_label_text_font_style = 'bold'

    return p


def make_plot(city, state, buffer_perc=0.0008):
    city_geometry = define_city_geometry(city, state)
    geometry_data = geometry2patch(city_geometry)

    min_x = min([min(x) for x in geometry_data['xs']])
    max_x = max([max(x) for x in geometry_data['xs']])
    min_y = min([min(y) for y in geometry_data['ys']])
    max_y = max([max(y) for y in geometry_data['ys']])

    p = figure(x_axis_type="mercator", y_axis_type="mercator",
               x_range=(min_x * (1 - buffer_perc), max_x * (1 + buffer_perc)),
               y_range=(min_y * (1 - buffer_perc), max_y * (1 + buffer_perc)),
               title="{0} Food Venues".format(city),
               x_axis_label='Longitude', y_axis_label='Latitude')

    p.multi_polygons(xs=[[geometry_data['xs']]],
                     ys=[[geometry_data['ys']]],
                     alpha=0.7, color='gray')

    tile_provider = get_provider(Vendors.OSM)
    p.add_tile(tile_provider)

    hover = HoverTool(names=["annulus"], tooltips=[('Name', '@names')])
    p.add_tools(hover)

    p = style(p)
    return p


def plot_venues(city, city_nickname, state, top_cats=None):
    if top_cats is None:
        top_cats = ['Grocery Store',
                    'Liquor Store',
                    'Supermarket',
                    'Food & Drink Shop',
                    'Health Food Store']

    venues_fname = "data/venues_results/{0}_venues_results.json".format(city_nickname)
    with open(venues_fname) as f_in:
        city_venues_results = json.load(f_in)
    src = make_dataset(city_venues_results, top_cats)

    p = make_plot(city, state)

    min_lat, min_lon = src.data['latitudes'][0], src.data['longitudes'][0]
    max_lat, max_lon = src.data['latitudes'][-1], src.data['longitudes'][-1]
    avg_city_mile = find_avg_city_mile(min_lat, min_lon, max_lat, max_lon)

    slider = Slider(start=0, end=1, step=0.01, value=0.5, title="Radius (miles)")

    category_selection = CheckboxGroup(labels=top_cats, active=[0])
    category_selection.js_on_change("active",
                                    CustomJS(code="src.change.emit();", args=dict(src=src)))

    category_filter = CustomJSFilter(code="""
        let selected = checkboxes.active.map(i=>checkboxes.labels[i]);
        let indices = [];
        let column = src.data.categories;
        for(let i=0; i<column.length; i++){
            if(selected.includes(column[i])){
                indices.push(i);
            }
        }
        return indices;
        """, args=dict(checkboxes=category_selection, src=src))

    color_choice = 'darkgreen'

    p.circle('x_coords', 'y_coords', source=src, name='circle',
             fill_color=color_choice, line_color=color_choice, size=4,
             view=CDSView(source=src, filters=[category_filter]))

    p_annulus = p.annulus(x='x_coords', y='y_coords', source=src, name='annulus',
                          inner_radius=0, outer_radius=avg_city_mile * 0.5,
                          fill_color=color_choice, fill_alpha=0.5, line_alpha=0,
                          view=CDSView(source=src, filters=[category_filter]))

    slider.js_on_change('value',
                        CustomJS(args=dict(other=p_annulus.glyph, factor=avg_city_mile),
                                 code="other.outer_radius = factor * this.value"))

    controls = column(category_selection, slider)
    layout = row(controls, p)

    f_out = "plots/venues_{0}.html".format(city_nickname)
    output_file(f_out)
    save(layout)

    script, div = components(layout)

    return script, div


if __name__ == '__main__':
    plot_venues('San Francisco', 'sf', 'california')
    # plot_venues('Chicago', 'chicago', 'illinois')
    # plot_venues('New York', 'nyc', 'new_york')

    pass
