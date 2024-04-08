import tkinter as tk
from tkinter import filedialog
import get_vip_video
import tools
import multiprocessing
import os
import tkinter.messagebox as messagebox
from queue import Empty
def start_download(save_location, chosen_browser, urls_to_download, enable_gpu_transcoding,queue):
    #子进程里面不能涉及GUI操作

    if not urls_to_download:
        print("没有输入URL.")
        return

    if not save_location:
        print("没有选择保存位置.")
        return

    print("下载位置：", save_location)
    print("选择的浏览器：", chosen_browser)

    try:
        GPU = enable_gpu_transcoding == 'Yes'
        climb = get_vip_video.get_VIP_video(urllist=urls_to_download, GPU=GPU, save_path=save_location, broswerType=chosen_browser)
        climb.run()
        get_vip_video.execute(climb)
        tools.remove_files(os.path.dirname(os.path.abspath(__file__)), '.m4s')
        queue.put('OK')
    except Exception as e:
        queue.put('NOT OK')

def start_download_thread():
    save_location = save_location_entry.get()
    chosen_browser = selected_browser.get()
    urls_to_download = [url_entry.get() for url_entry in url_entries if url_entry.get()]
    enable_gpu_transcoding = selected_gpu_transcoding.get()
    queue=multiprocessing.Queue()
    download_process = multiprocessing.Process(target=start_download, args=(save_location, chosen_browser, urls_to_download, enable_gpu_transcoding,queue))
    download_process.start()
    check_queue(queue)

def browse_save_location():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        save_location_entry.delete(0, tk.END)
        save_location_entry.insert(0, folder_selected)

# 创建窗口
root = tk.Tk()
root.title('Bilibili Downloader')

root.geometry('600x400')  # 设定窗口初始大小

# 添加 "Bilibili Downloader" 标签
title_label = tk.Label(root, text='Bilibili Downloader', font=('Arial', 14))
title_label.pack(pady=10)

# 创建一个框架用于放置输入框和标签
top_frame = tk.Frame(root)
top_frame.pack(pady=10)

# "Save Location" 输入框和标签
save_location_label = tk.Label(top_frame, text='Save Location:')
save_location_label.grid(row=0, column=0, sticky='e')
save_location_entry = tk.Entry(top_frame, width=50)
save_location_entry.grid(row=0, column=1)
browse_button = tk.Button(top_frame, text="Browse", command=browse_save_location)
browse_button.grid(row=0, column=2)

# 浏览器选择下拉菜单
browser_label = tk.Label(top_frame, text='Browser:')
browser_label.grid(row=1, column=0, sticky='e')
selected_browser = tk.StringVar()
selected_browser.set('msedge')
browser_options = ['msedge', 'chrome']
browser_menu = tk.OptionMenu(top_frame, selected_browser, *browser_options)
browser_menu.grid(row=1, column=1, sticky='w')

# GPU转码选择
gpu_transcoding_label = tk.Label(top_frame, text='Enable GPU Transcoding:')
gpu_transcoding_label.grid(row=2, column=0, sticky='e')
selected_gpu_transcoding = tk.StringVar()
selected_gpu_transcoding.set('Yes')
gpu_transcoding_options = ['Yes', 'No']
gpu_transcoding_menu = tk.OptionMenu(top_frame, selected_gpu_transcoding, *gpu_transcoding_options)
gpu_transcoding_menu.grid(row=2, column=1, sticky='w')

# 创建一个框架用于放置URL输入框
url_frame = tk.Frame(root)
url_frame.pack(pady=20)

url_entries = []
for i in range(5):
    url_label = tk.Label(url_frame, text=f'URL {i+1}:')
    url_label.grid(row=i, column=0, sticky='e')
    url_entry = tk.Entry(url_frame, width=50)
    url_entry.grid(row=i, column=1)
    url_entries.append(url_entry)

# 开始下载按钮
start_button = tk.Button(root, text='Start Download', command=start_download_thread)
start_button.pack(pady=10)
def check_queue(queue):
    try:
        message = queue.get_nowait()  # Try to get message without blocking
    except Empty:
        # If the queue is empty, re-schedule the check_queue function after 100ms
        root.after(100, check_queue, queue)
    else:
        # If a message was received, process it
        if message == 'OK':
            messagebox.showinfo('Notice', 'Download complete!')
        else:
            messagebox.showinfo('Error', 'Download Failed!')



if __name__ == "__main__":
    root.mainloop()
