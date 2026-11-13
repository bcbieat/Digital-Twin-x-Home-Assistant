# แผนงานโปรเจกต์ 3D Digital Twin และ Home Assistant IoT

## 1. ภาพรวมโครงการ

โครงการนี้มีเป้าหมายเพื่อสร้างโมเดล 3 มิติของห้อง **A3 และ A4** ภายในบริษัท Innovative Village รวมถึงอุปกรณ์ไฟฟ้าและอุปกรณ์ IoT ที่อยู่ในพื้นที่จริง จากนั้นนำโมเดลไปใช้งานร่วมกับแพลตฟอร์ม 3D ที่บริษัทกำลังพัฒนา เพื่อให้ผู้ใช้งานสามารถตรวจสอบสถานะและสั่งงานอุปกรณ์ IoT ผ่านพื้นที่ 3D ได้

ลำดับการสื่อสารหลักของระบบ:

```text
ผู้ใช้งานบนแพลตฟอร์ม 3D
        ↓ คำสั่งควบคุม
แพลตฟอร์ม 3D / Backend Integration
        ↓ Home Assistant API
Home Assistant
        ↓ Protocol ของอุปกรณ์ เช่น Wi-Fi, Zigbee หรือ MQTT
อุปกรณ์ IoT ในห้อง A3 และ A4
        ↓ สถานะจริงของอุปกรณ์
Home Assistant
        ↓ State Update / Event
แพลตฟอร์ม 3D แสดงผลสถานะล่าสุด
```

---

# 2. Task Breakdown

## Phase 0 — ทำความเข้าใจระบบและกำหนดขอบเขต

### TASK 0.1: ประชุมรับ Requirement จากผู้ดูแลโครงการ

- [ ] ระบุวัตถุประสงค์หลักของระบบ 3D
- [ ] ระบุผู้ใช้งานระบบ เช่น พนักงาน ผู้ดูแลระบบ หรือผู้เข้าชม
- [ ] ระบุสิ่งที่ต้องส่งมอบในช่วงฝึกงาน
- [ ] กำหนดขอบเขตพื้นที่ว่าครอบคลุมเฉพาะห้อง A3 และ A4 หรือรวมพื้นที่อื่น
- [ ] กำหนดว่าโมเดลต้องสมจริงระดับใด
- [ ] ระบุอุปกรณ์ที่ผู้ใช้ต้องสามารถควบคุมผ่านแพลตฟอร์ม 3D
- [ ] ระบุอุปกรณ์ที่ใช้แสดงสถานะอย่างเดียวและไม่ให้สั่งงาน

**ผลลัพธ์ที่ต้องได้**

- Project Scope
- รายการ Deliverables
- รายการฟีเจอร์ In Scope และ Out of Scope
- ผู้รับผิดชอบและผู้ตรวจรับงานแต่ละส่วน

---

### TASK 0.2: ศึกษาแพลตฟอร์ม 3D ที่พนักงานกำลังพัฒนา

- [ ] ตรวจสอบว่าแพลตฟอร์มใช้เทคโนโลยีอะไร เช่น Three.js, React Three Fiber, Babylon.js หรือ Unity WebGL
- [ ] ตรวจสอบวิธีนำเข้าไฟล์โมเดล 3D
- [ ] ยืนยันรูปแบบไฟล์ที่รองรับ เช่น `.glb` หรือ `.gltf`
- [ ] ตรวจสอบระบบพิกัด แกน และหน่วยวัดของแพลตฟอร์ม
- [ ] ตรวจสอบข้อจำกัดด้าน Polygon, Texture และขนาดไฟล์
- [ ] ตรวจสอบวิธีเลือกหรือคลิก Object ในฉาก 3D
- [ ] ตรวจสอบวิธีเปลี่ยน Material, Emission หรือสถานะของ Object
- [ ] ตรวจสอบว่าแพลตฟอร์มมี Backend หรือ Integration Layer อยู่แล้วหรือไม่

**ผลลัพธ์ที่ต้องได้**

