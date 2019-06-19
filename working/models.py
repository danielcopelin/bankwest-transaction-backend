from .extensions import db

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