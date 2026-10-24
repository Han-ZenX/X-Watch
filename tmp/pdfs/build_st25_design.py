from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs'/'ST25R3916-AQWT_NFC功能电路设计_矢量版.pdf'
pdfmetrics.registerFont(TTFont('CN','C:/Windows/Fonts/msyh.ttf'))
W,H=841.89,595.28
c=canvas.Canvas(str(OUT),pagesize=(W,H))
c.setTitle('ST25R3916-AQWT NFC功能电路设计');c.setAuthor('X-Watch / Codex')
INK='#172D40'; BLUE='#087D92'; GRAY='#596B79'; LIGHT='#E8EFF3'; RED='#A23F2A'
def text(x,y,s,size=9,color=INK,align='left'):
    c.setFillColor(HexColor(color));c.setFont('CN',size)
    {'left':c.drawString,'right':c.drawRightString,'center':c.drawCentredString}[align](x,y,s)
def line(x1,y1,x2,y2,color=INK,w=1):
    c.setStrokeColor(HexColor(color));c.setLineWidth(w);c.line(x1,y1,x2,y2)
def dot(x,y):
    c.setFillColor(HexColor(INK));c.circle(x,y,2,fill=1,stroke=0)
def ground(x,y):
    line(x,y,x,y-5)
    for off,half in [(5,8),(9,5),(13,2)]:line(x-half,y-off,x+half,y-off)
def nc(x,y):
    line(x-3,y-3,x+3,y+3,RED);line(x-3,y+3,x+3,y-3,RED)
def cv(x,y,top,bottom,label='',value=''):
    line(x,top,x,y+4);line(x-8,y+4,x+8,y+4);line(x-8,y-4,x+8,y-4);line(x,y-4,x,bottom)
    if label:text(x+12,y+6,label,8)
    if value:text(x+12,y-8,value,8)
def ch(x,y,left,right,label,value):
    line(left,y,x-4,y);line(x-4,y-8,x-4,y+8);line(x+4,y-8,x+4,y+8);line(x+4,y,right,y)
    text(x,y+20,label,9,align='center');text(x,y-23,value,9,align='center')
def rh(x,y,left,right,label,value):
    line(left,y,x-12,y);line(x+12,y,right,y);c.setStrokeColor(HexColor(INK));c.rect(x-12,y-4,24,8,fill=0,stroke=1)
    text(x,y+20,label,9,align='center');text(x,y-23,value,9,align='center')
def lh(x,y,left,right,label,value):
    line(left,y,x-20,y);line(x+20,y,right,y)
    p=c.beginPath();p.moveTo(x-20,y)
    for i in range(4):
        xx=x-20+i*10;p.curveTo(xx,y+12,xx+10,y+12,xx+10,y)
    c.setStrokeColor(HexColor(INK));c.drawPath(p)
    text(x,y+25,label,9,align='center');text(x,y-22,value,9,align='center')
def box(x,y,w,h):
    c.setFillColor(HexColor('#F4F8FA'));c.setStrokeColor(HexColor(LIGHT));c.roundRect(x,y,w,h,5,fill=1,stroke=1)
def base(n,title,sub):
    c.setFillColor(HexColor(INK));c.rect(0,H-16,W,16,fill=1,stroke=0)
    text(36,H-55,title,22);text(37,H-77,sub,10,GRAY)
    line(36,44,W-36,44,LIGHT)
    text(36,26,'X-Watch  /  ST25R3916-AQWT  /  参考设计 V1.0  /  2026-10-24',8,GRAY)
    text(W-36,26,f'{n:02d} / 06',9,GRAY,'right')
def para(x,y,s,width=770,size=10,leading=18):
    row=''
    for char in s:
        if char=='\n' or pdfmetrics.stringWidth(row+char,'CN',size)>width:
            text(x,y,row,size);y-=leading;row='' if char=='\n' else char
        else:row+=char
    if row:text(x,y,row,size);y-=leading
    return y