- `3D_PLATFORM_TECHNICAL_SPEC.md`
- Model Export Specification
- Naming Convention ที่ตกลงร่วมกับทีมพัฒนา

---

## Phase 1 — สำรวจพื้นที่และเก็บข้อมูลจริง

### TASK 1.1: สำรวจห้อง A3 และ A4

- [ ] ถ่ายภาพพื้นที่จากหลายมุม
- [ ] เก็บภาพ Top View หรือแบบแปลนที่มีอยู่
- [ ] วัดความกว้าง ความยาว และความสูงของห้อง
- [ ] วัดตำแหน่งประตู หน้าต่าง เสา ผนัง และเฟอร์นิเจอร์
- [ ] ระบุทิศทางและตำแหน่งอ้างอิงของพื้นที่
- [ ] บันทึกตำแหน่งอุปกรณ์ไฟฟ้าและ IoT ทุกชิ้น
- [ ] ตรวจสอบจุดที่ภาพหรือข้อมูลยังไม่ชัดเจน

**ผลลัพธ์ที่ต้องได้**

- ภาพ Reference ของห้อง A3 และ A4
- แบบแปลนพร้อมขนาดจริง
- ตารางพิกัดโดยประมาณของอุปกรณ์

---

### TASK 1.2: จัดทำรายการอุปกรณ์ 3D

สร้าง Asset Inventory โดยเก็บข้อมูลอย่างน้อยดังนี้:

| ข้อมูล | ตัวอย่าง |
|---|---|
| Asset ID | `A3_LIGHT_01` |
| ชื่ออุปกรณ์ | ไฟเพดาน A3 หมายเลข 1 |
| ห้อง | A3 |
| ประเภท | Light |
| จำนวน | 1 |
| ขนาดจริง | 0.60 × 0.60 × 0.08 เมตร |
| ตำแหน่งติดตั้ง | เพดาน |
| ต้องควบคุมหรือไม่ | ใช่ |
| Home Assistant Entity | ยังไม่ยืนยัน |
| ระดับความสำคัญ | สูง |
| สถานะข้อมูล | รอวัดขนาด |

- [ ] ทำรายการอุปกรณ์ในห้อง A3
- [ ] ทำรายการอุปกรณ์ในห้อง A4
- [ ] แยกอุปกรณ์ที่ต้องปั้นใหม่
- [ ] แยกอุปกรณ์ที่สามารถใช้ Asset เดียวกันซ้ำได้
- [ ] จัดลำดับอุปกรณ์ตามความสำคัญ

**ผลลัพธ์ที่ต้องได้**

- `ASSET_INVENTORY.csv` หรือ Spreadsheet
- รายการอุปกรณ์ที่ต้องทำโมเดลทั้งหมด

---

### TASK 1.3: สำรวจอุปกรณ์ใน Home Assistant

- [ ] ขอสิทธิ์เข้าถึงระบบสำหรับการศึกษาและทดสอบอย่างเหมาะสม
- [ ] ตรวจสอบ Home Assistant Version และวิธีติดตั้ง
- [ ] ระบุ Integration ที่ใช้งานกับอุปกรณ์จริง
- [ ] เก็บรายการ `entity_id` ของห้อง A3 และ A4
- [ ] บันทึก Domain ของแต่ละ Entity เช่น `light`, `switch`, `climate` หรือ `sensor`
- [ ] บันทึก State และ Attributes ที่สำคัญ
- [ ] ระบุอุปกรณ์ที่มีสถานะ `unavailable` หรือทำงานไม่เสถียร
- [ ] ตรวจสอบสิทธิ์ของ Account หรือ Token ที่ใช้ทดสอบ

**ข้อควรระวัง**

- ห้ามบันทึก Access Token, Password หรือ Secret ลง Git หรือเอกสารที่แชร์
- ใช้บัญชีหรือ Token สำหรับ Development ที่มีสิทธิ์เท่าที่จำเป็น
- หลีกเลี่ยงการทดสอบกับอุปกรณ์ที่กระทบผู้ใช้งานจริงโดยไม่ได้รับอนุญาต

**ผลลัพธ์ที่ต้องได้**

