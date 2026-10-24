from pathlib import Path
import hashlib, re, json, math
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, Color, white
from pypdf import PdfReader, PdfWriter

ROOT=Path('G:/C++/X-Watch-master')
SRC=ROOT/'docs/references/Rev3.0/AG3335MMTK北斗芯片开发板及模块原理图pcb/AG3335M_V2_EVK/源文件/20200323A_AG3335M_EVK_V2_BOM.pdf'
TMP=ROOT/'tmp/pdfs/ag3335m-search'
OUT=ROOT/'docs/AG3335M_EVK芯片解析与手表应用评估_矢量版.pdf'
pdfmetrics.registerFont(TTFont('CN','C:/Windows/Fonts/msyh.ttf'))
pdfmetrics.registerFont(TTFont('CNB','C:/Windows/Fonts/msyhbd.ttf'))
W,H=841.89,595.28
INK=HexColor('#172C44'); BLUE=HexColor('#176C9E'); TEAL=HexColor('#087F80'); GRAY=HexColor('#586A7B')
LIGHT=HexColor('#EDF4F8'); LINE=HexColor('#CDDAE3'); AMBER=HexColor('#A26309'); RED=HexColor('#A34238')
c=canvas.Canvas(str(TMP/'analysis_body.pdf'),pagesize=(W,H))
c.setTitle('AG3335M EVK 芯片解析与智能手表应用评估')
c.setAuthor('X-Watch 技术分析')
page=0; chapters=[]; audit=[]

def para(txt,x,y,width=745,size=10.5,color=INK,leading=None,bold=False):
    style=ParagraphStyle('p',fontName='CNB' if bold else 'CN',fontSize=size,leading=leading or size*1.55,textColor=color,wordWrap='CJK',spaceAfter=0)
    p=Paragraph(txt,style); _,h=p.wrap(width,5000); p.drawOn(c,x,H-y-h)
    audit.append((page,round(y+h,1),txt[:45]))
    return y+h

def txt(s,x,y,size=10,color=INK,bold=False):
    c.setFont('CNB' if bold else 'CN',size);c.setFillColor(color);c.drawString(x,H-y,s)

def line(x1,y1,x2,y2,color=LINE,width=1,dash=None):
    c.setStrokeColor(color);c.setLineWidth(width);c.setDash(dash or []);c.line(x1,H-y1,x2,H-y2);c.setDash([])

def box(x,y,w,h,title,sub='',color=BLUE,fill=LIGHT):
    c.setFillColor(fill);c.setStrokeColor(color);c.setLineWidth(1)
    c.roundRect(x,H-y-h,w,h,7,stroke=1,fill=1)
    para(title,x+10,y+10,w-20,11,color,15,True)
    if sub:para(sub,x+10,y+34,w-20,9,INK,13)

def arrow(x1,y1,x2,y2,color=BLUE,label=None):
    line(x1,y1,x2,y2,color,1.3)
    a=math.atan2(y2-y1,x2-x1)
    for sign in (-1,1):
        xx=x2-7*math.cos(a+sign*.45);yy=y2-7*math.sin(a+sign*.45)
        line(xx,yy,x2,y2,color,1.3)
    if label:txt(label,(x1+x2)/2+3,(y1+y2)/2-5,8,color)

def callout(text,y,color=TEAL):
    c.setFillColor(LIGHT);c.rect(48,H-y-52,746,52,fill=1,stroke=0)
    c.setFillColor(color);c.rect(48,H-y-52,4,52,fill=1,stroke=0)
    para(text,62,y+9,716,10,color)

def start(title,sub=''):
    global page
    if page:c.showPage()
    page+=1;chapters.append((page,title))
    c.setFillColor(INK);c.rect(0,H-9,W,9,fill=1,stroke=0)
    txt('X-WATCH  /  HARDWARE RESEARCH',48,33,8,GRAY)
    txt('AG3335M  ·  EVK V2 / Rev 0.5',590,33,8,GRAY)
    txt(title,48,76,23,INK,True)
    if sub:para(sub,49,89,742,9.5,GRAY)
    line(48,548,794,548)
    txt('依据用户提供的评估板图纸解析；未经实板验证。源页号均指原 PDF 第 1～14 页。',48,566,8,GRAY)
    txt(f'{page:02d}',770,566,9,BLUE,True)

def table(headers,rows,y=135,widths=None,size=9,rowh=None):
    widths=widths or [746/len(headers)]*len(headers)
    def cell(v,head=False):
        return Paragraph(str(v),ParagraphStyle('t',fontName='CNB' if head else 'CN',fontSize=size,leading=size*1.38,textColor=white if head else INK,wordWrap='CJK'))
    data=[[cell(v,True) for v in headers]]+[[cell(v) for v in r] for r in rows]
    t=Table(data,colWidths=widths,repeatRows=1,rowHeights=rowh)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),INK),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,LIGHT]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),('LINEBELOW',(0,0),(-1,0),.5,INK),('LINEBELOW',(0,1),(-1,-1),.3,LINE)]))
    _,h=t.wrap(746,5000);t.drawOn(c,48,H-y-h)
    audit.append((page,round(y+h,1),'TABLE'))
    return y+h

