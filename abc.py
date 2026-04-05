import time
import screenshot
import winapiclickandswipe


TEMPLATES = {
    "map_anchor": "images/map_anchor.png",
    "login_screen_1": "templates/2_home/2.png",
    "login_screen_2": "templates/2_home/2.png",
    "login_screen_3": "templates/2_home/3.png",
    "startgame1": "templates/1_startgame/1.png",
    "startgame2": "templates/1_startgame/2.png",
    "openbangnhiemvu1": "templates/3_openbangnhiemvu/1.png",
    "openbangnhiemvu2": "templates/3_openbangnhiemvu/2.png",
    "openbangnhiemvu3": "templates/3_openbangnhiemvu/3.png",
    "openbangnhiemvu4": "templates/3_openbangnhiemvu/4.png",

    "login_button": "images/login_button.png",
    "quest_panel_anchor": "images/quest_panel_anchor.png",
    "quest_icon": "images/quest_icon.png",
    "claim_button": "images/claim_button.png",
    "complete_text": "images/complete_text.png",
    "game_icon": "images/game_icon.png",
    "go_button": "images/go_button.png",
    "text_talk": "images/text_talk.png",
    "text_fight": "images/text_fight.png",
    "text_collect": "images/text_collect.png",
    "text_move": "images/text_move.png",
}

DEFAULT_THRESHOLD = 0.99

# =========================
# Primitive
# =========================

def get_screen_image(idx):
    return screenshot.screenshot(idx)

def get_screen_image2(idx):
    return screenshot.screenshot2(idx)


def see(idx, img, name, threshold=DEFAULT_THRESHOLD):
    template_path = TEMPLATES[name]
    return screenshot.found_image_with_region(idx, img, template_path, threshold)

def click(idx, img, name, threshold=DEFAULT_THRESHOLD):
    template_path = TEMPLATES[name]
    return screenshot.click_if_found_with_region(idx, img, template_path, threshold)
    # print(f"[CLICK] {name}")

def press_back(idx):
    winapiclickandswipe.press_esc(idx)
    print("[ACTION] press_back")

def press_f1(idx):
    winapiclickandswipe.press_f1(idx)
    print("[ACTION] press_f1")

def sleep(sec=0.5):
    time.sleep(sec)


# =========================
# Check functions
# =========================

def game_is_running(idx, img):
    return see(idx, img, "startgame2")


def in_map(idx, img):
    return see(idx, img, "login_screen_1") and see(idx, img, "login_screen_2") and see(idx, img, "login_screen_3")


def quest_panel_open(idx, img):
    return see(idx, img, "openbangnhiemvu4")


def quest_completed(idx, img):
    return see(idx, img, "claim_button") or see(idx, img, "complete_text")


def detect_quest_type(idx, img):
    if see(idx, img, "text_talk"):
        return "TALK_NPC"

    if see(idx, img, "text_fight"):
        return "FIGHT"

    if see(idx, img, "text_collect"):
        return "COLLECT"

    if see(idx, img, "text_move"):
        return "MOVE"

    return "UNKNOWN"


# =========================
# Ensure functions
# =========================

def ensure_game_running(idx, img):
    if game_is_running(idx, img):
        return True

    press_f1(idx)
    sleep(2)
    img = get_screen_image(idx)
    if see(idx, img, "startgame1"):
        print("abc")
        click(idx, img, "startgame1")
    sleep(2)

    return False


def ensure_in_map(idx, img):
    if in_map(idx, img):
        return True

    press_back(idx)
    sleep(1)
    return False


def ensure_quest_panel_open(idx, img):
    if quest_panel_open(idx, img):
        return True

    while True:
        img = screenshot.screenshot(idx)
        if click(idx,img,"openbangnhiemvu1"):
            sleep(1)
        if click(idx,img,"openbangnhiemvu2"):
            sleep(1)
        if click(idx,img,"openbangnhiemvu3"):
            break
        sleep(1)
    return False


# =========================
# Action functions
# =========================

def claim_reward(idx, img):
    if see(idx, img, "claim_button"):
        click(idx, img, "claim_button")
        sleep(1)
        return True

    return False


def do_quest_by_type(idx, img, qtype):
    if see(idx, img, "go_button"):
        click(idx, img, "go_button")
        sleep(1)
        return True

    if qtype == "TALK_NPC":
        print("[QUEST] TALK_NPC")
        return True

    if qtype == "FIGHT":
        print("[QUEST] FIGHT")
        return True

    if qtype == "COLLECT":
        print("[QUEST] COLLECT")
        return True

    if qtype == "MOVE":
        print("[QUEST] MOVE")
        return True

    print("[QUEST] UNKNOWN")
    return False


# =========================
# Main loop
# =========================

def quest_master_loop(idx):
    print("----- NEW LOOP -----")

    img = get_screen_image2(idx)

    if not ensure_game_running(idx, img):
        print("[FLOW] waiting game open")
        return

    img = get_screen_image(idx)

    if not ensure_in_map(idx, img):
        print("[FLOW] returning to map")
        return

    img = get_screen_image(idx)

    if not ensure_quest_panel_open(idx, img):
        print("[FLOW] opening quest panel")
        return

    # img = get_screen_image(idx)
    #
    # if quest_completed(idx, img):
    #     print("[FLOW] quest completed -> claim")
    #     claim_reward(idx, img)
    #     return
    #
    # qtype = detect_quest_type(idx, img)
    # print(f"[FLOW] quest type = {qtype}")
    #
    # do_quest_by_type(idx, img, qtype)


def main():
    idx = 3

    while True:
        quest_master_loop(idx)
        sleep(0.5)


if __name__ == "__main__":
    main()