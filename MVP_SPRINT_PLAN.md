# 🎯 PaperVerse MVP - 4-Week Sprint Plan

## Goal: Launch with Core Features + Unique Value Proposition

---

## 🏆 WEEK 1: Authentication & Database Setup

### **Day 1-2: Database Design**

**Database Schema:**
```sql
-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50), -- 'student', 'mentor', 'researcher', 'admin'
    institution VARCHAR(255),
    bio TEXT,
    profile_picture_url VARCHAR(500),
    orcid VARCHAR(50),
    created_at TIMESTAMP,
    last_login TIMESTAMP
);

-- User Profiles (Extended Info)
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    academic_level VARCHAR(50), -- 'undergrad', 'masters', 'phd', 'postdoc', 'faculty'
    research_interests TEXT[], -- Array of topics
    google_scholar_url VARCHAR(500),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    office_hours VARCHAR(255), -- For mentors
    availability TEXT
);

-- Mentor-Student Relationships
CREATE TABLE mentor_student (
    id UUID PRIMARY KEY,
    mentor_id UUID REFERENCES users(id),
    student_id UUID REFERENCES users(id),
    status VARCHAR(50), -- 'pending', 'active', 'inactive'
    created_at TIMESTAMP,
    UNIQUE(mentor_id, student_id)
);

-- Saved Papers
CREATE TABLE saved_papers (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    openalex_id VARCHAR(255) NOT NULL,
    paper_data JSONB, -- Store full paper metadata
    saved_at TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    notes TEXT,
    rating INTEGER, -- 1-5 stars
    UNIQUE(user_id, openalex_id)
);

-- Collections
CREATE TABLE collections (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Collection Papers (Many-to-Many)
CREATE TABLE collection_papers (
    collection_id UUID REFERENCES collections(id),
    paper_id UUID REFERENCES saved_papers(id),
    added_at TIMESTAMP,
    PRIMARY KEY(collection_id, paper_id)
);

-- Research Groups
CREATE TABLE research_groups (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by UUID REFERENCES users(id),
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);

-- Group Members
CREATE TABLE group_members (
    group_id UUID REFERENCES research_groups(id),
    user_id UUID REFERENCES users(id),
    role VARCHAR(50), -- 'owner', 'mentor', 'member'
    joined_at TIMESTAMP,
    PRIMARY KEY(group_id, user_id)
);

-- Group Papers (Shared Library)
CREATE TABLE group_papers (
    group_id UUID REFERENCES research_groups(id),
    paper_id UUID REFERENCES saved_papers(id),
    added_by UUID REFERENCES users(id),
    added_at TIMESTAMP,
    PRIMARY KEY(group_id, paper_id)
);

-- Assignments (Mentor assigns papers to students)
CREATE TABLE assignments (
    id UUID PRIMARY KEY,
    mentor_id UUID REFERENCES users(id),
    student_id UUID REFERENCES users(id),
    paper_id UUID REFERENCES saved_papers(id),
    group_id UUID REFERENCES research_groups(id), -- Optional
    title VARCHAR(255),
    instructions TEXT,
    due_date TIMESTAMP,
    status VARCHAR(50), -- 'pending', 'in_progress', 'completed'
    completed_at TIMESTAMP,
    created_at TIMESTAMP
);

-- Paper Annotations
CREATE TABLE annotations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    paper_id UUID REFERENCES saved_papers(id),
    text TEXT NOT NULL,
    color VARCHAR(20), -- 'yellow', 'green', 'blue', 'red', 'purple'
    page_number INTEGER,
    position JSONB, -- Store coordinates if needed
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);

-- Activity Log (For Mentor Dashboard)
CREATE TABLE activity_log (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    activity_type VARCHAR(50), -- 'search', 'save', 'read', 'annotate', 'join_group'
    entity_type VARCHAR(50), -- 'paper', 'group', 'collection'
    entity_id VARCHAR(255),
    metadata JSONB, -- Additional context
    created_at TIMESTAMP
);

-- Notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    type VARCHAR(50), -- 'assignment', 'mention', 'group_invite', 'new_paper'
    title VARCHAR(255),
    message TEXT,
    link VARCHAR(500),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);

-- Sessions (For JWT alternative)
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    token VARCHAR(500) UNIQUE,
    expires_at TIMESTAMP,
    created_at TIMESTAMP
);
```

