# 先安裝套件
# pip install -r requirements.txt

import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
import time
import os
from azure.storage.blob import BlobServiceClient

# 請在此處填入您的 Azure 儲存帳戶連接字串
azure_connection_string = "儲存體帳戶連接字串"

# 初始化 BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)

# 輸入您的容器名稱
container_name = "容器名稱"

# 取得容器客戶端
container_client = blob_service_client.get_container_client(container_name)

# 開啟攝像頭並顯示影像，手動拍攝
def capture_photo():
    # 啟動攝像頭
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        messagebox.showerror("錯誤", "無法啟動攝像頭")
        return

    # 設置畫面大小
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 顯示攝像頭畫面
        cv2.imshow("press 's' take a pic, press 'q' quit", frame)

        # 按 's' 鍵保存照片
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            # 保存圖片
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            photo_name = f"photo_{timestamp}.jpg"
            cv2.imwrite(photo_name, frame)
            messagebox.showinfo("成功", f"照片已拍攝並儲存為 {photo_name}")
            upload_to_azure(photo_name)  # 上傳至 Azure
            break
        # 按 'q' 鍵退出攝像頭畫面
        elif key == ord('q'):
            break

    # 釋放攝像頭並關閉窗口
    cap.release()
    cv2.destroyAllWindows()

# 上傳照片到 Azure 儲存
def upload_to_azure(file_path):
    try:
        # 開啟圖片並轉換為二進位資料流
        with open(file_path, "rb") as file:
            # 初始化 BlobClient，使用檔案的原本名稱
            blob_client = container_client.get_blob_client(os.path.basename(file_path))
            
            # 嘗試上傳 Blob
            blob_client.upload_blob(file, overwrite=True)
        
        # 上傳成功後顯示提示
        messagebox.showinfo("成功", f"照片已成功上傳到 Azure 儲存庫！\n檔案名稱: {os.path.basename(file_path)}")
        
        # 上傳後刪除本地照片
        os.remove(file_path)
    except Exception as e:
        # 顯示錯誤訊息
        messagebox.showerror("錯誤", f"上傳失敗: {e}")
        print(f"Error: {e}")  # 輸出錯誤訊息，方便調試

# 打開攝像頭拍照的按鈕觸發函式
def open_camera():
    capture_photo()

# 建立 GUI 讓使用者選擇拍照或選擇照片
def main():
    root = tk.Tk()
    root.title("雲端儲存照片")
    root.geometry("300x200")

    # 建立開啟相機拍照的按鈕
    button_camera = tk.Button(root, text="開啟相機拍照", command=open_camera)
    button_camera.pack(pady=20)

    # 建立選擇照片並上傳的按鈕
    def upload_photo():
        file_path = filedialog.askopenfilename(title="選擇一張照片", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
        if file_path:
            # 使用檔案原始名稱進行上傳
            upload_to_azure(file_path)

    button_upload = tk.Button(root, text="選擇照片上傳", command=upload_photo)
    button_upload.pack(pady=20)

    # 啟動 GUI
    root.mainloop()

# 呼叫主函式
if __name__ == "__main__":
    main()