# 73 unique ball IDs transcribed from U0401-A/B/C; functions describe this EVK, not a complete mux specification.
A=[
('G7','VCCK','核心电源节点','接 C414 4.7 µF；与外部核心电源方案相关'),
('C8','EXT_PWR_EN','外部电源控制','经 R413 0 Ω 出线，控制多路外部稳压器'),
('C7','CHIP_EN','芯片使能','接 CHIP_EN 网络和调试接口'),
('A6','AVDD18_IN','模拟电源输入','经 J1206 接入；1.8 V 方案见源第 7 页'),
('C6','AVDD18_VRTC_IN','RTC 电源输入','VRTC_IN_IC；与 C9 的 VRTC 节点不同'),
('B8','AVSS_AUXADC','ADC 模拟地','源图独立引出；接地方式需结合实际 PCB'),
('B6','AVDD18_TCXO','TCXO 电源节点','C402 1 µF；可供 TCXO 使用'),
('A9','AVDD18_AUXADC','ADC 电源输入','VAUXADC_IC；与 RTC 供电分开'),
('A7','VIO18','I/O 电源节点','C403 1 µF；供 DVDD18_IO 等网络使用'),
('C4','VRF','射频电源节点','C404 2.2 µF；向源第 5 页射频电源分支连接'),
('A5','VDD_SYS_IN','系统电源输入','源第 7 页 RT5707 默认标注 1.2 V'),
('B9','TSENSE_IN','温度检测相关','接 TP9146；不能据此确定输入量程'),
('D4','TESTMODE','测试模式控制','R405/R406 为上下拉选装；勿同时装配'),
('D5','AVSS18_VSYS','系统模拟地','源第 4 页接地'),
('B5','VDD_VRF_IN','射频稳压输入','源第 7 页 RT5707A 默认标注 0.7 V'),
('D2','OSC_XOUT','主时钟相关','源图接 TP9149；TCXO 方案并非跨两脚接无源晶体'),
('C1','OSC_XIN','主时钟输入','由 26 MHz TCXO 经 1 nF 串联电容接入'),
('C9','VRTC','RTC 保持节点','C407 1 µF；可选外部 0.9 V 保持供电'),
('D7','RTC_XIN','RTC 晶体输入','连接 X0401 与 C419'),
('D8','RTC_XOUT','RTC 晶体输出','连接 X0401 与 C420'),
('D6','RTC_EINT','RTC 外部控制','源网络 PWR_PWR_EN；R404 100 kΩ 下拉'),
('E6','FSOURCE_D','专用配置/测试脚','R407/R408 选装；具体功能与电平限制待原厂确认'),
('K1','DVDD18_IO','数字 I/O 供电','接 VIO18；C415/C416 去耦'),
('F7','VSRAM','存储电源节点','C406 2.2 µF；不等同外部可用电源'),
('A8','VCORE','内部核心电源节点','C405 4.7 µF；勿与 VCCK 不加区分地短接'),
('K9','DVDD28_IO','数字 I/O 供电','可选 VIO18 或 2V8_LDO；由供电选择决定'),
('F8','VUSB','USB 电源输入','源第 7 页 VUSB_IN 的 LDO 标注 3.1 V'),
('E8','AVDD18_USB','USB 模拟电源输入','源第 7 页 NCP186 1.8 V 分支'),
('E9','USB20_DM','USB D-','源第 11 页专用 USB 通路'),
('F9','USB20_DP','USB D+','源第 11 页专用 USB 通路'),
('H3','GNDK','数字/核心地','源图接公共地'),('F5','GNDK','数字/核心地','源图接公共地'),('E7','GNDK','数字/核心地','源图接公共地')]
B=[('B1','AVDD07_LO','射频 LO 电源','由 VRF 经 J501 供电；C524 1 µF'),('D3','AVDD07_DCXO','射频时钟电源','经 R553 0 Ω；C525 1 µF'),('B2','AVDD07_L1_L5','L1/L5 射频电源','C523 1 µF'),('A2','RF_IN_L1','L1 射频输入','接 RF_IN_L1 匹配支路'),('A3','RF_IN_L5','L5 射频输入','接 RF_IN_L5 匹配支路'),('B4','AVSS_RF_L1_L5','射频地','与 A1、B3 分别计为独立焊球'),('A1','AVSS_RF_L1_L5','射频地','同名不等于同一焊球'),('B3','AVSS_RF_L1_L5','射频地','同名不等于同一焊球'),('C2','AVSS_RF_ANA','射频模拟地','源图接地'),('C3','AVSS_RF_DCXO','射频时钟地','源图接地')]
gpio_balls=['J8','H7','J9','H9','H8','K8','K6','J6','G8','J7','K5','H6','H4','F3','K2','J2','J5','J4','H1','G2','H2','J1','K3','J3','G4','G3','E2','F2','F1','E1']
gpio_notes=[
'可选 SD CMD / UART2_RTS / GPIO 引出','可选 SD CLK / UART2_CTS / GPIO 引出','可选 SD DAT1 / UART0_RTS / GPIO 引出','可选 SD DAT0 / UART0_CTS / GPIO 引出','GPIO 引出；兼作慢时钟来源启动配置','可选 SD DAT3 / GPIO 引出','可选 SD DAT2 / GPIO 引出','UART0_TX_AG3335 或 GPIO 引出','UART0_RX_AG3335 或 GPIO 引出','GPIO9_O；源图未固定 PPS 功能','GPIO10_O；源图未固定 PPS 功能','可选 BTEN / GPIO 引出；兼 XBOOT 配置','GPIO12_O；兼 26/48 MHz 配置','可选 ANTENNA_BIAS / GPIO 引出','可选 ANT_DETECT / GPIO 引出','可选 EINT_ANTENNA / GPIO 引出','可选 UART2_RTS / GPIO 引出','可选 UART2_CTS / GPIO 引出','可选 UART2_TX / GPIO 引出','可选 UART2_RX / GPIO 引出','可选 ANTENNA_BIAS；兼下载模式位 0','可选 EINT_ANTENNA；兼下载模式位 1','GPIO22_O；未在本图证明其他复用功能','GPIO23_O；未在本图证明其他复用功能','GPIO24_O；兼 SLT 测试模式配置','GPIO25_O；兼 TCXO/DCXO 配置','GPIO26_O；源第 12 页经转换器接 FT234XD RTS#','GPIO27_O；测试排针引出','可选 SD 卡检测 / GPIO 引出','GPIO29_O；测试排针引出']
C=[(b,f'GPIO{i}',gpio_notes[i]) for i,b in enumerate(gpio_balls)]
assert len(A)==33 and len(B)==10 and len(C)==30
assert len({r[0] for r in A+B+C})==73

