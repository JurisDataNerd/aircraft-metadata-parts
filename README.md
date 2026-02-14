
# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

# Aircraft Configuration Intelligence Platform

Integrated Scope: Phase 1 – Phase 3
Versi 1.0 (Unified Specification)

---

# 1. PENDAHULUAN

## 1.1 Latar Belakang

Konfigurasi aircraft dikontrol oleh berbagai dokumen teknis berbeda, termasuk:

* **Illustrated Parts Data (IPD)** berbasis tabel part dan effectivity line
* **Engineering Placard / Marking Drawing** berbasis drawing dengan item dan approval authority

Karakteristik masalah:

* Format dokumen berbeda.
* Struktur informasi berbeda.
* Banyak part dengan nomor mirip.
* Perubahan revisi sering.
* Keputusan dilakukan manual tanpa sistem peringatan kontekstual.
* Tidak ada visibilitas pola risiko historis.

Sistem ini dirancang untuk menjadi:

> Structured Configuration Data Layer
>
> * Decision Guardrail
> * Configuration Intelligence Engine

---

# 2. TUJUAN SISTEM

1. Menyatukan data IPD dan Drawing dalam database terstruktur.
2. Menyediakan filtering deterministik berbasis line.
3. Mengurangi risiko salah pilih part.
4. Memberikan preview keputusan sebelum konfirmasi.
5. Mendeteksi alternatif dan part mirip.
6. Menyediakan riwayat revisi.
7. Menghitung risk score berbasis data historis.
8. Mendeteksi configuration drift.
9. Memberikan insight manajerial tanpa menggantikan otoritas engineering.

---

# 3. ARSITEKTUR SISTEM

```
DATA LAYER
(IPD + Drawing Structured Storage)

        ↓

CONFIGURATION FILTER ENGINE
(Line-based deterministic logic)

        ↓

DECISION PREVIEW LAYER
(Guardrail & Contextual Warning)

        ↓

INTELLIGENCE ENGINE
(Risk Scoring & Pattern Detection)

        ↓

ANALYTICS DASHBOARD
(Admin Only)
```

---

# 4. MODEL DATA TERPADU

---

## 4.1 Document

```
{
  document_id,
  document_type: "IPD" | "DRAWING",
  document_number,
  revision,
  issue_date,
  aircraft_model,
  source_pdf_path
}
```

---

## 4.2 IPD_Part

(Berdasarkan struktur IPD )

```
{
  ipd_part_id,
  document_id,
  change_type: "ADD" | "MODIFY" | "DELETE",
  figure,
  item,
  part_number,
  nomenclature,
  supplier_code,
  effectivity_type: "LIST" | "RANGE",
  effectivity_values: [],
  effectivity_range: { from, to },
  upa,
  sb_reference,
  page_number
}
```

---

## 4.3 Drawing_Item

(Berdasarkan drawing placard )

```
{
  drawing_item_id,
  document_id,
  item_number,
  part_number,
  title,
  sheet_number,
  material_spec,
  approval_authority,
  font_type,
  artwork_reference,
  notes
}
```

---

## 4.4 Part_Master

```
{
  part_number,
  linked_ipd_parts: [],
  linked_drawing_items: []
}
```

---

## 4.5 Decision_Log

```
{
  user_id,
  part_number,
  line_number,
  revision,
  timestamp_open,
  timestamp_confirm,
  duration_seconds,
  warnings_triggered: [],
  confirmation_checked: true
}
```

---

## 4.6 Part_Risk_Profile

```
{
  part_number,
  risk_score,
  volatility_index,
  similar_part_count,
  warning_count_30d,
  error_report_count,
  last_updated
}
```

---

## 4.7 Configuration_Drift_Log

```
{
  line_number,
  revision,
  conflicting_parts: [],
  detected_at,
  status
}
```

---

# 5. FITUR SISTEM TERINTEGRASI

---

# 5.1 Structured Data Layer

### FR-01 Input IPD Data

Admin dapat memasukkan IPD part lengkap dengan effectivity dan change_type.

### FR-02 Input Drawing Data

Admin dapat memasukkan drawing, item, approval authority, sheet.

Data per revisi immutable.

---

# 5.2 Configuration Filtering Engine

### FR-03 Line-Based Filtering

Input:

