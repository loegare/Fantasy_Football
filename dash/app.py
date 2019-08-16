import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import gamedata
df = gamedata.single_game_fps([2019081552])

import dash
import dash_table


app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True} for i in df.columns
        ],
        data=df.to_dict('records'),
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        selected_rows=[],
        page_action="native",  style_cell={
        # all three widths are needed
        'minWidth': '10px', 'width': '10px', 'maxWidth': '10px',
        'whiteSpace': 'no-wrap',
        'textOverflow': 'ellipsis',
    })], className="six columns"),

    html.Div([dash_table.DataTable(
        id='datatable-interactivity3',
        columns=[
            {"name": i, "id": i, "deletable": True} for i in df.columns
        ],
        data=df.to_dict('records'),
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        selected_rows=[],
        page_action="native",  style_cell={
        # all three widths are needed
        'minWidth': '10px', 'width': '10px', 'maxWidth': '10px',
        'whiteSpace': 'no-wrap',
        'textOverflow': 'ellipsis',
    })], className="six columns"),
], className="row")
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})
if __name__ == '__main__':
    app.run_server(debug=True)
