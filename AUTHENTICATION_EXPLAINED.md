# Authentication System Explained

## Overview
This pharmacy app uses a **custom authentication system** with **role-based access control (RBAC)**. Here's how it works:

---

## 1. Custom User Model (`pharmacy/models.py`)

The app uses a **custom User model** that extends Django's `AbstractUser`:

```python
class User(AbstractUser):
    ROLE_CHOICES = [
        ('pharmacist', 'Pharmacist'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    reset_token = models.CharField(max_length=100, blank=True, null=True)
```

**Key Points:**
- Extends Django's built-in user model
- Adds a `role` field with 3 roles: `admin`, `pharmacist`, `staff`
- Stores password reset tokens
- Configured in `settings.py`: `AUTH_USER_MODEL = 'pharmacy.User'`

---

## 2. Custom Authentication Backend (`pharmacy/backends.py`)

The app uses a **custom authentication backend** instead of Django's default:

```python
class CustomUserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        # Checks username and password
        # Returns user if valid, None if invalid
```

**Configured in `settings.py`:**
```python
AUTHENTICATION_BACKENDS = ['pharmacy.backends.CustomUserBackend']
```

**How it works:**
1. Takes username and password
2. Looks up user by username
3. Verifies password using Django's password hashing
4. Returns user if valid, None if invalid

---

## 3. Login Process (`pharmacy/views.py`)

### Login Flow:

```python
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)  # Creates session
            
            # Role-based redirect
            if user.role == 'admin':
                return redirect('index')  # Admin dashboard
            elif user.role == 'pharmacist':
                return redirect('pharmacist_dashboard')
            else:
                return redirect('staff_dashboard')
        else:
            messages.error(request, "Invalid username or password")
```

**Steps:**
1. User submits username/password
2. `authenticate()` uses `CustomUserBackend` to verify
3. If valid, `login()` creates a session
4. User is redirected based on their **role**

---

## 4. Access Control - Decorators (`pharmacy/decorators.py`)

The app uses **decorators** to control who can access which views:

### Available Decorators:

#### `@role_required(['admin', 'pharmacist'])`
- Checks if user has one of the specified roles
- Redirects to login if not authenticated
- Shows error message if wrong role

#### `@admin_required`
- Shortcut for `@role_required(['admin'])`
- Only admins can access

#### `@pharmacist_required`
- Only pharmacists can access

#### `@staff_required`
- Only staff can access

#### `@pharmacist_or_staff_required`
- Pharmacists OR staff can access

#### `@admin_or_pharmacist_required`
- Admin OR pharmacist can access

### How Decorators Work:

```python
def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # 1. Check if user is logged in
            if not request.user.is_authenticated:
                return redirect('login')
            
            # 2. Check if user has required role
            if request.user.role not in allowed_roles:
                messages.error(request, 'You do not have permission...')
                return redirect('login')
            
            # 3. If all checks pass, execute the view
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

---

## 5. Usage Examples

### In Views:

```python
from .decorators import admin_required, pharmacist_required

@admin_required
def admin_dashboard(request):
    # Only admins can access this
    return render(request, 'admin/dashboard.html')

@pharmacist_required
def pharmacist_dashboard(request):
    # Only pharmacists can access this
    return render(request, 'pharmacist/dashboard.html')
```

### Current Usage in App:

- **Admin-only views:**
  - User management (add/edit/delete users)
  - Admin dashboard
  - Stock reports
  - Sales reports

- **Login required (any role):**
  - Billing views
  - Supplier views

---

## 6. Session Management

### Login:
- Creates a session when user logs in
- Session stored in database (default Django behavior)
- User stays logged in until logout or session expires

### Logout:
```python
def logout_view(request):
    logout(request)  # Destroys session
    return redirect('login')
```

### Settings:
```python
LOGIN_URL = '/login/'              # Where to redirect if not logged in
LOGIN_REDIRECT_URL = '/dashboard/' # Default redirect after login
LOGOUT_REDIRECT_URL = '/login/'    # Where to go after logout
```

---

## 7. Password Reset System

The app includes a password reset feature:

1. User requests reset via email
2. System generates a random token
3. Token stored in `user.reset_token`
4. Email sent with reset link: `/reset-password/<token>/`
5. User clicks link and sets new password
6. Token is cleared after use

---

## 8. Role Hierarchy & Permissions

### Role Permissions:

| Role | Permissions |
|------|-------------|
| **Admin** | Full access - can manage users, view all reports, access admin dashboard |
| **Pharmacist** | Can manage medicines, billing, view pharmacist dashboard |
| **Staff** | Limited access - basic operations, staff dashboard |

### Access Control Flow:

```
User Request → Is Authenticated? → Has Required Role? → Access Granted
                    ↓ No                    ↓ No
              Redirect to Login    Show Error & Redirect
```

---

## 9. Security Features

1. **Password Hashing**: Uses Django's PBKDF2 password hasher
2. **Session Security**: Django's built-in session security
3. **CSRF Protection**: Enabled via middleware
4. **Role-based Access**: Prevents unauthorized access to views
5. **Custom Backend**: Allows custom authentication logic

---

## 10. How to Add New Protected View

```python
from .decorators import admin_required

@admin_required  # Add this decorator
def my_protected_view(request):
    # Only admins can access this
    return render(request, 'my_template.html')
```

---

## Summary

**Authentication Flow:**
1. User submits credentials → `login_view()`
2. `authenticate()` uses `CustomUserBackend`
3. If valid → `login()` creates session
4. Redirect based on role

**Access Control:**
1. Decorator checks if user is authenticated
2. Decorator checks if user has required role
3. If both pass → view executes
4. If fails → redirect to login with error message

**Key Files:**
- `pharmacy/models.py` - User model with roles
- `pharmacy/backends.py` - Custom authentication
- `pharmacy/decorators.py` - Access control decorators
- `pharmacy/views.py` - Login/logout views
- `pharmacy_app/settings.py` - Configuration

