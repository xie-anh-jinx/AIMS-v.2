'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { GraduationCap } from 'lucide-react';

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    const role = document.cookie.match(/(^| )role=([^;]+)/)?.[2];
    const token = document.cookie.match(/(^| )token=([^;]+)/)?.[2];
    if (!token) { router.push('/login'); return; }
    if (role === 'STUDENT') router.push('/student');
    else if (role === 'ADVISOR') router.push('/advisor');
    else router.push('/login');
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-500 to-purple-600 mb-4 animate-pulse">
          <GraduationCap size={32} className="text-white" />
        </div>
        <p className="text-slate-400 text-sm">Mengarahkan...</p>
      </div>
    </div>
  );
}
