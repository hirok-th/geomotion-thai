# ติดตั้งและเรียกใช้ใน Google Antigravity

[กลับหน้าหลัก](../README.md)

ใช้ source หรือ portable [GeoMotion_Thai_Kit.zip](../dist/GeoMotion_Thai_Kit.zip?raw=true) วิธีที่เอกสารนี้แนะนำเป็น **Agent Skill แบบ local** ไม่อาศัย manifest ของ Claude

## ติดตั้งใน App / CLI / IDE

จาก root ของ repository หลังดาวน์โหลด/clone ให้เลือกแบบส่วนตัว:

```bash
python skills/geomotion-thai/scripts/install_skill.py --platform antigravity --scope user --apply
```

ปลายทาง `~/.gemini/config/skills/geomotion-thai/` หรือเลือกเฉพาะโปรเจกต์:

```bash
python skills/geomotion-thai/scripts/install_skill.py --platform antigravity --scope project --workspace /absolute/path/to/project --apply
```

ปลายทาง `<workspace-root>/.agents/skills/geomotion-thai/` ใน Windows ใช้ `py` แทน `python` ได้ และแทน path ด้วย `"C:/Projects/MyVideo"`

เปิด workspace นั้นใน Antigravity หากใช้ standalone IDE ให้ตรวจ Skill ในเมนู **Customizations** ของ agent side panel โฟลเดอร์ `.agent/skills` เป็นรูปแบบเก่าที่บางรุ่นยังรองรับ ให้ยึดเอกสารของรุ่นที่ติดตั้งจริงก่อนย้ายตำแหน่ง

## เรียกใช้

Antigravity App และ CLI รองรับ slash command ในช่องสนทนา:

```text
/geomotion-thai ตรวจความพร้อม โดยยังไม่สร้างสื่อหรือเชื่อมต่อ Google
```

```text
/geomotion-thai สร้างคลิปเรื่อง “[หัวข้อ]” 60 วินาที 9:16
พากย์ชายไทยจาก Google AI Studio จริงจัง หนักแน่น ดุดัน เว้นจังหวะเป็นธรรมชาติ
ใช้แผนที่ 2D–3D ธงในประเทศ ลูกศรและวัตถุเคลื่อนไหว พร้อมซับ Kanit สองสี
ตรวจไฟล์จริงแล้วส่ง MP4, SRT และโปรเจกต์ต้นฉบับ
```

ถ้า CLI ไม่เห็น Skill ที่เพิ่งเพิ่ม ให้ใช้ `/skills reload` หรือเริ่มบทสนทนาใหม่ตามรุ่นของ CLI ส่วน IDE ให้ตรวจเมนู Customizations และสามารถพิมพ์ `ใช้ GeoMotion Thai ...` เพื่อให้ agent เลือก Skill ที่ค้นพบอยู่แล้ว

ตรวจเครื่องมือจริงก่อนผลิต: Python, Blender, FFmpeg/ffprobe, Thai shaping และวิธีเชื่อมต่อ Google AI Studio ตาม [หน้าหลัก](../README.md#เตรียมเครื่องผลิตสื่อภายหลัง) การติดตั้งไม่สร้างเสียง ไม่เรียก API และไม่เรนเดอร์ API ของ Gemini ปิดไว้โดยค่าเริ่มต้น ต้องแจ้งความต่างและได้รับอนุญาตก่อนใช้แทนหน้า Google AI Studio

แหล่งทางการ: [Antigravity Agent Skills](https://antigravity.google/docs/skills) ตรวจเอกสารวันที่ 25 พฤศจิกายน 2569; ทดสอบเส้นทางติดตั้งออฟไลน์แล้ว ยังไม่ได้ทดสอบ discovery/execution ใน Antigravity บนเครื่องผู้ใช้จริง