start('AG3335M 芯片解析', '评估板原理图审读 · 电源与射频架构 · 智能手表应用评估')
txt('从 73 个球位，到可验证的产品方案',49,151,25,BLUE,True)
para('基于用户提供的 AG3335M EVK V2 图纸，重新绘制关键功能关系，建立完整球位索引，并把原图事实、工程解释和待验证事项分别标明。',50,175,660,13)
for x,num,cap in [(50,'73','独立球位已核对'),(303,'14','页原始图纸保留'),(556,'24','页解析与工程评估')]:
    box(x,255,235,108,'','',TEAL)
    txt(num,x+15,306,32,TEAL,True)
    txt(cap,x+15,339,11,INK)
para('资料标识：AG3335M EVK V2；多数图页 Rev 0.5；日期 2020-03-23。\n源第 8 页单独标为 Rev 0.0。文件名中的 BOM 不代表正文为物料表。',51,395,725,11)
callout('本报告是对现有 EVK 的技术解析，不替代原厂 Datasheet，也不是已经完成验证的量产原理图。',465,AMBER)

start('01  这份图纸的价值与边界','评价结论：适合作为裸芯片硬件研究基线；尚不足以直接签核量产。')
table(['评价维度','已获得的证据','边界与使用方法'],[
('引脚定义','U0401-A/B/C 可提取 73 个唯一球位','可建立符号草案；不能从符号坐标推出封装物理排列'),
('电源实现','多路 Buck/LDO、核心外供、RTC 备用方案','可理解电源域；默认标注不是允许电压范围'),
('射频实现','独立 L1/L5 输入、SAW、双工器及匹配选装','可识别路径；实际装配与匹配值需实板、PCB 和 BOM 交叉核对'),
('开发支持','下载模式、电平转换、USB-UART 和引出排针','接口条件较完整；未随本图获得工具、固件和命令全集'),
('成熟度','图纸含历史更改、选装项和未关闭备注','它是研发评估平台，不能假定所有选项同时装配或均已验证')],widths=[95,292,359],size=10)
callout('证据分级：〔图纸〕直接可见；〔解释〕基于连接关系的工程推断；〔建议〕拟议产品策略；〔待核验〕当前资料不足。',452)

start('02  原图导航与版本识别','先按功能定位，再追踪网络名；源页码与文件名中的 SchDoc 前缀并不完全相同。')
table(['源页','标题 / 内容','在本报告中的作用'],[
('1','History','含 2019-11-07 “vcore power source change to external” 历史记录'),
('2','Ball Map','当前 PDF 主体为空白，不能用作封装排列依据'),
('3','Block Diagrams','平台功能与外设概览'),('4','Baseband','U0401-A：电源、控制、主时钟、RTC、USB'),
('5','RF','U0401-B：射频输入、电源与天线选装'),('6','GPIO & Strip Pin','U0401-C：GPIO 和上电绑带说明'),
('7 / 8','Power / Power source','多路稳压器、RTC 保持，以及 USB/电池输入选择'),
('9 / 10','SD Card / AB1532','存储与蓝牙测试外设，可与 GNSS 最小系统分开'),
('11 / 12','USB / USB2UART','原生 USB 和 FT234XD 串口桥是两条不同链路'),
('13 / 14','Indicator / GPIO','电源指示灯、GPIO 排针；低功耗测量时须计入或断开')],widths=[65,230,451],size=9)
para('注意：Rev 0.5 是文件页框版本，不代表已确认对应某个量产芯片后缀、硅版本或固件版本。',49,497,740,10,AMBER)

start('03  系统架构：芯片与 EVK 的职责','矢量重绘 / 功能关系图；箭头表示信号或供电关系，不表示时序或每根实际连线。')
box(310,167,240,218,'AG3335M / U0401','U0401-A：33 球\n供电、控制、时钟、USB<br/><br/>U0401-B：10 球\n射频输入及其电源 / 地<br/><br/>U0401-C：30 球\nGPIO 与复用接口',TEAL)
box(49,160,203,78,'天线及滤波 / 匹配','L1 → A2；L5 → A3')
box(49,273,203,81,'主时钟与 RTC','26 MHz TCXO；外部 RTC 晶体')
box(49,388,203,75,'电源与保持供电','Buck/LDO；EXT_VCORE；RTC')
box(605,160,188,78,'主机 / UART0','GPIO7 J6 → TX；GPIO8 G8 → RX')
box(605,273,188,81,'原生 USB / 下载','F9 D+；E9 D-；下载绑带')
box(605,388,188,75,'评估外设','AB1532、SD 卡、LED、排针')
arrow(252,200,310,200);arrow(252,310,310,310);arrow(252,423,310,365)
arrow(550,200,605,200);arrow(550,310,605,310);arrow(550,365,605,423)
para('〔图纸〕外设多，不等于手表必须全部保留。〔解释〕硬件上具备连接选项，不等于当前固件已实现相应协议或功能。',50,489,740,10)

start('04  完整球位表 A：电源与核心节点','源第 4 页 U0401-A；下表 19 球，下一页继续其余 14 球。功能分类不是原厂电气类型。')
idx=[0,3,4,6,7,8,9,10,14,17,22,23,24,25,26,27,13,5,30]
AA=[A[i] for i in idx]
y=table(['球位','信号名','功能分类','源图连接 / 说明'],AA,y=127,widths=[45,153,111,437],size=8.8)

start('05  完整球位表 A：控制、时钟与 USB','源第 4 页 U0401-A；与上一页合计 33 球，包含 3 个 GNDK。')
rest=[r for i,r in enumerate(A) if i not in idx]
y=table(['球位','信号名','功能分类','源图连接 / 说明'],rest,y=132,widths=[45,153,111,437],size=9.1)
para('电源节点判读：AVDD18_TCXO、VIO18、VRF、VCORE、VSRAM、VRTC 在图上从芯片右侧引出并去耦。它们的稳压输出能力、外部回灌条件及允许负载不能仅靠图形判断。',50,y+17,740,10,AMBER)

