import os
from flask import Flask, g, request, jsonify
from database import get_db
from functools import wraps

app = Flask(__name__)

api_username = os.environ.get('USERNAME')
api_password = os.environ.get('PASSWORD')


def protected(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == api_username and auth.password == api_password:
            return function(*args, **kwargs)
        return jsonify({'message': 'Authentication failed'}), 403

    return decorated


@app.teardown_request
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/member', methods=['GET'])
@protected
def get_members():
    db = get_db()
    members_cur = db.execute('SELECT id, name, email, level FROM members')
    members = members_cur.fetchall()

    all_members = [{'id': member['id'], 'name': member['name'], 'email': member['email'], 'level': member['level']}
                   for member in members]

    return jsonify({'members': all_members})


@app.route('/member/<int:member_id>', methods=['GET'])
def get_member(member_id):
    db = get_db()
    try:
        member_cur = db.execute('SELECT id, name, email, level FROM members WHERE id = ?', (member_id,))
        member = member_cur.fetchone()

        return jsonify(
            {'member': {'id': member['id'], 'name': member['name'], 'email': member['email'], 'level': member['level']}}
        )
    except TypeError:
        return f'member with id: {member_id} does not exist'


@app.route('/member', methods=['POST'])
def add_member():
    new_member_data = request.get_json()
    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']

    db = get_db()
    db.execute('INSERT INTO members (name, email, level) VALUES (?, ?, ?)', (name, email, level))
    db.commit()

    member_cur = db.execute('SELECT id, name, email, level FROM members WHERE name = ?', (name,))
    new_member = member_cur.fetchone()

    return jsonify({'member': {'id': new_member['id'], 'name': new_member['name'], 'email': new_member['email'],
                               'level': new_member['level']}})


@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
def edit_member(member_id):
    new_member_data = request.get_json()

    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']

    db = get_db()
    db.execute('UPDATE members SET name = ?, email = ?, level= ? WHERE id = ?', (name, email, level, member_id))
    db.commit()

    member_cur = db.execute('SELECT id, name, email, level FROM members WHERE id = ?', (member_id,))
    member = member_cur.fetchone()

    return jsonify({'member': {'id': member['id'], 'name': member['name'], 'email': member['email'],
                               'level': member['level']}})


@app.route('/member/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    db = get_db()
    db.execute('DELETE FROM members WHERE id = ?', (member_id,))
    db.commit()
    return jsonify({'message': 'The member has been deleted'})


if __name__ == '__main__':
    app.run(debug=True)