**Implementation:**
```bash
# Create migration files
cd hemal/backend
alembic init alembic
alembic revision -m "initial_schema"
# Add tables to migration
alembic upgrade head
```

---

### **Day 3-4: Authentication Backend**

**Files to Create:**
```
hemal/backend/
├── auth/
│   ├── __init__.py
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── routes.py          # Auth endpoints
│   ├── utils.py           # Password hashing, JWT
│   └── dependencies.py    # Auth dependencies
├── users/
│   ├── __init__.py
│   ├── models.py
│   ├── schemas.py
│   └── routes.py
└── database.py            # Database connection
```

**Key Endpoints:**
```python
POST /auth/register
POST /auth/login
POST /auth/logout
POST /auth/refresh
GET  /auth/me
POST /auth/forgot-password
POST /auth/reset-password

GET  /users/profile/{user_id}
PUT  /users/profile
GET  /users/search?q=name
```

**Implementation:**
```python
# hemal/backend/auth/utils.py
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
```

---

### **Day 5-7: Frontend Auth UI**

**Components to Create:**
```
citemesh-ui/src/
├── components/
│   ├── Auth/
│   │   ├── LoginForm.tsx
│   │   ├── RegisterForm.tsx
│   │   ├── ProfileSetup.tsx
│   │   └── ProtectedRoute.tsx
│   ├── Layout/
│   │   ├── Navbar.tsx           # Add login/profile button
│   │   ├── Sidebar.tsx          # User menu
│   │   └── Footer.tsx
│   └── Profile/
│       ├── ProfileCard.tsx
│       ├── ProfileEdit.tsx
│       └── UserAvatar.tsx
├── contexts/
│   └── AuthContext.tsx          # Global auth state
├── hooks/
│   └── useAuth.ts               # Auth hook
└── pages/
    ├── Login.tsx
    ├── Register.tsx
    ├── Profile.tsx
    └── Dashboard.tsx
```

**Auth Context:**
```typescript
// citemesh-ui/src/contexts/AuthContext.tsx
interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  loading: boolean;
}

export const AuthProvider: React.FC = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on mount
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token and fetch user
      fetchCurrentUser(token);
    }
  }, []);

  // ... implementation
};
```

---

## 🎨 WEEK 2: Core Features (Save, Collections, Groups)

### **Day 8-9: Paper Saving & Collections Backend**

**Endpoints:**
```python
POST /papers/save
DELETE /papers/{paper_id}
GET /papers/saved
PUT /papers/{paper_id}/read
POST /papers/{paper_id}/notes

POST /collections
GET /collections
GET /collections/{collection_id}
PUT /collections/{collection_id}
DELETE /collections/{collection_id}
POST /collections/{collection_id}/papers
DELETE /collections/{collection_id}/papers/{paper_id}
```

---

### **Day 10-11: Research Groups Backend**

**Endpoints:**
```python
POST /groups
GET /groups
GET /groups/{group_id}
PUT /groups/{group_id}
DELETE /groups/{group_id}
POST /groups/{group_id}/members
DELETE /groups/{group_id}/members/{user_id}
POST /groups/{group_id}/papers
GET /groups/{group_id}/activity
```

---

### **Day 12-14: Frontend UI for Save/Collections/Groups**

**Components:**
```typescript
// Save Paper Button
<SavePaperButton paperId={paper.id} />

// Collections Sidebar
<CollectionsList />
<CreateCollectionModal />
<CollectionDetail collectionId={id} />

// Research Groups
<GroupsList />
<CreateGroupModal />
<GroupDetail groupId={id} />
<GroupMembers groupId={id} />
```

---

## 👨‍🏫 WEEK 3: Mentor Dashboard & Student Tracking

### **Day 15-16: Activity Tracking Backend**

**Implementation:**
```python
# Activity logger middleware
@app.middleware("http")
async def log_activity(request: Request, call_next):
    response = await call_next(request)
    
    # Log certain actions
    if request.method in ["POST", "PUT", "DELETE"]:
        user = get_current_user(request)
        if user:
            log_user_activity(user.id, request.url, request.method)
    
    return response

# Activity endpoints
GET /activity/me
GET /activity/student/{student_id}  # For mentors
GET /activity/group/{group_id}
```

---

### **Day 17-18: Assignment System**

