
import screenshot
img = screenshot.screenshot(3)
ac = screenshot.found_image_with_region(3, img, "templates/1_startgame/1.png",0.9)
print(ac)