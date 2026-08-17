# core/crm_manager.py

import sqlite3

class CRMManager:
    """
    מנהל הלוגיקה העסקית ללקוחות ולידים (Customer Relationship Management).
    מחלקה זו מתווכת בין פקודות המשתמש לבין מנהל בסיס הנתונים תוך שמירה על שלמות המידע.
    """
    def __init__(self, db_manager):
        # קבלת מופע של מנהל הנתונים לצורך הפקת התחברויות לביצוע שאילתות
        self.db = db_manager

    # ==========================
    # מודול ניהול לקוחות קיימים
    # ==========================
    
    def add_client(self, name, phone, email, address):
        """מוסיף לקוח חדש. השימוש בפרמטרים עם סמן השאלה מגן מפני SQL Injection."""
        query = "INSERT INTO clients (name, phone, email, address) VALUES (?, ?, ?, ?)"
        with self.db.get_connection() as conn:
            conn.execute(query, (name, phone, email, address))
            conn.commit()

    def get_all_clients(self):
        """שולף את כלל הלקוחות הפעילים (שלא סומנו כמחוקים דרך מנגנון המחיקה הרכה)."""
        query = "SELECT * FROM clients WHERE is_deleted = 0"
        with self.db.get_connection() as conn:
            return conn.execute(query).fetchall()

    def delete_client(self, client_id):
        """
        מוחק לקוח מהמערכת באמצעות 'מחיקה רכה' (עדכון דגל אינדיקציה). 
        הטריגר במסד הנתונים ידאג לסמן במקביל גם את הרשומות המקושרות (תורים/חשבוניות).
        """
        query = "UPDATE clients SET is_deleted = 1 WHERE id = ?"
        with self.db.get_connection() as conn:
            conn.execute(query, (client_id,))
            conn.commit()

    def get_deleted_clients(self):
        """שולף את כלל הלקוחות שנמחקו מהמערכת."""
        query = "SELECT * FROM clients WHERE is_deleted = 1"
        with self.db.get_connection() as conn:
            return conn.execute(query).fetchall()

    def restore_client(self, client_id):
        """
        משחזר לקוח מחוק ומחזיר גם את כל התורים והחשבוניות שנמחקו איתו.
        מתבצע כטרנזקציה לשמירה על שלמות המידע.
        """
        query_client = "UPDATE clients SET is_deleted = 0 WHERE id = ?"
        query_apps = "UPDATE appointments SET is_deleted = 0 WHERE client_id = ?"
        query_invs = "UPDATE invoices SET is_deleted = 0 WHERE client_id = ?"
        with self.db.get_connection() as conn:
            try:
                conn.execute(query_client, (client_id,))
                conn.execute(query_apps, (client_id,))
                conn.execute(query_invs, (client_id,))
                conn.commit()
            except sqlite3.Error as e:
                conn.rollback()
                raise Exception(f"שגיאה בעת שחזור הלקוח: {e}")

    # ==========================
    # מודול ניהול לידים (פניות)
    # ==========================
    
    def add_lead(self, name, phone, source, notes):
        query = "INSERT INTO leads (name, phone, source, notes) VALUES (?, ?, ?, ?)"
        with self.db.get_connection() as conn:
            conn.execute(query, (name, phone, source, notes))
            conn.commit()

    def update_lead_status(self, lead_id, new_status):
        query = "UPDATE leads SET status = ? WHERE id = ?"
        with self.db.get_connection() as conn:
            conn.execute(query, (new_status, lead_id))
            conn.commit()

    def get_all_leads(self):
        query = "SELECT * FROM leads WHERE is_deleted = 0"
        with self.db.get_connection() as conn:
            return conn.execute(query).fetchall()

    def convert_lead_to_client(self, lead_id):
        """
        המרת ליד ללקוח - תהליך רגיש המבוצע כיחידה טרנזקציונית אחת.
        במידה ואחת מהפעולות נכשלת, פקודת ה-rollback תבטל את כל השינויים שבוצעו, למניעת נתונים סותרים.
        """
        select_lead = "SELECT name, phone FROM leads WHERE id = ? AND is_deleted = 0"
        insert_client = "INSERT INTO clients (name, phone) VALUES (?, ?)"
        update_lead = "UPDATE leads SET status = 'הפך ללקוח' WHERE id = ?"

        with self.db.get_connection() as conn:
            try:
                lead = conn.execute(select_lead, (lead_id,)).fetchone()
                if not lead:
                    raise ValueError("ליד לא נמצא במערכת (או שנמחק) ולכן לא ניתן להמירו.")
                
                conn.execute(insert_client, (lead['name'], lead['phone']))
                conn.execute(update_lead, (lead_id,))
                
                conn.commit()
            
            except sqlite3.Error as e:
                conn.rollback()
                raise Exception(f"שגיאה חמורה בעת המרת הליד, השינויים בוטלו. פירוט טכני: {e}")