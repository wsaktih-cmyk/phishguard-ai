import { NextResponse } from 'next/server';
import { pool } from '@/lib/db'; // Jalur ini akan otomatis nyari folder lib lu

export async function GET() {
    try {
        const query = `
            CREATE TABLE IF NOT EXISTS scan_history (
                id SERIAL PRIMARY KEY,
                input_text TEXT NOT NULL,
                is_phishing BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        `;

        await pool.query(query);

        return NextResponse.json({ message: "Tabel scan_history berhasil dibuat, bre!" }, { status: 200 });
    } catch (error) {
        console.error("Error bikin tabel:", error);
        return NextResponse.json({ error: "Gagal bikin tabel, cek terminal VS Code lu" }, { status: 500 });
    }
}