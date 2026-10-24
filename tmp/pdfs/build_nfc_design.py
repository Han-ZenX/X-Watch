from pathlib import Path
import math
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs'/'NT3H1101_NFC功能电路设计_矢量版.pdf'
OUT.parent.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('CN','C:/Windows/Fonts/msyh.ttf'))
W,H=841.89,595.28
c=canvas.Canvas(str(OUT),pagesize=(W,H))
c.setTitle('NT3H1101W0FHKH NFC功能电路设计'); c.setAuthor('X-Watch / Codex')
INK='#172D40'; BLUE='#087D92'; GRAY='#596B79'; LIGHT='#E8EFF3'; RED='#A23F2A'
def txt(x,y,s,size=10,color=INK):
    c.setFillColor(HexColor(color));c.setFont('CN',size);c.drawString(x,y,s)
def line(x1,y1,x2,y2,color=INK,w=1):
    c.setStrokeColor(HexColor(color));c.setLineWidth(w);c.line(x1,y1,x2,y2)
def dot(x,y):
    c.setFillColor(HexColor(INK));c.circle(x,y,2,fill=1,stroke=0)
def ground(x,y):
    line(x,y,x,y-7)
    for dy,half in [(7,10),(11,6),(15,2)]:line(x-half,y-dy,x+half,y-dy)
def nc(x,y):
    line(x-4,y-4,x+4,y+4,RED);line(x-4,y+4,x+4,y-4,RED)
def cap(x,y,top,bottom,label,value):
    line(x,top,x,y+4);line(x-10,y+4,x+10,y+4);line(x-10,y-4,x+10,y-4);line(x,y-4,x,bottom)
    txt(x+15,y+7,label,9);txt(x+15,y-9,value,9)
def resistor(x,top,bottom,label,value):
    mid=(top+bottom)/2
    line(x,top,x,mid+13);line(x,mid-13,x,bottom)
    c.setStrokeColor(HexColor(INK));c.rect(x-4,mid-13,8,26,stroke=1,fill=0)
    txt(x+9,mid+4,label,8);txt(x+9,mid-9,value,8)
def base(n,title,subtitle):
    c.setFillColor(HexColor(INK));c.rect(0,H-16,W,16,fill=1,stroke=0)
    txt(36,H-55,title,23);txt(37,H-77,subtitle,10,GRAY)
    line(36,44,W-36,44,LIGHT)
    txt(36,26,'X-Watch  /  NT3H1101W0FHKH  /  参考设计 V1.0  /  2026-10-24',8,GRAY)
    txt(W-105,26,f'{n:02d} / 04',9,GRAY)
def section(x,y,s):txt(x,y,s,14,BLUE)
def para(x,y,s,width=760,size=10,leading=18):
    row=''
    for ch in s:
        if ch=='\n' or pdfmetrics.stringWidth(row+ch,'CN',size)>width:
            txt(x,y,row,size);y-=leading;row='' if ch=='\n' else ch
        else:row+=ch
    if row:txt(x,y,row,size);y-=leading
    return y
def table(x,y,widths,rows,rowh=31):
    for i,row in enumerate(rows):
        xx=x
        if i==0:c.setFillColor(HexColor(LIGHT));c.rect(x,y-rowh,sum(widths),rowh,fill=1,stroke=0)
        for width,s in zip(widths,row):
            txt(xx+8,y-rowh+11,str(s),9);xx+=width
        line(x,y-rowh,x+sum(widths),y-rowh,LIGHT,.6);y-=rowh
    return y

base(1,'NFC 功能电路 · 主原理图','3.3 V 主控接口 + 无源 NFC 标签 | 电气连接按引脚号识别，符号位置与截图可不同')
# Power and digital side
c.setFillColor(HexColor('#F4F8FA'));c.roundRect(330,235,165,150,8,fill=1,stroke=0)
c.setStrokeColor(HexColor(INK));c.roundRect(330,235,165,150,8,fill=0,stroke=1)
txt(350,364,'U1  NT3H1101',12);txt(355,342,'XQFN8 / SOT902-3',8,GRAY)
for y,p,name in [(325,'1','LA'),(270,'8','LB')]:
    line(300,y,330,y);txt(309,y+5,p,9);txt(340,y-4,name,10)
for y,p,name in [(325,'3','SCL'),(290,'5','SDA'),(255,'4','FD')]:
    line(495,y,760,y);txt(500,y+5,p,8);txt(451,y-4,name,10)
    txt(765,y-3,'MCU_'+name if name!='FD' else 'MCU_IRQ',9)
