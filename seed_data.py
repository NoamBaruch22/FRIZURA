import sqlite3
from database.db_manager import DBManager

def seed():
    db = DBManager()
    
    with db.get_connection() as conn:
        print("Clearing existing data...")
        conn.execute("DELETE FROM appointments")
        conn.execute("DELETE FROM invoices")
        conn.execute("DELETE FROM leads")
        conn.execute("DELETE FROM clients")
        
        print("Inserting mock clients...")
        clients = [
            ("דניאל כהן", "050-1234567", "daniel@example.com", "תל אביב", 0),
            ("יעל אברהם", "052-9876543", "yael@example.com", "חיפה", 0),
            ("משה לוי", "054-1112233", "moshe@example.com", "ירושלים", 0),
            ("רותם ישראלי", "053-4445566", "rotem@example.com", "באר שבע", 1)  # לקוח מחוק
        ]
        
        for c in clients:
            conn.execute("INSERT INTO clients (name, phone, email, address, is_deleted) VALUES (?, ?, ?, ?, ?)", c)
        
        print("Inserting mock leads...")
        leads = [
            ("נועה בר", "050-9998877", "פייסבוק", "מתעניינת בייעוץ", "חדש", 0),
            ("יוסי גרין", "052-3334455", "חבר מביא חבר", "מעוניין בתספורת דחוף", "בטיפול", 0),
            ("אבי כץ", "054-6667788", "גוגל", "לא ענה לשיחה", "אין מענה", 1) # ליד מחוק
        ]
        for l in leads:
            conn.execute("INSERT INTO leads (name, phone, source, notes, status, is_deleted) VALUES (?, ?, ?, ?, ?, ?)", l)
            
        print("Inserting mock appointments...")
        # נניח ש-id 1 הוא דניאל, 2 זו יעל, 3 זה משה, 4 זו רותם (לקוח מחוק)
        apps = [
            (1, "תספורת", "2026-08-10", "10:00", "ממתין", 0),
            (1, "ייעוץ", "2026-08-12", "14:00", "ממתין", 0),
            (2, "טיפול", "2026-08-10", "11:30", "ממתין", 0),
            (3, "תספורת", "2026-08-11", "09:00", "בוצע", 0),
            (3, "תספורת", "2026-08-11", "13:00", "בוטל", 0),
            # תור מחוק (למשל של משה)
            (3, "ייעוץ", "2026-08-15", "16:00", "ממתין", 1),
            # תור ללקוח המחוק (רותם) - אמור להיות מחוק גם בגלל שמחיקת הלקוח מוחקת את התור
            (4, "טיפול", "2026-08-18", "12:00", "ממתין", 1)
        ]
        for a in apps:
            conn.execute("INSERT INTO appointments (client_id, service_type, appointment_date, appointment_time, status, is_deleted) VALUES (?, ?, ?, ?, ?, ?)", a)
            
        print("Inserting mock invoices...")
        invs = [
            (1, 150.0, 0),
            (2, 300.0, 0),
            (3, 100.0, 0),
            (3, 50.0, 1), # חשבונית מחוקה
            (4, 200.0, 1) # חשבונית של לקוח מחוק
        ]
        for i in invs:
            conn.execute("INSERT INTO invoices (client_id, amount, is_deleted) VALUES (?, ?, ?)", i)
            
        conn.commit()
        print("Mock data generated successfully!")

if __name__ == '__main__':
    seed()