- `HOME_ASSISTANT_ENTITY_INVENTORY.md` หรือ Spreadsheet
- รายการ Entity ที่พร้อมเชื่อมต่อ
- รายการ Entity ที่ยังต้องแก้ไขหรือยืนยัน

---

## Phase 2 — กำหนดมาตรฐานการสร้างโมเดล 3D

### TASK 2.1: กำหนด Blender Modeling Standard

- [ ] ตั้งหน่วยวัดเป็น Metric และใช้สเกล 1 Blender Unit = 1 เมตร
- [ ] กำหนดทิศทางแกนให้ตรงกับแพลตฟอร์มปลายทาง
- [ ] กำหนดตำแหน่ง Origin/Pivot ของ Asset แต่ละประเภท
- [ ] กำหนด Naming Convention ของ Object, Mesh, Material และ Texture
- [ ] กำหนด Polygon Budget ต่อ Asset และต่อห้อง
- [ ] กำหนด Texture Resolution เช่น 512, 1024 หรือ 2048 px
- [ ] กำหนดรูปแบบ PBR Material ที่รองรับ
- [ ] กำหนดมาตรฐาน UV Mapping
- [ ] กำหนดรูปแบบไฟล์ Export เป็น glTF 2.0 (`.glb`)
- [ ] กำหนดวิธี Apply Transform ก่อน Export

**ตัวอย่าง Naming Convention**

```text
ROOM_A3
ROOM_A4
DEV_A3_LIGHT_CEILING_01
DEV_A3_AC_WALL_01
DEV_A4_SWITCH_WALL_01
MAT_LIGHT_BODY_WHITE
MAT_LIGHT_EMISSION
```

**ผลลัพธ์ที่ต้องได้**

- `BLENDER_ASSET_STANDARD.md`
- Blender Template File
- Export Checklist

---

### TASK 2.2: สร้าง Prototype Asset หนึ่งชิ้น

เลือกอุปกรณ์ที่รูปทรงไม่ซับซ้อนและมีสถานะเปิด/ปิด เช่น ไฟเพดานหนึ่งดวง

- [ ] สร้างโมเดลตามขนาดจริง
- [ ] สร้าง Material แยกส่วน Body และ Emission
- [ ] ตั้งชื่อ Object และ Material ตามมาตรฐาน
- [ ] ตั้ง Origin และ Apply Transform
- [ ] Export เป็น `.glb`
- [ ] ตรวจสอบไฟล์ด้วย glTF Validator
- [ ] นำเข้าแพลตฟอร์ม 3D ทดสอบ
- [ ] ตรวจสอบ Scale, Rotation, Material และการคลิก Object
- [ ] รับ Feedback จากผู้พัฒนาแพลตฟอร์ม
- [ ] ปรับมาตรฐานก่อนเริ่มปั้น Asset จำนวนมาก

**Acceptance Criteria**

- ขนาดและทิศทางถูกต้องเมื่อโหลดเข้าแพลตฟอร์ม
- ระบบสามารถหา Object จากชื่อหรือ Metadata ได้
- ระบบสามารถเปลี่ยนสถานะการแสดงผล On/Off ได้
- ขนาดไฟล์อยู่ภายใน Budget ที่ทีมกำหนด

---

## Phase 3 — สร้างโมเดลห้องและอุปกรณ์

### TASK 3.1: สร้างโมเดลโครงสร้างห้อง A3

- [ ] สร้างพื้น ผนัง เพดาน ประตู และหน้าต่าง
- [ ] สร้างองค์ประกอบถาวรตามแบบแปลน
- [ ] ใส่ Material พื้นฐาน
- [ ] ตรวจสอบสัดส่วนกับขนาดจริง
- [ ] แยก Object ตามส่วนที่ทีมพัฒนาจำเป็นต้องเข้าถึง
- [ ] Optimize Geometry
- [ ] Export และทดสอบในแพลตฟอร์ม

---

### TASK 3.2: สร้างโมเดลโครงสร้างห้อง A4

