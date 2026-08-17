# ui/cli.py

import os
from database.db_manager import DBManager
from core.crm_manager import CRMManager
from core.operations_manager import OperationsManager

class Colors:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class CLI:
    """
    מנהל ממשק שורת הפקודה. מספק לולאה אינטראקטיבית לקבלת פקודות ולהצגת נתונים.
    המחלקה קושרת את כל שכבות הלוגיקה והנתונים לכדי מערכת אחת מתפקדת.
    """
    def __init__(self):
        # אתחול שרשרת התלויות: מסד נתונים -> לוגיקה עסקית -> תצוגה
        self.db = DBManager()
        self.crm = CRMManager(self.db)
        self.ops = OperationsManager(self.db)
        
        # Enables ANSI colors on some Windows environments
        if os.name == 'nt':
            os.system("")

    def clear_screen(self):
        """
        פונקציה חכמה לניקוי המסך בהתאם לסוג מערכת ההפעלה.
        במידה והמערכת מזוהה כ-'nt' (Windows), היא מריצה 'cls', אחרת 'clear' (macOS/Linux).
        """
        os.system('cls' if os.name == 'nt' else 'clear')

    def pause(self):
        input(f"\n{Colors.MAGENTA}לחץ Enter כדי לחזור לתפריט הראשי...{Colors.RESET}")

    def show_welcome_screen(self):
        self.clear_screen()
        logo = f"""{Colors.CYAN}{Colors.BOLD}
  ______ _____  _____ ________  _    _  _____            
 |  ____|  __ \\|_   _|___  / | | |  | ||  __ \\     /\\    
 | |__  | |__) | | |    / /| | | |  | || |__) |   /  \\   
 |  __| |  _  /  | |   / / | | | |  | ||  _  /   / /\\ \\  
 | |    | | \\ \\ _| |_ / /__| |_| |__| || | \\ \\  / ____ \\ 
 |_|    |_|  \\_\\_____/_____|\\___/\\____/ |_|  \\_\\/_/    \\_\\
{Colors.RESET}"""
        print(logo)
        slogan = "ניהול תורים והנה״ח למספרות בוטיק"
        print(f"{Colors.MAGENTA}=========================================================={Colors.RESET}")
        print(f"             {Colors.YELLOW}{Colors.BOLD}{slogan}{Colors.RESET}")
        print(f"{Colors.MAGENTA}=========================================================={Colors.RESET}\n")
        
        # We only want to pause here once on startup
        input(f"{Colors.MAGENTA}לחץ Enter כדי להיכנס למערכת...{Colors.RESET}")

    def run(self):
        """לולאת התוכנית הראשית. מחזיקה את התוכנית באוויר עד בחירה ביציאה."""
        self.show_welcome_screen()
        while True:
            self.clear_screen()
            print(f"{Colors.BLUE}{Colors.BOLD}╔══════════════════════════════════════════════════════╗{Colors.RESET}")
            print(f"{Colors.BLUE}{Colors.BOLD}║      מערכת ניהול תורים ולקוחות (פרויקט אמצע)         ║{Colors.RESET}")
            print(f"{Colors.BLUE}{Colors.BOLD}╚══════════════════════════════════════════════════════╝{Colors.RESET}\n")
            
            print(f"{Colors.CYAN} 1.{Colors.RESET} הוספת לקוח חדש")
            print(f"{Colors.CYAN} 2.{Colors.RESET} הוספת תור חדש (כולל מניעת חפיפת תורים)")
            print(f"{Colors.CYAN} 3.{Colors.RESET} הצגת כל התורים")
            print(f"{Colors.CYAN} 4.{Colors.RESET} עדכון סטטוס תור (ממתין / בוצע / בוטל)")
            print(f"{Colors.CYAN} 5.{Colors.RESET} הסרת תור מהלוח (מחיקה רכה ושמירה בארכיון הפנימי)")
            print(f"{Colors.CYAN} 6.{Colors.RESET} מודול ניהול לידים (הוספה, רשימה והמרה ללקוח)")
            print(f"{Colors.CYAN} 7.{Colors.RESET} הפקת חשבונית מס ללקוח")
            print(f"{Colors.CYAN} 8.{Colors.RESET} צפייה בהיסטוריית לקוח (תורים וחשבוניות מרוכזים)")
            print(f"{Colors.CYAN} 0.{Colors.RESET} יציאה מהמערכת ושמירת נתונים")
            
            print(f"\n{Colors.BLUE}──────────────────────────────────────────────────────{Colors.RESET}")
            choice = input(f"{Colors.YELLOW}בחר פעולה (0-8): {Colors.RESET}")
            
            try:
                # ניתוב התנועה למתודות הרלוונטיות בהתאם לבחירת המשתמש
                if choice == '1':
                    self.add_client_ui()
                elif choice == '2':
                    self.add_appointment_ui()
                elif choice == '3':
                    self.show_appointments_ui()
                elif choice == '4':
                    self.update_app_status_ui()
                elif choice == '5':
                    self.delete_app_ui()
                elif choice == '6':
                    self.leads_menu_ui()
                elif choice == '7':
                    self.create_invoice_ui()
                elif choice == '8':
                    self.client_history_ui()
                elif choice == '0':
                    print(f"\n{Colors.GREEN}הנתונים נשמרו. תודה שהשתמשת במערכת! להתראות.{Colors.RESET}")
                    break
                else:
                    print(f"\n{Colors.RED}בחירה לא חוקית. אנא הזן מספר מהתפריט ונסה שוב.{Colors.RESET}")
                    
            except ValueError as ve:
                # תפיסת שגיאות לוגיות, כגון ניסיון לקביעת תור חופף
                print(f"\n{Colors.RED}שגיאת קלט או לוגיקה במערכת: {ve}{Colors.RESET}")
            except Exception as e:
                # תפיסת שגיאות קריטיות (כגון הפרת אילוצי Database)
                print(f"\n{Colors.RED}שגיאת מערכת חמורה: {e}{Colors.RESET}")
            
            self.pause()

    # ==========================
    # תתי-תפריטים ומסכי קליטת נתונים
    # ==========================
    
    def add_client_ui(self):
        print(f"\n{Colors.CYAN}{Colors.BOLD}-- מסך הוספת לקוח חדש --{Colors.RESET}")
        name = input("שם הלקוח (חובה): ")
        if not name:
            raise ValueError("לא ניתן להוסיף לקוח ללא שם.")
        phone = input("טלפון (חובה): ")
        if not phone:
            raise ValueError("לא ניתן להוסיף לקוח ללא מספר טלפון.")
        email = input("אימייל (אופציונלי, לחץ Enter לדילוג): ")
        address = input("כתובת (אופציונלי, לחץ Enter לדילוג): ")
        self.crm.add_client(name, phone, email, address)
        print(f"\n{Colors.GREEN}✔ הלקוח נוסף בהצלחה למערכת!{Colors.RESET}")

    def add_appointment_ui(self):
        print(f"\n{Colors.CYAN}{Colors.BOLD}-- מסך קביעת תור חדש --{Colors.RESET}")
        client_id = input("מזהה לקוח (ID): ")
        service = input("סוג שירות (למשל תספורת / ייעוץ): ")
        date = input("תאריך (פורמט YYYY-MM-DD): ")
        time = input("שעה (פורמט HH:MM): ")
        
        if not date or not time:
            raise ValueError("תאריך ושעה הם שדות חובה לקביעת תור.")
            
        # השכבה הלוגית תוודא שאין התנגשות תורים ותזרוק שגיאה במידת הצורך
        self.ops.add_appointment(client_id, service, date, time)
        print(f"\n{Colors.GREEN}✔ התור נרשם ונקבע בהצלחה ביומן!{Colors.RESET}")

    def show_appointments_ui(self):
        print(f"\n{Colors.CYAN}{Colors.BOLD}-- רשימת התורים המלאה --{Colors.RESET}")
        apps = self.ops.get_all_appointments()
        if not apps:
            print(f"{Colors.YELLOW}אין תורים עתידיים זמינים במערכת.{Colors.RESET}")
            return
            
        # שימוש ביכולות ה-sqlite3.Row שהוגדרו קודם לכן לצורך קריאה נקייה
        for app in apps:
            print(f"מזהה תור: {Colors.CYAN}{app['id']}{Colors.RESET} | שם לקוח: {Colors.BOLD}{app['name']}{Colors.RESET} | "
                  f"שירות: {app['service_type']} | זמן: {app['appointment_date']} {app['appointment_time']} | "
                  f"סטטוס: {Colors.YELLOW}{app['status']}{Colors.RESET}")

    def update_app_status_ui(self):
        print(f"\n{Colors.CYAN}{Colors.BOLD}-- עדכון סטטוס תור --{Colors.RESET}")
        app_id = input("הכנס מספר מזהה של התור לעדכון: ")
        status = input("הכנס סטטוס חדש (ממתין / בוצע / בוטל): ")
        if status not in ['ממתין', 'בוצע', 'בוטל']:
            raise ValueError("סטטוס לא חוקי. יש לבחור באחת מהאפשרויות בלבד.")
            
        self.ops.update_appointment_status(app_id, status)
        print(f"\n{Colors.GREEN}✔ הסטטוס של התור עודכן בהצלחה במסד הנתונים!{Colors.RESET}")

    def delete_app_ui(self):
        print(f"\n{Colors.CYAN}{Colors.BOLD}-- מחיקת תור --{Colors.RESET}")
        app_id = input("הכנס מספר מזהה של התור להסרה: ")
        self.ops.delete_appointment(app_id)
        print(f"\n{Colors.GREEN}✔ התור הוסר מהתצוגה (אך נשמר בארכיון הנתונים למטרות תיעוד).{Colors.RESET}")

    def leads_menu_ui(self):
        print(f"\n{Colors.CYAN}{Colors.BOLD}-- מודול ניהול לידים (בונוס) --{Colors.RESET}")
        print(f"{Colors.CYAN} 1.{Colors.RESET} הוסף ליד חדש למעקב")
        print(f"{Colors.CYAN} 2.{Colors.RESET} הצג את רשימת כל הלידים הפעילים")
        print(f"{Colors.CYAN} 3.{Colors.RESET} המר ליד קיים ללקוח משלם")
        c = input(f"\n{Colors.YELLOW}בחר פעולה: {Colors.RESET}")
        
        if c == '1':
            n = input("שם הליד: ")
            p = input("טלפון: ")
            s = input("מקור הגעה (פייסבוק/גוגל/וכו'): ")
            self.crm.add_lead(n, p, s, "")
            print(f"\n{Colors.GREEN}✔ הליד נוסף בהצלחה.{Colors.RESET}")
        elif c == '2':
            leads = self.crm.get_all_leads()
            for l in leads:
                print(f"ID: {Colors.CYAN}{l['id']}{Colors.RESET} | שם: {Colors.BOLD}{l['name']}{Colors.RESET} | סטטוס מעקב: {Colors.YELLOW}{l['status']}{Colors.RESET}")
        elif c == '3':
            lead_id = input("הכנס ID של הליד המיועד להמרה ללקוח: ")
            self.crm.convert_lead_to_client(lead_id)
            print(f"\n{Colors.GREEN}✔ הליד הומר ללקוח בהצלחה, וכעת ניתן לקבוע עבורו תורים!{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}פעולה לא חוקית בניהול הלידים.{Colors.RESET}")

    def create_invoice_ui(self):
        print(f"\n{Colors.CYAN}{Colors.BOLD}-- הפקת חשבוניות מס (בונוס) --{Colors.RESET}")
        client_id = input("מזהה לקוח: ")
        try:
            amount = float(input("סכום לתשלום: "))
        except ValueError:
            raise ValueError("הסכום חייב להיות מספרי.")
            
        inv_id = self.ops.create_invoice(client_id, amount)
        print(f"\n{Colors.GREEN}✔ חשבונית מס' {inv_id} הופקה ונשמרה בהצלחה עבור סך {amount} ש״ח.{Colors.RESET}")

    def client_history_ui(self):
        print(f"\n{Colors.CYAN}{Colors.BOLD}-- צפייה בתיק לקוח --{Colors.RESET}")
        client_id = input("הזן מזהה לקוח לקבלת דוח מלא: ")
        apps, invs = self.ops.get_client_history(client_id)
        
        print(f"\n{Colors.BLUE}{Colors.BOLD}--- היסטוריית תורים ---{Colors.RESET}")
        if apps:
            for a in apps:
                print(f"תאריך: {Colors.CYAN}{a['appointment_date']}{Colors.RESET} | שירות: {a['service_type']} | סטטוס: {Colors.YELLOW}{a['status']}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}לא נמצאו תורים עבור לקוח זה.{Colors.RESET}")
            
        print(f"\n{Colors.BLUE}{Colors.BOLD}--- היסטוריית חשבוניות ותשלומים ---{Colors.RESET}")
        if invs:
            for i in invs:
                print(f"מספר חשבונית: {Colors.CYAN}{i['id']}{Colors.RESET} | סכום: {Colors.GREEN}{i['amount']}{Colors.RESET} | תאריך הפקה: {i['invoice_date']}")
        else:
            print(f"{Colors.YELLOW}לא נמצאו תשלומים או חשבוניות עבור לקוח זה.{Colors.RESET}")