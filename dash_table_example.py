import dash
import dash_html_components as html
import dash_table
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Sign
from dash.dependencies import Input, Output, State
import pandas as pd
from collections import OrderedDict

app = dash.Dash(__name__)

df_typing_formatting = pd.DataFrame(OrderedDict([
    ('city', ['Vancouver', 'Toronto', 'Calgary', 'Ottawa', 'Montreal', 'Halifax', 'Regina', 'Fredericton']),
    ('average_04_2018', [1092000, 766000, 431000, 382000, 341000, 316000, 276000, 173000]),
    ('change_04_2017_04_2018', [0.143, -0.051, 0.001, 0.083, 0.063, 0.024, -0.065, 0.012]),
]))

def changed_data(old_data, data):
    old = pd.DataFrame.from_records(old_data)
    new = pd.DataFrame.from_records(data)
    
    ne_stacked = (old != new).stack()
    changed = new.stack()[ne_stacked]

    return f"{changed}"

app.layout = html.Div([
    dash_table.DataTable(
        id='typing_formatting_1',
        data=df_typing_formatting.to_dict('rows'),
        columns=[{
            'id': 'city',
            'name': 'City',
            'type': 'text'
        }, {
            'id': 'average_04_2018',
            'name': 'Average Price ($)',
            'type': 'numeric',
            'format': FormatTemplate.money(2)
        }, {
            'id': 'change_04_2017_04_2018',
            'name': 'Variation (%)',
            'type': 'numeric',
            'format': FormatTemplate.percentage(1).sign(Sign.positive)
        }],
        editable=True
    ),
    html.Div(id='table-action-outputs'),
])

@app.callback(Output('table-action-outputs', 'children'),
              [Input('typing_formatting_1', 'data_previous')],
              [State('typing_formatting_1', 'data')])
def update_database(old_table_data, table_data):
    if old_table_data is not None:
        return html.P(changed_data(old_table_data, table_data))

if __name__ == '__main__':
    app.run_server(debug=True)