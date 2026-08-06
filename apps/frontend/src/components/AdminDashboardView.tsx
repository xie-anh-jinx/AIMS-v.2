'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  Menu, Users, AlertTriangle, Settings, LogOut, ChevronRight, Activity, Database,
  Bell, Shield, Server, Eye, Search, X, Trash, User, Edit2, RefreshCw, Key
} from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip as RechartsTooltip, Legend } from 'recharts';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

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
  advisor_id?: number;
  advisor_nama?: string;
  latest_record?: {
    ipk: number;
    ips: number;
    sks: number;
    status: string;
  };
}

interface ChartEntry { name: string; value: number; }

interface TranscriptRecord {
  id: number;
  course: { kode: string; nama: string; sks: number };
  semester: number;
  grade: string;
  bobot: number;
}

interface AdminDashboardViewProps {
  allowedRole: 'ADMIN' | 'DEKAN' | 'WD1' | 'KASUBAG_AKADEMIK';
  defaultTitle: string;
  roleBadgeText: string;
  roleBadgeColor?: string;
}

// Status color helpers
const getStatusBadge = (status: string) => {
  switch (status) {
    case 'Aktif':       return 'bg-green-500/10 text-green-400 border-green-500/20';
    case 'Lulus':       return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
    case 'Drop Out':    return 'bg-red-500/10 text-red-400 border-red-500/20';
    case 'Cuti':        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
    case 'Henti Studi': return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
    case 'Keluar':      return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    case 'Non Aktif':   return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
    default:            return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
  }
};

