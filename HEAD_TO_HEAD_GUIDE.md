# 🎮 Head-to-Head Mode - Panduan Singkat

## Apa itu Head-to-Head Mode?

Mode **Head-to-Head** adalah fitur alternatif untuk membandingkan algoritma tanpa membutuhkan Stockfish. Dalam mode ini, dua algoritma AI akan bertanding otomatis hingga selesai.

## 🎯 Kenapa Perlu Head-to-Head?

- ✅ **Tidak butuh Stockfish** - Bisa jalan di Vercel/serverless
- ✅ **Otomatis dimainkan** - AI vs AI tanpa interaksi manual
- ✅ **Perbandingan algoritma** - Test Pure Minimax vs Hybrid
- ✅ **Statistik lengkap** - Lihat performa, waktu, dan hasil

## 🚀 Cara Menggunakan

### 1. Pilih Mode Head-to-Head

Di web interface:
1. Buka aplikasi di browser
2. Pilih **"Mode Permainan"** → **"Head-to-Head (AI vs AI)"**
3. Konfigurasi akan berubah otomatis

### 2. Konfigurasi Pemain

**Pemain Putih:**
- Algoritma: Minimax / Hybrid
- Depth: 1-5 (rekomendasi: 2-3)
- Rollout Count: 5-50 (jika Hybrid)

**Pemain Hitam:**
- Algoritma: Minimax / Hybrid
- Depth: 1-5 (rekomendasi: 2-3)
- Rollout Count: 5-50 (jika Hybrid)

### 3. Mulai Pertandingan

1. Klik tombol **"🎮 Mulai Head-to-Head"**
2. AI akan otomatis bermain hingga selesai
3. Tunggu hasil (bisa 30 detik - 2 menit tergantung konfigurasi)

### 4. Lihat Hasil

Setelah selesai, Anda akan melihat:
- **Pemenang**: Putih / Hitam / Seri
- **Total langkah**: Berapa langkah dimainkan
- **Waktu rata-rata**: Per pemain
- **Waktu total**: Total waktu bermain
- **Terminasi**: Checkmate, stalemate, dll.

## 📊 Contoh Konfigurasi

### Test 1: Pure vs Hybrid
```
Putih: Pure Minimax (depth=3)
Hitam: Hybrid (depth=2, rollout=10)
```
**Tujuan:** Bandingkan kecepatan vs akurasi

### Test 2: Hybrid dengan Rollout Berbeda
```
Putih: Hybrid (depth=2, rollout=5)
Hitam: Hybrid (depth=2, rollout=20)
```
**Tujuan:** Test pengaruh rollout count

### Test 3: Depth Berbeda
```
Putih: Pure Minimax (depth=2)
Hitam: Pure Minimax (depth=4)
```
**Tujuan:** Test pengaruh depth

## ⚡ Tips Optimasi

### Untuk Testing Cepat:
- Depth: 2
- Rollout: 10
- Waktu: ~30-60 detik

### Untuk Hasil Lebih Akurat:
- Depth: 3
- Rollout: 20
- Waktu: ~1-2 menit

### Hindari Timeout (Vercel):
- Max Depth: 3
- Max Rollout: 30
- Jangan depth=5 + rollout=50 (terlalu lama!)

## 🔍 API Endpoint

### Auto-Play Endpoint
```
POST /h2h/auto_play
Content-Type: application/json

{
  "white_mode": "hybrid",
  "white_depth": 3,
  "white_rollout": 10,
  "black_mode": "minimax",
  "black_depth": 3,
  "black_rollout": 10
}
```

### Response
```json
{
  "success": true,
  "result": {
    "winner": "white",
    "total_moves": 45,
    "termination": "CHECKMATE",
    "white": {
      "mode": "hybrid",
      "depth": 3,
      "avg_time": 0.8,
      "total_time": 18.5
    },
    "black": {
      "mode": "minimax",
      "depth": 3,
      "avg_time": 0.3,
      "total_time": 6.2
    }
  }
}
```

## 📝 Game Logging

Setiap pertandingan H2H otomatis disimpan di:
```
engine-chess/results/logs/game_YYYYMMDD_HHMMSS_id.json
```

Format log:
```json
{
  "game_id": "abc123",
  "timestamp": "2025-12-22T19:00:00",
  "game_type": "head_to_head",
  "white_algorithm": "hybrid (depth=3)",
  "black_algorithm": "minimax (depth=3)",
  "result": { ... },
  "moves": [ ... ]
}
```

## 🎯 Use Cases

### 1. Tugas/Presentasi
- Demo perbandingan algoritma
- Tidak perlu Stockfish
- Bisa di-deploy online (Vercel)

### 2. Testing & Debugging
- Test perubahan algoritma
- Bandingkan konfigurasi
- Cek performa

### 3. Research
- Kumpulkan statistik
- Analisis move quality
- Bandingkan strategi

## ❓ Troubleshooting

### Timeout Error
**Problem:** Request timeout setelah 10 detik
**Solusi:**
- Kurangi depth (max 2-3)
- Kurangi rollout (max 20)
- Gunakan Pure Minimax (lebih cepat)

### No Move Found
**Problem:** AI tidak bisa membuat langkah
**Solusi:**
- Bug di algoritma, check logs
- Posisi invalid, reset board

### Game Terlalu Lama
**Problem:** Game tidak selesai-selesai
**Solusi:**
- Normal untuk posisi balance
- Max moves limit: 200
- Akan otomatis draw setelah 200 langkah

## 🔗 Related Files

- **Backend:** `web/app.py` (line 269-481)
- **Frontend:** `web/static/js/script.js` (line 900+)
- **HTML:** `web/templates/index.html` (h2hConfig section)
- **CSS:** `web/static/css/style.css` (.h2h-players)

## 🎊 Kesimpulan

Head-to-Head mode adalah **solusi sempurna** untuk:
- ✅ Deploy tanpa Stockfish
- ✅ Perbandingan algoritma otomatis
- ✅ Testing dan presentasi
- ✅ Tidak ada human interaction needed

**Cocok banget untuk Tugas Besar dan Deployment Vercel!** 🚀

---

*Dibuat untuk Tugas Besar Pengantar Kecerdasan Artifisial*
*Kelompok 9 - Kelas PKA C*
