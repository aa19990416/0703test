import cv2
import threading
from tracker import ObjectTracker
from zoom_handler import ZoomHandler
from camera_thread import CameraThread, thread_lock, thread_exit

class VideoCaptureThread(threading.Thread):
    def __init__(self, tracker):
        super().__init__()
        self.tracker = tracker  # 傳入的追蹤器對象
        self.running = True  # 控制循環的變量
        self.tracking_enabled = False  # 追蹤是否啟用
        self.zoom_handler = ZoomHandler()
        global thread_exit
        self.camera_id = 0  # 相機 ID
        self.img_height = 480  # 影像高度
        self.img_width = 640  # 影像寬度

        self.thread = CameraThread(self.camera_id, self.img_height, self.img_width)  # 創建相機執行緒
        self.thread.start()  # 啟動相機執行緒

    def run(self):
        cv2.namedWindow("Webcam")
        while self.running:
            thread_lock.acquire()
            frame = self.thread.get_frame()  # 獲取影像幀
            thread_lock.release()
            if frame is None:
                continue

            # 如果啟用了追蹤，調用 tracker 的 update 方法
            frame = self.zoom_handler.apply_zoom(frame)
            if self.tracking_enabled:
                self.tracker.update_tracker(frame)
            
            cv2.imshow("Webcam", frame)  # 顯示影像
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 按下 'q' 或 'esc' 鍵退出
                self.running = False
            if key == ord('t') or key == ord('T'):  # 按下 't' 鍵切換追蹤
                self.tracking_enabled = not self.tracking_enabled
                if self.tracking_enabled:
                    print("Tracking enabled")  # 啟動追蹤
                    cv2.setMouseCallback("Webcam", self.tracker.draw_rectangle)
                else:
                    print("Tracking disabled")  # 停止追蹤
                    self.tracker.stop_tracking()
                    cv2.setMouseCallback("Webcam", lambda *args: None)  # 移除滑鼠回調          
            if key == ord('+'):
                self.zoom_handler.zoom_in()
            if key == ord('-'):
                self.zoom_handler.zoom_out()
            if key == ord('z') or key == ord('Z'):
                self.zoom_handler.zoom_reset()

        global thread_exit
        thread_exit = True
        self.thread.join()  # 等待相機執行緒結束        
        cv2.destroyAllWindows()

def main():
    tracker = ObjectTracker(roi_size=30, tracker_type='CSRT', debug=True)  # 創建追蹤器對象
    video_thread = VideoCaptureThread(tracker)  # 創建主threading
    video_thread.start()  # 啟動主threading
    video_thread.join()  # 等待主threading結束

if __name__ == "__main__":
    main()
