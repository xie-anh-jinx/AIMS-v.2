'use client';

import React, { useEffect, useState, useCallback } from 'react';
import {useRouter} from 'next/navigation';
import { 
  Menu, Users, AlertTriangle, Settings, LogOut, ChevronRight, Activity, Database,
  Bell, Shield, Server, Eye, Search, X, Trash, User, Edit2, BookOpen, RefreshCw
} from 'lucide-react';
import {PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip as RechartsTooltip, Legend} from 'recharts';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface DashboardStats {
  total_students: number;
  total_active_students: number;
  high_risk_students: number;
  warning_students: number;
  safe_students: number;
  total_reminders_sent: number;
}

interface StudentRecord {
  id: number;
  nim: string;
  nama: string;
  angkatan: number;
  semester: number;
  prodi: string;
  status: string;
  email: string;
  nomor_whatsapp: string;
}

interface ChartEntry { name: string; value: number; }

interface TranscriptRecord {
  id: number;
  course: { kode: string; nama: string; sks: number };
  semester: number;
  grade: string;
  bobot: number;
}

// Status color helpers
const getStatusBadge = (status: string) => {
  switch (status) {
    case 'Aktif':    return 'bg-green-500/10 text-green-400 border-green-500/20';
    case 'Lulus':    return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
    case 'Drop Out': return 'bg-red-500/10 text-red-400 border-red-500/20';
    case 'Cuti':     return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
    default:         return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
  }
};

