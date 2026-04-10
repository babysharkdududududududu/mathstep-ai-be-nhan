# Database Schema Documentation

## Overview

The authentication system uses PostgreSQL with three main tables:
- `users` - Core user authentication
- `students` - Student profile data
- `parents` - Parent profile data

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR,
    google_id VARCHAR UNIQUE,
    role ENUM('STUDENT', 'PARENT') NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_google_id ON users(google_id);
```

**Columns:**
- `id` - UUID primary key, automatically generated
- `email` - User's email, must be unique
- `password_hash` - Bcrypt hashed password (NULL for OAuth users)
- `google_id` - Google account ID (NULL for non-OAuth users)
- `role` - User role (STUDENT or PARENT)
- `created_at` - Account creation timestamp

**Indexes:**
- Unique index on `email` for fast lookups
- Unique index on `google_id` for OAuth users

---

### Students Table

```sql
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    name VARCHAR,
    grade_level VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_students_user_id ON students(user_id);
```

**Columns:**
- `id` - UUID primary key
- `user_id` - FK to users.id (ON DELETE CASCADE)
- `name` - Student's name (optional)
- `grade_level` - Academic grade (optional, e.g., "9th", "10th")
- `created_at` - Record creation timestamp

**Relationships:**
- One-to-One with Users
- Cascade delete when user is deleted

---

### Parents Table

```sql
CREATE TABLE parents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    name VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_parents_user_id ON parents(user_id);
```

**Columns:**
- `id` - UUID primary key
- `user_id` - FK to users.id (ON DELETE CASCADE)
- `name` - Parent's name (optional)
- `created_at` - Record creation timestamp

**Relationships:**
- One-to-One with Users
- Cascade delete when user is deleted

---

## Entity Relationships

```
┌──────────────────┐
│      User        │
├──────────────────┤
│ id (PK)          │
│ email            │
│ password_hash    │
│ google_id        │
│ role             │
│ created_at       │
└────────┬─────────┘
         │
    ┌────┴────┬─────────┐
    │          │         │
    ▼          ▼         ▼
┌────────┐  ┌────────┐  ┌──────────┐
│Student │  │ Parent │  (role      │
│        │  │        │   determines│
│user_id─┼──┼user_id─┤   which     │
│(FK)    │  │ (FK)   │   record to │
└────────┘  └────────┘   create)
   1:1         1:1
```

## Enums

### UserRole
```sql
CREATE TYPE user_role AS ENUM ('STUDENT', 'PARENT');
```

## Data Flow

### User Registration Flow

```
1. RegisterRequest received
   ↓
2. Validate role (STUDENT or PARENT)
   ↓
3. Hash password with bcrypt
   ↓
4. Create User record with role
   ↓
5. Create Student or Parent record
   (based on role)
   ↓
6. Commit transaction
   ↓
7. Generate JWT token
   ↓
8. Return TokenResponse
```

### Google OAuth Flow

```
1. User clicks "Login with Google"
   ↓
2. Receive Google authorization code
   ↓
3. Exchange code for ID token
   ↓
4. Verify and decode token
   ↓
5. Extract google_id, email, name
   ↓
6. Check if user exists (by google_id)
   ├─ EXISTS: Login user
   └─ NOT EXISTS: Create new user
      • Create User (role=STUDENT by default)
      • Create Student record
   ↓
7. Generate JWT token
   ↓
8. Return TokenResponse
```

## Query Examples

### Find User by Email
```sql
SELECT * FROM users WHERE email = 'student@example.com';
```

### Find User with Student Info
```sql
SELECT u.*, s.*
FROM users u
LEFT JOIN students s ON u.id = s.user_id
WHERE u.email = 'student@example.com';
```

### Find All Students
```sql
SELECT u.id, u.email, s.name, s.grade_level
FROM users u
JOIN students s ON u.id = s.user_id;
```

### Find User by Google ID
```sql
SELECT * FROM users WHERE google_id = 'google_user_123';
```

### Count Users by Role
```sql
SELECT role, COUNT(*) as count
FROM users
GROUP BY role;
```

## Database Maintenance

### Verify Table Structure
```sql
\d users
\d students
\d parents
```

### View Indexes
```sql
SELECT * FROM pg_indexes WHERE tablename IN ('users', 'students', 'parents');
```

### Check Constraints
```sql
SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name IN ('users', 'students', 'parents');
```

## Performance Optimization

### Recommended Indexes (Already Created)
```sql
-- Primary indexes for lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_students_user_id ON students(user_id);
CREATE INDEX idx_parents_user_id ON parents(user_id);

-- Optional: For role-based queries
CREATE INDEX idx_users_role ON users(role);

-- Optional: For date range queries
CREATE INDEX idx_users_created_at ON users(created_at);
```

## Scaling Considerations

### Current Design Supports:
- ✅ Millions of records
- ✅ Multi-tenancy (via future tenant_id field)
- ✅ Horizontal scaling (UUID primary keys)
- ✅ Archive/soft delete (via status flag if needed)

### Future Enhancements:
- Partitioning by date (for large datasets)
- Read replicas for analytics
- Caching layer (Redis)
- Archive tables for old records

## Backup & Recovery

### Backup Database
```bash
pg_dump -U mathstep_user mathstep_db > backup.sql
```

### Restore Database
```bash
psql -U mathstep_user mathstep_db < backup.sql
```

## Common Issues

### Issue: Foreign Key Constraint Violation
**Cause:** Trying to insert into students/parents without valid user_id
**Solution:** Ensure user exists before creating related records

### Issue: Duplicate Key Error
**Cause:** Email already exists or google_id conflicts
**Solution:** Check constraints, handle in application logic

### Issue: Connection Pool Exhausted
**Solution:** Increase max connections in connection string or use connection pooling
