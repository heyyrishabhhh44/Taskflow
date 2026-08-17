-- TaskFlow: Task & Productivity Management System
-- Target database: PostgreSQL
-- Run with: psql -U your_user -d taskflow -f schema_postgres.sql

DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS priorities CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE priorities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE,   -- Low / Medium / High
    weight INTEGER NOT NULL UNIQUE       -- used for sorting: 1=Low, 2=Medium, 3=High
);

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    assigned_to INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(150) NOT NULL,
    description TEXT,
    priority_id INTEGER NOT NULL REFERENCES priorities(id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'in_progress', 'completed')),
    deadline DATE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_deadline ON tasks(deadline);
CREATE INDEX idx_tasks_project ON tasks(project_id);

INSERT INTO priorities (name, weight) VALUES ('Low', 1), ('Medium', 2), ('High', 3);