* line_number
* revision

Logic:

```
Jika line ∈ effectivity_values
atau dalam range
→ BERLAKU
Else → TIDAK BERLAKU
```

Output:

```
BERLAKU
TIDAK BERLAKU
```

---

# 5.3 Decision Preview Layer (Guardrail)

Setiap selection wajib melalui preview.

Preview menampilkan:

* Part Number
* Nomenclature
* Line
* Revision
* Change type
* SB reference
* Drawing reference
* Alternatif tersedia
* Part mirip

Engineer wajib centang:

```
Saya telah verifikasi terhadap dokumen resmi.
```

Tanpa centang → tidak bisa lanjut.

---

# 5.4 Alternative Detection

Jika:

* Figure sama
* Effectivity overlap
* Nomenclature mirip

Tampilkan sebagai alternatif.

---

# 5.5 Similar Part Detection

Jika:

* Prefix sama
* Levenshtein distance ≤ 2

Tampilkan warning.

---

# 5.6 Revision History View

Sistem menampilkan timeline revisi part:

* Rev
* Change type
* Tanggal

---

# 5.7 SB Flag Visibility

Jika IPD mencantumkan SB reference

Sistem menampilkan:

```
SB terkait. Refer ke dokumen SB resmi.
```

Tanpa compliance automation.

---

# 5.8 Cross-Document Reference

Jika part muncul di drawing

Tampilkan:

* Drawing number
* Item
* Approval authority
* Sheet

---

# 5.9 Risk Scoring Engine

Risk Score dihitung dari:

* Warning frequency
* Change frequency
* Similar part density
* Error report count
* Alternative overlap
* Drawing complexity

Formula transparan:

```
Risk Score =
(Warn × 0.3) +
(Change × 0.2) +
(Similar × 0.2) +
(Error × 0.2) +
(Overlap × 0.1)
```

Skala 0–100.

---

# 5.10 Volatility Index

```
Volatility =
Jumlah revisi yang mengubah part /
Total revisi
```

Kategori:

* Low
* Medium
* High

---

# 5.11 Configuration Drift Detection

Jika:

* Line sama
* Revision sama
* Part dipilih berbeda

→ Drift flag.

---

# 5.12 Near-Miss Detection

Jika:

* User buka part A
* Batal
* Pilih part B

Catat sebagai near-miss event.

---

# 5.13 Behavior Analytics Dashboard (Admin)

Menampilkan:

* Top 10 High Risk Parts
* Top 5 High Risk Lines
* Warning ignore rate
* Average decision time
* Drift cases

Data anonymized.

---

# 6. NON-FUNCTIONAL REQUIREMENTS

---

## 6.1 Performance

* Filtering ≤ 1 detik untuk 2000 part.
* Risk batch calculation ≤ 10 menit untuk 10.000 part.

---

## 6.2 Data Integrity

* Revisi immutable.
* Log immutable.
* Audit read-only.

---

## 6.3 Explainability

Setiap risk score harus dapat dijelaskan komponennya.

---

## 6.4 Security

* Role-based access.
* Admin analytics only.
* PDF referensi read-only.

---

# 7. METRIK SUKSES SISTEM

---

## 7.1 Error Rate

Target:
< 0.5 error per 100 lookup.

---

## 7.2 Risk Awareness

Indikator:

* Decision time naik sedikit.
* Error turun signifikan.

---

## 7.3 Drift Reduction

Target:
Penurunan konflik konfigurasi antar user.

---

# 8. BATASAN SISTEM

Sistem ini tidak:

* Menggantikan dokumen resmi.
* Mengeluarkan approval engineering.
* Menghitung compliance SB.
* Mengambil keputusan otomatis.

Sistem ini adalah:
Decision Support + Configuration Intelligence Platform.

---

# 9. EVOLUSI ARSITEKTUR

Phase 1 → Data Structure
Phase 2 → Guardrail
Phase 3 → Intelligence

Sekarang semuanya menyatu.

Bukan lagi viewer.
Bukan lagi filter tool.

Ini menjadi sistem yang:

* Mengerti struktur
* Mengawasi keputusan
* Membaca pola risiko

Dan tetap sadar batasnya.

Tidak mengambil alih manusia.
Hanya membuat salah jadi lebih sulit terjadi tanpa disadari.