- [ ] สร้างพื้น ผนัง เพดาน ประตู และหน้าต่าง
- [ ] สร้างองค์ประกอบถาวรตามแบบแปลน
- [ ] ใส่ Material พื้นฐาน
- [ ] ตรวจสอบสัดส่วนกับขนาดจริง
- [ ] แยก Object ตามส่วนที่ทีมพัฒนาจำเป็นต้องเข้าถึง
- [ ] Optimize Geometry
- [ ] Export และทดสอบในแพลตฟอร์ม

---

### TASK 3.3: สร้างอุปกรณ์ไฟฟ้าและ IoT

ดำเนินการตามลำดับความสำคัญ:

1. อุปกรณ์ที่ต้องควบคุมผ่านแพลตฟอร์ม
2. อุปกรณ์ที่ต้องแสดงสถานะ
3. อุปกรณ์สำคัญต่อภาพรวมของห้อง
4. อุปกรณ์ตกแต่งที่ไม่มี Interaction

สำหรับ Asset แต่ละชิ้น:

- [ ] ตรวจสอบขนาดและภาพ Reference
- [ ] สร้าง Low-poly Base Mesh
- [ ] สร้าง UV และ PBR Material
- [ ] แยกส่วนที่ต้องเปลี่ยนสถานะบนแพลตฟอร์ม
- [ ] ตั้งชื่อ Object และ Material
- [ ] Apply Transform
- [ ] Export `.glb`
- [ ] Validate และทดสอบโหลด
- [ ] บันทึก Version และสถานะการอนุมัติ

---

### TASK 3.4: ประกอบฉากห้อง A3 และ A4

- [ ] วาง Asset ตามตำแหน่งจริง
- [ ] ตรวจสอบ Scale และ Orientation
- [ ] ตรวจสอบ Object Hierarchy
- [ ] ตรวจสอบ Material และ Texture
- [ ] ตรวจสอบแสงเบื้องต้น
- [ ] ตรวจสอบจำนวน Polygon และ Draw Calls
- [ ] Export ฉากทดสอบ
- [ ] ตรวจสอบประสิทธิภาพบนอุปกรณ์เป้าหมาย

**ผลลัพธ์ที่ต้องได้**

- โมเดลห้อง A3
- โมเดลห้อง A4
- Asset Library ของอุปกรณ์
- ไฟล์ `.blend` ต้นฉบับ
- ไฟล์ `.glb` สำหรับใช้งานจริง

---

## Phase 4 — ศึกษาและทดสอบ Home Assistant API

### TASK 4.1: ศึกษา Home Assistant REST API

- [ ] ศึกษาการ Authentication ด้วย Bearer Token
- [ ] ทดสอบอ่านสถานะ Entity
- [ ] ทดสอบเรียก Service แบบไม่กระทบการทำงานจริง
- [ ] ทดสอบ Domain ที่จำเป็น เช่น `light`, `switch` และ `climate`
- [ ] บันทึก Request, Response และ Error ที่อาจเกิดขึ้น

**ตัวอย่าง Use Case**

```text
อ่านสถานะไฟ → เปิดไฟ → ตรวจสอบสถานะใหม่ → ปิดไฟ
```

**ผลลัพธ์ที่ต้องได้**

- `HOME_ASSISTANT_API_NOTES.md`
- ชุดคำขอทดสอบที่ไม่รวม Secret

---

### TASK 4.2: ศึกษา Home Assistant WebSocket API

- [ ] ศึกษาขั้นตอนเปิด Connection
- [ ] ศึกษาขั้นตอน Authentication
- [ ] Subscribe Event `state_changed`
- [ ] กรอง Event เฉพาะ Entity ของห้อง A3 และ A4
- [ ] ทดสอบรับสถานะเมื่อสั่งงานจาก Home Assistant
- [ ] ทดสอบรับสถานะเมื่อมีผู้กดสวิตช์จริง
- [ ] วางแนวทาง Reconnect เมื่อ Connection หลุด
- [ ] วางแนวทางดึง Current State ใหม่หลัง Reconnect

**Acceptance Criteria**

