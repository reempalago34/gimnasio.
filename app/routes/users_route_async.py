from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from app.models.users import User
from app import db
from io import BytesIO
import base64
import json

bp = Blueprint('userAsync', __name__, url_prefix='/UserAsync')

@bp.route('/index', methods=['GET'])
@login_required
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@bp.route('/add', methods=['POST'])
@login_required
def create_user():
    if current_user.rol != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
        
    data = request.json
    new_user = User(
        nombre=data['nameUser'],
        passwordUser=data['passwordUser']
    )
    new_user.save()
    return jsonify({'message': 'User created successfully'}), 201

@bp.route('/update/<int:id>', methods=['PUT'])
@login_required
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
        
    if current_user.idUser != user.idUser and current_user.rol != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.json
    user.nameUser = data['nameUser']
    if 'passwordUser' in data and data['passwordUser']:
        user.passwordUser = data['passwordUser']

    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@bp.route('/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_user(id):
    if current_user.rol != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
        
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})
    return jsonify({'message': 'User not found'}), 404