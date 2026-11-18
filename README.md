# 🎮 Roblox Games Data Pipeline & Analytics Dashboard

## 📌 ภาพรวมโปรเจกต์ (Project Overview)
โปรเจกต์นี้เป็นการสร้างระบบท่อส่งข้อมูลอัตโนมัติ (End-to-End Data Pipeline) เพื่อดึงข้อมูลสถิติของเกมบนแพลตฟอร์ม Roblox มาทำความสะอาด แปลงรูปแบบ และส่งขึ้นคลาวด์ ก่อนนำไปแสดงผลผ่าน Dashboard 

**เป้าหมาย/ปัญหาที่โปรเจกต์นี้แก้ไข:**
เพื่อวิเคราะห์พฤติกรรมผู้เล่น สภาพการแข่งขันในตลาดเกม และประสิทธิภาพของเกมในหมวดหมู่ต่างๆ ซึ่งจะช่วยให้นักพัฒนาเกมสามารถหา "ช่องว่างตลาด (Blue Ocean)" และวางกลยุทธ์การปล่อยเกมหรืออัปเดตแพตช์ได้อย่างแม่นยำ

---

## 🏗️ สถาปัตยกรรมข้อมูล (Data Flow & Architecture)
โปรเจกต์นี้ทำงานแบบอัตโนมัติผ่านกระบวนการ ETL (Extract, Transform, Load) ดังนี้:

1. **Extract (`extract.py`):** ดึงข้อมูลดิบของเกมบน Roblox 
2. **Transform (`transform.py`):** ทำความสะอาดข้อมูล คัดเลือกเฉพาะคอลัมน์ที่จำเป็น และทำการยุบรวมข้อมูลเป็นรายวัน (Daily Aggregation) เพื่อลดขนาดข้อมูลให้เหลือประมาณ 8,400+ แถว ซึ่งเหมาะสมกับข้อจำกัดของ Google Sheets
3. **Load (`publish.py`):** ส่งมอบข้อมูลที่พร้อมใช้งาน (Clean Data) อัปโหลดขึ้น Google Sheets ผ่าน API
4. **Visualize (Looker Studio):** นำข้อมูลจาก Google Sheets ไปสร้างเป็น Interactive Dashboard เพื่อตอบคำถามทางธุรกิจ

---

## 📊 คำถามทางธุรกิจที่วิเคราะห์ (Business Questions Answered)
Dashboard ของโปรเจกต์นี้ถูกออกแบบมาเพื่อหา Insight ใน 5 ประเด็นหลัก:
* **Q1:** วิเคราะห์ความนิยมและสภาพการแข่งขันของตลาดเกม (Genre)
* **Q2:** วิเคราะห์ช่วงเวลา (วันในสัปดาห์) ที่มียอดผู้เล่น Peak ที่สุด
* **Q3:** ติดตามแนวโน้มการเติบโต/ถดถอย ของเกมระดับ Top 10
* **Q6:** ตรวจสอบการกระจุกตัวของตลาด และส่วนแบ่งผู้เล่นของ Creator 10 อันดับแรก
* **Q7:** เปรียบเทียบประสิทธิภาพของเกมในหมวดจัดอันดับต่างๆ (Popular, Engaging, Up-And-Coming)

*🔗 **[คลิกที่นี่เพื่อดู Looker Studio Dashboard] [https://datastudio.google.com/reporting/3f4592d0-0513-4d54-8991-05be2f1a9f77]*

---

## 🛠️ เครื่องมือและเทคโนโลยีที่ใช้ (Tech Stack)
* **ภาษาโปรแกรม:** Python (Pandas)
* **แหล่งเก็บข้อมูล (Data Warehouse):** Google Sheets API
* **การนำเสนอข้อมูล (BI Tool):** Google Looker Studio
* **การจัดการโค้ด:** `run_pipeline.py` สำหรับการรันระบบทั้งหมดแบบอัตโนมัติ

---

## 🚀 วิธีการติดตั้งและรันโค้ด (How to Run)

### 1. สิ่งที่ต้องเตรียม (Prerequisites)
* ติดตั้ง Python 3.x
* สมัครและเปิดใช้งาน Google Cloud Service Account พร้อมดาวน์โหลดไฟล์ `credentials.json` (นำมาวางไว้ในโฟลเดอร์เดียวกันกับโค้ด)
* แชร์ Google Sheets ของคุณให้มีสิทธิ์เข้าถึงจากอีเมลของ Service Account

### 2. การติดตั้งไลบรารี
เปิด Terminal/Command Prompt และรันคำสั่ง:
```bash
pip install pandas gspread oauth2client
```
*(หมายเหตุ: หากคุณมีไฟล์ requirements.txt ให้ใช้ `pip install -r requirements.txt` แทน)*

### 3. การรัน Data Pipeline
คุณสามารถรันกระบวนการทั้งหมด (Extract -> Transform -> Load) ได้ในคำสั่งเดียวผ่านสคริปต์หลัก:
```bash
python run_pipeline.py
```
เมื่อรันสำเร็จ โค้ดจะแสดงข้อความยืนยันการส่งข้อมูลขึ้น Google Sheets เรียบร้อยแล้ว

---
