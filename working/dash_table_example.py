import dash
import dash_html_components as html
import dash_table
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Sign
from dash.dependencies import Input, Output, State
import pandas as pd
from collections import OrderedDict
from flask_sqlalchemy import SQLAlchemy
import datetime

app = dash.Dash(__name__)
app.server.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data/tmp.db"
db = SQLAlchemy(app.server)

class Transaction(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    account = db.Column(db.String(80), unique=False, nullable=False)
    date = db.Column(db.DateTime, unique=False, nullable=False)
    narration = db.Column(db.String(120), unique=False, nullable=False)
    debit = db.Column(db.Float, unique=False)
    credit = db.Column(db.Float, unique=False)
    balance = db.Column(db.Float, unique=False)
    added_date = db.Column(
        db.DateTime, unique=False, nullable=False, default=datetime.datetime.utcnow
    )
    category = db.Column(db.String(80), nullable=True)
    sub_category = db.Column(db.String(80), nullable=True)

    def __repr__(self):
        return "<Transaction %r>" % self.id

transactions = db.session.query(Transaction)
df = pd.read_sql(transactions.statement, transactions.session.bind)

def changed_data(old_data, data):
    old = pd.DataFrame.from_records(old_data)
    new = pd.DataFrame.from_records(data)
    
    ne_stacked = (old != new).stack()
    changed = new.stack()[ne_stacked]

    return f"{changed}"

app.layout = html.Div([
    html.Div(id='table-action-outputs'),
    dash_table.DataTable(
        id='typing_formatting_1',
        data=df.to_dict('rows'),
        columns=[{
            'id': 'id',
            'name': 'Hash',
            'type': 'text',
            'hidden': True
        }, {
            'id': 'date',
            'name': 'Date',
            'type': 'text',
            # 'format': FormatTemplate.money(2)
        }, {
            'id': 'narration',
            'name': 'Narration',
            'type': 'text',
        }, {
            'id': 'debit',
            'name': 'Debit',
            'type': 'numeric',
            'format': FormatTemplate.money(2)
        }, {
            'id': 'credit',
            'name': 'Credit',
            'type': 'numeric',
            'format': FormatTemplate.money(2)
        }, {
            'id': 'category',
            'name': 'Category',
            'type': 'text',
            # 'format': FormatTemplate.money(2)
        }, {
            'id': 'sub_category',
            'name': 'Sub-category',
            'type': 'text',
            # 'format': FormatTemplate.money(2)
        }],
        editable=True,
        sorting=True,
        filtering=True
    ),
])

@app.callback(Output('table-action-outputs', 'children'),
              [Input('typing_formatting_1', 'data_previous')],
              [State('typing_formatting_1', 'data')])
def update_database(old_table_data, table_data):
    if old_table_data is not None:
        return html.P(changed_data(old_table_data, table_data))

if __name__ == '__main__':
    app.run_server(debug=True)