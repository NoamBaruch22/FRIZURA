# database/db_manager.py

import sqlite3
import json
from pathlib import Path

class DBManager:
    """
    מחלקה המנהלת את החיבור למסד הנתונים SQLite ואת אתחול הסכמה.
    המחלקה מטפלת ביצירת נתיבים בטוחה בהתאם למערכת ההפעלה ומחילת הגדרות PRAGMA קריטיות.
    """
    def __init__(self, db_name="appointments.db"):
        # זיהוי דינמי של הנתיב לקובץ ההרצה הנוכחי ויצירת נתיב לקובץ הנתונים
        # מנגנון זה מונע שגיאות הקשורות ללוכסנים שונים בין מערכות Windows ו-macOS
        self.db_path = Path(__file__).parent.parent / db_name
        self._initialize_db()

    def get_connection(self):
        """
        יוצר חיבור למסד הנתונים ומפעיל הגדרות תצורה הכרחיות.
        מחזיר אובייקט חיבור (Connection) המאפשר תקשורת ישירה מול הנתונים.
        """
        conn = sqlite3.connect(self.db_path)
        
        # אכיפת חוקיות מפתחות זרים. ללא שורה זו, המערכת תאפשר הזנת נתוני כזב לטבלאות התלויות.
        conn.execute("PRAGMA foreign_keys = ON")
        
        # מעבר למצב WAL משפר משמעותית את ביצועי הקריאה והכתיבה ומונע נעילות קובץ מיותרות
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        
        # הגדרה המאפשרת למשוך נתונים באמצעות שמות העמודות (כמו במילון) ולא רק לפי אינדקסים מספריים
        conn.row_factory = sqlite3.Row 
        return conn

    def _initialize_db(self):
        """
        פונקציה פרטית המופעלת בעת עליית המערכת. בודקת אם קובץ הסכמה קיים,
        ומפעילה אותו בשלמותו על מנת ליצור את הטבלאות במידה ואינן קיימות.
        """
        schema_path = Path(__file__).parent / "schema.sql"
        if not schema_path.exists():
            raise FileNotFoundError("קובץ הסכמה schema.sql לא נמצא בתיקיית database.")
        
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_script = f.read()

        # שימוש במנהל הקשר (with) מבטיח שהחיבור ייסגר בצורה מסודרת גם במקרה של קריסה
        with self.get_connection() as conn:
            conn.executescript(schema_script)
            conn.commit()

    def get_business_settings(self):
        """
        שולף את הגדרות העסק ממסד הנתונים. מחזיר מילון עם הערכים או ריק אם לא קיימים.
        """
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM business_settings WHERE id = 1").fetchone()
            if row:
                data = dict(row)
                # Parse JSON fields
                for field in ['employees', 'working_hours', 'services']:
                    try:
                        data[field] = json.loads(data[field]) if data[field] else []
                    except json.JSONDecodeError:
                        data[field] = [] if field != 'working_hours' else {}
                return data
            return {}

    def update_business_settings(self, settings_data):
        """
        מעדכן או יוצר את הגדרות העסק בטבלה.
        """
        # Serialize JSON fields
        employees_json = json.dumps(settings_data.get('employees', []), ensure_ascii=False)
        hours_json = json.dumps(settings_data.get('working_hours', {}), ensure_ascii=False)
        services_json = json.dumps(settings_data.get('services', []), ensure_ascii=False)

        with self.get_connection() as conn:
            # בדיקה האם כבר קיימת רשומה
            row = conn.execute("SELECT id FROM business_settings WHERE id = 1").fetchone()
            if row:
                # עדכון
                conn.execute('''
                    UPDATE business_settings
                    SET name = ?, address = ?, phone = ?, description = ?, employees = ?, working_hours = ?, services = ?
                    WHERE id = 1
                ''', (
                    settings_data.get('name', ''),
                    settings_data.get('address', ''),
                    settings_data.get('phone', ''),
                    settings_data.get('description', ''),
                    employees_json,
                    hours_json,
                    services_json
                ))
            else:
                # יצירה
                conn.execute('''
                    INSERT INTO business_settings (id, name, address, phone, description, employees, working_hours, services)
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    settings_data.get('name', ''),
                    settings_data.get('address', ''),
                    settings_data.get('phone', ''),
                    settings_data.get('description', ''),
                    employees_json,
                    hours_json,
                    services_json
                ))
            conn.commit()