# ติดตั้งและเรียกใช้ใน Claude

[กลับหน้าหลัก](../README.md)

## Claude เว็บ / Desktop

1. ดาวน์โหลด [GeoMotion_Thai_Claude_Plugin.zip](../dist/GeoMotion_Thai_Claude_Plugin.zip?raw=true)
2. เปิดหน้า Plugins ของคุณ แล้วเลือก Upload plugin หรือเมนูอัปโหลดที่รุ่นของคุณแสดง
3. อัปโหลด ZIP ทั้งไฟล์ **ไม่แตกไฟล์และไม่ใช้ Code → Download ZIP ของทั้ง repository**
4. เปิดใช้งาน GeoMotion Thai แล้วพิมพ์คำสั่งตามตัวอย่างด้านล่าง

ถ้าใช้เมนูอัปโหลด **Skill เดี่ยว** ให้เลือก [GeoMotion_Thai_Kit.zip](../dist/GeoMotion_Thai_Kit.zip?raw=true) แทน ซึ่งมี `geomotion-thai/SKILL.md` และทุกไฟล์อยู่ภายใต้โฟลเดอร์หลักเดียวกัน

```text
ใช้ GeoMotion Thai ตรวจความพร้อมของแพ็กเกจ โดยยังไม่สร้างสื่อหรือเชื่อมต่อ Google
```

เมื่อจะผลิตจริง:

```text
ใช้ GeoMotion Thai สร้างคลิปเรื่อง “[หัวข้อ]” 60 วินาที 9:16
พากย์ชายไทยจาก Google AI Studio จริงจัง ดุดัน เว้นจังหวะเป็นธรรมชาติ
ใช้แผนที่ 2D–3D ธงในประเทศ ลูกศรและวัตถุเคลื่อนไหว พร้อมซับ Kanit สองสี
ตรวจไฟล์จริงแล้วส่ง MP4, SRT และโปรเจกต์ต้นฉบับ
```

การอัปโหลดสำเร็จหมายถึงติดตั้งคำแนะนำ/ไฟล์ ไม่รับรองว่า host มี Blender, FFmpeg, browser authorization หรือ Google AI Studio พร้อมใช้งาน ต้องตรวจจริงก่อนผลิต และแจ้งข้อจำกัดหาก host รันไม่ได้ ไม่ขอ login และไม่สร้างเสียงตอนติดตั้ง

## Claude Code — Skill ในเครื่อง

จาก root ของ repository ที่ดาวน์โหลดหรือ clone แล้ว:

```bash
python skills/geomotion-thai/scripts/install_skill.py --platform claude --scope user --apply
```

ปลายทาง `~/.claude/skills/geomotion-thai/` ใช้ได้กับโปรเจกต์ของเครื่องนั้น ถ้าต้องการเฉพาะโปรเจกต์:

```bash
python skills/geomotion-thai/scripts/install_skill.py --platform claude --scope project --workspace /absolute/path/to/project --apply
```

ปลายทาง `<project>/.claude/skills/geomotion-thai/` ใน Windows ให้ใส่ path ในเครื่อง เช่น `--workspace "C:/Projects/MyVideo"`; ใช้ `py` แทน `python` ได้ตามการติดตั้ง

ในช่องสนทนา Claude Code:

```text
/geomotion-thai ตรวจความพร้อม โดยยังไม่สร้างสื่อ
```

```text
/geomotion-thai สร้างคลิปเรื่อง “[หัวข้อ]” 60 วินาที 9:16 พากย์ชายไทยจาก Google AI Studio พร้อมซับ Kanit สองสี
```

ถ้าไม่ปรากฏ ให้ตรวจว่ามี `SKILL.md` ตรง path ที่ระบุ แล้วตรวจเมนู `/skills` หรือ `/reload-skills` ตามรุ่นที่ใช้

## Claude Code — plugin จาก source

Repository นี้มี manifest ที่ root และมี `skills/` ตามโครงสร้าง Claude plugin สามารถโหลดภายในเครื่องเพื่อใช้งาน/ตรวจได้:

```bash
claude --plugin-dir /absolute/path/to/geomotion-thai
```

เมื่อโหลดเป็น plugin คำสั่งมี namespace ต่างจาก Skill เดี่ยว:

```text
/geomotion-thai:geomotion-thai ตรวจความพร้อม โดยยังไม่สร้างสื่อ
```

ก่อนผลิตคลิปให้เตรียม dependencies ตาม [หน้าหลัก](../README.md#เตรียมเครื่องผลิตสื่อภายหลัง) และอ่าน [การเชื่อมต่อ](../skills/geomotion-thai/references/connections.md) ไม่มี API key บรรจุใน ZIP

แหล่งทางการ: [Skills](https://code.claude.com/docs/en/skills), [plugin structure](https://code.claude.com/docs/en/plugins/manifest-reference), [custom Skill ZIP](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) ตรวจเอกสารวันที่ 25 พฤศจิกายน 2569; ยังไม่ได้ทดสอบการอัปโหลด/การค้นพบในเครื่องผู้ใช้จริง