**Endpoints:**
```python
POST /assignments
GET /assignments/received  # For students
GET /assignments/given     # For mentors
PUT /assignments/{id}/complete
DELETE /assignments/{id}
```

**Frontend:**
```typescript
<AssignmentList />
<CreateAssignment mentorId={user.id} studentId={studentId} />
<AssignmentDetail assignmentId={id} />
```

---

### **Day 19-21: Mentor Dashboard**

**Dashboard Components:**
```typescript
// Mentor Dashboard
<MentorDashboard>
  <MenteesList mentees={mentees} />
  <RecentActivity activities={activities} />
  <ResearchGroups groups={groups} />
  <Assignments assignments={assignments} />
  <MenteeProgress studentId={id} />
</MentorDashboard>

// Stats Cards
<StatsCard 
  title="Active Mentees" 
  value={12} 
  change="+2 this month" 
/>

// Activity Feed
<ActivityFeed>
  {activities.map(activity => (
    <ActivityItem 
      user={activity.user}
      action={activity.type}
      timestamp={activity.created_at}
    />
  ))}
</ActivityFeed>
```

**Backend:**
```python
GET /mentor/dashboard
  Returns:
  - mentees list
  - recent activity
  - assignments
  - groups
  - stats

GET /mentor/student/{student_id}/analytics
  Returns:
  - papers read
  - reading pace
  - engagement score
  - topic distribution
```

---

## 🤖 WEEK 4: AI Features & Polish

### **Day 22-23: AI Chat Assistant**

**Backend:**
```python
# hemal/backend/ai_chat.py
from typing import List

class ResearchChatBot:
    def __init__(self):
        self.conversation_history = []
    
    async def chat(self, user_query: str, context_papers: List[dict]) -> str:
        """
        Chat about research papers with context.
        """
        # Build prompt with paper context
        prompt = self._build_prompt(user_query, context_papers)
        
        # Call Gemini API
        response = await call_gemini(prompt)
        
        return response
    
    def _build_prompt(self, query: str, papers: List[dict]) -> str:
        context = "\n\n".join([
            f"Paper: {p['title']}\nAbstract: {p.get('abstract', 'N/A')}"
            for p in papers[:5]  # Limit to 5 papers
        ])
        
        return f"""You are a research assistant helping a student understand papers.

Context Papers:
{context}

Student Question: {query}

Provide a helpful, concise answer based on the papers above."""

# Endpoint
POST /chat
{
  "message": "Explain the attention mechanism",
  "paper_ids": ["W123", "W456"]
}
```

**Frontend:**
```typescript
<ChatInterface>
  <ChatMessages messages={messages} />
  <ChatInput onSend={handleSend} />
  <PaperContext papers={selectedPapers} />
</ChatInterface>
```

---

### **Day 24-25: Annotations System**

**Backend:**
```python
POST /papers/{paper_id}/annotations
GET /papers/{paper_id}/annotations
PUT /annotations/{id}
DELETE /annotations/{id}
GET /annotations/my  # All my annotations
```

**Frontend:**
```typescript
// PDF Viewer with annotations
<PDFViewer 
  pdfUrl={paper.pdf_url}
  annotations={annotations}
  onAnnotate={handleAnnotate}
/>

// Annotation Sidebar
<AnnotationsList 
  annotations={annotations}
  onSelect={scrollToAnnotation}
/>
```

---

### **Day 26-28: Polish & Testing**

**Tasks:**
- [ ] UI/UX improvements
- [ ] Responsive design
- [ ] Error handling
- [ ] Loading states
- [ ] Empty states
- [ ] Success messages
- [ ] Performance optimization
- [ ] Security audit
- [ ] User testing

---

## 🎯 MVP FEATURE CHECKLIST

### **✅ Authentication (MUST HAVE)**
- [x] User registration
- [x] Email/password login
- [x] User profiles (student, mentor, researcher)
- [x] Role-based access control
- [x] Profile editing

### **✅ Paper Management (MUST HAVE)**
- [x] Save papers
- [x] Mark as read
- [x] Add notes
- [x] Rate papers
- [x] View saved papers

### **✅ Collections (MUST HAVE)**
- [x] Create collections
- [x] Add papers to collections
- [x] Public/private collections
- [x] Share collections

### **✅ Research Groups (MUST HAVE)**
- [x] Create groups
- [x] Invite members
- [x] Shared paper library
- [x] Group activity feed

