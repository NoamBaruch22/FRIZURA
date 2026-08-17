# core/operations_manager.py
from datetime import datetime

class OperationsManager:
    """
    מנהל התפעול היומיומי של העסק: קביעת תורים, ביטולים, וניהול גבייה באמצעות חשבוניות.
    """
    def __init__(self, db_manager):
        self.db = db_manager

    # ==========================
    # מודול ניהול תורים
    # ==========================
    
    def add_appointment(self, client_id, service_type, app_date, app_time):
        """
        מוסיף תור חדש תוך בדיקה למניעת חפיפת תורים, כאשר הוא מתעלם מתורים שהוגדרו כמבוטלים או נמחקו.
        מוודא שיש מרווח של לפחות 60 דקות מתורים קיימים באותו יום.
        """
        check_query = """
            SELECT appointment_time FROM appointments 
            WHERE appointment_date = ? AND status != 'בוטל' AND is_deleted = 0
        """
        insert_query = """
            INSERT INTO appointments (client_id, service_type, appointment_date, appointment_time) 
            VALUES (?, ?, ?, ?)
        """
        
        new_time = datetime.strptime(app_time, "%H:%M")
        
        with self.db.get_connection() as conn:
            # בדיקה האם קיים תור בטווח של פחות מ-60 דקות
            existing_apps = conn.execute(check_query, (app_date,)).fetchall()
            for app in existing_apps:
                existing_time_str = app['appointment_time']
                existing_time = datetime.strptime(existing_time_str, "%H:%M")
                
                # מרווח מינימלי של 3600 שניות (60 דקות)
                if abs((new_time - existing_time).total_seconds()) < 3600:
                    raise ValueError("התראה: קיים תור קרוב מדי בשעה המבוקשת. נדרש מרווח של לפחות 60 דקות בין תורים.")
            
            # ביצוע רישום התור בפועל
            conn.execute(insert_query, (client_id, service_type, app_date, app_time))
            conn.commit()

    def get_all_appointments(self):
        """
        שולף את כל התורים במערכת ומשלב נתונים מטבלת הלקוחות (JOIN), 
        תוך סינון נתונים שסומנו כנמחקו.
        """
        query = """
            SELECT a.id, c.name, a.service_type, a.appointment_date, a.appointment_time, a.status 
            FROM appointments a
            JOIN clients c ON a.client_id = c.id
            WHERE a.is_deleted = 0 AND c.is_deleted = 0
            ORDER BY a.appointment_date, a.appointment_time
        """
        with self.db.get_connection() as conn:
            return conn.execute(query).fetchall()

    def get_deleted_appointments(self):
        """שולף את התורים המחוקים (is_deleted=1)."""
        query = """
            SELECT a.id, c.name, a.service_type, a.appointment_date, a.appointment_time, a.status 
            FROM appointments a
            JOIN clients c ON a.client_id = c.id
            WHERE a.is_deleted = 1
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """
        with self.db.get_connection() as conn:
            return conn.execute(query).fetchall()

    def update_appointment_status(self, app_id, status):
        query = "UPDATE appointments SET status = ? WHERE id = ?"
        with self.db.get_connection() as conn:
            conn.execute(query, (status, app_id))
            conn.commit()

    def delete_appointment(self, app_id):
        """הפיכת התור ללא זמין באמצעות 'מחיקה רכה' לטובת תיעוד ושמירה על ההיסטוריה."""
        query = "UPDATE appointments SET is_deleted = 1 WHERE id = ?"
        with self.db.get_connection() as conn:
            conn.execute(query, (app_id,))
            conn.commit()

    # ==========================
    # מודול תשלומים וחשבוניות
    # ==========================
    
    def create_invoice(self, client_id, amount):
        """יוצר רשומת חשבונית המקושרת ללקוח. מחזיר את המספר המזהה הייחודי."""
        query = "INSERT INTO invoices (client_id, amount) VALUES (?, ?)"
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (client_id, amount))
            conn.commit()
            return cursor.lastrowid 

    def get_client_history(self, client_id, include_deleted=False):
        """מחזיר מבט כולל על נתוני הלקוח: מערך התורים והחשבוניות. מאפשר בחירה לכלול פריטים מחוקים."""
        if include_deleted:
            apps_query = "SELECT * FROM appointments WHERE client_id = ? ORDER BY appointment_date DESC"
            invs_query = "SELECT * FROM invoices WHERE client_id = ? ORDER BY invoice_date DESC"
        else:
            apps_query = "SELECT * FROM appointments WHERE client_id = ? AND is_deleted = 0 ORDER BY appointment_date DESC"
            invs_query = "SELECT * FROM invoices WHERE client_id = ? AND is_deleted = 0 ORDER BY invoice_date DESC"
        
        with self.db.get_connection() as conn:
            appointments = conn.execute(apps_query, (client_id,)).fetchall()
            invoices = conn.execute(invs_query, (client_id,)).fetchall()
            return appointments, invoices