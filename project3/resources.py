from flask import jsonify
from data import db_session
from data.notes import Note
from data.messages import Message
from flask_restful import reqparse, abort, Resource


def abort_if_notes_not_found(note_id):
    session = db_session.create_session()
    notes = session.query(Note).get(note_id)
    if not notes:
        abort(404, message=f"Note {notes} not found")


class NoteResource(Resource):
    def get(self, note_id):
        abort_if_notes_not_found(note_id)
        session = db_session.create_session()
        notes = session.query(Note).get(note_id)
        return jsonify({"notes": notes.to_dict(only=('mood', 'comment', 'transaction_date'))})
    
    def delete(self, note_id):
        abort_if_notes_not_found(note_id)
        session = db_session.create_session()
        note = session.query(Note).get(note_id)
        session.delete(note)
        session.commit()
        return jsonify({"success": "OK"})
    

parser = reqparse.RequestParser()
parser.add_argument('mood', required=True)
parser.add_argument('comment', required=True)
parser.add_argument('user_id', required=True, type=int)


class NoteListResource(Resource):
    def get(self):
        session = db_session.create_session()
        notes = session.query(Note).all()
        return jsonify({"notes": [item.to_dict(only=('mood', 'comment', 'transaction_date')) for item in notes]})
    
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        note = Note(
            mood=args['mood'],
            comment=args['comment'],
            user_id=args['user_id']
        )
        session.add(note)
        session.commit()
        return jsonify({"id": note.id})
        

def abort_if_message_not_found(message_id):
    session = db_session.create_session()
    message = session.query(Message).get(message_id)
    if not message:
        abort(404, message=f"Message {message_id} not found")


class MessageResource(Resource):
    def get(self, message_id):
        abort_if_message_not_found(message_id)
        session = db_session.create_session()
        message = session.query(Message).get(message_id)
        return jsonify({"message": message.to_dict(only=('question', 'answer', 'transaction_date'))})
    
    def delete(self, message_id):
        abort_if_message_not_found(message_id)
        session = db_session.create_session()
        message = session.query(Message).get(message_id)
        session.delete(message)
        session.commit()
        return jsonify({"success": "OK"})
    

parser = reqparse.RequestParser()
parser.add_argument('question', required=True)
parser.add_argument('answer', required=True)
parser.add_argument('user_id', required=True, type=int)
parser.add_argument('transaction_date', required=True)


class MessageListResource(Resource):
    def get(self):
        session = db_session.create_session()
        messages = session.query(Message).all()
        return jsonify({"messages": [item.to_dict(only=('question', 'answer', 'transaction_date')) for item in messages]})
    
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        message = Message(
            question=args['question'],
            answer=args['answer'],
            user_id=args['user_id'],
            transaction_date=args['transaction_date']
        )
        session.add(message)
        session.commit()
        return jsonify({"id": message.id})