start('06  完整球位表 B：射频及地','源第 5 页 U0401-B；10 球。L1、L5 物理输入分别为 A2、A3。')
y=table(['球位','信号名','功能分类','源图连接 / 说明'],B,y=135,widths=[45,170,110,421],size=9.7)
box(48,424,235,72,'U0401-A：33 球','电源、地、控制、时钟、USB',TEAL)
box(303,424,235,72,'U0401-B：10 球','射频输入、射频电源与地',TEAL)
box(558,424,235,72,'U0401-C：30 球','GPIO0～GPIO29',TEAL)
para('计数方法：逐个记录球位字符串并去重。33 + 10 + 30 = 73；同名地脚按不同球位分别计数。',49,510,740,10)

for half in range(2):
    start(f'0{7+half}  完整球位表 C：GPIO{half*15}～GPIO{half*15+14}', '源第 6 页 U0401-C；记录本 EVK 连接选项，不把其他设计中的复用功能直接套入。')
    rows=C[half*15:(half+1)*15]
    y=table(['球位','引脚名','本 EVK 连接及用途'],rows,y=132,widths=[55,100,591],size=9.7)
    para('〔待核验〕GPIO 的完整复用表、方向、驱动能力及具体 I/O 电压分组，仍需对应版本 Datasheet。不要从 DVDD28_IO 的名字推定只能供 2.8 V。',49,y+18,740,10,AMBER)

start('09  电源树：三类节点必须分开','源第 4、7、8 页；以下为 EVK 功能重绘，标值为图纸默认 / 标称方案，不是芯片绝对最大额定值。')
box(49,143,170,74,'输入选择','USB / 适配器 / 电池<br/>经 J1103、SW1101 到 VBAT')
box(49,259,170,92,'RTC 保持分支','3.1 V 充电支路 + 0.22 F<br/>1.8 V RTC_IN / 0.9 V VRTC')
box(300,143,204,74,'主开关电源','RT5707：SYS 1.2 V<br/>RT5707A：VRF_IN 0.7 V')
box(300,253,204,84,'模拟 / USB 分支','AVDD18_IN / USB：1.8 V<br/>AUXADC：1.8 V；VUSB：3.1 V')
box(300,375,204,75,'外部核心电源','RT5795A → EXT_VCORE<br/>默认标注约 0.7 V')
box(591,157,203,200,'AG3335M 电源域','输入：A5、B5、A6、A9、F8、E8、C6<br/><br/>I/O：K1、K9<br/><br/>节点：A7、C4、A8、F7、C9、G7、B6',TEAL)
arrow(219,179,300,179);line(247,179,247,411,BLUE);arrow(247,294,300,294);arrow(247,412,300,412)
arrow(504,179,591,179);arrow(504,294,591,294);arrow(504,412,640,412);arrow(640,412,640,357)
arrow(219,305,270,305,TEAL);line(270,305,270,479,TEAL);line(270,479,727,479,TEAL);arrow(727,479,727,357,TEAL)
para('EXT_PWR_EN 与 RTC_EINT/PWR_PWR_EN 是控制网络，不是电源输出。J1206 允许插入电流测量或改变接法；不是永久短接所有电源域。',50,497,740,10,AMBER)

start('10  电源实现逐项核查','电压数据只描述这份 EVK 的标注；不能作为新产品的允许输入范围或精度指标。')
table(['源图器件 / 分支','目标网络及球位','图纸标值','解析要点'],[
('U1008 / RT5707','VDD_SYS_IN → A5','1.2 V 默认','VSEL 绑带控制；需核对实装及芯片模式'),
('U1012 / RT5707A','VDD_VRF_IN → B5','0.7 V 默认','不是 A6 的 1.8 V 模拟输入；两者不可混接'),
('U1016 / RT5707','AVDD18_IN → A6','1.8 V','VSEL3:2:1 标注 010'),
('U1005 / RT9073A','VAUXADC → A9','1.8 V','和 RTC 输入分供是图纸历史修订内容'),
('U1099 / RT9073A','VRTC_IN → C6','1.8 V','输入来自备用保持节点；开关条件需追线'),
('U1098 / TCR3UM09A','VRTC → C9','0.9 V','备用保持供电；不能与 C6 当成同一节点'),
('U1096 / RT5795A','EXT_VCORE → 可选核心通路','约 0.7 V 默认','经 J1206 与 VCCK / VCORE 路径选择；先核对跳线'),
('U1007 / RT9078','VUSB_IN → F8','3.1 V','不能直接把 USB 接口的 5 V 接到 F8'),
('U1015 / NCP186','AVDD18_USB → E8','1.8 V','USB 电源不止一路；禁用 USB 时也不能随意断供'),
('U1010 / RT9078','DVDD28_IO → K9 可选','2.8 V','另有 VIO18 选项；供电互斥，不能两源并接')],widths=[152,205,89,300],size=9)
para('读图顺序：稳压器输出 → 网络名 → 跳线 / 0 Ω 电阻 → 芯片球位 → 本地去耦。图中标注额定输出电流不是 GNSS 实际电流。',50,497,740,10)