### **✅ Mentor-Student (UNIQUE FEATURE)**
- [x] Mentor-student relationships
- [x] Activity tracking
- [x] Mentor dashboard
- [x] Assign papers
- [x] Track progress
- [x] View student activity

### **✅ AI Features (UNIQUE FEATURE)**
- [x] Natural language search (already done)
- [x] AI chat assistant
- [x] Query translation

### **✅ Annotations (SHOULD HAVE)**
- [x] Highlight text
- [x] Add comments
- [x] Color coding
- [x] Share annotations

### **⭐ Nice to Have (Post-MVP)**
- [ ] Notification system
- [ ] Email notifications
- [ ] Advanced analytics
- [ ] Citation graph
- [ ] Timeline view
- [ ] Mobile app

---

## 🛠️ TECH STACK SETUP

### **Backend Dependencies:**
```bash
cd hemal/backend

# Install packages
pip install \
  fastapi \
  uvicorn \
  sqlalchemy \
  alembic \
  psycopg2-binary \
  python-jose[cryptography] \
  passlib[bcrypt] \
  python-multipart \
  pydantic[email] \
  redis \
  celery

# Create requirements.txt
pip freeze > requirements.txt
```

### **Database Setup:**
```bash
# Install PostgreSQL
brew install postgresql
brew services start postgresql

# Create database
createdb paperverse_dev

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost/paperverse_dev"
export SECRET_KEY="your-secret-key-here"
export JWT_ALGORITHM="HS256"
```

### **Frontend Dependencies:**
```bash
cd citemesh-ui

# Install packages
npm install \
  react-router-dom \
  @tanstack/react-query \
  zustand \
  axios \
  date-fns \
  lucide-react \
  @radix-ui/react-dialog \
  @radix-ui/react-dropdown-menu \
  @radix-ui/react-tabs \
  react-hot-toast \
  clsx \
  tailwind-merge

# Dev dependencies
npm install -D \
  @types/react \
  @types/react-dom \
  autoprefixer \
  postcss \
  tailwindcss
```

---

## 📊 SUCCESS METRICS

### **After 4 Weeks:**
- ✅ 100% core features working
- ✅ Authentication fully functional
- ✅ Mentor dashboard operational
- ✅ AI chat assistant working
- ✅ Mobile-responsive UI
- ✅ <2 second page load time
- ✅ Zero critical bugs

### **User Testing Goals:**
- 10 students test the platform
- 3 mentors use the dashboard
- Collect feedback
- Identify pain points
- Measure task completion rate

---

## 🚀 DEPLOYMENT PLAN

### **Week 5: Production Deployment**

**Infrastructure:**
```
Frontend: Vercel / Netlify
Backend: Railway / Render / Fly.io
Database: Supabase / Railway
Storage: AWS S3 / Cloudflare R2
```

**Steps:**
1. Set up production database
2. Configure environment variables
3. Deploy backend API
4. Deploy frontend app
5. Set up custom domain
6. Configure SSL
7. Set up monitoring (Sentry)
8. Set up analytics (Plausible)

---

## 📚 DOCUMENTATION TO CREATE

1. **README.md** - Project overview
2. **SETUP.md** - Local development setup
3. **API.md** - API documentation
4. **DEPLOYMENT.md** - Deployment guide
5. **USER_GUIDE.md** - User documentation
6. **MENTOR_GUIDE.md** - Mentor-specific guide

---

## 💡 QUICK WINS (Can implement in 1-2 hours each)

1. **Dark Mode** - Use system preference
2. **Keyboard Shortcuts** - Power user features
3. **Export Citations** - BibTeX export
4. **Reading Time Estimate** - Show estimated time
5. **Paper Stats** - Citation count, year, venue
6. **Search Filters** - Year range, open access
7. **Sort Options** - By date, citations, relevance
8. **Share Links** - Share papers with others

---

**Next Step:** Review this plan with your mentor and prioritize features based on:
1. Academic requirements
2. Unique value proposition
3. Technical feasibility
4. Time constraints

**Questions for your mentor:**
- Which mentor dashboard features are most valuable?
- What student activity should be tracked?
- Privacy concerns with activity tracking?
- Integration with institution systems needed?
- Timeline expectations?

Let me know which features to start implementing first! 🚀
