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

    # start_ldplayer(idx)    # 0 - Start LDplayer

    hwnd = screenshot.gethwnd(f"LDPlayer-{idx}", target="child")  #get hwnd

    # start_game(idx, hwnd)  # 1 - Start game
    # sleep(1)
    #
    # login(idx, hwnd)        # 2 - Login
    # sleep(1)
    #
    # off_ad(idx,hwnd)
    auto_trong_cay(idx,hwnd)
    log_message.logg("Hoàn thành công việc")

def start_game(idx, hwnd):
    # 1 - Start game
    log_message.logg(f"[LD {idx}] Đang thao tác mở game")
    # hwnd = screenshot.gethwnd(f"LDPlayer-{idx}")
    daclick = False
    while True:
        img = screenshot.screenshot_window_by_hwnd(hwnd)
        found, score, rect = screenshot.find_template_on_screen(img, "templates/start_game/tpl_20251010_080251game.png")
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
                # daclick = False
                log_message.logg(f"[LD {idx}] Đang đợi mở game")
                time.sleep(5)
                break
            else:
                time.sleep(0.5)

def login(idx, hwnd):
    # 2 - Login
    log_message.logg(f"[LD {idx}] Đang thao tác login game")
    templates = ("templates/login/tpl_20251010_081109taikhoan.png", "templates/login/tpl_20251010_081150game.png")
    x = 0
    daclick = False
    while True:
        image = screenshot.screenshot_window_by_hwnd(hwnd)
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
                daclick = False
                if x==1:
                    log_message.logg(f"[LD {idx}] Đang đợi login game")
                    time.sleep(15)
                    break
                else:
                    time.sleep(0.5)
            else:
                time.sleep(0.5)
            x = x + 1
            if x == 2:
                x = 0

def off_ad(idx, hwnd):
    daclick = False
    while True:
        image = screenshot.screenshot_window_by_hwnd(hwnd)
        found, score, rect = screenshot.find_template_on_screen(image,
                                                                "templates/origin/tpl_20251010_082554buttonarrive.png")
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
                break
            else:
                winapiclickandswipe.press_esc(hwnd)
                time.sleep(1)

def auto_trong_cay(idx, hwnd):
    templates = ("templates/origin/tpl_20251010_082415origin1.png",
                 "templates/autotrongcay/tpl_20251010_091551tang1.png")
    x = 0
    while True:

        image = screenshot.screenshot_window_by_hwnd(hwnd)
        found, score, rect = screenshot.find_template_on_screen(image, templates[x])
        match x:
            case 0:
                if found:
                    winapiclickandswipe.swipe_multi(hwnd, [(770, 230), (770, 450)], duration=800, step=20)
                    time.sleep(1)
            case 1:
                if found:
                    daxuli = xuli1(idx, hwnd)
                    time.sleep(1)
                print("ok")

            case _:
                time.sleep(0.5)
                print("ko thay origin")  # default
        x = x + 1
        if x == 2:
            x = 0

def xuli1(idx, hwnd):           # autotrongcay
    templates = ("templates/xuli1/tpl_20251010_095702.png",
                 "templates/xuli1/tpl_20251010_140819.png",
                 "templates/xuli1/tpl_20251010_141221.png")
    x = 0
    da_gieo_hat_hoac_thu_hoach = False
    while True:
        image = screenshot.screenshot_window_by_hwnd(hwnd)
        found, score, rect = screenshot.find_template_on_screen(image, templates[x])
        match x:
            case 0: #----------gieo hạt---------
                if found:
                    found, score, rect = screenshot.find_template_on_screen(image, templates[2])
                    if found:
                        if rect:
                            x1, y1, x2, y2 = rect
                            cx = (x1 + x2) // 2
                            cy = (y1 + y2) // 2
                            winapiclickandswipe.swipe_multi(hwnd, [(cx, cy), (300, 740), (370, 740)], duration=800, step=20)
                            da_gieo_hat_hoac_thu_hoach = True
                            time.sleep(1)
                            break
            case 1: #------------thu hoạch---------
                if found:
                    if rect:
                        x1, y1, x2, y2 = rect
                        cx = (x1 + x2) // 2
                        cy = (y1 + y2) // 2
                        winapiclickandswipe.swipe_multi(hwnd, [(cx, cy), (300, 740), (650, 740)], duration=800, step=20)
                        daclick = True
                        time.sleep(1)
                        break
            case _:
                winapiclickandswipe.click(hwnd, 720, 450)
                time.sleep(1)
                winapiclickandswipe.click(hwnd, 300, 740)
                time.sleep(1)
                break
        x = x + 1
        if x == 3:
            x = 0
    return True
import GUI