- แพลตฟอร์มได้รับสถานะจริงโดยไม่ต้อง Refresh
- เมื่อ Connection หลุด ระบบสามารถเชื่อมต่อใหม่ได้
- หลังเชื่อมต่อใหม่ สถานะบน 3D ตรงกับสถานะใน Home Assistant

---

### TASK 4.3: ตัดสินใจรูปแบบ Integration Architecture

เปรียบเทียบอย่างน้อย 2 แนวทาง:

#### แนวทาง A: แพลตฟอร์ม 3D เชื่อม Home Assistant โดยตรง

```text
Browser 3D → Home Assistant API → IoT
```

ข้อดี: Prototype เร็ว

ข้อควรระวัง: Token และสิทธิ์อาจถูกเปิดเผยใน Browser, จัดการ CORS และความปลอดภัยยากกว่า

#### แนวทาง B: ใช้ Backend Integration Layer

```text
Browser 3D → Platform Backend → Home Assistant → IoT
```

ข้อดี: ซ่อน Token, ตรวจสอบสิทธิ์, ทำ Audit Log, Rate Limit และ Mapping ได้ง่ายกว่า

**ข้อเสนอเริ่มต้น:** ใช้ Backend Integration Layer สำหรับระบบที่จะนำไปใช้งานจริง ส่วนการเชื่อมตรงใช้ได้เฉพาะ Prototype ในระบบทดสอบที่ควบคุมได้

**ผลลัพธ์ที่ต้องได้**

- Architecture Decision Record
- Data Flow Diagram
- Security Boundary

---

## Phase 5 — ออกแบบการ Mapping ระหว่าง 3D กับ Home Assistant

### TASK 5.1: กำหนด Device Mapping Schema

ข้อมูล Mapping ขั้นต่ำ:

```json
{
  "objectId": "DEV_A3_LIGHT_CEILING_01",
  "entityId": "light.a3_ceiling_01",
  "domain": "light",
  "roomId": "A3",
  "capabilities": ["turn_on", "turn_off"],
  "visualState": {
    "on": "emission_on",
    "off": "emission_off",
    "unavailable": "device_unavailable"
  }
}
```

- [ ] กำหนด Unique ID ของ 3D Object
- [ ] จับคู่กับ `entity_id`
- [ ] ระบุคำสั่งที่อนุญาต
- [ ] ระบุวิธีแสดงสถานะแต่ละค่า
- [ ] ระบุพฤติกรรมเมื่ออุปกรณ์ `unknown` หรือ `unavailable`
- [ ] ระบุว่า Mapping จะเก็บใน Code, JSON, Database หรือ Metadata ของ glTF

**ผลลัพธ์ที่ต้องได้**

- `DEVICE_MAPPING_SCHEMA.md`
- `config/device-mapping.example.json`

---

### TASK 5.2: กำหนด Visual State ของอุปกรณ์

ตัวอย่าง:

| สถานะจริง | การแสดงผลใน 3D |
|---|---|
| On | เปิด Emission หรือเปลี่ยน Material |
| Off | ปิด Emission |
| Unavailable | สีเทาและแสดงไอคอนเตือน |
| Loading | แสดง Indicator ระหว่างรอผล |
| Error | คืนสถานะเดิมและแจ้งข้อผิดพลาด |

- [ ] กำหนดสถานะไฟ
- [ ] กำหนดสถานะสวิตช์หรือปลั๊ก
- [ ] กำหนดสถานะแอร์
- [ ] กำหนดสถานะเซนเซอร์
- [ ] กำหนดสถานะ Offline/Unavailable

---

## Phase 6 — พัฒนา Integration Prototype

### TASK 6.1: สร้าง Read-only Prototype

เริ่มจากอ่านสถานะอย่างเดียวเพื่อลดความเสี่ยง

- [ ] โหลดฉาก 3D ตัวอย่าง
- [ ] เชื่อมต่อ Backend หรือ Home Assistant Test Environment
- [ ] อ่านสถานะของ Entity ตัวอย่างหนึ่งตัว
- [ ] เปลี่ยน Visual State ของโมเดลตามสถานะจริง
- [ ] Subscribe การเปลี่ยนสถานะแบบ Real-time
- [ ] แสดงสถานะการเชื่อมต่อของระบบ