export default function ProdiDashboard() {
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('Dashboard');
  const [overview, setOverview] = useState<any>(null);
  const [students, setStudents] = useState<any[]>([]);
  const [advisors, setAdvisors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [prodiAdminName, setProdiAdminName] = useState<string>('Kaprodi');
  const [prodiName, setProdiName] = useState<string>('Program Studi');
  const [profilePictureUrl, setProfilePictureUrl] = useState<string | null>(null);

  // Filter state for Data Mahasiswa
  const [filterProdi, setFilterProdi] = useState('');
  const [filterAngkatan, setFilterAngkatan] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterLoading, setFilterLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalStudents, setTotalStudents] = useState(0);

  // Transcript state
  const [transcriptModalOpen, setTranscriptModalOpen] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<any>(null);
  const [transcriptData, setTranscriptData] = useState<any[]>([]);
  const [transcriptLoading, setTranscriptLoading] = useState(false);

  // Risk Students Modal State
  const [riskModalOpen, setRiskModalOpen] = useState(false);
  const [activeRiskZone, setActiveRiskZone] = useState<string>('');
  const [riskStudents, setRiskStudents] = useState<any[]>([]);
  const [riskLoading, setRiskLoading] = useState(false);

  // Admin notes
  const [showAdminNoteModal, setShowAdminNoteModal] = useState(false);
  const [adminNoteForm, setAdminNoteForm] = useState({ advisor_id: '', type: 'Peringatan', status: 'Warning', notes: '' });
  const [advisorsList, setAdvisorsList] = useState<any[]>([]);
  const [submittingAdminNote, setSubmittingAdminNote] = useState(false);
  const [sentAdminNotes, setSentAdminNotes] = useState<any[]>([]);

  // Profile Update State
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [profileForm, setProfileForm] = useState({ username: '', password: '', email: '', whatsapp: '', profile_picture: '' });
  const [submittingProfile, setSubmittingProfile] = useState(false);

  const openProfileModal = async () => {
    try {
      const res = await fetch(`${API_URL}/prodi/profile`, { headers: authHeaders() });
      if (res.ok) {
        const data = await res.json();
        setProfileForm({
          username: data.username || '',
          password: '',
          email: data.email || '',
          whatsapp: data.whatsapp || '',
          profile_picture: data.profile_picture || ''
        });
      } else {
        setProfileForm({ username: '', password: '', email: '', whatsapp: '', profile_picture: '' });
      }
    } catch (err) {
      console.error(err);
      setProfileForm({ username: '', password: '', email: '', whatsapp: '', profile_picture: '' });
    }
    setShowProfileModal(true);
  };

  // Stats arrays for graphs
  const [stats, setStats] = useState<any>(null);
  const [semesterDist, setSemesterDist] = useState<any[]>([]);
  const [statusDist, setStatusDist] = useState<any[]>([]);
  const [prodis, setProdis] = useState<string[]>([]);
  const [angkatans, setAngkatans] = useState<number[]>([]);
  const [allStudents, setAllStudents] = useState<any[]>([]);

  const getToken = () => {
    if (typeof document === 'undefined') return '';
    const match = document.cookie.match(/(^| )token=([^;]+)/);
    return match ? match[2] : '';
  };

  const authHeaders = useCallback(() => ({ Authorization: `Bearer ${getToken()}` }), []);

  const fetchData = useCallback(async () => {
    try {
      const [ovRes, stRes, advRes, semRes, statRes, angkatanRes] = await Promise.all([
        fetch(`${API_URL}/prodi/overview`, { headers: authHeaders() }),
        fetch(`${API_URL}/prodi/students?limit=100`, { headers: authHeaders() }),
        fetch(`${API_URL}/prodi/advisors`, { headers: authHeaders() }),
        fetch(`${API_URL}/prodi/stats/semester`, { headers: authHeaders() }),
        fetch(`${API_URL}/prodi/stats/status`, { headers: authHeaders() }),
        fetch(`${API_URL}/prodi/stats/angkatan`, { headers: authHeaders() })
      ]);
      
      if (ovRes.status === 401) { router.push('/login'); return; }
      
      const ov = await ovRes.json();
      setOverview(ov);
      setStats(ov);
      setTotalStudents(ov.total_students);

      const st = await stRes.json();
      setStudents(st);
      setAllStudents(st);

      const adv = await advRes.json();
      setAdvisors(adv);
      setAdvisorsList(adv);
      if (Array.isArray(adv) && adv.length > 0) {
        setAdminNoteForm(prev => ({ ...prev, advisor_id: adv[0].id.toString() }));
      }

      // Mock setting remaining graphs
      setSemesterDist(await semRes.json());
      setStatusDist(await statRes.json());
      
      const angkatanData = await angkatanRes.json();
      setAngkatans(angkatanData.map((d: any) => Number(d.name)).sort((a: number, b: number) => b - a));
    } catch (e) {
      console.warn("Tunggu sebentar, menghubungkan ke server...", e);
    } finally {
      setLoading(false);
    }
  }, [authHeaders, router]);

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingProfile(true);
    try {
      const res = await fetch(`${API_URL}/prodi/profile`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify({
          username: profileForm.username,
          password: profileForm.password,
          email: profileForm.email,
          whatsapp: profileForm.whatsapp
        })
      });
      if (res.ok) {
        if (profileForm.profile_picture) {
           await fetch(`${API_URL}/auth/profile-picture`, {
             method: 'PUT',
             headers: { 'Content-Type': 'application/json', ...authHeaders() },
             body: JSON.stringify({ profile_picture: profileForm.profile_picture })
           });
           setProfilePictureUrl(profileForm.profile_picture);
           localStorage.setItem('profile_picture', profileForm.profile_picture);
        }
        alert("Profil berhasil diperbarui!");
        setShowProfileModal(false);
        if (profileForm.username) {
          document.cookie = `name=${profileForm.username}; path=/; max-age=86400`;
          setProdiAdminName(profileForm.username);
        }
      } else {
        const data = await res.json();
        alert(data.detail || "Gagal memperbarui profil.");
      }
    } catch (err) {
      console.error(err);
      alert("Gagal memperbarui profil.");
    } finally {
      setSubmittingProfile(false);
    }
  };

  const openTranscript = async (student: any) => {
    setSelectedStudent(student);
    setTranscriptModalOpen(true);
    setTranscriptLoading(true);
    try {
      const res = await fetch(`${API_URL}/students/${student.nim}/transcript`, { headers: authHeaders() });
      const data = await res.json();
      setTranscriptData(Array.isArray(data) ? data : []);
    } catch (e) {
      console.warn("Gagal membuka transkrip", e);
    } finally {
      setTranscriptLoading(false);
    }
  };

  const handleResetUserPassword = async (username: string) => {
    const confirmReset = window.confirm(`Apakah Anda yakin ingin mereset password untuk user ${username} kembali ke default ("password123")?`);
    if (!confirmReset) return;
    
    try {
      const res = await fetch(`${API_URL}/auth/reset-user-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify({
          target_username: username,
          new_password: "password123"
        })
      });
      if (res.ok) {
        alert(`Sandi untuk user ${username} berhasil disetel kembali ke "password123"!`);
      } else {
        const data = await res.json();
        alert(data.detail || "Gagal mereset sandi.");
      }
    } catch (e) {
      console.error(e);
      alert("Gagal mereset sandi.");
    }
  };

  const openRiskModal = async (zone: 'merah' | 'kuning' | 'hijau', title: string) => {
    setActiveRiskZone(title);
    setRiskModalOpen(true);
    setRiskLoading(true);
    try {
      const res = await fetch(`${API_URL}/prodi/risk-students?zone=${zone}`, { headers: authHeaders() });
      if (res.ok) {
        setRiskStudents(await res.json());
      } else {
        setRiskStudents([]);
      }
    } catch (e) {
      console.warn("Gagal membuka data zona risiko", e);
    } finally {
      setRiskLoading(false);
    }
  };

  const fetchSentNotes = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/prodi/advisor-notes/sent`, { headers: authHeaders() });
      if (res.ok) {
        const data = await res.json();
        setSentAdminNotes(Array.isArray(data) ? data : []);
      }
    } catch (e) {
      console.warn("Gagal mengambil catatan (Mungkin server sibuk)...", e);
    }
  }, [authHeaders]);

  const handleCreateAdminNote = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingAdminNote(true);
    try {
      const r = await fetch(`${API_URL}/prodi/advisor-notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify({
          advisor_id: parseInt(adminNoteForm.advisor_id, 10),
          type: adminNoteForm.type,
          status: adminNoteForm.status,
          notes: adminNoteForm.notes
        })
      });
      if (r.ok) {
        alert("Pesan berhasil dikirim ke PA!");
        setAdminNoteForm(prev => ({ ...prev, notes: '' }));
        setShowAdminNoteModal(false);
        fetchSentNotes();
      } else {
        const error = await r.json();
        alert(error.detail || "Gagal mengirim catatan");
      }
    } catch (e) {
      alert("Terjadi kesalahan jaringan");
    } finally {
      setSubmittingAdminNote(false);
    }
  };

  const handleDeleteSentNote = async (id: number) => {
    if (!confirm("Hapus catatan ini dari riwayat?")) return;
    try {
      const r = await fetch(`${API_URL}/prodi/advisor-notes/${id}`, {
        method: 'DELETE',
        headers: authHeaders()
      });
      if (r.ok) {
        alert("Catatan dihapus");
        fetchSentNotes();
      }
    } catch (e) {
       alert("Gagal menghapus");
    }
  };

  useEffect(() => {
    const token = getToken();
    const role = document.cookie.match(/(^| )role=([^;]+)/)?.[2];
    if (!token || role !== 'PRODI') { router.push('/login'); return; }

    const cachedPic = localStorage.getItem('profile_picture');
    if (cachedPic) setProfilePictureUrl(cachedPic);
    
    const nameMatch = document.cookie.match(/(^| )name=([^;]+)/);
    if(nameMatch) setProdiAdminName(decodeURIComponent(nameMatch[2]));

    const prodiMatch = document.cookie.match(/(^| )prodi_name=([^;]+)/);
    if (prodiMatch) setProdiName(decodeURIComponent(prodiMatch[2]));

    fetchData();
    fetchSentNotes();
  }, [router, authHeaders, fetchSentNotes, fetchData]);

  const applyFilters = useCallback(async (eOrPage?: any) => {
    const page = typeof eOrPage === 'number' ? eOrPage : 1;
    setFilterLoading(true);
    try {
      const limit = 50;
      const skip = (page - 1) * limit;
      const params = new URLSearchParams({ limit: limit.toString(), skip: skip.toString() });
      if (filterAngkatan) params.set('angkatan', filterAngkatan);
      if (filterStatus) params.set('status', filterStatus);
      if (searchQuery) params.set('search', searchQuery);
      
      const res = await fetch(`${API_URL}/prodi/students?${params}`, { headers: authHeaders() });
      const st = await res.json();
      setStudents(st);
      setAllStudents(st);
      setCurrentPage(page);
    } catch (e) {
      console.warn("Gagal menerapkan filter...", e);
    } finally {
      setFilterLoading(false);
    }
  }, [filterAngkatan, filterStatus, searchQuery, authHeaders]);

  const handleLogout = () => {
    document.cookie = 'token=; path=/; max-age=0';
    document.cookie = 'role=; path=/; max-age=0';
    document.cookie = 'name=; path=/; max-age=0';
    document.cookie = 'prodi_name=; path=/; max-age=0';
    router.push('/login');
  };

  if (loading || !stats) {
    return (
      <div className="min-h-screen bg-[#0b1121] flex items-center justify-center">
        <div className="flex flex-col items-center">
          <div className="w-12 h-12 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mb-4" />
          <p className="text-blue-400 font-medium">Memuat Portal Prodi...</p>
        </div>
      </div>
    );
  }

  // Pie chart: Aktif vs Cuti vs lainnya
  const PIE_COLORS: Record<string, string> = {
    'Aktif': '#22c55e', 'Lulus': '#3b82f6',
    'Drop Out': '#ef4444', 'Cuti': '#eab308', 'Non Aktif': '#94a3b8',
  };

  return (
    <div className="flex min-h-screen font-sans bg-[#0b1121] text-slate-300">
      
      {/* ── Sidebar ─────────────────────────────────────────────────── */}
      <aside className="w-[280px] bg-[#111827] flex flex-col fixed h-full z-20 border-r border-[#1f2937]">
        <div className="p-6 pb-6">
          <div className="flex flex-col items-center justify-center text-center mb-6">
            <div className="w-20 h-20 rounded-xl overflow-hidden bg-gradient-to-tr from-slate-700 to-slate-800 border border-slate-600 mb-3 flex items-center justify-center text-white">
              {profilePictureUrl ? (
                <img src={profilePictureUrl} alt="Profile" className="w-full h-full object-cover" />
              ) : (
                <User size={40} className="text-slate-400" />
              )}
            </div>
            <div>
              <p className="text-[15px] font-bold text-slate-200">{prodiAdminName}</p>
              <p className="text-xs text-slate-400 mt-1">{prodiName}</p>
              <p className="text-xs text-slate-500 font-medium mt-1">Ketua Program Studi</p>
            </div>
          </div>
          <button 
            onClick={openProfileModal}
            className="mt-4 flex items-center justify-center gap-2 w-full py-2 px-3 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-semibold transition"
          >
            <Edit2 size={12} />
            Pengaturan Profil
          </button>
        </div>

        <nav className="flex-1 px-4 space-y-1.5 overflow-y-auto">
          {[
            { id: 'Dashboard', icon: Activity, label: 'Dashboard' },
            { id: 'Data Mahasiswa', icon: Users, label: 'Data Mahasiswa' },
            { id: 'Monitoring Dosen PA', icon: BookOpen, label: 'Monitoring Dosen PA' },
            { id: 'Riwayat Catatan PA', icon: Bell, label: 'Riwayat Catatan PA' },
            { id: 'Analisis Risiko', icon: AlertTriangle, label: 'Analisis Risiko' }
          ].map(({ id, icon: Icon, label }) => {
            const active = activeTab === id;
            return (
              <button key={id} onClick={() => { setActiveTab(id); if (id === 'Data Mahasiswa') applyFilters(); }}
                className={`w-full flex items-center justify-between px-4 py-3 rounded-lg transition-all group ${active ? 'bg-red-500/10 text-red-400 border-l-4 border-red-500' : 'text-slate-400 hover:text-slate-200 hover:bg-[#1f2937] border-l-4 border-transparent'}`}>
                <div className="flex items-center gap-3">
                  <Icon size={18} className={active ? 'text-red-400' : 'text-slate-500 group-hover:text-slate-400'} />
                  <span className={`text-sm ${active ? 'font-semibold' : 'font-medium'}`}>{label}</span>
                </div>
                {active && <ChevronRight size={14} className="text-red-500" />}
              </button>
            );
          })}
        </nav>

        <div className="p-4 border-t border-[#1f2937] mt-auto">
          <button onClick={handleLogout} className="w-full flex items-center justify-center gap-3 px-3 py-2.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition mt-1">
            <LogOut size={16} /><span className="text-sm font-medium">Keluar</span>
          </button>
        </div>
      </aside>

      {/* ── Main Content ─────────────────────────────────────────────── */}
      <main className="flex-1 md:ml-[280px] p-4 md:p-8 overflow-y-auto w-full">
        <div className="max-w-[1200px] mx-auto w-full">
          
          <div className="md:hidden flex items-center mb-6"><button onClick={() => setMobileMenuOpen(true)} className="text-slate-300 hover:text-white p-2 -ml-2"><Menu size={24} /></button></div>
          {/* Header */}
          <div className="flex items-start justify-between mb-8">
            <div>
              <h1 className="text-2xl font-bold text-white">
                Dashboard <span className="text-orange-500">Program Studi</span>
              </h1>
              <p className="text-[#64748b] text-sm mt-1">Manajemen Akademik Tingkat Program Studi</p>
            </div>
            <div className="flex items-center gap-3">
              <button 
                onClick={() => setShowAdminNoteModal(true)}
                className="flex items-center gap-2 bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition"
              >
                Buat Catatan Baru
              </button>
              <div className="flex items-center gap-2 bg-[#1e293b]/50 border border-[#334155] px-3 py-2 rounded-xl">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                <span className="text-xs text-slate-400 font-medium whitespace-nowrap">Sistem Aktif</span>
              </div>
            </div>
          </div>

          {/* ── Tab: Dashboard ─────────────────────────────────────── */}
          {activeTab === 'Dashboard' && (
            <div className="space-y-6">
              {/* Stat Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                {[
                  { label: 'Total Mahasiswa', value: stats?.total_students, icon: Database, color: 'blue' },
                  { label: 'Mahasiswa Aktif', value: stats?.total_active_students, icon: Activity, color: 'green' },
                  { label: 'Risiko D.O.', value: stats?.high_risk_students, icon: AlertTriangle, color: 'red', note: 'Perlu tindak' },
                  { label: 'Reminder Terkirim', value: stats?.total_reminders_sent, icon: Bell, color: 'yellow', note: 'Hari ini: 0' },
                ].map(({ label, value, icon: Icon, color, note }) => (
                  <div key={label} className="bg-[#1e293b] rounded-xl p-5 border border-[#334155]">
                    <div className="flex justify-between items-start mb-4">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        color === 'blue' ? 'bg-blue-500/10 text-blue-500' :
                        color === 'green' ? 'bg-green-500/10 text-green-500' :
                        color === 'red' ? 'bg-red-500/10 text-red-500' :
                        'bg-yellow-500/10 text-yellow-500'
                      }`}><Icon size={20} /></div>
                      {note && <span className="text-xs font-semibold text-slate-400">{note}</span>}
                    </div>
                    <h3 className="text-3xl font-bold text-white mb-1">{value?.toLocaleString('id-ID') ?? '–'}</h3>
                    <p className="text-xs text-slate-400 font-medium">{label}</p>
                  </div>
                ))}
              </div>

              {/* Charts */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Pie: Status */}
                <div className="bg-[#1e293b] rounded-xl p-6 border border-[#334155]">
                  <h3 className="text-sm font-semibold text-white mb-4">Status Mahasiswa</h3>
                  <div className="h-[200px]">
                    {statusDist.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie 
                            data={statusDist} 
                            cx="50%" 
                            cy="50%" 
                            innerRadius={55} 
                            outerRadius={80} 
                            paddingAngle={2} 
                            dataKey="value" 
                            nameKey="name" 
                            stroke="none"
                            isAnimationActive={false}
                          >
                            {statusDist.map((entry) => (
                              <Cell key={`cell-${entry.name}`} fill={PIE_COLORS[entry.name] ?? '#64748b'} />
                            ))}
                          </Pie>
                          <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px', color: '#fff' }} itemStyle={{ color: '#fff' }} />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="w-full h-full flex flex-col justify-center items-center">
                        <div className="w-8 h-8 rounded-full border-2 border-slate-700 border-t-slate-500 animate-spin mb-2"></div>
                      </div>
                    )}
                  </div>
                  <div className="flex flex-wrap gap-x-4 gap-y-1.5 mt-2">
                    {statusDist.map(s => (
                      <div key={s.name} className="flex items-center gap-1.5">
                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: PIE_COLORS[s.name] ?? '#64748b' }}></div>
                        <span className="text-[11px] text-slate-400">{s.name} ({s.value.toLocaleString('id-ID')})</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Bar: Distribusi per Semester */}
                <div className="bg-[#1e293b] rounded-xl p-6 border border-[#334155] col-span-2">
                  <h3 className="text-sm font-semibold text-white mb-4">Distribusi Mahasiswa Aktif per Semester</h3>
                  <div className="h-[240px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={semesterDist} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                        <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                        <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                        <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px', color: '#fff' }} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                        <Bar dataKey="value" name="Mahasiswa" fill="#ef4444" radius={[4, 4, 0, 0]} barSize={28} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {/* Recent Students table */}
              <div className="bg-[#1e293b] rounded-xl border border-[#334155] overflow-hidden">
                <div className="p-5 border-b border-[#334155] flex justify-between items-center">
                  <h3 className="text-sm font-semibold text-white">Mahasiswa Terbaru</h3>
                  <button onClick={() => setActiveTab('Data Mahasiswa')} className="text-xs text-blue-400 hover:text-blue-300 transition">Lihat Semua →</button>
                </div>
                <div className="overflow-x-auto w-full"><table className="w-full text-left text-sm min-w-[700px]">
                  <thead className="bg-[#0b1121]/50 border-b border-[#334155]">
                    <tr>
                      {['NIM','Nama','Program Studi','Semester','Status'].map(h => (
                        <th key={h} className="py-3 px-5 text-xs text-slate-400 font-medium">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#334155]">
                    {allStudents.slice(0, 5).map(s => (
                      <tr key={s.nim} className="hover:bg-[#334155]/20 transition">
                        <td className="py-4 px-5 text-xs font-mono text-slate-300">{s.nim}</td>
                        <td className="py-4 px-5">
                          <div className="flex items-center gap-3">
                            <div className="w-7 h-7 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs font-bold shrink-0">{s.nama.charAt(0)}</div>
                            <span className="font-semibold text-slate-200 text-[13px]">{s.nama}</span>
                          </div>
                        </td>
                        <td className="py-4 px-5 text-sm text-slate-400">{s.prodi}</td>
                        <td className="py-4 px-5 text-sm text-slate-400">Semester {s.semester}</td>
                        <td className="py-4 px-5">
                          <span className={`inline-flex px-2 py-0.5 rounded text-[11px] font-medium border ${getStatusBadge(s.status)}`}>{s.status}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table></div>
              </div>
            </div>
          )}

          {/* ── Tab: Analisis Risiko ───────────────────────────────── */}
          {activeTab === 'Analisis Risiko' && (
            <div className="bg-[#1e293b] rounded-xl border border-[#334155] p-8 space-y-6">
              <div className="flex items-center gap-2">
                <AlertTriangle size={18} className="text-red-400" />
                <h2 className="text-[15px] font-semibold text-white">Analisis Profil Risiko Akademik</h2>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                {[
                  { id: 'merah', label: 'Zona Merah (Kritis)', val: stats?.high_risk_students, sub: 'Mahasiswa dengan indikasi Drop Out tinggi (IPK < 2.0)', bg: 'bg-[#2c1316]', border: 'border-red-900/30', color: 'text-red-400', glow: 'bg-red-900/40' },
                  { id: 'kuning', label: 'Zona Kuning (Warning)', val: stats?.warning_students, sub: 'Performa akademik pas-pasan (IPK 2.0 - 2.74)', bg: 'bg-[#282111]', border: 'border-yellow-900/30', color: 'text-yellow-400', glow: 'bg-yellow-900/40' },
                  { id: 'hijau', label: 'Zona Hijau (Aman)', val: stats?.safe_students, sub: 'Trek akademik aman (IPK 2.75 ke atas)', bg: 'bg-[#0f291e]', border: 'border-green-900/30', color: 'text-green-400', glow: 'bg-green-900/40', disabled: true },
                ].map(({ id, label, val, sub, bg, border, color, glow, disabled }) => (
                  <div 
                    key={label} 
                    onClick={() => !disabled && openRiskModal(id as any, label)}
                    className={`${bg} rounded-xl p-5 border ${border} relative overflow-hidden ${!disabled ? 'cursor-pointer hover:scale-[1.02] transition-transform' : 'opacity-80'}`}
                  >
                    <div className={`absolute -right-6 -bottom-6 w-24 h-24 ${glow} rounded-full blur-xl`}></div>
                    <p className={`text-sm font-semibold ${color} mb-3`}>{label}</p>
                    <h3 className="text-4xl font-bold text-white mb-2">{val?.toLocaleString('id-ID') ?? '–'}</h3>
                    <p className="text-xs text-slate-400">{sub}</p>
                  </div>
                ))}
              </div>
              <div className="p-5 rounded-xl border border-[#334155] bg-[#1a2333]">
                <h3 className="text-sm font-semibold text-white mb-4">Tindakan Mitigasi Berbasis AI (Rekomendasi)</h3>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2 text-sm text-slate-300">
                    <div className="w-1.5 h-1.5 rounded-full bg-red-500 mt-1.5 shrink-0"></div>
                    <p>Jadwalkan <em>mandatory counseling</em> sesegera mungkin untuk <strong className="text-white">{stats?.high_risk_students?.toLocaleString('id-ID')} mahasiswa</strong> (Zona Merah).</p>
                  </li>
                  <li className="flex items-start gap-2 text-sm text-slate-300">
                    <div className="w-1.5 h-1.5 rounded-full bg-yellow-500 mt-1.5 shrink-0"></div>
                    <p>Kirimkan broadcast peringatan perbaikan KRS via Telegram & WhatsApp kepada <strong className="text-white">{stats?.warning_students?.toLocaleString('id-ID')} mahasiswa</strong> (Zona Kuning).</p>
                  </li>
                </ul>
              </div>
            </div>
          )}

          {/* ── Tab: Pengaturan ───────────────────────────────────── */}
          {activeTab === 'Pengaturan' && (
            <div className="bg-[#1e293b] rounded-xl border border-[#334155] p-8">
              <div className="flex items-center gap-2 mb-8">
                <Settings size={18} className="text-slate-400" />
                <h2 className="text-[15px] font-semibold text-white">Pengaturan Sistem</h2>
              </div>
              <div className="space-y-8">
                <div>
                  <h3 className="text-sm font-semibold text-slate-200 mb-4">Integrasi OpenClaw & Notifikasi</h3>
                  <div className="space-y-4">
                    <div className="p-4 rounded-xl border border-[#334155] bg-[#1a2333] flex justify-between items-center">
                      <div>
                        <p className="text-sm font-semibold text-white">Status Gateway Notifikasi</p>
                        <p className="text-xs text-slate-500 mt-1">Mengatur *webhook* komunikasi dengan module OpenClaw.</p>
                      </div>
                      <span className="text-xs font-semibold text-green-500">Aktif (Connected)</span>
                    </div>
                    <div className="p-4 rounded-xl border border-[#334155] bg-[#1a2333] flex justify-between items-center gap-4">
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-white">Saluran Prioritas</p>
                        <p className="text-xs text-slate-500 mt-1">Metode pengiriman utama untuk pengingat sistem.</p>
                      </div>
                      <select className="bg-[#1e293b] border border-[#334155] text-white text-sm px-4 py-2 rounded-lg focus:outline-none focus:border-blue-500 w-48">
                        <option>WhatsApp (Default)</option>
                        <option>Telegram Channel</option>
                        <option>Email Blast</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-200 mb-4">Bobot Algoritma AI (Ruleset)</h3>
                  <div className="flex flex-col sm:flex-row gap-4">
                    <div className="flex-1 p-4 rounded-xl border border-[#334155] bg-[#1a2333]">
                      <p className="text-xs text-slate-400 mb-2">Batas IPK Kritis (DO Warning)</p>
                      <input type="text" defaultValue="2,00" className="w-full bg-[#1e293b] border border-[#334155] text-white text-sm px-4 py-2.5 rounded-lg focus:outline-none focus:border-blue-500" />
                    </div>
                    <div className="flex-1 p-4 rounded-xl border border-[#334155] bg-[#1a2333]">
                      <p className="text-xs text-slate-400 mb-2">Toleransi Fluktuasi IPS (Warning)</p>
                      <input type="text" defaultValue="0,50" className="w-full bg-[#1e293b] border border-[#334155] text-white text-sm px-4 py-2.5 rounded-lg focus:outline-none focus:border-blue-500" />
                    </div>
                  </div>
                </div>
                <div className="flex justify-end pt-4">
                  <button className="bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm px-6 py-2.5 rounded-lg transition-colors">Simpan Perubahan</button>
                </div>
              </div>
            </div>
          )}

          {/* ── Tab: Data Mahasiswa ───────────────────────────────── */}
          {activeTab === 'Data Mahasiswa' && (
            <div className="bg-[#1e293b] rounded-xl border border-[#334155] overflow-hidden">
              <div className="p-6 border-b border-[#334155] bg-[#1a2333]">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-[15px] font-semibold text-white">Direktori Lengkap Mahasiswa</h2>
                    <p className="text-xs text-slate-500 mt-1">Mengelola data mahasiswa terstruktur berdasarkan program studi.</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-white">{allStudents.length.toLocaleString('id-ID')}</p>
                    <p className="text-[10px] text-slate-500">Hasil ditampilkan</p>
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-3">
                  <select value={filterProdi} onChange={e => setFilterProdi(e.target.value)}
                    className="bg-[#1e293b] border border-[#334155] text-slate-300 text-xs px-3 py-2 rounded-lg focus:outline-none focus:border-blue-500 min-w-[160px]">
                    <option value="">Semua Prodi</option>
                    {prodis.map(p => <option key={p} value={p}>{p}</option>)}
                  </select>
                  <select value={filterAngkatan} onChange={e => setFilterAngkatan(e.target.value)}
                    className="bg-[#1e293b] border border-[#334155] text-slate-300 text-xs px-3 py-2 rounded-lg focus:outline-none focus:border-blue-500 min-w-[140px]">
                    <option value="">Semua Angkatan</option>
                    {angkatans.map(a => <option key={a} value={String(a)}>{a}</option>)}
                  </select>
                  <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)}
                    className="bg-[#1e293b] border border-[#334155] text-slate-300 text-xs px-3 py-2 rounded-lg focus:outline-none focus:border-blue-500">
                    <option value="">Semua Status</option>
                    {['Aktif','Cuti','Lulus','Drop Out','Non Aktif'].map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                  <div className="relative flex-1 min-w-[200px]">
                    <input type="text" value={searchQuery} onChange={e => setSearchQuery(e.target.value)} onKeyDown={e => e.key === 'Enter' && applyFilters()}
                      placeholder="Cari Nama atau NIM... (Enter)" className="w-full pl-9 pr-4 py-2 bg-[#1e293b] border border-[#334155] text-white text-xs rounded-lg focus:outline-none focus:border-blue-500" />
                    <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  </div>
                  <button onClick={applyFilters} disabled={filterLoading}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg transition disabled:opacity-60">
                    {filterLoading ? 'Memuat...' : 'Filter'}
                  </button>
                </div>
              </div>

              <div className="overflow-x-auto">
                <div className="overflow-x-auto w-full"><table className="w-full text-left text-sm min-w-[700px]">
                  <thead className="bg-[#1e293b] border-b border-[#334155]">
                    <tr>
                      {['NIM','Nama Lengkap','Program Studi','Angkatan','Semester','Status Terkini','Aksi'].map(h => (
                        <th key={h} className="py-4 px-5 text-xs text-slate-400 font-semibold">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#334155]">
                    {allStudents.length === 0 ? (
                      <tr><td colSpan={7} className="py-10 text-center text-slate-500 text-sm">Tidak ada data yang ditemukan.</td></tr>
                    ) : allStudents.map(s => (
                      <tr key={s.nim} className="hover:bg-[#334155]/20 transition">
                        <td className="py-3.5 px-5 text-xs text-slate-300 font-mono">{s.nim}</td>
                        <td className="py-3.5 px-5 font-semibold text-slate-200 text-sm">{s.nama}</td>
                        <td className="py-3.5 px-5 text-xs text-slate-400">{s.prodi}</td>
                        <td className="py-3.5 px-5 text-xs text-slate-400">{s.angkatan}</td>
                        <td className="py-3.5 px-5 text-xs text-slate-400">Sem {s.semester}</td>
                        <td className="py-3.5 px-5">
                          <span className={`inline-flex px-2 py-0.5 rounded text-[11px] font-medium border ${getStatusBadge(s.status)}`}>{s.status}</span>
                        </td>
                        <td className="py-3.5 px-5">
                          <div className="flex gap-2">
                            <button onClick={() => openTranscript(s)} className="text-xs bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 px-3 py-1.5 rounded-lg border border-blue-500/10 flex items-center gap-1.5 transition">
                              <Eye size={12} /> Lihat Transkrip
                            </button>
                            <button 
                              onClick={() => handleResetUserPassword(s.nim)} 
                              className="text-xs bg-red-500/10 hover:bg-red-500/20 text-red-400 px-3 py-1.5 rounded-lg border border-red-500/10 flex items-center gap-1.5 transition font-semibold"
                            >
                              <RefreshCw size={12} /> Reset Sandi
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table></div>
              </div>
              <div className="flex justify-between items-center p-4 border-t border-[#334155] bg-[#1a2333]">
                <div className="text-xs text-slate-500">
                  Halaman {currentPage} &bull; Menampilkan {(currentPage - 1) * 50 + (allStudents.length > 0 ? 1 : 0)}-{(currentPage - 1) * 50 + allStudents.length}
                </div>
                <div className="flex items-center gap-2">
                  <button onClick={() => applyFilters(currentPage - 1)} disabled={currentPage === 1 || filterLoading} className="px-3 py-1.5 text-xs font-semibold text-slate-300 bg-[#1e293b] border border-[#334155] rounded hover:bg-[#334155] disabled:opacity-50 transition">Sebelumnya</button>
                  <button onClick={() => applyFilters(currentPage + 1)} disabled={allStudents.length < 50 || filterLoading} className="px-3 py-1.5 text-xs font-semibold text-slate-300 bg-[#1e293b] border border-[#334155] rounded hover:bg-[#334155] disabled:opacity-50 transition">Selanjutnya</button>
                </div>
              </div>
            </div>
          )}

          {/* ── Tab: Monitoring Dosen PA ───────────────────────────── */}
          {activeTab === 'Monitoring Dosen PA' && (
            <div className="bg-[#1e293b] rounded-xl border border-[#334155] overflow-hidden">
              <div className="p-6 border-b border-[#334155] bg-[#1a2333] flex justify-between items-center">
                <div>
                  <h2 className="text-[15px] font-semibold text-white">Monitoring Dosen Penasihat Akademik (PA)</h2>
                  <p className="text-xs text-slate-500 mt-1">Daftar Dosen PA di program studi beserta performa bimbingan dan konsultasi.</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-white">{advisors.length}</p>
                  <p className="text-[10px] text-slate-500">Total Dosen PA</p>
                </div>
              </div>

              <div className="overflow-x-auto">
                <div className="overflow-x-auto w-full"><table className="w-full text-left text-sm min-w-[700px]">
                  <thead className="bg-[#0b1121]/50 border-b border-[#334155]">
                    <tr>
                      {['Nama Dosen Penasihat', 'Mahasiswa Bimbingan', 'Total Konsultasi', 'Pesan Terkirim', 'Aksi'].map(h => (
                        <th key={h} className="py-4 px-5 text-xs text-slate-400 font-semibold">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#334155]">
                    {advisors.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="py-10 text-center text-slate-500 text-sm">
                          Tidak ada data Penasihat Akademik di prodi ini.
                        </td>
                      </tr>
                    ) : (
                      advisors.map(adv => (
                        <tr key={adv.id} className="hover:bg-[#334155]/20 transition">
                          <td className="py-3.5 px-5">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 rounded-full bg-orange-500/10 text-orange-400 flex items-center justify-center text-xs font-bold shrink-0">
                                {adv.nama.charAt(0)}
                              </div>
                              <div>
                                <span className="font-semibold text-slate-200 text-[13px]">{adv.nama}</span>
                              </div>
                            </div>
                          </td>
                          <td className="py-3.5 px-5 text-sm text-slate-300 font-medium">{adv.student_count} Mahasiswa</td>
                          <td className="py-3.5 px-5 text-sm text-slate-400">{adv.total_consultations || 0} Kali</td>
                          <td className="py-3.5 px-5 text-sm text-slate-400">{adv.warnings_sent || 0} Pesan</td>
                          <td className="py-3.5 px-5">
                            <button
                              onClick={() => {
                                setAdminNoteForm({ advisor_id: adv.id.toString(), type: 'Peringatan', status: 'Warning', notes: '' });
                                setShowAdminNoteModal(true);
                              }}
                              className="text-xs bg-orange-500/10 hover:bg-orange-500/20 text-orange-400 px-3 py-1.5 rounded-lg border border-orange-500/10 flex items-center gap-1.5 transition font-semibold"
                            >
                              <Bell size={12} /> Kirim Catatan
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table></div>
              </div>
            </div>
          )}

          {/* ── Tab: Agent Monitor (static) ───────────────────────── */}
          {activeTab === 'Agent Monitor' && (
            <div className="bg-[#1e293b] rounded-xl border border-[#334155] p-8 flex flex-col items-center justify-center min-h-[400px]">
              <Server size={48} className="text-slate-600 mb-4" />
              <h3 className="text-lg font-bold text-white mb-2">Agent Monitor</h3>
              <p className="text-slate-400 text-sm text-center max-w-md">Layanan backend dan integrasi webhook OpenClaw node sedang aktif. Sinkronisasi data mahasiswa otomatis berjalan di latar belakang.</p>
              <div className="mt-6 flex items-center gap-2 bg-green-500/10 border border-green-500/20 px-4 py-2 rounded-full">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span className="text-xs text-green-400 font-medium">Semua Layanan Online</span>
              </div>
            </div>
          )}

        </div>
      </main>

      {/* Transcript Modal */}
      {transcriptModalOpen && selectedStudent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#000000_cc] backdrop-blur-sm p-4">
          <div className="bg-[#0f172a] border border-[#334155] rounded-xl w-full max-w-3xl flex flex-col max-h-[90vh] shadow-2xl">
            <div className="flex justify-between items-center p-5 border-b border-[#334155]">
              <div>
                <h3 className="text-lg font-bold text-white">Transkrip Akademik</h3>
                <p className="text-sm text-slate-400">{selectedStudent.nama} ({selectedStudent.nim}) - {selectedStudent.prodi}</p>
              </div>
              <button onClick={() => setTranscriptModalOpen(false)} className="text-slate-400 hover:text-white transition">
                <X size={24} />
              </button>
            </div>
            <div className="p-5 overflow-y-auto flex-1">
              {transcriptLoading ? (
                <div className="py-12 flex justify-center"><div className="w-8 h-8 border-4 border-slate-700 border-t-blue-500 rounded-full animate-spin"></div></div>
              ) : transcriptData.length === 0 ? (
                <div className="py-12 text-center text-slate-500">Tidak ada data transkrip.</div>
              ) : (
                <div className="overflow-x-auto w-full"><table className="w-full text-left text-sm min-w-[700px]">
                  <thead className="bg-[#1e293b] border border-[#334155]">
                    <tr>
                      <th className="py-2.5 px-4 text-xs text-slate-400 font-semibold border-b border-[#334155]">Semester</th>
                      <th className="py-2.5 px-4 text-xs text-slate-400 font-semibold border-b border-[#334155]">Kode MK</th>
                      <th className="py-2.5 px-4 text-xs text-slate-400 font-semibold border-b border-[#334155]">Mata Kuliah</th>
                      <th className="py-2.5 px-4 text-xs text-slate-400 font-semibold border-b border-[#334155] text-center">SKS</th>
                      <th className="py-2.5 px-4 text-xs text-slate-400 font-semibold border-b border-[#334155] text-center">Nilai</th>
                      <th className="py-2.5 px-4 text-xs text-slate-400 font-semibold border-b border-[#334155] text-center">Bobot</th>
                    </tr>
                  </thead>
                  <tbody className="border border-[#334155]">
                    {transcriptData.map((t, idx) => (
                      <tr key={idx} className="border-b border-[#334155] hover:bg-[#1e293b]/50">
                        <td className="py-2.5 px-4 text-slate-300">Sem {t.semester}</td>
                        <td className="py-2.5 px-4 text-slate-400 font-mono text-xs">{t.course?.kode}</td>
                        <td className="py-2.5 px-4 text-slate-200 font-medium">{t.course?.nama}</td>
                        <td className="py-2.5 px-4 text-slate-400 text-center">{t.course?.sks}</td>
                        <td className="py-2.5 px-4 text-center">
                          <span className={`inline-flex items-center justify-center w-6 h-6 rounded font-semibold text-xs ${['A','A-'].includes(t.grade) ? 'bg-green-500/10 text-green-400' : ['B+','B','B-'].includes(t.grade) ? 'bg-blue-500/10 text-blue-400' : 'bg-red-500/10 text-red-400'}`}>{t.grade}</span>
                        </td>
                        <td className="py-2.5 px-4 text-slate-400 text-center">{t.bobot}</td>
                      </tr>
                    ))}
                  </tbody>
                </table></div>
              )}
            </div>
            {!transcriptLoading && transcriptData.length > 0 && (
              <div className="bg-[#1e293b] p-4 border-t border-[#334155] flex justify-between items-center text-sm">
                <span className="text-slate-400">Total SKS: <strong className="text-white">{transcriptData.reduce((acc, t) => acc + (t.course?.sks || 0), 0)}</strong></span>
                <span className="text-slate-400">IPK Estimasi: <strong className="text-white">{(transcriptData.reduce((acc, t) => acc + (t.bobot * (t.course?.sks || 0)), 0) / Math.max(1, transcriptData.reduce((acc, t) => acc + (t.course?.sks || 0), 0))).toFixed(2)}</strong></span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Risk Student Modal */}
      {riskModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-[#1e293b] rounded-xl border border-[#334155] w-full max-w-3xl max-h-[85vh] flex flex-col shadow-2xl">
            <div className="flex justify-between items-center p-6 border-b border-[#334155]">
              <div>
                <h3 className="text-lg font-bold text-white">Mahasiswa {activeRiskZone}</h3>
                <p className="text-sm text-slate-400 mt-1">Daftar mahasiswa yang memerlukan mitigasi</p>
              </div>
              <button onClick={() => setRiskModalOpen(false)} className="text-slate-400 hover:text-white p-2">
                <X size={20} />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1">
              {riskLoading ? (
                <div className="text-center py-12 text-slate-400 animate-pulse">Memuat data mahasiswa...</div>
              ) : riskStudents.length === 0 ? (
                <div className="text-center py-12 text-slate-500">Tidak ada mahasiswa di zona ini.</div>
              ) : (
                <div className="space-y-3">
                  {riskStudents.map((s, idx) => (
                    <div key={idx} className="flex flex-col md:flex-row justify-between items-start md:items-center p-4 rounded-xl border border-[#334155] bg-[#0f172a] gap-4 md:gap-0 hover:border-slate-500 transition-colors">
                      <div>
                        <h4 className="font-bold text-white uppercase">{s.nama}</h4>
                        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1 text-sm text-slate-400">
                          <span>{s.nim}</span>
                          <span className="hidden md:inline">&bull;</span>
                          <span>{s.prodi}</span>
                          <span className="hidden md:inline">&bull;</span>
                          <span>Smt {s.semester || '?'}</span>
                        </div>
                        <div className="mt-2 inline-flex flex-wrap gap-2 text-xs">
                          <span className="bg-slate-800 text-slate-300 px-2.5 py-1 rounded-md border border-slate-700 flex items-center gap-1.5">
                            <Users size={12} className="text-slate-400" />
                            PA: <strong className="text-slate-200">{s.advisor_name}</strong>
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4 w-full md:w-auto justify-between md:justify-end">
                        <div className="text-right">
                          <span className="block text-2xl font-black text-red-400">{Number(s.ipk || 0).toFixed(2)}</span>
                          <span className="text-[10px] uppercase text-slate-500 font-bold">IPK Terakhir</span>
                        </div>
                        <button 
                          onClick={() => {
                             setRiskModalOpen(false);
                             openTranscript(s);
                          }}
                          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white text-sm font-semibold rounded-lg shadow-lg shadow-blue-900/20 transition-all flex items-center gap-2"
                        >
                          <Activity size={16} /> Open Transkrip
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── Tab: Riwayat Catatan PA ─────────────────────────────────────── */}
      {activeTab === 'Riwayat Catatan PA' && (
        <div className="bg-[#1e293b] rounded-2xl border border-[#334155] p-6 shadow-xl">
          <div className="flex justify-between items-center mb-6 border-b border-[#334155] pb-4">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Bell size={20} className="text-orange-500" />
                Riwayat Catatan ke Penasihat Akademik
              </h2>
              <p className="text-sm text-slate-400 mt-1">Daftar teguran, informasi, dan peringatan yang disiarkan ke PA</p>
            </div>
            <button 
              onClick={() => setShowAdminNoteModal(true)}
              className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition flex flex-row items-center gap-2"
            >
              <Activity size={16} /> Buat Catatan Baru
            </button>
          </div>
          
          <div className="space-y-4">
            {sentAdminNotes.length === 0 ? (
              <div className="text-center py-12 text-slate-500 border border-dashed border-slate-700/50 rounded-xl bg-[#0f172a]/30">Belum ada catatan yang dikirim ke PA.</div>
            ) : (sentAdminNotes.map((note) => (
              <div key={note.id} className="bg-[#0f172a] p-5 rounded-xl border border-[#334155] hover:border-slate-500 transition-colors flex justify-between items-start">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-bold text-white uppercase text-sm">PA Target: {note.advisor_name}</span>
                    <span className={`px-2 py-0.5 text-[10px] font-bold uppercase rounded ${
                        note.status === 'Urgent' ? 'bg-red-500/20 text-red-500' :
                        note.status === 'Warning' ? 'bg-orange-500/20 text-orange-400' :
                        'bg-blue-500/20 text-blue-400'
                      }`}>
                        {note.type} - {note.status}
                    </span>
                    <span className="text-xs text-slate-500 font-medium">{note.date}</span>
                  </div>
                  <p className="text-sm text-slate-300 border-l-2 border-slate-700 pl-3 italic">&quot;{note.notes}&quot;</p>
                </div>
                <button
                  onClick={() => handleDeleteSentNote(note.id)}
                  className="bg-red-500/10 hover:bg-red-500/20 text-red-400 p-2 rounded-lg transition"
                  title="Hapus / Arsipkan"
                >
                  <Trash size={18} />
                </button>
              </div>
            )))}
          </div>
        </div>
      )}

      {/* Admin Note Modal */}
      {showAdminNoteModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0f172a] border border-[#1e293b] rounded-2xl w-full max-w-lg shadow-2xl flex flex-col max-h-[90vh]">
            <div className="p-6 border-b border-[#1e293b] flex justify-between items-center bg-slate-900/50 rounded-t-2xl">
              <div>
                <h3 className="font-bold text-white text-lg">Buat Catatan untuk Penasihat Akademik</h3>
                <p className="text-sm text-slate-400 mt-1">Kirimkan teguran, peringatan, atau info khusus ke Dosen PA.</p>
              </div>
              <button onClick={() => setShowAdminNoteModal(false)} className="text-slate-400 hover:text-white p-2">
                <X size={20} />
              </button>
            </div>
            <div className="p-6 overflow-y-auto">
              <form onSubmit={handleCreateAdminNote} className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-1">Target Dosen PA</label>
                  <select
                    className="w-full bg-[#1e293b] border border-[#334155] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500"
                    value={adminNoteForm.advisor_id}
                    onChange={(e) => setAdminNoteForm({ ...adminNoteForm, advisor_id: e.target.value })}
                    required
                  >
                    {advisorsList.length === 0 ? <option value="">Memuat data PA...</option> : null}
                    {advisorsList.map((adv: any) => (
                      <option key={adv.id} value={adv.id}>
                        {adv.nama}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-1">Tipe Catatan</label>
                    <select
                      className="w-full bg-[#1e293b] border border-[#334155] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500"
                      value={adminNoteForm.type}
                      onChange={(e) => setAdminNoteForm({ ...adminNoteForm, type: e.target.value })}
                    >
                      <option value="Informasi">Informasi</option>
                      <option value="Peringatan">Peringatan</option>
                      <option value="Teguran">Teguran (Urgent)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-1">Level Indikator</label>
                    <select
                      className="w-full bg-[#1e293b] border border-[#334155] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500"
                      value={adminNoteForm.status}
                      onChange={(e) => setAdminNoteForm({ ...adminNoteForm, status: e.target.value })}
                    >
                      <option value="Selesai">Hijau (Info/Selesai)</option>
                      <option value="Warning">Kuning (Warning)</option>
                      <option value="Urgent">Merah (Urgent/Bahaya)</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-1">Isi Pesan/Catatan</label>
                  <textarea
                    required
                    className="w-full bg-[#1e293b] border border-[#334155] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500 resize-none h-32"
                    placeholder="Tuliskan arahan atau teguran untuk Penasihat Akademik terkait..."
                    value={adminNoteForm.notes}
                    onChange={(e) => setAdminNoteForm({ ...adminNoteForm, notes: e.target.value })}
                  />
                </div>
                <button
                  type="submit"
                  disabled={submittingAdminNote}
                  className="w-full py-3 bg-orange-600 hover:bg-orange-500 disabled:bg-orange-600/50 text-white font-bold rounded-xl transition flex justify-center mt-2"
                >
                  {submittingAdminNote ? 'Mengirim...' : 'Kirim Catatan ke PA'}
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Profil Modal */}
      {showProfileModal && (
        <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#1e293b] rounded-2xl w-full max-w-md border border-[#334155] shadow-2xl flex flex-col max-h-[85vh]">
            <div className="p-5 border-b border-[#334155] flex justify-between items-center bg-[#1a2333]/80 shrink-0">
              <h3 className="font-bold text-white">Pengaturan Profil & Akun</h3>
              <button 
                onClick={() => setShowProfileModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>
            
            <form onSubmit={handleUpdateProfile} className="p-6 space-y-4 overflow-y-auto flex-1">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Upload Foto Profil (Opsional)</label>
                <input 
                  type="file" accept="image/*"
                  onChange={e => {
                    const file = e.target.files?.[0];
                    if (file) {
                      const reader = new FileReader();
                      reader.onload = (ev) => setProfileForm({...profileForm, profile_picture: ev.target?.result as string});
                      reader.readAsDataURL(file);
                    }
                  }}
                  className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-4 py-2 text-sm text-white focus:outline-none file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-500/20 file:text-blue-400 hover:file:bg-blue-500/30"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Username Login</label>
                <input 
                  type="text"
                  required
                  value={profileForm.username}
                  onChange={e => setProfileForm({...profileForm, username: e.target.value})}
                  className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-red-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Kata Sandi Baru</label>
                <input 
                  type="password"
                  value={profileForm.password}
                  onChange={e => setProfileForm({...profileForm, password: e.target.value})}
                  placeholder="Isi hanya jika ingin mengganti sandi..."
                  className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-red-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Email Aktif</label>
                <input 
                  type="email"
                  value={profileForm.email}
                  onChange={e => setProfileForm({...profileForm, email: e.target.value})}
                  className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-red-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Nomor WhatsApp (+62)</label>
                <input 
                  type="text"
                  value={profileForm.whatsapp}
                  onChange={e => setProfileForm({...profileForm, whatsapp: e.target.value})}
                  placeholder="+628123456789"
                  className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-green-500"
                />
              </div>

              <div className="pt-4 border-t border-[#334155] flex justify-end gap-3 shrink-0">
                <button type="button" onClick={() => setShowProfileModal(false)} className="px-4 py-2 text-sm font-semibold text-slate-300 hover:text-white transition">Batal</button>
                <button type="submit" disabled={submittingProfile} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white text-sm font-semibold rounded-lg transition disabled:opacity-50">
                  {submittingProfile ? 'Menyimpan...' : 'Simpan Profil'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
