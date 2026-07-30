'use client';

import {useState, useEffect} from 'react';
import {  Users, AlertTriangle, TrendingDown, ClipboardList, LogOut, ChevronRight, Bell, BarChart2, Edit2, Trash, User , Menu, X } from 'lucide-react';
import {BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell} from 'recharts';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Student {
  id: number;
  nim: string;
  nama: string;
  semester: number;
  prodi: string;
  status: string;
}

interface AcademicRecord {
  student_id: number;
  ips: number;
  ipk: number;
  sks: number;
  status: string;
  semester: number;
}

export default function AdvisorDashboard() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [students, setStudents] = useState<Student[]>([]);
  const [records, setRecords] = useState<{ [nim: string]: AcademicRecord }>({});
  const [consultations, setConsultations] = useState<any[]>([]);
  const [adminNotes, setAdminNotes] = useState<any[]>([]);
  const [showNoteModal, setShowNoteModal] = useState(false);
  const [showTranscriptModal, setShowTranscriptModal] = useState(false);
  const [selectedTranscript, setSelectedTranscript] = useState<any[]>([]);
  const [selectedStudentForTranscript, setSelectedStudentForTranscript] = useState<Student | null>(null);
  const [loadingTranscript, setLoadingTranscript] = useState(false);
  const [noteForm, setNoteForm] = useState({ nim: '', type: 'Konsultasi Akademik', status: 'Selesai', notes: '' });
  const [submittingNote, setSubmittingNote] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all'); // For student list filter
  const [activeNav, setActiveNav] = useState('Mahasiswa Saya'); // For sidebar navigation
  
  // Profile Update State
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [profileForm, setProfileForm] = useState({ username: '', password: '', email: '', whatsapp: '', telegram_username: '', profile_picture: '' });
  const [submittingProfile, setSubmittingProfile] = useState(false);
  const [doStudents, setDoStudents] = useState<Student[]>([]); // Drop Out students
  const [profilePictureUrl, setProfilePictureUrl] = useState<string | null>(null);
  const [advisorName, setAdvisorName] = useState<string>('Dosen PA');
  const [advisorNip, setAdvisorNip] = useState<string>('');

  useEffect(() => {
    const fetchData = async () => {
      const token = document.cookie.match(/(^| )token=([^;]+)/)?.[2] || '';
      try {
        const res = await fetch(`${API_URL}/students/`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const data = await res.json();
        const studs: Student[] = Array.isArray(data) ? data : [];
        setStudents(studs);
        
        // Fetch Drop Out students separately
        const doRes = await fetch(`${API_URL}/students/?include_do=true`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (doRes.ok) {
          const allData: Student[] = await doRes.json();
          setDoStudents(allData.filter(s => s.status === 'Drop Out'));
        }

        const recMap: { [nim: string]: AcademicRecord } = {};
        
        // Chunk sizes untuk mencegah browser ERR_INSUFFICIENT_RESOURCES dan N+1 timeout collapse
        const chunkSize = 10;
        for (let i = 0; i < studs.length; i += chunkSize) {
          const chunk = studs.slice(i, i + chunkSize);
          await Promise.all(
            chunk.map(async s => {
              try {
                const r = await fetch(`${API_URL}/students/${s.nim}/records`, {
                  headers: { Authorization: `Bearer ${token}` }
                });
                if (r.ok) {
                  const recs = await r.json();
                  if (Array.isArray(recs) && recs.length > 0) {
                    recMap[s.nim] = recs[0];
                  }
                }
              } catch (err) {
                console.error(`Fetch record error for ${s.nim}:`, err);
              }
            })
          );
        }
        
        setRecords(recMap);
        
        // Fetch Consultations
        const cRes = await fetch(`${API_URL}/advisor/consultations`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (cRes.ok) {
          const cData = await cRes.json();
          setConsultations(Array.isArray(cData) ? cData : []);
        }

        // Fetch Admin Notes
        const aNotesRes = await fetch(`${API_URL}/advisor/admin-notes`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (aNotesRes.ok) {
          const aData = await aNotesRes.json();
          setAdminNotes(Array.isArray(aData) ? aData : []);
        }

      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    const cachedPic = localStorage.getItem('profile_picture');
    if (cachedPic) setProfilePictureUrl(cachedPic);
    
    const nameMatch = document.cookie.match(/(^| )name=([^;]+)/);
    if(nameMatch) setAdvisorName(decodeURIComponent(nameMatch[2]));
    
    const nimMatch = document.cookie.match(/(^| )nim=([^;]+)/);
    if(nimMatch) setAdvisorNip(decodeURIComponent(nimMatch[2]));
  }, []);

  const openProfileModal = async () => {
    try {
      const token = document.cookie.match(/(^| )token=([^;]+)/)?.[2] || '';
      const res = await fetch(`${API_URL}/advisor/profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setProfileForm({
          username: data.username || '',
          password: '',
          email: data.email || '',
          whatsapp: data.whatsapp || '',
          telegram_username: data.telegram_username || '',
          profile_picture: data.profile_picture || ''
        });
      } else {
        setProfileForm({ username: '', password: '', email: '', whatsapp: '', telegram_username: '', profile_picture: '' });
      }
    } catch (err) {
      console.error(err);
      setProfileForm({ username: '', password: '', email: '', whatsapp: '', telegram_username: '', profile_picture: '' });
    }
    setShowProfileModal(true);
  };

  const hideAdminNote = async (id: number) => {
    if (!confirm('Apakah Anda yakin ingin menyembunyikan pesan ini?')) return;
    try {
      const token = document.cookie.match(/(^| )token=([^;]+)/)?.[2];
      const res = await fetch(`${API_URL}/advisor/admin-notes/${id}/archive`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        setAdminNotes(prev => prev.filter(n => n.id !== id));
      } else {
        alert('Gagal menyembunyikan pesan');
      }
    } catch (e) {
      console.error(e);
    }
  };

  const hideConsultationData = async (id: number) => {
    if (!confirm('Apakah Anda yakin ingin menghapus riwayat konsultasi ini?')) return;
    try {
      const token = document.cookie.match(/(^| )token=([^;]+)/)?.[2];
      const res = await fetch(`${API_URL}/advisor/consultations/${id}/archive`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        setConsultations(prev => prev.filter(c => c.id !== id));
      } else {
        alert('Gagal menghapus log');
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleLogout = () => {
    document.cookie = 'token=; path=/; max-age=0';
    document.cookie = 'role=; path=/; max-age=0';
    window.location.href = '/login';
  };


  // --- Risk classification based on AcademicRecord.status or IPK ---
  const activeStudents = students.filter(s => s.status !== 'Drop Out' && s.status !== 'Lulus' && s.status !== 'Non Aktif');
  const dropOutStudents = students.filter(s => s.status === 'Drop Out');
  const highRisk = activeStudents.filter(s => 
    records[s.nim]?.status === 'HIGH_RISK' || 
    ((records[s.nim]?.ipk ?? 0) > 0 && (records[s.nim]?.ipk ?? 0) < 2.0)
  );
  const warning  = activeStudents.filter(s => 
    (records[s.nim]?.status === 'Warning' || 
    ((records[s.nim]?.ipk ?? 0) >= 2.0 && (records[s.nim]?.ipk ?? 0) < 2.75)) &&
    records[s.nim]?.status !== 'HIGH_RISK' &&
    !((records[s.nim]?.ipk ?? 0) > 0 && (records[s.nim]?.ipk ?? 0) < 2.0)
  );
  const active   = activeStudents.filter(s => s.status === 'Aktif');

  // Chart data excludes DO students
  const chartData = activeStudents.map(s => ({
    name: s.nama.split(' ')[0],
    IPK: records[s.nim]?.ipk || 0,
  }));

  const handleCreateNote = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingNote(true);
    try {
      const token = document.cookie.match(/(^| )token=([^;]+)/)?.[2] || '';
      const res = await fetch(`${API_URL}/advisor/consultations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(noteForm)
      });
      if (res.ok) {
        setShowNoteModal(false);
        setNoteForm({ nim: '', type: 'Konsultasi Akademik', status: 'Selesai', notes: '' });
        // Refresh consultations
        const cRes = await fetch(`${API_URL}/advisor/consultations`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (cRes.ok) {
          const cData = await cRes.json();
          setConsultations(Array.isArray(cData) ? cData : []);
        }
      } else {
        alert("Gagal menyimpan, pastikan NIM valid dan termasuk dalam mahasiswa asuhan Anda.");
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSubmittingNote(false);
    }
  };

  const handleOpenTranscript = async (s: Student) => {
    setSelectedStudentForTranscript(s);
    setShowTranscriptModal(true);
    setLoadingTranscript(true);
    try {
      const token = document.cookie.match(/(^| )token=([^;]+)/)?.[2] || '';
      const res = await fetch(`${API_URL}/students/${s.nim}/transcript`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        setSelectedTranscript(await res.json());
      } else {
        setSelectedTranscript([]);
      }
    } catch (err) {
      console.error(err);
      setSelectedTranscript([]);
    } finally {
      setLoadingTranscript(false);
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingProfile(true);
    try {
      const token = document.cookie.match(/(^| )token=([^;]+)/)?.[2] || '';
      const res = await fetch(`${API_URL}/advisor/profile`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(profileForm)
      });
      if (res.ok) {
        alert("Profil berhasil diperbarui!");
        setShowProfileModal(false);
        if (profileForm.profile_picture) {
           await fetch(`${API_URL}/auth/profile-picture`, {
             method: 'PUT',
             headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
             body: JSON.stringify({ profile_picture: profileForm.profile_picture })
           });
           setProfilePictureUrl(profileForm.profile_picture);
           localStorage.setItem('profile_picture', profileForm.profile_picture);
        }
        if (profileForm.username) {
          document.cookie = `name=${profileForm.username}; path=/; max-age=86400`;
          setAdvisorName(profileForm.username);
        }
      } else {
        const d = await res.json();
        alert(d.detail || "Gagal memperbarui profil.");
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSubmittingProfile(false);
    }
  };

  const filtered = activeTab === 'risk' ? highRisk : activeTab === 'warning' ? warning : students;

  const getRiskColor = (nim: string) => {
    const status = records[nim]?.status;
    if (status === 'HIGH_RISK') return 'border-l-4 border-l-red-500 bg-red-500/5';
    if (status === 'Warning') return 'border-l-4 border-l-yellow-500 bg-yellow-500/5';
    return 'border-l-4 border-l-green-500 bg-green-500/5';
  };

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-10 h-10 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="flex min-h-screen">
      {/* Mobile Overlay */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/60 z-40 md:hidden backdrop-blur-sm" 
          onClick={() => setMobileMenuOpen(false)} 
        />
      )}

      {/* Sidebar */}
      <aside className={`w-[280px] bg-[#111827] flex flex-col fixed h-full z-50 border-r border-[#1f2937] transition-transform duration-300 ${mobileMenuOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}`}>
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
              <p className="text-[15px] font-bold text-slate-200">{advisorName}</p>
              <p className="text-xs text-slate-400 mt-1">{advisorNip || 'NIP Tidak Tersedia'}</p>
              <p className="text-xs text-slate-500 font-medium mt-1">Dosen Penasihat Akademik</p>
            </div>
          </div>
          <button 
            onClick={openProfileModal}
            className="flex items-center justify-center gap-2 w-full py-2 px-3 rounded-lg bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 text-xs font-semibold transition"
          >
            <Edit2 size={12} />
            Pengaturan Profil
          </button>
        </div>

        <nav className="flex-1 space-y-1 px-4">
          {[
            { icon: Users, label: 'Mahasiswa Saya' },
            { icon: AlertTriangle, label: 'Risiko Akademik' },
            { icon: ClipboardList, label: 'Riwayat Konsultasi' },
            { icon: Bell, label: 'Notifikasi' },
          ].map(({ icon: Icon, label }) => {
            const isActive = activeNav === label;
            return (
              <button 
                key={label}
                onClick={() => setActiveNav(label)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition text-left ${isActive ? 'bg-purple-500/10 text-purple-400' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
              >
                <Icon size={18} />
                <span className="text-sm font-medium">{label}</span>
                {isActive && <ChevronRight size={14} className="ml-auto" />}
              </button>
            );
          })}
        </nav>

        <button onClick={handleLogout} className="flex items-center gap-3 px-4 py-3 w-full rounded-xl text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition mt-4 mb-4">
          <LogOut size={18} /><span className="text-sm">Keluar</span>
        </button>
      </aside>

      {/* Main */}
      <main className="flex-1 md:ml-[280px] p-4 md:p-8 overflow-y-auto w-full">
        <div className="max-w-6xl mx-auto">
          <div className="md:hidden flex items-center mb-6"><button onClick={() => setMobileMenuOpen(true)} className="text-slate-300 hover:text-white p-2 -ml-2"><Menu size={24} /></button></div>
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-white">Dashboard <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-400">Penasehat Akademik</span></h1>
            <p className="text-slate-400 text-sm mt-1">{activeNav === 'Mahasiswa Saya' ? 'Pantau perkembangan akademik mahasiswa bimbingan Anda' : `Mode: ${activeNav}`}</p>
          </div>

          {activeNav === 'Mahasiswa Saya' && (
            <div className="space-y-6">
              {/* Stats */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                  { label: 'Total Mahasiswa Aktif', value: activeStudents.length, icon: Users, color: 'purple' },
                  { label: 'Perlu Perhatian', value: warning.length, icon: Bell, color: 'yellow' },
                  { label: 'Risiko Tinggi (IPK<2)', value: highRisk.length, icon: AlertTriangle, color: 'red' },
                  { label: 'Drop Out', value: doStudents.length, icon: AlertTriangle, color: 'gray' },
                ].map(({ label, value, icon: Icon, color }) => (
                  <div key={label} className="glass-panel p-5">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${
                      color === 'purple' ? 'bg-purple-500/20 text-purple-400' :
                      color === 'green' ? 'bg-green-500/20 text-green-400' :
                      color === 'red' ? 'bg-red-500/20 text-red-400' :
                      color === 'gray' ? 'bg-slate-500/20 text-slate-400' :
                      'bg-yellow-500/20 text-yellow-400'}`}>
                      <Icon size={20} />
                    </div>
                    <p className="text-slate-400 text-xs mb-1">{label}</p>
                    <p className="text-3xl font-bold text-white">{value}</p>
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* IPK Bar Chart */}
                <div className="glass-panel p-6">
                  <div className="flex items-center gap-2 mb-5">
                    <BarChart2 size={18} className="text-purple-400" />
                    <h3 className="font-semibold text-white">IPK Per Mahasiswa</h3>
                  </div>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={chartData} barSize={28}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                      <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis domain={[0, 4]} tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                      <Tooltip contentStyle={{ background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }} />
                      <Bar dataKey="IPK" radius={[6,6,0,0]}>
                        {chartData.map((entry, idx) => (
                          <Cell key={idx} fill={entry.IPK < 2 ? '#ef4444' : entry.IPK < 2.75 ? '#eab308' : '#a855f7'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* High Risk Alert */}
                <div className="glass-panel p-6">
                  <h3 className="font-semibold text-white mb-4 flex items-center gap-2"><AlertTriangle size={18} className="text-red-400" />Mahasiswa Risiko Tinggi</h3>
                  <div className="space-y-3">
                    {highRisk.length === 0 ? (
                      <div className="text-center text-slate-500 text-sm py-8">🎉 Tidak ada mahasiswa berisiko tinggi</div>
                    ) : highRisk.map(s => (
                      <div key={s.nim} className="flex items-center justify-between p-3 rounded-xl bg-red-500/10 border border-red-500/20">
                        <div>
                          <p className="text-sm font-medium text-white">{s.nama}</p>
                          <p className="text-xs text-slate-400">{s.nim} · Sem {s.semester}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-bold text-red-400">{records[s.nim]?.ipk?.toFixed(2)}</p>
                          <p className="text-xs text-slate-400">IPK</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Admin Notes Section */}
              {adminNotes.length > 0 && (
                <div className="glass-panel p-6 border-l-4 border-l-orange-500 relative overflow-hidden">
                  <div className="absolute -right-6 -top-6 text-orange-500/10">
                    <AlertTriangle size={120} />
                  </div>
                  <div className="flex items-center gap-3 mb-4 relative z-10">
                    <div className="w-10 h-10 rounded-full bg-orange-500/20 flex items-center justify-center text-orange-400">
                      <Bell size={20} />
                    </div>
                    <div>
                      <h3 className="font-bold text-white text-lg">Catatan dari Administrator</h3>
                      <p className="text-xs text-slate-400">Peringatan dan info sistem untuk Penasihat Akademik</p>
                    </div>
                  </div>
                  <div className="space-y-3 relative z-10">
                    {adminNotes.map((note) => (
                      <div key={note.id} className="bg-slate-900/60 p-4 rounded-xl border border-white/5 flex flex-col md:flex-row justify-between gap-4">
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <span className={`px-2.5 py-1 text-[10px] font-bold uppercase rounded-md tracking-wider ${
                              note.status === 'Urgent' ? 'bg-red-500/20 text-red-500 border border-red-500/30' :
                              note.status === 'Warning' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
                              'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                            }`}>
                              {note.type} - {note.status}
                            </span>
                            <span className="text-xs text-slate-500 font-medium">{note.date}</span>
                          </div>
                          <p className="text-sm text-slate-300 leading-relaxed font-medium">{note.notes}</p>
                        </div>
                        {note.status === 'Selesai' && (
                          <button
                            onClick={() => hideAdminNote(note.id)}
                            className="text-slate-500 hover:text-red-400 p-2 rounded-lg transition self-start"
                            title="Tandai telah dibaca dan hapus"
                          >
                            <Trash size={18} />
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Full Student List */}
              <div className="glass-panel p-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5">
                  <h3 className="font-semibold text-white">Daftar Mahasiswa Bimbingan</h3>
                  <div className="flex flex-wrap gap-2">
                    {[
                      { key: 'all', label: 'Semua' },
                      { key: 'risk', label: 'Risiko' },
                      { key: 'warning', label: 'Warning' },
                    ].map(tab => (
                      <button
                        key={tab.key}
                        onClick={() => setActiveTab(tab.key as any)}
                        className={`px-3 py-1 rounded-lg text-xs font-medium transition ${activeTab === tab.key ? 'bg-purple-500/20 text-purple-400' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
                      >
                        {tab.label}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="space-y-3">
                  {filtered.map(s => (
                    <div key={s.nim} className={`flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl gap-4 ${getRiskColor(s.nim)} transition hover:bg-white/5`}>
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-purple-500 to-pink-500 flex items-center justify-center text-white text-sm font-bold">
                          {s.nama.charAt(0)}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-white">{s.nama}</p>
                          <p className="text-xs text-slate-400">{s.nim} · Semester {s.semester} · {s.prodi}</p>
                        </div>
                      </div>
                      <div className="flex flex-wrap items-center gap-3 sm:gap-4 w-full sm:w-auto justify-between sm:justify-end">
                        <div className="text-right">
                          <p className="text-sm font-bold text-white">{records[s.nim]?.ipk?.toFixed(2) || '-'}</p>
                          <p className="text-xs text-slate-400">IPK</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-bold text-white">{records[s.nim]?.sks || '-'}</p>
                          <p className="text-xs text-slate-400">SKS</p>
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          records[s.nim]?.status === 'HIGH_RISK' ? 'bg-red-500/20 text-red-400' :
                          records[s.nim]?.status === 'Warning' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-green-500/20 text-green-400'}`}>
                          {records[s.nim]?.status || 'N/A'}
                        </span>
                        <button 
                          onClick={() => handleOpenTranscript(s)}
                          className="text-xs bg-purple-500/20 text-purple-400 px-3 py-1 rounded-lg hover:bg-purple-500/30 transition"
                        >
                          Detail
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeNav === 'Risiko Akademik' && (
            <div className="glass-panel p-6">
              <h3 className="font-semibold text-white mb-2">Manajemen Risiko Tinggi</h3>
              <p className="text-sm text-slate-400 mb-6">Daftar mahasiswa bimbingan yang membutuhkan intervensi akademik secepatnya (DO Warning).</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {highRisk.length === 0 ? (
                  <div className="col-span-2 text-center text-slate-500 py-10">Bagus sekali! Seluruh mahasiswa Anda aman.</div>
                ) : highRisk.map(s => (
                  <div key={s.nim} className="p-5 rounded-2xl bg-slate-800/50 border-l-4 border-l-red-500">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-bold text-white">{s.nama}</h4>
                        <p className="text-xs text-slate-400">{s.nim}</p>
                      </div>
                      <span className="text-xl font-black text-red-500">{records[s.nim]?.ipk?.toFixed(2)}</span>
                    </div>
                    <p className="text-xs text-red-400 mb-4 bg-red-500/10 p-2 rounded-lg inline-block">Menunggak 3 SKS Wajib, IPK &lt; 2.00</p>
                    <div className="flex gap-2">
                      <button 
                        onClick={() => {
                          setNoteForm({ nim: s.nim, type: 'Konsultasi Akademik', status: 'Warning', notes: '' });
                          setShowNoteModal(true);
                        }}
                        className="flex-1 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium py-2 rounded-lg transition"
                      >
                        Jadwalkan Panggilan
                      </button>
                      <button 
                        onClick={() => handleOpenTranscript(s)}
                        className="bg-slate-700 hover:bg-slate-600 text-white text-xs font-medium px-4 py-2 rounded-lg transition"
                      >
                        Detail Transkrip
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeNav === 'Riwayat Konsultasi' && (
            <div className="glass-panel p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="font-semibold text-white">Log Konsultasi & Bimbingan KRS</h3>
                  <p className="text-xs text-slate-400">Diselaraskan dengan validasi KRS Online mahasiswa.</p>
                </div>
                <button 
                  onClick={() => setShowNoteModal(true)}
                  className="bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 text-sm font-medium rounded-lg transition"
                >
                  Buat Catatan Baru
                </button>
              </div>

              <div className="space-y-4">
                {consultations.length === 0 ? (
                  <div className="text-center py-10 text-slate-500 text-sm">Belum ada catatan konsultasi. Pilih mahasiswa untuk menjadwalkan.</div>
                ) : consultations.map((log, i) => (
                  <div key={i} className="bg-slate-800/30 p-4 rounded-xl border border-white/5">
                    <div className="flex gap-4 items-start">
                      <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center text-slate-300 font-bold flex-shrink-0">
                        {log.nama.charAt(0)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
                          <div>
                            <p className="text-sm font-semibold text-white">{log.nama}</p>
                            <p className="text-xs text-slate-400">{log.type} · {log.date}</p>
                          </div>
                          <div className="flex gap-2 items-center">
                            <span className={`text-xs font-medium px-3 py-1 rounded-full ${log.status === 'Selesai' ? 'bg-green-500/20 text-green-400' : log.status === 'Warning' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                              {log.status}
                            </span>
                            <button
                              onClick={() => hideConsultationData(log.id)}
                              className="text-slate-500 hover:text-red-400 p-2 rounded-lg transition"
                              title="Hapus riwayat"
                            >
                              <Trash size={16} />
                            </button>
                          </div>
                        </div>
                        {log.notes && (
                          <div className="mt-2 p-3 bg-slate-900/50 rounded-lg border border-white/5">
                            <p className="text-xs text-slate-400 font-medium mb-1">📝 Pesan ke Mahasiswa:</p>
                            <p className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">{log.notes}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeNav === 'Notifikasi' && (
            <div className="glass-panel p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-full bg-orange-500/20 flex items-center justify-center text-orange-400">
                  <Bell size={20} />
                </div>
                <div>
                  <h3 className="font-bold text-white text-lg">Catatan dari Administrator & Prodi</h3>
                  <p className="text-xs text-slate-400">Pesan dan arahan yang ditujukan kepada Anda</p>
                </div>
              </div>

              {adminNotes.length === 0 ? (
                <div className="text-center py-12 text-slate-500 border border-dashed border-slate-700/50 rounded-xl bg-slate-900/20">
                  <Bell size={32} className="mx-auto mb-3 opacity-30" />
                  <p className="text-sm">Tidak ada catatan atau pesan saat ini.</p>
                  <p className="text-xs mt-1">Catatan dari Administrator dan Prodi akan muncul di sini.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {adminNotes.map((note) => (
                    <div key={note.id} className={`p-4 rounded-xl border relative overflow-hidden ${
                      note.status === 'Urgent' ? 'bg-red-500/10 border-red-500/20' :
                      note.status === 'Warning' ? 'bg-orange-500/10 border-orange-500/20' :
                      'bg-blue-500/10 border-blue-500/20'
                    }`}>
                      <div className={`absolute left-0 top-0 h-full w-1 ${
                        note.status === 'Urgent' ? 'bg-red-500' :
                        note.status === 'Warning' ? 'bg-orange-400' :
                        'bg-blue-500'
                      }`} />
                      <div className="pl-2">
                        <div className="flex flex-wrap items-center gap-2 mb-2">
                          <span className={`px-2.5 py-1 text-[10px] font-bold uppercase rounded-md tracking-wider ${
                            note.status === 'Urgent' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                            note.status === 'Warning' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
                            'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                          }`}>
                            {note.type}
                          </span>
                          <span className={`px-2 py-0.5 text-[10px] font-semibold rounded ${
                            note.status === 'Urgent' ? 'bg-red-500/10 text-red-400' :
                            note.status === 'Warning' ? 'bg-orange-500/10 text-orange-400' :
                            'bg-green-500/10 text-green-400'
                          }`}>
                            {note.status === 'Urgent' ? '🔴 Urgent' : note.status === 'Warning' ? '🟡 Warning' : '🟢 Info'}
                          </span>
                          <span className="text-xs text-slate-500 ml-auto">{note.date}</span>
                        </div>
                        <p className="text-sm text-slate-200 leading-relaxed">{note.notes}</p>
                        {note.status === 'Selesai' && (
                          <button
                            onClick={() => hideAdminNote(note.id)}
                            className="mt-3 text-xs text-slate-500 hover:text-red-400 flex items-center gap-1 transition"
                          >
                            <Trash size={12} /> Tandai sudah dibaca
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

        </div>
      </main>

      {/* Modal Buat Catatan Baru */}
      {showNoteModal && (
        <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-800 rounded-2xl w-full max-w-md border border-white/10 overflow-hidden shadow-2xl">
            <div className="p-5 border-b border-white/5 flex justify-between items-center bg-slate-800/80">
              <h3 className="font-bold text-white">Buat Catatan Baru</h3>
              <button onClick={() => setShowNoteModal(false)} className="text-slate-400 hover:text-white">&times;</button>
            </div>
            
            <form onSubmit={handleCreateNote} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Pilih Mahasiswa</label>
                <select 
                  required
                  value={noteForm.nim}
                  onChange={e => setNoteForm({...noteForm, nim: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-purple-500"
                >
                  <option value="" disabled>-- Pilih Mahasiswa Bimbingan --</option>
                  {students.map(s => (
                    <option key={s.nim} value={s.nim}>{s.nim} - {s.nama}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Tipe Konsultasi</label>
                <select 
                  value={noteForm.type}
                  onChange={e => setNoteForm({...noteForm, type: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-purple-500"
                >
                  <option value="KRS & Administrasi">KRS & Administrasi</option>
                  <option value="Konsultasi Akademik">Konsultasi Akademik (Nilai)</option>
                  <option value="Skripsi/Tugas Akhir">Skripsi/Tugas Akhir</option>
                  <option value="Personal/Non-Akademik">Personal/Non-Akademik</option>
                </select>
              </div>
              
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Status Tindak Lanjut</label>
                <select 
                  value={noteForm.status}
                  onChange={e => setNoteForm({...noteForm, status: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-purple-500"
                >
                  <option value="Selesai">Tuntas (Selesai)</option>
                  <option value="On Progress">Butuh Tindak Lanjut (On Progress)</option>
                  <option value="Warning">Warning (Peringatan)</option>
                </select>
              </div>
              
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Catatan & Evaluasi</label>
                <textarea 
                  required
                  rows={4}
                  value={noteForm.notes}
                  onChange={e => setNoteForm({...noteForm, notes: e.target.value})}
                  placeholder="Tuliskan catatan diskusi, solusi, atau peringatan..."
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-purple-500 resize-none"
                />
              </div>
              
              <div className="pt-2 flex justify-end gap-3">
                <button 
                  type="button" 
                  onClick={() => setShowNoteModal(false)}
                  className="px-5 py-2.5 text-sm font-medium text-slate-300 hover:text-white"
                >
                  Batal
                </button>
                <button 
                  type="submit" 
                  disabled={submittingNote}
                  className="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white text-sm font-bold rounded-xl shadow-lg hover:shadow-purple-500/25 transition flex items-center gap-2"
                >
                  {submittingNote ? 'Menyimpan...' : 'Simpan Catatan'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Detail Transkrip */}
      {showTranscriptModal && selectedStudentForTranscript && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#000000_cc] backdrop-blur-sm p-4">
          <div className="bg-[#0f172a] border border-[#334155] rounded-xl w-full max-w-3xl flex flex-col max-h-[90vh] shadow-2xl">
            <div className="flex justify-between items-center p-5 border-b border-[#334155]">
              <div>
                <h3 className="text-lg font-bold text-white">Transkrip Akademik</h3>
                <p className="text-sm text-slate-400">{selectedStudentForTranscript.nama} ({selectedStudentForTranscript.nim}) - {selectedStudentForTranscript.prodi}</p>
              </div>
              <button 
                onClick={() => {
                   setShowTranscriptModal(false);
                   setSelectedTranscript([]);
                   setSelectedStudentForTranscript(null);
                }} 
                className="text-slate-400 hover:text-white transition"
              >
                <X size={24} />
              </button>
            </div>
            
            <div className="p-5 overflow-y-auto flex-1">
              {loadingTranscript ? (
                <div className="py-12 flex justify-center">
                  <div className="w-8 h-8 border-4 border-slate-700 border-t-blue-500 rounded-full animate-spin"></div>
                </div>
              ) : selectedTranscript.length === 0 ? (
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
                    {selectedTranscript.map((t, idx) => (
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
            
            {!loadingTranscript && selectedTranscript.length > 0 && (
              <div className="bg-[#1e293b] p-4 border-t border-[#334155] flex justify-between items-center text-sm">
                <div className="flex flex-col gap-0.5 text-slate-400">
                  <span>Total SKS: <strong className="text-white">{selectedTranscript.reduce((acc, t) => acc + (t.course?.sks || 0), 0)} SKS</strong></span>
                  <span>IPK Estimasi: <strong className="text-white">{(selectedTranscript.reduce((acc, t) => acc + (t.bobot * (t.course?.sks || 0)), 0) / Math.max(1, selectedTranscript.reduce((acc, t) => acc + (t.course?.sks || 0), 0))).toFixed(2)}</strong></span>
                </div>
                <button 
                  onClick={() => {
                    setShowTranscriptModal(false);
                    setNoteForm({ ...noteForm, nim: selectedStudentForTranscript.nim });
                    setShowNoteModal(true);
                  }}
                  className="text-xs font-semibold bg-purple-500/20 text-purple-400 hover:bg-purple-500 hover:text-white transition px-4 py-2.5 rounded-lg border border-purple-500/20"
                >
                  Jadwalkan Konsultasi
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Profil Modal */}
      {showProfileModal && (
        <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-800 rounded-2xl w-full max-w-md border border-white/10 shadow-2xl flex flex-col max-h-[85vh]">
            <div className="p-5 border-b border-white/5 flex justify-between items-center bg-slate-800/80 shrink-0">
              <h3 className="font-bold text-white">Pengaturan Profil Dosen</h3>
              <button 
                onClick={() => setShowProfileModal(false)}
                className="text-slate-400 hover:text-white"
              >
                &times;
              </button>
            </div>
            
            <form onSubmit={handleUpdateProfile} className="p-6 space-y-4 max-h-[70vh] overflow-y-auto">
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
                <label className="block text-xs font-medium text-slate-400 mb-1">Username NIP</label>
                <input 
                  type="text"
                  value={profileForm.username}
                  onChange={e => setProfileForm({...profileForm, username: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-purple-500 disabled:opacity-50"
                  placeholder="Opsional, masukan NIP untuk login..."
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Kata Sandi Baru</label>
                <input 
                  type="password"
                  value={profileForm.password}
                  onChange={e => setProfileForm({...profileForm, password: e.target.value})}
                  placeholder="Isi hanya jika ingin mengganti sandi..."
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Email Aktif</label>
                <input 
                  type="email"
                  value={profileForm.email}
                  onChange={e => setProfileForm({...profileForm, email: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Nomor WhatsApp Aktif (+62)</label>
                <input 
                  type="text"
                  value={profileForm.whatsapp}
                  onChange={e => setProfileForm({...profileForm, whatsapp: e.target.value})}
                  placeholder="+628123456789"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-green-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Username Telegram (Opsional)</label>
                <div className="flex">
                   <div className="bg-slate-900 border border-r-0 border-slate-700 rounded-l-xl px-3 py-3 text-sm text-slate-500">@</div>
                   <input 
                     type="text"
                     value={profileForm.telegram_username}
                     onChange={e => setProfileForm({...profileForm, telegram_username: e.target.value})}
                     placeholder="dosen_fib"
                     className="w-full bg-slate-900 border border-slate-700 rounded-r-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-purple-500"
                   />
                </div>
              </div>

              <div className="pt-4 flex justify-end gap-3 mt-4 border-t border-white/5">
                <button 
                  type="button" 
                  onClick={() => setShowProfileModal(false)}
                  className="px-5 py-2.5 text-sm font-medium text-slate-300 hover:text-white"
                >
                  Batal
                </button>
                <button 
                  type="submit" 
                  disabled={submittingProfile}
                  className="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white text-sm font-bold rounded-xl shadow-lg transition"
                >
                  {submittingProfile ? 'Menyimpan...' : 'Simpan Pembaruan'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
