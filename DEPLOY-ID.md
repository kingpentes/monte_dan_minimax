# 🚀 Panduan Deploy ke Vercel (Bahasa Indonesia)

## ✅ Persiapan Sudah Selesai!

File-file berikut sudah dibuat dan dikonfigurasi:
- ✅ `vercel.json` - Konfigurasi deployment Vercel
- ✅ `.vercelignore` - File yang diabaikan saat deploy
- ✅ `api/index.py` - Entry point untuk serverless function
- ✅ `.gitignore` - File yang diabaikan Git
- ✅ `requirements.txt` - Dependencies Python

## 📋 Langkah-Langkah Deploy

### Metode 1: Deploy via Vercel Dashboard (Paling Mudah) ⭐

1. **Push kode ke GitHub**
   ```bash
   git add .
   git commit -m "Siap deploy ke Vercel"
   git push origin main
   ```
   *Catatan: Ganti `main` dengan nama branch Anda (bisa juga `master`)*

2. **Login ke Vercel**
   - Buka https://vercel.com
   - Klik tombol "Sign Up" atau "Login"
   - Login dengan GitHub account Anda

3. **Import Project**
   - Klik tombol "Add New..." → "Project"
   - Pilih repository `tubes` dari list
   - Klik "Import"

4. **Configure & Deploy**
   - Vercel akan otomatis detect konfigurasi dari `vercel.json`
   - **Root Directory**: biarkan default (root)
   - **Framework Preset**: Other
   - Klik "Deploy"

5. **Tunggu Build Selesai**
   - Proses build akan memakan waktu 1-2 menit
   - Setelah selesai, Anda akan mendapat URL deployment

### Metode 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login ke Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   # Test deployment
   vercel
   
   # Production deployment
   vercel --prod
   ```

## 🎯 Setelah Deploy

### Testing Aplikasi

1. Buka URL yang diberikan Vercel (contoh: `https://tubes-username.vercel.app`)
2. Pastikan:
   - ✅ Halaman web loading dengan benar
   - ✅ Board catur tampil
   - ✅ Bisa drag-and-drop pieces
   - ✅ AI merespon langkah Anda

### Fitur yang Tersedia

✅ **Berjalan di Vercel:**
- Pure Minimax Algorithm
- Hybrid Algorithm (Minimax + Monte Carlo)
- Web interface untuk bermain catur
- Game logging dan history
- Responsive design

❌ **Tidak Tersedia di Vercel:**
- Stockfish evaluation (butuh binary external)
- Move quality analysis dengan Stockfish
- Stockfish comparison mode

*Catatan: Ini normal karena Vercel adalah platform serverless yang tidak mendukung binary external seperti Stockfish.*

## 🔧 Troubleshooting

### Problem: Build Failed

**Solusi:**
1. Cek logs di Vercel dashboard
2. Pastikan `requirements.txt` tidak ada typo
3. Coba deploy ulang dengan `vercel --prod --force`

### Problem: Timeout Error (504)

**Solusi:**
1. Kurangi depth search (max 2-3)
2. Kurangi rollout count untuk hybrid mode
3. Gunakan Pure Minimax untuk performa lebih cepat

### Problem: Static Files Not Loading

**Solusi:**
1. Pastikan struktur folder `web/static/` sudah benar
2. Cek `vercel.json` untuk route `/static/`
3. Clear cache browser (Ctrl+Shift+R)

### Problem: Import Error

**Solusi:**
1. Pastikan semua dependencies ada di `requirements.txt`
2. Cek path di `api/index.py`
3. Deploy ulang

## 🔄 Update Aplikasi

Setelah melakukan perubahan:

```bash
# Commit changes
git add .
git commit -m "Update fitur xyz"
git push origin main
```

Vercel akan otomatis build dan deploy versi terbaru!

## 📊 Monitoring

- **Dashboard**: https://vercel.com/dashboard
- **Logs**: Klik project → "Logs" tab
- **Analytics**: Klik project → "Analytics" tab

## 💡 Tips

1. **Domain Custom**: Bisa tambahkan domain custom di Vercel dashboard
2. **Environment Variables**: Bisa set di Project Settings → Environment Variables
3. **Preview Deployments**: Setiap push ke branch akan otomatis dapat preview URL
4. **Rollback**: Bisa rollback ke deployment sebelumnya kapan saja

## 📞 Butuh Bantuan?

1. Cek dokumentasi Vercel: https://vercel.com/docs
2. Cek logs deployment untuk error messages
3. Review file `DEPLOY.md` untuk informasi teknis lebih detail

---

## ✨ Next Steps

Setelah berhasil deploy:

1. ✅ Test aplikasi secara menyeluruh
2. ✅ Share URL ke teman/dosen
3. ✅ Update README dengan link deployment
4. ✅ Screenshot untuk laporan/presentasi

**Selamat! Aplikasi Anda sudah live di internet! 🎉**
