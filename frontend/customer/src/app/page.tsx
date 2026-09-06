import React from 'react';

export default function CustomerHome() {
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
            <button className="mt-4 px-6 py-2 bg-[#c9a962] text-white rounded-full">קבע תור</button>
          </div>
          <div className="bg-white p-6 rounded-xl shadow">
            <h3 className="text-xl font-bold mb-2">תספורת גברים</h3>
            <p>תספורת וזקן</p>
            <button className="mt-4 px-6 py-2 bg-[#c9a962] text-white rounded-full">קבע תור</button>
          </div>
        </div>
      </main>

      {/* Chatbot Widget Placeholder */}
      <div className="fixed bottom-4 left-4 bg-white p-4 rounded-xl shadow-lg border border-gray-200 w-80">
        <div className="bg-[#1a2332] text-white p-3 -m-4 mb-4 rounded-t-xl font-bold flex justify-between">
          <span>Chatbot (Gemini 2.0)</span>
          <button className="text-sm bg-[#c9a962] px-2 rounded">x</button>
        </div>
        <p className="text-sm mb-4">שלום! אני העוזר החכם של FRIZURA. איך אפשר לעזור?</p>
        <input type="text" placeholder="הקלד הודעה..." className="w-full border p-2 rounded" />
      </div>
    </div>
  );
}
