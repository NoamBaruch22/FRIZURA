# __main__.py

from ui.gui import GUI

def main():
    """
    נקודת הכניסה הראשית של המערכת.
    מאתחלת את הלולאה הראשית של הממשק הגרפי (GUI).
    """
    try:
        app = GUI()
        app.run()
        
    except KeyboardInterrupt:
        print("\n\nפקודת סיום מזוהה. התוכנית הופסקה על ידי המשתמש. להתראות!")
        
    except Exception as e:
        print(f"\nשגיאה קריטית הופיעה ברמת הליבה, המערכת נאלצת להיסגר: {e}")

if __name__ == "__main__":
    main()
    