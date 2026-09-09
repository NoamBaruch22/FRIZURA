'use client';
import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';

export default function ManagerDashboard() {
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  
  // Data States
  const [appointments, setAppointments] = useState<any[]>([]);
  const [leads, setLeads] = useState<any[]>([]);
  const [clients, setClients] = useState<any[]>([]);
  const [invoices, setInvoices] = useState<any[]>([]);
  const [settings, setSettings] = useState<any>(null);
  
  // Archive States
  const [archivedClients, setArchivedClients] = useState<any[]>([]);
  const [archivedAppointments, setArchivedAppointments] = useState<any[]>([]);
  const [archivedInvoices, setArchivedInvoices] = useState<any[]>([]);

  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Modal States
  const [showClientModal, setShowClientModal] = useState(false);
  const [showApptModal, setShowApptModal] = useState(false);
  const [showLeadModal, setShowLeadModal] = useState(false);
  const [showInvoiceModal, setShowInvoiceModal] = useState(false);
  const [selectedClientForDossier, setSelectedClientForDossier] = useState<any>(null);
  const [formData, setFormData] = useState<any>({});

  // Direct backend API endpoint
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

  // Helpers
  const formatDate = (dateStr: string) => {
    if (!dateStr) return '';
    const parts = dateStr.split('-');
    if (parts.length === 3) {
      return `${parts[2]}.${parts[1]}.${parts[0]}`; // DD.MM.YYYY (יום.חודש.שנה)
    }
    return dateStr;
  };

  const clientsMap = useMemo(() => {
    const map = new Map<number, any>();
    clients.forEach(c => map.set(c.id, c));
    return map;
  }, [clients]);

  useEffect(() => {
    const storedToken = localStorage.getItem("manager_token");
    if (storedToken) setToken(storedToken);
  }, []);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchData();
    }
  }, [token]);

  useEffect(() => {
    if (activeTab === 'archive') {
      fetchArchive();
    }
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [apptsRes, leadsRes, clientsRes, invoicesRes, settingsRes] = await Promise.all([
        axios.get(`${apiUrl}/api/appointments/`),
        axios.get(`${apiUrl}/api/leads/`),
        axios.get(`${apiUrl}/api/clients/`),
        axios.get(`${apiUrl}/api/invoices/`),
        axios.get(`${apiUrl}/api/settings/`)
      ]);
      setAppointments(apptsRes.data);
      setLeads(leadsRes.data);
      setClients(clientsRes.data);
      setInvoices(invoicesRes.data);
      setSettings(settingsRes.data);
    } catch (err: any) {
      if (err.response?.status === 401) handleLogout();
    } finally {
      setLoading(false);
    }
  };

  const fetchArchive = async () => {
    try {
      const [clientsRes, apptsRes, invRes] = await Promise.all([
        axios.get(`${apiUrl}/api/clients/archive`),
        axios.get(`${apiUrl}/api/appointments/archive`),
        axios.get(`${apiUrl}/api/invoices/archive`)
      ]);
      setArchivedClients(clientsRes.data);
      setArchivedAppointments(apptsRes.data);
      setArchivedInvoices(invRes.data);
    } catch (err) { console.error(err); }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const res = await axios.post(`${apiUrl}/api/auth/login`, new URLSearchParams({ username: email.trim(), password: password }));
      const accessToken = res.data.access_token;
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
      setToken(accessToken);
      localStorage.setItem("manager_token", accessToken);
    } catch (err: any) {
      console.error("Login failed:", err);
      let msg = "שגיאה בהתחברות לשרת.";
      if (err.response?.status === 401) {
        msg = "אימייל או סיסמה שגויים. (ברירת מחדל: admin@frizura.com / Password123!)";
      } else if (err.response?.status === 429) {
        msg = "הגבלת ניסיונות. אנא המתן דקה ונסה שוב.";
      } else if (err.code === "ERR_NETWORK" || !err.response) {
        msg = `שגיאת רשת (ERR_NETWORK): לא ניתן להגיע לשרת הבקאנד ב-${apiUrl}. ודא שפורט 8000 פועל.`;
      } else {
        msg = `שגיאה (${err.response?.status}): ${err.response?.data?.detail || err.message}`;
      }
      setError(msg);
      alert(msg);
    }
  };

  const handleLogout = () => {
    setToken("");
    localStorage.removeItem("manager_token");
  };

  // WhatsApp Integration
  const sendWhatsAppReminder = (appt: any) => {
    const client = clientsMap.get(appt.client_id);
    const phone = client?.phone || '';
    if (!phone) {
      alert('לא נמצא מספר טלפון עבור לקוח זה.');
      return;
    }
    const cleanPhone = phone.replace(/\D/g, '');
    const intlPhone = cleanPhone.startsWith('0') ? `972${cleanPhone.slice(1)}` : cleanPhone;
    const clientName = client ? `${client.first_name} ${client.last_name}` : 'לקוח יקר';
    const timeFormatted = appt.appointment_time?.substring(0, 5) || '';
    const dateFormatted = formatDate(appt.appointment_date);
    const message = `שלום ${clientName}, תזכורת לתורך במספרת FRIZURA בתאריך ${dateFormatted} בשעה ${timeFormatted} עבור ${appt.service}. נשמח לראותך! ✂️`;
    window.open(`https://wa.me/${intlPhone}?text=${encodeURIComponent(message)}`, '_blank');
  };

  const sendWhatsAppToLead = (lead: any) => {
    const phone = lead.phone || '';
    if (!phone) {
      alert('לא נמצא מספר טלפון עבור ליד זה.');
      return;
    }
    const cleanPhone = phone.replace(/\D/g, '');
    const intlPhone = cleanPhone.startsWith('0') ? `972${cleanPhone.slice(1)}` : cleanPhone;
    const message = `שלום ${lead.first_name}, תודה על פנייתך למספרת FRIZURA! ✂️ נשמח לתאם עבורך תור או לענות על כל שאלה.`;
    window.open(`https://wa.me/${intlPhone}?text=${encodeURIComponent(message)}`, '_blank');
  };

  // Client CRUD
  const createClient = async (e: React.FormEvent) => {
    e.preventDefault();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    if (!formData.email || !emailRegex.test(formData.email.trim())) {
      alert("אנא הזן כתובת אימייל תקינה (למשל name@example.com).");
      return;
    }
    try {
      await axios.post(`${apiUrl}/api/clients/`, {
        ...formData,
        email: formData.email.trim(),
        source: 'מנהל ידני'
      });
      setShowClientModal(false);
      setFormData({});
      fetchData();
      alert("הלקוח נוצר בהצלחה!");
    } catch (err: any) { 
      alert(err.response?.data?.detail || 'שגיאה ביצירת לקוח'); 
    }
  };

  const deleteClient = async (id: number) => {
    if (!confirm('למחוק לקוח זה? כל התורים העתידיים שלו יועברו לסל המחזור.')) return;
    try {
      await axios.delete(`${apiUrl}/api/clients/${id}`);
      fetchData();
    } catch (err) { alert('שגיאה במחיקה'); }
  };

  const restoreClient = async (id: number) => {
    try {
      await axios.post(`${apiUrl}/api/clients/${id}/restore`);
      fetchArchive();
      fetchData();
    } catch (err) { alert('שגיאה בשחזור'); }
  };

  // Appointment CRUD
  const createAppointment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.client_id) {
      alert("אנא בחר לקוח מהרשימה.");
      return;
    }
    try {
      const fullService = formData.employee 
        ? `${formData.service_type || 'תספורת'} (עם: ${formData.employee})`
        : (formData.service_type || 'תספורת');

      await axios.post(`${apiUrl}/api/appointments/`, {
        client_id: parseInt(formData.client_id),
        service: fullService,
        appointment_date: formData.appointment_date,
        appointment_time: formData.appointment_time,
        status: "ממתין לאישור"
      });
      setShowApptModal(false);
      setFormData({});
      fetchData();
      alert("התור נקבע בהצלחה ביומן!");
    } catch (err: any) {
      if (err.response?.status === 409) {
        alert("השעה תפוסה! קיים כבר תור ביומן בטווח של שעה מזמן זה. אנא בחר שעה אחרת.");
      } else {
        alert(err.response?.data?.detail || 'שגיאה ביצירת תור. ודא שכל השדות מלאים.');
      }
    }
  };

  const updateAppointmentStatus = async (id: number, newStatus: string) => {
    try {
      await axios.patch(`${apiUrl}/api/appointments/${id}`, { status: newStatus });
      fetchData();
    } catch (err) { alert('שגיאה בעדכון סטטוס התור'); }
  };

  const deleteAppointment = async (id: number) => {
    if (!confirm('למחוק תור זה?')) return;
    try {
      await axios.delete(`${apiUrl}/api/appointments/${id}`);
      fetchData();
    } catch (err) { alert('שגיאה במחיקה'); }
  };

  const restoreAppointment = async (id: number) => {
    try {
      await axios.post(`${apiUrl}/api/appointments/${id}/restore`);
      fetchArchive();
      fetchData();
    } catch (err) { alert('שגיאה בשחזור תור'); }
  };

  // Lead CRUD
  const createLead = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(`${apiUrl}/api/leads/`, {
        first_name: formData.first_name,
        last_name: formData.last_name,
        phone: formData.phone,
        source: formData.source || 'אתר הבית',
        notes: formData.notes || '',
        status: 'חדש'
      });
      setShowLeadModal(false);
      setFormData({});
      fetchData();
      alert("הליד נוצר בהצלחה!");
    } catch (err: any) {
      alert(err.response?.data?.detail || 'שגיאה ביצירת ליד');
    }
  };

  const updateLeadStatus = async (id: number, newStatus: string) => {
    try {
      await axios.patch(`${apiUrl}/api/leads/${id}`, { status: newStatus });
      fetchData();
    } catch (err) { alert('שגיאה בעדכון סטטוס ליד'); }
  };

  const convertLeadToClient = async (id: number) => {
    if (!confirm('להמיר ליד זה ללקוח רשמי במאגר הלקוחות?')) return;
    try {
      await axios.post(`${apiUrl}/api/leads/${id}/convert`);
      fetchData();
      alert('הליד הומר בהצלחה ללקוח רשמי! תוכל למצוא אותו בלשונית לקוחות.');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'שגיאה בהמרת ליד');
    }
  };

  const deleteLead = async (id: number) => {
    if (!confirm('האם למחוק ליד זה?')) return;
    try {
      await axios.delete(`${apiUrl}/api/leads/${id}`);
      fetchData();
    } catch (err) { alert('שגיאה במחיקת ליד'); }
  };

  // Invoice CRUD
  const createInvoice = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.client_id) {
      alert('אנא בחר לקוח.');
      return;
    }
    try {
      await axios.post(`${apiUrl}/api/invoices/`, {
        client_id: parseInt(formData.client_id),
        amount: parseFloat(formData.amount),
        service_description: formData.service_description
      });
      setShowInvoiceModal(false);
      setFormData({});
      fetchData();
      alert('הקבלה הופקה בהצלחה!');
    } catch (err: any) { alert(err.response?.data?.detail || 'שגיאה ביצירת קבלה'); }
  };

  const deleteInvoice = async (id: number) => {
    if (!confirm('למחוק קבלה זו?')) return;
    try {
      await axios.delete(`${apiUrl}/api/invoices/${id}`);
      fetchData();
    } catch (err) { alert('שגיאה במחיקה'); }
  };
  
  const restoreInvoice = async (id: number) => {
    try {
      await axios.post(`${apiUrl}/api/invoices/${id}/restore`);
      fetchArchive();
      fetchData();
    } catch (err) { alert('שגיאה בשחזור'); }
  };

  const saveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.put(`${apiUrl}/api/settings/`, settings);
      alert('הגדרות ושעות הפעילות נשמרו בהצלחה!');
      fetchData();
    } catch (err) { alert('שגיאה בשמירת הגדרות'); }
  };

  const timeOptions = [
    "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
    "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30"
  ];

  if (!token) {
    return (
      <div dir="rtl" className="min-h-screen bg-[#1a2332] flex items-center justify-center p-4">
        <form onSubmit={handleLogin} className="bg-white p-8 rounded-xl shadow-2xl w-full max-w-md">
          <h2 className="text-3xl font-serif text-center mb-6 text-[#1a2332] font-bold">התחברות מנהל FRIZURA</h2>
          {error && <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-center font-bold">{error}</div>}
          <div className="mb-4">
            <label className="block text-gray-700 mb-2 font-bold">כתובת אימייל</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} className="w-full border rounded p-2 text-left" dir="ltr" placeholder="admin@frizura.com" required />
          </div>
          <div className="mb-6">
            <label className="block text-gray-700 mb-2 font-bold">סיסמה</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="w-full border rounded p-2 text-left" dir="ltr" placeholder="••••••••" required />
          </div>
          <button type="submit" className="w-full bg-[#c9a962] text-white py-3 rounded-lg font-bold hover:bg-yellow-600 transition shadow">היכנס למערכת</button>

          <div className="mt-4 pt-4 border-t text-center">
            <button
              type="button"
              onClick={() => {
                setEmail("admin@frizura.com");
                setPassword("Password123!");
              }}
              className="text-xs text-blue-600 hover:underline font-medium"
            >
              🔑 מילוי אוטומטי של פרטי מנהל (admin@frizura.com)
            </button>
          </div>
        </form>
      </div>
    );
  }

  const renderContent = () => {
    // 1. DASHBOARD
    if (activeTab === 'dashboard') {
      return (
        <div>
          <h1 className="text-3xl font-bold mb-6 text-[#1a2332]">לוח בקרה</h1>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div 
              onClick={() => setActiveTab('clients')}
              className="bg-white p-6 rounded-xl shadow hover:shadow-lg transition cursor-pointer border-t-4 border-[#c9a962] group"
              title="לחץ לצפייה בלקוחות פעילים"
            >
              <div className="flex justify-between items-center">
                <h3 className="text-gray-500 text-sm font-bold group-hover:text-[#c9a962] transition">לקוחות פעילים</h3>
                <span className="text-xl">👥</span>
              </div>
              <p className="text-4xl font-bold mt-3 text-[#1a2332]">{clients.length}</p>
              <p className="text-xs text-gray-400 mt-2">לחץ לפתיחת לשונית לקוחות ←</p>
            </div>

            <div 
              onClick={() => setActiveTab('appointments')}
              className="bg-white p-6 rounded-xl shadow hover:shadow-lg transition cursor-pointer border-t-4 border-blue-500 group"
              title="לחץ לצפייה ביומן תורים"
            >
              <div className="flex justify-between items-center">
                <h3 className="text-gray-500 text-sm font-bold group-hover:text-blue-600 transition">תורים עתידיים</h3>
                <span className="text-xl">📅</span>
              </div>
              <p className="text-4xl font-bold mt-3 text-[#1a2332]">{appointments.length}</p>
              <p className="text-xs text-gray-400 mt-2">לחץ לפתיחת יומן תורים ←</p>
            </div>

            <div 
              onClick={() => setActiveTab('leads')}
              className="bg-white p-6 rounded-xl shadow hover:shadow-lg transition cursor-pointer border-t-4 border-green-500 group"
              title="לחץ לצפייה בלידים CRM"
            >
              <div className="flex justify-between items-center">
                <h3 className="text-gray-500 text-sm font-bold group-hover:text-green-600 transition">לידים חדשים</h3>
                <span className="text-xl">🎯</span>
              </div>
              <p className="text-4xl font-bold mt-3 text-[#1a2332]">{leads.filter(l => l.status === 'חדש').length}</p>
              <p className="text-xs text-gray-400 mt-2">לחץ לפתיחת ניהול לידים ←</p>
            </div>
          </div>

          {/* Upcoming appointments quick preview */}
          <div className="mt-8 bg-white rounded-xl shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-[#1a2332]">תורים קרובים להיום והשבוע</h2>
              <button onClick={() => setActiveTab('appointments')} className="text-blue-600 text-sm font-bold hover:underline">כל התורים ביומן ←</button>
            </div>
            {appointments.length === 0 ? <p className="text-gray-500">אין תורים קרובים במערכת.</p> : (
              <div className="overflow-x-auto">
                <table className="w-full text-right border-collapse">
                  <thead>
                    <tr className="border-b text-gray-400 text-sm">
                      <th className="pb-3">לקוח</th>
                      <th className="pb-3">טלפון</th>
                      <th className="pb-3">שירות</th>
                      <th className="pb-3">תאריך</th>
                      <th className="pb-3">שעה</th>
                      <th className="pb-3">סטטוס</th>
                      <th className="pb-3">תזכורת WhatsApp</th>
                    </tr>
                  </thead>
                  <tbody>
                    {appointments.slice(0, 5).map(appt => {
                      const client = clientsMap.get(appt.client_id);
                      return (
                        <tr key={appt.id} className="border-b hover:bg-gray-50">
                          <td className="py-3 font-bold text-[#1a2332]">{client ? `${client.first_name} ${client.last_name}` : `לקוח #${appt.client_id}`}</td>
                          <td className="py-3 text-gray-600" dir="ltr">{client?.phone || '-'}</td>
                          <td className="py-3">{appt.service}</td>
                          <td className="py-3 font-medium text-blue-600"><span dir="ltr">{formatDate(appt.appointment_date)}</span></td>
                          <td className="py-3 font-medium text-blue-600"><span dir="ltr">{appt.appointment_time?.substring(0, 5)}</span></td>
                          <td className="py-3">
                            <span className={`px-2 py-1 rounded-full text-xs font-bold ${
                              appt.status === 'בוצע' ? 'bg-green-100 text-green-800' :
                              appt.status === 'אושר' ? 'bg-blue-100 text-blue-800' :
                              appt.status === 'בוטל' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {appt.status}
                            </span>
                          </td>
                          <td className="py-3">
                            <button 
                              onClick={() => sendWhatsAppReminder(appt)} 
                              className="bg-green-50 text-green-700 hover:bg-green-600 hover:text-white px-3 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1 border border-green-200"
                            >
                              <span>💬</span> וואטסאפ
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      );
    }

    // 2. APPOINTMENTS TAB
    if (activeTab === 'appointments') {
      return (
        <div>
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-[#1a2332]">יומן תורים</h1>
              <p className="text-gray-500 text-sm mt-1">ניהול תורים, שינוי סטטוס ושליחת תזכורות WhatsApp ישירות ללקוחות</p>
            </div>
            <button onClick={() => { setFormData({ appointment_date: new Date().toISOString().split('T')[0], appointment_time: '10:00', service_type: 'תספורת גברים / עיצוב זקן', employee: 'דני' }); setShowApptModal(true); }} className="bg-blue-600 text-white px-5 py-2.5 rounded-lg hover:bg-blue-700 font-bold shadow transition flex items-center gap-2">
              <span>➕</span> תור חדש
            </button>
          </div>
          <div className="bg-white rounded-xl shadow p-6 overflow-x-auto">
            {appointments.length === 0 ? <p className="text-gray-500">אין תורים פעילים במערכת.</p> : (
              <table className="w-full text-right border-collapse">
                <thead>
                  <tr className="border-b text-gray-500 text-sm">
                    <th className="pb-3">שם הלקוח</th>
                    <th className="pb-3">טלפון</th>
                    <th className="pb-3">עיר מגורים</th>
                    <th className="pb-3">שירות ועובד</th>
                    <th className="pb-3">תאריך</th>
                    <th className="pb-3">שעה</th>
                    <th className="pb-3">סטטוס (ניתן לעריכה)</th>
                    <th className="pb-3">תזכורת WhatsApp</th>
                    <th className="pb-3">פעולות</th>
                  </tr>
                </thead>
                <tbody>
                  {appointments.map(appt => {
                    const client = clientsMap.get(appt.client_id);
                    const clientName = client ? `${client.first_name} ${client.last_name}` : `לקוח #${appt.client_id}`;
                    return (
                      <tr key={appt.id} className="border-b hover:bg-gray-50 transition">
                        <td className="py-3 font-bold text-[#1a2332]">
                          <button 
                            onClick={() => client && setSelectedClientForDossier(client)}
                            className="hover:text-blue-600 hover:underline text-right"
                            title="לחץ לפתיחת כרטיס לקוח"
                          >
                            {clientName}
                          </button>
                        </td>
                        <td className="py-3 text-gray-600 font-mono text-sm" dir="ltr">{client?.phone || '-'}</td>
                        <td className="py-3 text-gray-700 text-sm font-medium">{client?.city || '-'}</td>
                        <td className="py-3">{appt.service}</td>
                        <td className="py-3 font-medium text-blue-700"><span dir="ltr">{formatDate(appt.appointment_date)}</span></td>
                        <td className="py-3 font-medium text-blue-700"><span dir="ltr">{appt.appointment_time?.substring(0, 5)}</span></td>
                        <td className="py-3">
                          <select 
                            value={appt.status} 
                            onChange={e => updateAppointmentStatus(appt.id, e.target.value)}
                            className={`border rounded px-2 py-1 text-xs font-bold cursor-pointer ${
                              appt.status === 'בוצע' ? 'bg-green-50 text-green-800 border-green-200' :
                              appt.status === 'אושר' ? 'bg-blue-50 text-blue-800 border-blue-200' :
                              appt.status === 'בוטל' ? 'bg-red-50 text-red-800 border-red-200' : 'bg-yellow-50 text-yellow-800 border-yellow-200'
                            }`}
                          >
                            <option value="ממתין לאישור">ממתין לאישור</option>
                            <option value="אושר">אושר</option>
                            <option value="בוצע">בוצע</option>
                            <option value="בוטל">בוטל</option>
                          </select>
                        </td>
                        <td className="py-3">
                          <button 
                            onClick={() => sendWhatsAppReminder(appt)} 
                            className="bg-green-100 text-green-800 hover:bg-green-600 hover:text-white px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 shadow-sm"
                            title="שלח תזכורת בוואטסאפ ללקוח"
                          >
                            <span>💬</span> שלח תזכורת
                          </button>
                        </td>
                        <td className="py-3">
                          <button onClick={() => deleteAppointment(appt.id)} className="text-red-500 hover:text-red-700 text-sm font-bold transition">🗑️ מחיקה</button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>
      );
    }

    // 3. LEADS CRM TAB
    if (activeTab === 'leads') {
      return (
        <div>
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-[#1a2332]">לידים CRM</h1>
              <p className="text-gray-500 text-sm mt-1">מעקב פניות, עדכון סטטוסים והמרה ישירה של ליד ללקוח משלם</p>
            </div>
            <button onClick={() => { setFormData({ source: 'אתר הבית', status: 'חדש' }); setShowLeadModal(true); }} className="bg-green-600 text-white px-5 py-2.5 rounded-lg hover:bg-green-700 font-bold shadow transition flex items-center gap-2">
              <span>➕</span> ליד חדש
            </button>
          </div>
          <div className="bg-white rounded-xl shadow p-6 overflow-x-auto">
            {leads.length === 0 ? <p className="text-gray-500">אין לידים במערכת.</p> : (
              <table className="w-full text-right border-collapse">
                <thead>
                  <tr className="border-b text-gray-500 text-sm">
                    <th className="pb-3">שם</th>
                    <th className="pb-3">טלפון</th>
                    <th className="pb-3">מקור הגעה</th>
                    <th className="pb-3">סטטוס פנייה</th>
                    <th className="pb-3">הערות</th>
                    <th className="pb-3">פעולות CRM</th>
                  </tr>
                </thead>
                <tbody>
                  {leads.map(lead => (
                    <tr key={lead.id} className="border-b hover:bg-gray-50 transition">
                      <td className="py-3 font-bold text-[#1a2332]">{lead.first_name} {lead.last_name}</td>
                      <td className="py-3 text-gray-700" dir="ltr">{lead.phone}</td>
                      <td className="py-3"><span className="bg-gray-100 text-gray-800 px-2 py-0.5 rounded text-xs">{lead.source || 'כללי'}</span></td>
                      <td className="py-3">
                        <select
                          value={lead.status}
                          onChange={e => updateLeadStatus(lead.id, e.target.value)}
                          className={`border rounded px-2 py-1 text-xs font-bold cursor-pointer ${
                            lead.status === 'הפך ללקוח' ? 'bg-green-100 text-green-800 border-green-300' :
                            lead.status === 'בטיפול' ? 'bg-blue-100 text-blue-800 border-blue-300' :
                            lead.status === 'לא מעוניין' ? 'bg-gray-100 text-gray-800 border-gray-300' :
                            lead.status === 'אין מענה' ? 'bg-orange-100 text-orange-800 border-orange-300' : 'bg-yellow-100 text-yellow-800 border-yellow-300'
                          }`}
                        >
                          <option value="חדש">חדש</option>
                          <option value="בטיפול">בטיפול</option>
                          <option value="אין מענה">אין מענה</option>
                          <option value="לא מעוניין">לא מעוניין</option>
                          <option value="הפך ללקוח">הפך ללקוח</option>
                        </select>
                      </td>
                      <td className="py-3 text-gray-600 text-sm max-w-xs truncate">{lead.notes || '-'}</td>
                      <td className="py-3 flex items-center gap-2">
                        {lead.status !== 'הפך ללקוח' && (
                          <button 
                            onClick={() => convertLeadToClient(lead.id)} 
                            className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs font-bold transition flex items-center gap-1 shadow-sm"
                            title="המר ישירות ללקוח במאגר"
                          >
                            <span>👤</span> המר ללקוח
                          </button>
                        )}
                        <button 
                          onClick={() => sendWhatsAppToLead(lead)} 
                          className="bg-green-50 text-green-700 hover:bg-green-600 hover:text-white px-2.5 py-1 rounded text-xs font-bold border border-green-300 transition"
                          title="צור קשר בוואטסאפ"
                        >
                          💬 וואטסאפ
                        </button>
                        <button onClick={() => deleteLead(lead.id)} className="text-red-500 hover:text-red-700 text-xs font-bold transition">
                          🗑️
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      );
    }

    // 4. CLIENTS TAB
    if (activeTab === 'clients') {
      return (
        <div>
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-[#1a2332]">לקוחות רשומים</h1>
              <p className="text-gray-500 text-sm mt-1">ניהול פרטי לקוחות, עיר מגורים, מעקב מקור רישום ופתיחת כרטיס לקוח אישי</p>
            </div>
            <button onClick={() => { setFormData({}); setShowClientModal(true); }} className="bg-blue-600 text-white px-5 py-2.5 rounded-lg hover:bg-blue-700 font-bold shadow transition flex items-center gap-2">
              <span>➕</span> לקוח חדש
            </button>
          </div>
          <div className="bg-white rounded-xl shadow p-6 overflow-x-auto">
            {clients.length === 0 ? <p className="text-gray-500">אין לקוחות במערכת.</p> : (
              <table className="w-full text-right border-collapse">
                <thead>
                  <tr className="border-b text-gray-500 text-sm">
                    <th className="pb-3">שם הלקוח</th>
                    <th className="pb-3">טלפון</th>
                    <th className="pb-3">אימייל</th>
                    <th className="pb-3">עיר מגורים</th>
                    <th className="pb-3">מקור רישום</th>
                    <th className="pb-3">הערות</th>
                    <th className="pb-3">פעולות</th>
                  </tr>
                </thead>
                <tbody>
                  {clients.map(client => (
                    <tr key={client.id} className="border-b hover:bg-gray-50 transition">
                      <td className="py-3 font-bold text-[#1a2332]">{client.first_name} {client.last_name}</td>
                      <td className="py-3 text-gray-700 font-mono text-sm" dir="ltr">{client.phone}</td>
                      <td className="py-3 text-gray-600 font-mono text-xs" dir="ltr">{client.email || '-'}</td>
                      <td className="py-3 font-medium text-gray-800">{client.city || '-'}</td>
                      <td className="py-3">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                          client.source === 'טופס אתר' ? 'bg-purple-100 text-purple-800' :
                          client.source === 'צ׳אט בוט' ? 'bg-teal-100 text-teal-800' :
                          client.source?.includes('ליד') ? 'bg-orange-100 text-orange-800' : 'bg-gray-100 text-gray-700'
                        }`}>
                          {client.source || 'מנהל ידני'}
                        </span>
                      </td>
                      <td className="py-3 text-gray-500 text-sm max-w-xs truncate">{client.notes || '-'}</td>
                      <td className="py-3 flex items-center gap-2">
                        <button 
                          onClick={() => setSelectedClientForDossier(client)} 
                          className="bg-blue-50 text-blue-700 hover:bg-blue-600 hover:text-white px-3 py-1 rounded-lg text-xs font-bold transition border border-blue-200 flex items-center gap-1 shadow-sm"
                        >
                          <span>📋</span> כרטיס לקוח
                        </button>
                        <button onClick={() => deleteClient(client.id)} className="text-red-500 hover:text-red-700 text-xs font-bold transition">🗑️ מחיקה</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      );
    }

    // 5. INVOICES TAB
    if (activeTab === 'invoices') {
      return (
        <div>
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-[#1a2332]">קופות וחשבוניות</h1>
              <p className="text-gray-500 text-sm mt-1">הפקת קבלות מס, מעקב תשלומים לפי לקוח והיסטוריית עסקאות</p>
            </div>
            <button onClick={() => { setFormData({ amount: 120, service_description: 'תספורת ועיצוב שיער' }); setShowInvoiceModal(true); }} className="bg-[#c9a962] text-white px-5 py-2.5 rounded-lg hover:bg-yellow-600 font-bold shadow transition flex items-center gap-2">
              <span>➕</span> קבלה חדשה
            </button>
          </div>
          <div className="bg-white rounded-xl shadow p-6 overflow-x-auto">
            {invoices.length === 0 ? <p className="text-gray-500">אין חשבוניות במערכת.</p> : (
              <table className="w-full text-right border-collapse">
                <thead>
                  <tr className="border-b text-gray-500 text-sm">
                    <th className="pb-3">מס' קבלה</th>
                    <th className="pb-3">שם הלקוח</th>
                    <th className="pb-3">טלפון</th>
                    <th className="pb-3">עיר מגורים</th>
                    <th className="pb-3">סכום לתשלום</th>
                    <th className="pb-3">תיאור שירות / מוצר</th>
                    <th className="pb-3">תאריך הפקה</th>
                    <th className="pb-3">פעולות</th>
                  </tr>
                </thead>
                <tbody>
                  {invoices.map(inv => {
                    const client = clientsMap.get(inv.client_id);
                    return (
                      <tr key={inv.id} className="border-b hover:bg-gray-50 transition">
                        <td className="py-3 font-mono font-bold text-gray-600">#{inv.id}</td>
                        <td className="py-3 font-bold text-[#1a2332]">
                          <button 
                            onClick={() => client && setSelectedClientForDossier(client)}
                            className="hover:text-blue-600 hover:underline text-right"
                            title="פתח כרטיס לקוח"
                          >
                            {client ? `${client.first_name} ${client.last_name}` : `לקוח #${inv.client_id}`}
                          </button>
                        </td>
                        <td className="py-3 text-gray-600 font-mono text-sm" dir="ltr">{client?.phone || '-'}</td>
                        <td className="py-3 text-gray-700 text-sm font-medium">{client?.city || '-'}</td>
                        <td className="py-3 font-bold text-green-700 text-lg">₪{inv.amount}</td>
                        <td className="py-3">{inv.service_description}</td>
                        <td className="py-3 text-gray-600 font-medium"><span dir="ltr">{formatDate(inv.invoice_date)}</span></td>
                        <td className="py-3">
                          <button onClick={() => deleteInvoice(inv.id)} className="text-red-500 hover:text-red-700 text-sm font-bold transition">🗑️ מחיקה</button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>
      );
    }

    // 6. SETTINGS TAB
    if (activeTab === 'settings') {
      if (!settings) return <div>טוען הגדרות...</div>;
      const days = [
        { key: 'sunday', label: 'יום ראשון' },
        { key: 'monday', label: 'יום שני' },
        { key: 'tuesday', label: 'יום שלישי' },
        { key: 'wednesday', label: 'יום רביעי' },
        { key: 'thursday', label: 'יום חמישי' },
        { key: 'friday', label: 'יום שישי' },
      ];

      return (
        <div>
          <h1 className="text-3xl font-bold mb-6 text-[#1a2332]">הגדרות עסק ושעות פעילות</h1>
          <form onSubmit={saveSettings} className="bg-white rounded-xl shadow p-8 max-w-3xl flex flex-col gap-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="font-bold text-gray-700 block mb-1">שם העסק</label>
                <input type="text" className="border p-2.5 rounded-lg w-full" value={settings.business_name || ''} onChange={e => setSettings({...settings, business_name: e.target.value})} />
              </div>
              <div>
                <label className="font-bold text-gray-700 block mb-1">טלפון ליצירת קשר</label>
                <input type="text" className="border p-2.5 rounded-lg w-full" value={settings.phone || ''} onChange={e => setSettings({...settings, phone: e.target.value})} dir="ltr" />
              </div>
            </div>
            <div>
              <label className="font-bold text-gray-700 block mb-1">כתובת המספרה</label>
              <input type="text" className="border p-2.5 rounded-lg w-full" value={settings.address || ''} onChange={e => setSettings({...settings, address: e.target.value})} />
            </div>

            <div className="border-t pt-6">
              <h3 className="text-lg font-bold text-[#1a2332] mb-4">לוח שעות וימי עבודה</h3>
              <div className="flex flex-col gap-3">
                {days.map(d => {
                  const daySchedule = settings.working_hours?.[d.key] || { active: true, start: '09:00', end: '19:00' };
                  return (
                    <div key={d.key} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border">
                      <div className="flex items-center gap-3 w-36">
                        <input 
                          type="checkbox" 
                          id={`chk-${d.key}`}
                          checked={daySchedule.active !== false}
                          onChange={e => {
                            const updated = { ...settings.working_hours, [d.key]: { ...daySchedule, active: e.target.checked } };
                            setSettings({ ...settings, working_hours: updated });
                          }}
                          className="w-4 h-4 text-blue-600 rounded cursor-pointer"
                        />
                        <label htmlFor={`chk-${d.key}`} className="font-bold text-gray-700 cursor-pointer">{d.label}</label>
                      </div>

                      {daySchedule.active !== false ? (
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-500">משעה:</span>
                          <select 
                            value={daySchedule.start || '09:00'}
                            onChange={e => {
                              const updated = { ...settings.working_hours, [d.key]: { ...daySchedule, start: e.target.value } };
                              setSettings({ ...settings, working_hours: updated });
                            }}
                            className="border p-1.5 rounded text-sm bg-white font-mono"
                          >
                            {timeOptions.map(t => <option key={t} value={t}>{t}</option>)}
                          </select>
                          <span className="text-xs text-gray-500">עד:</span>
                          <select 
                            value={daySchedule.end || '19:00'}
                            onChange={e => {
                              const updated = { ...settings.working_hours, [d.key]: { ...daySchedule, end: e.target.value } };
                              setSettings({ ...settings, working_hours: updated });
                            }}
                            className="border p-1.5 rounded text-sm bg-white font-mono"
                          >
                            {timeOptions.map(t => <option key={t} value={t}>{t}</option>)}
                          </select>
                        </div>
                      ) : (
                        <span className="text-sm font-bold text-red-500">סגור</span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            <button type="submit" className="bg-[#c9a962] text-white py-3 px-6 rounded-lg font-bold hover:bg-yellow-600 self-start transition shadow">
              שמור שינויים בהגדרות
            </button>
          </form>
        </div>
      );
    }

    // 7. ARCHIVE TAB
    if (activeTab === 'archive') {
      return (
        <div>
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-[#1a2332]">סל מחזור (ארכיון)</h1>
              <p className="text-gray-500 text-sm mt-1">שחזור מהיר של לקוחות, תורים וקבלות שנמחקו בלחיצת כפתור</p>
            </div>
            <button onClick={fetchArchive} className="text-blue-600 text-sm font-bold hover:underline">רענן סל מחזור ↻</button>
          </div>
          
          <div className="flex flex-col gap-8">
            {/* Deleted Appointments */}
            <div className="bg-white rounded-xl shadow p-6">
              <h3 className="text-lg font-bold text-blue-700 mb-3 flex items-center gap-2">
                <span>📅</span> תורים שנמחקו ({archivedAppointments.length})
              </h3>
              {archivedAppointments.length === 0 ? <p className="text-gray-400 text-sm">אין תורים בסל המחזור.</p> : (
                <div className="overflow-x-auto">
                  <table className="w-full text-right border-collapse">
                    <thead>
                      <tr className="border-b text-gray-400 text-xs">
                        <th className="pb-2">לקוח</th>
                        <th className="pb-2">טלפון</th>
                        <th className="pb-2">שירות</th>
                        <th className="pb-2">תאריך</th>
                        <th className="pb-2">שעה</th>
                        <th className="pb-2">פעולה</th>
                      </tr>
                    </thead>
                    <tbody>
                      {archivedAppointments.map(a => {
                        const client = clientsMap.get(a.client_id);
                        return (
                          <tr key={a.id} className="border-b text-sm">
                            <td className="py-2 font-bold">{client ? `${client.first_name} ${client.last_name}` : `לקוח #${a.client_id}`}</td>
                            <td className="py-2 text-gray-600" dir="ltr">{client?.phone || '-'}</td>
                            <td className="py-2">{a.service}</td>
                            <td className="py-2 text-blue-600"><span dir="ltr">{formatDate(a.appointment_date)}</span></td>
                            <td className="py-2 text-blue-600"><span dir="ltr">{a.appointment_time?.substring(0, 5)}</span></td>
                            <td className="py-2"><button onClick={() => restoreAppointment(a.id)} className="bg-green-100 text-green-800 px-3 py-1 rounded text-xs font-bold hover:bg-green-200 transition">♻️ שחזר</button></td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Deleted Clients */}
            <div className="bg-white rounded-xl shadow p-6">
              <h3 className="text-lg font-bold text-blue-700 mb-3 flex items-center gap-2">
                <span>👥</span> לקוחות שנמחקו ({archivedClients.length})
              </h3>
              {archivedClients.length === 0 ? <p className="text-gray-400 text-sm">אין לקוחות בסל המחזור.</p> : (
                <div className="overflow-x-auto">
                  <table className="w-full text-right border-collapse">
                    <thead>
                      <tr className="border-b text-gray-400 text-xs">
                        <th className="pb-2">שם</th>
                        <th className="pb-2">טלפון</th>
                        <th className="pb-2">אימייל</th>
                        <th className="pb-2">עיר</th>
                        <th className="pb-2">מקור</th>
                        <th className="pb-2">פעולה</th>
                      </tr>
                    </thead>
                    <tbody>
                      {archivedClients.map(c => (
                        <tr key={c.id} className="border-b text-sm">
                          <td className="py-2 font-bold">{c.first_name} {c.last_name}</td>
                          <td className="py-2" dir="ltr">{c.phone}</td>
                          <td className="py-2 font-mono text-xs" dir="ltr">{c.email || '-'}</td>
                          <td className="py-2">{c.city || '-'}</td>
                          <td className="py-2 text-xs text-gray-500">{c.source || '-'}</td>
                          <td className="py-2"><button onClick={() => restoreClient(c.id)} className="bg-green-100 text-green-800 px-3 py-1 rounded text-xs font-bold hover:bg-green-200 transition">♻️ שחזר</button></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Deleted Invoices */}
            <div className="bg-white rounded-xl shadow p-6">
              <h3 className="text-lg font-bold text-blue-700 mb-3 flex items-center gap-2">
                <span>💰</span> קבלות שנמחקו ({archivedInvoices.length})
              </h3>
              {archivedInvoices.length === 0 ? <p className="text-gray-400 text-sm">אין קבלות בסל המחזור.</p> : (
                <div className="overflow-x-auto">
                  <table className="w-full text-right border-collapse">
                    <thead>
                      <tr className="border-b text-gray-400 text-xs">
                        <th className="pb-2">מס' קבלה</th>
                        <th className="pb-2">לקוח</th>
                        <th className="pb-2">סכום</th>
                        <th className="pb-2">תיאור</th>
                        <th className="pb-2">תאריך</th>
                        <th className="pb-2">פעולה</th>
                      </tr>
                    </thead>
                    <tbody>
                      {archivedInvoices.map(inv => {
                        const client = clientsMap.get(inv.client_id);
                        return (
                          <tr key={inv.id} className="border-b text-sm">
                            <td className="py-2 font-mono">#{inv.id}</td>
                            <td className="py-2 font-bold">{client ? `${client.first_name} ${client.last_name}` : `לקוח #${inv.client_id}`}</td>
                            <td className="py-2 font-bold text-green-700">₪{inv.amount}</td>
                            <td className="py-2">{inv.service_description}</td>
                            <td className="py-2 text-gray-600"><span dir="ltr">{formatDate(inv.invoice_date)}</span></td>
                            <td className="py-2"><button onClick={() => restoreInvoice(inv.id)} className="bg-green-100 text-green-800 px-3 py-1 rounded text-xs font-bold hover:bg-green-200 transition">♻️ שחזר</button></td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      );
    }
  };

  return (
    <div dir="rtl" className="flex h-screen bg-gray-100 font-sans text-right">
      {/* SIDEBAR */}
      <div className="w-64 bg-[#1a2332] text-white flex flex-col justify-between shadow-xl shrink-0">
        <div>
          <div className="p-6 text-center border-b border-gray-700">
            <h1 className="text-2xl font-serif text-[#c9a962] tracking-wider font-bold">FRIZURA Admin</h1>
            <p className="text-xs text-gray-400 mt-1">מערכת ניהול מספרת בוטיק</p>
          </div>
          <nav className="p-4 flex flex-col gap-1.5 font-medium">
            <button onClick={() => setActiveTab('dashboard')} className={`w-full text-right px-4 py-2.5 rounded-lg transition ${activeTab === 'dashboard' ? 'bg-[#c9a962] text-white font-bold shadow' : 'hover:bg-gray-800 text-gray-300'}`}>לוח בקרה</button>
            <button onClick={() => setActiveTab('appointments')} className={`w-full text-right px-4 py-2.5 rounded-lg transition ${activeTab === 'appointments' ? 'bg-[#c9a962] text-white font-bold shadow' : 'hover:bg-gray-800 text-gray-300'}`}>יומן תורים</button>
            <button onClick={() => setActiveTab('clients')} className={`w-full text-right px-4 py-2.5 rounded-lg transition ${activeTab === 'clients' ? 'bg-[#c9a962] text-white font-bold shadow' : 'hover:bg-gray-800 text-gray-300'}`}>לקוחות</button>
            <button onClick={() => setActiveTab('leads')} className={`w-full text-right px-4 py-2.5 rounded-lg transition ${activeTab === 'leads' ? 'bg-[#c9a962] text-white font-bold shadow' : 'hover:bg-gray-800 text-gray-300'}`}>לידים CRM</button>
            <button onClick={() => setActiveTab('invoices')} className={`w-full text-right px-4 py-2.5 rounded-lg transition ${activeTab === 'invoices' ? 'bg-[#c9a962] text-white font-bold shadow' : 'hover:bg-gray-800 text-gray-300'}`}>קופות וחשבוניות</button>
            <button onClick={() => setActiveTab('settings')} className={`w-full text-right px-4 py-2.5 rounded-lg transition ${activeTab === 'settings' ? 'bg-[#c9a962] text-white font-bold shadow' : 'hover:bg-gray-800 text-gray-300'}`}>הגדרות עסק</button>
            <button onClick={() => setActiveTab('archive')} className={`w-full text-right px-4 py-2.5 rounded-lg transition ${activeTab === 'archive' ? 'bg-red-900 text-white font-bold shadow' : 'hover:bg-gray-800 text-red-300'}`}>סל מחזור</button>
          </nav>
        </div>
        <div className="p-4 border-t border-gray-700">
          <button onClick={handleLogout} className="w-full text-right px-4 py-2 text-red-400 hover:bg-gray-800 rounded-lg transition font-bold">
            🚪 התנתק
          </button>
        </div>
      </div>

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white shadow-sm px-8 py-4 flex justify-between items-center shrink-0">
          <span className="text-gray-600 font-medium">שלום, <strong className="text-[#1a2332]">מנהל מערכת</strong></span>
          <button onClick={fetchData} className="text-[#c9a962] hover:text-yellow-600 font-bold flex items-center gap-1 transition">
            <span>↻</span> רענן נתונים
          </button>
        </header>
        <main className="flex-1 p-8 overflow-y-auto">
          {loading ? (
            <div className="flex justify-center items-center h-full">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#c9a962]"></div>
            </div>
          ) : renderContent()}
        </main>
      </div>

      {/* MODAL 1: ADD APPOINTMENT */}
      {showApptModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white p-6 rounded-2xl shadow-2xl w-full max-w-lg">
            <h2 className="text-2xl font-bold mb-4 text-[#1a2332]">יצירת תור חדש ביומן</h2>
            <form onSubmit={createAppointment} className="flex flex-col gap-3.5">
              <div>
                <label className="block text-xs font-bold text-gray-600 mb-1">בחר לקוח מהמאגר *</label>
                <select 
                  required 
                  className="border p-2.5 rounded-lg w-full"
                  value={formData.client_id || ""}
                  onChange={e => setFormData({...formData, client_id: e.target.value})}
                >
                  <option value="">בחר לקוח...</option>
                  {clients.map(c => (
                    <option key={c.id} value={c.id}>
                      {c.first_name} {c.last_name} ({c.phone})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-gray-600 mb-1">סוג שירות *</label>
                  <select 
                    required 
                    className="border p-2.5 rounded-lg w-full"
                    value={formData.service_type || "תספורת גברים / עיצוב זקן"}
                    onChange={e => setFormData({...formData, service_type: e.target.value})}
                  >
                    <option value="תספורת גברים / עיצוב זקן">תספורת גברים / עיצוב זקן</option>
                    <option value="תספורת נשים">תספורת נשים</option>
                    <option value="צבע / גוונים">צבע / גוונים</option>
                    <option value="החלקת קרטין / כלה">החלקת קרטין / כלה</option>
                    <option value="שיקום / כימיה">שיקום / כימיה</option>
                    <option value="עיסוי קרקפת">עיסוי קרקפת</option>
                    <option value="שירות מותאם אישית">שירות מותאם אישית</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-600 mb-1">איש / אשת צוות *</label>
                  <select 
                    required 
                    className="border p-2.5 rounded-lg w-full"
                    value={formData.employee || "דני"}
                    onChange={e => setFormData({...formData, employee: e.target.value})}
                  >
                    <option value="דני">דני (גברים, זקן)</option>
                    <option value="יעל">יעל (נשים, צבע)</option>
                    <option value="שירן">שירן (כלה, קרטין)</option>
                    <option value="דוד">דוד (גברים, דירוגים)</option>
                    <option value="נועם">נועם (כימיה, שיקום)</option>
                    <option value="צוות כללי">צוות כללי</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-gray-600 mb-1">תאריך התור *</label>
                  <input 
                    type="date" 
                    required 
                    className="border p-2.5 rounded-lg w-full"
                    value={formData.appointment_date || ""}
                    min={new Date().toISOString().split('T')[0]}
                    onChange={e => setFormData({...formData, appointment_date: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-600 mb-1">שעה *</label>
                  <select 
                    required 
                    className="border p-2.5 rounded-lg w-full font-mono"
                    value={formData.appointment_time || "10:00"}
                    onChange={e => setFormData({...formData, appointment_time: e.target.value})}
                  >
                    {timeOptions.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-2 mt-4">
                <button type="button" onClick={() => setShowApptModal(false)} className="px-4 py-2 text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition font-medium">ביטול</button>
                <button type="submit" className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold shadow transition">קבע תור</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: ADD CLIENT */}
      {showClientModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white p-6 rounded-2xl shadow-2xl w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4 text-[#1a2332]">הוספת לקוח חדש</h2>
            <form onSubmit={createClient} className="flex flex-col gap-3">
              <div className="grid grid-cols-2 gap-3">
                <input type="text" placeholder="שם פרטי *" required className="border p-2.5 rounded-lg" onChange={e => setFormData({...formData, first_name: e.target.value})} />
                <input type="text" placeholder="שם משפחה *" required className="border p-2.5 rounded-lg" onChange={e => setFormData({...formData, last_name: e.target.value})} />
              </div>
              <input type="tel" placeholder="מספר טלפון *" required className="border p-2.5 rounded-lg" dir="ltr" onChange={e => setFormData({...formData, phone: e.target.value})} />
              <input type="email" placeholder="אימייל (חובה) *" required className="border p-2.5 rounded-lg" dir="ltr" onChange={e => setFormData({...formData, email: e.target.value})} />
              <input type="text" placeholder="עיר מגורים" className="border p-2.5 rounded-lg" onChange={e => setFormData({...formData, city: e.target.value})} />
              <textarea placeholder="הערות על הלקוח" className="border p-2.5 rounded-lg h-20" onChange={e => setFormData({...formData, notes: e.target.value})}></textarea>
              <div className="flex justify-end gap-2 mt-4">
                <button type="button" onClick={() => setShowClientModal(false)} className="px-4 py-2 text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition font-medium">ביטול</button>
                <button type="submit" className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold shadow transition">שמור לקוח</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 3: ADD LEAD */}
      {showLeadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white p-6 rounded-2xl shadow-2xl w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4 text-[#1a2332]">יצירת ליד CRM חדש</h2>
            <form onSubmit={createLead} className="flex flex-col gap-3">
              <div className="grid grid-cols-2 gap-3">
                <input type="text" placeholder="שם פרטי *" required className="border p-2.5 rounded-lg" onChange={e => setFormData({...formData, first_name: e.target.value})} />
                <input type="text" placeholder="שם משפחה *" required className="border p-2.5 rounded-lg" onChange={e => setFormData({...formData, last_name: e.target.value})} />
              </div>
              <input type="tel" placeholder="מספר טלפון *" required className="border p-2.5 rounded-lg" dir="ltr" onChange={e => setFormData({...formData, phone: e.target.value})} />
              <div>
                <label className="block text-xs font-bold text-gray-600 mb-1">מקור הפנייה</label>
                <select className="border p-2.5 rounded-lg w-full" onChange={e => setFormData({...formData, source: e.target.value})}>
                  <option value="אתר הבית">אתר הבית</option>
                  <option value="אינסטגרם">אינסטגרם</option>
                  <option value="פייסבוק">פייסבוק</option>
                  <option value="גוגל">גוגל</option>
                  <option value="חבר מביא חבר">חבר מביא חבר</option>
                  <option value="אחר">אחר</option>
                </select>
              </div>
              <textarea placeholder="הערות ומה הליד ביקש" className="border p-2.5 rounded-lg h-24" onChange={e => setFormData({...formData, notes: e.target.value})}></textarea>
              <div className="flex justify-end gap-2 mt-4">
                <button type="button" onClick={() => setShowLeadModal(false)} className="px-4 py-2 text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition font-medium">ביטול</button>
                <button type="submit" className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-bold shadow transition">שמור ליד</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 4: ADD INVOICE */}
      {showInvoiceModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white p-6 rounded-2xl shadow-2xl w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4 text-[#1a2332]">הפקת קבלה / חשבונית</h2>
            <form onSubmit={createInvoice} className="flex flex-col gap-3">
              <div>
                <label className="block text-xs font-bold text-gray-600 mb-1">בחר לקוח *</label>
                <select 
                  required 
                  className="border p-2.5 rounded-lg w-full"
                  value={formData.client_id || ""}
                  onChange={e => setFormData({...formData, client_id: e.target.value})}
                >
                  <option value="">בחר לקוח...</option>
                  {clients.map(c => (
                    <option key={c.id} value={c.id}>
                      {c.first_name} {c.last_name} ({c.phone})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-600 mb-1">מלא אוטומטית לפי מחירון שירותים:</label>
                <select 
                  className="border p-2 rounded-lg w-full text-sm bg-gray-50"
                  onChange={e => {
                    const val = e.target.value;
                    if (!val) return;
                    const [desc, price] = val.split('|');
                    setFormData({...formData, service_description: desc, amount: price});
                  }}
                >
                  <option value="">-- בחר למילוי אוטומטי מהמחירון --</option>
                  <option value="תספורת גברים וזקן|80">תספורת גברים וזקן - ₪80</option>
                  <option value="תספורת נשים ופן|180">תספורת נשים ופן - ₪180</option>
                  <option value="צבע וגוונים|350">צבע וגוונים - ₪350</option>
                  <option value="החלקת קרטין אורגנית|700">החלקת קרטין אורגנית - ₪700</option>
                  <option value="טיפול שיקום לשיער|220">טיפול שיקום לשיער - ₪220</option>
                  <option value="עיצוב זקן בלבד|50">עיצוב זקן בלבד - ₪50</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-600 mb-1">תיאור השירות / המוצר *</label>
                <input 
                  type="text" 
                  placeholder="למשל: תספורת גבר + מוצר עיצוב" 
                  required 
                  className="border p-2.5 rounded-lg w-full"
                  value={formData.service_description || ""}
                  onChange={e => setFormData({...formData, service_description: e.target.value})} 
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-600 mb-1">סכום לתשלום (₪) *</label>
                <input 
                  type="number" 
                  step="0.01" 
                  placeholder="0.00" 
                  required 
                  className="border p-2.5 rounded-lg w-full font-bold text-green-700 font-mono"
                  value={formData.amount || ""}
                  onChange={e => setFormData({...formData, amount: e.target.value})} 
                />
              </div>

              <div className="flex justify-end gap-2 mt-4">
                <button type="button" onClick={() => setShowInvoiceModal(false)} className="px-4 py-2 text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition font-medium">ביטול</button>
                <button type="submit" className="px-6 py-2 bg-[#c9a962] hover:bg-yellow-600 text-white rounded-lg font-bold shadow transition">הפק קבלה</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 5: CLIENT DOSSIER (כרטיס לקוח) */}
      {selectedClientForDossier && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden">
            {/* Header */}
            <div className="bg-[#1a2332] text-white p-6 flex justify-between items-center shrink-0">
              <div>
                <h2 className="text-2xl font-bold font-serif text-[#c9a962]">
                  כרטיס לקוח: {selectedClientForDossier.first_name} {selectedClientForDossier.last_name}
                </h2>
                <p className="text-gray-300 text-sm mt-1">מזהה לקוח: #{selectedClientForDossier.id}</p>
              </div>
              <button onClick={() => setSelectedClientForDossier(null)} className="text-gray-400 hover:text-white text-2xl font-bold">×</button>
            </div>

            {/* Body */}
            <div className="p-6 overflow-y-auto flex flex-col gap-6">
              {/* Contact Details Card */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-gray-50 p-4 rounded-xl border">
                <div>
                  <span className="text-xs text-gray-500 block">טלפון</span>
                  <strong className="text-[#1a2332]" dir="ltr">{selectedClientForDossier.phone}</strong>
                </div>
                <div>
                  <span className="text-xs text-gray-500 block">אימייל</span>
                  <strong className="text-[#1a2332] text-xs truncate block" dir="ltr">{selectedClientForDossier.email || '-'}</strong>
                </div>
                <div>
                  <span className="text-xs text-gray-500 block">עיר מגורים</span>
                  <strong className="text-[#1a2332]">{selectedClientForDossier.city || '-'}</strong>
                </div>
                <div>
                  <span className="text-xs text-gray-500 block">מקור רישום</span>
                  <span className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded-full font-bold">{selectedClientForDossier.source || 'מנהל'}</span>
                </div>
              </div>

              {/* Financial KPI for this client */}
              {(() => {
                const clientInvoices = invoices.filter(inv => inv.client_id === selectedClientForDossier.id);
                const totalSpent = clientInvoices.reduce((acc, curr) => acc + (curr.amount || 0), 0);
                const clientAppts = appointments.filter(a => a.client_id === selectedClientForDossier.id);
                return (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-green-50 border border-green-200 p-4 rounded-xl text-center">
                      <span className="text-xs text-green-700 font-bold block">סך כל הרכישות והתשלומים</span>
                      <strong className="text-3xl text-green-800 font-bold font-mono">₪{totalSpent}</strong>
                    </div>
                    <div className="bg-blue-50 border border-blue-200 p-4 rounded-xl text-center">
                      <span className="text-xs text-blue-700 font-bold block">סה״כ תורים שנקבעו</span>
                      <strong className="text-3xl text-blue-800 font-bold">{clientAppts.length}</strong>
                    </div>
                  </div>
                );
              })()}

              {/* Client Appointments History */}
              <div>
                <h4 className="font-bold text-[#1a2332] mb-2 flex items-center gap-2">
                  <span>📅</span> היסטוריית תורים
                </h4>
                {appointments.filter(a => a.client_id === selectedClientForDossier.id).length === 0 ? (
                  <p className="text-gray-400 text-sm bg-gray-50 p-3 rounded">אין תורים רשומים עבור לקוח זה.</p>
                ) : (
                  <div className="border rounded-xl overflow-hidden">
                    <table className="w-full text-right text-sm">
                      <thead className="bg-gray-50 border-b text-gray-500 text-xs">
                        <tr>
                          <th className="p-2.5">שירות</th>
                          <th className="p-2.5">תאריך</th>
                          <th className="p-2.5">שעה</th>
                          <th className="p-2.5">סטטוס</th>
                        </tr>
                      </thead>
                      <tbody>
                        {appointments.filter(a => a.client_id === selectedClientForDossier.id).map(a => (
                          <tr key={a.id} className="border-b">
                            <td className="p-2.5 font-medium">{a.service}</td>
                            <td className="p-2.5 text-blue-600"><span dir="ltr">{formatDate(a.appointment_date)}</span></td>
                            <td className="p-2.5 text-blue-600"><span dir="ltr">{a.appointment_time?.substring(0, 5)}</span></td>
                            <td className="p-2.5"><span className="bg-gray-100 text-gray-800 px-2 py-0.5 rounded text-xs">{a.status}</span></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              {/* Client Invoices History */}
              <div>
                <h4 className="font-bold text-[#1a2332] mb-2 flex items-center gap-2">
                  <span>💰</span> היסטוריית חשבוניות ורכישות
                </h4>
                {invoices.filter(inv => inv.client_id === selectedClientForDossier.id).length === 0 ? (
                  <p className="text-gray-400 text-sm bg-gray-50 p-3 rounded">אין חשבוניות רשומות עבור לקוח זה.</p>
                ) : (
                  <div className="border rounded-xl overflow-hidden">
                    <table className="w-full text-right text-sm">
                      <thead className="bg-gray-50 border-b text-gray-500 text-xs">
                        <tr>
                          <th className="p-2.5">מספר קבלה</th>
                          <th className="p-2.5">תיאור</th>
                          <th className="p-2.5">סכום</th>
                          <th className="p-2.5">תאריך</th>
                        </tr>
                      </thead>
                      <tbody>
                        {invoices.filter(inv => inv.client_id === selectedClientForDossier.id).map(inv => (
                          <tr key={inv.id} className="border-b">
                            <td className="p-2.5 font-mono">#{inv.id}</td>
                            <td className="p-2.5">{inv.service_description}</td>
                            <td className="p-2.5 font-bold text-green-700">₪{inv.amount}</td>
                            <td className="p-2.5 text-gray-500"><span dir="ltr">{formatDate(inv.invoice_date)}</span></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>

            {/* Footer actions */}
            <div className="bg-gray-50 p-4 border-t flex justify-end gap-3 shrink-0">
              <button 
                onClick={() => {
                  const client = selectedClientForDossier;
                  setSelectedClientForDossier(null);
                  setFormData({ client_id: client.id, appointment_date: new Date().toISOString().split('T')[0], appointment_time: '10:00' });
                  setShowApptModal(true);
                }}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-bold transition"
              >
                ➕ קבע תור ללקוח זה
              </button>
              <button 
                onClick={() => {
                  const client = selectedClientForDossier;
                  setSelectedClientForDossier(null);
                  setFormData({ client_id: client.id, amount: 100, service_description: 'טיפול במספרה' });
                  setShowInvoiceModal(true);
                }}
                className="bg-[#c9a962] hover:bg-yellow-600 text-white px-4 py-2 rounded-lg text-sm font-bold transition"
              >
                ➕ הפק קבלה ללקוח זה
              </button>
              <button onClick={() => setSelectedClientForDossier(null)} className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm font-bold hover:bg-gray-300 transition">
                סגור
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