start('11  核心外供与 RTC 保持：最需要谨慎的两处','源第 1、4、7 页；图中存在多套可选连接，以下示意仅解释功能，不能替代跳线配置表。')
box(49,146,208,95,'外部核心降压','RT5795A → EXT_VCORE<br/>VOUT = 0.45 × (1 + R1/R2)<br/>R1 标注 22 kΩ')
box(321,146,203,95,'J1206 / 选择通路','EXT_VCORE、VCCK、VCORE<br/>分属不同引出节点<br/>不预设可全部短接')
box(588,146,205,95,'芯片核心域','G7 VCCK；A8 VCORE<br/>分别有去耦<br/>先核对输入 / 输出及回灌条件',TEAL)
arrow(257,194,321,194);arrow(524,194,588,194)
para('〔图纸〕2019-11-07 修订将 vcore 电源改为外供。SW2002 旁明确写明一次仅开启一个开关；全关约 0.55 V，默认 A1-B1 约 0.7 V。〔解释〕该开关用于改变反馈电阻，不是多档可以叠加使用。',50,263,740,10.5)
box(49,350,208,85,'备用储能','BAT1099 标注 0.22 F / 3.3 V<br/>配套二极管与限流支路')
box(321,350,203,85,'两路 RTC 供电','1.8 V → C6 VRTC 输入<br/>0.9 V → C9 VRTC 保持节点')
box(588,350,205,85,'断主电后的状态','希望保留 RTC / 热启动条件<br/>不代表 GNSS 持续定位<br/>实际保持时间需测量',TEAL)
arrow(257,393,321,393);arrow(524,393,588,393)
para('〔待核验〕掉电先后、备用电源回灌、内部稳压器允许外供条件、RTC 保持电流与保存内容。源图没有给出完整电源时序或保证保持时长。',50,465,740,10.5,AMBER)

start('12  时钟网络：26 MHz 主参考与 RTC 晶体','源第 4、6 页；有源 TCXO 和两脚 RTC 晶体是不同的电路。')
box(49,143,224,100,'TCXO402 / TCXO403（二选一）','KT2016K / KT1612A 系列<br/>均标注 26 MHz<br/>供电取 AVDD18_TCXO，附近 1 µF')
box(336,160,158,65,'C426 / C427','串联 1 nF；其中一套选装')
box(558,143,235,100,'C1 / OSC_XIN','接收主参考时钟<br/>D2 / OSC_XOUT 仅引到测试点<br/>不能按无源晶体连接方式照搬',TEAL)
arrow(273,193,336,193);arrow(494,193,558,193)
txt('RTC 晶体连接（功能示意）',50,302,13,INK,True)
box(65,329,170,70,'D7 / RTC_XIN','C419 20 pF → GND')
box(337,329,169,70,'X0401','两脚 RTC 晶体')
box(609,329,169,70,'D8 / RTC_XOUT','C420 20 pF → GND')
line(235,364,337,364,BLUE,1.5);line(506,364,609,364,BLUE,1.5)
para('〔待核验〕原图写有 “32.368khz”，与常见 RTC 32.768 kHz 存在明显疑点；X0401 器件值仅写 32 KHz。必须按实装晶体料号确认，不能静默修正后发板。',50,423,740,10.5,AMBER)
para('C419/C420 的 20 pF 是外接电容值，不是晶体负载电容 CL。近似 CL ≈ C1×C2/(C1+C2) + 杂散电容；必须结合晶体规格与 PCB 重新检查。GPIO12 选择 26/48 MHz；GPIO25 选择 TCXO/DCXO。',50,479,740,10)

start('13  上电绑带与下载配置','源第 6 页文字说明；0/1 表示上电采样逻辑，不是要求运行时始终强制该电平。')
table(['引脚 / 球位','0 状态','1 状态','图纸中的内部下拉'],[
('GPIO4 / H8','外部慢时钟（默认）','从 26 MHz DCXO 分频得到内部慢时钟','8.33 kΩ'),
('GPIO11 / H6','启动时禁用 host 接口（默认）','启动时开启 SPI slave host 接口','8.33 kΩ'),
('GPIO12 / H4','26 MHz（默认）','48 MHz','75 kΩ'),
('GPIO24 / G4','Normal（默认）','SLT 测试模式','源图未给此项阻值'),
('GPIO25 / G3','TCXO（默认）','DCXO','75 kΩ')],widths=[140,215,281,110],size=9.6)
y=table(['{GPIO21, GPIO20}','源图定义','球位'],[
('00','no / UART download（默认）','J1 / H2'),('01','USB download','J1 / H2'),('10','SPI download','J1 / H2'),('11','I²C download','J1 / H2')],y=348,widths=[160,440,146],size=9.2)
para('绑带 ≠ 跳线默认实装。需核实上下拉选件、主机复位时输出状态及采样时间。GPIO4 的内部慢钟选项描述了 DCXO 条件，不能未经确认套用到当前 TCXO 方案。',50,492,740,10,AMBER)

start('14  射频路径：单天线与双端口是选装方案','源第 5 页；蓝色为独立端口路径，绿色为共用天线 / 双工器路径。下图为功能重绘。')
box(49,144,139,64,'CON501','独立 L1 端口')
box(249,144,194,64,'C0501 / U0501','隔直 + L1 带通滤波')
box(504,144,144,64,'匹配网络','R / L / C 选装')
box(707,144,86,64,'A2','RF_IN_L1',TEAL)
arrow(188,176,249,176);arrow(443,176,504,176);arrow(648,176,707,176)
box(49,261,139,64,'CON502','独立 L5 端口')
box(249,261,194,64,'C517 / U509','隔直 + L5 带通滤波')
box(504,261,144,64,'匹配网络','R / L / C 选装')
box(707,261,86,64,'A3','RF_IN_L5',TEAL)
arrow(188,293,249,293);arrow(443,293,504,293);arrow(648,293,707,293)
box(49,388,139,67,'CON503','共用 L1 + L5 端口',TEAL)
box(249,388,194,67,'U506 / SAWFD1G17AA0F0A','一进二出双工器',TEAL)
arrow(188,422,249,422,TEAL)
line(443,407,463,407,TEAL,1.5);line(463,407,463,176,TEAL,1.5);arrow(463,176,504,176,TEAL)
line(443,439,488,439,TEAL,1.5);line(488,439,488,293,TEAL,1.5);arrow(488,293,504,293,TEAL)
txt('HCH / L1',356,430,8,TEAL);txt('LCH / L5',356,448,8,TEAL)
para('Co-PAD / 0 Ω / NC 表示备选装配与共用焊盘关系；不是“全部装上更好”。实际采用哪条路径要结合 PCB、装配记录和 VNA 测试确认。本页不推定有额外外置 LNA。',50,483,740,10,AMBER)

