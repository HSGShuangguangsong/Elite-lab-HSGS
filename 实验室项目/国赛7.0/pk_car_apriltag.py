from maix import image, camera, display
from maix import camera, display, image, nn, app
from maix import uart
import time

device = "/dev/ttyS0"
serial = uart.UART(device, 115200)
cam = camera.Camera()
disp = display.Display()

families = image.ApriltagFamilies.TAG36H11
x_scale = cam.width() / 160
y_scale = cam.height() / 120

while 1:
    img = cam.read()

    new_img = img.resize(160, 120)
    apriltags = new_img.find_apriltags(families = families)
    
    # 如果检测到AprilTag，发送ID数据
    if len(apriltags) > 0:
        for a in apriltags:
            if a.id() < 3:
                corners = a.corners()

                for i in range(4):
                    corners[i][0] = int(corners[i][0] * x_scale)
                    corners[i][1] = int(corners[i][1] * y_scale)
                x = int(a.x() * x_scale)
                y = int(a.y() * y_scale)
                w = int(a.w() * x_scale)
                h = int(a.h() * y_scale)

                # 绘制检测框
                for i in range(4):
                    img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED)
                img.draw_string(x + w, y, "id: " + str(a.id()), image.COLOR_RED)
                img.draw_string(x + w, y + 15, "family: " + str(a.family()), image.COLOR_RED)
                
                # 只发送ID数据
                data_str = f"#{a.id():02d}OK"
                
                # 发送到串口
                serial.write_str(data_str)
                
                # 在终端输出发送的内容
                print(f"发送数据: {data_str.strip()}")
    else:
        data_str = "#NNOK"
        serial.write_str(data_str)
        print(f"发送数据: {data_str}")
    disp.show(img)