# ui/gui.py

import tkinter as tk
import customtkinter as ctk
import json
from tkinter import ttk, messagebox, simpledialog
from database.db_manager import DBManager
from core.crm_manager import CRMManager
from core.operations_manager import OperationsManager

class GUI:
    """
    מנהל הממשק הגרפי (Graphical User Interface) של מערכת לניהול תורים ולקוחות.
    מחלקה זו מהווה תחליף נגיש וידידותי לממשק שורת הפקודה (CLI), ומאפשרת עבודה עם:
    1. טאבים (Notebook) למעבר נוח בין המודולים: תורים, לקוחות, לידים ודוחות היסטוריה.
    2. טבלאות נתונים אינטראקטיביות (Treeview) לתצוגה ברורה וחלקה של המידע.
    3. חלונות קפיצה (Popups/Toplevel) לקליטת נתונים בצורה מבוקרת וידידותית למשתמש.
    """
    def __init__(self):
        # 1. אתחול מנוע מסד הנתונים ושכבות הלוגיקה העסקית (ממש כמו ב-CLI)
        self.db = DBManager()
        self.crm = CRMManager(self.db)
        self.ops = OperationsManager(self.db)

        # 2. יצירת החלון הראשי והגדרת מאפיינים בסיסיים
        self.root = ctk.CTk()
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        self.root.title("מערכת ניהול תורים ולקוחות (GUI) - פרויקט אמצע")
        self.root.geometry("980x660") # מגדיר את הגודל ההתחלילי של החלון בפיקסלים (רוחב X גובה)
        self.root.minsize(800, 500)   # גודל מינימלי למניעת הסתרה של רכיבים בעת הקטנה

        
        # 3. עיצוב וסטייל כללי של מערכת ה-UI
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except tk.TclError:
            pass

        self.listboxes_to_update = []
        self.update_ttk_styles()
        
        # Track appearance mode changes
        try:
            ctk.AppearanceModeTracker.add_add_callback(self.update_ttk_styles)
        except AttributeError:
            # Older CTk versions or private API changed
            pass

        # 4. יצירת מסגרת המערכת המחולקת לתפריט צד (Sidebar) ואזור תוכן מרכזי
        self.system_frame = ctk.CTkFrame(self.root)
        
        self.sidebar_frame = ctk.CTkFrame(self.system_frame, width=220, corner_radius=0)
        self.sidebar_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.main_content_frame = ctk.CTkFrame(self.system_frame, corner_radius=0)
        self.main_content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # לוגו ב-Sidebar
        lbl_logo = ctk.CTkLabel(self.sidebar_frame, text="FRIZURA", font=("Georgia", 28, "bold"), anchor="e", text_color="#3a7ebf")
        lbl_logo.pack(pady=20, padx=20)
        
        self.frames = {}
        
        self.tab_appointments = ctk.CTkFrame(self.main_content_frame)
        self.frames["appointments"] = self.tab_appointments
        
        self.tab_clients = ctk.CTkFrame(self.main_content_frame)
        self.frames["clients"] = self.tab_clients
        
        self.tab_leads = ctk.CTkFrame(self.main_content_frame)
        self.frames["leads"] = self.tab_leads
        
        self.tab_history = ctk.CTkFrame(self.main_content_frame)
        self.frames["history"] = self.tab_history
        
        self.tab_deleted_clients = ctk.CTkFrame(self.main_content_frame)
        self.frames["deleted_clients"] = self.tab_deleted_clients
        
        self.tab_business = ctk.CTkFrame(self.main_content_frame)
        self.frames["business"] = self.tab_business
        
        # כפתורי תפריט צד
        self.create_sidebar_button("📅 ניהול תורים", "appointments")
        self.create_sidebar_button("👥 ניהול לקוחות", "clients")
        self.create_sidebar_button("🌱 ניהול לידים (CRM)", "leads")
        self.create_sidebar_button("📂 היסטוריה ותיק לקוח", "history")
        self.create_sidebar_button("🗑️ ארכיון מחוקים", "deleted_clients")
        self.create_sidebar_button("⚙️ הגדרות העסק", "business")

        # בניית הרכיבים המרכזים בתוך כל טאב
        self._setup_appointments_tab()
        self._setup_clients_tab()
        self._setup_leads_tab()
        self._setup_history_tab()
        self._setup_deleted_clients_tab()
        self._setup_business_tab()
        
        self.show_frame("appointments")

        # טעינה ראשונית של כל הנתונים לתוך הטבלאות
        self.refresh_all()
        self.update_ttk_styles()
        

        # Zoom functionality
        self.current_scaling = 1.0
        self.root.bind("<Command-plus>", self.zoom_in)
        self.root.bind("<Command-equal>", self.zoom_in)
        self.root.bind("<Command-minus>", self.zoom_out)
        self.root.bind("<Control-plus>", self.zoom_in)
        self.root.bind("<Control-equal>", self.zoom_in)
        self.root.bind("<Control-minus>", self.zoom_out)
        self.root.bind("<Control-MouseWheel>", self.zoom_wheel)
        
        # הצגת מסך פתיחה לפני הכניסה למערכת

        self.show_welcome_screen()


    def zoom_in(self, event=None):
        self.current_scaling = min(2.5, self.current_scaling + 0.1)
        ctk.set_widget_scaling(self.current_scaling)
        ctk.set_window_scaling(self.current_scaling)
        
    def zoom_out(self, event=None):
        self.current_scaling = max(0.5, self.current_scaling - 0.1)
        ctk.set_widget_scaling(self.current_scaling)
        ctk.set_window_scaling(self.current_scaling)

    def zoom_wheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def show_welcome_screen(self):

        """מציג מסך פתיחה מעוצב עם השם FRIZURA"""
        self.welcome_frame = ctk.CTkFrame(self.root)
        self.welcome_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # כותרת הארגון - פונט פרימיום
        title_font = ctk.CTkFont(family="Georgia", size=90, weight="bold")
        lbl_title = ctk.CTkLabel(self.welcome_frame, text="FRIZURA", font=title_font, text_color="#2b5f8c", anchor="e")
        lbl_title.pack(pady=(120, 10))
        
        # סלוגן סנס-סריף עדין
        slogan_font = ctk.CTkFont(family="Helvetica", size=22, weight="normal")
        lbl_slogan = ctk.CTkLabel(self.welcome_frame, text="ניהול תורים והנה״ח למספרות בוטיק", font=slogan_font, text_color="#9fa8af", anchor="e")
        lbl_slogan.pack(pady=(0, 70))
        
        # כפתור כניסה אלגנטי
        btn_enter = ctk.CTkButton(
            self.welcome_frame, 
            text="היכנס למערכת", 
            font=("Helvetica", 20, "bold"),
            height=55,
            width=250,
            corner_radius=27,
            command=self.enter_main_system,
            fg_color="#3a7ebf",
            hover_color="#2b5f8c"
        )
        btn_enter.pack()

    def enter_main_system(self):
        """סוגר את מסך הפתיחה ומציג את התפריט הצדדי והתוכן המרכזי"""
        self.welcome_frame.destroy()
        self.system_frame.pack(fill=tk.BOTH, expand=True)

    def create_sidebar_button(self, text, frame_name):
        btn = ctk.CTkButton(
            self.sidebar_frame, 
            text=text, 
            command=lambda: self.show_frame(frame_name), 
            font=("Helvetica", 14), 
            fg_color="transparent", 
            text_color=("black", "white"), 
            hover_color=("#e0e0e0", "#444444"),
            anchor="e"
        )
        btn.pack(pady=5, padx=10, fill=tk.X)

    def show_frame(self, frame_name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[frame_name].pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def update_ttk_styles(self, new_appearance_mode=None):
        """מעדכן את העיצוב של רכיבי ttk (כגון Treeview) כך שיתאימו למצב הנוכחי (Dark/Light)."""
        mode = ctk.get_appearance_mode() if new_appearance_mode is None else new_appearance_mode
        
        if mode == "Dark":
            bg_color = "#333333" # Lighter than #2b2b2b for better readability
            fg_color = "white"
            heading_bg = "#444444"
            selected_bg = "#1f538d"
            border_col = "#444444"
        else:
            bg_color = "#ffffff"
            fg_color = "black"
            heading_bg = "#e0e0e0"
            selected_bg = "#3a7ebf"
            border_col = "#cccccc"
            
        self.style.configure("Treeview", font=("Helvetica", 14), 
                             background=bg_color,
                             foreground=fg_color,
                             rowheight=26,
                             fieldbackground=bg_color,
                             bordercolor=border_col,
                             borderwidth=0)
        self.style.map('Treeview', background=[('selected', selected_bg)])
        
        self.style.configure("Treeview.Heading", font=("Helvetica", 15, "bold"), 
                             background=heading_bg,
                             foreground=fg_color,
                             relief="flat")
        self.style.map("Treeview.Heading", background=[('active', selected_bg)])
        
        # Update listboxes if they exist
        listboxes = getattr(self, "listboxes_to_update", [])
        for lb in listboxes:
            try:
                lb.configure(bg=bg_color, fg=fg_color, selectbackground=selected_bg, selectforeground="white")
            except Exception:
                pass

    def run(self):
        """
        הפעולת הלולאה הראשית של Tkinter להצגה ותפעול החלון הגרפי.
        תוכנית זו נשארת פעילה באוויר ומאזנת לאירועי משתמש (לחיצות עכבר ומקלדת) עד לסגירת החלון.
        """
        self.root.mainloop()

    def refresh_all(self):
        """פונקציה מרוכזת לרענון כללי של הטבלאות ברחבי התוכנה."""
        self.refresh_appointments_table()
        self.refresh_clients_table()
        self.refresh_leads_table()
        self.refresh_history_clients_dropdown()
        self.refresh_deleted_clients_table()

    # ==========================================
    # טאב 1: ניהול תורים (Appointments Module)
    # ==========================================
    
    def _setup_appointments_tab(self):
        """בניית התצוגה של טאב התורים - כולל כותרת, פאנל לחצני פעולה, וטבלת תורים."""
        # פאנל עליון לכפתורים וניהול
        top_frame = ctk.CTkFrame(self.tab_appointments)
        top_frame.pack(fill=tk.X)

        btn_add = ctk.CTkButton(top_frame, text="➕ קבע תור חדש", command=self.open_add_appointment_dialog)
        btn_add.pack(side=tk.RIGHT, padx=5)

        btn_status = ctk.CTkButton(top_frame, text="✏️ עדכן סטטוס תור", command=self.update_appointment_status_dialog)
        btn_status.pack(side=tk.RIGHT, padx=5)

        btn_delete = ctk.CTkButton(top_frame, text="🗑️ מחיקת תור (מחיקה רכה)", command=self.delete_appointment_action)
        btn_delete.pack(side=tk.RIGHT, padx=5)

        btn_deleted_apps = ctk.CTkButton(top_frame, text="📂 תורים מחוקים", command=self.open_deleted_appointments_dialog)
        btn_deleted_apps.pack(side=tk.RIGHT, padx=5)

        btn_refresh = ctk.CTkButton(top_frame, text="🔄 רענן רשימה", command=self.refresh_appointments_table)
        btn_refresh.pack(side=tk.LEFT, padx=5)

        # אזור התצוגה המרכזי המכיל את הטבלה (Treeview) ופס גלילה (Scrollbar)
        tree_frame = ctk.CTkFrame(self.tab_appointments)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)

        # הגדרת עמודות הטבלה: מזהה, שם לקוח, שירות, תאריך, שעה וסטטוס
        columns = ("id", "client", "service", "date", "time", "status")
        self.tree_appointments = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree_appointments["displaycolumns"] = columns[::-1]
        
        # הגדרת כותרות ורוחב לכל עמודה
        self.tree_appointments.heading("id", text="מזהה תור")
        self.tree_appointments.column("id", width=80, anchor=tk.E)

        self.tree_appointments.heading("client", text="שם הלקוח")
        self.tree_appointments.column("client", width=180, anchor=tk.E)

        self.tree_appointments.heading("service", text="סוג השירות")
        self.tree_appointments.column("service", width=160, anchor=tk.E)

        self.tree_appointments.heading("date", text="תאריך התור")
        self.tree_appointments.column("date", width=120, anchor=tk.E)

        self.tree_appointments.heading("time", text="שעה")
        self.tree_appointments.column("time", width=100, anchor=tk.E)

        self.tree_appointments.heading("status", text="סטטוס תור")
        self.tree_appointments.column("status", width=120, anchor=tk.E)

        # הוספת סרגל גלילה אנכי (Scrollbar) בצד הטבלה במקרה של תורים רבים
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_appointments.yview)
        self.tree_appointments.configure(yscroll=scrollbar.set)

        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.tree_appointments.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def refresh_appointments_table(self):
        """שולף את התורים הרלוונטיים ממנהל התפעול (OperationsManager) ומציג בטבלה."""
        # ניקוי השורות הקודמות בטבלה
        for row in self.tree_appointments.get_children():
            self.tree_appointments.delete(row)
            
        try:
            apps = self.ops.get_all_appointments()
            for app in apps:
                # הזנת רשומת התור לתוך ה-Treeview. נתמך במבנה sqlite3.Row של הסבר
                self.tree_appointments.insert("", tk.END, values=(
                    app["id"],
                    app["name"],
                    app["service_type"],
                    app["appointment_date"],
                    app["appointment_time"],
                    app["status"]
                ))
        except Exception as e:
            messagebox.showerror("שגיאה בטעינת תורים", f"אירעה שגיאה: {e}")

    def open_add_appointment_dialog(self):
        """חלון קפיצה (Toplevel Modal) לקביעת תור חדש - בחירה נוחה של לקוח מתוך תפריט."""
        clients = self.crm.get_all_clients()
        if not clients:
            messagebox.showwarning("אין לקוחות במערכת", "עליך ליצור לפחות לקוח אחד במערכת לפני שיהיה ניתן לקבע לו תור!")
            return

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("קביעת תור חדש")
        dialog.geometry("420x350")
        dialog.transient(self.root)      # קושר את החלון החדש לחלון האב
        dialog.grab_set()                # מונע לחיצות על החלון הראשי עד לסיום או סגירת חלון הקפיצה

        ctk.CTkLabel(dialog, text="בחר לקוח:", font=("Helvetica", 14), anchor="e").pack(anchor=tk.E, padx=20, pady=(15, 5))
        
        # בניית תפריט בחירה נוח המציג את שמו ומספרו של הלקוח
        client_options = [f"ID {c['id']}: {c['name']} ({c['phone']})" for c in clients]
        combo_client = ctk.CTkComboBox(dialog, values=client_options)
        if client_options: combo_client.set(client_options[0])
        combo_client.pack(fill=tk.X, padx=20)

        import datetime
        now = datetime.datetime.now()

        ctk.CTkLabel(dialog, text="סוג שירות:", font=("Helvetica", 14), anchor="e").pack(anchor=tk.E, padx=20, pady=(10, 5))
        settings = self.db.get_business_settings()
        services = settings.get("services", []) if settings else []
        if not services:
            services = ["תספורת", "ייעוץ", "טיפול", "פגישת עבודה", "עיסוי"]
        combo_service = ctk.CTkComboBox(dialog, values=services, justify=tk.RIGHT)
        combo_service.set(services[0])
        combo_service.pack(fill=tk.X, padx=20)

        ctk.CTkLabel(dialog, text="תאריך התור:", font=("Helvetica", 14), anchor="e").pack(anchor=tk.E, padx=20, pady=(10, 5))
        frame_date = ctk.CTkFrame(dialog)
        frame_date.pack(fill=tk.X, padx=20)
        
        years = [str(y) for y in range(now.year, now.year + 5)]
        months = [f"{m:02d}" for m in range(1, 13)]
        days = [f"{d:02d}" for d in range(1, 32)]

        combo_year = ctk.CTkComboBox(frame_date, values=years, width=80, justify=tk.CENTER)
        combo_year.set(str(now.year))
        combo_year.pack(side=tk.RIGHT, padx=2)
        ctk.CTkLabel(frame_date, text="/", anchor="e").pack(side=tk.RIGHT)

        combo_month = ctk.CTkComboBox(frame_date, values=months, width=70, justify=tk.CENTER)
        combo_month.set(f"{now.month:02d}")
        combo_month.pack(side=tk.RIGHT, padx=2)
        ctk.CTkLabel(frame_date, text="/", anchor="e").pack(side=tk.RIGHT)

        combo_day = ctk.CTkComboBox(frame_date, values=days, width=70, justify=tk.CENTER)
        combo_day.set(f"{now.day:02d}")
        combo_day.pack(side=tk.RIGHT, padx=2)

        ctk.CTkLabel(dialog, text="שעת התור:", font=("Helvetica", 14), anchor="e").pack(anchor=tk.E, padx=20, pady=(10, 5))
        frame_time = ctk.CTkFrame(dialog)
        frame_time.pack(fill=tk.X, padx=20)
        
        min_hour, max_hour = 7, 23
        if settings and settings.get("working_hours"):
            wh = settings["working_hours"]
            open_hours = [int(v["open"].split(":")[0]) for v in wh.values() if v.get("is_open") and "open" in v and v["open"]]
            close_hours = [int(v["close"].split(":")[0]) for v in wh.values() if v.get("is_open") and "close" in v and v["close"]]
            if open_hours and close_hours:
                min_hour = min(open_hours)
                max_hour = max(close_hours)
                
        hours = [f"{h:02d}" for h in range(min_hour, max_hour + 1)]
        minutes = ["00", "15", "30", "45"]
        
        combo_minute = ctk.CTkComboBox(frame_time, values=minutes, width=70, justify=tk.CENTER)
        combo_minute.set("00")
        combo_minute.pack(side=tk.RIGHT, padx=2)
        ctk.CTkLabel(frame_time, text=":", anchor="e").pack(side=tk.RIGHT)
        
        combo_hour = ctk.CTkComboBox(frame_time, values=hours, width=70, justify=tk.CENTER)
        combo_hour.set("10")
        combo_hour.pack(side=tk.RIGHT, padx=2)

        def submit():
            service = combo_service.get().strip()
            date_val = f"{combo_year.get()}-{combo_month.get()}-{combo_day.get()}"
            time_val = f"{combo_hour.get()}:{combo_minute.get()}"
            
            if not service or not date_val or not time_val:
                messagebox.showerror("שגיאה בנתונים", "כל השדות חייבים להיות מלאים!", parent=dialog)
                return

            # חילוף זיהוי הלקוח מהאינדקס בתיבת הבחירה (תואם לרשימת clients)
            selected_str = combo_client.get()
            selected_idx = client_options.index(selected_str) if selected_str in client_options else -1
            if selected_idx == -1: return
            client_id = clients[selected_idx]["id"]

            try:
                # הוספת התור דרך הלוגיקה העסקית שתוודא גם שאין חפיפה בין תורים
                self.ops.add_appointment(client_id, service, date_val, time_val)
                messagebox.showinfo("הצלחה!", "התור נקבע בהצלחה ובצורה תקינה במערכת!", parent=dialog)
                self.refresh_appointments_table()
                dialog.destroy()
            except ValueError as ve:
                # טיפול במקרים של ניסיון קביעת תור חופף או שגיאה לוגית
                messagebox.showerror("התראה אודות התור", str(ve), parent=dialog)
            except Exception as e:
                messagebox.showerror("שגיאה חמורה", f"אירעה תקלה בעת שמירת התור: {e}", parent=dialog)

        btn_submit = ctk.CTkButton(dialog, text="✔️ שמור וקבע תור", command=submit)
        btn_submit.pack(pady=20)

    def update_appointment_status_dialog(self):
        """חלון לעדכון סטטוס תור הנבחר מהטבלה."""
        selected_item = self.tree_appointments.selection()
        if not selected_item:
            messagebox.showwarning("בחירה חסרה", "אנא בחר תחילה תור מתוך הטבלה על מנת לעדכנו!")
            return

        item_data = self.tree_appointments.item(selected_item[0])["values"]
        app_id, client_name = item_data[0], item_data[1]

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("עדכון סטטוס תור")
        dialog.geometry("340x220")
        dialog.transient(self.root)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"עדכון עבור תור מזהה {app_id} - {client_name}", font=("Helvetica", 14), anchor="e").pack(pady=12)
        ctk.CTkLabel(dialog, text="בחר את הסטטוס החדש המבוקש:", anchor="e").pack(pady=5)

        combo_status = ctk.CTkComboBox(dialog, values=["ממתין", "בוצע", "בוטל"])
        combo_status.set(item_data[5]) # סטטוס נוכחי
        combo_status.pack(fill=tk.X, padx=30, pady=10)

        def confirm_update():
            new_status = combo_status.get()
            try:
                self.ops.update_appointment_status(app_id, new_status)
                messagebox.showinfo("עודכן", f"הסטטוס שונה ל-'{new_status}' בהצלחה!", parent=dialog)
                self.refresh_appointments_table()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("שגיאה", str(e), parent=dialog)

        ctk.CTkButton(dialog, text="💾 שמור סטטוס", command=confirm_update).pack(pady=10)

    def delete_appointment_action(self):
        """פעולה למחיקה רכה של תור נבחר בטבלה תוך הצגת הודעת אישור."""
        selected_item = self.tree_appointments.selection()
        if not selected_item:
            messagebox.showwarning("בחירה חסרה", "אנא בחר תור מתוך הטבלה שברצונך למחוק.")
            return

        app_id = self.tree_appointments.item(selected_item[0])["values"][0]
        if messagebox.askyesno("אישור מחיקת תור", "האם אתה בטוח שברצונך למחוק תור זה מהלוח? (התור יישמר כארכיון מחיקה רכה בלבד)"):
            try:
                self.ops.delete_appointment(app_id)
                messagebox.showinfo("נמחק בהצלחה", "התור הוסר מהלוח המרכזי.")
                self.refresh_appointments_table()
            except Exception as e:
                messagebox.showerror("שגיאה", str(e))

    def open_deleted_appointments_dialog(self):
        """פותח חלון נפרד המציג את כל התורים המחוקים (ארכיון תורים)."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("ארכיון תורים מחוקים")
        dialog.geometry("700x400")
        dialog.transient(self.root)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="רשימת כל התורים המחוקים במערכת:", font=("Helvetica", 14), anchor="e", text_color="#d32f2f").pack(pady=10)

        tree_frame = ctk.CTkFrame(dialog)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("id", "client", "service", "date", "time", "status")
        tree_deleted_apps = ttk.Treeview(tree_frame, columns=columns, show="headings")
        tree_deleted_apps["displaycolumns"] = columns[::-1]
        
        tree_deleted_apps.heading("id", text="מזהה תור")
        tree_deleted_apps.column("id", width=80, anchor=tk.E)
        tree_deleted_apps.heading("client", text="שם הלקוח")
        tree_deleted_apps.column("client", width=180, anchor=tk.E)
        tree_deleted_apps.heading("service", text="סוג השירות")
        tree_deleted_apps.column("service", width=160, anchor=tk.E)
        tree_deleted_apps.heading("date", text="תאריך התור")
        tree_deleted_apps.column("date", width=120, anchor=tk.E)
        tree_deleted_apps.heading("time", text="שעה")
        tree_deleted_apps.column("time", width=100, anchor=tk.E)
        tree_deleted_apps.heading("status", text="סטטוס תור")
        tree_deleted_apps.column("status", width=120, anchor=tk.E)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree_deleted_apps.yview)
        tree_deleted_apps.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        tree_deleted_apps.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        try:
            apps = self.ops.get_deleted_appointments()
            for app in apps:
                tree_deleted_apps.insert("", tk.END, values=(
                    app["id"],
                    app["name"],
                    app["service_type"],
                    app["appointment_date"],
                    app["appointment_time"],
                    app["status"] + " (נמחק)"
                ))
        except Exception as e:
            messagebox.showerror("שגיאה בטעינת תורים מחוקים", f"אירעה שגיאה: {e}", parent=dialog)

        ctk.CTkButton(dialog, text="סגור חלון", command=dialog.destroy).pack(pady=10)
    # ==========================================
    # טאב 2: ניהול לקוחות (Clients Module)
    # ==========================================
    
    def _setup_clients_tab(self):
        """הגדרת טאב הלקוחות במערכת - תצוגה, הוספה, ומחיקה רכה."""
        top_frame = ctk.CTkFrame(self.tab_clients)
        top_frame.pack(fill=tk.X)

        btn_add = ctk.CTkButton(top_frame, text="👤 הוסף לקוח חדש", command=self.open_add_client_dialog)
        btn_add.pack(side=tk.RIGHT, padx=5)

        btn_invoice = ctk.CTkButton(top_frame, text="🧾 הפק חשבונית מס ללקוח", command=self.open_create_invoice_for_selected_client)
        btn_invoice.pack(side=tk.RIGHT, padx=5)

        btn_del = ctk.CTkButton(top_frame, text="🗑️ מחק לקוח", command=self.delete_client_action)
        btn_del.pack(side=tk.RIGHT, padx=5)

        btn_ref = ctk.CTkButton(top_frame, text="🔄 רענן רשימה", command=self.refresh_clients_table)
        btn_ref.pack(side=tk.LEFT, padx=5)

        tree_frame = ctk.CTkFrame(self.tab_clients)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)

        columns = ("id", "name", "phone", "email", "address", "created_at")
        self.tree_clients = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree_clients["displaycolumns"] = columns[::-1]
        
        self.tree_clients.heading("id", text="ID")
        self.tree_clients.column("id", width=50, anchor=tk.E)

        self.tree_clients.heading("name", text="שם הלקוח")
        self.tree_clients.column("name", width=160, anchor=tk.E)

        self.tree_clients.heading("phone", text="מספר טלפון")
        self.tree_clients.column("phone", width=120, anchor=tk.E)

        self.tree_clients.heading("email", text="כתובת אימייל")
        self.tree_clients.column("email", width=180, anchor=tk.E)

        self.tree_clients.heading("address", text="כתובת מגורים")
        self.tree_clients.column("address", width=180, anchor=tk.E)

        self.tree_clients.heading("created_at", text="תאריך רישום")
        self.tree_clients.column("created_at", width=140, anchor=tk.E)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_clients.yview)
        self.tree_clients.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.tree_clients.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def refresh_clients_table(self):
        """טעינת רשימת הלקוחות שלא נמחקו (is_deleted=0) והצגתם בטבלה."""
        for row in self.tree_clients.get_children():
            self.tree_clients.delete(row)
        try:
            clients = self.crm.get_all_clients()
            for c in clients:
                self.tree_clients.insert("", tk.END, values=(
                    c["id"], c["name"], c["phone"], c["email"] or "", c["address"] or "", c["created_at"]
                ))
            # דואגים לרענן במקביל גם את תיבת תפריט הבחירה בטאב ההיסטוריה
            self.refresh_history_clients_dropdown()
        except Exception as e:
            messagebox.showerror("שגיאה", f"כשל בטעינת לקוחות: {e}")

    def open_add_client_dialog(self):
        """טופס הזנת פרטי לקוח חדש ושמידתו במערכת ה-CRM."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("הוספת לקוח חדש")
        dialog.geometry("400x340")
        dialog.transient(self.root)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="שם מלא (חובה):", anchor="e", font=("Helvetica", 14)).pack(anchor=tk.E, padx=20, pady=(15, 4))
        ent_name = ctk.CTkEntry(dialog, justify="right", width=200)
        ent_name.pack(fill=tk.X, padx=20)

        ctk.CTkLabel(dialog, text="טלפון ליצירת קשר (חובה):", anchor="e", font=("Helvetica", 14)).pack(anchor=tk.E, padx=20, pady=(10, 4))
        ent_phone = ctk.CTkEntry(dialog, justify="right", width=200)
        ent_phone.pack(fill=tk.X, padx=20)

        ctk.CTkLabel(dialog, text="אימייל (אופציונלי):", anchor="e").pack(anchor=tk.E, padx=20, pady=(10, 4))
        ent_email = ctk.CTkEntry(dialog, justify="right", width=200)
        ent_email.pack(fill=tk.X, padx=20)

        ctk.CTkLabel(dialog, text="כתובת (אופציונלי):", anchor="e").pack(anchor=tk.E, padx=20, pady=(10, 4))
        ent_addr = ctk.CTkEntry(dialog, justify="right", width=200)
        ent_addr.pack(fill=tk.X, padx=20)

        def save_client():
            name = ent_name.get().strip()
            phone = ent_phone.get().strip()
            email = ent_email.get().strip()
            addr = ent_addr.get().strip()

            if not name or not phone:
                messagebox.showerror("שגיאה", "שם וטלפון הינם שדי מפתח שהינם בגדר חובה!", parent=dialog)
                return

            try:
                self.crm.add_client(name, phone, email, addr)
                messagebox.showinfo("הצלחה", f"הלקוח '{name}' נוסף בהצלחה למערכת!", parent=dialog)
                self.refresh_clients_table()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("שגית מערכת", str(e), parent=dialog)

        ctk.CTkButton(dialog, text="✔️ שמור לקוח במערכת", command=save_client).pack(pady=20)

    def delete_client_action(self):
        """מחיקת לקוח (מחיקה רכה) המפעילה טריגר בבסיס הנתונים שימחק גם את תוריו."""
        selected = self.tree_clients.selection()
        if not selected:
            messagebox.showwarning("בחירה חסרה", "אנא בחר תחילה לקוח מתוך הטבלה לשם מחיקתו.")
            return

        c_data = self.tree_clients.item(selected[0])["values"]
        client_id, name = c_data[0], c_data[1]

        msg = (f"האם אתה בטוח שברצונך למחוק את הלקוח '{name}' (ID {client_id})?\n\n"
               "שים לב: הודעה זו תבצע מחיקה רכה שבעקבותיה כל תוריו של הלקוח ייסגרו וימחקו גם כן באופן מדורג (Trigger Cascade)!")
        
        if messagebox.askyesno("אזהרת מחיקת לקוח", msg):
            try:
                self.crm.delete_client(client_id)
                messagebox.showinfo("בוטל", "הלקוח נמחק בהצלחה ממסוף התצוגה.")
                self.refresh_clients_table()
                self.refresh_appointments_table() # מרענן את טבלת התורים שיתכן שהורדה מהם רשומות
            except Exception as e:
                messagebox.showerror("שגיאה", str(e))

    def open_create_invoice_for_selected_client(self):
        """מעבר לטופס הפקת חשבונית עבור הלקוח הנבחר כרגע בטבלה."""
        selected = self.tree_clients.selection()
        if not selected:
            messagebox.showwarning("בחירה חסרה", "אנא בחר קודם לקוח מתוך הרשימה עבורו ברצונך להפיק חשבונית.")
            return

        c_data = self.tree_clients.item(selected[0])["values"]
        client_id, client_name = c_data[0], c_data[1]
        self.open_invoice_dialog(client_id, client_name)

    def open_invoice_dialog(self, client_id, client_name):
        """חלון קפיצה להפקת חשבונית תשלום מס ללקוח."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"הפקת חשבונית מס ללקוח: {client_name}")
        dialog.geometry("360x220")
        dialog.transient(self.root)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"הפקת חשבונית עבור: {client_name} (ID: {client_id})", font=("Helvetica", 14)).pack(pady=15)
        ctk.CTkLabel(dialog, text="הזן סכום לתשלום בש״ח:", anchor="e").pack(anchor=tk.E, pady=5)
        
        ent_amount = ctk.CTkEntry(dialog, justify="right", width=150)
        ent_amount.insert(0, "150.0")
        ent_amount.pack(pady=5)

        def confirm_invoice():
            try:
                val = float(ent_amount.get().strip())
                if val <= 0:
                    raise ValueError("הסכום חייב להיות גדול מ-0.")
            except ValueError:
                messagebox.showerror("שגיאת קלט", "אנא הזן סכום כספי מספרי חוקי בשקלים חדשים.", parent=dialog)
                return

            try:
                inv_id = self.ops.create_invoice(client_id, val)
                messagebox.showinfo("החשבונית הופקה בהצלחה!", f"חשבונית מס' {inv_id} הופקה ונשמרה במערכת על סך {val:.2f} ש״ח.", parent=dialog)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("שגיאת מסד נתונים", str(e), parent=dialog)

        ctk.CTkButton(dialog, text="✔️ החתם והפק חשבונית", command=confirm_invoice).pack(pady=15)

    # ==========================================
    # טאב 3: מודול לניהול לידים (Leads CRM Module)
    # ==========================================
    
    def _setup_leads_tab(self):
        """הקמת מסך ניהול הלידים וההעברה שלהם לטבלת לקוחות משלמים בעת סגירה."""
        top_frame = ctk.CTkFrame(self.tab_leads)
        top_frame.pack(fill=tk.X)

        btn_add = ctk.CTkButton(top_frame, text="🌱 הוסף ליד חדש", command=self.open_add_lead_dialog)
        btn_add.pack(side=tk.RIGHT, padx=5)

        btn_convert = ctk.CTkButton(top_frame, text="✨ המר ליד ללקוח משלם!", command=self.convert_lead_action)
        btn_convert.pack(side=tk.RIGHT, padx=5)

        btn_status = ctk.CTkButton(top_frame, text="✏️ עדכן סטטוס מעקב", command=self.update_lead_status_action)
        btn_status.pack(side=tk.RIGHT, padx=5)

        btn_ref = ctk.CTkButton(top_frame, text="🔄 רענן לידים", command=self.refresh_leads_table)
        btn_ref.pack(side=tk.LEFT, padx=5)

        tree_frame = ctk.CTkFrame(self.tab_leads)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)

        columns = ("id", "name", "phone", "source", "status", "notes")
        self.tree_leads = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree_leads["displaycolumns"] = columns[::-1]
        
        self.tree_leads.heading("id", text="מזהה ליד")
        self.tree_leads.column("id", width=70, anchor=tk.E)

        self.tree_leads.heading("name", text="שם הליד / קשר")
        self.tree_leads.column("name", width=160, anchor=tk.E)

        self.tree_leads.heading("phone", text="טלפון ליצירת קשר")
        self.tree_leads.column("phone", width=130, anchor=tk.E)

        self.tree_leads.heading("source", text="מקור גיוס (קמפיין)")
        self.tree_leads.column("source", width=140, anchor=tk.E)

        self.tree_leads.heading("status", text="סטטוס מעקב")
        self.tree_leads.column("status", width=120, anchor=tk.E)

        self.tree_leads.heading("notes", text="הערות")
        self.tree_leads.column("notes", width=200, anchor=tk.E)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_leads.yview)
        self.tree_leads.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.tree_leads.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def refresh_leads_table(self):
        """רענון הטבלה עם כלל הלידים הרלוונטיים ממסד הנתונים."""
        for row in self.tree_leads.get_children():
            self.tree_leads.delete(row)
        try:
            leads = self.crm.get_all_leads()
            for l in leads:
                self.tree_leads.insert("", tk.END, values=(
                    l["id"], l["name"], l["phone"], l["source"] or "", l["status"], l["notes"] or ""
                ))
        except Exception as e:
            messagebox.showerror("שגיאה", f"תקלה בשליפת הלידים: {e}")

    def open_add_lead_dialog(self):
        """חלון לקליטת ליד חדש (לקוח פוטנציאלי)."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("הוספת ליד חדש למעקב")
        dialog.geometry("380x350")
        dialog.transient(self.root)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="שם הליד (חובה):", anchor="e", font=("Helvetica", 14)).pack(anchor=tk.E, padx=20, pady=(15, 4))
        ent_name = ctk.CTkEntry(dialog, justify="right", width=200)
        ent_name.pack(fill=tk.X, padx=20)

        ctk.CTkLabel(dialog, text="טלפון (חובה):", anchor="e", font=("Helvetica", 14)).pack(anchor=tk.E, padx=20, pady=(10, 4))
        ent_phone = ctk.CTkEntry(dialog, justify="right", width=200)
        ent_phone.pack(fill=tk.X, padx=20)

        ctk.CTkLabel(dialog, text="מקור הגעה (פייסבוק / גוגל / חבר):", anchor="e").pack(anchor=tk.E, padx=20, pady=(10, 4))
        ent_src = ctk.CTkEntry(dialog, justify="right", width=200)
        ent_src.pack(fill=tk.X, padx=20)

        ctk.CTkLabel(dialog, text="הערות ראשוניות:", anchor="e").pack(anchor=tk.E, padx=20, pady=(10, 4))
        ent_notes = ctk.CTkEntry(dialog, justify="right", width=200)
        ent_notes.pack(fill=tk.X, padx=20)

        def save_lead():
            n = ent_name.get().strip()
            p = ent_phone.get().strip()
            s = ent_src.get().strip()
            notes = ent_notes.get().strip()

            if not n or not p:
                messagebox.showerror("שגיאה", "שם וטלפון הם שדי חובה בהזנת ליד!", parent=dialog)
                return

            try:
                self.crm.add_lead(n, p, s, notes)
                messagebox.showinfo("הצלחה", "הליד נוסף בהצלחה למאגר!", parent=dialog)
                self.refresh_leads_table()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("שגיאת מסד נתונים", str(e), parent=dialog)

        ctk.CTkButton(dialog, text="✔️ הרשם ליד במאגר", command=save_lead).pack(pady=20)

    def convert_lead_action(self):
        """העברת הליד לסטטוס לקוח באמצעות הפעולה הטרנזקציונית convert_lead_to_client שב-CRMManager."""
        selected = self.tree_leads.selection()
        if not selected:
            messagebox.showwarning("בחירה חסרה", "אנא בחר ליד מהטבלה על מנת להמירו ללקוח מן המניין!")
            return

        l_data = self.tree_leads.item(selected[0])["values"]
        lead_id, lead_name, current_status = l_data[0], l_data[1], l_data[4]

        if current_status == "הפך ללקוח":
            messagebox.showinfo("כבר הומר", "ליד זה כבר סומן והומר בעבר ללקוח פעיל!")
            return

        if messagebox.askyesno("אישור המרת ליד ללקוח", f"האם להעביר את הליד '{lead_name}' לטבלת הלקוחות המשלמים? (המערכת תפתח עבורו רשומת לקוח באופן אוטומטי ותשנה את הסטטוס שלו)"):
            try:
                self.crm.convert_lead_to_client(lead_id)
                messagebox.showinfo("המרת הליד הושלמה בהצלחה! 🎉", f"הליד '{lead_name}' הומר ללקוח פעיל כעת! כעת תראה אותו בטאב הלקוחות ותוכל לשריין עבורו תורים ולהפיק חשבוניות.")
                self.refresh_leads_table()
                self.refresh_clients_table() # רענן את הלקוחות מידית
            except Exception as e:
                messagebox.showerror("תקלה בעת המרת ליד", str(e))

    def update_lead_status_action(self):
        """עדכון סטטוס ליד באופן גמיש מול תיבת שיח פשוטה."""
        selected = self.tree_leads.selection()
        if not selected:
            messagebox.showwarning("בחירה חסרה", "בחר תחילה ליד כדי לעדכן את סטטוס הטיפול בו.")
            return

        lead_id = self.tree_leads.item(selected[0])["values"][0]
        new_val = simpledialog.askstring("עדכון סטטוס ליד", "הזן את הסטטוס החדש לליד (לדוגמה: בטיפול, אין מענה, לא מעוניין):", parent=self.root)
        if new_val and new_val.strip():
            try:
                self.crm.update_lead_status(lead_id, new_val.strip())
                messagebox.showinfo("הצלחה", "סטטוס הליד עודכן!")
                self.refresh_leads_table()
            except Exception as e:
                messagebox.showerror("שגיאה", str(e))

    # ==========================================
    # טאב 4: דוחות היסטוריה ותיק לקוח (Client History & Invoices Module)
    # ==========================================
    
    def _setup_history_tab(self):
        """טאב המרכז תורים וחשבוניות עבור לקוח נבחר לשם קבלת מבט ברמת תיק הלקוח."""
        # פאנל סינון ופילטור עליון לפי לקוח
        filter_frame = ctk.CTkFrame(self.tab_history)
        filter_frame.pack(fill=tk.X)

        ctk.CTkLabel(filter_frame, text="🔍 בחר לקוח לצפייה בתיק הנתונים שלו:", font=("Helvetica", 14), anchor="e").pack(side=tk.RIGHT, padx=5)
        
        self.combo_history_client = ctk.CTkComboBox(filter_frame, width=200)
        self.combo_history_client.pack(side=tk.RIGHT, padx=10)
        
        btn_show = ctk.CTkButton(filter_frame, text="📂 טען פרטי תיק", command=self.load_client_history)
        btn_show.pack(side=tk.RIGHT, padx=5)

        btn_inv = ctk.CTkButton(filter_frame, text="🧾 הפק חשבונית ללקוח זה", command=self.create_invoice_from_history)
        btn_inv.pack(side=tk.LEFT, padx=5)

        # הקמת אזור מרכזי מפוצל לשתי תתי-טבלאות שונות באמצעות מיכלים (Frames)
        split_frame = ctk.CTkFrame(self.tab_history)
        split_frame.pack(fill=tk.BOTH, expand=True)

        # טבלת תוריו של הלקוח (בחלק העליון של חלון ההיסטוריה)
        lbl_apps = ctk.CTkLabel(split_frame, text="--- היסטוריית תורים שבוצעו או שמתוכננים ---", font=("Helvetica", 14), anchor="e", text_color="#0044cc")
        lbl_apps.pack(anchor=tk.E, pady=(5, 2))

        app_frame = ctk.CTkFrame(split_frame)
        app_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.tree_hist_apps = ttk.Treeview(app_frame, columns=("date", "service", "status"), show="headings", height=6)
        self.tree_hist_apps["displaycolumns"] = ("date", "service", "status")[::-1]
        self.tree_hist_apps.heading("date", text="תאריך ושעה")
        self.tree_hist_apps.heading("service", text="סוג השירות")
        self.tree_hist_apps.heading("status", text="סטטוס התור")
        
        self.tree_hist_apps.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        sb1 = ttk.Scrollbar(app_frame, orient=tk.VERTICAL, command=self.tree_hist_apps.yview)
        self.tree_hist_apps.configure(yscroll=sb1.set)
        sb1.pack(side=tk.LEFT, fill=tk.Y)

        # טבלת החשבוניות (בחלקו התחתון של חלון ההיסטוריה)
        lbl_inv = ctk.CTkLabel(split_frame, text="--- היסטוריית תשלומים והפקת חשבוניות מס ---", font=("Helvetica", 14), anchor="e", text_color="#2e7d32")
        lbl_inv.pack(anchor=tk.E, pady=(10, 2))

        inv_frame = ctk.CTkFrame(split_frame)
        inv_frame.pack(fill=tk.BOTH, expand=True)

        self.tree_hist_invs = ttk.Treeview(inv_frame, columns=("id", "amount", "date"), show="headings", height=5)
        self.tree_hist_invs["displaycolumns"] = ("id", "amount", "date")[::-1]
        self.tree_hist_invs.heading("id", text="מספר חשבונית (ID)")
        self.tree_hist_invs.heading("amount", text="סכום לתשלום (₪)")
        self.tree_hist_invs.heading("date", text="תאריך ומקור החשבונית")
        
        self.tree_hist_invs.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        sb2 = ttk.Scrollbar(inv_frame, orient=tk.VERTICAL, command=self.tree_hist_invs.yview)
        self.tree_hist_invs.configure(yscroll=sb2.set)
        sb2.pack(side=tk.LEFT, fill=tk.Y)

    def refresh_history_clients_dropdown(self):
        """טוען מחדש את רשימת הלקוחות לתפריט הבחירה בטאב ההיסטוריה."""
        clients = self.crm.get_all_clients()
        self.history_clients_list = clients
        options = [f"ID {c['id']}: {c['name']} ({c['phone']})" for c in clients]
        self.combo_history_client.configure(values=options)
        current_val = self.combo_history_client.get()
        if options and current_val not in options:
            self.combo_history_client.set(options[0])

    def load_client_history(self):
        """טוען ומפצל לטבלאות את נתוני הלקוח הנבחר ע"פ הפונקציה get_client_history של OperationsManager."""
        current_val = self.combo_history_client.get()
        options = self.combo_history_client.cget("values")
        idx = options.index(current_val) if options and current_val in options else -1
        if idx == -1 or not self.history_clients_list:
            messagebox.showwarning("אין בחירה", "אנא בחר מתוך התפריט לקוח שברצונך לטעון את פרטיו.")
            return

        client = self.history_clients_list[idx]
        client_id = client["id"]

        # ניקוי הטבלאות
        for r in self.tree_hist_apps.get_children():
            self.tree_hist_apps.delete(r)
        for r in self.tree_hist_invs.get_children():
            self.tree_hist_invs.delete(r)

        try:
            apps, invs = self.ops.get_client_history(client_id)
            for a in apps:
                time_str = f"{a['appointment_date']} | שעה: {a['appointment_time']}"
                self.tree_hist_apps.insert("", tk.END, values=(time_str, a["service_type"], a["status"]))

            for i in invs:
                self.tree_hist_invs.insert("", tk.END, values=(f"#{i['id']}", f"{i['amount']:,.2f} ₪", i["invoice_date"]))

        except Exception as e:
            messagebox.showerror("תקלה בטעינת נתוני לקוח", str(e))

    def create_invoice_from_history(self):
        """מאפשר להפיק חשבונית ישירות עבור הלקוח שנבחר במסך ההיסטוריה ומרענן מידית את התצוגה."""
        current_val = self.combo_history_client.get()
        options = self.combo_history_client.cget("values")
        idx = options.index(current_val) if options and current_val in options else -1
        if idx == -1 or not self.history_clients_list:
            messagebox.showwarning("אין בחירה", "בחר לקוח ברשימה.")
            return

        client = self.history_clients_list[idx]
        self.open_invoice_dialog(client["id"], client["name"])
        # לאחר הסגירה מווסת אירוע עדין לטעינת החשבונית שזה עתה הופקה
        self.root.after(500, self.load_client_history)

    # ==========================================
    # טאב 5: ארכיון לקוחות מחוקים (Deleted Clients Archive)
    # ==========================================
    
    def _setup_deleted_clients_tab(self):
        """הגדרת טאב ארכיון הלקוחות המחוקים - תצוגה ושחזור."""
        top_frame = ctk.CTkFrame(self.tab_deleted_clients)
        top_frame.pack(fill=tk.X)

        btn_restore = ctk.CTkButton(top_frame, text="♻️ שחזר לקוח מחוק", command=self.restore_deleted_client_action)
        btn_restore.pack(side=tk.RIGHT, padx=5)

        btn_ref = ctk.CTkButton(top_frame, text="🔄 רענן רשימה", command=self.refresh_deleted_clients_table)
        btn_ref.pack(side=tk.LEFT, padx=5)

        # אזור עליון - טבלת לקוחות מחוקים
        tree_frame = ctk.CTkFrame(self.tab_deleted_clients)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)

        columns = ("id", "name", "phone", "email", "address", "created_at")
        self.tree_deleted_clients = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)
        self.tree_deleted_clients["displaycolumns"] = columns[::-1]
        
        self.tree_deleted_clients.heading("id", text="ID")
        self.tree_deleted_clients.column("id", width=50, anchor=tk.E)
        self.tree_deleted_clients.heading("name", text="שם הלקוח")
        self.tree_deleted_clients.column("name", width=160, anchor=tk.E)
        self.tree_deleted_clients.heading("phone", text="מספר טלפון")
        self.tree_deleted_clients.column("phone", width=120, anchor=tk.E)
        self.tree_deleted_clients.heading("email", text="כתובת אימייל")
        self.tree_deleted_clients.column("email", width=180, anchor=tk.E)
        self.tree_deleted_clients.heading("address", text="כתובת מגורים")
        self.tree_deleted_clients.column("address", width=180, anchor=tk.E)
        self.tree_deleted_clients.heading("created_at", text="תאריך רישום")
        self.tree_deleted_clients.column("created_at", width=140, anchor=tk.E)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_deleted_clients.yview)
        self.tree_deleted_clients.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.tree_deleted_clients.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # כריכת אירוע בחירה בטבלה כדי לטעון היסטוריה
        self.tree_deleted_clients.bind("<<TreeviewSelect>>", lambda e: self.load_deleted_client_history())

        # אזור תחתון - היסטוריית הלקוח המחוק
        lbl_hist = ctk.CTkLabel(self.tab_deleted_clients, text="--- היסטוריית התורים והחשבוניות של הלקוח המחוק ---", font=("Helvetica", 14), anchor="e", text_color="#d32f2f")
        lbl_hist.pack(anchor=tk.E, padx=10, pady=(10, 2))

        hist_frame = ctk.CTkFrame(self.tab_deleted_clients)
        hist_frame.pack(fill=tk.BOTH, expand=True)

        # טבלת תורים מחוקים של הלקוח
        self.tree_del_apps = ttk.Treeview(hist_frame, columns=("date", "service", "status"), show="headings", height=5)
        self.tree_del_apps["displaycolumns"] = ("date", "service", "status")[::-1]
        self.tree_del_apps.heading("date", text="תאריך ושעה")
        self.tree_del_apps.heading("service", text="סוג השירות")
        self.tree_del_apps.heading("status", text="סטטוס התור")
        self.tree_del_apps.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 5))

        # טבלת חשבוניות מחוקות של הלקוח
        self.tree_del_invs = ttk.Treeview(hist_frame, columns=("id", "amount", "date"), show="headings", height=4)
        self.tree_del_invs["displaycolumns"] = ("id", "amount", "date")[::-1]
        self.tree_del_invs.heading("id", text="מספר חשבונית (ID)")
        self.tree_del_invs.heading("amount", text="סכום לתשלום (₪)")
        self.tree_del_invs.heading("date", text="תאריך החשבונית")
        self.tree_del_invs.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)


    def refresh_deleted_clients_table(self):
        """טעינת רשימת הלקוחות שנמחקו (is_deleted=1) והצגתם בטבלה."""
        for row in self.tree_deleted_clients.get_children():
            self.tree_deleted_clients.delete(row)
        # מנקה גם את טבלאות ההיסטוריה
        for r in self.tree_del_apps.get_children():
            self.tree_del_apps.delete(r)
        for r in self.tree_del_invs.get_children():
            self.tree_del_invs.delete(r)

        try:
            clients = self.crm.get_deleted_clients()
            for c in clients:
                self.tree_deleted_clients.insert("", tk.END, values=(
                    c["id"], c["name"], c["phone"], c["email"] or "", c["address"] or "", c["created_at"]
                ))
        except Exception as e:
            messagebox.showerror("שגיאה", f"כשל בטעינת ארכיון לקוחות: {e}")

    def load_deleted_client_history(self):
        """טוען את היסטוריית הלקוח המחוק שנבחר."""
        selected = self.tree_deleted_clients.selection()
        if not selected:
            return

        c_data = self.tree_deleted_clients.item(selected[0])["values"]
        client_id = c_data[0]

        for r in self.tree_del_apps.get_children():
            self.tree_del_apps.delete(r)
        for r in self.tree_del_invs.get_children():
            self.tree_del_invs.delete(r)

        try:
            # מעבירים include_deleted=True כדי לראות את התורים והחשבוניות שנמחקו איתו
            apps, invs = self.ops.get_client_history(client_id, include_deleted=True)
            for a in apps:
                time_str = f"{a['appointment_date']} | שעה: {a['appointment_time']}"
                status = a["status"] + (" (נמחק)" if a["is_deleted"] else "")
                self.tree_del_apps.insert("", tk.END, values=(time_str, a["service_type"], status))

            for i in invs:
                self.tree_del_invs.insert("", tk.END, values=(f"#{i['id']}", f"{i['amount']:,.2f} ₪", i["invoice_date"]))

        except Exception as e:
            messagebox.showerror("תקלה בטעינת נתוני ארכיון", str(e))

    def restore_deleted_client_action(self):
        """שחזור לקוח מחוק והחזרתו למערכת."""
        selected = self.tree_deleted_clients.selection()
        if not selected:
            messagebox.showwarning("בחירה חסרה", "אנא בחר לקוח מתוך טבלת הארכיון שברצונך לשחזר.")
            return

        c_data = self.tree_deleted_clients.item(selected[0])["values"]
        client_id, name = c_data[0], c_data[1]

        msg = (f"האם אתה בטוח שברצונך לשחזר את הלקוח '{name}' (ID {client_id})?\n\n"
               "פעולה זו תשחזר את הלקוח יחד עם כל התורים והחשבוניות המקושרים אליו ותחזיר אותם לפעילות מלאה במערכת.")
        
        if messagebox.askyesno("אישור שחזור לקוח", msg):
            try:
                self.crm.restore_client(client_id)
                messagebox.showinfo("שוחזר בהצלחה", f"הלקוח '{name}' שוחזר בהצלחה חזרה למערכת יחד עם ההיסטוריה שלו.")
                self.refresh_all()
            except Exception as e:
                messagebox.showerror("שגיאה בשחזור", str(e))

    def _setup_business_tab(self):
        """הקמת ממשק הלשונית של הגדרות העסק (עם תתי-טאבים)."""
        # Container for the notebook
        self.biz_notebook = ctk.CTkTabview(self.tab_business)
        self.biz_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.biz_notebook.add("מידע כללי")
        self.biz_notebook.add("עובדים ושירותים")
        self.biz_notebook.add("שעות פעילות")

        self.biz_tab_general = self.biz_notebook.tab("מידע כללי")
        self.biz_tab_staff = self.biz_notebook.tab("עובדים ושירותים")
        self.biz_tab_hours = self.biz_notebook.tab("שעות פעילות")

        # --- General Tab ---
        gen_frame = ctk.CTkFrame(self.biz_tab_general)
        gen_frame.pack(fill=tk.BOTH, expand=True)

        ctk.CTkLabel(gen_frame, text="שם העסק:", anchor="e").grid(row=0, column=1, sticky="w", pady=5)
        self.entry_biz_name = ctk.CTkEntry(gen_frame, width=250, justify="right")
        self.entry_biz_name.grid(row=0, column=0, sticky="e", pady=5, padx=10)

        ctk.CTkLabel(gen_frame, text="טלפון:", anchor="e").grid(row=1, column=1, sticky="w", pady=5)
        self.entry_biz_phone = ctk.CTkEntry(gen_frame, width=250, justify="right")
        self.entry_biz_phone.grid(row=1, column=0, sticky="e", pady=5, padx=10)

        ctk.CTkLabel(gen_frame, text="כתובת:", anchor="e").grid(row=2, column=1, sticky="w", pady=5)
        self.entry_biz_address = ctk.CTkEntry(gen_frame, width=250, justify="right")
        self.entry_biz_address.grid(row=2, column=0, sticky="e", pady=5, padx=10)

        ctk.CTkLabel(gen_frame, text="תיאור העסק:", anchor="e").grid(row=3, column=1, sticky="nw", pady=5)
        self.text_biz_description = ctk.CTkTextbox(gen_frame, width=250, height=4, font=("Helvetica", 14))
        self.text_biz_description.grid(row=3, column=0, sticky="e", pady=5, padx=10)
        
        gen_frame.grid_columnconfigure(0, weight=1)
        gen_frame.grid_columnconfigure(1, weight=0)

        # --- Staff & Services Tab ---
        staff_frame = ctk.CTkFrame(self.biz_tab_staff)
        staff_frame.pack(fill=tk.BOTH, expand=True)

        # Employees
        ctk.CTkLabel(staff_frame, text="רשימת עובדים:", font=("Helvetica", 14), anchor="e").grid(row=0, column=1, sticky="e", pady=5)
        self.listbox_employees = tk.Listbox(staff_frame, width=30, height=8)
        self.listboxes_to_update.append(self.listbox_employees)
        self.listbox_employees.grid(row=1, column=1, sticky="e", padx=10)
        
        emp_btn_frame = ctk.CTkFrame(staff_frame)
        emp_btn_frame.grid(row=2, column=1, sticky="e", pady=5, padx=10)
        self.entry_new_emp = ctk.CTkEntry(emp_btn_frame, width=150, justify="right")
        self.entry_new_emp.pack(side=tk.RIGHT, padx=5)
        ctk.CTkButton(emp_btn_frame, text="➕ הוסף", command=self.add_employee).pack(side=tk.RIGHT)
        ctk.CTkButton(emp_btn_frame, text="🗑️ הסר", command=self.remove_employee).pack(side=tk.RIGHT, padx=5)

        # Services
        ctk.CTkLabel(staff_frame, text="שירותים מוצעים:", font=("Helvetica", 14), anchor="e").grid(row=0, column=0, sticky="e", pady=5)
        self.listbox_services = tk.Listbox(staff_frame, width=30, height=8)
        self.listboxes_to_update.append(self.listbox_services)
        self.listbox_services.grid(row=1, column=0, sticky="e", padx=10)
        
        srv_btn_frame = ctk.CTkFrame(staff_frame)
        srv_btn_frame.grid(row=2, column=0, sticky="e", pady=5, padx=10)
        self.entry_new_srv = ctk.CTkEntry(srv_btn_frame, width=150, justify="right")
        self.entry_new_srv.pack(side=tk.RIGHT, padx=5)
        ctk.CTkButton(srv_btn_frame, text="➕ הוסף", command=self.add_service).pack(side=tk.RIGHT)
        ctk.CTkButton(srv_btn_frame, text="🗑️ הסר", command=self.remove_service).pack(side=tk.RIGHT, padx=5)

        staff_frame.grid_columnconfigure(0, weight=1)
        staff_frame.grid_columnconfigure(1, weight=1)

        # --- Hours Tab ---
        hours_frame = ctk.CTkFrame(self.biz_tab_hours)
        hours_frame.pack(fill=tk.BOTH, expand=True)
        
        days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"]
        day_keys = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
        
        # Times from 06:00 to 22:00 in 30min intervals
        time_options = [f"{h:02d}:{m:02d}" for h in range(6, 23) for m in (0, 30)]
        
        self.hours_widgets = {} # dict to store references to variables

        ctk.CTkLabel(hours_frame, text="יום", font=("Helvetica", 14), anchor="e").grid(row=0, column=4, sticky="e", padx=5)
        ctk.CTkLabel(hours_frame, text="פתוח?", font=("Helvetica", 14), anchor="e").grid(row=0, column=3, sticky="e", padx=5)
        ctk.CTkLabel(hours_frame, text="שעת פתיחה", font=("Helvetica", 14), anchor="e").grid(row=0, column=2, sticky="e", padx=5)
        ctk.CTkLabel(hours_frame, text="שעת סגירה", font=("Helvetica", 14), anchor="e").grid(row=0, column=1, sticky="e", padx=5)

        for i, (day_name, day_key) in enumerate(zip(days, day_keys)):
            row = i + 1
            ctk.CTkLabel(hours_frame, text=day_name, anchor="e").grid(row=row, column=4, sticky="e", padx=5, pady=5)
            
            is_open_var = tk.BooleanVar(value=True)
            chk = ctk.CTkCheckBox(hours_frame, variable=is_open_var, text="")
            chk.grid(row=row, column=3, sticky="e", padx=5)
            
            combo_open = ctk.CTkComboBox(hours_frame, values=time_options, width=100)
            combo_open.set("09:00")
            combo_open.grid(row=row, column=2, sticky="e", padx=5)
            
            combo_close = ctk.CTkComboBox(hours_frame, values=time_options, width=100)
            combo_close.set("18:00")
            combo_close.grid(row=row, column=1, sticky="e", padx=5)
            
            self.hours_widgets[day_key] = {
                "is_open": is_open_var,
                "open": combo_open,
                "close": combo_close
            }
        
        hours_frame.grid_columnconfigure(0, weight=1)

        # Save Button at the bottom of the main tab
        bottom_frame = ctk.CTkFrame(self.tab_business)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        btn_save = ctk.CTkButton(bottom_frame, text="💾 שמור הגדרות", command=self.save_business_settings)
        btn_save.pack(pady=10)

        self.load_business_settings()

    def add_employee(self):
        val = self.entry_new_emp.get().strip()
        if val:
            self.listbox_employees.insert(tk.END, val)
            self.entry_new_emp.delete(0, tk.END)

    def remove_employee(self):
        sel = self.listbox_employees.curselection()
        if sel:
            self.listbox_employees.delete(sel[0])

    def add_service(self):
        val = self.entry_new_srv.get().strip()
        if val:
            self.listbox_services.insert(tk.END, val)
            self.entry_new_srv.delete(0, tk.END)

    def remove_service(self):
        sel = self.listbox_services.curselection()
        if sel:
            self.listbox_services.delete(sel[0])

    def load_business_settings(self):
        """טעינת הנתונים למסך הגדרות העסק מה-JSON והטבלה."""
        try:
            settings = self.db.get_business_settings()
            
            # General
            self.entry_biz_name.delete(0, tk.END)
            self.entry_biz_name.insert(0, settings.get("name", ""))
            self.entry_biz_phone.delete(0, tk.END)
            self.entry_biz_phone.insert(0, settings.get("phone", ""))
            self.entry_biz_address.delete(0, tk.END)
            self.entry_biz_address.insert(0, settings.get("address", ""))
            self.text_biz_description.delete("1.0", tk.END)
            self.text_biz_description.insert("1.0", settings.get("description", ""))
            
            # Employees
            self.listbox_employees.delete(0, tk.END)
            for emp in settings.get("employees", []):
                self.listbox_employees.insert(tk.END, emp)
                
            # Services
            self.listbox_services.delete(0, tk.END)
            for srv in settings.get("services", []):
                self.listbox_services.insert(tk.END, srv)
                
            # Hours
            hours_data = settings.get("working_hours", {})
            for day_key, widgets in self.hours_widgets.items():
                day_data = hours_data.get(day_key, {})
                widgets["is_open"].set(day_data.get("is_open", True))
                if "open" in day_data: widgets["open"].set(day_data["open"])
                if "close" in day_data: widgets["close"].set(day_data["close"])
            
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בטעינת הגדרות העסק:\n{str(e)}")

    def save_business_settings(self):
        """שמירת נתוני העסק שהוזנו במסך, כולל המרת רשימות ומילונים."""
        # איסוף שעות מתוך המילון
        hours_data = {}
        for day_key, widgets in self.hours_widgets.items():
            hours_data[day_key] = {
                "is_open": widgets["is_open"].get(),
                "open": widgets["open"].get(),
                "close": widgets["close"].get()
            }
            
        # איסוף עובדים ושירותים
        employees = list(self.listbox_employees.get(0, tk.END))
        services = list(self.listbox_services.get(0, tk.END))

        data = {
            "name": self.entry_biz_name.get().strip(),
            "phone": self.entry_biz_phone.get().strip(),
            "address": self.entry_biz_address.get().strip(),
            "description": self.text_biz_description.get("1.0", tk.END).strip(),
            "employees": employees,
            "working_hours": hours_data,
            "services": services
        }
        try:
            self.db.update_business_settings(data)
            messagebox.showinfo("הצלחה", "הגדרות העסק נשמרו בהצלחה!")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בשמירת הגדרות העסק:\n{str(e)}")
