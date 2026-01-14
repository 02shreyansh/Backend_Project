from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import jwt
import re
from datetime import datetime, timedelta
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

CORS(app, resources={r"/api/*": {"origins": "*"}})
SUPABASE_URL = os.getenv('SUPABASE_URL', 'your-supabase-url')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'your-supabase-key')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    if not is_valid_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    try:
        response = supabase.auth.sign_up({
            "email": data['email'],
            "password": data['password']
        })
        
        if response.user:
            token = jwt.encode({
                'user_id': response.user.id,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'message': 'User registered successfully',
                'token': token,
                'user': {
                    'id': response.user.id,
                    'email': response.user.email
                }
            }), 201
        else:
            return jsonify({'error': 'Registration failed'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data['email'],
            "password": data['password']
        })
        
        if response.user:
            token = jwt.encode({
                'user_id': response.user.id,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'user': {
                    'id': response.user.id,
                    'email': response.user.email
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': 'Invalid credentials'}), 401
@app.route('/api/employees', methods=['POST'])
@token_required
def create_employee(current_user):
    data = request.get_json()

    if not data or not data.get('name') or not data.get('email'):
        return jsonify({'error': 'Name and email are required'}), 400
    
    if not data['name'].strip():
        return jsonify({'error': 'Name cannot be empty'}), 400
    
    if not is_valid_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    try:
        existing = supabase.table('employees').select('*').eq('email', data['email']).execute()
        if existing.data:
            return jsonify({'error': 'Email already exists'}), 400
        
        employee_data = {
            'name': data['name'].strip(),
            'email': data['email'].lower(),
            'department': data.get('department', ''),
            'role': data.get('role', ''),
            'date_joined': datetime.utcnow().isoformat()
        }
        
        response = supabase.table('employees').insert(employee_data).execute()
        
        return jsonify({
            'message': 'Employee created successfully',
            'employee': response.data[0]
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees', methods=['GET'])
@token_required
def list_employees(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        start = (page - 1) * per_page
        end = start + per_page - 1
        query = supabase.table('employees').select('*', count='exact')
        department = request.args.get('department')
        role = request.args.get('role')
        
        if department:
            query = query.eq('department', department)
        if role:
            query = query.eq('role', role)

        response = query.range(start, end).order('date_joined', desc=True).execute()
        
        total_count = response.count if hasattr(response, 'count') else len(response.data)
        total_pages = (total_count + per_page - 1) // per_page
        
        return jsonify({
            'employees': response.data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees/<int:employee_id>', methods=['GET'])
@token_required
def get_employee(current_user, employee_id):
    try:
        response = supabase.table('employees').select('*').eq('id', employee_id).execute()
        
        if not response.data:
            return jsonify({'error': 'Employee not found'}), 404
        
        return jsonify({'employee': response.data[0]}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees/<int:employee_id>', methods=['PUT'])
@token_required
def update_employee(current_user, employee_id):
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        existing = supabase.table('employees').select('*').eq('id', employee_id).execute()
        if not existing.data:
            return jsonify({'error': 'Employee not found'}), 404
        
        if 'name' in data and not data['name'].strip():
            return jsonify({'error': 'Name cannot be empty'}), 400
        
        if 'email' in data:
            if not is_valid_email(data['email']):
                return jsonify({'error': 'Invalid email format'}), 400

            email_check = supabase.table('employees').select('*').eq('email', data['email']).neq('id', employee_id).execute()
            if email_check.data:
                return jsonify({'error': 'Email already exists'}), 400
        
        update_data = {}
        if 'name' in data:
            update_data['name'] = data['name'].strip()
        if 'email' in data:
            update_data['email'] = data['email'].lower()
        if 'department' in data:
            update_data['department'] = data['department']
        if 'role' in data:
            update_data['role'] = data['role']
        
        response = supabase.table('employees').update(update_data).eq('id', employee_id).execute()
        
        return jsonify({
            'message': 'Employee updated successfully',
            'employee': response.data[0]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees/<int:employee_id>', methods=['DELETE'])
@token_required
def delete_employee(current_user, employee_id):
    try:
        existing = supabase.table('employees').select('*').eq('id', employee_id).execute()
        if not existing.data:
            return jsonify({'error': 'Employee not found'}), 404

        supabase.table('employees').delete().eq('id', employee_id).execute()
        
        return '', 204
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)