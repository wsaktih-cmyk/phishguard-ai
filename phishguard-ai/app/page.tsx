"use client";
import { useState } from 'react';

export default function Home() {
  const [inputText, setInputText] = useState('');
  const [status, setStatus] = useState('');

  const periksaLink = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('Sedang memindai...');

    try {
      // Ini adalah momen Frontend ngobrol sama Backend lewat REST API
      const response = await fetch('/api/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText }),
      });
      
      const data = await response.json();
      setStatus(data.message);
    } catch (error) {
      setStatus('Gagal terhubung ke server awan.');
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-2xl bg-white p-8 rounded-xl shadow-lg border border-gray-100">
        <h1 className="text-3xl font-bold text-center text-blue-600 mb-2">PhishGuard AI</h1>
        <p className="text-center text-gray-500 mb-8">Pendeteksi Link & Teks Penipuan Berbasis AI</p>
        
        <form onSubmit={periksaLink} className="flex flex-col gap-4">
          <input
            type="text"
            placeholder="Masukkan link atau teks SMS mencurigakan di sini..."
            className="w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            required
          />
          <button 
            type="submit"
            className="w-full bg-blue-600 text-white font-semibold p-4 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Check Sekarang
          </button>
        </form>

        {status && (
          <div className="mt-6 p-4 bg-gray-100 rounded-lg text-center text-gray-700 font-medium">
            {status}
          </div>
        )}
      </div>
    </main>
  );
}