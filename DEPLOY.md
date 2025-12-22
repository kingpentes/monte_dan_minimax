# Deploy ke Vercel

## Langkah-langkah Deploy

### 1. Install Vercel CLI (opsional)
```bash
npm install -g vercel
```

### 2. Deploy via Vercel CLI
```bash
vercel
```

### 3. Deploy via Vercel Dashboard
1. Buka [vercel.com](https://vercel.com)
2. Login dengan GitHub/GitLab/Bitbucket
3. Klik "Import Project"
4. Pilih repository ini
5. Vercel akan otomatis mendeteksi konfigurasi dari `vercel.json`
6. Klik "Deploy"

## Catatan Penting

### Stockfish Engine
⚠️ **Penting**: Stockfish engine tidak akan tersedia di Vercel karena keterbatasan environment serverless. 

Aplikasi akan tetap berjalan dengan engine Minimax (Pure & Hybrid mode) yang tidak membutuhkan binary external.

Fitur yang **tersedia**:
- ✅ Minimax Algorithm (Pure mode)
- ✅ Hybrid Algorithm (Minimax + Monte Carlo)
- ✅ Web interface untuk bermain chess
- ✅ Game logging dan history

Fitur yang **tidak tersedia**:
- ❌ Stockfish evaluation
- ❌ Move quality analysis (membutuhkan Stockfish)
- ❌ Stockfish vs Hybrid comparison

### Environment Variables
Tidak ada environment variables yang diperlukan untuk deployment dasar.

### File Size Limits
Vercel memiliki limit 50MB untuk deployment. Project ini sudah dikonfigurasi dengan `.vercelignore` untuk mengecualikan:
- Stockfish binaries
- Game logs
- Cache files
- Large result files

## Alternatif Hosting dengan Stockfish

Jika membutuhkan Stockfish engine, pertimbangkan hosting alternatif:
- **Heroku**: Mendukung apt buildpacks untuk install Stockfish
- **Railway**: Mendukung Docker dengan full Linux environment
- **Fly.io**: Mendukung Docker deployment
- **VPS (DigitalOcean, Linode, dll)**: Full control

## Testing Lokal

Untuk test lokal sebelum deploy:
```bash
# Install dependencies
pip install -r requirements.txt

# Run Flask app
python web/app.py
```

Buka browser ke `http://localhost:5000`

## Troubleshooting

### Import Error
Jika ada import error, pastikan struktur path sudah benar di `api/index.py`

### Static Files Not Loading
Pastikan route untuk `/static/` sudah benar di `vercel.json`

### Timeout Error
Vercel memiliki limit 10 detik untuk serverless functions. Jika timeout:
- Kurangi depth search
- Kurangi rollout count untuk hybrid mode
