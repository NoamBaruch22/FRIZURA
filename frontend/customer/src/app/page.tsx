"use client";
import React, { useState } from 'react';
import axios from 'axios';

export default function CustomerHome() {
  const [messages, setMessages] = useState<{role: string, content: string}[]>([
    { role: 'model', content: 'שלום! אני העוזר החכם של FRIZURA. איך אפשר לעזור?' }
  ]);
  const [input, setInput] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  // Booking Form State
  const [showBooking, setShowBooking] = useState(false);
  const [bookingService, setBookingService] = useState('');
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    notes: ''
  });
  const [bookingSuccess, setBookingSuccess] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const newMessages = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);
    
    try {
      const response = await axios.post('/api/chatbot/chat', {
        phone: "guest",
        messages: newMessages
      });
      setMessages([...newMessages, { role: 'model', content: response.data.reply }]);
    } catch (error) {
      console.error(error);
      setMessages([...newMessages, { role: 'model', content: 'מצטערים, חלה שגיאה בתקשורת עם השרת.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBookingSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post('/api/leads', {
        first_name: formData.first_name,
        last_name: formData.last_name,
        phone: formData.phone,
        source: "אתר",
        notes: `בקשה לתור: ${bookingService} | הערות: ${formData.notes}`
      });
      setBookingSuccess(true);
      setTimeout(() => {
        setShowBooking(false);
        setBookingSuccess(false);
        setFormData({ first_name: '', last_name: '', phone: '', notes: '' });
      }, 3000);
    } catch (err) {
      console.error(err);
      alert("שגיאה בשליחת הבקשה. אנא נסה שנית.");
    }
  };

  const openBooking = (service: string) => {
    setBookingService(service);
    setShowBooking(true);
  };

  return (
    <div dir="rtl" className="min-h-screen bg-[#f5f0e8] text-[#1a2332] font-sans relative">
      {/* Hero Section */}
      <header className="py-20 px-4 text-center bg-[#1a2332] text-white">
        <h1 className="text-5xl font-serif mb-4 text-[#c9a962]">FRIZURA</h1>
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
          <div className="bg-white rounded-xl p-8 max-w-md w-full relative shadow-2xl">
            <button onClick={() => setShowBooking(false)} className="absolute top-4 left-4 text-gray-500 hover:text-black font-bold">X</button>
            <h2 className="text-2xl font-bold mb-2">קביעת תור</h2>
            <p className="text-gray-600 mb-6">שירות מבוקש: <strong>{bookingService}</strong></p>
            
            {bookingSuccess ? (
              <div className="text-center py-8">
                <div className="text-green-500 text-5xl mb-4">✓</div>
                <h3 className="text-xl font-bold">הבקשה נשלחה בהצלחה!</h3>
                <p>נציג שלנו יחזור אליך בהקדם לתיאום התור.</p>
              </div>
            ) : (
              <form onSubmit={handleBookingSubmit} className="flex flex-col gap-4">
                <div className="flex gap-4">
                  <input required type="text" placeholder="שם פרטי" className="border p-2 rounded flex-1" value={formData.first_name} onChange={e => setFormData({...formData, first_name: e.target.value})} />
                  <input required type="text" placeholder="שם משפחה" className="border p-2 rounded flex-1" value={formData.last_name} onChange={e => setFormData({...formData, last_name: e.target.value})} />
                </div>
                <input required type="tel" placeholder="מספר טלפון" className="border p-2 rounded" dir="ltr" value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} />
                <textarea placeholder="הערות נוספות (לא חובה)" className="border p-2 rounded h-24" value={formData.notes} onChange={e => setFormData({...formData, notes: e.target.value})}></textarea>
                <button type="submit" className="bg-[#1a2332] text-white p-3 rounded-xl font-bold hover:bg-gray-800 mt-2">שלח בקשה לתור</button>
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
              <div key={i} className={`p-3 rounded-lg max-w-[85%] ${msg.role === 'user' ? 'bg-[#c9a962] text-white self-end rounded-br-none' : 'bg-white border text-gray-800 self-start rounded-bl-none'}`}>
                <p className="text-sm">{msg.content}</p>
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
