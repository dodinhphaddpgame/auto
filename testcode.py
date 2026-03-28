import json
import screenshot

roi = json.load(open("templates/3_openbangnhiemvu/1.json"))
region = (roi["x1"], roi["y1"], roi["x2"], roi["y2"])
# screenshot.find_template_on_screen("templates/1_startgame/1.png")
# print(roi)
# print(roi["y1"])
print(region[0])

# x = 0
# while True:
abcd = screenshot.gethwnd(window_title="LDPlayer-3", target = "child")
img = screenshot.screenshot_window_by_hwnd(abcd)  # img is BGR numpy array or None
# found, score, rect = screenshot.find_template_on_screen_with_region(img, "templates/3_openbangnhiemvu/1.png", threshold=0.99)
# found = screenshot.found_image_with_region(3, img,"templates/3_openbangnhiemvu/1.png",abcd)
# found, score, rect = screenshot.find_template_on_screen_with_region(img, "templates/3_openbangnhiemvu/1.png")
found, score, rect = screenshot.find_template_on_screen_with_region(img, "templates/3_openbangnhiemvu/1.png")

print(found)

#     # found, score, rect = screenshot.find_template_with_region_on_screen(img, "templates/3_openbangnhiemvu/1.png",threshold=0.99)
#
#     x=x+1
#     if found:
#         print(f"{score}" , {x})