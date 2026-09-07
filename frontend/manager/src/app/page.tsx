"use client";
import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function ManagerDashboard() {
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  
  const [appointments, setAppointments] = useState<any[]>([]);
  const [leads, setLeads] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const storedToken = localStorage.getItem("manager_token");
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchData();
    }
  }, [token]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [apptsRes, leadsRes] = await Promise.all([
        axios.get('/api/appointments/'),
        axios.get('/api/leads/')
      ]);
      setAppointments(apptsRes.data);
      setLeads(leadsRes.data);
    } catch (err: any) {
      console.error(err);
      if (err.response?.status === 401) {
        handleLogout();
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      
      const res = await axios.post('/api/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      const newToken = res.data.access_token;
      setToken(newToken);
      localStorage.setItem("manager_token", newToken);
    } catch (err: any) {
      setError("שגיאה בהתחברות. אנא בדוק אימייל וסיסמה.");
    }
  };

  const handleLogout = () => {
    setToken("");
    localStorage.removeItem("manager_token");
    delete axios.defaults.headers.common['Authorization'];
  };

  if (!token) {
    return (
      <div dir="rtl" className="min-h-screen flex items-center justify-center bg-gray-50">
        <form onSubmit={handleLogin} className="bg-white p-8 rounded shadow max-w-sm w-full text-center">
          <h1 className="text-2xl font-serif mb-6 text-[#1a2332]">כניסת מנהלים</h1>
          {error && <p className="text-red-500 mb-4">{error}</p>}
          <input 
            className="w-full mb-4 p-2 border rounded" 
            type="email" 
            placeholder="אימייל" 
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input 
            className="w-full mb-6 p-2 border rounded" 
            type="password" 
            placeholder="סיסמה" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit" className="w-full bg-[#1a2332] text-white p-2 rounded hover:bg-gray-800">התחבר</button>
        </form>
      </div>
    );
  }

  return (
    <div dir="rtl" className="min-h-screen bg-gray-100 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-[#1a2332] text-white p-6 flex flex-col h-screen sticky top-0">
        <h2 className="text-2xl font-serif text-[#c9a962] mb-8">FRIZURA Admin</h2>
        <nav className="flex flex-col gap-4 flex-1">
          <a href="#" className="hover:text-[#c9a962]">יומן תורים</a>
          <a href="#" className="hover:text-[#c9a962]">לקוחות</a>
          <a href="#" className="hover:text-[#c9a962]">לידים CRM</a>
          <a href="#" className="hover:text-[#c9a962]">קופות וחשבוניות</a>
          <a href="#" className="hover:text-[#c9a962]">הגדרות עסק</a>
        </nav>
        <button onClick={handleLogout} className="mt-auto text-red-400 hover:text-red-300 text-right">
          התנתק
        </button>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">לוח בקרה</h1>
          <button onClick={fetchData} className="bg-gray-200 px-4 py-2 rounded hover:bg-gray-300">
            {loading ? "טוען..." : "רענן נתונים"}
          </button>
        </div>

        <div className="grid grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded shadow border-t-4 border-[#1a2332]">
            <h3 className="text-gray-500">תורים פעילים</h3>
            <p className="text-4xl font-bold text-[#1a2332]">{appointments.length}</p>
          </div>
          <div className="bg-white p-6 rounded shadow border-t-4 border-[#c9a962]">
            <h3 className="text-gray-500">לידים חדשים</h3>
            <p className="text-4xl font-bold text-[#c9a962]">{leads.filter(l => l.status === 'חדש').length}</p>
          </div>
          <div className="bg-white p-6 rounded shadow border-t-4 border-green-600">
            <h3 className="text-gray-500">סך הכל לידים</h3>
            <p className="text-4xl font-bold text-green-600">{leads.length}</p>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-6">
          <div className="bg-white rounded shadow p-6">
            <h2 className="text-xl font-bold mb-4">תורים קרובים</h2>
            {appointments.length === 0 ? (
              <p className="text-gray-500">אין תורים קרובים.</p>
            ) : (
              <table className="w-full text-right border-collapse">
                <thead>
                  <tr className="border-b">
                    <th className="pb-2">תאריך ושעה</th>
                    <th className="pb-2">שירות</th>
                    <th className="pb-2">סטטוס</th>
                  </tr>
                </thead>
                <tbody>
                  {appointments.slice(0, 5).map(appt => (
                    <tr key={appt.id} className="border-b hover:bg-gray-50">
                      <td className="py-3" dir="ltr">{appt.appointment_date} {appt.appointment_time}</td>
                      <td className="py-3">{appt.service}</td>
                      <td className="py-3">
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                          {appt.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div className="bg-white rounded shadow p-6">
            <h2 className="text-xl font-bold mb-4">לידים אחרונים</h2>
            {leads.length === 0 ? (
              <p className="text-gray-500">אין לידים במערכת.</p>
            ) : (
              <table className="w-full text-right border-collapse">
                <thead>
                  <tr className="border-b">
                    <th className="pb-2">שם</th>
                    <th className="pb-2">טלפון</th>
                    <th className="pb-2">מקור</th>
                    <th className="pb-2">סטטוס</th>
                  </tr>
                </thead>
                <tbody>
                  {leads.slice(0, 5).map(lead => (
                    <tr key={lead.id} className="border-b hover:bg-gray-50">
                      <td className="py-3">{lead.first_name} {lead.last_name}</td>
                      <td className="py-3" dir="ltr">{lead.phone}</td>
                      <td className="py-3">{lead.source}</td>
                      <td className="py-3">
                        <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-sm">
                          {lead.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
