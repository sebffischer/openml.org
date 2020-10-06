import datetime
import hashlib

from flask import redirect
from flask_cors import CORS
from server.extensions import db
from server.user.models import User
from server.utils import confirmation_email, forgot_password_email, send_feedback

from flask import (  # current_app,; flash,; redirect,; render_template,; url_for,
    Blueprint, jsonify, request)
import os

blueprint = Blueprint("public", __name__)

CORS(blueprint)


@blueprint.route('/signup', methods=['POST'])
def signupfunc():
    """Registering user and checking for already existing user"""
    register_obj = request.get_json()
    check_user = User.query.filter_by(email=register_obj['email']).first()
    if check_user is None:
        user = User(username=register_obj['email'], email=register_obj['email'])
        user.set_password(register_obj['password'])
        user.set_session_hash()
        user.ip_address = request.remote_addr
        user.activation_selector = None
        user.activation_code = '0000'
        user.forgotten_password_selector = None
        user.forgotten_password_code = '0000'
        user.forgotten_password_time = '0000'
        user.remember_selector = None
        user.remember_code = '0000'
        user.created_on = '0000'
        user.last_login = '0000'
        user.active = '0'
        user.first_name = register_obj['first_name']
        user.last_name = register_obj['last_name']
        user.company = '0000'
        user.phone = '0000'
        user.country = '0000'
        user.image = '0000'
        user.bio = 'No Bio'
        user.core = '0000'
        user.external_source = '0000'
        user.external_id = '0000'
        user.password_hash = '0000'
        timestamp = datetime.datetime.now()
        timestamp = timestamp.strftime("%d %H")
        md5_digest = hashlib.md5(timestamp.encode()).hexdigest()
        user.update_activation_code(md5_digest)
        confirmation_email(user.email, md5_digest)

        db.session.add(user)
        db.session.commit()
        return jsonify({"msg": "User created"}), 200
    else:
        return jsonify({"msg": "User already exists"}), 200


@blueprint.route('/forgotpassword', methods=['POST'])
def password():
    """Sending forgotten password code"""
    jobj = request.get_json()
    timestamp = datetime.datetime.now()
    timestamp = timestamp.strftime("%d %H")
    md5_digest = hashlib.md5(timestamp.encode()).hexdigest()
    user = User.query.filter_by(email=jobj['email']).first()
    user.update_forgotten_code(md5_digest)
    # user.update_forgotten_time(timestamp)
    forgot_password_email(user.email, md5_digest)
    db.session.merge(user)
    db.session.commit()
    return jsonify({"msg": "Token sent"}), 200


@blueprint.route('/send-confirmation-token', methods=['POST'])
def confirmation_token():
    """Sending confirmation token again"""
    jobj = request.get_json()
    timestamp = datetime.datetime.now()
    timestamp = timestamp.strftime("%d %H")
    md5_digest = hashlib.md5(timestamp.encode()).hexdigest()
    user = User.query.filter_by(email=jobj['email']).first()
    user.update_activation_code(md5_digest)
    confirmation_email(user.email, md5_digest)
    db.session.merge(user)
    db.session.commit()
    return jsonify({"msg": "User confirmation token sent"}), 200


@blueprint.route('/feedback', methods=['POST'])
def feedback():
    jobj = request.get_json()
    email = jobj['email']
    feedback_msg = jobj['feedback']
    send_feedback(email, feedback_msg)
    return jsonify({"msg": "Email sent"}), 200


@blueprint.route('/d/<id>', methods=['GET', 'POST'])
def data_reroute(id):
    url = str(os.environ.get('SERVER_URL')) + "search?type=data&sort=runs&id=" + id
    return redirect(url, code=302)


@blueprint.route('/t/<id>', methods=['GET', 'POST'])
def task_reroute(id):
    url = str(os.environ.get('SERVER_URL')) + "search?type=task&sort=runs&id=" + id
    return redirect(url, code=302)


@blueprint.route('/f/<id>', methods=['GET', 'POST'])
def flow_reroute(id):
    url = str(os.environ.get('SERVER_URL')) + "search?type=flow&sort=runs&id=" + id
    return redirect(url, code=302)


@blueprint.route('/r/<id>', methods=['GET', 'POST'])
def run_reroute(id):
    url = str(os.environ.get('SERVER_URL')) + "search?type=run&sort=date&id=" + id
    return redirect(url, code=302)


@blueprint.route('/s/<id>', methods=['GET', 'POST'])
def study_reroute(id):
    url = str(os.environ.get('SERVER_URL')) + "search?type=study&study_type=run&id=" + id
    return redirect(url, code=302)
