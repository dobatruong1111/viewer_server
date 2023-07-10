from db import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.BigInteger(), primary_key=True)
    username = db.Column(db.Unicode())
    password = db.Column(db.Unicode())

    def __repr__(self):
        return '{}<{}>'.format(self.username, self.id)
