# ⚡ PaperVerse - Quick Reference & Commands

## 📁 Documentation Index

1. **FEATURE_ROADMAP.md** - Complete feature list (11 phases, 100+ features)
2. **MVP_SPRINT_PLAN.md** - 4-week implementation plan with database schema
3. **FEATURE_SUMMARY.md** - Visual summary & next steps
4. **This file** - Quick commands & cheatsheet

---

## 🎯 TOP PRIORITIES (Talk to Mentor First)

### ✅ **Must Have (MVP)**
- [ ] Authentication (login/signup)
- [ ] User profiles (student, mentor, researcher)
- [ ] Save papers
- [ ] Collections
- [ ] Research groups
- [ ] Mentor dashboard
- [ ] Student activity tracking
- [ ] Assign papers to students

### ⭐ **Nice to Have (Phase 2)**
- [ ] AI chat assistant
- [ ] Annotations
- [ ] Citation network graph
- [ ] Timeline visualization
- [ ] Notifications
- [ ] Mobile app

---

## 🚀 QUICK START COMMANDS

### **1. Database Setup**
```bash
# Install PostgreSQL (macOS)
brew install postgresql
brew services start postgresql

# Create database
createdb paperverse_dev

# Create user (optional)
psql postgres
CREATE USER paperverse_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE paperverse_dev TO paperverse_user;
\q
```

### **2. Backend Setup**
```bash
cd hemal/backend

# Install new dependencies
pip install \
  sqlalchemy \
  alembic \
  psycopg2-binary \
  python-jose[cryptography] \
  passlib[bcrypt] \
  python-multipart \
  pydantic[email]

# Initialize Alembic (database migrations)
alembic init alembic

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://localhost/paperverse_dev
SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
EOF

# Apply migrations (after creating them)
alembic upgrade head

# Run backend
export $(cat .env | xargs)
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### **3. Frontend Setup**
```bash
cd citemesh-ui

# Install new dependencies
npm install \
  react-router-dom \
  @tanstack/react-query \
  zustand \
  axios \
  date-fns \
  lucide-react \
  react-hot-toast \
  clsx \
  tailwind-merge

# Install UI components (optional)
npx shadcn-ui@latest init
npx shadcn-ui@latest add button dialog dropdown-menu tabs

# Run frontend
npm run dev
```

---

## 📊 DATABASE SCHEMA (Quick Reference)

### **Core Tables:**
```sql
users                  -- Basic user info
user_profiles          -- Extended profile info
mentor_student         -- Mentor-student relationships
saved_papers           -- User's saved papers
collections            -- User's collections
collection_papers      -- Many-to-many: collections ↔ papers
research_groups        -- Research groups
group_members          -- Group membership
group_papers           -- Shared group papers
assignments            -- Papers assigned by mentors
annotations            -- Paper annotations/notes
activity_log           -- User activity tracking
notifications          -- User notifications
sessions               -- Login sessions
```

### **Key Relationships:**
```
User (1) ──→ (N) Saved Papers
User (1) ──→ (N) Collections
Collection (1) ──→ (N) Papers
User (N) ←──→ (N) Research Groups
Mentor (1) ──→ (N) Students
Mentor (1) ──→ (N) Assignments
User (1) ──→ (N) Annotations
```

---

## 🎨 FRONTEND STRUCTURE

### **New Pages to Create:**
```
src/
├── pages/
│   ├── Login.tsx              # Login page
│   ├── Register.tsx           # Signup page
│   ├── Dashboard.tsx          # Student dashboard
│   ├── MentorDashboard.tsx    # Mentor dashboard
│   ├── Profile.tsx            # User profile
│   ├── Collections.tsx        # User's collections
│   ├── Groups.tsx             # Research groups
│   ├── Papers.tsx             # Saved papers
│   └── Search.tsx             # Search (existing, enhance)
```

### **New Components to Create:**
```
src/components/
├── Auth/
│   ├── LoginForm.tsx
│   ├── RegisterForm.tsx
│   └── ProtectedRoute.tsx
├── Dashboard/
│   ├── ActivityFeed.tsx
│   ├── StatsCard.tsx
│   ├── PaperCard.tsx
│   └── QuickActions.tsx
├── Mentor/
│   ├── MenteeList.tsx
│   ├── MenteeCard.tsx
│   ├── AssignmentForm.tsx
│   ├── ProgressChart.tsx
│   └── ActivityTimeline.tsx
├── Collections/
│   ├── CollectionList.tsx
│   ├── CollectionCard.tsx
│   ├── CreateCollectionModal.tsx
│   └── CollectionDetail.tsx
└── Groups/
    ├── GroupList.tsx
    ├── GroupCard.tsx
    ├── CreateGroupModal.tsx
    ├── GroupDetail.tsx
    └── GroupMembers.tsx
