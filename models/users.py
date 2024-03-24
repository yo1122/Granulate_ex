from sqlalchemy.exc import IntegrityError

from constants import MAX_PASSWORD, MAX_ROOM_NAME
from models.messaging import USER_TABLE_NAME, MAX_USERNAME, CHATROOM_TABLE_NAME
from utils import db


class User(db.Model):
    __tablename__ = USER_TABLE_NAME

    username = db.Column(db.String(MAX_USERNAME), primary_key=True)
    password = db.Column(db.String(MAX_PASSWORD))
    chatroom_name = db.Column(db.String(MAX_ROOM_NAME), db.ForeignKey(f'{CHATROOM_TABLE_NAME}.name'))

    def __repr__(self):
        return f'<User {self.username}>'

    @staticmethod
    def get_or_create(username):
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return existing_user
        try:
            new_user = User(username=username)
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except IntegrityError:
            # Handle the case where another request created the user concurrently
            db.session.rollback()
            return User.query.filter_by(username=username).first()
