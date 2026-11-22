# 🎮 Roblox Games Data Pipeline & Analytics Dashboard

## 📌 ภาพรวมโปรเจกต์ (Project Overview)
โปรเจกต์นี้สร้างระบบ Data Pipeline อัตโนมัติแบบ End-to-End ที่นำข้อมูลสถิติเกมบนแพลตฟอร์ม Roblox จาก Kaggle (119,715 แถว, ประมาณ 117 MB) มาทำความสะอาด แปลงรูปแบบ และยุบรวมเป็นข้อมูลรายวัน (8,487 แถว) ก่อนส่งขึ้น Google Sheets และแสดงผลผ่าน Looker Studio Dashboard

**เป้าหมาย:** วิเคราะห์พฤติกรรมผู้เล่น สภาพการแข่งขันในตลาด และประสิทธิภาพของเกมแต่ละหมวด เพื่อช่วยนักพัฒนาเกมหาช่องว่างตลาด (Blue Ocean) และวางแผนการปล่อยอัปเดตได้แม่นยำขึ้น

* 📊 **Dashboard:** [Looker Studio Dashboard](https://datastudio.google.com/reporting/3f4592d0-0513-4d54-8991-05be2f1a9f77)
* 📦 **ชุดข้อมูลต้นทาง:** [Roblox Games Data (Kaggle)](https://www.kaggle.com/datasets/databitio/roblox-games-data)

---

## 🏗️ สถาปัตยกรรมข้อมูล (Data Architecture)

```
roblox_games_data.csv
      │  ingest.py      (Extract)
      ▼
PostgreSQL : raw_data.roblox_games_data
      │  transform.py   (Transform)
      ▼
PostgreSQL : production.roblox_games_data
      │  publish.py     (Load + Daily Aggregation)
      ▼
Google Sheets  ──►  Looker Studio Dashboard
```

| ขั้นตอน | ไฟล์ | หน้าที่ |
| --- | --- | --- |
| Extract | `ingest.py` | อ่าน CSV ด้วย Pandas กำหนด Data Type และนำเข้า Schema `raw_data` ทีละ 5,000 แถว พร้อมตรวจนับจำนวนแถวเทียบกับไฟล์ต้นทาง |
| Transform | `transform.py` | ลบคอลัมน์ที่ไม่ใช้ เติมค่าว่าง ปรับรูปแบบวันที่ และแปลง `Total Visits` จากข้อความ (เช่น `50.9M+`) เป็นตัวเลข แล้วบันทึกลง Schema `production` |
| Load | `publish.py` | ยุบรวมเป็นรายวันต่อเกม (Daily Snapshot) แล้วอัปโหลดขึ้น Google Sheets ผ่าน Service Account |
| Orchestration | `run_pipeline.py` | รันทั้ง 3 ขั้นตามลำดับ และหยุดทันทีถ้าขั้นใดล้มเหลว (Fail-Fast) |

---

## 🛠️ เครื่องมือที่ใช้ (Tech Stack)
* **Python 3 + Pandas** — อ่าน ทำความสะอาด และยุบรวมข้อมูล
* **PostgreSQL 16 + Docker Compose** — ฐานข้อมูลกลาง แยก Schema `raw_data` / `production`
* **SQLAlchemy + psycopg2** — เชื่อมต่อฐานข้อมูล
* **gspread + gspread-dataframe** — ส่งข้อมูลขึ้น Google Sheets
* **Google Looker Studio** — สร้าง Interactive Dashboard

---

## 📊 คำถามทางธุรกิจ (Business Questions)
* **Q1:** หมวดเกม (Genre) ใดคู่แข่งน้อยแต่ผู้เล่นสูง (Blue Ocean) และหมวดใดแข่งขันสูง (Red Ocean)
* **Q2:** วันใดในสัปดาห์ที่มียอดผู้เล่นสูงสุด
* **Q3:** เกม Top 10 เกมใดเติบโตหรือถดถอย
* **Q6:** ตลาดกระจุกตัวแค่ไหน และ Creator 10 อันดับแรกครองส่วนแบ่งผู้เล่นเท่าใด
* **Q7:** เปรียบเทียบหมวดจัดอันดับ Popular / Most Engaging / Up-And-Coming

---

## 🚀 วิธีติดตั้งและรันโปรเจกต์ (How to Run)

### 1. สิ่งที่ต้องมี
* Python 3.9 ขึ้นไป
* Docker Desktop (สำหรับรัน PostgreSQL)
* Google Cloud Service Account และไฟล์กุญแจ `credentials.json` (ดูขั้นตอนที่ 4)

### 2. Clone และเตรียมไฟล์ข้อมูล
```bash
git clone https://github.com/waru1549/roblox-data-pipeline.git
cd roblox-data-pipeline
unzip roblox_games_data.csv.zip
```
> ไฟล์ CSV ต้นฉบับมีขนาดประมาณ 117 MB ซึ่งเกินลิมิต 100 MB ของ GitHub จึงเก็บไว้ในรูป `.zip` ต้องแตกไฟล์ให้ได้ `roblox_games_data.csv` ในโฟลเดอร์เดียวกับโค้ดก่อนรัน

### 3. สร้างไฟล์ `.env`
สร้างไฟล์ชื่อ `.env` ในโฟลเดอร์โปรเจกต์ (ไฟล์นี้อยู่ใน `.gitignore` จะไม่ถูกอัปโหลดขึ้น GitHub)
```env
POSTGRES_DB=roblox_db
POSTGRES_USER=roblox_user
POSTGRES_PASSWORD=your_password
POSTGRES_PORT=5433
GOOGLE_SHEET_NAME=Roblox_Dashboard_Data
```

### 4. ตั้งค่า Google API Credentials
1. เข้า [Google Cloud Console](https://console.cloud.google.com/) แล้วสร้าง Project ใหม่
2. ไปที่ **APIs & Services → Library** แล้วเปิดใช้งาน **Google Sheets API** และ **Google Drive API**
3. ไปที่ **IAM & Admin → Service Accounts → Create Service Account**
4. เปิด Service Account ที่สร้าง → แท็บ **Keys → Add Key → Create new key → JSON**
5. เปลี่ยนชื่อไฟล์ที่ดาวน์โหลดเป็น `credentials.json` แล้ววางไว้ในโฟลเดอร์โปรเจกต์
6. สร้าง Google Sheet ชื่อตรงกับ `GOOGLE_SHEET_NAME` แล้วกด **Share** ให้อีเมลของ Service Account (ค่า `client_email` ในไฟล์ JSON) เป็น **Editor**

> ⚠️ ห้าม commit `credentials.json` ขึ้น GitHub เด็ดขาด ไฟล์นี้ถูกระบุไว้ใน `.gitignore` แล้ว

### 5. เปิดฐานข้อมูล PostgreSQL
```bash
docker compose up -d
```

### 6. ติดตั้งไลบรารี
```bash
pip install -r requirements.txt
```

### 7. รัน Data Pipeline
```bash
python run_pipeline.py
```
สคริปต์จะรัน `ingest.py` → `transform.py` → `publish.py` ตามลำดับ เมื่อสำเร็จจะแสดงข้อความ `PIPELINE EXECUTION COMPLETED SUCCESSFULLY!` และข้อมูลจะขึ้นใน Google Sheets พร้อมให้ Looker Studio ดึงไปแสดงผล

---

## 📁 โครงสร้างไฟล์
```
roblox-data-pipeline/
├── ingest.py                 # Extract: CSV → raw_data
├── transform.py              # Transform: raw_data → production
├── publish.py                # Load: production → Google Sheets
├── run_pipeline.py           # รันทุกขั้นตอนในคำสั่งเดียว
├── docker-compose.yml        # PostgreSQL 16
├── requirements.txt
├── roblox_games_data.csv.zip # ข้อมูลดิบ (บีบอัด)
├── .gitignore
└── README.md
```
ไฟล์ที่ต้องสร้างเองและไม่ถูก commit: `.env`, `credentials.json`, `roblox_games_data.csv`