**Acceptance Criteria**

- เมื่อสถานะใน Home Assistant เปลี่ยน โมเดล 3D เปลี่ยนตาม
- หน้า 3D ไม่ค้างเมื่อ Home Assistant ติดต่อไม่ได้
- ระบบแสดงสถานะ Unavailable ได้ชัดเจน

---

### TASK 6.2: เพิ่มการควบคุมอุปกรณ์หนึ่งตัว

- [ ] เลือกอุปกรณ์ทดสอบที่ปลอดภัย เช่น ไฟหนึ่งดวง
- [ ] คลิกโมเดลและเปิด Control Panel
- [ ] ส่งคำสั่งผ่าน Integration Layer
- [ ] แสดง Loading State ระหว่างรอคำตอบ
- [ ] รอ State Event ยืนยันผลจริง
- [ ] หากคำสั่งไม่สำเร็จ ให้แสดง Error และคืน UI สู่สถานะจริง
- [ ] บันทึก Audit Log ของคำสั่ง

**Acceptance Criteria**

- คำสั่งจาก 3D ส่งถึง Home Assistant ได้
- อุปกรณ์จริงเปลี่ยนสถานะ
- สถานะ 3D อัปเดตจากผลจริง ไม่ใช่เปลี่ยนล่วงหน้าอย่างเดียว
- ผู้ไม่มีสิทธิ์ไม่สามารถส่งคำสั่งได้

---

### TASK 6.3: ขยายไปยังอุปกรณ์ประเภทอื่น

ดำเนินการทีละ Domain:

- [ ] `light`
- [ ] `switch`
- [ ] `climate`
- [ ] `sensor` แบบ Read-only
- [ ] Domain อื่นที่บริษัทใช้งานจริง

สำหรับแต่ละ Domain ต้องกำหนด:

- Service ที่เรียก
- Payload ที่อนุญาต
- State และ Attributes ที่นำมาแสดง
- การ Validate ค่า
- Permission ของผู้ใช้
- Error Handling

---

## Phase 7 — Security, Reliability และ Performance

### TASK 7.1: ความปลอดภัย

- [ ] ไม่ฝัง Home Assistant Token ในไฟล์ JavaScript ฝั่ง Browser
- [ ] เก็บ Secret ใน Environment Variable หรือ Secret Manager
- [ ] ใช้ HTTPS/WSS
- [ ] ตรวจสอบสิทธิ์ผู้ใช้งานก่อนส่งคำสั่ง
- [ ] จำกัด Entity และ Service ที่อนุญาต
- [ ] Validate Payload ทุกครั้ง
- [ ] ทำ Rate Limiting
- [ ] บันทึก Audit Log ว่าใครสั่งอุปกรณ์ใดและเมื่อใด
- [ ] กำหนด Session Timeout และ Token Rotation

---

### TASK 7.2: Reliability

- [ ] รองรับ WebSocket Disconnect/Reconnect
- [ ] ทำ Initial State Synchronization
- [ ] กำหนด Timeout ของคำสั่ง
- [ ] ป้องกันการกดคำสั่งซ้ำถี่เกินไป
- [ ] แสดงสถานะ Stale Data
- [ ] รองรับ Entity `unknown` และ `unavailable`
- [ ] ออกแบบให้ระบบ 3D ยังเปิดดูพื้นที่ได้เมื่อ Home Assistant Offline

---

### TASK 7.3: ประสิทธิภาพของ 3D

- [ ] วัดขนาดรวมของ GLB และ Texture
- [ ] วัด FPS บนอุปกรณ์เป้าหมาย
- [ ] ลด Polygon และ Draw Calls
- [ ] ใช้ Mesh Instancing สำหรับอุปกรณ์ที่ซ้ำกัน
- [ ] ใช้ Texture Compression หากแพลตฟอร์มรองรับ
- [ ] ใช้ Draco หรือ Meshopt เมื่อเหมาะสม
- [ ] ใช้ LOD สำหรับ Asset ที่ซับซ้อน
- [ ] ทดสอบเวลาโหลดครั้งแรก

