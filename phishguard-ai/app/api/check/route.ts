import { NextResponse } from 'next/server';
// Nanti kita import koneksi DB di sini

export async function POST(request: Request) {
    try {
        // Menerima paket data (JSON) dari Frontend
        const body = await request.json();
        const { text } = body;

        // --- MATA KULIAH SAINS KOMPUTASI & AI NANTI AKAN DITARUH DI SINI ---
        // Sementara kita buat respons bodong (dummy) dulu sebelum ngoding rumus matematika besok
        
        return NextResponse.json({ 
            message: `Server Backend berhasil menerima teks: "${text}". Tunggu update AI besok bre!` 
        }, { status: 200 });

    } catch (error) {
        return NextResponse.json({ message: "Data gagal diproses server." }, { status: 500 });
    }
}