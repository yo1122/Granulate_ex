from sqlalchemy import text

from constants import MAX_USERNAME, CHATROOM_TABLE_NAME, MESSAGE_TABLE_NAME, USER_TABLE_NAME
from utils import db


class ChatRoom(db.Model):
    __tablename__ = CHATROOM_TABLE_NAME

    name = db.Column(db.String(100), primary_key=True)
    messages = db.relationship('Message', backref='chatroom', lazy=True)
    users = db.relationship('User', backref='chatroom', lazy=True)

    def __repr__(self):
        return f'ChatRoom {self.name}'

    @staticmethod
    def chatroom_to_db(chatroom_name, user):
        new_chatroom = ChatRoom(name=chatroom_name)
        new_chatroom.users.append(user)
        db.session.add(new_chatroom)
        db.session.commit()
        return new_chatroom.name

    @staticmethod
    def get_all_chatrooms():
        chat_rooms = ChatRoom.query.all()
        return [str(chat_room) for chat_room in chat_rooms]


class Message(db.Model):
    __tablename__ = MESSAGE_TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(MAX_USERNAME), db.ForeignKey(f'{USER_TABLE_NAME}.username'), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    chatroom_name = db.Column(db.String(100), db.ForeignKey(f'{CHATROOM_TABLE_NAME}.name'))

    seen_by_users = db.relationship(
        'User',
        secondary=lambda: message_seen,
        backref=db.backref('seen_messages', lazy='dynamic'),
        lazy='dynamic'
    )

    @staticmethod
    def get_all_unseen(username, chatroom_name):
        # Get IDs of messages seen by the user using raw SQL query
        sql_query = text("SELECT message_id FROM message_seen WHERE user_username = :username")
        seen_message_ids = [
            row[0] for row in
            db.session.execute(sql_query, {"username": username}).fetchall()
        ]

        # Get all unseen messages for the given user in the specified chatroom
        unseen_messages = Message.query.filter(
            ~Message.id.in_(seen_message_ids),
            Message.chatroom_name == chatroom_name
        ).all()

        # Mark all fetched messages as seen by the user
        for message in unseen_messages:
            seen_relation = message_seen.insert().values(message_id=message.id, user_username=username)
            db.session.execute(seen_relation)

        db.session.commit()

        return [{"username": message.username, "message": message.message_text} for message in unseen_messages]

    @staticmethod
    def message_to_db(username, message_text, chatroom_name):
        new_message = Message(username=username, message_text=message_text, chatroom_name=chatroom_name)
        db.session.add(new_message)
        db.session.commit()
        return new_message.id


message_seen = db.Table(
    'message_seen',
    db.Column('message_id', db.Integer, db.ForeignKey(f'{MESSAGE_TABLE_NAME}.id')),
    db.Column('user_username', db.String(MAX_USERNAME), db.ForeignKey(f'{USER_TABLE_NAME}.username')),
    db.Column('timestamp', db.DateTime, default=db.func.current_timestamp())
)