---

## Phase 8 — Testing และ User Acceptance Test

### TASK 8.1: ทดสอบโมเดล 3D

- [ ] ตรวจสอบสเกลและตำแหน่ง
- [ ] ตรวจสอบชื่อ Object
- [ ] ตรวจสอบ Material และ Texture
- [ ] ตรวจสอบ Pivot และ Transform
- [ ] ตรวจสอบไฟล์เสียหรือ Texture หาย
- [ ] ตรวจสอบประสิทธิภาพ

---

### TASK 8.2: ทดสอบ Integration

- [ ] อ่านสถานะเริ่มต้น
- [ ] รับ State Change แบบ Real-time
- [ ] ส่งคำสั่งเปิด/ปิด
- [ ] ทดสอบคำสั่งไม่สำเร็จ
- [ ] ทดสอบ Home Assistant Offline
- [ ] ทดสอบ WebSocket หลุด
- [ ] ทดสอบ Entity Unavailable
- [ ] ทดสอบผู้ใช้ไม่มีสิทธิ์
- [ ] ทดสอบการกดคำสั่งพร้อมกันหลายครั้ง

---

### TASK 8.3: ทดสอบกับผู้ใช้งานจริง

- [ ] ให้พนักงานทดลองเลือกห้องและอุปกรณ์
- [ ] ทดลองอ่านสถานะจากโมเดล
- [ ] ทดลองสั่งงานอุปกรณ์ที่ได้รับอนุญาต
- [ ] เก็บ Feedback ด้านความเข้าใจและความง่ายในการใช้งาน
- [ ] บันทึก Bug และข้อเสนอแนะ
- [ ] จัดลำดับสิ่งที่ต้องแก้ก่อนส่งมอบ

---

## Phase 9 — Documentation และส่งมอบ

### TASK 9.1: จัดทำเอกสาร

- [ ] คู่มือการสร้างและ Export Asset จาก Blender
- [ ] รายการ Asset และ Version
- [ ] เอกสาร Architecture และ Data Flow
- [ ] เอกสาร Home Assistant Integration
- [ ] Device Mapping Specification
- [ ] คู่มือการตั้งค่า Environment
- [ ] คู่มือทดสอบระบบ
- [ ] คู่มือผู้ใช้งาน
- [ ] Known Issues และข้อจำกัด

---

### TASK 9.2: เตรียม Demo และส่งมอบ

- [ ] เตรียม Demo Scenario
- [ ] แสดงสถานะอุปกรณ์จริงบนโมเดล
- [ ] สั่งเปิด/ปิดอุปกรณ์ผ่านโมเดล 3D
- [ ] แสดงกรณีอุปกรณ์ Offline
- [ ] ตรวจสอบไฟล์ต้นฉบับและไฟล์ Export
- [ ] สำรองไฟล์และกำหนด Version
- [ ] ส่งมอบ Source, Assets และ Documentation

---

# 3. ลำดับการเริ่มงานที่แนะนำ

ให้เริ่มตามลำดับนี้ก่อนลงมือปั้น Asset จำนวนมาก:

```text
1. ยืนยัน Requirement และ Deliverables
2. ศึกษา Tech Stack และข้อจำกัดของแพลตฟอร์ม 3D
3. สำรวจห้อง A3/A4 และทำ Asset Inventory
4. สำรวจ Home Assistant Entities
5. กำหนด Blender Standard และ Naming Convention
6. สร้าง Prototype Asset หนึ่งชิ้น
7. ทดสอบนำ GLB เข้าแพลตฟอร์ม
8. ทดสอบอ่านสถานะ Home Assistant แบบ Read-only
9. ทำ Mapping ระหว่าง 3D Object กับ Entity
10. ทดสอบสั่งงานอุปกรณ์ที่ปลอดภัยหนึ่งตัว
11. เมื่อ Prototype ผ่าน จึงขยายการปั้นและ Integration ทั้งห้อง
```

---

# 4. Milestones ที่แนะนำ

