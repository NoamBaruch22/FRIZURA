"use client";
import React, { useState } from 'react';

export default function ManagerDashboard() {
  const [token, setToken] = useState("");

  if (!token) {
    return (
      <div dir="rtl" className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="bg-white p-8 rounded shadow max-w-sm w-full text-center">
          <h1 className="text-2xl font-serif mb-6 text-[#1a2332]">כניסת מנהלים</h1>
          <input className="w-full mb-4 p-2 border rounded" type="email" placeholder="אימייל" />
          <input className="w-full mb-6 p-2 border rounded" type="password" placeholder="סיסמה" />
          <button onClick={() => setToken("fake-jwt")} className="w-full bg-[#1a2332] text-white p-2 rounded">התחבר</button>
        </div>
      </div>
    );
  }

  return (
    <div dir="rtl" className="min-h-screen bg-gray-100 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-[#1a2332] text-white p-6">
        <h2 className="text-2xl font-serif text-[#c9a962] mb-8">FRIZURA Admin</h2>
        <nav className="flex flex-col gap-4">
          <a href="#" className="hover:text-[#c9a962]">יומן תורים</a>
          <a href="#" className="hover:text-[#c9a962]">לקוחות</a>
          <a href="#" className="hover:text-[#c9a962]">לידים CRM</a>
          <a href="#" className="hover:text-[#c9a962]">קופות וחשבוניות</a>
          <a href="#" className="hover:text-[#c9a962]">הגדרות עסק</a>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-6">לוח בקרה</h1>
        <div className="grid grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded shadow">
            <h3 className="text-gray-500">תורים היום</h3>
            <p className="text-3xl font-bold">12</p>
          </div>
          <div className="bg-white p-6 rounded shadow">
            <h3 className="text-gray-500">לידים חדשים</h3>
            <p className="text-3xl font-bold">3</p>
          </div>
          <div className="bg-white p-6 rounded shadow">
            <h3 className="text-gray-500">הכנסות החודש</h3>
            <p className="text-3xl font-bold">₪4,500</p>
          </div>
        </div>
        
        <div className="bg-white rounded shadow p-6">
          <h2 className="text-xl font-bold mb-4">תורים קרובים</h2>
          <table className="w-full text-right">
            <thead>
              <tr className="border-b">
                <th className="pb-2">שעה</th>
                <th className="pb-2">לקוח</th>
                <th className="pb-2">שירות</th>
                <th className="pb-2">סטטוס</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b">
                <td className="py-4">10:00</td>
                <td>ישראל ישראלי</td>
                <td>תספורת גברים</td>
                <td><span className="bg-green-100 text-green-800 px-2 py-1 rounded">אושר</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
