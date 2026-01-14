# Employee Management System

A full-stack REST API application for managing company employees with authentication, built with Flask (Python) backend and React TypeScript frontend.

## 🚀 Features

- **JWT Authentication**: Secure token-based authentication
- **CRUD Operations**: Complete Create, Read, Update, Delete functionality
- **RESTful API**: Follows REST principles with proper HTTP methods and status codes
- **Filtering**: Filter employees by department and role
- **Pagination**: 10 employees per page with navigation
- **Validation**: Email uniqueness and format validation
- **Responsive UI**: Mobile-friendly design with Tailwind CSS
- **Modern Stack**: Flask + Supabase backend, React + TypeScript frontend

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- Supabase account (free tier works)
- Git

## 🛠️ Tech Stack

### Backend
- Flask 3.0.0
- Supabase (PostgreSQL database)
- JWT for authentication
- pytest for testing

### Frontend
- React 18.3
- TypeScript 5.2
- Tailwind CSS 3.4
- shadcn/ui components
- Vite 5.3

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd employee-management-system
```

### 2. Backend Setup

#### Create Supabase Project

1. Go to [Supabase](https://supabase.com) and create a new project
2. Once created, go to SQL Editor and run this SQL:

```sql
-- Create employees table
CREATE TABLE employees (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    department TEXT,
    role TEXT,
    date_joined TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on email for faster lookups
CREATE INDEX idx_employees_email ON employees(email);

-- Create indexes for filtering
CREATE INDEX idx_employees_department ON employees(department);
CREATE INDEX idx_employees_role ON employees(role);
```

3. Get your Supabase URL and anon key from Settings > API

#### Install Backend Dependencies

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
SECRET_KEY=your-secret-key-min-32-characters-long
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

#### Run Backend

```bash
python app.py
```

Backend will run on `http://localhost:5000`

### 3. Frontend Setup

```bash
cd frontend
npm install
```

#### Configure API URL

If your backend runs on a different URL, update the `API_URL` in `src/App.tsx`:

```typescript
const API_URL = 'http://localhost:5000/api';
```

#### Run Frontend

```bash
npm run dev
```

Frontend will run on `http://localhost:5173`

## 🧪 Running Tests

### Backend Tests

```bash
cd backend
pytest test_app.py -v
```

Expected output:
```
test_app.py::test_health_check PASSED
test_app.py::test_register_success PASSED
test_app.py::test_register_missing_data PASSED
test_app.py::test_register_invalid_email PASSED
test_app.py::test_login_success PASSED
test_app.py::test_login_invalid_credentials PASSED
test_app.py::test_create_employee_no_auth PASSED
test_app.py::test_create_employee_success PASSED
test_app.py::test_create_employee_duplicate_email PASSED
test_app.py::test_create_employee_empty_name PASSED
test_app.py::test_create_employee_invalid_email PASSED
test_app.py::test_list_employees PASSED
test_app.py::test_list_employees_with_filter PASSED
test_app.py::test_get_employee PASSED
test_app.py::test_get_employee_not_found PASSED
test_app.py::test_update_employee PASSED
test_app.py::test_delete_employee PASSED
test_app.py::test_delete_employee_not_found PASSED
```

## 📚 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication

All employee endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your-token>
```

### Endpoints

#### 1. Register User

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-id",
    "email": "user@example.com"
  }
}
```

#### 2. Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-id",
    "email": "user@example.com"
  }
}
```

#### 3. Create Employee

```http
POST /api/employees
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "department": "Engineering",
  "role": "Developer"
}
```

**Response (201 Created):**
```json
{
  "message": "Employee created successfully",
  "employee": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "department": "Engineering",
    "role": "Developer",
    "date_joined": "2025-01-14T10:30:00Z"
  }
}
```

**Error (400 Bad Request) - Duplicate Email:**
```json
{
  "error": "Email already exists"
}
```

#### 4. List All Employees

```http
GET /api/employees?page=1&department=Engineering&role=Developer
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `department` (optional): Filter by department
- `role` (optional): Filter by role

**Response (200 OK):**
```json
{
  "employees": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "department": "Engineering",
      "role": "Developer",
      "date_joined": "2025-01-14T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 25,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

#### 5. Get Single Employee

```http
GET /api/employees/{id}
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "employee": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "department": "Engineering",
    "role": "Developer",
    "date_joined": "2025-01-14T10:30:00Z"
  }
}
```

**Error (404 Not Found):**
```json
{
  "error": "Employee not found"
}
```

#### 6. Update Employee

```http
PUT /api/employees/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "John Updated",
  "department": "Sales",
  "role": "Manager"
}
```

**Response (200 OK):**
```json
{
  "message": "Employee updated successfully",
  "employee": {
    "id": 1,
    "name": "John Updated",
    "email": "john@example.com",
    "department": "Sales",
    "role": "Manager",
    "date_joined": "2025-01-14T10:30:00Z"
  }
}
```

#### 7. Delete Employee

```http
DELETE /api/employees/{id}
Authorization: Bearer <token>
```

**Response (204 No Content):**
```
(empty response body)
```

**Error (404 Not Found):**
```json
{
  "error": "Employee not found"
}
```

### HTTP Status Codes

- `200 OK`: Successful GET/PUT request
- `201 Created`: Successful POST request
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## 🎨 Frontend Features

### Authentication
- Login/Register tabs
- Form validation
- Token storage in localStorage
- Auto-logout on token expiration

### Employee Management
- Add new employees with modal dialog
- Edit existing employees
- Delete employees with confirmation
- View all employees in card layout

### Filtering & Search
- Filter by department
- Filter by role
- Clear filters button
- Combines with pagination

### Pagination
- 10 employees per page
- Previous/Next navigation
- Page indicator
- Disabled state when no more pages

### Responsive Design
- Mobile-first approach
- Tailwind CSS utilities
- Adaptive grid layouts
- Touch-friendly buttons

## 🔒 Security Features

1. **JWT Authentication**: Secure token-based auth with 24-hour expiration
2. **Password Hashing**: Supabase handles password hashing
3. **Email Validation**: Regex-based email format validation
4. **CORS**: Configured for cross-origin requests
5. **Token Verification**: All employee routes protected
6. **Input Sanitization**: Trim and lowercase where appropriate

## 📝 Validation Rules

### Employee Model
- `name`: Required, cannot be empty string
- `email`: Required, must be valid email format, must be unique
- `department`: Optional string
- `role`: Optional string
- `date_joined`: Auto-generated on creation

### Email Validation
- Must match pattern: `user@domain.com`
- Must be unique across all employees
- Case-insensitive storage (converted to lowercase)

## 🐛 Error Handling

### Backend
- Try-catch blocks for database operations
- Proper HTTP status codes
- Descriptive error messages
- Validation before database operations

### Frontend
- Error state management
- User-friendly error messages
- Loading states during operations
- Confirmation dialogs for destructive actions


## 📄 Project Structure

```
employee-management-system/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── test_app.py            # Unit tests
│   ├── requirements.txt       # Python dependencies
│   └── .env.example          # Environment template
├── frontend/
│   ├── src/
│   │   ├── App.tsx           # Main React component
│   │   └── components/       # shadcn/ui components
│   ├── package.json          # Node dependencies
│   ├── tsconfig.json         # TypeScript config
│   ├── tailwind.config.js    # Tailwind config
│   └── vite.config.ts        # Vite config
└── README.md                 # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 🆘 Support

For issues or questions:
1. Check the documentation above
2. Review the error messages
3. Check Supabase dashboard for database issues
4. Ensure all environment variables are set correctly