def section(x,y,s):text(x,y,s,14,BLUE)
def table(x,y,widths,rows,rowh=29,size=9):
    for i,row in enumerate(rows):
        if i==0:
            c.setFillColor(HexColor(LIGHT));c.rect(x,y-rowh,sum(widths),rowh,fill=1,stroke=0)
        xx=x
        for width,s in zip(widths,row):
            assert pdfmetrics.stringWidth(str(s),'CN',size)<=width-14,(s,width)
            text(xx+7,y-rowh+10,str(s),size);xx+=width
        line(x,y-rowh,x+sum(widths),y-rowh,LIGHT,.6);y-=rowh
    return y

base(1,'NFC 芯片与主控 · 全引脚连接图','适用 ST25R3916-AQWT（非 B 版） | 3.3 V、四线 SPI、固定匹配、内部负载调制')
box(310,130,230,350)
text(425,461,'U1  ST25R3916-AQWT',12,align='center')
left=[('1','VDD_IO','+3V3_NFC'),('2','CSO','NC：禁用电容传感'),('3','VDD_D','VDD_D_OUT → P2'),('4','XTO','XTAL_O → P2'),('5','XTI','XTAL_I → P2'),('6','GND_D','GND'),('7','VDD_A','VDD_A_OUT → P2'),('8','VDD','+3V3_NFC'),('9','VDD_RF','VDD_RF_OUT → P2'),('10','VDD_TX','+3V3_NFC'),('11','VDD_AM','VDD_AM_OUT → P2'),('12','GND_DR1','GND'),('13','RFO1','RF_OUT1 → P3'),('14','VDD_DR','VDD_RF_OUT（与 9 脚相连）'),('15','RFO2','RF_OUT2 → P3'),('16','GND_DR2','GND')]
right=[('32','MISO/SDA','NFC_MISO → MCU'),('31','MOSI','NFC_MOSI ← MCU'),('30','SCLK/SCL','NFC_SCK ← MCU'),('29','BSS','NFC_CS_N ← MCU / R1'),('28','MCU_CLK','NFC_CLK → MCU 时钟输入'),('27','IRQ','NFC_IRQ → MCU 唤醒输入'),('26','GND_A','GND'),('25','CSI','NC：禁用电容传感'),('24','AGDC','AGDC_BYP → P2'),('23','RFI2','RF_IN2 ← P3'),('22','RFI1','RF_IN1 ← P3'),('21','VSS','GND'),('20','I2C_EN','GND：选择 SPI'),('19','AAT_B','NC：固定匹配'),('18','AAT_A','NC：固定匹配'),('17','EXT_LM','NC：内部负载调制')]
for i,(pin,name,net) in enumerate(left):
    y=438-i*19;line(270,y,310,y);text(290,y+4,pin,8,align='center');text(320,y-3,name,9)
    text(260,y-3,net,9,BLUE if net!='GND' else INK,'right')
    if net.startswith('NC'):nc(270,y)
for i,(pin,name,net) in enumerate(right):
    y=438-i*19;line(540,y,580,y);text(560,y+4,pin,8,align='center');text(530,y-3,name,9,align='right')
    text(590,y-3,net,9,BLUE if net!='GND' else INK)
    if net.startswith('NC'):nc(580,y)
line(425,130,425,106);ground(425,106);text(440,112,'33 EP → GND',9)
para(36,83,'同名网络电气相连；P2/P3 为本文件页码。引脚电气属性虽已在库中设为无源，实际接线仍按原厂功能区分输入、输出。',size=9)
para(36,65,'本文件为打样参考，未完成硬件验证。不能保证复制现有门禁卡，也不包含支付安全单元或交通卡发行功能。',size=9)
c.showPage()