```

---

## 🔐 API ENDPOINTS (To Build)

### **Authentication:**
```
POST   /auth/register          # Create account
POST   /auth/login             # Login
POST   /auth/logout            # Logout
POST   /auth/refresh           # Refresh token
GET    /auth/me                # Get current user
POST   /auth/forgot-password   # Password reset request
POST   /auth/reset-password    # Reset password
```

### **Users:**
```
GET    /users/profile/{id}     # Get user profile
PUT    /users/profile          # Update profile
GET    /users/search           # Search users
POST   /users/follow           # Follow user
DELETE /users/unfollow         # Unfollow user
```

### **Papers:**
```
POST   /papers/save            # Save paper
DELETE /papers/{id}            # Delete saved paper
GET    /papers/saved           # Get saved papers
PUT    /papers/{id}/read       # Mark as read
POST   /papers/{id}/notes      # Add notes
GET    /papers/{id}/notes      # Get notes
POST   /papers/{id}/rate       # Rate paper
```

### **Collections:**
```
POST   /collections            # Create collection
GET    /collections            # Get user's collections
GET    /collections/{id}       # Get collection detail
PUT    /collections/{id}       # Update collection
DELETE /collections/{id}       # Delete collection
POST   /collections/{id}/papers        # Add paper
DELETE /collections/{id}/papers/{pid}  # Remove paper
```

### **Research Groups:**
```
POST   /groups                 # Create group
GET    /groups                 # Get user's groups
GET    /groups/{id}            # Get group detail
PUT    /groups/{id}            # Update group
DELETE /groups/{id}            # Delete group
POST   /groups/{id}/members    # Add member
DELETE /groups/{id}/members/{uid}  # Remove member
POST   /groups/{id}/papers     # Add paper to group
GET    /groups/{id}/activity   # Get group activity
```

### **Mentor:**
```
GET    /mentor/dashboard       # Mentor dashboard data
GET    /mentor/students        # List mentees
POST   /mentor/students        # Add mentee
GET    /mentor/students/{id}/activity    # Student activity
GET    /mentor/students/{id}/analytics   # Student analytics
POST   /assignments            # Create assignment
GET    /assignments/given      # Assignments created by mentor
GET    /assignments/received   # Assignments for student
PUT    /assignments/{id}/complete        # Complete assignment
```

### **Activity:**
```
GET    /activity/me            # My activity
GET    /activity/student/{id}  # Student activity (mentor only)
GET    /activity/group/{id}    # Group activity
```

### **Annotations:**
```
POST   /papers/{id}/annotations     # Create annotation
GET    /papers/{id}/annotations     # Get annotations
PUT    /annotations/{id}             # Update annotation
DELETE /annotations/{id}             # Delete annotation
GET    /annotations/my               # All my annotations
```

---

## 🎯 FEATURE IMPLEMENTATION ORDER

### **Sprint 1 (Week 1): Auth & Users**
1. Database setup
2. User model
3. Authentication endpoints
4. Login/Register UI
5. User profiles

### **Sprint 2 (Week 2): Core Features**
6. Save papers
7. Collections
8. Research groups
9. UI for collections/groups

### **Sprint 3 (Week 3): Mentor Features**
10. Mentor-student relationships
11. Activity tracking
12. Assignments
13. Mentor dashboard
14. Student analytics

### **Sprint 4 (Week 4): AI & Polish**
15. AI chat assistant
16. Annotations
17. Notifications
18. UI/UX polish
19. Testing

---

## 🔧 USEFUL COMMANDS

### **Database:**
```bash
# Connect to database
psql paperverse_dev

# List tables
\dt

# Describe table
\d users

# Run SQL
SELECT * FROM users;

# Exit
\q

# Create migration
alembic revision -m "add annotations table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### **Backend:**
```bash
# Run with auto-reload
uvicorn app:app --reload

# Run on different port
uvicorn app:app --port 8001

# Check logs
tail -f /tmp/paperverse_backend.log

# Kill backend
pkill -f uvicorn
```

### **Frontend:**
```bash
# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Check for errors
npm run lint
```