for x,y,r,v in [(560,325,'R1','4.7 kΩ'),(630,290,'R2','4.7 kΩ'),(700,255,'R3','10 kΩ')]:
    resistor(x,430,y,r,v);dot(x,y);txt(x-17,443,'+3V3',9,BLUE)
line(412,385,412,465);txt(421,394,'6 VCC',9);txt(394,477,'+3V3',10,BLUE)
line(285,450,412,450);dot(412,450);cap(285,428,450,407,'C1','100 nF');ground(285,407)
line(350,235,350,188);txt(335,219,'2',9);txt(354,196,'VSS',9);ground(350,188)
line(400,235,400,202);txt(407,214,'EP / 9',9);nc(400,202);txt(414,190,'NC：不接地',9,RED)
line(470,235,470,220);line(470,220,620,220);nc(620,220);txt(488,205,'7 VOUT：默认悬空',9)
txt(622,184,'取能变体见第 3 页',8,GRAY)
# Antenna and parallel tuning
line(110,325,300,325);line(110,270,300,270)
line(110,325,110,319);line(110,276,110,270)
p=c.beginPath();p.moveTo(110,319)
for i in range(4):
    yy=319-i*10.75;p.curveTo(92,yy,92,yy-10.75,110,yy-10.75)
c.setStrokeColor(HexColor(INK));c.drawPath(p)
txt(44,346,'ANT1',11,BLUE);txt(42,248,'PCB / FPC 线圈',9);txt(42,232,'电感实测后配容',9,GRAY)
cap(225,297.5,325,270,'CT','DNP');dot(225,325);dot(225,270)
txt(164,356,'调谐电容跨 LA / LB',9,GRAY)
section(38,146,'连接要点')
para(38,124,'同名 +3V3 网络相连；所有 GND 与主控共地。R1/R2 若主板已有上拉则按并联等效值处理，避免重复装配。',size=10)
para(38,103,'CT 默认不装（DNP），不能预先指定最终容量。ANT1 两端均不接地；EP 按原厂要求悬空。[1 §7.2]',size=10)
para(38,82,'本页为原创矢量参考电路，尚未完成样机射频验证。芯片作为标签响应手机，不支持主动读卡或支付安全功能。',size=10)
c.showPage()

base(2,'引脚、器件与接口约束','装配基线 | 用户截图中的 EP=9 是库符号编号，原厂功能引脚为 1 至 8')
section(36,490,'01  引脚核对 [1 §7.2]')
table(36,476,[46,64,280],[( '脚号','名称','本设计连接'),('1','LA','ANT1 一端；CT 上端'),('2','VSS','系统 GND'),('3','SCL','MCU_SCL；R1 上拉 +3V3'),('4','FD','MCU_IRQ；R3 上拉 +3V3'),('5','SDA','MCU_SDA；R2 上拉 +3V3'),('6','VCC','+3V3；C1 去耦至 GND'),('7','VOUT','默认 NC；不连接 +3V3'),('8','LB','ANT1 另一端；CT 下端'),('EP','中心焊盘','悬空；不布接地过孔')],rowh=29)
section(450,490,'02  建议 BOM（工程选值）')
table(450,476,[65,126,155],[('位号','规格','装配说明'),('U1','NT3H1101W0FHKH','核对封装方向'),('C1','100 nF / 10 V','X7R，0402，必装'),('R1/R2','4.7 kΩ / 1%','0402，各 1 只'),('R3','10 kΩ / 1%','0402，1 只'),('CT','C0G / ≥25 V','0402，默认 DNP'),('ANT1','PCB 或 FPC 天线','电感 / Q 值实测')],rowh=29)
section(450,234,'03  主控接入')
para(450,212,'VCC 采用系统稳压 3.3 V，不接锂电池原始电压。FD 为开漏输出，连接可唤醒的 GPIO 输入。[1]',width=340)
para(450,159,'I²C 先用 100 kHz 调通。推荐上拉值为起点，按实际总线电容及波形确认，再决定是否升速。',width=340)
para(36,115,'上拉估算：tr ≈ 0.8473 × Rp × Cbus。若 Cbus = 100 pF、Rp = 4.7 kΩ，则 tr ≈ 398 ns；用于 400 kHz 时应重新核查上升时间。',size=10)
para(36,79,'供电策略：基线要求主控 I/O、上拉和 U1 使用同一 3.3 V 电源域。若单独关断 U1 或主控，需另行验证隔离与反向供电。',size=10)
c.showPage()

