from flask import Flask, request, jsonify, render_template  
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 
from flask_cors import CORS
import os
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rpg_game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    characters = db.relationship('Character', backref='user', lazy=True)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    level = db.Column(db.Integer, default=1)
    exp = db.Column(db.Integer, default=0)
    exp_to_level = db.Column(db.Integer, default=100)
    health = db.Column(db.Integer, default=100)
    max_health = db.Column(db.Integer, default=100)
    attack = db.Column(db.Integer, default=10)
    defense = db.Column(db.Integer, default=5)
    gold = db.Column(db.Integer, default=50)
    potions = db.Column(db.Integer, default=3)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Routes
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/characters', methods=['GET'])
def characters_page():
    return render_template('characters.html')

@app.route('/highscores', methods=['GET'])
def highscores_page():
    return render_template('high_scores.html')

# API Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Username already exists'})
    
    user = User(username=username)
    user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'User created successfully'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({
            'success': True, 
            'user_id': user.id,
            'username': user.username
        })
    
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/api/characters', methods=['GET'])
def get_characters():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'error': 'user_id is required'}), 400

    try:
        characters = Character.query.filter_by(user_id=user_id).all()
    except SQLAlchemyError as e:
        return jsonify({'success': False, 'error': 'Database error occurred'}), 500

    characters_data = []
    for char in characters:
        characters_data.append({
            'id': char.id,
            'name': char.name,
            'level': char.level,
            'exp': char.exp,
            'gold': char.gold,
            'health': char.health,
            'max_health': char.max_health,
            'attack': char.attack,
            'defense': char.defense,
            'potions': char.potions
        })
    
    return jsonify({'success': True, 'characters': characters_data})

@app.route('/api/characters', methods=['POST'])
def create_character():
    data = request.get_json()

    if not data or 'name' not in data or 'user_id' not in data:
        return jsonify({'success': False, 'error': 'name and user_id are required'}), 400

    try:
        character = Character(
            name=data['name'],
            user_id=data['user_id']
        )
        db.session.add(character)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Database error occurred'}), 500
    
    return jsonify({'success': True, 'character_id': character.id})

@app.route('/api/characters/<int:character_id>', methods=['PUT'])
def update_character(character_id):
    character = Character.query.get_or_404(character_id)
    data = request.get_json()
    
    character.level = data.get('level', character.level)
    character.exp = data.get('exp', character.exp)
    character.exp_to_level = data.get('exp_to_level', character.exp_to_level)
    character.health = data.get('health', character.health)
    character.max_health = data.get('max_health', character.max_health)
    character.attack = data.get('attack', character.attack)
    character.defense = data.get('defense', character.defense)
    character.gold = data.get('gold', character.gold)
    character.potions = data.get('potions', character.potions)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/highscores', methods=['GET'])
def get_highscores():
    # Get top 10 characters by level, then gold
    characters = Character.query.order_by(
        Character.level.desc(), 
        Character.gold.desc()
    ).limit(10).all()
    
    highscores = []
    for char in characters:
        user = User.query.get(char.user_id)
        highscores.append({
            'character_name': char.name,
            'username': user.username,
            'level': char.level,
            'gold': char.gold
        })
    
    return jsonify({'success': True, 'highscores': highscores})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)