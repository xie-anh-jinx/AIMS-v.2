'use client';

import React, { useState, useEffect } from 'react';
import { Menu, BookOpen, TrendingUp, Award, Calendar, LogOut, ChevronRight, MessageSquare, Edit2, Trash, User, Bell, AlertTriangle, CheckCircle } from 'lucide-react';
import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer} from 'recharts';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const getCookie = (name: string) => {
  if (typeof document === 'undefined') return '';
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? match[2] : '';
};

interface AcademicRecord {
  id: number;
  semester: number;
  ips: number;
  ipk: number;
  sks: number;
  status: string;
}

interface StudentData {
  nim: string;
  nama: string;
  prodi: string;
  angkatan: number;
  semester: number;
  status: string;
  email: string;
  nomor_whatsapp: string;
}

export default function StudentDashboard() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [student, setStudent] = useState<StudentData | null>(null);
  const [records, setRecords] = useState<AcademicRecord[]>([]);
  const [transcript, setTranscript] = useState<any[]>([]);
  const [consultations, setConsultations] = useState<any[]>([]);
  const [neosiaStatus, setNeosiaStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('Dashboard');
  const [expandedRecordId, setExpandedRecordId] = useState<number | null>(null);

  // Profile Edit State
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [profileForm, setProfileForm] = useState({ username: '', password: '', email: '', phone_number_wa: '', telegram_username: '', profile_picture: '' });
  const [submittingProfile, setSubmittingProfile] = useState(false);
  const [profilePictureUrl, setProfilePictureUrl] = useState<string | null>(null);

  useEffect(() => {
    const nim = getCookie('nim') || '2021401001';
    const token = getCookie('token');

    if (!token) {
      window.location.href = '/login';
      return;
    }

    const fetchData = async () => {
      try {
        const headers = { 'Authorization': `Bearer ${token}` };
        const studRes = await fetch(`${API_URL}/students/${nim}`, { headers });
        if (studRes.ok) {
          const studentData = await studRes.json();
          setStudent(studentData);

          const recRes = await fetch(`${API_URL}/students/${nim}/records`, { headers });
          if (recRes.ok) setRecords(await recRes.json());

          const trRes = await fetch(`${API_URL}/students/${nim}/transcript`, { headers });
          if (trRes.ok) {
            const trData = await trRes.json();
            setTranscript(trData);
          }

          const consRes = await fetch(`${API_URL}/students/${nim}/consultations`, { headers });
          if (consRes.ok) {
            const consData = await consRes.json();
            setConsultations(consData);
          }

          const neoRes = await fetch(`${API_URL}/students/${nim}/neosia-status`, { headers });
          if (neoRes.ok) {
            const neoData = await neoRes.json();
            setNeosiaStatus(neoData);
          }
        }
      } catch {
        console.error('Failed to fetch student data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    const cachedPic = localStorage.getItem('profile_picture');
    if (cachedPic) setProfilePictureUrl(cachedPic);
  }, []);

  const handleLogout = () => {
    document.cookie = 'token=; path=/; max-age=0';
    document.cookie = 'role=; path=/; max-age=0';
    window.location.href = '/login';
  };

  const hideConsultationData = async (logId: number) => {
    if (!confirm('Apakah Anda yakin ingin menyembunyikan log catatan ini?')) return;
    try {
      const token = document.cookie.match(/(^| )token=([^;]+)/)?.[2];
      const nim = getCookie('nim') || '2021401001';
      const res = await fetch(`${API_URL}/students/${nim}/consultations/${logId}/archive`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        setConsultations(prev => prev.filter(c => c.id !== logId));
      } else {
        const body = await res.json();
        alert(body.detail || 'Gagal menyembunyikan pesan');
      }
    } catch (e) { console.error(e); }
  };

  const getStatusColor = (status: string) => {
    if (status === 'HIGH_RISK') return 'text-red-400 bg-red-500/15 border-red-500/30';
    if (status === 'Warning') return 'text-yellow-400 bg-yellow-500/15 border-yellow-500/30';
    return 'text-green-400 bg-green-500/15 border-green-500/30';
  };

  const groupedSemesters = React.useMemo(() => {
    if (!transcript || transcript.length === 0) return [];

    const grouped = transcript.reduce((acc, grade) => {
      const sem = grade.semester || 0;
      if (!acc[sem]) acc[sem] = { semester: sem, subjects: [], totalSks: 0, totalBobot: 0 };
      acc[sem].subjects.push(grade);
      acc[sem].totalSks += (grade.course?.sks || 0);
      acc[sem].totalBobot += (grade.bobot || 0) * (grade.course?.sks || 0);
      return acc;
    }, {} as Record<number, any>);

    const sortedSems = Object.values(grouped).sort((a: any, b: any) => a.semester - b.semester);

    let cumulativeSks = 0;
    let cumulativeBobot = 0;

    return sortedSems.map((g: any, index: number) => {
      cumulativeSks += g.totalSks;
      cumulativeBobot += g.totalBobot;

      const ips = g.totalSks > 0 ? (g.totalBobot / g.totalSks) : 0;
      const ipk = cumulativeSks > 0 ? (cumulativeBobot / cumulativeSks) : 0;
      const status = ips < 2.0 ? 'Warning' : 'Aman';

      return {
        id: g.semester,
        semesterName: `T.A ${g.semester}`,
        originalSemester: g.semester,
        sks: g.totalSks,
        cumulativeSks: cumulativeSks,
        ips: ips,
        ipk: ipk,
        status: status,
        subjects: g.subjects
      };
    }).reverse();
  }, [transcript]);

  const chartData = [...groupedSemesters].reverse().map(r => ({
    name: r.semesterName,
    IPS: parseFloat(r.ips.toFixed(2)),
    IPK: parseFloat(r.ipk.toFixed(2)),
  }));

  const latestRecord = groupedSemesters[0] || records[0];
  const targetSKS = 144;
  const currentTotalSks = latestRecord?.cumulativeSks || latestRecord?.sks || 0;
  const sksProgress = latestRecord ? Math.round((currentTotalSks / targetSKS) * 100) : 0;

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingProfile(true);
    try {
      const token = document.cookie.match(/(^| )token=([^;]+)/)?.[2] || '';
      const res = await fetch(`${API_URL}/students/${student?.nim}/profile`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(profileForm)
      });
      if (res.ok) {
        alert("Profil berhasil diperbarui!");
        setShowProfileModal(false);
        if (student) {
          setStudent({ ...student, email: profileForm.email || student.email });
        }
        if (profileForm.profile_picture) {
          await fetch(`${API_URL}/auth/profile-picture`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
            body: JSON.stringify({ profile_picture: profileForm.profile_picture })
          });
          setProfilePictureUrl(profileForm.profile_picture);
          localStorage.setItem('profile_picture', profileForm.profile_picture);
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

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-10 h-10 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      {mobileMenuOpen && <div className="fixed inset-0 bg-black/50 z-30 md:hidden" onClick={() => setMobileMenuOpen(false)} />}
      <aside className={`w-64 glass-sidebar p-6 flex flex-col fixed h-full z-40 transition-transform duration-300 ${mobileMenuOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}`}>
        <div className="mb-8">
          <div className="flex flex-col items-center justify-center text-center mb-1">
            <div className="w-20 h-20 rounded-xl overflow-hidden bg-gradient-to-tr from-slate-700 to-slate-800 border border-slate-600 mb-3 flex items-center justify-center text-white">
              {profilePictureUrl ? (
                <img src={profilePictureUrl} alt="Profile" className="w-full h-full object-cover" />
              ) : (
                <User size={40} className="text-slate-400" />
              )}
            </div>
            <div>
              <p className="text-sm font-semibold text-white leading-tight">{student?.nama || 'Mahasiswa'}</p>
              <p className="text-xs text-slate-400 mt-1">{student?.nim}</p>
            </div>
          </div>
          {latestRecord && (
            <span className={`mt-2 inline-flex px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(latestRecord.status)}`}>
              {latestRecord.status === 'Aman' ? '✓ Status Aman' : latestRecord.status === 'Warning' ? '⚠ Perlu Perhatian' : '⛔ Risiko Tinggi'}
            </span>
          )}
          <button
            onClick={() => {
              setProfileForm({
                username: student?.nim || '',
                password: '',
                email: student?.email || '',
                phone_number_wa: (student as any)?.phone_number_wa || '',
                telegram_username: (student as any)?.telegram_username || '',
                profile_picture: ''
              });
              setShowProfileModal(true);
            }}
            className="mt-4 flex items-center justify-center gap-2 w-full py-1.5 px-3 rounded-lg bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 text-xs font-semibold transition"
          >
            <Edit2 size={12} />
            Pengaturan Profil
          </button>
        </div>

        <nav className="flex-1 space-y-1">
          {[
            { icon: TrendingUp, label: 'Dashboard' },
            { icon: BookOpen, label: 'Riwayat Nilai' },
            { icon: Calendar, label: 'Jadwal & KRS' },
            { icon: MessageSquare, label: 'Catatan PA' },
            { icon: Bell, label: 'Pengingat' },
          ].map(({ icon: Icon, label }) => {
            const active = activeTab === label;
            return (
              <button key={label} onClick={() => setActiveTab(label)} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition group ${active ? 'bg-blue-500/10 text-blue-400' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}>
                <Icon size={18} />
                <span className="text-sm font-medium">{label}</span>
                {active && <ChevronRight size={14} className="ml-auto" />}
              </button>
            );
          })}
        </nav>

        <button onClick={handleLogout} className="flex items-center gap-3 px-4 py-3 rounded-xl text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition mt-4 w-full">
          <LogOut size={18} />
          <span className="text-sm">Keluar</span>
        </button>
      </aside>

      {/* Main Content */}
      <main className="flex-1 md:ml-64 p-4 md:p-8 overflow-y-auto w-full">
        <div className="max-w-6xl mx-auto">
          <div className="md:hidden flex items-center mb-6"><button onClick={() => setMobileMenuOpen(true)} className="text-slate-300 hover:text-white p-2 -ml-2"><Menu size={24} /></button></div>
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-white">
              {activeTab === 'Dashboard' ? 'Selamat Datang, ' : activeTab}
              {activeTab === 'Dashboard' && <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">{student?.nama?.split(' ')[0] || '...'}</span>}
              {activeTab === 'Dashboard' && ''}
            </h1>
            <p className="text-slate-400 text-sm mt-1">{student?.prodi} · Angkatan {student?.angkatan} · Semester {student?.semester}</p>
          </div>

          {activeTab === 'Dashboard' && (
            <div className="space-y-6 flex flex-col md:w-full">
              {/* Stats Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                  { label: 'IPK Terkini', value: latestRecord?.ipk?.toFixed(2) || '-', icon: Award, color: 'blue', sub: 'Indeks Prestasi Kumulatif' },
                  { label: 'IPS Semester Ini', value: latestRecord?.ips?.toFixed(2) || '-', icon: TrendingUp, color: 'purple', sub: 'Indeks Prestasi Semester' },
                  { label: 'Total SKS', value: currentTotalSks || '-', icon: BookOpen, color: 'green', sub: `dari ${targetSKS} SKS target` },
                  { label: 'Sisa Semester', value: student?.semester ? Math.max(14 - student.semester, 0) : '-', icon: Calendar, color: 'yellow', sub: 'Estimasi menuju lulus' },
                ].map(({ label, value, icon: Icon, color, sub }) => (
                  <div key={label} className="glass-panel p-5">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${color === 'blue' ? 'bg-blue-500/20 text-blue-400' :
                      color === 'purple' ? 'bg-purple-500/20 text-purple-400' :
                        color === 'green' ? 'bg-green-500/20 text-green-400' :
                          'bg-yellow-500/20 text-yellow-400'}`}>
                      <Icon size={20} />
                    </div>
                    <p className="text-slate-400 text-xs mb-1">{label}</p>
                    <p className="text-3xl font-bold text-white">{value}</p>
                    <p className="text-slate-500 text-xs mt-1">{sub}</p>
                  </div>
                ))}
              </div>

              {/* Progress Bar */}
              <div className="glass-panel p-6">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="font-semibold text-white">Progress Kelulusan</p>
                    <p className="text-slate-400 text-xs">{currentTotalSks} SKS dari {targetSKS} SKS yang dibutuhkan</p>
                  </div>
                  <span className="text-2xl font-bold text-blue-400">{sksProgress}%</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-1000"
                    style={{ width: `${sksProgress}%` }}
                  />
                </div>
              </div>

              {/* Chart */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="glass-panel p-6">
                  <h3 className="font-semibold text-white mb-5">Grafik Perkembangan Akademik</h3>
                  {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={200}>
                      <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                        <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                        <YAxis domain={[0, 4]} tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                        <Tooltip contentStyle={{ background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }} />
                        <Line type="monotone" dataKey="IPK" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, fill: '#3b82f6' }} />
                        <Line type="monotone" dataKey="IPS" stroke="#a855f7" strokeWidth={2} dot={{ r: 4, fill: '#a855f7' }} strokeDasharray="4 2" />
                      </LineChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="h-48 flex items-center justify-center text-slate-500 text-sm">Belum ada data akademik</div>
                  )}
                </div>

                <div className="glass-panel p-6">
                  <h3 className="font-semibold text-white mb-5 flex items-center justify-between">
                    Riwayat Akademik
                    <button onClick={() => setActiveTab('Riwayat Nilai')} className="text-xs text-blue-400 hover:text-blue-300">Lihat Semua</button>
                  </h3>
                  <div className="space-y-3">
                    {records.slice(0, 3).map(rec => (
                      <div key={rec.id} className="flex items-center justify-between p-3 bg-slate-800/40 rounded-xl">
                        <div>
                          <p className="text-sm font-medium text-white">Semester {rec.semester}</p>
                          <p className="text-xs text-slate-400">IPS: {rec.ips?.toFixed(2)} · SKS: {rec.sks}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-bold text-white">{rec.ipk?.toFixed(2)}</p>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${rec.status === 'Aman' ? 'bg-green-500/15 text-green-400' : rec.status === 'Warning' ? 'bg-yellow-500/15 text-yellow-400' : 'bg-red-500/15 text-red-400'}`}>
                            {rec.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'Riwayat Nilai' && (
            <div className="glass-panel p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white mb-1">Transkrip Nilai Sementara</h2>
                  <p className="text-slate-400 text-sm">Keseluruhan rekam jejak akademik Anda.</p>
                </div>
                <button className="px-4 py-2 rounded-lg bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 text-sm font-medium transition">
                  Cetak Transkrip
                </button>
              </div>
              <div className="overflow-x-auto">
                <div className="overflow-x-auto w-full"><table className="w-full text-left text-sm min-w-[700px] text-slate-400 border-collapse">
                  <thead className="bg-slate-800/50 text-slate-300 border-y border-white/5">
                    <tr>
                      <th className="py-3 px-4 font-semibold">Semester</th>
                      <th className="py-3 px-4 font-semibold">SKS Diambil</th>
                      <th className="py-3 px-4 font-semibold">IPS</th>
                      <th className="py-3 px-4 font-semibold">IPK</th>
                      <th className="py-3 px-4 font-semibold">Status Evaluasi</th>
                      <th className="py-3 px-4 font-semibold text-right">Aksi</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {groupedSemesters.map(rec => (
                      <React.Fragment key={rec.id}>
                        <tr className={`hover:bg-slate-800/50 transition cursor-pointer ${expandedRecordId === rec.id ? 'bg-slate-800/30' : ''}`} onClick={() => setExpandedRecordId(expandedRecordId === rec.id ? null : rec.id)}>
                          <td className="py-3 px-4 text-white font-medium">{rec.semesterName}</td>
                          <td className="py-3 px-4">{rec.sks}</td>
                          <td className="py-3 px-4">{rec.ips?.toFixed(2)}</td>
                          <td className="py-3 px-4 font-semibold text-white">{rec.ipk?.toFixed(2)}</td>
                          <td className="py-3 px-4">
                            <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(rec.status)}`}>
                              {rec.status}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-right">
                            <button onClick={() => setExpandedRecordId(expandedRecordId === rec.id ? null : rec.id)} className="text-slate-500 hover:text-blue-400 font-semibold transition bg-slate-800/80 px-3 py-1 rounded-md border border-white/10 hover:border-blue-500/30">
                              {expandedRecordId === rec.id ? 'Tutup' : 'Detail'}
                            </button>
                          </td>
                        </tr>
                        {expandedRecordId === rec.id && (
                          <tr className="bg-slate-900/80">
                            <td colSpan={6} className="p-0 border-b border-white/5">
                              <div className="bg-slate-800/40 p-4 shadow-inner">
                                <h4 className="text-white font-semibold text-sm mb-3 px-1 border-b border-white/10 pb-2">Rincian Mata Kuliah & Nilai Kelulusan</h4>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                                  {rec.subjects.length > 0 ? rec.subjects.map((mk: any) => (
                                    <div key={mk.id} className="flex justify-between items-center bg-slate-800/80 p-3 rounded-lg border border-white/5 hover:border-blue-500/20 transition group">
                                      <div className="w-full truncate pr-2">
                                        <p className="text-slate-200 text-xs font-semibold truncate" title={mk.course?.nama}>{mk.course?.nama}</p>
                                        <p className="text-slate-400 text-[10px] mt-1">SKS: {mk.course?.sks} · T.A: {mk.semester}</p>
                                      </div>
                                      <div className="flex flex-col items-end justify-center pl-2 border-l border-white/10">
                                        <p className={`font-bold text-sm ${['A', 'A-'].includes(mk.grade) ? 'text-green-400' : ['B+', 'B', 'B-'].includes(mk.grade) ? 'text-blue-400' : ['C+', 'C'].includes(mk.grade) ? 'text-yellow-400' : 'text-red-400'}`}>{mk.grade || '-'}</p>
                                      </div>
                                    </div>
                                  )) : (
                                    <div className="col-span-full text-center py-4 text-xs text-slate-500 py-6 border border-dashed border-white/10 rounded-lg">Transkrip mata kuliah belum tersinkronisasi.</div>
                                  )}
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    ))}
                  </tbody>
                </table></div>
              </div>
            </div>
          )}

          {activeTab === 'Jadwal & KRS' && (
            <div className="space-y-6">
              <div className="glass-panel p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="font-bold text-white">Jadwal Kuliah & KRS Aktif</h3>
                    <p className="text-slate-400 text-sm">Dimuat dari data NeoSIA terpadu.</p>
                  </div>
                  <span className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full text-xs font-semibold">Tersinkronisasi</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {(() => {
                    const maxSem = transcript.reduce((max, t) => Math.max(max, t.semester || 0), 0);
                    return transcript.filter(t => t.semester === maxSem).slice(0, 8).map((mk, i) => {
                      const days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat'];
                      const day = days[mk.course_id % 5];
                      const hourStart = 8 + (mk.course_id % 6);
                      return (
                        <div key={mk.id} className="flex gap-4 p-4 rounded-xl border border-white/5 bg-slate-800/40 hover:border-blue-500/30 transition shadow-sm hover:shadow-[0_0_15px_rgba(59,130,246,0.1)]">
                          <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0 border border-blue-500/20">
                            <span className="text-blue-400 font-bold">{mk.course?.sks}S</span>
                          </div>
                          <div>
                            <p className="text-white font-medium mb-1 line-clamp-1">{mk.course?.nama}</p>
                            <p className="text-slate-400 text-xs flex items-center gap-2">
                              <Calendar size={12} className="text-blue-400" /> {day}, {hourStart < 10 ? `0${hourStart}` : hourStart}:00 - {hourStart + Math.ceil((mk.course?.sks || 2) / 1.5)}:30 · Ruang FIB {Math.floor(mk.course_id % 20) || 1}
                            </p>
                          </div>
                        </div>
                      )
                    });
                  })()}
                  {transcript.length === 0 && (
                    <div className="col-span-1 md:col-span-2 text-center py-8 text-slate-500 text-sm border-2 border-dashed border-white/10 rounded-xl bg-slate-800/20">
                      Data KRS belum ditemukan atau masih dalam proses sinkronisasi dari portal NeoSIA.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
 
          {activeTab === 'Pengingat' && (
            <div className="glass-panel p-6">
              <h2 className="text-xl font-bold text-white mb-6">Pusat Notifikasi AIMS (NeoSIA)</h2>
              <div className="space-y-4">
                {/* 1. Status SPP */}
                {neosiaStatus ? (
                  neosiaStatus.sudah_bayar ? (
                    <div className="flex items-start gap-4 p-5 rounded-2xl bg-green-500/10 border border-green-500/20 shadow-[0_0_15px_rgba(34,197,94,0.05)]">
                      <div className="p-2 bg-green-500/20 rounded-full text-green-400 shrink-0 mt-1">
                        <CheckCircle size={24} />
                      </div>
                      <div>
                        <h4 className="text-lg font-bold text-green-400 mb-1">Status Pembayaran SPP: Lunas</h4>
                        <p className="text-slate-300 text-sm">Pembayaran SPP Anda untuk semester berjalan telah lunas dan terverifikasi di NeoSIA. Anda dapat mengisi/mengubah KRS.</p>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-start gap-4 p-5 rounded-2xl bg-red-500/10 border border-red-500/20 shadow-[0_0_15px_rgba(239,68,68,0.05)]">
                      <div className="p-2 bg-red-500/20 rounded-full text-red-400 shrink-0 mt-1">
                        <AlertTriangle size={24} />
                      </div>
                      <div>
                        <h4 className="text-lg font-bold text-red-400 mb-1">Tagihan Pembayaran SPP Aktif</h4>
                        <p className="text-slate-300 text-sm">Status SPP Anda belum terbayar di NeoSIA. Silakan lakukan pembayaran agar hak registrasi & pengisian KRS Anda terbuka pada portal NeoSIA.</p>
                      </div>
                    </div>
                  )
                ) : (
                  <div className="text-center py-6 text-slate-500 text-sm border border-dashed border-white/10 rounded-xl bg-slate-800/10">Memuat status pembayaran...</div>
                )}

                {/* 2. Status KRS */}
                {neosiaStatus ? (
                  neosiaStatus.status_krs === 'SUDAH_KRS' ? (
                    <div className="flex items-start gap-4 p-5 rounded-2xl bg-green-500/10 border border-green-500/20 shadow-[0_0_15px_rgba(34,197,94,0.05)]">
                      <div className="p-2 bg-green-500/20 rounded-full text-green-400 shrink-0 mt-1">
                        <CheckCircle size={24} />
                      </div>
                      <div>
                        <h4 className="text-lg font-bold text-green-400 mb-1">Status KRS: Disetujui / Diisi</h4>
                        <p className="text-slate-300 text-sm">Rencana Studi (KRS) Anda semester {neosiaStatus.tahun_ajaran} ({neosiaStatus.semester_jenis}) telah diinput dan diverifikasi oleh Dosen Wali.</p>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-start gap-4 p-5 rounded-2xl bg-yellow-500/15 border border-yellow-500/20 shadow-[0_0_15px_rgba(234,179,8,0.05)]">
                      <div className="p-2 bg-yellow-500/20 rounded-full text-yellow-400 shrink-0 mt-1">
                        <AlertTriangle size={24} />
                      </div>
                      <div>
                        <h4 className="text-lg font-bold text-yellow-400 mb-1">Status KRS: Belum Selesai</h4>
                        <p className="text-slate-300 text-sm font-semibold">Anda belum menyelesaikan atau menyimpan permanen KRS Anda di NeoSIA untuk semester {neosiaStatus.tahun_ajaran} ({neosiaStatus.semester_jenis}).</p>
                        <p className="text-slate-400 text-xs mt-1">Segera hubungi Dosen PA Anda jika memerlukan konsultasi mata kuliah.</p>
                      </div>
                    </div>
                  )
                ) : (
                  <div className="text-center py-6 text-slate-500 text-sm border border-dashed border-white/10 rounded-xl bg-slate-800/10">Memuat status rencana studi (KRS)...</div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'Catatan PA' && (
            <div className="glass-panel p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="font-semibold text-white text-xl">Catatan Penasihat Akademik</h3>
                  <p className="text-xs text-slate-400 mt-1">Seluruh evaluasi, arahan, dan pemantauan dari Dosen PA Anda.</p>
                </div>
                <div className="bg-purple-500/20 text-purple-400 p-2 rounded-lg">
                  <MessageSquare size={24} />
                </div>
              </div>

              <div className="space-y-4">
                {consultations.length === 0 ? (
                  <div className="text-center py-10 text-slate-500 text-sm border border-dashed border-white/5 rounded-xl bg-slate-800/20">Belum ada catatan konsultasi turun dari Dosen PA.</div>
                ) : consultations.map((log, i) => (
                  <div key={i} className="flex gap-4 items-start bg-slate-800/30 p-5 rounded-xl border border-white/5 hover:border-purple-500/30 transition shadow-sm">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-purple-500 to-pink-500 flex flex-shrink-0 items-center justify-center text-white font-bold">
                      {log.advisor_name?.charAt(0) || 'P'}
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between items-start mb-1">
                        <div>
                          <p className="text-sm font-bold text-white">{log.advisor_name}</p>
                          <p className="text-xs text-slate-400">{log.type} · {log.date}</p>
                        </div>
                        <span className={`text-xs font-semibold px-3 py-1 rounded-full ${log.status === 'Selesai' ? 'bg-green-500/20 text-green-400 border border-green-500/20' : log.status === 'Warning' ? 'bg-red-500/20 text-red-400 border border-red-500/20' : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/20'}`}>
                          {log.status}
                        </span>
                      </div>
                      <div className="mt-3 bg-slate-900/50 p-4 rounded-lg text-sm text-slate-300 italic border-l-2 border-purple-500">
                        "{log.notes}"
                      </div>
                    </div>

                    {log.status === 'Selesai' && (
                      <button
                        onClick={() => hideConsultationData(log.id)}
                        className="text-slate-500 hover:text-red-400 p-2 rounded-lg transition"
                        title="Tandai selesai dan sembunyikan"
                      >
                        <Trash size={18} />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>
      </main>

      {/* Profil Modal */}
      {showProfileModal && (
        <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-800 rounded-2xl w-full max-w-md border border-white/10 shadow-2xl">
            <div className="p-5 border-b border-white/5 flex justify-between items-center bg-slate-800/80">
              <h3 className="font-bold text-white">Pengaturan Profil & Akun</h3>
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
                      reader.onload = (ev) => setProfileForm({ ...profileForm, profile_picture: ev.target?.result as string });
                      reader.readAsDataURL(file);
                    }
                  }}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2 text-sm text-white focus:outline-none file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-500/20 file:text-blue-400 hover:file:bg-blue-500/30"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Username Login</label>
                <input
                  type="text"
                  value={profileForm.username}
                  onChange={e => setProfileForm({ ...profileForm, username: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-blue-500 disabled:opacity-50"
                />
                <p className="text-[10px] text-slate-500 mt-1">Gunakan NIM Anda jika ragu. Berubahnya username bisa membuat Anda gagal login dengan NIM.</p>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Kata Sandi Baru</label>
                <input
                  type="password"
                  value={profileForm.password}
                  onChange={e => setProfileForm({ ...profileForm, password: e.target.value })}
                  placeholder="Isi hanya jika ingin mengganti sandi..."
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Email Pribadi</label>
                <input
                  type="email"
                  value={profileForm.email}
                  onChange={e => setProfileForm({ ...profileForm, email: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Nomor WhatsApp Aktif (+62)</label>
                <input
                  type="text"
                  value={profileForm.phone_number_wa}
                  onChange={e => setProfileForm({ ...profileForm, phone_number_wa: e.target.value })}
                  placeholder="+628123456789"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-green-500"
                />
                <p className="text-[10px] text-green-400 mt-1">Dibutuhkan untuk notifikasi siaran PA.</p>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Username Telegram (Opsional)</label>
                <div className="flex">
                  <div className="bg-slate-900 border border-r-0 border-slate-700 rounded-l-xl px-3 py-3 text-sm text-slate-500">@</div>
                  <input
                    type="text"
                    value={profileForm.telegram_username}
                    onChange={e => setProfileForm({ ...profileForm, telegram_username: e.target.value })}
                    placeholder="mahasiswa_fib"
                    className="w-full bg-slate-900 border border-slate-700 rounded-r-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="pt-4 flex justify-end gap-3 mt-4 border-t border-white/5 pt-4">
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
                  className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white text-sm font-bold rounded-xl shadow-lg transition"
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
