import os
import json
import cv2
import screenshot

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ROOT = os.path.join(BASE_DIR, "templatesnhiemvu")


def load_roi(path):
    j = json.load(open(path))
    return j["x1"], j["y1"], j["x2"], j["y2"]


def get_next_index(folder):
    used = set()
    for f in os.listdir(folder):
        name, ext = os.path.splitext(f)
        if name.isdigit():
            used.add(int(name))
    i = 1
    while i in used:
        i += 1
    return i


def match_in_group(roi_img, group_path, threshold=0.98):
    for f in os.listdir(group_path):
        if not f.endswith(".png"):
            continue

        tpl = cv2.imread(os.path.join(group_path, f))
        if tpl is None or tpl.shape != roi_img.shape:
            continue

        res = cv2.matchTemplate(roi_img, tpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)

        if max_val >= threshold:
            return True, f, max_val

    return False, None, 0.0


# ===== MAIN =====
screen = screenshot.screenshot(window_title="LDPlayer-acc_chinh", target="child")

for group in os.listdir(TEMPLATE_ROOT):
    group_path = os.path.join(TEMPLATE_ROOT, group)
    if not os.path.isdir(group_path):
        continue

    roi_json = os.path.join(group_path, "roi.json")
    if not os.path.exists(roi_json):
        continue

    x1, y1, x2, y2 = load_roi(roi_json)
    roi_img = screen[y1:y2, x1:x2]

    found, name, score = match_in_group(roi_img, group_path)

    if found:
        print(f"[{group}] MATCH {name}  score={score:.4f}")
        continue

    # ===== Nhiệm vụ mới trong group này =====
    next_id = get_next_index(group_path)
    new_name = str(next_id)

    png_path = os.path.join(group_path, new_name + ".png")
    json_path = os.path.join(group_path, new_name + ".json")

    cv2.imwrite(png_path, roi_img)

    # Lưu thêm json cùng tên
    with open(json_path, "w") as f:
        json.dump({
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        }, f, indent=2)

    print(f"[{group}] NEW TEMPLATE → {new_name}")