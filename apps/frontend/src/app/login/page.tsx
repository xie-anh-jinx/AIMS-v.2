'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { GraduationCap, Eye, EyeOff, LogIn, AlertCircle } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Login gagal');
      }

      const data = await res.json();
      
      // Store token & role in cookies (JS-accessible for simplicity in dev)
      document.cookie = `token=${data.access_token}; path=/; max-age=86400`;
      document.cookie = `role=${data.role}; path=/; max-age=86400`;
      document.cookie = `user_id=${data.user_id}; path=/; max-age=86400`;
      document.cookie = `nim=${username}; path=/; max-age=86400`;
      if (data.name) {
        document.cookie = `name=${encodeURIComponent(data.name)}; path=/; max-age=86400`;
      }
      if (data.prodi_name) {
        document.cookie = `prodi_name=${encodeURIComponent(data.prodi_name)}; path=/; max-age=86400`;
      }
      if (data.profile_picture) {
        localStorage.setItem('profile_picture', data.profile_picture);
      } else {
        localStorage.removeItem('profile_picture');
      }

      if (data.role === 'STUDENT') {
        router.push('/student');
      } else if (data.role === 'ADVISOR') {
        router.push('/advisor');
      } else if (data.role === 'ADMIN') {
        router.push('/admin');
      } else if (data.role === 'PRODI') {
        router.push('/prodi');
      } else {
        setError('Akun ini tidak memiliki akses ke portal ini.');
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Terjadi kesalahan');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      {/* Animated BG blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{animationDelay:'1s'}} />
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Logo Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-500 to-purple-600 shadow-lg shadow-blue-500/30 mb-4">
            <GraduationCap size={32} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">AIMS Portal</h1>
          <p className="text-slate-400 mt-1 text-sm">Academic Intelligence Management System</p>
        </div>

        {/* Card */}
        <div className="glass-panel p-8">
          <h2 className="text-xl font-semibold mb-6 text-white">Masuk ke Akun Anda</h2>

          {error && (
            <div className="flex items-center gap-2 p-3 mb-5 rounded-lg bg-red-500/15 border border-red-500/30 text-red-400 text-sm">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label className="block text-sm text-slate-400 mb-2">Username / NIM</label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
                placeholder="Masukkan NIM atau username..."
                className="w-full px-4 py-3 rounded-xl bg-slate-800/60 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
              />
            </div>

            <div>
              <label className="block text-sm text-slate-400 mb-2">Password</label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  placeholder="Masukkan password..."
                  className="w-full px-4 py-3 rounded-xl bg-slate-800/60 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition pr-12"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <button
              id="login-btn"
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-semibold flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-500/20 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <LogIn size={18} />
                  Masuk
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-5 border-t border-white/10">
            <p className="text-xs text-slate-400 text-center mb-2">Akun Demo FIB:</p>
            <div className="grid grid-cols-2 gap-2 text-xs text-slate-300">
              <div className="bg-slate-800/60 rounded-lg p-2 text-center border border-white/5">
                <p className="font-semibold text-blue-400 mb-1">Mahasiswa</p>
                <p>NIM: F081231020</p>
              </div>
              <div className="bg-slate-800/60 rounded-lg p-2 text-center border border-white/5">
                <p className="font-semibold text-purple-400 mb-1">Dosen PA</p>
                <p>User: PA_FRN1</p>
              </div>
            </div>
            <p className="text-xs text-slate-500 text-center mt-3">Password: <span className="text-slate-300 font-mono">password123</span></p>
          </div>
        </div>
      </div>
    </div>
  );
}
