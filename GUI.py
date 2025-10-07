import time
import tkinter as tk
import threading
import log_message
import works

def a():
    print("hello")

def close_all_tabs():
    while True:
        instances = get_instances()
        if not instances:
            log_message.logg("Tất cả tab đã được tắt.")
            break
        for idx in instances:
            works.run_ldconsole(["quit", "--index", idx])
            log_message.logg(f"Đã gửi lệnh tắt LDPlayer instance {idx}")
            time.sleep(2)

def get_instances():
    output = works.run_ldconsole(["list2"])
    instances = []
    for line in output.splitlines():
        parts = line.split(",")
        if len(parts) >= 5 and parts[0].isdigit():
            index = parts[0].strip()
            status = parts[4].strip()
            if index != "99999" and status == "1":
                instances.append(index)
    return instances

def open_tabs():
    try:
        start_idx = int(entry_start.get())
        end_idx = int(entry_end.get())
        for idx in range(start_idx, end_idx + 1):
            threading.Thread(target=works.worker_instance, args=(idx,), daemon=True).start()
            time.sleep(5)
    except ValueError:
        log_message.logg("Vui lòng nhập số hợp lệ!")
# ================= GUI =================
root = tk.Tk()
root.title("Auto Controller")
root.geometry("900x900")

frame_range = tk.Frame(root)
frame_range.pack(pady=10)

tk.Label(frame_range, text="Start index:").grid(row=0, column=0, padx=5)
entry_start = tk.Entry(frame_range, width=5)
entry_start.grid(row=0, column=1, padx=5)
entry_start.insert(0, "1")

tk.Label(frame_range, text="End index:").grid(row=0, column=2, padx=5)
entry_end = tk.Entry(frame_range, width=5)
entry_end.grid(row=0, column=3, padx=5)
entry_end.insert(0, "1")

open_button = tk.Button(frame_range, text="Open Tabs", font=("Arial", 12), bg="blue", fg="white",
                        command=lambda: threading.Thread(target=open_tabs, daemon=True).start())
open_button.grid(row=0, column=4, padx=8)

close_button = tk.Button(frame_range, text="Close All Tabs", font=("Arial", 12), bg="red", fg="white",
                         command=lambda: threading.Thread(target=close_all_tabs, daemon=True).start())
close_button.grid(row=0, column=5, padx=8)
# text log
text_box = tk.Text(root, height=20, width=100)
text_box.pack(pady=10)

def append_to_text_box(msg):
    """
    Chạy append vào text_box trên luồng UI bằng text_box.after để an toàn.
    """
    def _append():
        text_box.insert("end", msg + "\n")
        text_box.see("end")
    try:
        text_box.after(0, _append)
    except Exception as e:
        print("append_to_text_box error:", e)

# đăng ký callback với module log_message
log_message.register_text_widget_callback(append_to_text_box)

root.mainloop()
