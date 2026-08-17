# run_gui.py
import sys
from pathlib import Path

# מוודא שתיקיית הליבה של הפרויקט מוגדרת בנתיבי הייבוא הרשמיים
sys.path.append(str(Path(__file__).resolve().parent))

from ui.gui import GUI

def main():
    """
    קובץ הפעלה ייעודי וישיר עבור הממשק הגרפי (GUI).
    מקל מאוד על הפעלת התוכנה על ידי הרצה ישרה מהטרמינל או מסביבת העבודה (IDE).
    """
    try:
        print("טוען את הממשק הגרפי (GUI)...")
        app = GUI()
        app.run()
    except Exception as e:
        print(f"שגיאה בעת הפעלת חלון התוכנה הגרפי: {e}")

if __name__ == "__main__":
    main()
