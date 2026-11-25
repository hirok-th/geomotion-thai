# ติดตั้งและเรียกใช้ใน Codex

[กลับหน้าหลัก](../README.md)

## Codex CLI / IDE extension

ดาวน์โหลดหรือ clone repository แล้วเปิด Terminal/PowerShell ที่ root ของ repository เลือกแบบส่วนตัว:

```bash
python skills/geomotion-thai/scripts/install_skill.py --platform codex --scope user --apply
```

ปลายทาง `~/.agents/skills/geomotion-thai/` หรือเลือกเฉพาะโปรเจกต์:

```bash
python skills/geomotion-thai/scripts/install_skill.py --platform codex --scope project --workspace /absolute/path/to/project --apply
```

ปลายทาง `<project>/.agents/skills/geomotion-thai/` ใน Windows ใช้ `py` แทน `python` ได้ และใช้ path ของเครื่อง เช่น `"C:/Projects/MyVideo"`

เปิดโปรเจกต์ใน Codex แล้วเลือกผ่าน `/skills` หรือพิมพ์ `$` เพื่อเลือก Skill จากรายการ ข้อความต่อไปนี้พิมพ์ในช่องสนทนา Codex **ไม่ใช่คำสั่ง shell**:

```text
$geomotion-thai ตรวจความพร้อม โดยยังไม่สร้างสื่อหรือเชื่อมต่อ Google
```

```text
$geomotion-thai สร้างคลิปเรื่อง “[หัวข้อ]” 60 วินาที 9:16
พากย์ชายไทยจาก Google AI Studio จริงจัง หนักแน่น ดุดัน
ใช้แผนที่ 2D–3D ธงในประเทศ ลูกศรและวัตถุเคลื่อนไหว พร้อมซับ Kanit สองสี
ตรวจไฟล์จริงแล้วส่ง MP4, SRT และโปรเจกต์ที่แก้ไขต่อได้
```

ไม่ปรากฏในรายการ: ตรวจ `SKILL.md` ที่ปลายทาง และเปิด/รีเฟรชรายการ Skill หรือเริ่มบทสนทนาใหม่ตามไคลเอนต์ที่ใช้ ไม่ถือว่าติดตั้ง dependencies หรืออนุญาตบริการ Google แล้วเพียงเพราะ Skill ปรากฏ

## Codex ใน ChatGPT / สภาพแวดล้อมที่จัดการให้

การคัดลอกไฟล์บนเครื่องของคุณไม่ได้ติดตั้งเข้าสู่บัญชี ChatGPT โดยอัตโนมัติ ใช้ช่องทางอัปโหลด/เลือก Skill หรือ plugin ที่ไคลเอนต์และบัญชีนั้นรองรับ ถ้า GeoMotion Thai ติดตั้งอยู่ในรายการแล้ว ให้เลือกชื่อ Skill และใช้คำสั่งภาษาไทยบนหน้าหลัก การเรียก browser, Google speech และ renderer ต้องขึ้นกับสิทธิ์/เครื่องมือจริงของ session นั้น

สำหรับการติดตั้งแบบ local ให้ใช้ portable [GeoMotion_Thai_Kit.zip](../dist/GeoMotion_Thai_Kit.zip?raw=true) หรือ source ใน repository นี้ ไม่ถือว่า wrapper ของ Claude เป็น manifest plugin ของ Codex โดยอัตโนมัติ

อ่าน [dependencies](../README.md#เตรียมเครื่องผลิตสื่อภายหลัง) และ [บริการ/ข้อมูลลับ](../skills/geomotion-thai/references/connections.md) เมื่อต้องการผลิตจริงเท่านั้น

แหล่งทางการ: [Codex skills และตำแหน่งค้นหา local](https://developers.openai.com/codex/skills) ตรวจเอกสารวันที่ 25 พฤศจิกายน 2569; ทดสอบเส้นทางติดตั้งออฟไลน์แล้ว ยังไม่ได้ทดสอบ discovery ใน Codex ที่ติดตั้งแยกบนเครื่องผู้ใช้
