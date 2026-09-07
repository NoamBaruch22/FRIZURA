'use client';
import { useState, useEffect } from 'react';
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
  const [showInvoiceModal, setShowInvoiceModal] = useState(false);
  const [formData, setFormData] = useState<any>({});

  const apiUrl = process.env.NODE_ENV === 'development' ? 'http://127.0.0.1:8000' : '';

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
    try {
      const res = await axios.post(`${apiUrl}/api/auth/login`, new URLSearchParams({ username: email, password: password }));
      const accessToken = res.data.access_token;
      setToken(accessToken);
      localStorage.setItem("manager_token", accessToken);
    } catch (err) {
      setError("שגיאה בהתחברות. אנא בדוק פרטים.");
    }
  };

  const handleLogout = () => {
    setToken("");
    localStorage.removeItem("manager_token");
  };

  // CRUD Functions
  const createClient = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(`${apiUrl}/api/clients/`, formData);
      setShowClientModal(false);
      setFormData({});
      fetchData();
    } catch (err) { alert('שגיאה ביצירת לקוח'); }
  };

  const deleteClient = async (id: number) => {
    if (!confirm('למחוק לקוח זה?')) return;
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

  const createInvoice = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(`${apiUrl}/api/invoices/`, formData);
      setShowInvoiceModal(false);
      setFormData({});
      fetchData();
    } catch (err) { alert('שגיאה ביצירת קבלה'); }
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

  const createAppointment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(`${apiUrl}/api/appointments/`, formData);
      setShowApptModal(false);
      setFormData({});
      fetchData();
    } catch (err) { alert('שגיאה ביצירת תור (אולי התנגשות זמנים?)'); }
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
    } catch (err) { alert('שגיאה בשחזור'); }
  };

  const saveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.put(`${apiUrl}/api/settings/`, settings);
      alert('הגדרות נשמרו בהצלחה!');
      fetchData();
    } catch (err) { alert('שגיאה בשמירת הגדרות'); }
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <form onSubmit={handleLogin} className="bg-white p-8 rounded shadow-md w-96 text-right">
          <h1 className="text-2xl font-bold mb-6">כניסת מנהל FRIZURA</h1>
          {error && <div className="bg-red-100 text-red-700 p-2 rounded mb-4 text-sm">{error}</div>}
          <div className="mb-4">
            <label className="block text-gray-700 mb-2">אימייל</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} className="w-full border rounded p-2 text-left" dir="ltr" required />
          </div>
          <div className="mb-6">
            <label className="block text-gray-700 mb-2">סיסמא</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="w-full border rounded p-2 text-left" dir="ltr" required />
          </div>
          <button type="submit" className="w-full bg-[#1a2332] text-white py-2 rounded hover:bg-gray-800 transition">היכנס</button>
        </form>
      </div>
    );
  }

  const renderContent = () => {
    if (activeTab === 'dashboard') {
      return (
        <div>
          <h1 className="text-3xl font-bold mb-6">לוח בקרה</h1>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded shadow border-t-4 border-[#c9a962]">
              <h3 className="text-gray-500 text-sm font-bold">לקוחות פעילים</h3>
              <p className="text-3xl font-bold mt-2">{clients.length}</p>
            </div>
            <div className="bg-white p-6 rounded shadow border-t-4 border-blue-500">
              <h3 className="text-gray-500 text-sm font-bold">תורים עתידיים</h3>
              <p className="text-3xl font-bold mt-2">{appointments.length}</p>
            </div>
            <div className="bg-white p-6 rounded shadow border-t-4 border-green-500">
              <h3 className="text-gray-500 text-sm font-bold">לידים חדשים</h3>
              <p className="text-3xl font-bold mt-2">{leads.filter(l => l.status === 'חדש').length}</p>
            </div>
          </div>
        </div>
      );
    }

    if (activeTab === 'appointments') {
      return (
        <div>
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold">יומן תורים</h1>
            <button onClick={() => setShowApptModal(true)} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">➕ תור חדש</button>
          </div>
          <div className="bg-white rounded shadow p-6 overflow-x-auto">
            {appointments.length === 0 ? <p className="text-gray-500">אין תורים במערכת.</p> : (
              <table className="w-full text-right border-collapse">
                <thead>
                  <tr className="border-b"><th className="pb-2">מזהה לקוח</th><th className="pb-2">שירות</th><th className="pb-2">תאריך</th><th className="pb-2">שעה</th><th className="pb-2">סטטוס</th><th className="pb-2">פעולות</th></tr>
                </thead>
                <tbody>
                  {appointments.map(appt => (
                    <tr key={appt.id} className="border-b hover:bg-gray-50">
                      <td className="py-3">{appt.client_id}</td>
                      <td className="py-3">{appt.service}</td>
                      <td className="py-3 text-blue-600" dir="ltr">{appt.appointment_date}</td>
                      <td className="py-3 text-blue-600" dir="ltr">{appt.appointment_time}</td>
                      <td className="py-3"><span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs">{appt.status}</span></td>
                      <td className="py-3"><button onClick={() => deleteAppointment(appt.id)} className="text-red-500 hover:text-red-700">🗑️ מחיקה</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      );
    }

    if (activeTab === 'leads') {
      return (
        <div>
          <h1 className="text-3xl font-bold mb-6">לידים CRM</h1>
          <div className="bg-white rounded shadow p-6 overflow-x-auto">
            {leads.length === 0 ? <p className="text-gray-500">אין לידים במערכת.</p> : (
              <table className="w-full text-right border-collapse">
                <thead>
                  <tr className="border-b"><th className="pb-2">שם</th><th className="pb-2">טלפון</th><th className="pb-2">מקור</th><th className="pb-2">סטטוס</th><th className="pb-2">הערות</th></tr>
                </thead>
                <tbody>
                  {leads.map(lead => (
                    <tr key={lead.id} className="border-b hover:bg-gray-50">
                      <td className="py-3">{lead.first_name} {lead.last_name}</td>
                      <td className="py-3" dir="ltr">{lead.phone}</td>
                      <td className="py-3">{lead.source || '-'}</td>
                      <td className="py-3"><span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">{lead.status}</span></td>
                      <td className="py-3">{lead.notes || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      );
    }

    if (activeTab === 'clients') {
      return (
        <div>
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold">לקוחות רשומים</h1>
            <button onClick={() => setShowClientModal(true)} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">➕ לקוח חדש</button>
          </div>
          <div className="bg-white rounded shadow p-6">
            {clients.length === 0 ? <p className="text-gray-500">אין לקוחות במערכת.</p> : (
              <table className="w-full text-right border-collapse">
                <thead>
                  <tr className="border-b"><th className="pb-2">שם</th><th className="pb-2">טלפון</th><th className="pb-2">אימייל</th><th className="pb-2">הערות</th><th className="pb-2">פעולות</th></tr>
                </thead>
                <tbody>
                  {clients.map(client => (
                    <tr key={client.id} className="border-b hover:bg-gray-50">
                      <td className="py-3">{client.first_name} {client.last_name}</td>
                      <td className="py-3" dir="ltr">{client.phone}</td>
                      <td className="py-3">{client.email || '-'}</td>
                      <td className="py-3">{client.notes || '-'}</td>
                      <td className="py-3"><button onClick={() => deleteClient(client.id)} className="text-red-500 hover:text-red-700">🗑️ מחיקה</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      );
    }

    if (activeTab === 'invoices') {
      return (
        <div>
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold">קופות וחשבוניות</h1>
            <button onClick={() => setShowInvoiceModal(true)} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">➕ קבלה חדשה</button>
          </div>
          <div className="bg-white rounded shadow p-6">
            {invoices.length === 0 ? <p className="text-gray-500">אין חשבוניות במערכת.</p> : (
              <table className="w-full text-right border-collapse">
                <thead>
                  <tr className="border-b"><th className="pb-2">מזהה לקוח</th><th className="pb-2">סכום</th><th className="pb-2">תיאור שירות</th><th className="pb-2">תאריך</th><th className="pb-2">פעולות</th></tr>
                </thead>
                <tbody>
                  {invoices.map(inv => (
                    <tr key={inv.id} className="border-b hover:bg-gray-50">
                      <td className="py-3">{inv.client_id}</td>
                      <td className="py-3 text-green-600 font-bold">{inv.amount} ₪</td>
                      <td className="py-3">{inv.service_description}</td>
                      <td className="py-3" dir="ltr">{inv.invoice_date}</td>
                      <td className="py-3"><button onClick={() => deleteInvoice(inv.id)} className="text-red-500 hover:text-red-700">🗑️ ביטול</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      );
    }

    if (activeTab === 'settings') {
      return (
        <div>
          <h1 className="text-3xl font-bold mb-6">הגדרות עסק</h1>
          {settings ? (
            <form onSubmit={saveSettings} className="bg-white rounded shadow p-6 flex flex-col gap-4 max-w-lg">
              <div>
                <label className="font-bold text-gray-700 block mb-1">שם העסק</label>
                <input type="text" className="border p-2 rounded w-full bg-gray-50 focus:bg-white" value={settings.business_name || ''} onChange={e => setSettings({...settings, business_name: e.target.value})} required />
              </div>
              <div>
                <label className="font-bold text-gray-700 block mb-1">כתובת</label>
                <input type="text" className="border p-2 rounded w-full bg-gray-50 focus:bg-white" value={settings.address || ''} onChange={e => setSettings({...settings, address: e.target.value})} />
              </div>
              <div>
                <label className="font-bold text-gray-700 block mb-1">טלפון</label>
                <input type="text" className="border p-2 rounded w-full bg-gray-50 focus:bg-white" value={settings.phone || ''} onChange={e => setSettings({...settings, phone: e.target.value})} dir="ltr" />
              </div>
              
              <div className="mt-4 border-t pt-4">
                <label className="font-bold text-gray-700 block mb-3">שעות פעילות (ימי עבודה)</label>
                {['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי'].map(day => (
                  <div key={day} className="flex items-center gap-3 mb-2">
                    <span className="w-16">{day}</span>
                    <label className="flex items-center gap-1 text-sm">
                      <input type="checkbox" 
                        checked={settings.working_hours?.[day]?.active ?? true} 
                        onChange={e => setSettings({...settings, working_hours: {...(settings.working_hours||{}), [day]: {...(settings.working_hours?.[day]||{}), active: e.target.checked}}})} 
                      /> פעיל
                    </label>
                    <select 
                      className="border rounded p-1 text-sm" 
                      value={settings.working_hours?.[day]?.start || '09:00'}
                      onChange={e => setSettings({...settings, working_hours: {...(settings.working_hours||{}), [day]: {...(settings.working_hours?.[day]||{}), start: e.target.value}}})}
                      disabled={!(settings.working_hours?.[day]?.active ?? true)}
                    >
                      
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
                    <span>עד</span>
                    <select 
                      className="border rounded p-1 text-sm" 
                      value={settings.working_hours?.[day]?.end || '18:00'}
                      onChange={e => setSettings({...settings, working_hours: {...(settings.working_hours||{}), [day]: {...(settings.working_hours?.[day]||{}), end: e.target.value}}})}
                      disabled={!(settings.working_hours?.[day]?.active ?? true)}
                    >
                      
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
                ))}
              </div>

              <button type="submit" className="bg-[#c9a962] text-white py-2 px-4 rounded hover:bg-yellow-600 self-start mt-4">שמור שינויים</button>
            </form>
          ) : <p>טוען הגדרות...</p>}
        </div>
      );
    }

    if (activeTab === 'archive') {
      return (
        <div>
          <h1 className="text-3xl font-bold mb-6 text-red-600">סל מחזור (ארכיון)</h1>
          <div className="flex flex-col gap-8">
            {/* Archived Clients */}
            <div className="bg-white rounded shadow p-6">
              <h2 className="text-xl font-bold mb-4">לקוחות שנמחקו</h2>
              {archivedClients.length === 0 ? <p className="text-gray-500">אין לקוחות בארכיון.</p> : (
                <table className="w-full text-right border-collapse">
                  <thead><tr className="border-b"><th className="pb-2">שם</th><th className="pb-2">טלפון</th><th className="pb-2">פעולות</th></tr></thead>
                  <tbody>
                    {archivedClients.map(client => (
                      <tr key={client.id} className="border-b"><td className="py-2">{client.first_name} {client.last_name}</td><td className="py-2">{client.phone}</td>
                      <td className="py-2"><button onClick={() => restoreClient(client.id)} className="text-green-600 hover:text-green-800 font-bold">♻️ שחזר</button></td></tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
            {/* Archived Appointments */}
            <div className="bg-white rounded shadow p-6">
              <h2 className="text-xl font-bold mb-4">תורים שבוטלו/נמחקו</h2>
              {archivedAppointments.length === 0 ? <p className="text-gray-500">אין תורים בארכיון.</p> : (
                <table className="w-full text-right border-collapse">
                  <thead><tr className="border-b"><th className="pb-2">מזהה לקוח</th><th className="pb-2">שירות</th><th className="pb-2">תאריך</th><th className="pb-2">פעולות</th></tr></thead>
                  <tbody>
                    {archivedAppointments.map(appt => (
                      <tr key={appt.id} className="border-b"><td className="py-2">{appt.client_id}</td><td className="py-2">{appt.service}</td><td className="py-2">{appt.appointment_date}</td>
                      <td className="py-2"><button onClick={() => restoreAppointment(appt.id)} className="text-green-600 hover:text-green-800 font-bold">♻️ שחזר</button></td></tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
            {/* Archived Invoices */}
            <div className="bg-white rounded shadow p-6">
              <h2 className="text-xl font-bold mb-4">קבלות שבוטלו</h2>
              {archivedInvoices.length === 0 ? <p className="text-gray-500">אין קבלות בארכיון.</p> : (
                <table className="w-full text-right border-collapse">
                  <thead><tr className="border-b"><th className="pb-2">מזהה לקוח</th><th className="pb-2">סכום</th><th className="pb-2">פעולות</th></tr></thead>
                  <tbody>
                    {archivedInvoices.map(inv => (
                      <tr key={inv.id} className="border-b"><td className="py-2">{inv.client_id}</td><td className="py-2">{inv.amount} ₪</td>
                      <td className="py-2"><button onClick={() => restoreInvoice(inv.id)} className="text-green-600 hover:text-green-800 font-bold">♻️ שחזר</button></td></tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      );
    }
  };

  return (
    <div className="flex h-screen bg-gray-100" dir="rtl">
      <div className="w-64 bg-[#1a2332] text-white flex flex-col shadow-lg">
        <div className="p-6 border-b border-gray-700 flex flex-col items-center">
          <h2 className="text-2xl font-bold text-[#c9a962]">FRIZURA Admin</h2>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <button onClick={() => setActiveTab('dashboard')} className={`w-full text-right px-4 py-2 rounded ${activeTab === 'dashboard' ? 'bg-[#c9a962] text-white' : 'hover:bg-gray-800'}`}>לוח בקרה</button>
          <button onClick={() => setActiveTab('appointments')} className={`w-full text-right px-4 py-2 rounded ${activeTab === 'appointments' ? 'bg-[#c9a962] text-white' : 'hover:bg-gray-800'}`}>יומן תורים</button>
          <button onClick={() => setActiveTab('clients')} className={`w-full text-right px-4 py-2 rounded ${activeTab === 'clients' ? 'bg-[#c9a962] text-white' : 'hover:bg-gray-800'}`}>לקוחות</button>
          <button onClick={() => setActiveTab('leads')} className={`w-full text-right px-4 py-2 rounded ${activeTab === 'leads' ? 'bg-[#c9a962] text-white' : 'hover:bg-gray-800'}`}>לידים CRM</button>
          <button onClick={() => setActiveTab('invoices')} className={`w-full text-right px-4 py-2 rounded ${activeTab === 'invoices' ? 'bg-[#c9a962] text-white' : 'hover:bg-gray-800'}`}>קופות וחשבוניות</button>
          <button onClick={() => setActiveTab('settings')} className={`w-full text-right px-4 py-2 rounded ${activeTab === 'settings' ? 'bg-[#c9a962] text-white' : 'hover:bg-gray-800'}`}>הגדרות עסק</button>
          <button onClick={() => setActiveTab('archive')} className={`w-full text-right px-4 py-2 rounded text-red-300 ${activeTab === 'archive' ? 'bg-red-900 text-white' : 'hover:bg-gray-800'}`}>סל מחזור</button>
        </nav>
        <div className="p-4 border-t border-gray-700">
          <button onClick={handleLogout} className="w-full text-right px-4 py-2 text-red-400 hover:bg-gray-800 rounded">התנתק</button>
        </div>
      </div>
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white shadow-sm p-4 flex justify-between items-center">
          <span className="text-gray-500 font-medium">ברוך שובך, מנהל</span>
          <button onClick={fetchData} className="text-[#c9a962] hover:text-yellow-600 font-bold">רענן נתונים ↻</button>
        </header>
        <main className="flex-1 p-8 overflow-y-auto">
          {loading ? <div className="flex justify-center items-center h-full"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#c9a962]"></div></div> : renderContent()}
        </main>
      </div>

      {/* MODALS */}
      {showClientModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white p-6 rounded shadow-lg w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">הוספת לקוח חדש</h2>
            <form onSubmit={createClient} className="flex flex-col gap-3">
              <input type="text" placeholder="שם פרטי" required className="border p-2 rounded" onChange={e => setFormData({...formData, first_name: e.target.value})} />
              <input type="text" placeholder="שם משפחה" required className="border p-2 rounded" onChange={e => setFormData({...formData, last_name: e.target.value})} />
              <input type="tel" placeholder="טלפון" required className="border p-2 rounded" onChange={e => setFormData({...formData, phone: e.target.value})} dir="ltr" />
              <input type="email" placeholder="אימייל (אופציונלי)" className="border p-2 rounded" onChange={e => setFormData({...formData, email: e.target.value})} dir="ltr" />
              <div className="flex justify-end gap-2 mt-4">
                <button type="button" onClick={() => setShowClientModal(false)} className="px-4 py-2 text-gray-600 bg-gray-100 rounded">ביטול</button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">שמור</button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {showApptModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white p-6 rounded shadow-lg w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">יצירת תור חדש</h2>
            <form onSubmit={createAppointment} className="flex flex-col gap-3">
              <select required className="border p-2 rounded" onChange={e => setFormData({...formData, client_id: e.target.value})}>
                <option value="">בחר לקוח...</option>
                {clients.map(c => <option key={c.id} value={c.id}>{c.first_name} {c.last_name} ({c.phone})</option>)}
              </select>
              <input type="text" placeholder="סוג שירות (למשל: תספורת גבר)" required className="border p-2 rounded" onChange={e => setFormData({...formData, service: e.target.value})} />
              <input type="date" required className="border p-2 rounded" onChange={e => setFormData({...formData, appointment_date: e.target.value})} />
              <select required className="border p-2 rounded" value={formData.appointment_time?.substring(0,5) || ""} onChange={e => setFormData({...formData, appointment_time: e.target.value+":00"})}>
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
              <div className="flex justify-end gap-2 mt-4">
                <button type="button" onClick={() => setShowApptModal(false)} className="px-4 py-2 text-gray-600 bg-gray-100 rounded">ביטול</button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">שמור</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showInvoiceModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white p-6 rounded shadow-lg w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">הפקת קבלה חדשה</h2>
            <form onSubmit={createInvoice} className="flex flex-col gap-3">
              <select required className="border p-2 rounded" onChange={e => setFormData({...formData, client_id: e.target.value})}>
                <option value="">בחר לקוח...</option>
                {clients.map(c => <option key={c.id} value={c.id}>{c.first_name} {c.last_name} ({c.phone})</option>)}
              </select>
              <input type="number" placeholder="סכום לתשלום (₪)" required className="border p-2 rounded" onChange={e => setFormData({...formData, amount: parseFloat(e.target.value)})} />
              <input type="text" placeholder="תיאור שירות" required className="border p-2 rounded" onChange={e => setFormData({...formData, service_description: e.target.value})} />
              <div className="flex justify-end gap-2 mt-4">
                <button type="button" onClick={() => setShowInvoiceModal(false)} className="px-4 py-2 text-gray-600 bg-gray-100 rounded">ביטול</button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">הפק</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