start('15  射频器件、偏置及匹配评估','原图与 Murata 官方滤波器资料交叉核对；本页的匹配值只是 EVK 记录，不是手表推荐定值。')
table(['对象','原图信息','解析与约束'],[
('U0501','SAFFB1G56KB0F0A；位于 L1 路径','官方频点 1561.1 / 1575.4 / 1601.7 MHz，覆盖多系统 L1 频段 [S3]'),
('U509','SAFFB1G17AB0F0A；位于 L5 路径','官方中心频率 1176.45 MHz；不能只按 1G17 字样猜用途 [S4]'),
('U506','SAWFD1G17AA0F0A','官方为一进二出器件；与前述 SAFFB 单滤波器不同 [S5]'),
('L1 芯片侧','L503 6.8 nH；C504 3.9 pF；C505 NC','含双工器选路与共用焊盘；不同装配必须分别检查匹配'),
('L5 芯片侧','L511 6.8 nH；L512 4 nH；C520 NC','天线、壳体、手腕和走线会改变最佳值，需重新调谐'),
('有源天线偏置','L505 / L513 22 nH；L504 为共用端口偏置支路','电感向射频线注入直流；隔直电容保护后级直流条件'),
('天线检测','Q1/Q2/Q3；Q501/Q502；ANT_DETECT、EINT_ANTENNA','带插拔 / 短路检测和开关；需验证阈值，不能当作已认证保护电路')],widths=[100,287,359],size=9.4)
para('手表采用被动天线时，有源天线偏置和检测支路可评估删除；但 SAW、匹配、ESD 与 LNA 需求须根据链路预算和抗干扰测试决定，不能一并删去。',50,493,740,10,AMBER)

start('16  主机连接：先把 UART0 调通','源第 6、12 页；该方案是产品化建议，不表示 MCU 可直接使用任意电压连接。')
box(49,148,206,232,'AG3335M','J6 / GPIO7：UART0 TX<br/><br/>G8 / GPIO8：UART0 RX<br/><br/>J9 / GPIO2：UART0 RTS 选项<br/><br/>H9 / GPIO3：UART0 CTS 选项',TEAL)
box(320,148,201,232,'电平与掉电隔离','按实际 I/O 供电匹配<br/><br/>跨电压域时加转换器<br/><br/>掉电时避免由主机信号回灌<br/><br/>RTS/CTS 的启用由固件确定')
box(588,148,206,232,'手表 MCU','UART RX<br/><br/>UART TX<br/><br/>CTS（可选）<br/><br/>RTS（可选）',TEAL)
arrow(255,207,320,207);arrow(521,207,588,207)
arrow(588,249,521,249);arrow(320,249,255,249)
arrow(255,291,320,291);arrow(521,291,588,291)
arrow(588,333,521,333);arrow(320,333,255,333)
para('〔图纸〕FT234XD 的 RTS# 在源第 12 页被转换并引至 GPIO26 路径；不能把这个调试辅助信号误当成 GNSS UART0 的固定 RTS 球位。源第 6 页将 GPIO2/3 提供为 UART0 流控选项。',50,407,740,10.5,AMBER)
para('建议保留：CHIP_EN C7、RTC_EINT D6、UART0 TX/RX、共地、各电源测试点以及下载绑带访问点。PPS 如有需求，应先取得固件引脚定义，不能直接把专利中的 GPIO10 用法套进本 EVK。',50,478,740,10)

start('17  USB、串口桥与外围：别把评估设施算成芯片必需','源第 9～14 页。')
table(['电路块','源图实现','对芯片验证的作用','手表迁移建议'],[
('原生 USB','源第 11 页，AG3335 D+/D- → 独立 USB 连接器','配合 USB 电源与下载模式使用','调试阶段留测试接口；量产可否删除须确认启动和供电要求'),
('USB-UART','源第 12 页，FT234XD + SN74LVC1T45','把 PC 串口接到 UART0，并带辅助控制','可放在外部工装，减少手表面积与静态电流'),
('AB1532','源第 10 页，蓝牙芯片及独立时钟/电源','通过 UART2 等选项做连接性评估','如手表已有 MCU/BLE，通常无须复制整套 AB1532'),
('Micro SD','源第 9 页，4-bit SD 接口','日志与存储评估，需固件支持','按产品数据架构决定；不属于定位射频核心'),
('电源 LED','源第 13 页，多路电源指示','便于观察上电','测低功耗时逐路断开或单独核算'),
('GPIO 排针','源第 14 页，J9107 30×2','暴露 GPIO 与可选复用网络','首板保留必要测试焊盘，量产缩减')],widths=[80,221,205,240],size=10)
callout('“删掉外围”必须按供电域、固件依赖和下载恢复需求逐项判断；删除连接器不代表可以同时切断芯片的相关电源。',465,AMBER)

