# שימוש בתמונת בסיס רשמית של אובונטו
FROM ubuntu:22.04

# מניעת חלונות קופצים ושאלות אינטראקטיביות מצד אובונטו בזמן ההתקנה
ENV DEBIAN_FRONTEND=noninteractive

# עדכון חבילות המערכת והתקנת פייתון, מנהל החבילות (pip) ותמיכה ב-SQLite
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# הגדרת תיקיית העבודה בתוך הקונטיינר
WORKDIR /app

# העתקת כל קבצי הפרויקט לתיקיית העבודה
COPY . .

# במידה ויש לך קובץ requirements.txt, הסר את הסולמית מהשורה הבאה כדי להתקין את הספריות:
# RUN pip3 install --no-cache-dir -r requirements.txt

# הפקודה שתרוץ כשהקונטיינר יעלה
CMD ["python3", "__main__.py"]

