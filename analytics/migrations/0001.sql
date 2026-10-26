CREATE TABLE visitors (id TEXT PRIMARY KEY, first_at TEXT NOT NULL);
CREATE TABLE sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, visitor TEXT NOT NULL, token TEXT NOT NULL, started_at TEXT NOT NULL, UNIQUE(visitor, token));
CREATE INDEX sessions_visitor ON sessions(visitor, id);
CREATE TABLE events (id TEXT PRIMARY KEY, at TEXT NOT NULL, visitor TEXT NOT NULL, session_id INTEGER NOT NULL, path TEXT NOT NULL, ip TEXT NOT NULL, country TEXT, region TEXT, city TEXT);
CREATE INDEX events_at ON events(at);
CREATE INDEX events_session ON events(session_id);