start('18  面向 X-Watch 的最小功能方案','建议架构 / 尚非可投板电路。优先完成定位、通信、休眠与恢复，再逐项压缩面积。')
box(49,143,180,80,'手表 GNSS 天线','L1/L5 双频适配<br/>金属壳体与佩戴状态需实测')
box(298,143,215,80,'双工 / 滤波 / 匹配','选定一套 RF 架构<br/>由 VNA 与整机定位测试验证')
box(582,143,211,80,'AG3335M','A2 / A3 射频<br/>26 MHz TCXO + RTC',TEAL)
arrow(229,183,298,183);arrow(513,183,582,183)
box(49,276,180,83,'电池与 PMIC','GNSS 独立电源域<br/>核心外供 / RTC 保持策略')
box(298,276,215,83,'测试与恢复入口','串口、绑带、使能、电源点<br/>USB / 下载工装按需保留')
box(582,276,211,83,'主 MCU','UART0 + 控制 GPIO<br/>必要的电平转换 / 掉电隔离',TEAL)
arrow(229,317,270,317);line(270,317,270,245,BLUE);line(270,245,660,245,BLUE);arrow(660,245,660,223)
arrow(687,276,687,223);arrow(513,317,582,317)
table(['保留优先级','候选内容','删除前验证'],[
('核心必需','芯片完整供电、去耦、主参考时钟、选定 RF 通路','按手册确认工作条件及未使用引脚处理'),
('首板强烈建议','RTC 晶体与保持选项、UART、绑带、核心电源测点','可恢复下载；休眠/唤醒正常；可量测各电源域'),
('可迁出工装','FT234XD、USB 接口、大排针、LED、SD、AB1532','调试功能能由主机或外部工装替代')],y=395,widths=[110,347,289],size=9.1)

start('19  封装与 PCB：已知球号，不等于已知封装图','以此 EVK 的 73 个独立球位为事实基础；本报告未解析 PCB 二进制焊盘坐标。')
table(['已确认 / 未确认','内容','落板前动作'],[
('已确认','33 + 10 + 30 个唯一球位；名称见完整球位表','符号中保留同名地脚及独立电源节点'),
('外部交叉信息','公开器件页将 AG3335MV/B 标为 VFBGA-73，3.8×4.2 mm [S2]','与芯片采购后缀、实物顶标、源 PCB 封装交叉核对'),
('尚未确认','球距、球径、封装高度、顶/底视方向、缺球及空位图','从原厂 Package Drawing 或经核验 PCB 源文件提取'),
('不能推定','原理图 A/B/C 单元的引脚摆放不是物理焊球排列','不要把符号画法直接变成 PCB 焊盘阵列'),
('仍需确认','盲埋孔/通孔策略、阻焊开窗、焊盘工艺与装联规则','与实际球距和制板/贴装工艺一起确定')],widths=[125,324,297],size=10)
para('布局建议：RF 通道短且有连续参考地；TCXO 与 RTC 区域远离开关节点；去耦靠近相应电源球；Buck 热回路缩小；天线区域按实际结构预留净空。以上是工程建议，不是该 EVK 已完成的 PCB 审核结论。',50,433,740,10.5)
para('手表额外验证：屏幕刷新、电容触控、BLE 发射、NFC、充电与振动电机工作时，记录 GNSS C/N₀、掉星和定位轨迹变化。不能仅以无遮挡静态定位成功判断整机 RF 合格。',50,488,740,10)

start('20  首次上电与恢复：可执行验证顺序','下列为测试流程建议；原图没有完整时序保证值，因此不编造延时、上升时间或复位宽度。')
steps=[('1','断电检查','核对芯片版本、跳线和 NC 实装；检查各电源到地阻抗，排除相互短接。'),('2','分域供电检查','先断开芯片负载或使用原图测量跳线，确认稳压器输出和使能逻辑；电流限值按器件规格设置。'),('3','接入芯片与捕获波形','记录各电源、CHIP_EN、EXT_PWR_EN、RTC_EINT 的实际波形；异常立即断电排查。'),('4','时钟与串口验证','检查主参考时钟配置与 26 MHz TCXO 一致；使用低电容探测方式；检查 UART 电平和 TX/RX。'),('5','下载与功能恢复','按绑带表选择已获支持的下载方式，确认工具识别与正确固件；保存可重复恢复步骤。'),('6','定位及掉电验证','空旷环境记录冷/热启动、C/N₀、更新率；再测待机、断主电保持与异常恢复。')]
for i,(n,title,body) in enumerate(steps):
    y=137+i*62
    c.setFillColor(TEAL);c.circle(64,H-y-14,13,fill=1,stroke=0);txt(n,60,y+18,11,white,True)
    txt(title,91,y+10,11,INK,True);para(body,91,y+18,695,9.5)
para('禁止把本流程理解为已获原厂批准的上电时序。每次改变供电跳线、核心电压或绑带，都先在断电状态操作。',50,517,740,9.5,AMBER)

start('21  功耗与定位测试计划','以可复现数据支持选型；本报告不引用模组电流冒充裸芯片电流。')
table(['测试项目','记录条件','输出及判定依据'],[
('芯片工作功率','逐路电压/电流；卫星组合、双频开关、更新率、温度、固件','P = Σ(Vrail × Irail)；含供电效率时测电池端功率，避免重复计入内外供电'),
('EVK 总电流','LED、FT234XD、AB1532、SD、有源天线分别启停','分离外围负载；比较芯片端与整板端，说明测量边界'),
('冷/热启动','清除/保留状态的方法、天线、天空条件、上次关机时间','TTFF 分布；有效定位条件预先定义，不能只取最快一次'),
('RTC 保持','主电断开、备用电容初始电压、保持时长、温度','保持电压与后续 TTFF；热启动不能仅由 RTC 有电推定'),
('整机干扰','BLE/NFC/显示/充电/电机逐项开关，固定天线姿态','C/N₀、可用卫星数、位置跳变、重捕获时间'),
('步行 / 跑步轨迹','同一线路、佩戴姿态、参考设备、不同遮挡场景','轨迹偏差和里程误差；分别记录单频与双频配置'),
('休眠与恢复','主机 IO 状态、各电源开关、串口状态、重复次数','待机电流、恢复成功率、回灌/锁死；阈值由产品需求定义')],widths=[105,315,326],size=9.5)
para('电池估算：T ≈ 可用电池能量 Wh / 平均电池端功率 W。平均功率要按定位占空比及手表其他负载加权；不要直接用单路 GNSS 电流估计整表续航。',50,491,740,10)