base(2,'电源去耦与 27.12 MHz 时钟','保留内部稳压器 | 稳压输出只接本芯片所需负载与电容，不并入外部 3.3 V')
cards=[('外部主电源','U1.8  VDD','+3V3_NFC',[('C1','2.2 μF'),('C2','10 nF')]),('外部 TX 电源','U1.10  VDD_TX','+3V3_NFC',[('C3','4.7 μF'),('C4','10 nF')]),('数字接口电源','U1.1  VDD_IO','+3V3_NFC',[('C5','10 nF')]),('数字稳压输出','U1.3  VDD_D','VDD_D_OUT',[('C6','2.2 μF'),('C7','10 nF')]),('模拟稳压输出','U1.7  VDD_A','VDD_A_OUT',[('C8','2.2 μF'),('C9','10 nF')]),('RF 稳压 / 驱动输入','U1.9 + U1.14','VDD_RF_OUT',[('C10','4.7 μF'),('C11','10 nF')]),('AM 稳压输出','U1.11  VDD_AM','VDD_AM_OUT',[('C12','2.2 μF'),('C13','10 nF')]),('模拟参考旁路','U1.24  AGDC','AGDC_BYP',[('C14','1 μF'),('C15','10 nF')])]
for i,(title,pin,net,caps) in enumerate(cards):
    x=36+(i%4)*195;top=490-(i//4)*132
    box(x,top-120,185,120);text(x+9,top-17,title,10,BLUE);text(x+9,top-34,pin,9)
    text(x+9,top-49,net,8,GRAY)
    xs=[x+30,x+112] if len(caps)==2 else [x+65]
    line(xs[0],top-59,xs[-1],top-59)
    for xx,(ref,value) in zip(xs,caps):
        dot(xx,top-59);cv(xx,top-78,top-59,top-100,ref,value);ground(xx,top-100)
section(36,211,'Y1：无源晶体，不是 13.56 MHz 晶体')
line(65,159,213,159);line(267,159,385,159)
line(213,146,213,172);line(267,146,267,172)
c.setStrokeColor(HexColor(INK));c.rect(222,147,36,24,fill=0,stroke=1)
text(66,179,'U1.4 XTO',9);text(315,179,'U1.5 XTI',9)
text(240,188,'Y1 27.12 MHz',10,BLUE,'center')
cv(150,124,159,99,'C16','10 pF*');dot(150,159);ground(150,99)
cv(330,124,159,99,'C17','10 pF*');dot(330,159);ground(330,99)
para(450,204,'VDD 与 VDD_TX 由同一稳压 3.3 V 供电；VDD_IO 也采用同一电源域。电容就近接地。',width=350,size=10)
para(450,153,'* 晶体电容为起点：CL ≈ C16×C17/(C16+C17)+Cstray。两只 10 pF、寄生 3 pF 对应 CL≈8 pF。按晶体规格复核。',width=350,size=10)
para(450,83,'晶体的 ESR、驱动等级及起振裕量按数据手册核验；金属外壳的接地端按晶体厂商要求处理。',width=350,size=9)
c.showPage()

base(3,'射频通道 · 差分固定匹配网络','原创简化拓扑：去除可变电容和外部调制支路 | RF 元件值为调试起点，非整机定值')
for y,suffix,out,emc,series,parallel,rd in [(395,'A','RF_OUT1','C18','C20','C22','R2'),(265,'B','RF_OUT2','C19','C21','C23','R3')]:
    text(36,y+6,out,9,BLUE);lh(155,y,90,225,'L1' if suffix=='A' else 'L2','270 nH*')
    dot(225,y);cv(225,y-40,y,y-60,emc,'680 pF*');ground(225,y-60)
    ch(335,y,225,450,series,'100 pF*');dot(450,y)
    cv(450,y-40,y,y-60,parallel,'56 pF*');ground(450,y-60)
    text(492,y+8,f'RF_{suffix}',10,BLUE)
    rh(590,y,450,735,rd,'2.4 Ω*')
line(735,395,735,385);line(735,275,735,265)
p=c.beginPath();p.moveTo(735,385)
for i in range(5):
    yy=385-i*22;p.curveTo(763,yy,763,yy-22,735,yy-22)
c.setStrokeColor(HexColor(INK));c.drawPath(p)
text(738,424,'ANT1',11,BLUE);text(690,229,'PCB / FPC 线圈',9)
text(690,212,'无直流接地端',9)
section(36,190,'接收分压：两路保持对称，必须连接 RFI1 / RFI2')
for x,net,rx,ref1,ref2 in [(36,'RF_A','RF_IN1 → U1.22','C24','C25'),(440,'RF_B','RF_IN2 → U1.23','C26','C27')]:
    y=140;text(x,y+7,net,9,BLUE);ch(x+102,y,x+48,x+210,ref1,'10 pF*');dot(x+210,y)
    text(x+222,y-3,rx,9,BLUE);cv(x+210,111,y,90,ref2,'180 pF*');ground(x+210,90)
para(36,475,'RFO1/2 经滤波、匹配及阻尼驱动线圈；RF_A/B 是串联匹配电容之后、阻尼电阻之前的取样点。',size=10)
para(36,452,'* 参考量级来自 NFC06A1，但移除 AAT 后不能原样视为已匹配。需测线圈参数并重新计算 C18~C27、L1/L2、R2/R3。',size=9)
para(36,60,'接收电容分压的一阶比例约 10/(10+180)=1/19；最终须核查强外场下 RFI 峰值、电容耐压及目标模式灵敏度。',size=9)
c.showPage()

base(4,'器件清单与装配约束','先确认器件与网络，再定天线尺寸及匹配值 | DNP 表示预留但不装配')
table(36,488,[175,225,370],[('位号','规格 / 数量','用途及装配要求'),('U1','ST25R3916-AQWT ×1','VFQFPN32；按库封装检查 1 脚、EP 及焊盘'),('Y1','27.12 MHz 无源晶体 ×1','负载电容按所选型号；检查起振与频差'),('C1/C6/C8/C12','2.2 μF ×4','X5R/X7R，≥10 V，0402 或 0603'),('C3/C10','4.7 μF ×2','X5R/X7R，≥10 V；核查直流偏压后有效容量'),('C14','1 μF ×1','X5R/X7R，≥10 V；AGDC 专用旁路'),('C2/C4/C5/C7/C9/C11/C13/C15','10 nF ×8','X7R，≥10 V；贴近对应引脚'),('C16/C17','10 pF ×2，待核定','C0G/NP0；晶体负载电容'),('C18/C19','680 pF ×2，待调','C0G/NP0，初选 ≥50 V；EMC 滤波'),('C20/C21；C22/C23','100 pF ×2；56 pF ×2，待调','C0G/NP0，初选 ≥50 V；固定匹配'),('C24/C26；C25/C27','10 pF ×2；180 pF ×2，待调','C0G/NP0，初选 ≥50 V；接收分压'),('L1/L2','270 nH ×2，待调','RF 高 Q 电感；核查 SRF、电流和封装损耗'),('R1；R2/R3','100 kΩ ×1；2.4 Ω ×2','R1：CS 默认上拉；R2/R3：阻尼，初选 0603'),('ANT1','定制 PCB / FPC 天线 ×1','测量 L、串联损耗与寄生；金属环境考虑磁片')],rowh=27,size=8)
section(36,82,'装配边界')
para(36,62,'本版不装 AAT、外部负载调制及电容传感支路。只安装一个完整的射频匹配方案；器件耐压、电流与功率须以实测峰值复核。',size=9)
c.showPage()

base(5,'主控接入、固件与门禁功能边界','四线 SPI 基线 | 透明模式预留的引脚能力须在选择 MCU 管脚时确认')
section(36,488,'01  主控接口与默认状态')
table(36,474,[180,220,370],[('U1 信号','主控连接','要求'),('BSS / 29','GPIO 输出 NFC_CS_N','R1=100 kΩ 上拉到 +3V3_NFC；上电保持高'),('SCLK / 30；MOSI / 31','SPI 时钟；SPI 输出','SPI Mode 1：CPOL=0，CPHA=1；先低速调通'),('MISO / 32','SPI 输入 + 可切换捕获输入','透明模式为接收数据；不能只预留普通 SPI 功能'),('IRQ / 27','可唤醒的中断输入','CMOS 输出，高电平有效；读取中断状态后清除'),('MCU_CLK / 28','定时器 / 外部同步时钟输入','透明模式必需；核查主控同步采样及引脚复用'),('I2C_EN / 20','直接接 GND','固定 SPI；不是 3.3 V 电平的模式控制口')],rowh=29,size=9)
section(36,245,'02  固件启动与节电')
para(36,222,'上电后按 DS12484 Rev8 §4.1 完成初始化，包括其要求的 FC / 04 / 10 测试寄存器帧；Set default 后亦应执行。配置 3.3 V 模式，再进行稳压调整及晶体稳定检查。',size=10)
para(36,171,'首版先验证 RFAL 的标准读写与卡模拟，再接入上层应用。刷门禁以监听外部读头为主，不持续开启读卡轮询；记录待机、唤醒与刷卡三种状态的整板电流。',size=10)
para(36,143,'内部负载调制：按 AN5276 §3.1.1 启用 lm_dri、禁用 lm_ext，并调节 pt_res / ptm_res；固定匹配不执行 AAT。',size=9)
section(36,117,'03  “能模拟”与“能开门”之间仍有协议条件')
para(36,94,'本电路提供 NFC 射频硬件。门禁还需匹配卡类型、UID 规则、应用数据与认证。MIFARE Classic 透明模式涉及额外时序 / 编码实现，不能视为已由本图完成。',size=10)
para(36,58,'原理图库中“全部引脚无源”只影响 ERC，不改变芯片电气功能；供电输出误接等问题仍须人工检查。',size=9)
c.showPage()

base(6,'PCB 布局、调谐与验收','使用电池、屏幕、外壳和表带金属件的最终装配状态验证，避免只在裸板上定值')
section(36,486,'01  布局重点')
para(36,462,'U1.6、12、16、21、26 与 EP33 接连续地平面；EP 下布接地散热过孔并控制焊膏。RFO、匹配网络与天线馈点保持对称、短连接。')
para(36,427,'去耦电容紧贴对应引脚，优先形成短回流。晶体靠近 XTI/XTO；SPI 与开关电源远离 RFI。天线及其投影区域避免连续铜面和金属遮挡；磁片安装后重新调谐。')
section(36,377,'02  按结果推进样机验收')
table(36,361,[42,230,498],[('序号','操作','通过条件 / 留存结果'),('1','断电检查与限流上电','各电源无短路；稳压输出未被外部 3.3 V 强灌；EP 接地'),('2','验证 SPI、时钟、中断','能读取芯片标识 / 寄存器；起振稳定；IRQ 能唤醒主控'),('3','测天线 L / R / SRF 并计算匹配','用 AN5276 / 匹配工具迭代；记录最终 L/C/R 与网络阻抗'),('4','验证弱场、强场及多方向耦合','RFI 电压及射频元件应力在限值内；能稳定激活及通信'),('5','实际门禁协议与整机功耗','受控测试门禁能够认证；记录成功率、距离、耗时及电流')],rowh=29,size=9)
section(36,150,'03  原厂依据（点击条目打开）')
refs=[('[1] ST DS12484 Rev8，2023-05：引脚表、供电、SPI、透明模式和初始化。','https://www.st.com/resource/en/datasheet/st25r3916.pdf'),('[2] ST X-NUCLEO-NFC06A1：电源、晶体与差分匹配参考；本方案已简化。','https://www.st.com/resource/en/schematic_pack/x-nucleo-nfc06a1_schematic.pdf'),('[3] ST AN5276 Rev6，2023-05：天线测量、内部负载调制、匹配及验证。','https://www.st.com/resource/en/application_note/an5276-antenna-design-for-st25r391616b-st25r391717b-st25r3918-st25r3919b-and-st25r392020b-devices-stmicroelectronics.pdf')]
for i,(s,url) in enumerate(refs):
    y=126-i*21;text(36,y,s,9,BLUE);c.linkURL(url,(36,y-2,805,y+12),relative=0)
text(36,59,'状态：文档接线与排版已核对；未进行样机电测、射频仿真或门禁兼容性测试。',9,GRAY)
c.showPage();c.save()
reader=PdfReader(OUT)
assert len(reader.pages)==6
assert sum(len(page.images) for page in reader.pages)==0
assert all(len(page.extract_text())>200 for page in reader.pages)
assert {int(p[0]) for p in left+right} == set(range(1,33))
assert len(left+right)==32
print(OUT)
print('Verified: 6 pages; vector drawing only; searchable text; reference links included')

