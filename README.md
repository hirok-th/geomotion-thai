# GeoMotion Thai

Skill สำหรับผลิต Geographic Infographic Animation ภาษาไทยแบบ 2D–3D ใช้แกนงานเดียวกันบน **Claude, Codex และ Google Antigravity** พร้อมโค้ด Python/Blender, templates, ไอคอนและโมเดล, ฟอนต์ Kanit และการตั้งค่าบริการที่ไม่บรรจุข้อมูลลับ

**การติดตั้งและตรวจแพ็กเกจไม่ผลิตสื่อ** เริ่มค้นคว้า สร้างเสียง และเรนเดอร์เมื่อผู้ใช้สั่งสร้างคลิปเท่านั้น การอัปโหลด Skill ไม่ได้ติดตั้ง Blender/FFmpeg หรือให้สิทธิ์บัญชี Google โดยอัตโนมัติ

## ดาวน์โหลด

| ไฟล์ | ใช้เมื่อใด |
|---|---|
| [GeoMotion_Thai_Claude_Plugin.zip](dist/GeoMotion_Thai_Claude_Plugin.zip?raw=true) | หน้า **Upload plugin** ของ Claude มี `.claude-plugin/plugin.json` และ `skills/geomotion-thai/SKILL.md` |
| [GeoMotion_Thai_Kit.zip](dist/GeoMotion_Thai_Kit.zip?raw=true) | อัปโหลดเป็น Skill เดี่ยว หรือแตกไฟล์ติดตั้งกับ Claude Code, Codex และ Antigravity |

ดาวน์โหลด ZIP ที่ระบุด้านบนโดยตรง ไม่ใช้ ZIP ทั้ง repository ไปอัปโหลดในช่อง Skill/plugin เพราะ ZIP ทั้ง repository มีเอกสารและไฟล์แจกจ่ายเพิ่มเติม

## เลือกคู่มือตามโปรแกรม

