
---

# 📄 **KONSEP.md — Konsep dan Aturan Kerja Proyek Engine Catur**

### *Dokumen ini menjelaskan tujuan proyek, arsitektur yang diinginkan, serta instruksi untuk AI.*

---

# 🎯 **1. Tujuan Proyek**

Proyek ini bertujuan untuk mengimplementasikan dan membandingkan dua algoritma pencarian langkah dalam engine catur:

1. **Minimax + Alpha-Beta Pruning** (baseline)
2. **Minimax + Alpha-Beta Pruning + Monte Carlo Rollout** (hybrid)

Fokus analisis:

* Efisiensi waktu (average time per move)
* Kualitas keputusan (win-rate & evaluasi posisi)
* Node count (opsional)

Proyek ini bersifat *eksperimental* dan berorientasi pada koding praktik — bukan UI, bukan server besar, dan bukan machine learning berat.

---

# 📦 **2. Stack Teknologi**

Proyek sepenuhnya berbasis Python:

* `python-chess` → representasi papan, legal moves, game state
* `random`, `numpy` → simulasi acak (Monte Carlo)
* `time` → tracking waktu
* `matplotlib` → visualisasi hasil
* **Tidak menggunakan library eksternal lain** kecuali dibutuhkan untuk keperluan testing ringan.

---

# 🧩 **3. Struktur Folder yang Diinginkan**

AI IDE () harus menjaga struktur berikut:

```
/engine-chess
│
├── main.py                      # entry point untuk menjalankan engine
│
├── minimax/
│   ├── minimax_ab.py            # implementasi Minimax + Alpha-Beta
│   ├── evaluator_static.py      # evaluasi statis: nilai material
│   └── evaluator_mc.py          # evaluasi Monte Carlo Rollout
│
├── simulation/
│   ├── auto_vs_stockfish.py     # uji otomatis lawan Stockfish
│   ├── game_runner.py           # handler simulasi N game otomatis
│   └── metrics.py               # helper untuk menghitung waktu, node, winrate
│
├── utils/
│   ├── board_utils.py           # helper fungsi: print board, FEN, dsb
│   └── timer.py                 # wrapper time measurement
│
├── results/
│   ├── logs/                    # riwayat game / PGN
│   ├── charts/                  # grafik hasil
│   └── summary.json             # ringkasan hasil uji
│
└── tests/
    ├── test_minimax.py
    └── test_mc.py
```

 **jangan mengubah nama folder** tanpa instruksi eksplisit.

---

# ⚙️ **4. Aturan Penulisan Kode (Instruction for  AI)**

###  harus mengikuti aturan berikut:

### **(A) Penamaan & Struktur**

* Gunakan snake_case untuk python.
* Setiap file berisi **1 konsep utama** (single responsibility).
* Jangan gabungkan evaluator static + Monte Carlo dalam 1 file.

### **(B) Komentar**

* Tambahkan komentar ringkas pada fungsi utama.
* Jangan komentar berlebihan.

### **(C) Konsistensi Parameter**

Untuk fungsi Minimax:

```python
def minimax(board, depth, alpha, beta, maximizing, use_mc=False, rollout_count=30):
```

 **wajib mempertahankan parameter tersebut**.

### **(D) Monte Carlo Rules**

Monte Carlo evaluator harus mengikuti aturan:

* Simulasi acak maksimal 40 langkah.
* Jika game over → hasil langsung digunakan.
* Rollout default = 30.
* Return nilai float -1 sampai 1.

### **(E) Jangan Pakai Library Berat**

* Dilarang: TensorFlow, PyTorch, Scikit-learn.
* Fokus hanya pada simulasi algoritma, bukan ML.

### **(F) Hindari perubahan besar otomatis**

 **tidak boleh merombak struktur proyek** kecuali diminta.

---

# 🧠 **5. Fungsi-Fungsi Kunci yang Harus Ada**

### **Minimax baseline (minimax_ab.py)**

* `minimax(...)`
* `select_best_move(board, depth=3)`

### **Monte Carlo evaluator (evaluator_mc.py)**

* `simulate_random(board)`
* `evaluate_mc(board, rollout_count)`

### **Simulation Runner (game_runner.py)**

* `run_single_game(engine_func)`
* `run_experiment(n_games)`

### **Metrics (metrics.py)**

* `measure_move_time(func)`
* `calculate_winrate(results)`
* `save_summary_json(results)`

---

# 🧪 **6. Lingkungan Pengujian**

Gunakan environment berikut:

* Python 3.10+
* Depth pengujian = 3
* Rollout Monte Carlo = 10, 30, 50 untuk pembandingan

 harus menghasilkan kode yang berjalan di lingkungan ini.

---

# 📈 **7. Output yang Diharapkan**

Folder `results/` harus memiliki:

* `summary.json`
* grafik `.png` hasil waktu vs akurasi
* file log game (opsional)

 boleh membantu membuat grafik, tapi tidak boleh menambahkan library baru.

---

# 🛑 **8. Hal yang Tidak Boleh Dilakukan **

 **tidak boleh**:

* Menggunakan library deep learning
* Menyusun ulang folder tanpa instruksi
* Mengubah struktur minimax tanpa persetujuan
* Menghasilkan UI besar (web/fullstack)
* Menambahkan dependensi besar

---

# 🚀 **9. Tujuan Akhir Proyek**

Proyek harus menghasilkan:

1. **Engine Catur Minimax + Alpha-Beta yang stabil**
2. **Engine Hybrid Minimax + Monte Carlo yang berfungsi**
3. **Script pengujian otomatis**
4. **Perbandingan performa (waktu vs akurasi)**

---

# ✔️ **Dokumen ini harus dibaca oleh AI pada setiap permulaan tugas.**

Silakan mengikuti seluruh aturan secara konsisten.

---

dia langsung mengikuti pedoman di `KONSEP.md`.

Ingin dibuatkan?
