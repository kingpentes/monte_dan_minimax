# Chess Engine - Web Interface

Aplikasi web interaktif untuk bermain catur melawan AI menggunakan algoritma Minimax dan Hybrid (Minimax + Monte Carlo).

## 🚀 Live Demo

Deploy ke Vercel: [Link akan tersedia setelah deployment]

## 🎮 Fitur

- **Pure Minimax**: Algoritma pencarian dengan Alpha-Beta Pruning
- **Hybrid Mode**: Kombinasi Minimax dengan Monte Carlo evaluation
- **Interactive Board**: Interface drag-and-drop untuk bermain catur
- **Game History**: Lihat riwayat permainan yang telah dimainkan
- **Move Analysis**: Analisis kualitas langkah (jika Stockfish tersedia)

## 📦 Tech Stack

- **Backend**: Python Flask
- **Chess Logic**: python-chess library
- **Frontend**: JavaScript, HTML, CSS
- **Board UI**: chessboard.js
- **Deployment**: Vercel (Serverless)

## 🛠️ Development

### Prerequisites
```bash
Python 3.8+
pip
```

### Installation
```bash
# Clone repository
git clone <repository-url>
cd tubes

# Install dependencies
pip install -r requirements.txt

# Run development server
python web/app.py
```

Aplikasi akan berjalan di `http://localhost:5000`

## 🌐 Deployment ke Vercel

### Quick Deploy dengan Vercel CLI

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Login ke Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

4. Untuk production deployment:
```bash
vercel --prod
```

### Deploy via GitHub

1. Push code ke GitHub repository
2. Login ke [vercel.com](https://vercel.com)
3. Klik "New Project"
4. Import GitHub repository
5. Vercel akan otomatis detect konfigurasi
6. Klik "Deploy"

### Konfigurasi

File konfigurasi sudah disediakan:
- `vercel.json` - Konfigurasi Vercel
- `.vercelignore` - File yang diabaikan saat deployment
- `api/index.py` - Entry point untuk serverless function

### Catatan Deployment

⚠️ **Stockfish Engine**: 
Stockfish tidak tersedia di environment Vercel karena keterbatasan serverless. Aplikasi akan tetap berjalan dengan:
- ✅ Minimax Algorithm
- ✅ Hybrid Algorithm (Minimax + Monte Carlo)
- ❌ Stockfish evaluation (disabled)

## 📁 Struktur Project

```
tubes/
├── api/
│   └── index.py          # Vercel entry point
├── web/
│   ├── app.py           # Flask application
│   ├── static/          # CSS, JS, assets
│   └── templates/       # HTML templates
├── engine-chess/
│   ├── minimax/         # Minimax algorithm
│   ├── simulation/      # Simulation tools
│   └── results/         # Game logs & charts
├── vercel.json          # Vercel config
├── .vercelignore        # Vercel ignore file
├── requirements.txt     # Python dependencies
└── DEPLOY.md           # Deployment guide
```

## 🎯 Cara Bermain

1. Pilih mode algoritma (Pure Minimax / Hybrid)
2. Atur depth dan parameter lainnya
3. Drag-and-drop piece untuk melakukan langkah
4. AI akan otomatis merespon
5. Lihat statistik dan riwayat permainan

## 🔧 Troubleshooting

### Timeout di Vercel
Jika mengalami timeout (>10 detik):
- Kurangi depth search (max 2-3 untuk hybrid)
- Kurangi rollout count
- Gunakan Pure Minimax untuk performa lebih cepat

### Import Errors
Pastikan struktur folder sesuai dan `sys.path` sudah dikonfigurasi dengan benar di `api/index.py`

## 📝 License

Educational project - Tugas Besar Pengantar Kecerdasan Artifisial

## 👥 Team

Kelompok 9 - Kelas PKA C

---

Untuk detail deployment lebih lengkap, lihat [DEPLOY.md](DEPLOY.md)
