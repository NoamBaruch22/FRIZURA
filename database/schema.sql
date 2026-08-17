-- database/schema.sql

-- יצירת טבלת לקוחות קיימים (כולל תמיכה במחיקה רכה)
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    address TEXT,
    is_deleted INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- יצירת טבלת לידים (לקוחות פוטנציאליים)
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    source TEXT,
    status TEXT DEFAULT 'חדש',
    notes TEXT,
    is_deleted INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- יצירת טבלת תורים וקישורה ללקוח ספציפי
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    service_type TEXT NOT NULL,
    appointment_date TEXT NOT NULL,
    appointment_time TEXT NOT NULL,
    status TEXT DEFAULT 'ממתין',
    is_deleted INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
);

-- יצירת טבלת חשבוניות וקישורה ללקוח ספציפי
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    is_deleted INTEGER DEFAULT 0,
    invoice_date TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
);

-- טריגר המיישם מחיקה רכה מדורגת עבור רשומות מקושרות (מדמה התנהגות CASCADE)
CREATE TRIGGER IF NOT EXISTS soft_delete_client_cascade
AFTER UPDATE ON clients
WHEN NEW.is_deleted = 1 AND OLD.is_deleted = 0
BEGIN
    UPDATE appointments SET is_deleted = 1 WHERE client_id = NEW.id;
    UPDATE invoices SET is_deleted = 1 WHERE client_id = NEW.id;
END;

-- יצירת טבלת הגדרות עסק
CREATE TABLE IF NOT EXISTS business_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1), -- Ensure only one row exists
    name TEXT DEFAULT '',
    address TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    description TEXT DEFAULT '',
    employees TEXT DEFAULT '',
    working_hours TEXT DEFAULT '',
    services TEXT DEFAULT ''
);