export default function AdminDashboardView({
  allowedRole,
  defaultTitle,
  roleBadgeText,
  roleBadgeColor = 'bg-red-500/10 text-red-400 border-red-500/20'
}: AdminDashboardViewProps) {
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [semesterDist, setSemesterDist] = useState<ChartEntry[]>([]);
  const [angkatanDist, setAngkatanDist] = useState<ChartEntry[]>([]);
  const [statusDist, setStatusDist] = useState<ChartEntry[]>([]);
  const [riskStatusPerProdi, setRiskStatusPerProdi] = useState<any[]>([]);
  const [allStudents, setAllStudents] = useState<StudentRecord[]>([]);
  const [prodis, setProdis] = useState<string[]>([]);
  const [angkatans, setAngkatans] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('Dashboard');

  // Filter state for Data Mahasiswa
  const [filterProdi, setFilterProdi] = useState('');
  const [filterAngkatan, setFilterAngkatan] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterLoading, setFilterLoading] = useState(false);
  const [totalStudents, setTotalStudents] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);

  // Transcript state
  const [transcriptModalOpen, setTranscriptModalOpen] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<StudentRecord | null>(null);
  const [transcriptData, setTranscriptData] = useState<TranscriptRecord[]>([]);
  const [transcriptLoading, setTranscriptLoading] = useState(false);

  // Risk Students Modal State
  const [riskModalOpen, setRiskModalOpen] = useState(false);
  const [activeRiskZone, setActiveRiskZone] = useState<string>('');
  const [riskStudents, setRiskStudents] = useState<any[]>([]);
  const [riskLoading, setRiskLoading] = useState(false);

  const getToken = () => {
    if (typeof document === 'undefined') return '';
    const match = document.cookie.match(/(^| )token=([^;]+)/);
    return match ? match[2] : '';
  };

  const authHeaders = useCallback(() => ({ Authorization: `Bearer ${getToken()}` }), []);

  const [showAdminNoteModal, setShowAdminNoteModal] = useState(false);
  const [adminNoteForm, setAdminNoteForm] = useState({ advisor_id: '', type: 'Peringatan', status: 'Warning', notes: '' });
  const [advisorsList, setAdvisorsList] = useState<any[]>([]);
  const [submittingAdminNote, setSubmittingAdminNote] = useState(false);
  const [sentAdminNotes, setSentAdminNotes] = useState<any[]>([]);

  // Profile Update State
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [profileForm, setProfileForm] = useState({ username: '', password: '', email: '', whatsapp: '', profile_picture: '' });
  const [submittingProfile, setSubmittingProfile] = useState(false);
  const [profilePictureUrl, setProfilePictureUrl] = useState<string | null>(null);
  const [adminName, setAdminName] = useState<string>(defaultTitle);

  // OpenClaw states
  const [evaluating, setEvaluating] = useState(false);
  const [broadcastForm, setBroadcastForm] = useState({ target: 'YELLOW_ZONE', channel: 'WHATSAPP', message: '' });
  const [broadcasting, setBroadcasting] = useState(false);
  const [agentLogs, setAgentLogs] = useState<any[]>([]);
  const [notifLogs, setNotifLogs] = useState<any[]>([]);
  const [activeLogTab, setActiveLogTab] = useState('NOTIF');

  // Agent Config States
  const [agentConfig, setAgentConfig] = useState<any>({ auto_sync: false, interval: 'Tiap 2 Minggu' });
  const [neosiaToken, setNeosiaToken] = useState<string>('');
  const [savingToken, setSavingToken] = useState<boolean>(false);
  const [tokenMasked, setTokenMasked] = useState<string>('');
  const [manualSyncing, setManualSyncing] = useState<boolean>(false);

  // Modals Add/Edit Student
  const [showAddStudentModal, setShowAddStudentModal] = useState(false);
  const [showEditStudentModal, setShowEditStudentModal] = useState(false);
  const [editingStudent, setEditingStudent] = useState<any>(null);
  const [studentForm, setStudentForm] = useState({
    nim: '', nama: '', prodi: '', angkatan: new Date().getFullYear(), semester: 1, email: '', nomor_whatsapp: '', status: 'Aktif', advisor_id: ''
  });

  // Dynamic Tabs by Role
  const showAgentMonitor = allowedRole === 'ADMIN';
  const showSettings = allowedRole !== 'KASUBAG_AKADEMIK';

  const navItems = [
    { id: 'Dashboard', icon: Activity, label: 'Dashboard' },
    ...(showAgentMonitor ? [{ id: 'Agent Monitor', icon: Server, label: 'Agent Monitor' }] : []),
    { id: 'Data Mahasiswa', icon: Users, label: 'Data Mahasiswa' },
    { id: 'Analisis Risiko', icon: AlertTriangle, label: 'Analisis Risiko' },
    { id: 'Riwayat Catatan PA', icon: Bell, label: 'Riwayat Catatan PA' },
    ...(showSettings ? [{ id: 'Pengaturan', icon: Settings, label: 'Pengaturan' }] : []),
  ];

  const fetchDashboard = useCallback(async () => {
    setLoading(true);
    try {
      const headers = authHeaders();
      const [resOv, resSem, resAngk, resStat, resProdi, resAdvisors, resNotes] = await Promise.all([
        fetch(`${API_URL}/admin/overview`, { headers }),
        fetch(`${API_URL}/admin/analytics/semester-distribution`, { headers }),
        fetch(`${API_URL}/admin/analytics/angkatan-distribution`, { headers }),
        fetch(`${API_URL}/admin/analytics/status-distribution`, { headers }),
        fetch(`${API_URL}/admin/analytics/prodi-distribution`, { headers }),
        fetch(`${API_URL}/admin/advisors`, { headers }),
        fetch(`${API_URL}/admin/notes`, { headers }),
      ]);

      if (resOv.ok) setStats(await resOv.json());
      if (resSem.ok) setSemesterDist(await resSem.json());
      if (resAngk.ok) setAngkatanDist(await resAngk.json());
      if (resStat.ok) setStatusDist(await resStat.json());
      if (resProdi.ok) setRiskStatusPerProdi(await resProdi.json());
      if (resAdvisors.ok) setAdvisorsList(await resAdvisors.json());
      if (resNotes.ok) setSentAdminNotes(await resNotes.json());

      const [resP, resA] = await Promise.all([
        fetch(`${API_URL}/admin/prodis`, { headers }),
        fetch(`${API_URL}/admin/angkatans`, { headers }),
      ]);
      if (resP.ok) setProdis(await resP.json());
      if (resA.ok) setAngkatans(await resA.json());
    } catch (e) {
      console.error('Fetch dashboard error:', e);
    } finally {
      setLoading(false);
    }
  }, [authHeaders]);

  const applyFilters = useCallback(async (page = 1) => {
    setFilterLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterProdi) params.append('prodi', filterProdi);
      if (filterAngkatan) params.append('angkatan', filterAngkatan);
      if (filterStatus) params.append('status_filter', filterStatus);
      if (searchQuery) params.append('search', searchQuery);
      params.append('limit', '50');

      const res = await fetch(`${API_URL}/admin/students?${params.toString()}`, { headers: authHeaders() });
      if (res.ok) {
        const data = await res.json();
        setAllStudents(data);
        setTotalStudents(data.length);
        setCurrentPage(page);
      }
    } catch (e) {
      console.error('Filter error:', e);
    } finally {
      setFilterLoading(false);
    }
  }, [filterProdi, filterAngkatan, filterStatus, searchQuery, authHeaders]);

  const fetchAgentLogs = useCallback(async () => {
    try {
      const [resAgent, resNotif, resCfg] = await Promise.all([
        fetch(`${API_URL}/admin/agent/logs`, { headers: authHeaders() }),
        fetch(`${API_URL}/admin/agent/notif-logs`, { headers: authHeaders() }),
        fetch(`${API_URL}/admin/agent/config`, { headers: authHeaders() }),
      ]);
      if (resAgent.ok) setAgentLogs(await resAgent.json());
      if (resNotif.ok) setNotifLogs(await resNotif.json());
      if (resCfg.ok) {
        const cfg = await resCfg.json();
        setAgentConfig(cfg);
        if (cfg.token_masked) setTokenMasked(cfg.token_masked);
      }
    } catch (e) {
      console.error('Fetch logs error:', e);
    }
  }, [authHeaders]);

  useEffect(() => {
    const roleCookie = document.cookie.split('; ').find(row => row.startsWith('role='))?.split('=')[1];
    const nameCookie = document.cookie.split('; ').find(row => row.startsWith('name='))?.split('=')[1];
    if (nameCookie) setAdminName(decodeURIComponent(nameCookie));
    
    if (roleCookie && roleCookie !== allowedRole && roleCookie !== 'ADMIN') {
      router.push('/login');
      return;
    }

    const savedPic = localStorage.getItem('profile_picture');
    if (savedPic) setProfilePictureUrl(savedPic);

    fetchDashboard();
    applyFilters(1);
    if (showAgentMonitor) fetchAgentLogs();
  }, [router, allowedRole, fetchDashboard, applyFilters, fetchAgentLogs, showAgentMonitor]);

  const handleLogout = () => {
    document.cookie = 'token=; path=/; max-age=0';
    document.cookie = 'role=; path=/; max-age=0';
    document.cookie = 'user_id=; path=/; max-age=0';
    router.push('/login');
  };

  const handleOpenTranscript = async (student: StudentRecord) => {
    setSelectedStudent(student);
    setTranscriptModalOpen(true);
    setTranscriptLoading(true);
    try {
      const res = await fetch(`${API_URL}/students/${student.nim}/transcript`, { headers: authHeaders() });
      if (res.ok) setTranscriptData(await res.json());
    } catch (e) {
      console.error('Fetch transcript error:', e);
    } finally {
      setTranscriptLoading(false);
    }
  };

  const openRiskZoneModal = async (zone: string) => {
    setActiveRiskZone(zone);
    setRiskModalOpen(true);
    setRiskLoading(true);
    try {
      const res = await fetch(`${API_URL}/admin/students/by-risk-zone?zone=${zone}`, { headers: authHeaders() });
      if (res.ok) setRiskStudents(await res.json());
    } catch (e) {
      console.error('Fetch risk students error:', e);
    } finally {
      setRiskLoading(false);
    }
  };

  const handleSaveNeosiaToken = async () => {
    if (!neosiaToken || neosiaToken.length < 50) {
      alert('Token NeoSIA tidak valid');
      return;
    }
    setSavingToken(true);
    try {
      const res = await fetch(`${API_URL}/admin/agent/neosia-token`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ token: neosiaToken })
      });
      if (res.ok) {
        alert('Token NeoSIA berhasil disimpan!');
        setNeosiaToken('');
        fetchAgentLogs();
      } else {
        alert('Gagal menyimpan token');
      }
    } catch (e) {
      console.error(e);
      alert('Terjadi kesalahan');
    } finally {
      setSavingToken(false);
    }
  };

  const handleManualSync = async () => {
    setManualSyncing(true);
    try {
      const res = await fetch(`${API_URL}/admin/agent/sync`, { method: 'POST', headers: authHeaders() });
      if (res.ok) {
        alert('Proses pembaruan nilai & transkrip dari NeoSIA sedang berjalan di latar belakang!');
        fetchAgentLogs();
        fetchDashboard();
      } else {
        alert('Gagal memulai sinkronisasi');
      }
    } catch (e) {
      console.error(e);
      alert('Terjadi kesalahan');
    } finally {
      setManualSyncing(false);
    }
  };

  const handleRunEvaluation = async () => {
    setEvaluating(true);
    try {
      const res = await fetch(`${API_URL}/admin/agent/evaluate`, { method: 'POST', headers: authHeaders() });
      if (res.ok) {
        alert('Evaluasi AI Agent berhasil dijalankan!');
        fetchAgentLogs();
        fetchDashboard();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setEvaluating(false);
    }
  };

  const handleSendAdminNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!adminNoteForm.advisor_id || !adminNoteForm.notes) return;
    setSubmittingAdminNote(true);
    try {
      const res = await fetch(`${API_URL}/admin/notes`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({
          advisor_id: parseInt(adminNoteForm.advisor_id),
          type: adminNoteForm.type,
          status: adminNoteForm.status,
          notes: adminNoteForm.notes
        })
      });
      if (res.ok) {
        alert('Catatan berhasil dikirim ke Penasihat Akademik!');
        setShowAdminNoteModal(false);
        setAdminNoteForm({ advisor_id: '', type: 'Peringatan', status: 'Warning', notes: '' });
        fetchDashboard();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setSubmittingAdminNote(false);
    }
  };

  const openProfileModal = async () => {
    try {
      const res = await fetch(`${API_URL}/admin/profile`, { headers: authHeaders() });
      if (res.ok) {
        const data = await res.json();
        setProfileForm({ username: data.username || '', password: '', email: data.email || '', whatsapp: data.whatsapp || '', profile_picture: '' });
        setShowProfileModal(true);
      }
    } catch (e) { console.error(e); }
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingProfile(true);
    try {
      const res = await fetch(`${API_URL}/admin/profile`, {
        method: 'PUT',
        headers: authHeaders(),
        body: JSON.stringify({
          username: profileForm.username,
          password: profileForm.password || undefined,
          email: profileForm.email,
          whatsapp: profileForm.whatsapp,
        })
      });
      if (res.ok) {
        const data = await res.json();
        alert('Profil berhasil diperbarui!');
        setShowProfileModal(false);
        if (data.name) setAdminName(data.name);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setSubmittingProfile(false);
    }
  };

  const handleProfilePictureUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      const token = getToken();
      const res = await fetch(`${API_URL}/admin/profile/picture`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        setProfilePictureUrl(data.profile_picture);
        localStorage.setItem('profile_picture', data.profile_picture);
      }
    } catch (e) { console.error(e); }
  };

  const COLORS_PRODI = ['#ef4444', '#f59e0b', '#10b981'];

  return (
    <div className="flex min-h-screen font-sans bg-[#0b1121] text-slate-300">

      {/* ── Sidebar ── */}
      {mobileMenuOpen && <div className="fixed inset-0 bg-black/50 z-30 md:hidden" onClick={() => setMobileMenuOpen(false)} />}
      <aside className={`w-[260px] bg-[#111827] flex flex-col fixed h-full z-40 border-r border-[#1f2937] transition-transform duration-300 ${mobileMenuOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}`}>
        <div className="p-6 pb-6 border-b border-[#1f2937]/60">
          <div className="flex flex-col items-center justify-center text-center mb-4">
            <div className="w-20 h-20 rounded-xl overflow-hidden bg-gradient-to-tr from-slate-700 to-slate-800 border border-slate-600 mb-3 flex items-center justify-center text-white shadow-lg">
              {profilePictureUrl ? (
                <img src={profilePictureUrl} alt="Profile" className="w-full h-full object-cover" />
              ) : (
                <User size={40} className="text-slate-400" />
              )}
            </div>
            <div>
              <p className="text-[15px] font-bold text-slate-200">{adminName}</p>
              <span className={`text-xs font-semibold mt-1 inline-block px-2.5 py-0.5 rounded-full border ${roleBadgeColor}`}>
                {roleBadgeText}
              </span>
            </div>
          </div>
          {showSettings && (
            <button
              onClick={openProfileModal}
              className="flex items-center justify-center gap-2 w-full py-2 px-3 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-semibold transition"
            >
              <Edit2 size={13} /> Edit Profil &amp; Sandi
            </button>
          )}
        </div>

        <nav className="flex-1 px-4 py-4 space-y-1.5">
          {navItems.map(({ id, icon: Icon, label }) => {
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
          <button onClick={handleLogout} className="w-full flex items-center justify-center gap-3 px-3 py-2.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition">
            <LogOut size={16} /><span className="text-sm font-medium">Keluar</span>
          </button>
        </div>
      </aside>

      {/* ── Main Content ── */}
      <main className="flex-1 md:ml-[260px] min-h-screen flex flex-col">
        {/* Topbar */}
        <header className="h-16 bg-[#111827]/80 backdrop-blur-md border-b border-[#1f2937] sticky top-0 z-30 px-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button onClick={() => setMobileMenuOpen(true)} className="p-2 text-slate-400 hover:text-white md:hidden">
              <Menu size={20} />
            </button>
            <div>
              <h1 className="text-base font-bold text-white flex items-center gap-2">
                <span>Dashboard Pengawasan Akademik (AIMS)</span>
                <span className="text-xs font-normal text-slate-400">| FIB Unhas</span>
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className={`text-xs px-3 py-1 rounded-full font-medium border ${roleBadgeColor}`}>
              {roleBadgeText}
            </span>
          </div>
        </header>

        {/* Content Body */}
        <div className="p-6 flex-1 space-y-6">
          {/* ── TAB 1: DASHBOARD OVERVIEW ── */}
          {activeTab === 'Dashboard' && (
            <>
              {/* Stat Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-[#111827] border border-[#1f2937] p-5 rounded-xl">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs font-medium text-slate-400">Total Mahasiswa</p>
                      <p className="text-2xl font-bold text-white mt-1">{stats?.total_students?.toLocaleString() || 0}</p>
                    </div>
                    <div className="p-3 bg-blue-500/10 text-blue-400 rounded-lg"><Users size={22} /></div>
                  </div>
                  <p className="text-xs text-slate-500 mt-3">{stats?.total_active_students?.toLocaleString() || 0} Mahasiswa Aktif</p>
                </div>

                <div onClick={() => openRiskZoneModal('GREEN_ZONE')} className="bg-[#111827] border border-emerald-500/20 p-5 rounded-xl cursor-pointer hover:border-emerald-500/40 transition">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs font-medium text-slate-400">Zona Aman</p>
                      <p className="text-2xl font-bold text-emerald-400 mt-1">{stats?.safe_students?.toLocaleString() || 0}</p>
                    </div>
                    <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-lg"><Shield size={22} /></div>
                  </div>
                  <p className="text-xs text-slate-500 mt-3">Klik untuk lihat rincian</p>
                </div>

                <div onClick={() => openRiskZoneModal('YELLOW_ZONE')} className="bg-[#111827] border border-amber-500/20 p-5 rounded-xl cursor-pointer hover:border-amber-500/40 transition">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs font-medium text-slate-400">Zona Perhatian</p>
                      <p className="text-2xl font-bold text-amber-400 mt-1">{stats?.warning_students?.toLocaleString() || 0}</p>
                    </div>
                    <div className="p-3 bg-amber-500/10 text-amber-400 rounded-lg"><AlertTriangle size={22} /></div>
                  </div>
                  <p className="text-xs text-slate-500 mt-3">Klik untuk lihat rincian</p>
                </div>

                <div onClick={() => openRiskZoneModal('RED_ZONE')} className="bg-[#111827] border border-red-500/20 p-5 rounded-xl cursor-pointer hover:border-red-500/40 transition">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs font-medium text-slate-400">Zona Risiko Tinggi</p>
                      <p className="text-2xl font-bold text-red-400 mt-1">{stats?.high_risk_students?.toLocaleString() || 0}</p>
                    </div>
                    <div className="p-3 bg-red-500/10 text-red-400 rounded-lg"><AlertTriangle size={22} /></div>
                  </div>
                  <p className="text-xs text-slate-500 mt-3">Klik untuk lihat rincian</p>
                </div>
              </div>

              {/* Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-[#111827] border border-[#1f2937] p-5 rounded-xl">
                  <h3 className="text-sm font-bold text-white mb-4">Distribusi Risiko Per Program Studi</h3>
                  <div className="h-72 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={riskStatusPerProdi} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis dataKey="prodi" stroke="#9ca3af" angle={-35} textAnchor="end" interval={0} tick={{ fontSize: 10 }} />
                        <YAxis stroke="#9ca3af" />
                        <RechartsTooltip contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#fff' }} />
                        <Legend verticalAlign="top" height={36} />
                        <Bar dataKey="merah" name="Risiko Tinggi" fill="#ef4444" stackId="a" />
                        <Bar dataKey="kuning" name="Perhatian" fill="#f59e0b" stackId="a" />
                        <Bar dataKey="hijau" name="Aman" fill="#10b981" stackId="a" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="bg-[#111827] border border-[#1f2937] p-5 rounded-xl">
                  <h3 className="text-sm font-bold text-white mb-4">Distribusi Status Keaktifan Mahasiswa</h3>
                  <div className="h-72 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={statusDist} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={4} dataKey="value">
                          {statusDist.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS_PRODI[index % COLORS_PRODI.length]} />
                          ))}
                        </Pie>
                        <RechartsTooltip contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#fff' }} />
                        <Legend verticalAlign="bottom" height={36} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* ── TAB 2: AGENT MONITOR (Hanya untuk ADMIN) ── */}
          {activeTab === 'Agent Monitor' && showAgentMonitor && (
            <div className="space-y-6">
              {/* Card Token NeoSIA */}
              <div className="bg-[#111827] border border-blue-500/30 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Key size={18} className="text-blue-400" />
                    <h3 className="text-sm font-bold text-white">Konfigurasi Token Akses API NeoSIA</h3>
                  </div>
                  {tokenMasked && (
                    <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-1 rounded-full font-mono">
                      Token Terpasang: {tokenMasked}
                    </span>
                  )}
                </div>
                <div className="flex gap-2">
                  <input
                    type="password"
                    placeholder="Tempelkan Bearer Token NeoSIA terbaru di sini..."
                    value={neosiaToken}
                    onChange={e => setNeosiaToken(e.target.value)}
                    className="flex-1 bg-[#1f2937] border border-slate-700 text-white rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-blue-500 font-mono"
                  />
                  <button onClick={handleSaveNeosiaToken} disabled={savingToken} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold transition">
                    {savingToken ? 'Menyimpan...' : 'Simpan Token'}
                  </button>
                  <button onClick={handleManualSync} disabled={manualSyncing} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold transition flex items-center gap-1.5">
                    <RefreshCw size={13} className={manualSyncing ? "animate-spin" : ""} />
                    {manualSyncing ? 'Proses Sync...' : 'Jalankan Sync NeoSIA Real-Time'}
                  </button>
                </div>
              </div>

              {/* Action Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-[#111827] border border-[#1f2937] p-5 rounded-xl space-y-3">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Server size={18} className="text-blue-400" />
                    Evaluasi Otomatis AI Agent Evaluator
                  </h3>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Jalankan analisis Aturan Akademik (Rule Engine) secara menyeluruh untuk mengevaluasi risiko studi seluruh mahasiswa S1, S2, dan S3.
                  </p>
                  <button onClick={handleRunEvaluation} disabled={evaluating} className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold transition">
                    {evaluating ? 'Sedang Mengevaluasi...' : 'Jalankan Evaluasi AI Agent Now'}
                  </button>
                </div>

                <div className="bg-[#111827] border border-[#1f2937] p-5 rounded-xl space-y-3">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Bell size={18} className="text-amber-400" />
                    Pengirim Peringatan Dini (Engine Notifikasi)
                  </h3>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Kirim notifikasi pesan pengingat ke Dosen PA atau Mahasiswa yang berada di Zona Perhatian / Risiko Tinggi.
                  </p>
                  <button onClick={() => setShowAdminNoteModal(true)} className="w-full py-2.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-semibold transition">
                    + Kirim Catatan Instruktif ke Dosen PA
                  </button>
                </div>
              </div>

              {/* Logs */}
              <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-5 space-y-4">
                <div className="flex justify-between items-center border-b border-[#1f2937] pb-3">
                  <h3 className="text-sm font-bold text-white">Log Aktivitas Engine Notifikasi &amp; AI Agent</h3>
                  <div className="flex gap-2">
                    <button onClick={() => setActiveLogTab('NOTIF')} className={`px-3 py-1 rounded text-xs font-semibold ${activeLogTab === 'NOTIF' ? 'bg-red-500 text-white' : 'bg-[#1f2937] text-slate-400'}`}>
                      Log Notifikasi ({notifLogs.length})
                    </button>
                    <button onClick={() => setActiveLogTab('AGENT')} className={`px-3 py-1 rounded text-xs font-semibold ${activeLogTab === 'AGENT' ? 'bg-red-500 text-white' : 'bg-[#1f2937] text-slate-400'}`}>
                      Log System ({agentLogs.length})
                    </button>
                  </div>
                </div>

                <div className="max-h-60 overflow-y-auto space-y-2 text-xs font-mono">
                  {activeLogTab === 'NOTIF' ? (
                    notifLogs.map(l => (
                      <div key={l.id} className="p-2.5 bg-[#1f2937] rounded-lg border border-slate-700/50 flex justify-between items-center">
                        <div>
                          <span className="text-amber-400 font-bold">[{l.channel}]</span> <span className="text-slate-200">{l.target_name} ({l.target})</span>: {l.message}
                        </div>
                        <span className="text-[10px] text-slate-500">{new Date(l.created_at).toLocaleString('id-ID')}</span>
                      </div>
                    ))
                  ) : (
                    agentLogs.map(l => (
                      <div key={l.id} className="p-2.5 bg-[#1f2937] rounded-lg border border-slate-700/50 flex justify-between items-center">
                        <div>
                          <span className="text-blue-400 font-bold">[{l.event_type}]</span> <span className="text-slate-300">{l.message}</span>
                        </div>
                        <span className="text-[10px] text-slate-500">{new Date(l.created_at).toLocaleString('id-ID')}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ── TAB 3: DATA MAHASISWA ── */}
          {activeTab === 'Data Mahasiswa' && (
            <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-5 space-y-4">
              <div className="flex flex-col md:flex-row gap-3 justify-between items-center">
                <div className="relative w-full md:w-80">
                  <Search size={16} className="absolute left-3 top-3 text-slate-500" />
                  <input
                    type="text"
                    placeholder="Cari NIM atau Nama..."
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    className="w-full bg-[#1f2937] border border-slate-700 text-white rounded-lg pl-9 pr-4 py-2 text-xs focus:outline-none focus:border-red-500"
                  />
                </div>
                <div className="flex flex-wrap gap-2 w-full md:w-auto">
                  <select value={filterProdi} onChange={e => setFilterProdi(e.target.value)} className="bg-[#1f2937] border border-slate-700 text-slate-300 rounded-lg px-3 py-2 text-xs">
                    <option value="">Semua Prodi</option>
                    {prodis.map(p => <option key={p} value={p}>{p}</option>)}
                  </select>
                  <select value={filterAngkatan} onChange={e => setFilterAngkatan(e.target.value)} className="bg-[#1f2937] border border-slate-700 text-slate-300 rounded-lg px-3 py-2 text-xs">
                    <option value="">Semua Angkatan</option>
                    {angkatans.map(a => <option key={a} value={a}>{a}</option>)}
                  </select>
                  <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)} className="bg-[#1f2937] border border-slate-700 text-slate-300 rounded-lg px-3 py-2 text-xs">
                    <option value="">Semua Status</option>
                    <option value="Aktif">Aktif</option>
                    <option value="Cuti">Cuti</option>
                    <option value="Non Aktif">Non Aktif</option>
                  </select>
                  <button onClick={() => applyFilters(1)} className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg text-xs font-semibold transition flex items-center gap-1.5">
                    <RefreshCw size={13} /> Filter
                  </button>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#1f2937] text-slate-300 font-semibold border-b border-[#374151]">
                    <tr>
                      <th className="p-3">NIM / Nama</th>
                      <th className="p-3">Prodi</th>
                      <th className="p-3">Angkatan/Sem</th>
                      <th className="p-3">Dosen PA</th>
                      <th className="p-3">IPK</th>
                      <th className="p-3">Status Risiko</th>
                      <th className="p-3">Aksi</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1f2937]">
                    {allStudents.length === 0 ? (
                      <tr><td colSpan={7} className="text-center p-6 text-slate-500">Tidak ada data ditemukan. Klik "Filter" untuk memuat data.</td></tr>
                    ) : (
                      allStudents.map(s => (
                        <tr key={s.id} className="hover:bg-[#1f2937]/50 transition">
                          <td className="p-3 font-medium text-white">
                            <div>{s.nama}</div>
                            <div className="text-[11px] text-slate-500 font-mono">{s.nim}</div>
                          </td>
                          <td className="p-3 text-slate-300">{s.prodi}</td>
                          <td className="p-3 text-slate-300">{s.angkatan} / Sem {s.semester}</td>
                          <td className="p-3 text-slate-400">{s.advisor_nama || '-'}</td>
                          <td className="p-3 font-bold text-white">{s.latest_record?.ipk?.toFixed(2) || '0.00'}</td>
                          <td className="p-3">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              s.latest_record?.status === 'HIGH_RISK' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                              s.latest_record?.status === 'Warning' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                              'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                            }`}>
                              {s.latest_record?.status || 'Aman'}
                            </span>
                          </td>
                          <td className="p-3">
                            <button onClick={() => handleOpenTranscript(s)} className="p-1.5 bg-blue-600/20 text-blue-400 hover:bg-blue-600/40 rounded transition">
                              <Eye size={14} />
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ── TAB 4: ANALISIS RISIKO ── */}
          {activeTab === 'Analisis Risiko' && (
            <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-6 space-y-6">
              <h3 className="text-base font-bold text-white">Distribusi Mahasiswa Berisiko Per Program Studi</h3>
              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={riskStatusPerProdi} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="prodi" stroke="#9ca3af" angle={-35} textAnchor="end" interval={0} tick={{ fontSize: 10 }} />
                    <YAxis stroke="#9ca3af" />
                    <RechartsTooltip contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#fff' }} />
                    <Legend verticalAlign="top" height={36} />
                    <Bar dataKey="merah" name="Risiko Tinggi (Merah)" fill="#ef4444" stackId="a" />
                    <Bar dataKey="kuning" name="Perhatian (Kuning)" fill="#f59e0b" stackId="a" />
                    <Bar dataKey="hijau" name="Aman (Hijau)" fill="#10b981" stackId="a" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* ── TAB 5: RIWAYAT CATATAN PA ── */}
          {activeTab === 'Riwayat Catatan PA' && (
            <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-6 space-y-4">
              <div className="flex justify-between items-center border-b border-[#1f2937] pb-4">
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <Bell size={18} className="text-amber-400" />
                    Catatan &amp; Instruksi Ke Penasihat Akademik
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">Daftar instruksi dan arahan pembinaan yang disampaikan ke Dosen PA</p>
                </div>
                <button onClick={() => setShowAdminNoteModal(true)} className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg text-xs font-semibold transition">
                  + Buat Catatan Baru
                </button>
              </div>

              <div className="space-y-3">
                {sentAdminNotes.length === 0 ? (
                  <p className="text-xs text-slate-500 italic p-4 text-center">Belum ada catatan yang dikirim.</p>
                ) : (
                  sentAdminNotes.map(n => (
                    <div key={n.id} className="bg-[#1f2937] border border-slate-700/60 p-4 rounded-xl space-y-2">
                      <div className="flex justify-between items-start">
                        <h4 className="text-sm font-bold text-amber-300">{n.notes}</h4>
                        <span className="text-[11px] text-slate-400 font-mono">{new Date(n.created_at).toLocaleString('id-ID')}</span>
                      </div>
                      <div className="text-[11px] text-slate-500 border-t border-slate-700/40 pt-2 flex items-center justify-between">
                        <span>Tujuan Dosen PA: <span className="text-slate-300 font-medium">{n.advisor_name || 'Semua Dosen PA'}</span></span>
                        <span>Jenis: <span className="text-red-400 font-medium">{n.type} ({n.status})</span></span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* ── TAB 6: PENGATURAN (Untuk Admin, Dekan, WD1) ── */}
          {activeTab === 'Pengaturan' && showSettings && (
            <div className="bg-[#111827] border border-[#1f2937] rounded-xl p-6 max-w-2xl space-y-6">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Settings size={18} className="text-red-400" />
                Pengaturan Akun Pengawas Akademik
              </h3>
              <form onSubmit={handleSaveProfile} className="space-y-4 text-xs">
                <div>
                  <label className="block text-slate-300 mb-1 font-medium">Foto Profil</label>
                  <input type="file" accept="image/*" onChange={handleProfilePictureUpload} className="text-slate-400" />
                </div>
                <div>
                  <label className="block text-slate-300 mb-1 font-medium">Username</label>
                  <input type="text" value={profileForm.username} onChange={e => setProfileForm({ ...profileForm, username: e.target.value })} className="w-full bg-[#1f2937] border border-slate-700 rounded-lg px-3 py-2 text-white" />
                </div>
                <div>
                  <label className="block text-slate-300 mb-1 font-medium">Email</label>
                  <input type="email" value={profileForm.email} onChange={e => setProfileForm({ ...profileForm, email: e.target.value })} className="w-full bg-[#1f2937] border border-slate-700 rounded-lg px-3 py-2 text-white" />
                </div>
                <div>
                  <label className="block text-slate-300 mb-1 font-medium">Nomor WhatsApp</label>
                  <input type="text" value={profileForm.whatsapp} onChange={e => setProfileForm({ ...profileForm, whatsapp: e.target.value })} className="w-full bg-[#1f2937] border border-slate-700 rounded-lg px-3 py-2 text-white" />
                </div>
                <div>
                  <label className="block text-slate-300 mb-1 font-medium">Kata Sandi Baru (Kosongkan jika tidak diubah)</label>
                  <input type="password" value={profileForm.password} onChange={e => setProfileForm({ ...profileForm, password: e.target.value })} className="w-full bg-[#1f2937] border border-slate-700 rounded-lg px-3 py-2 text-white" />
                </div>
                <button type="submit" disabled={submittingProfile} className="px-5 py-2.5 bg-red-600 hover:bg-red-500 text-white font-semibold rounded-lg transition">
                  {submittingProfile ? 'Menyimpan...' : 'Simpan Perubahan'}
                </button>
              </form>
            </div>
          )}
        </div>
      </main>

      {/* Modal Transcript Detail */}
      {transcriptModalOpen && selectedStudent && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#111827] border border-[#1f2937] rounded-xl max-w-2xl w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start border-b border-[#1f2937] pb-3">
              <div>
                <h3 className="text-base font-bold text-white">{selectedStudent.nama}</h3>
                <p className="text-xs text-slate-400 font-mono">{selectedStudent.nim} • {selectedStudent.prodi}</p>
              </div>
              <button onClick={() => setTranscriptModalOpen(false)} className="text-slate-400 hover:text-white"><X size={18} /></button>
            </div>

            {transcriptLoading ? (
              <p className="text-center p-6 text-xs text-slate-400">Memuat transkrip dari NeoSIA...</p>
            ) : (
              <div className="max-h-60 overflow-y-auto border border-slate-700 rounded-lg">
                <table className="w-full text-left text-[11px]">
                  <thead className="bg-[#1f2937] text-slate-300">
                    <tr><th className="p-2">Kode</th><th className="p-2">Mata Kuliah</th><th className="p-2">SKS</th><th className="p-2">Nilai</th></tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {transcriptData.map((t, idx) => (
                      <tr key={idx}>
                        <td className="p-2 font-mono text-slate-400">{t.course?.kode}</td>
                        <td className="p-2 text-white">{t.course?.nama}</td>
                        <td className="p-2 text-slate-300">{t.course?.sks}</td>
                        <td className="p-2 font-bold text-amber-300">{t.grade}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modal Admin Note */}
      {showAdminNoteModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#111827] border border-[#1f2937] rounded-xl max-w-lg w-full p-6 space-y-4">
            <div className="flex justify-between items-center border-b border-[#1f2937] pb-3">
              <h3 className="text-sm font-bold text-white">Kirim Catatan Ke Penasihat Akademik</h3>
              <button onClick={() => setShowAdminNoteModal(false)} className="text-slate-400 hover:text-white"><X size={16} /></button>
            </div>
            <form onSubmit={handleSendAdminNote} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 mb-1 font-medium">Pilih Dosen PA</label>
                <select value={adminNoteForm.advisor_id} onChange={e => setAdminNoteForm({ ...adminNoteForm, advisor_id: e.target.value })} required className="w-full bg-[#1f2937] border border-slate-700 text-white rounded-lg px-3 py-2">
                  <option value="">-- Pilih Dosen PA --</option>
                  {advisorsList.map(a => (
                    <option key={a.id} value={a.id}>{a.nama} ({a.prodi || 'FIB'})</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-slate-300 mb-1 font-medium">Instruksi / Catatan</label>
                <textarea required rows={4} placeholder="Tuliskan arahan pembinaan..." value={adminNoteForm.notes} onChange={e => setAdminNoteForm({ ...adminNoteForm, notes: e.target.value })} className="w-full bg-[#1f2937] border border-slate-700 text-white rounded-lg px-3 py-2" />
              </div>
              <button type="submit" disabled={submittingAdminNote} className="w-full py-2.5 bg-red-600 hover:bg-red-500 text-white font-semibold rounded-lg transition">
                {submittingAdminNote ? 'Mengirim...' : 'Kirim Catatan'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Modal Risk Zone Students */}
      {riskModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#111827] border border-[#1f2937] rounded-xl max-w-3xl w-full p-6 space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex justify-between items-center border-b border-[#1f2937] pb-3">
              <h3 className="text-sm font-bold text-white">Daftar Mahasiswa - {activeRiskZone === 'RED_ZONE' ? 'Zona Risiko Tinggi' : activeRiskZone === 'YELLOW_ZONE' ? 'Zona Perhatian' : 'Zona Aman'}</h3>
              <button onClick={() => setRiskModalOpen(false)} className="text-slate-400 hover:text-white"><X size={16} /></button>
            </div>
            {riskLoading ? (
              <p className="text-center p-6 text-xs text-slate-400">Memuat data mahasiswa...</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#1f2937] text-slate-300">
                    <tr><th className="p-2">NIM / Nama</th><th className="p-2">Prodi</th><th className="p-2">Angkatan/Sem</th><th className="p-2">IPK</th></tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {riskStudents.map(s => (
                      <tr key={s.id}>
                        <td className="p-2 text-white font-medium">{s.nama} <div className="text-[10px] text-slate-400">{s.nim}</div></td>
                        <td className="p-2 text-slate-300">{s.prodi}</td>
                        <td className="p-2 text-slate-300">{s.angkatan} / Sem {s.semester}</td>
                        <td className="p-2 font-bold text-amber-300">{s.latest_record?.ipk?.toFixed(2) || '0.00'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