start('22  图纸疑点与工程风险清单','以下均是从当前资料识别的未关闭事项；不是已证实的硅缺陷。')
table(['优先级','证据位置','问题与风险','关闭方法'],[
('高','源第 2 页','Ball Map 正文为空，物理封装数据缺失','核对原厂封装图与源 PCB 焊盘，确认视图方向和球距'),
('高','源第 1 / 4 / 7 页','核心供电改为外供，多个 VCORE / VCCK 选项可能误接','建立断电跳线表；确认稳压器允许外供/回灌和上电时序'),
('高','源第 4 页','RTC 标注 32.368 kHz 与常用 32.768 kHz 不一致','查 X0401 采购料号与实测，不直接把文字当确定频率'),
('高','源第 5 页','多套 Co-PAD、0 Ω、NC 射频路径；滤波器易选错','按目标装配列唯一选路，核对 Murata 精确料号并测 S 参数'),
('高','源第 6 页','绑带、电平域、运行时 GPIO 复用可能互相影响','确认采样时刻、上拉阻值、主机默认态与固件复用'),
('中','源第 5 / 7 页','存在 PMU 电容需检查、多个选装电源备注','逐一核对稳定性、电容容值/偏压降额和实装状态'),
('中','源第 6 / 7 / 8 页','部分文字重叠、拼写问题；源第 8 页单列 Rev 0.0','结合源文件和连接关系阅读，不凭截图 OCR 自动出网表'),
('高','整个资料包','缺芯片完整 DS、对应固件/工具及认证工作条件','原厂/供应商确认后，才关闭量产设计门槛')],widths=[48,100,305,293],size=9.1)
para('评估结论：图纸极具研究价值，但“有原理图”不等于“全部电压、时序与固件条件均已明确”。本次不修改源文件或源图参数。',50,512,740,9.5,AMBER)

start('23  结论、交付范围与证据索引','解析部分共 24 页；其后附用户原始 14 页 PDF，保留原有矢量内容与页内细节。')
para('可以直接使用的成果',49,131,740,13,BLUE,bold=True)
para('73 个球位的可追溯索引；电源域和默认供电方案；主时钟/RTC 连接；上电绑带；射频选装逻辑；主机接口与工装边界；手表迁移建议及验证清单。',49,158,740,11)
para('进入下一版硬件前的四个门槛',49,214,740,13,BLUE,bold=True)
para('① 核对实际芯片后缀与封装；② 确认所有电源输入、内部节点和外供条件；③ 获取匹配固件、工具和下载恢复流程；④ 用已确认装配的 RF 通路完成实板测试。',49,242,740,11)
sources=[
('S1','用户提供的 EVK 原始 PDF','原图 14 页；正文事实主要来源。标题与日期见源图框。',None),
('S2','嘉立创 AG3335MV/B 器件页','仅用于封装型号和本体尺寸交叉信息；不证明与 EVK 的版本一致。','https://jlcpcb.com/partdetail/AIROHA-AG3335MVB/C22392157'),
('S3','Murata SAFFB1G56KB0F0A','L1 多系统频段滤波器资料。','https://www.murata.com/en/products/productdata/8797683712030/DS-SAFFB1G56KB0F0A.pdf'),
('S4','Murata SAFFB1G17AB0F0A','L5 1176.45 MHz 滤波器资料。','https://pim.murata.com/asset/pim4/acousticWaveDeviceForMobile/DS_SAFFB1G17AB0F0A_PDF_ACOUSTICWAVEDEVICEFORMOBILE'),
('S5','Murata SAWFD1G17AA0F0A','一进二出双工滤波器资料。','https://www.murata.com/products/productdata/8803693035550/DS-SAWFD1G17AA0F0A.pdf')]
y=306
for key,name,desc,url in sources:
    txt(key,49,y+12,9,TEAL,True)
    para((f'<link href="{url}" color="#176C9E">{name}</link>' if url else name)+'：'+desc,79,y,709,9.2)
    y+=39
txt('分析日期：2026-10-24  |  原始 PDF SHA-256（截取前 24 位）：'+hashlib.sha256(SRC.read_bytes()).hexdigest()[:24],49,527,8,GRAY)

assert page==24,page
c.save()

# Validate the manually transcribed pin sets against the PDF text.
r=PdfReader(SRC)
extracted=[]
for pi,s,e,expected in [(3,'G7VCCK','U0401-A',A),(4,'B1 AVDD07_LO','U0401-B',B),(5,'J8GPIO0','U0401-C',C)]:
    text=r.pages[pi].extract_text(); segment=text[text.index(s):text.index(e)]
    pins=re.findall(r'(?<![A-Z0-9])([A-HJK][1-9])(?=[A-Z_]|\s)',segment)
    assert set(pins)=={p[0] for p in expected},(e,pins)
    extracted+=pins
assert len(extracted)==len(set(extracted))==73
assert max(v[1] for v in audit)<544,sorted(audit,key=lambda v:v[1])[-10:]

writer=PdfWriter();writer.append(str(TMP/'analysis_body.pdf'))
for n,title in chapters:writer.add_outline_item(f'{n:02d} {title}',n-1)
writer.append(str(SRC),outline_item='附录：用户原始 EVK 图纸（14 页）')
for i in range(14):writer.add_outline_item(f'原图第 {i+1} 页',24+i)
writer.add_metadata({'/Title':'AG3335M EVK 芯片解析与智能手表应用评估（矢量版）','/Author':'X-Watch 技术分析','/Subject':'73 球位、电源、时钟、RF、绑带与验证方案；含 14 页原图'})
with OUT.open('wb') as f:writer.write(f)
final=PdfReader(OUT)
images=sum(len(p.images) for p in final.pages)
assert len(final.pages)==38
assert images==0,images
manifest={'output':str(OUT),'pages':len(final.pages),'analysis_pages':24,'appendix_pages':14,'image_objects':images,'pins':{'A':33,'B':10,'C':30,'unique':73},'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'max_content_y':max(v[1] for v in audit),'bytes':OUT.stat().st_size}
(TMP/'analysis_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False,indent=2))
