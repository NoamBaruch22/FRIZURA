"use client";
import React, { useState } from 'react';
import axios from 'axios';

export default function CustomerHome() {
  const [messages, setMessages] = useState<{role: string, content: string}[]>([
    { role: 'model', content: 'שלום! אני העוזר החכם של FRIZURA. איך אפשר לעזור?' }
  ]);
  const [input, setInput] = useState('');
  const [isOpen, setIsOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const newMessages = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);
    
    try {
      const response = await axios.post('/api/chatbot/chat', {
        phone: "guest", // Placeholder for actual auth
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

  return (
    <div dir="rtl" className="min-h-screen bg-[#f5f0e8] text-[#1a2332] font-sans">
      {/* Hero Section */}
      <header className="py-20 px-4 text-center bg-[#1a2332] text-white">
        <h1 className="text-5xl font-serif mb-4 text-[#c9a962]">FRIZURA</h1>
        <p className="text-xl">Boutique Hair Salon</p>
      </header>
      
      {/* Services */}
      <main className="max-w-4xl mx-auto py-12 px-4">
        <h2 className="text-3xl font-serif mb-8 text-center">השירותים שלנו</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-xl shadow">
            <h3 className="text-xl font-bold mb-2">תספורת נשים</h3>
            <p>עיצוב שיער מקצועי</p>
            <button className="mt-4 px-6 py-2 bg-[#c9a962] text-white rounded-full hover:bg-[#b09355]">קבע תור</button>
          </div>
          <div className="bg-white p-6 rounded-xl shadow">
            <h3 className="text-xl font-bold mb-2">תספורת גברים</h3>
            <p>תספורת וזקן</p>
            <button className="mt-4 px-6 py-2 bg-[#c9a962] text-white rounded-full hover:bg-[#b09355]">קבע תור</button>
          </div>
        </div>
      </main>

      {/* Functional Chatbot Widget */}
      {isOpen ? (
        <div className="fixed bottom-4 left-4 bg-white p-0 rounded-xl shadow-2xl border border-gray-200 w-80 flex flex-col h-96 overflow-hidden">
          <div className="bg-[#1a2332] text-white p-3 font-bold flex justify-between items-center shrink-0">
            <span>Chatbot (Gemini 2.0)</span>
            <button onClick={() => setIsOpen(false)} className="text-sm bg-[#c9a962] px-2 py-1 rounded hover:bg-[#b09355]">x</button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3 bg-gray-50">
            {messages.map((msg, i) => (
              <div key={i} className={`p-3 rounded-lg max-w-[85%] ${msg.role === 'user' ? 'bg-[#c9a962] text-white self-end' : 'bg-white border text-gray-800 self-start'}`}>
                <p className="text-sm">{msg.content}</p>
              </div>
            ))}
            {isLoading && (
              <div className="bg-white border text-gray-800 self-start p-3 rounded-lg">
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
          className="fixed bottom-4 left-4 bg-[#c9a962] text-white p-4 rounded-full shadow-lg hover:bg-[#b09355]"
        >
          💬 צ'אט
        </button>
      )}
    </div>
  );
}