## Milestone 1 — Discovery Complete

- Requirement ผ่านการยืนยัน
- ทราบ Tech Stack ของแพลตฟอร์ม 3D
- มีแบบแปลนห้องและ Asset Inventory
- มี Home Assistant Entity Inventory

## Milestone 2 — 3D Pipeline Validated

- มี Blender Standard
- Prototype Asset โหลดเข้าแพลตฟอร์มสำเร็จ
- Scale, Material, Naming และ Interaction ผ่านการตรวจสอบ

## Milestone 3 — IoT Read-only Integration

- แพลตฟอร์มอ่านสถานะ Home Assistant ได้
- โมเดลเปลี่ยนตามสถานะจริงแบบ Real-time
- รองรับ Reconnect และ Unavailable State

## Milestone 4 — IoT Control Prototype

- คลิกโมเดลและสั่งงานอุปกรณ์จริงหนึ่งตัวได้
- มี Permission, Validation, Error Handling และ Audit Log

## Milestone 5 — A3/A4 Integrated Demo

- ห้อง A3 และ A4 พร้อมใช้งานในแพลตฟอร์ม
- อุปกรณ์เป้าหมายถูก Mapping ครบ
- ผ่าน Integration Test และ User Acceptance Test
- เอกสารและไฟล์ต้นฉบับพร้อมส่งมอบ

---

# 5. คำถามที่ต้องหาคำตอบก่อนเริ่ม Implementation

1. แพลตฟอร์ม 3D ใช้ Framework หรือ Engine อะไร?
2. ใครเป็นผู้ดูแล Source Code และ Integration Layer?
3. ต้องส่งไฟล์ `.blend`, `.glb` หรือทั้งสองแบบ?
4. มี Polygon, Texture และ File-size Budget หรือไม่?
5. ระบบพิกัด แกน และหน่วยของแพลตฟอร์มเป็นแบบใด?
6. ห้อง A3 และ A4 มีแบบแปลนหรือขนาดจริงครบหรือไม่?
7. อุปกรณ์ IoT ใดต้องควบคุม และอุปกรณ์ใดแสดงสถานะอย่างเดียว?
8. Home Assistant มี Test Environment หรือไม่?
9. สามารถสร้าง Development Account/Token แบบจำกัดสิทธิ์ได้หรือไม่?
10. แพลตฟอร์มมีระบบ Login และ Permission อยู่แล้วหรือไม่?
11. การเชื่อม Home Assistant จะผ่าน Backend ของแพลตฟอร์มหรือเชื่อมโดยตรง?
12. ระบบต้องใช้งานเฉพาะเครือข่ายภายในหรือเปิดใช้งานจากภายนอกด้วย?
13. ผู้ใช้ต้องควบคุมอุปกรณ์ประเภทใดบ้าง เช่น ไฟ แอร์ ปลั๊ก หรือม่าน?
14. ต้องเก็บ Audit Log หรือประวัติการสั่งงานหรือไม่?
15. เกณฑ์การยอมรับงานและวันส่งมอบของแต่ละ Milestone คือเมื่อใด?

---

# 6. สถานะเริ่มต้นของโครงการ

| งาน | สถานะ |
|---|---|
| สรุปภาพรวมและแบ่ง Task | เสร็จแล้ว |
| ยืนยัน Requirement | ยังไม่เริ่ม |
| ศึกษาแพลตฟอร์ม 3D | ยังไม่เริ่ม |
| สำรวจห้อง A3/A4 | ยังไม่เริ่ม |
| สำรวจ Home Assistant Entities | ยังไม่เริ่ม |
| กำหนด Blender Standard | ยังไม่เริ่ม |
| Prototype 3D Asset | ยังไม่เริ่ม |
| Prototype Home Assistant Integration | ยังไม่เริ่ม |

> หมายเหตุ: รายการงานนี้เป็นแผนตั้งต้น ต้องปรับอีกครั้งหลังจากได้รับข้อมูล Tech Stack, ข้อจำกัดของแพลตฟอร์ม 3D, แบบแปลนห้อง และรายการ Entity จาก Home Assistant
