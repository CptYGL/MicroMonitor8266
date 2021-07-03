# Author yangguanlin<--->18631661520@163.com VBIGFCKPXWWTIIFT
from machine import I2C, Pin    #rtc not yet completed
from ssd1306 import SSD1306_I2C
from utime import sleep_ms
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
d = dht.DHT11(dht_dat)
disp_i2c = I2C(scl=scl_pin,sda=sda_pin,freq=4000000)
dev = disp_i2c.scan()
display = SSD1306_I2C(width=128,height=64,addr=dev[0],i2c=disp_i2c)
wlan = network.WLAN(network.STA_IF)

def rgb(R,G,B):
    r_pin.value(not R)
    g_pin.value(not G)
    b_pin.value(not B)
    sleep_ms(100)
    r_pin.value(R)
    g_pin.value(G)
    b_pin.value(B)
def refresh(msec):
    display.fill(0)
    display.show()
    sleep_ms(msec)
def crawler():
    url = 'http://quan.suning.com/getSysTime.do'
    jpyder = ujson.loads(urequests.get(url).text)
    date = str(jpyder['sysTime2'])
    time = date.split(' ')[0].split('-')[1:]+date.split(' ')[1].split(':')[:2]
    display.text(time[0]+'-'+time[1]+' '+time[2]+':'+time[3],0,0)
    display.show()
def dht11_tick():
    d.measure()
    if(d.temperature()>=30):rgb(1,0,0)
    elif(d.temperature()<=20):rgb(0,0,1)
    else:rgb(0,1,0)
    if(d.humidity()>=85):rgb(1,0,0)
    elif(d.humidity()<=30):rgb(0,0,1)
    else:rgb(0,1,0)
    display.fill_rect(0,8,128,16,0)
    display.show()
    display.text(str(d.temperature())+'^C '+str(d.humidity())+'%RH',24,8)
    display.show()
    sleep_ms(1000)

while(1):
    refresh(100)
    wlan.active(True)
    flag = wlan.isconnected()
    if(flag == False):
        wlan.connect('GanlinV40','49a63f5650f0')
        display.text('Connecting...',0,0)
        display.show()
        sleep_ms(3000)
    if(flag == True):
        refresh(100)
        tup_wlan = wlan.ifconfig()
        display.text('IP:'+str(tup_wlan[0]),0,32)
        display.text('MK:'+str(tup_wlan[1]),0,40)
        display.text('MC:'+str(tup_wlan[2]),0,48)
        display.text('DS:'+str(tup_wlan[3]),0,56)
        display.show()
        crawler()
        cnt = 10
        while(cnt):
            while(cnt > 0):
                dht11_tick()
                cnt-=1
            if(not wlan.isconnected()):break
