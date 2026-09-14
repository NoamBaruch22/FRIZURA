"use client";
import React, { useState } from 'react';
import axios from 'axios';

interface CalendarEvent {
  title: string;
  date: string;
  time: string;
  duration_minutes?: number;
  location?: string;
  description?: string;
}

interface ChatMsg {
  role: string;
  content: string;
  options?: string[];
  calendar_event?: CalendarEvent;
}

export default function CustomerHome() {
  const [messages, setMessages] = useState<ChatMsg[]>([
    { role: 'model', content: 'שלום וברוכים הבאים למספרת FRIZURA! ✂️ איך אוכל לעזור לך היום?', options: ["לקבוע תור", "בדיקת תור קיים", "שעות פעילות", "איזה שירותים יש לכם?"] }
  ]);
  const [input, setInput] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  // Google Calendar URL Generator
  const createGoogleCalendarUrl = (event: CalendarEvent) => {
    try {
      const cleanDate = event.date.replace(/-/g, '');
      const timeParts = (event.time || '10:00').substring(0, 5).split(':');
      const startHours = timeParts[0].padStart(2, '0');
      const startMinutes = timeParts[1].padStart(2, '0');
      
      const startDateTime = `${cleanDate}T${startHours}${startMinutes}00`;
      
      // Calculate end time (default 60 min)
      const duration = event.duration_minutes || 60;
      const startTotalMinutes = parseInt(startHours, 10) * 60 + parseInt(startMinutes, 10);
      const endTotalMinutes = startTotalMinutes + duration;
      const endHours = String(Math.floor(endTotalMinutes / 60) % 24).padStart(2, '0');
      const endMinutes = String(endTotalMinutes % 60).padStart(2, '0');
      const endDateTime = `${cleanDate}T${endHours}${endMinutes}00`;

      const params = new URLSearchParams({
        action: 'TEMPLATE',
        text: event.title || 'תור למספרת FRIZURA',
        dates: `${startDateTime}/${endDateTime}`,
        details: event.description || 'תור למספרת FRIZURA - קפלן 5, אזור. טלפון: 054-2002400',
        location: event.location || 'קפלן 5, אזור'
      });
      return `https://calendar.google.com/calendar/render?${params.toString()}`;
    } catch {
      return 'https://calendar.google.com';
    }
  };

  // Booking Form State
  const [showBooking, setShowBooking] = useState(false);
  const [bookingService, setBookingService] = useState('');
  const [lastBookedEvent, setLastBookedEvent] = useState<CalendarEvent | null>(null);
  const [confirmedAppointment, setConfirmedAppointment] = useState<{
    clientName: string;
    phone: string;
    email: string;
    city?: string;
    service: string;
    employee: string;
    date: string;
    time: string;
    notes?: string;
  } | null>(null);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    email: '',
    city: '',
    service_type: '',
    employee: '',
    notes: '',
    appointment_date: '',
    appointment_time: ''
  });
  const [bookingSuccess, setBookingSuccess] = useState(false);

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '';
    const parts = dateStr.split('-');
    if (parts.length === 3) {
      return `${parts[2]}.${parts[1]}.${parts[0]}`;
    }
    return dateStr;
  };

  const sendMessage = async (text?: string | React.MouseEvent) => {
    // If text is a string (from a button click), use it. Otherwise use the input state.
    const messageContent = typeof text === 'string' ? text : input;
    if (!messageContent.trim()) return;

    // Check if user clicked the "Add to Google Calendar" option button
    if (messageContent.includes("הוסף ליומן Google") || messageContent.includes("הוסף ליומן גוגל")) {
      const lastWithCalendar = [...messages].reverse().find(m => m.calendar_event);
      if (lastWithCalendar?.calendar_event) {
        window.open(createGoogleCalendarUrl(lastWithCalendar.calendar_event), '_blank');
        setMessages(prev => [...prev, 
          { role: 'user', content: 'כן, הוסף ליומן גוגל' },
          { role: 'model', content: 'מעולה! פתחתי עבורך את יומן Google עם כל פרטי הפגישה. נשמח לראותך!' }
        ]);
        return;
      }
    }
    
    const newMessages = [...messages, { role: 'user', content: messageContent }];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);
    
    try {
      const apiUrl = typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000` : 'http://localhost:8000';
      const response = await axios.post(`${apiUrl}/api/chatbot/chat`, {
        phone: "guest",
        messages: newMessages
      });
      setMessages([...newMessages, { 
        role: 'model', 
        content: response.data.reply, 
        options: response.data.options,
        calendar_event: response.data.calendar_event 
      }]);
    } catch (error) {
      console.error(error);
      setMessages([...newMessages, { role: 'model', content: 'מצטערים, המערכת החכמה שלנו חווה כרגע עומס זמני או שגיאת התחברות לשרתי Google. אנא נסה שנית בעוד כמה דקות.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const openBooking = (service: string) => {
    const isWomen = service.includes("נשים");
    const defaultService = isWomen ? "תספורת נשים" : "תספורת גברים";
    const defaultEmployee = isWomen ? "יעל" : "דני";

    setBookingService(service);
    setFormData({
      first_name: '',
      last_name: '',
      phone: '',
      email: '',
      city: '',
      service_type: defaultService,
      employee: defaultEmployee,
      notes: '',
      appointment_date: '',
      appointment_time: ''
    });
    setConfirmedAppointment(null);
    setLastBookedEvent(null);
    setBookingSuccess(false);
    setShowBooking(true);
  };

  const closeBookingModal = () => {
    setShowBooking(false);
    setBookingSuccess(false);
    setConfirmedAppointment(null);
    setLastBookedEvent(null);
    setFormData({
      first_name: '',
      last_name: '',
      phone: '',
      email: '',
      city: '',
      service_type: '',
      employee: '',
      notes: '',
      appointment_date: '',
      appointment_time: ''
    });
  };

  const handleBookingSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    if (!formData.email || !emailRegex.test(formData.email.trim())) {
      alert("אנא הזן כתובת אימייל תקינה (למשל name@example.com).");
      return;
    }
    try {
      const apiUrl = typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000` : 'http://localhost:8000';
      const fullService = `${formData.service_type} (עם: ${formData.employee})`;
      await axios.post(`${apiUrl}/api/appointments/book_public`, {
        first_name: formData.first_name,
        last_name: formData.last_name,
        phone: formData.phone,
        email: formData.email.trim(),
        city: formData.city || undefined,
        service: fullService,
        employee: formData.employee,
        notes: formData.notes || undefined,
        appointment_date: formData.appointment_date,
        appointment_time: formData.appointment_time
      });

      const clientFullName = `${formData.first_name} ${formData.last_name}`;
      setConfirmedAppointment({
        clientName: clientFullName,
        phone: formData.phone,
        email: formData.email.trim(),
        city: formData.city,
        service: formData.service_type,
        employee: formData.employee,
        date: formData.appointment_date,
        time: formData.appointment_time,
        notes: formData.notes
      });

      setLastBookedEvent({
        title: `תור למספרת FRIZURA - ${formData.service_type}`,
        date: formData.appointment_date,
        time: formData.appointment_time,
        duration_minutes: 60,
        location: "קפלן 5, אזור",
        description: `תור למספרת FRIZURA עבור ${clientFullName}. שירות: ${formData.service_type} (ספר/ית: ${formData.employee}). טלפון: 054-2002400.`
      });
      setBookingSuccess(true);
    } catch (err: any) {
      console.error(err);
      if (err.response?.status === 409) {
        alert(err.response?.data?.detail || "השעה תפוסה! קיים כבר תור עבור ספר/ית זה בטווח של שעה מזמן זה. אנא בחר שעה אחרת.");
      } else {
        alert("שגיאה בשליחת הבקשה. אנא ודא שכל הפרטים מולאו כראוי ונסה שנית.");
      }
    }
  };

  return (
    <div dir="rtl" className="min-h-screen bg-[#f5f0e8] text-[#1a2332] font-sans relative">
      {/* Hero Section */}
      <header className="py-20 px-4 text-center bg-[#1a2332] text-white">
        <h1 className="text-7xl md:text-9xl font-serif mb-6 text-[#c9a962] font-black tracking-widest">FRIZURA</h1>
        <p className="text-xl">Boutique Hair Salon</p>
      </header>
      
      {/* Services */}
      <main className="max-w-4xl mx-auto py-12 px-4">
        <h2 className="text-3xl font-serif mb-8 text-center">השירותים שלנו</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-xl shadow hover:shadow-lg transition">
            <h3 className="text-xl font-bold mb-2">תספורת נשים</h3>
            <p className="text-gray-600">עיצוב שיער מקצועי, צבע וגוונים בהתאמה אישית.</p>
            <button onClick={() => openBooking("תספורת נשים")} className="mt-4 px-6 py-2 bg-[#c9a962] text-white rounded-full hover:bg-[#b09355]">קבע תור</button>
          </div>
          <div className="bg-white p-6 rounded-xl shadow hover:shadow-lg transition">
            <h3 className="text-xl font-bold mb-2">תספורת גברים</h3>
            <p className="text-gray-600">תספורת קלאסית, עיצוב זקן ודירוג ברמה הגבוהה ביותר.</p>
            <button onClick={() => openBooking("תספורת גברים")} className="mt-4 px-6 py-2 bg-[#c9a962] text-white rounded-full hover:bg-[#b09355]">קבע תור</button>
          </div>
        </div>
      </main>

      {/* Booking Modal */}
      {showBooking && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-6 md:p-8 max-w-lg w-full relative shadow-2xl max-h-[92vh] overflow-y-auto">
            <button 
              onClick={closeBookingModal} 
              className="absolute top-4 left-4 text-gray-400 hover:text-gray-800 font-bold text-xl w-8 h-8 rounded-full flex items-center justify-center hover:bg-gray-100 transition"
              aria-label="סגור"
            >
              ✕
            </button>
            <h2 className="text-2xl font-bold mb-1 text-[#1a2332]">קביעת תור מקוון</h2>
            <p className="text-gray-500 mb-6 text-sm">מספרת FRIZURA • קפלן 5, אזור</p>
            
            {bookingSuccess && confirmedAppointment ? (
              <div className="text-center py-2 flex flex-col items-center gap-4">
                <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-3xl font-bold shadow-sm">
                  ✓
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">התור נקבע בהצלחה!</h3>
                  <p className="text-gray-600 text-sm mt-1">פרטי התור נרשמו במערכת ונשמרו עבורך</p>
                </div>

                {/* Full Details Card */}
                <div className="w-full bg-[#fbf9f5] border border-amber-200/70 rounded-xl p-4 text-right flex flex-col gap-2.5 text-sm shadow-sm">
                  <div className="flex justify-between items-center border-b pb-2 border-stone-200">
                    <span className="text-gray-500 font-medium">שם לקוח/ה:</span>
                    <span className="font-bold text-gray-900">{confirmedAppointment.clientName}</span>
                  </div>
                  <div className="flex justify-between items-center border-b pb-2 border-stone-200">
                    <span className="text-gray-500 font-medium">סוג שירות:</span>
                    <span className="font-bold text-[#1a2332]">{confirmedAppointment.service}</span>
                  </div>
                  <div className="flex justify-between items-center border-b pb-2 border-stone-200">
                    <span className="text-gray-500 font-medium">ספר/ית מטפל/ת:</span>
                    <span className="font-bold text-[#c9a962] bg-[#1a2332] px-2.5 py-0.5 rounded text-xs">{confirmedAppointment.employee}</span>
                  </div>
                  <div className="flex justify-between items-center border-b pb-2 border-stone-200">
                    <span className="text-gray-500 font-medium">תאריך:</span>
                    <span className="font-bold text-gray-900 font-mono">{formatDate(confirmedAppointment.date)}</span>
                  </div>
                  <div className="flex justify-between items-center border-b pb-2 border-stone-200">
                    <span className="text-gray-500 font-medium">שעה:</span>
                    <span className="font-bold text-gray-900 font-mono text-base">{confirmedAppointment.time}</span>
                  </div>
                  <div className="flex justify-between items-center border-b pb-2 border-stone-200">
                    <span className="text-gray-500 font-medium">כתובת:</span>
                    <span className="font-medium text-gray-800">קפלן 5, אזור 📍</span>
                  </div>
                  <div className="flex justify-between items-center border-b pb-2 border-stone-200">
                    <span className="text-gray-500 font-medium">טלפון:</span>
                    <span className="font-mono text-gray-800" dir="ltr">{confirmedAppointment.phone}</span>
                  </div>
                  <div className="flex justify-between items-center border-b pb-2 border-stone-200">
                    <span className="text-gray-500 font-medium">אימייל:</span>
                    <span className="font-mono text-gray-800 text-xs" dir="ltr">{confirmedAppointment.email}</span>
                  </div>
                  {confirmedAppointment.notes && (
                    <div className="flex flex-col gap-1 pt-1 text-right">
                      <span className="text-gray-500 text-xs font-medium">הערות לטיפול:</span>
                      <span className="text-gray-800 text-xs bg-white p-2 rounded border border-stone-200">{confirmedAppointment.notes}</span>
                    </div>
                  )}
                </div>

                {/* Google Calendar Action */}
                {lastBookedEvent && (
                  <div className="w-full p-4 bg-blue-50 border border-blue-200 rounded-xl text-center flex flex-col items-center gap-2">
                    <p className="text-xs text-blue-900 font-semibold">רוצה תזכורת? שמור את הפגישה ישירות ביומן שלך:</p>
                    <a
                      href={createGoogleCalendarUrl(lastBookedEvent)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2.5 px-6 rounded-lg text-sm shadow transition transform hover:scale-[1.02]"
                    >
                      <span>📅</span> הוסף ליומן Google
                    </a>
                  </div>
                )}

                <button 
                  onClick={closeBookingModal}
                  className="mt-2 text-sm text-gray-500 hover:text-gray-900 underline font-medium"
                >
                  סגור חלון
                </button>
              </div>
            ) : (
              <form onSubmit={handleBookingSubmit} className="flex flex-col gap-4">
                <div className="bg-amber-50 border border-amber-200 p-2.5 rounded-lg text-xs text-amber-900 font-medium flex items-center justify-between">
                  <span>{bookingService.includes("נשים") ? "💇‍♀️ קביעת תור למחלקת נשים" : "💈 קביעת תור למחלקת גברים"}</span>
                  <span className="text-gray-500">שירות מבוקש: {bookingService}</span>
                </div>
                <div className="flex gap-4">
                  <input 
                    required 
                    type="text" 
                    placeholder="שם פרטי" 
                    className="border p-2.5 rounded-lg flex-1" 
                    value={formData.first_name} 
                    onChange={e => setFormData({...formData, first_name: e.target.value})} 
                  />
                  <input 
                    required 
                    type="text" 
                    placeholder="שם משפחה" 
                    className="border p-2.5 rounded-lg flex-1" 
                    value={formData.last_name} 
                    onChange={e => setFormData({...formData, last_name: e.target.value})} 
                  />
                </div>
                <div className="flex gap-4">
                  <input 
                    required 
                    type="tel" 
                    placeholder="מספר טלפון" 
                    className="border p-2.5 rounded-lg flex-1" 
                    dir="ltr" 
                    value={formData.phone} 
                    onChange={e => setFormData({...formData, phone: e.target.value})} 
                  />
                  <input 
                    required 
                    type="email" 
                    placeholder="אימייל (חובה)" 
                    className="border p-2.5 rounded-lg flex-1" 
                    dir="ltr" 
                    value={formData.email} 
                    onChange={e => setFormData({...formData, email: e.target.value})} 
                  />
                </div>
                <div className="flex gap-4">
                  {bookingService.includes("נשים") ? (
                    <select 
                      required 
                      className="border p-2.5 rounded-lg flex-1" 
                      value={formData.service_type} 
                      onChange={e => setFormData({...formData, service_type: e.target.value})}
                    >
                      <option value="תספורת נשים">תספורת נשים</option>
                      <option value="עיצוב שיער ופן">עיצוב שיער ופן</option>
                      <option value="צבע / גוונים">צבע / גוונים</option>
                      <option value="החלקת קרטין">החלקת קרטין</option>
                      <option value="תסרוקות ערב וכלה">תסרוקות ערב וכלה</option>
                      <option value="שיקום / כימיה">שיקום / כימיה</option>
                    </select>
                  ) : (
                    <select 
                      required 
                      className="border p-2.5 rounded-lg flex-1" 
                      value={formData.service_type} 
                      onChange={e => setFormData({...formData, service_type: e.target.value})}
                    >
                      <option value="תספורת גברים">תספורת גברים</option>
                      <option value="עיצוב זקן">עיצוב זקן</option>
                      <option value="תספורת גברים וזקן">תספורת גברים וזקן</option>
                      <option value="טיפול פנים ודירוג">טיפול פנים ודירוג</option>
                    </select>
                  )}

                  {bookingService.includes("נשים") ? (
                    <select 
                      required 
                      className="border p-2.5 rounded-lg flex-1" 
                      value={formData.employee} 
                      onChange={e => setFormData({...formData, employee: e.target.value})}
                    >
                      <option value="יעל">יעל (נשים, צבע וגוונים)</option>
                      <option value="שירן">שירן (כלה, תסרוקות, קרטין)</option>
                      <option value="נועם">נועם (כימיה, שיקום וטיפוח)</option>
                    </select>
                  ) : (
                    <select 
                      required 
                      className="border p-2.5 rounded-lg flex-1" 
                      value={formData.employee} 
                      onChange={e => setFormData({...formData, employee: e.target.value})}
                    >
                      <option value="דני">דני (גברים, זקן)</option>
                      <option value="דוד">דוד (גברים, דירוגים)</option>
                    </select>
                  )}
                </div>
                <div className="flex gap-4">
                  <input 
                    required 
                    type="date" 
                    className="border p-2.5 rounded-lg flex-1" 
                    value={formData.appointment_date} 
                    onChange={e => setFormData({...formData, appointment_date: e.target.value})} 
                    min={new Date().toISOString().split('T')[0]} 
                  />
                  <select 
                    required 
                    className="border p-2.5 rounded-lg flex-1 font-mono" 
                    value={formData.appointment_time} 
                    onChange={e => setFormData({...formData, appointment_time: e.target.value})}
                  >
                    <option value="">בחר שעה</option>
                    <option value="08:00">08:00</option>
                    <option value="08:30">08:30</option>
                    <option value="09:00">09:00</option>
                    <option value="09:30">09:30</option>
                    <option value="10:00">10:00</option>
                    <option value="10:30">10:30</option>
                    <option value="11:00">11:00</option>
                    <option value="11:30">11:30</option>
                    <option value="12:00">12:00</option>
                    <option value="12:30">12:30</option>
                    <option value="13:00">13:00</option>
                    <option value="13:30">13:30</option>
                    <option value="14:00">14:00</option>
                    <option value="14:30">14:30</option>
                    <option value="15:00">15:00</option>
                    <option value="15:30">15:30</option>
                    <option value="16:00">16:00</option>
                    <option value="16:30">16:30</option>
                    <option value="17:00">17:00</option>
                    <option value="17:30">17:30</option>
                    <option value="18:00">18:00</option>
                    <option value="18:30">18:30</option>
                    <option value="19:00">19:00</option>
                    <option value="19:30">19:30</option>
                  </select>
                </div>
                <input 
                  type="text" 
                  placeholder="עיר מגורים (לא חובה)" 
                  className="border p-2.5 rounded-lg" 
                  value={formData.city} 
                  onChange={e => setFormData({...formData, city: e.target.value})} 
                />
                <textarea 
                  placeholder="הערות נוספות או בקשות מיוחדות (לא חובה)" 
                  className="border p-2.5 rounded-lg h-20 text-sm" 
                  value={formData.notes} 
                  onChange={e => setFormData({...formData, notes: e.target.value})}
                ></textarea>
                <button 
                  type="submit" 
                  className="bg-[#1a2332] text-white p-3 rounded-xl font-bold hover:bg-[#c9a962] hover:text-[#1a2332] transition shadow"
                >
                  אשר וקבע תור
                </button>
              </form>
            )}
          </div>
        </div>
      )}

      {/* Functional Chatbot Widget */}
      {isOpen ? (
        <div className="fixed bottom-4 left-4 bg-white p-0 rounded-xl shadow-2xl border border-gray-200 w-80 flex flex-col h-[450px] overflow-hidden z-40">
          <div className="bg-[#1a2332] text-white p-3 font-bold flex justify-between items-center shrink-0">
            <span>Chatbot (Gemini 2.0)</span>
            <button onClick={() => setIsOpen(false)} className="text-sm bg-[#c9a962] px-2 py-1 rounded hover:bg-[#b09355]">x</button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3 bg-gray-50">
            {messages.map((msg, i) => (
              <div key={i} className="flex flex-col gap-2">
                <div className={`p-3 rounded-lg max-w-[85%] ${msg.role === 'user' ? 'bg-[#c9a962] text-white self-end rounded-br-none' : 'bg-white border text-gray-800 self-start rounded-bl-none shadow-sm'}`}>
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  
                  {/* Google Calendar Action Card */}
                  {msg.calendar_event && (
                    <div className="mt-3 p-2.5 bg-blue-50 border border-blue-200 rounded-lg text-xs text-blue-950 flex flex-col gap-1.5">
                      <div className="font-bold flex items-center gap-1">
                        <span>📅</span> {msg.calendar_event.title}
                      </div>
                      <div className="text-gray-600">
                        📍 {msg.calendar_event.location || 'קפלן 5, אזור'}
                      </div>
                      <div className="text-gray-600">
                        ⏰ תאריך ושעה: {msg.calendar_event.date} בשעה {msg.calendar_event.time}
                      </div>
                      <a 
                        href={createGoogleCalendarUrl(msg.calendar_event)} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="mt-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-1.5 px-3 rounded text-center transition flex items-center justify-center gap-1 shadow-sm"
                      >
                        <span>➕</span> הוסף ליומן Google
                      </a>
                    </div>
                  )}
                </div>
                {msg.options && msg.options.length > 0 && msg.role === 'model' && i === messages.length - 1 && !isLoading && (
                  <div className="flex flex-wrap gap-2 mt-1 self-start">
                    {msg.options
                      .filter(opt => !(msg.calendar_event && (opt.includes('יומן') || opt.includes('Google') || opt.includes('גוגל'))))
                      .map((opt, idx) => (
                      <button 
                        key={idx} 
                        onClick={() => sendMessage(opt)}
                        className={`px-3 py-1.5 rounded-full text-xs font-medium transition ${
                          opt.includes('יומן') 
                            ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm font-bold' 
                            : 'bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100'
                        }`}
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="bg-white border text-gray-800 self-start p-3 rounded-lg rounded-bl-none">
                <p className="text-sm text-gray-500">מקליד...</p>
              </div>
            )}
          </div>
          
          <div className="p-3 bg-white border-t flex shrink-0">
            <input 
              type="text" 
              placeholder="הקלד הודעה..." 
              className="flex-1 border p-2 rounded-r focus:outline-none focus:border-[#c9a962]" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              disabled={isLoading}
            />
            <button onClick={sendMessage} disabled={isLoading} className="bg-[#1a2332] text-white px-4 rounded-l hover:bg-gray-800">
              שלח
            </button>
          </div>
        </div>
      ) : (
        <button 
          onClick={() => setIsOpen(true)} 
          className="fixed bottom-4 left-4 bg-[#c9a962] text-white p-4 rounded-full shadow-2xl hover:bg-[#b09355] transition transform hover:scale-105 z-40"
        >
          💬 צ'אט
        </button>
      )}
    </div>
  );
}
