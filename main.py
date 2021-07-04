# Author yangguanlin<--->18631661520@163.com VBIGFCKPXWWTIIFT
from machine import I2C, Pin    #rtc not yet completed
from ssd1306 import SSD1306_I2C
from utime import sleep_ms
import framebuf
# I2C & SSD1306 for OLED support
import network,dht,urequests,ujson
# utime to halt ; network to connect to AP ;
# don't know why but it worked
# pinmux
# ESP8266 & LCD
# on RGB , D5,D6,D7 as R,G,B
# use D1 as scl ; D2 as sda ; D3 as dht11-data entry
indicator = Pin(2,Pin.OUT)
dht_dat = Pin(0,Pin.IN)
scl_pin,sda_pin = Pin(5,Pin.OUT),Pin(4,Pin.OUT)
r_pin,g_pin,b_pin = Pin(14,Pin.OUT),Pin(12,Pin.OUT),Pin(13,Pin.OUT) #PP,gpio second use
#instants
d = dht.DHT11(dht_dat)
disp_i2c = I2C(scl=scl_pin,sda=sda_pin,freq=4000000)
dev = disp_i2c.scan()
display = SSD1306_I2C(width=128,height=64,addr=dev[0],i2c=disp_i2c)
wlan = network.WLAN(network.STA_IF)

def graph(file,pix_x,pix_y,x,y):
    with open(file+'.pbm','rb') as f:
        f.readline()
        f.readline()
        line = bytearray(f.read())
        data = framebuf.FrameBuffer(line,pix_x,pix_y,framebuf.MONO_HLSB)
        display.blit(data,x,y) 
def rgb(R,G,B):
    r_pin.value(not R)
    g_pin.value(not G)
    b_pin.value(not B)
    r_pin.value(R)
    g_pin.value(G)
    b_pin.value(B)
def get_web_usage(code):
    #try:
        quest = urequests.get('http://hq.sinajs.cn/list=sh'+code)
        # dec = quest.text
        # market = str(ujson.loads(dec))['v_s_sh'+code]
        # code,price,up_down,sold,value = market.split('~')[2],market.split('~')[3],market.split('~')[5],market.split('~')[7],market.split('~')[9]
        # info = '#'+code+' NOW:'+price+'CNY '+up_down+'% SOLD:'+sold+' VAL:'+value
        # print(info)
        #if(quest.status_code == 200):display.text(time+flow/1024+fee)
    #except ValueError :display.text('HOST BUSY',24,24)
def get_date():
    try:
        jpyder = urequests.post('http://quan.suning.com/getSysTime.do')
        jpyder = ujson.loads(jpyder.text)
        date = str(jpyder['sysTime2']).split(' ')
        print(date[1])
        display.text(date[0],16,0)
        display.text(date[1],16,8)
    except ValueError :display.text('API BUSY',16,0)
def dht11_tick(tm_min,tm_max,rh_min,rh_max):
    try:
        d.measure()
        if(d.temperature()>=tm_max):rgb(1,0,0)
        elif(d.temperature()<=tm_min):rgb(0,0,1)
        else:rgb(0,1,0)
        if(d.humidity()>=rh_max):rgb(1,0,0)
        elif(d.humidity()<=rh_min):rgb(0,0,1)
        else:rgb(0,1,0)
        display.text(str(d.temperature())+'^C '+str(d.humidity())+'%RH',24,16)
    except ValueError :display.text('getting...',24,16)

while(1):
    display.fill(0)
    graph('logo',128,64,0,0)
    display.show()
    sleep_ms(2000)
    wlan.active(True)
    if(wlan.isconnected() == True):wlan.disconnect()
    while(1):
        try:
            display.fill(0)
            tup_wlan = wlan.ifconfig()
            net_seg,sub_msk = str(tup_wlan[1]).split('.'),''
            for idx in range(4):
                if(net_seg[idx] == '0'):
                    sub_msk = str(idx*8)
                    break
            display.text(str(tup_wlan[0])+'/'+sub_msk,0,56)
            display.fill_rect(0,0,128,24,0)
            get_web_usage('600519')
            sleep_ms(150)
            get_date()
            dht11_tick(18,30,30,90)
            graph('wifi',16,16,112,0)
            display.show()
            sleep_ms(150)
        except OSError as err:
            if(not wlan.isconnected()):
                wlan.connect('4-407 Private','YGLGJWZJYMMJ')
                display.fill(0)
                graph('wrong',16,16,112,0)
                display.text('AP LOST...',0,16)
                display.show()
                sleep_ms(3000)
            print(err)
#EOF,all print is for debug
