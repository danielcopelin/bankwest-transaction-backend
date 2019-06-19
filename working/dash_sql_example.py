import datetime
import base64
import io
import os
import hashlib

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.exc import IntegrityError

import pandas as pd

app = dash.Dash()
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

def parse_csv(csv):
    df = pd.read_csv(csv)
    for i, row in df.iterrows():
        try:
            h = hashlib.md5("{0}{1}{2}".format(row["Transaction Date"], row["Narration"], row["Balance"]).encode('utf-8')).hexdigest()
            db.session.add(
                Transaction(
                    id=h,
                    account=row["Account Number"],
                    date=pd.to_datetime(row["Transaction Date"]),
                    narration=row["Narration"],
                    debit=row["Debit"],
                    credit=row["Credit"],
                    balance=row["Balance"],
                )
            )
            db.session.flush()
            
        except IntegrityError as e:
            # print(e)
            db.session.rollback()
        else:
            db.session.commit()

def create_table():
    try:
        transactions = db.session.query(Transaction)
        df = pd.read_sql(transactions.statement, transactions.session.bind)

        return [
            html.Div(
                dash_table.DataTable(
                    id="table",
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict("records"),
                )
            )
        ]

    except Exception as e:
        print(e)
        pass

main = html.Div(
    [
        html.Table(
            [
                html.Td(
                    [
                        dcc.Upload(
                            id="csv-file",
                            children=html.Div(
                                ["CSV File: Drag & Drop or ", html.A("Select")]
                            ),
                        )
                    ]
                ),
                html.H3("Transactions:"),
                html.Div(create_table(), id="transactions"),
            ]
        )
    ]
)

app.layout = main

@app.callback(
    Output("transactions", "children"),
    [Input("csv-file", "contents"), Input("csv-file", "filename")],
)
def parse_contents(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        try:
            if "csv" in filename:
                # Assume that the user uploaded a CSV file
                parse_csv(io.StringIO(decoded.decode("utf-8")))
        except Exception as e:
            print(e)
            # return html.Div(["There was an error processing this file."])

        # get all transactions in database
        return create_table()


if __name__ == "__main__":
    db.create_all()
    app.run_server(debug=True)
