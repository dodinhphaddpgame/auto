# win32_capture.py
import time
import threading
import queue
import ctypes
# from ctypes import wintypes
import win32gui, win32ui, win32con
import numpy as np
import cv2

# Make process DPI-aware to get correct coordinates on high-DPI displays
try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

# PrintWindow prototype
user32 = ctypes.windll.user32
PrintWindow = user32.PrintWindow
IsIconic = user32.IsIconic

class Win32WindowCapture:
    def __init__(self, hwnd, use_client_area=True):
        """
        hwnd: window handle (int) or window title string (then we find it)
        use_client_area: if True capture client area only (no title bar); else whole window
        """
        if isinstance(hwnd, str):
            hwnd = win32gui.FindWindow(None, hwnd)
            if not hwnd:
                raise RuntimeError("Không tìm thấy window với tiêu đề: " + hwnd)
        self.hwnd = hwnd
        self.use_client_area = use_client_area

        # Create DCs / bitmap placeholders
        self.hdc_window = None
        self.mfc_dc = None
        self.save_dc = None
        self.bmp = None
        self.width = 0
        self.height = 0

        self._ensure_dc()

    def _ensure_dc(self):
        """(Re)create DC and bitmap if size changed or not created."""
        # get client rect or window rect and convert to screen coords if necessary
        if self.use_client_area:
            left, top, right, bottom = win32gui.GetClientRect(self.hwnd)
            # Client rect is in client coords; convert origin to screen
            left_top = win32gui.ClientToScreen(self.hwnd, (left, top))
            right_bottom = win32gui.ClientToScreen(self.hwnd, (right, bottom))
            left, top = left_top
            right, bottom = right_bottom
        else:
            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)

        w = right - left
        h = bottom - top
        if w <= 0 or h <= 0:
            raise RuntimeError("Window size invalid: {}x{}".format(w, h))

        if (self.width, self.height) != (w, h):
            # cleanup old
            try:
                if self.mfc_dc:
                    self.mfc_dc.DeleteDC()
            except Exception:
                pass
            try:
                if self.save_dc:
                    self.save_dc.DeleteDC()
            except Exception:
                pass
            try:
                if self.bmp:
                    win32gui.DeleteObject(self.bmp.GetHandle())
            except Exception:
                pass

            # create new DCs/bitmap
            hwnd_dc = win32gui.GetWindowDC(self.hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(mfc_dc, w, h)
            save_dc.SelectObject(bmp)

            # store
            self.hdc_window = hwnd_dc
            self.mfc_dc = mfc_dc
            self.save_dc = save_dc
            self.bmp = bmp
            self.left = left
            self.top = top
            self.width = w
            self.height = h

    def grab_bitblt(self):
        """Capture via BitBlt. Returns BGR numpy array or None on failure."""
        if IsIconic(self.hwnd):
            # minimized -> no reliable content
            return None

        try:
            self._ensure_dc()
        except Exception as e:
            print("Ensure DC failed:", e)
            return None

        # copy screen into our memory DC
        try:
            # SRCCOPY from screen DC starting at (left, top)
            self.save_dc.BitBlt((0, 0), (self.width, self.height), self.mfc_dc, (0, 0), win32con.SRCCOPY)
        except Exception as e:
            # sometimes BitBlt can fail
            # print("BitBlt failed:", e)
            return None

        # get raw bits
        bmpinfo = self.bmp.GetInfo()
        bmpstr = self.bmp.GetBitmapBits(True)
        img = np.frombuffer(bmpstr, dtype=np.uint8)
        # shape may be (h, w, 4)
        try:
            img.shape = (self.height, self.width, 4)
        except Exception:
            return None
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def grab_printwindow(self):
        """Try PrintWindow fallback. Returns BGR numpy array or None."""
        if IsIconic(self.hwnd):
            return None
        try:
            self._ensure_dc()
        except Exception:
            return None
        # PW_RENDERFULLCONTENT = 2 on some systems; pass 2 to encourage full render
        res = PrintWindow(self.hwnd, self.save_dc.GetSafeHdc(), 2)
        if res == 0:
            # failed
            return None
        bmpstr = self.bmp.GetBitmapBits(True)
        try:
            arr = np.frombuffer(bmpstr, dtype=np.uint8)
            arr.shape = (self.height, self.width, 4)
            img = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
            return img
        except Exception:
            return None

    def grab(self, try_printwindow_if_black=True, black_thresh=10):
        """
        Capture best-effort: try BitBlt, if result is mostly black then try PrintWindow.
        Returns BGR numpy array or None.
        """
        img = self.grab_bitblt()
        if img is None:
            # try PrintWindow directly
            return self.grab_printwindow()
        # quick check for mostly-black frame
        if try_printwindow_if_black:
            # compute mean brightness; if very low, probably black
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            if gray.mean() < black_thresh:
                # try PrintWindow fallback
                pw = self.grab_printwindow()
                if pw is not None:
                    return pw
        return img

    def release(self):
        try:
            if self.mfc_dc:
                self.mfc_dc.DeleteDC()
            if self.save_dc:
                self.save_dc.DeleteDC()
            if self.bmp:
                win32gui.DeleteObject(self.bmp.GetHandle())
            if self.hdc_window:
                win32gui.ReleaseDC(self.hwnd, self.hdc_window)
        except Exception:
            pass

# ---------------------------
# Producer / consumer example
# ---------------------------
class CaptureProducer(threading.Thread):
    def __init__(self, capturer: Win32WindowCapture, out_queue: queue.Queue, max_fps=30):
        super().__init__(daemon=True)
        self.cap = capturer
        self.q = out_queue
        self.max_fps = max_fps
        self.running = True

    def run(self):
        interval = 1.0 / self.max_fps if self.max_fps > 0 else 0
        while self.running:
            t0 = time.time()
            img = self.cap.grab()
            if img is not None:
                # non-blocking put
                try:
                    if self.q.qsize() < 2:  # simple backpressure: keep small buffer
                        self.q.put_nowait(img)
                    else:
                        # drop frame if consumer is slow
                        pass
                except queue.Full:
                    pass
            elapsed = time.time() - t0
            to_sleep = interval - elapsed
            # print(interval)
            if to_sleep > 0:
                time.sleep(to_sleep)

    def stop(self):
        self.running = False

# ---------------------------
# Demo usage
# ---------------------------
def demo(window_title):
    # find hwnd by title (first match)
    # hwnd = win32gui.FindWindow(None, window_title)
    hwnd = gethwnd(window_title, "child")
    if hwnd is None:
        if not hwnd:
            print("Window not found:", window_title)
            return
    cap = Win32WindowCapture(hwnd, use_client_area=True)
    q = queue.Queue(maxsize=4)
    producer = CaptureProducer(cap, q, max_fps=25)
    producer.start()

    # consumer loop: process frames with OpenCV (template matching or show)
    try:
        last_print = time.time()
        frames = 0
        while True:
            try:
                frame = q.get(timeout=1.0)
            except queue.Empty:
                # no frames
                if IsIconic(hwnd):
                    print("Window minimized -> stopping demo")
                    break
                continue
            frames += 1
            # example processing: convert and show
            cv2.imshow("capture", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            # print FPS every 2s
            if time.time() - last_print > 2:
                print("FPS (consumer):", frames / (time.time() - last_print))
                frames = 0
                last_print = time.time()
    finally:
        producer.stop()
        cap.release()
        cv2.destroyAllWindows()

def gethwnd(window_title, target="child"):
    """
    window_title: substring của title (ví dụ "LDPlayer-4")
    target: "child" để gửi tới RenderWindow (mặc định), "parent" để gửi tới cửa sổ cha
    """
    parent_hwnd = None
    child_hwnd = None

    # tìm parent window (top-level) chứa window_title
    def enum_windows_proc(hwnd, _):
        nonlocal parent_hwnd, child_hwnd
        try:
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd) or ""
                if window_title.lower() in title.lower():
                    parent_hwnd = hwnd

                    # tìm child RenderWindow bên trong parent
                    def enum_child_proc(chwnd, _2):
                        nonlocal child_hwnd
                        try:
                            cls = (win32gui.GetClassName(chwnd) or "").lower()
                            if "renderwindow" in cls:
                                child_hwnd = chwnd
                        except Exception:
                            pass

                    win32gui.EnumChildWindows(hwnd, enum_child_proc, None)
        except Exception:
            pass

    win32gui.EnumWindows(enum_windows_proc, None)

    if not parent_hwnd and not child_hwnd:
        raise Exception(f"Không tìm thấy cửa sổ chứa: '{window_title}'")

    # chọn target theo mode
    if target == "child":
        if not child_hwnd:
            raise Exception(f"Không tìm thấy RenderWindow trong cửa sổ chứa: '{window_title}'")
        return child_hwnd
    else:  # target == "parent"
        if not parent_hwnd:
            raise Exception(f"Không tìm thấy parent window chứa: '{window_title}'")
        return parent_hwnd

if __name__ == "__main__":
    # chỉnh tên cửa sổ cho phù hợp, ví dụ "LDPlayer" hoặc một phần tiêu đề
    demo("LDPlayer")
    # img_bgr = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
