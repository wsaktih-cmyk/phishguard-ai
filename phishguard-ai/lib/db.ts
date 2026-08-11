import { Pool } from 'pg';

export const pool = new Pool({
    // Ubah DATABASE_URL jadi POSTGRES_URL sesuai isi baris ke-15 di .env.local lu
    connectionString: process.env.POSTGRES_URL, 
    ssl: {
        rejectUnauthorized: false
    }
});