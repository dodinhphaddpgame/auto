import subprocess
import time
from time import sleep
import log_message
import screenshot
import winapiclickandswipe
# ================= Per-Instance Worker =================

LD_CONSOLE = r"D:\LDPlayer\LDPlayer9\ldconsole.exe"  # Đường dẫn ldconsole.exe
GAME_PACKAGE = "vn.kvtm.js"
ACCOUNTS_FILE = "accounts_used.txt"

def run_ldconsole(args):
    cmd = [LD_CONSOLE]
    if "--command" in args:
        pos = args.index("--command")
        # Ghép tất cả sau --command thành một chuỗi duy nhất
        cmd += args[:pos+1] + [" ".join(args[pos+1:])]
    else:
        cmd += args

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return (result.stdout + result.stderr).strip()

def start_ldplayer(idx):
    run_ldconsole(["launch", "--index", str(idx)])
    log_message.logg(f"[LD {idx}] Đang mở LDPlayer instance")
    sleep(30)
    # run_ldconsole([
    #    "adb", "--index", str(idx),
    #    "--command", f"shell monkey -p {GAME_PACKAGE} -c android.intent.category.LAUNCHER 1"
    # ])
    #
    # log_message.logg(f"[LD {idx}] Đang mở game {GAME_PACKAGE}")
    #
    # sleep(12)  # đợi game load

def worker_instance(idx):
    log_message.logg(f"[LD {idx}] Bắt đầu quản lý instance {idx}")

    # 0 - Start LDplayer
    start_ldplayer(idx)

    # 1 - Start game
    log_message.logg(f"[LD {idx}] Đang thao tác mở game")
    hwnd = screenshot.gethwnd(f"LDPlayer-{idx}")
    daclick = False
    while True:
        img = screenshot.screenshot(window_title=f"LDPlayer-{idx}", target="child")
        found = screenshot.found_image(img,"templates/tpl_20251007_151509.png")
        if found:
            screenshot.click_if_found(idx, img,"templates/tpl_20251007_151509.png", hwnd)
            daclick = True
            time.sleep(1)
        else:
            if daclick:
                if found:
                    daclick = False
                else:
                    log_message.logg(f"[LD {idx}] Đang đợi mở game")
                    time.sleep(5)
                    break
            else:
                time.sleep(0.5)

    # status = 0

    # 2 - Login
    log_message.logg(f"[LD {idx}] Đang thao tác login game")
    x = 0
    daclick = False
    while True:
        image = screenshot.screenshot(window_title=f"LDPlayer-{idx}", target="child")
        templates = ("templates/tpl_20251007_210223.png","templates/tpl_20251007_210319.png")
        x = x + 1
        if x == 2:
            x = 0
        found, score, rect = screenshot.find_template_on_screen(image, templates[x])
        if found:
            if rect:
                x1, y1, x2, y2 = rect
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                winapiclickandswipe.click(hwnd, cx, cy)
            daclick = True
            time.sleep(1)
        else:
            if daclick:
                if found:
                    daclick = False
                elif x==1 and not found:
                    log_message.logg(f"[LD {idx}] Đang đợi login game")
                    time.sleep(5)
                    break
            else:
                time.sleep(0.5)

    # found, score, rect = screenshot.find_template_on_screen(image, "templates/tpl_20251007_210223.png")

    # image = screenshot.screenshot(window_title=f"LDPlayer-{idx}", target = "child")
    # match status:
    #     case 1:
    #         screenshot.click_if_found(idx, image,"templates/tpl_20251007_151509.png", hwnd)
    #         break
    #     case _:
    #         print("Other")

    log_message.logg("Hoàn thành công việc")