base(3,'天线调谐与取能变体','天线尺寸、壳体和金属结构未给定，因此只给出计算起点与验证方法')
section(36,488,'01  谐振估算 [2 §2、§3]')
para(36,462,'一阶并联近似：f0 ≈ 1 / (2π√(Lant × Ctotal))；Ctotal ≈ Cic + Cpar + CT。高损耗与强耦合时需用实际测量修正。')
para(36,431,'Cic 典型值约 50 pF [1]。以下按 Cpar = 5 pF、f0 = 13.56 MHz 演示，均为估算，不是最终装配值。')
rows=[('假设线圈电感','所需总电容','CT 计算值','判断')]
for lu in [1.5,2.0,2.2,2.5]:
    ct=1/( (2*math.pi*13.56e6)**2 * lu*1e-6)*1e12
    rows.append((f'{lu:.1f} μH',f'{ct:.1f} pF',f'{ct-55:.1f} pF','负值时应减小电感' if ct<55 else '按实测选 C0G'))
table(36,410,[150,150,150,320],rows,29)
para(36,247,'调谐顺序：测裸线圈电感 / 损耗 → 装 U1 与外壳，用弱耦合探头或 VNA 测谐振 → 调整 CT / 匝数 → 多款手机验证读写。',size=10)
para(36,219,'13.56 MHz 用作本表的计算基准。最佳未加载谐振点可能偏移，应以整机耦合和实际读写表现确定。[2]')
section(36,178,'02  可选 VOUT 取能支路 [1 §8.6]')
line(70,125,325,125);txt(42,146,'U1.7 VOUT',10);cap(185,102,125,75,'CEH','180 nF / ±5%');ground(185,75);dot(185,125)
txt(330,122,'至低功耗负载测试点',9)
para(450,159,'替代第 1 页 VOUT 的 NC；CEH 至 GND。\n总输出电容须为 150~200 nF，计入负载侧电容和容差。',width=345,size=10)
para(450,103,'本变体仍由外部 3.3 V 供给 VCC。VOUT 不并入系统电源；负载能力须实测，负载增加可能缩短读距。',width=345,size=10)
c.showPage()

base(4,'布局要求与样机验收','从参考电路到可用整机 | 以下为工程建议，不代表已通过测试')
section(36,486,'01  PCB / FPC 布局')
para(36,461,'将 U1 放在天线馈点附近，LA/LB 走线短且靠近；CT 紧邻 LA/LB。C1 贴近 VCC/VSS，回流路径直接。')
para(36,431,'天线环路及其正反面投影区域避免大面积铜、屏蔽罩和金属件；不要用地平面填满线圈内部。馈线避免绕过开关电源。')
para(36,401,'手表中应将电池、屏幕、金属壳和表带扣纳入整机测试。必要时使用适用于 13.56 MHz 的磁性隔离片，并在装配状态重调。')
para(36,371,'预留天线测试连接与 CT 换料空间；正式产品应评估可触及导体的 ESD。射频保护件的寄生电容必须计入调谐。')
section(36,331,'02  验收步骤与合格条件')
table(36,313,[55,233,482],[('步骤','操作','合格条件 / 记录'),('1','上电前检查','VCC-GND 无短路；EP 与地无设计连接；ANT 两端不接地'),('2','3.3 V 上电 / I²C 访问','波形满足时序；能稳定读写可用用户区，写后回读一致'),('3','手机 NFC 靠近 / 移开','UID / NDEF 可读；FD 按所配置事件触发并释放'),('4','关闭整机电源后手机访问','验证 EEPROM 标签访问；不把无源访问等同于主控工作'),('5','装壳、多手机及方向测试','记录最大稳定读距、成功率、谐振点及最终 CT；再冻结 BOM')],29)
section(36,111,'03  设计依据与状态')
txt(36,91,'[1] NXP NT3H1101/NT3H1201，Rev.3.3，2015-07-15：§7.2、§8.6、§13。',9)
txt(36,74,'[2] NXP AN11276 NTAG Antenna Design Guide，Rev.1.8，2018-10-23：天线模型与调谐。',9)
c.linkURL('https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/2210/NT3H1101_NT3H1201_DS.pdf',(36,88,740,103),relative=0)
c.linkURL('https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/nfc/6155/1/AN11276.pdf',(36,71,780,85),relative=0)
c.showPage();c.save()
print(OUT)
