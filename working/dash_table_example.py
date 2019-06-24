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
import csv

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
df = df.iloc[:50]


def update_changed_data(old_data, data):
    old = pd.DataFrame.from_records(old_data)
    new = pd.DataFrame.from_records(data)

    ne_stacked = (old != new).stack()

    changed = new.stack()[ne_stacked]
    idx = changed.index.get_level_values(0)[0]
    column = changed.index.get_level_values(1)[0]
    id = old.loc[idx, 'id']
    value = changed[0]
    # print(idx, column, id, value)

    try:
        transaction = Transaction.query.get(id)
        setattr(transaction, column, value)
        db.session.flush() 
    except IntegrityError as e:
        print(e)
        db.session.rollback()
    else:
        db.session.commit()

    return f"{id}, {column}, {value}"


def gen_conditionals_from_csv(src, category_column, sub_category_column):
    categories = {}
    with open(src) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            categories[row[0]] = [c for c in row[1:] if c != ""]

    conditional_dict = {
        "id": category_column,
        "dropdown": [{"label": i, "value": i} for i in categories.keys()],
    }

    sub_conditional_dict = {}
    sub_conditional_dict["id"] = sub_category_column
    sub_conditional_dict["dropdowns"] = [
        {
            "condition": f'{{{category_column}}} eq "{category_item}"',
            "dropdown": [{"label": i, "value": i} for i in categories[category_item]],
        }
        for category_item in categories.keys()
    ]

    return conditional_dict, sub_conditional_dict


conditional_dict, sub_conditional_dict = gen_conditionals_from_csv(
    "working\\data\\categories.csv", "category", "sub_category"
)

app.layout = html.Div(
    [
        html.Div(id="table-action-outputs"),
        dash_table.DataTable(
            id="typing_formatting_1",
            data=df.to_dict("rows"),
            columns=[
                {"id": "id", "name": "Hash", "type": "text", "hidden": True},
                {"id": "date", "name": "Date", "type": "text"},
                {"id": "narration", "name": "Narration", "type": "text"},
                {
                    "id": "debit",
                    "name": "Debit",
                    "type": "numeric",
                    "format": FormatTemplate.money(2),
                },
                {
                    "id": "credit",
                    "name": "Credit",
                    "type": "numeric",
                    "format": FormatTemplate.money(2),
                },
                {
                    "id": "category",
                    "name": "Category",
                    # "type": "text",
                    "presentation": "dropdown",
                },
                {
                    "id": "sub_category",
                    "name": "Sub-category",
                    # "type": "text",
                    "presentation": "dropdown",
                },
            ],
            editable=True,
            sorting=True,
            filtering=True,
            column_static_dropdown=[conditional_dict],
            column_conditional_dropdowns=[sub_conditional_dict],
        ),
    ]
)


@app.callback(
    Output("table-action-outputs", "children"),
    [Input("typing_formatting_1", "data_previous")],
    [State("typing_formatting_1", "data")],
)
def update_database(old_table_data, table_data):
    if old_table_data is not None:
        return update_changed_data(old_table_data, table_data)
        # transactions = db.session.query(Transaction)
        # df = pd.read_sql(transactions.statement, transactions.session.bind)
        # df = df.iloc[:10]
        # return df.to_dict("rows")


if __name__ == "__main__":
    app.run_server(debug=True)