### **Testing:**
```bash
# Backend tests
pytest

# Frontend tests
npm test

# Run specific test
pytest tests/test_auth.py

# Coverage
pytest --cov=.
```

---

## 📝 CODE SNIPPETS

### **Create User Model (SQLAlchemy):**
```python
# hemal/backend/models.py
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum('student', 'mentor', 'researcher', 'admin', name='user_role'))
    created_at = Column(DateTime, default=datetime.utcnow)
```

### **Create Login Endpoint:**
```python
# hemal/backend/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login(credentials: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
```

### **Protected Route:**
```python
# hemal/backend/auth/dependencies.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
```

### **Auth Context (React):**
```typescript
// citemesh-ui/src/contexts/AuthContext.tsx
import { createContext, useContext, useState, useEffect } from 'react';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string) => {
    const response = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    localStorage.setItem('token', data.access_token);
    // Fetch user data
    const userResponse = await fetch('/auth/me', {
      headers: { 'Authorization': `Bearer ${data.access_token}` },
    });
    const userData = await userResponse.json();
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
```

---

## 🎨 UI LIBRARIES RECOMMENDATIONS

### **Component Libraries:**
```bash
# shadcn/ui (Recommended - modern, customizable)
npx shadcn-ui@latest init
npx shadcn-ui@latest add button dialog dropdown-menu tabs

# OR Ant Design (Rich components)
npm install antd

# OR Material-UI (Google style)
npm install @mui/material @emotion/react @emotion/styled
```

### **Icons:**
```bash
# Lucide React (Recommended)
npm install lucide-react

# OR Hero Icons
npm install @heroicons/react

# OR React Icons
npm install react-icons
```

### **Charts:**
```bash
# Recharts (Recommended for analytics)
npm install recharts

# OR Chart.js
npm install chart.js react-chartjs-2
```

---

## 📚 LEARNING RESOURCES

### **FastAPI + SQLAlchemy:**
- https://fastapi.tiangolo.com/tutorial/sql-databases/
- https://docs.sqlalchemy.org/en/14/orm/tutorial.html

### **Authentication:**
- https://fastapi.tiangolo.com/tutorial/security/
- https://www.youtube.com/watch?v=H5mbgVNJ3Lk (JWT Auth)

### **React + TypeScript:**
- https://react-typescript-cheatsheet.netlify.app/
- https://www.youtube.com/watch?v=TPACABQTHvM (React Query)

### **Database Design:**
- https://www.postgresql.org/docs/current/tutorial.html
- https://dbdiagram.io/ (Visualize schema)

---

## 🐛 TROUBLESHOOTING

### **Common Issues:**

**Database connection error:**
```bash
# Check if PostgreSQL is running
brew services list

# Start PostgreSQL
brew services start postgresql
```

**Alembic migration error:**
```bash
# Check current revision
alembic current

# Show migration history
alembic history

# Stamp to specific revision
alembic stamp head
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Clear cache
pip cache purge
```

**Frontend build errors:**
```bash
# Clear node_modules
rm -rf node_modules package-lock.json
npm install

# Clear cache
npm cache clean --force
```

---

## ✅ PRE-IMPLEMENTATION CHECKLIST

Before starting implementation:

- [ ] Discussed features with mentor
- [ ] Prioritized must-have vs nice-to-have
- [ ] Set timeline (4 weeks? 8 weeks?)
- [ ] Installed PostgreSQL
- [ ] Created database
- [ ] Reviewed database schema
- [ ] Installed new dependencies
- [ ] Read authentication tutorial
- [ ] Planned UI mockups
- [ ] Set up version control (git)

---

## 🎯 SUCCESS METRICS

After implementation, check:

- [ ] Users can register and login
- [ ] Users can save papers
- [ ] Users can create collections
- [ ] Users can join groups
- [ ] Mentors can see student activity
- [ ] Mentors can assign papers
- [ ] Students can see assignments
- [ ] UI is responsive (mobile-friendly)
- [ ] Performance is good (<2s page load)
- [ ] No critical bugs

---

## 📞 SUPPORT

Need help? Check:
1. Documentation files
2. FastAPI docs: https://fastapi.tiangolo.com/
3. React docs: https://react.dev/
4. Stack Overflow
5. GitHub Discussions (if open-sourcing)

---

**Ready to start? Begin with:**
```bash
# 1. Set up database
createdb paperverse_dev

# 2. Install dependencies
cd hemal/backend
pip install sqlalchemy alembic psycopg2-binary python-jose passlib

# 3. Let's build the authentication system first!
```

Good luck! 🚀