| โปรแกรม | คู่มือติดตั้ง | เรียกใช้หลังติดตั้ง |
|---|---|---|
| Claude เว็บ/Desktop | [Claude](docs/CLAUDE.th.md) | พิมพ์ `ใช้ GeoMotion Thai ...` เมื่อเปิดใช้แล้ว |
| Claude Code แบบ Skill | [Claude Code](docs/CLAUDE.th.md#claude-code--skill-ในเครื่อง) | `/geomotion-thai` |
| Claude Code แบบ plugin | [Claude plugin](docs/CLAUDE.th.md#claude-code--plugin-จาก-source) | `/geomotion-thai:geomotion-thai` |
| Codex CLI/IDE | [Codex](docs/CODEX.th.md) | `$geomotion-thai` หรือเลือกผ่าน `/skills` |
| Google Antigravity App/CLI/IDE | [Antigravity](docs/ANTIGRAVITY.th.md) | `/geomotion-thai` ใน App/CLI; IDE ตรวจใน Customizations |

## ติดตั้งในเครื่องแบบเร็ว

ดาวน์โหลด repository ด้วย **Code → Download ZIP** แล้วแตกไฟล์ หรือ clone:

```bash
git clone https://github.com/hirok-th/geomotion-thai.git
cd geomotion-thai
```

เลือกคำสั่งเดียวสำหรับโปรแกรมที่ต้องการ ติดตั้งเป็น Skill ส่วนตัวบนเครื่องปัจจุบัน:

```bash
python skills/geomotion-thai/scripts/install_skill.py --platform claude --scope user --apply
python skills/geomotion-thai/scripts/install_skill.py --platform codex --scope user --apply
python skills/geomotion-thai/scripts/install_skill.py --platform antigravity --scope user --apply
```

ถ้า Windows ใช้ `py` แทน `python` ตามการติดตั้ง Python ของเครื่องนั้น ถ้าต้องการดูก่อนว่าจะคัดลอกไปที่ใด ให้เอา `--apply` ออก การติดตั้งนี้ใช้ Python standard library และคัดลอกไฟล์เท่านั้น ยังไม่ต้องติดตั้งเครื่องมือผลิตสื่อ

หากปลายทางมี Skill เดิมอยู่ ตัวติดตั้งจะหยุดก่อนเขียนทับ ใช้ `--replace` เพิ่มเมื่อคุณต้องการอัปเดต โดยตัวติดตั้งจะย้ายโฟลเดอร์เดิมเป็นสำรองก่อน

## ตัวอย่างคำสั่งสร้างคลิป

คัดลอกข้อความนี้ไปส่งให้ agent ในโปรแกรมที่ติดตั้ง Skill แล้ว เปลี่ยนหัวข้อและระยะเวลาตามต้องการ:

```text
ใช้ GeoMotion Thai สร้างคลิปเรื่อง “[หัวข้อ]” ความยาว 60 วินาที
แนวตั้ง 9:16 ขนาด 1080×1920 ที่ 30 fps
ค้นคว้าข้อมูลและระบุแหล่งที่มา เขียนบทเปิดเรื่องให้ดึงความสนใจ
ใช้แผนที่สีเข้มสด แสดงธงภายในรูปทรงประเทศก่อนซูมสู่ภูมิประเทศ 3D
ใส่ไอคอน วัตถุ ลูกศร และเส้นทางเคลื่อนไหวตรงกับเสียงพากย์
พากย์ผู้ชายไทยจาก Google AI Studio จริงจัง หนักแน่น ดุดัน
ถ่ายทอดอารมณ์และเว้นจังหวะเป็นธรรมชาติ
ใส่ซับ Kanit สีขาว เน้นคำสำคัญสีเหลือง ขอบดำ อ่านชัดบนมือถือ
ตรวจวิดีโอจริงก่อนส่ง MP4 พร้อมซับฝัง ไฟล์ SRT และโปรเจกต์ที่แก้ไขต่อได้
หากส่วนใดทำไม่ได้ ให้แจ้งตามจริง
```

แนวนอน: ระบุ `16:9 ขนาด 1920×1080 จัดองค์ประกอบใหม่สำหรับแนวนอน` ลายน้ำ: แนบโลโก้และสั่งชัดเจนว่า `ใช้โลโก้ที่แนบเป็นลายน้ำ` จึงเปิดใช้งาน ค่าเริ่มต้นขวาบน กว้าง 10% ทึบ 70%

## ความสามารถ

- แผนที่สีเข้มสด ไฮไลต์พื้นที่ตามประโยค/คำสำคัญ
- ธงอยู่ภายใน polygon ประเทศ: ภาพกว้าง → แสดงธง/ชื่อ → เว้นจังหวะ → ซูม → ลดธง → เอียงสู่ terrain 3D → วัตถุตามเรื่อง
- โมเดล/ไอคอนเครื่องบิน เรือ รถไฟ ราง รถยนต์ เมือง อาคาร โรงงาน ภูเขา ต้นไม้ เขื่อน อ่างเก็บน้ำ และลูกศรแยกชั้น
- เส้นทางเคลื่อนไหว วัตถุหันตามทิศทาง และกล้อง zoom/pan/tilt/rotate
- Google AI Studio สำหรับเสียงผู้ชายไทย; API เป็นตัวเลือกแยกที่ต้องแจ้งความต่างและได้รับอนุญาตก่อน
- ซับ Kanit Medium/SemiBold ขาว–เหลือง ขอบดำ พร้อม SRT; จับเวลาจากเสียงจริงและตรวจทาน
- ลายน้ำเมื่อมีทั้งไฟล์โลโก้และคำสั่งให้ใช้; รองรับ 9:16 และ 16:9

โมเดลเดิมเป็นงาน 3D แบบ stylized ที่มีเอกสารเปรียบเทียบกับภาพอ้างอิง ไม่รับรองว่าเหมือนภาพอ้างอิงแบบ photorealistic แผนที่ Natural Earth เป็นข้อมูลทั่วไปและเส้นทางตัวอย่างเป็น schematic ต้องเปลี่ยนข้อมูลและตรวจพิกัดสำหรับหัวข้อจริง

## เตรียมเครื่องผลิตสื่อภายหลัง

ต้องมี Python 3.11+, Blender รุ่นที่เข้ากันได้กับโค้ด (ชุดเดิมใช้ 4.2–4.3), FFmpeg/ffprobe พร้อม libass, Pillow/RAQM และ dependencies ที่ประกาศ การสร้างเสียงผ่าน Google AI Studio ต้องมีบัญชี/สิทธิ์และวิธีเชื่อมต่อที่ host รองรับ ตรวจรุ่นและเสียงที่มีจริงตอนผลิต ไม่ถือว่ามีเสียงชื่อใดให้ใช้เสมอ

```bash
python -m venv .venv
# เปิดใช้ venv ตามระบบปฏิบัติการของคุณ แล้วติดตั้ง:
python -m pip install -r skills/geomotion-thai/requirements.txt
python skills/geomotion-thai/scripts/geomotion.py doctor
```

อ่าน [การเชื่อมต่อ Google](skills/geomotion-thai/references/connections.md) และ [ข้อจำกัดของสภาพแวดล้อม](skills/geomotion-thai/references/environment.md) ค่าเริ่มต้น Gemini API เป็น `enabled: false` เก็บ key นอก repository ผ่าน environment variable เท่านั้น

## การตรวจที่ทำแล้วและยังไม่ได้ทดสอบ

ตรวจแบบออฟไลน์ **12 รายการผ่าน** รวม syntax, JSON/YAML, resources, การปิดบริการตามค่าเริ่มต้น, ตัวป้องกันการผลิตสื่อ, เส้นทางติดตั้ง, templates สองสัดส่วน และ ZIP/checksum ทั้งสองแบบ ดู [รายงาน](skills/geomotion-thai/references/package-validation.json)

```bash
python skills/geomotion-thai/scripts/check_package.py
python skills/geomotion-thai/scripts/build_package.py dist/GeoMotion_Thai_Kit.zip --kind skill --check-only
python skills/geomotion-thai/scripts/build_package.py dist/GeoMotion_Thai_Claude_Plugin.zip --kind claude-plugin --check-only
```

**ยังไม่ได้ทดสอบ** การยอมรับไฟล์ในบัญชี Claude ของผู้ใช้จริง, การค้นพบ/เรียกใช้ในโปรแกรมทั้งสามที่ติดตั้งแยก, Google speech/API จริง, การซิงก์เสียงจริง และเรนเดอร์ครบกระบวนการในรุ่นนี้ ไม่มีการสร้างคลิปหรือเสียงใหม่ระหว่างจัดแพ็กเกจ

## โครงสร้างและสิทธิ์ทรัพยากร

Source อยู่ใน `skills/geomotion-thai/`; manifest สำหรับ Claude อยู่ที่ `.claude-plugin/plugin.json`; ZIP พร้อมติดตั้งอยู่ที่ `dist/`; คู่มือภาษาไทยอยู่ที่ `docs/` เปลี่ยนหัวข้อผ่าน templates/ข้อมูลโปรเจกต์ โดยไม่แก้ renderer หลัก

อ่าน [LICENSE](LICENSE) และ [แหล่งข้อมูล/สิทธิ์](skills/geomotion-thai/references/data-and-rights.md) ฟอนต์ Kanit ใช้ SIL OFL; ข้อมูลภูมิศาสตร์และ DEM มีข้อกำหนดของแต่ละแหล่ง ภาพอ้างอิงที่ผู้ใช้ให้ใช้เพื่อเปรียบเทียบสไตล์ ไม่ใช่การให้สิทธิ์บุคคลที่สามในภาพนั้น

คู่มือแพลตฟอร์มตรวจจากเอกสารทางการวันที่ 25 พฤศจิกายน 2569: [Claude Code](https://code.claude.com/docs/en/skills), [Claude Skill ZIP](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills), [Codex](https://developers.openai.com/codex/skills), [Antigravity](https://antigravity.google/docs/skills)
