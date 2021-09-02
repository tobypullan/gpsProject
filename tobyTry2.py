from PIL import Image, ImageDraw, ImageFont
from gps3 import gps3
import ST7789, random, time, csv
disp = ST7789.ST7789(
    port=0,
    cs=ST7789.BG_SPI_CS_FRONT,  # BG_SPI_CS_BACK or BG_SPI_CS_FRONT
    dc=9,
    backlight=19,               # 18 for back BG slot, 19 for front BG slot.
    spi_speed_hz=80 * 1000 * 1000,
)

disp.begin()
img = Image.new('RGB', (disp.width, disp.height), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)

def display(measure, value, pos):
    draw.rectangle((10, pos, disp.width, disp.height), (0, 0, 0))
    draw.text((10,pos), f'{measure}: {value}', font=font, fill=(255, 255, 255))
    print(f'{measure}: {value}')

t1 = time.time()
headers = ['longitude', 'latitude']
rows = []
gps_socket = gps3.GPSDSocket()
data_stream = gps3.DataStream()
gps_socket.connect()
gps_socket.watch()
d = 0
s = []
t = []
tD = 0
def minute(time):
    if time > 59:
        mins = time // 60
        secs = time % 60
    else:
        mins = 0
        secs = time
    return f'{mins} minutes {secs} seconds'
#((s1+s2)/2)*(t1-t2)
with open('coors.csv','w',encoding='UTF8',newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headers)    
    for new_data in gps_socket:
        if new_data:
            data_stream.unpack(new_data)
            long = data_stream.TPV['lon']
            lat = data_stream.TPV['lat']

            speed = data_stream.TPV['speed']
            pT = time.time() - t1
            
            if speed == 'n/a':
                d = 'n/a'
            else:
                speed *= 3.6
                t.append(pT)
                s.append(speed/3600)
                
            if len(t) <= 1:
                d = 'n/a'
            else:
                d = ((s[0]+s[1])/2)*(t[1]-t[0])
                tD += d
                del t[0]
                del s[0]
            print(tD)
            display('Distance', tD, 10)
            display('Speed', speed, 50)
            display('Time', minute(round(pT, 2)), 90)
            disp.display(img)
            writer.writerow([long, lat])
            