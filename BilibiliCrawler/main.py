import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from bilibili_downloader import get_play_url, download_files, combin_video_audio

class VideoDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("B站视频下载器")
        self.root.geometry("600x500")  # 增加窗口高度
        
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL输入框
        ttk.Label(main_frame, text="请输入B站视频链接:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 下载按钮
        self.download_btn = ttk.Button(main_frame, text="开始下载", command=self.start_download)
        self.download_btn.grid(row=2, column=0, pady=10)
        
        # 视频下载进度条
        ttk.Label(main_frame, text="视频下载进度:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.video_progress = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.video_progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        self.video_label = ttk.Label(main_frame, text="0%")
        self.video_label.grid(row=4, column=2, padx=5)
        
        # 音频下载进度条
        ttk.Label(main_frame, text="音频下载进度:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.audio_progress = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.audio_progress.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        self.audio_label = ttk.Label(main_frame, text="0%")
        self.audio_label.grid(row=6, column=2, padx=5)
        
        # 添加合并进度条
        ttk.Label(main_frame, text="合并进度:").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.merge_progress = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.merge_progress.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        self.merge_label = ttk.Label(main_frame, text="0%")
        self.merge_label.grid(row=8, column=2, padx=5)
        
        # 状态显示
        self.progress_var = tk.StringVar(value="准备就绪")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=9, column=0, sticky=tk.W, pady=5)
        
        # 日志显示框
        self.log_text = tk.Text(main_frame, height=15, width=60)
        self.log_text.grid(row=10, column=0, columnspan=2, pady=10)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=10, column=2, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def update_progress(self, file_type, progress, downloaded, total):
        """更新进度条"""
        if file_type == 'video':
            self.video_progress['value'] = progress
            self.video_label['text'] = f"{progress:.1f}%"
        else:
            self.audio_progress['value'] = progress
            self.audio_label['text'] = f"{progress:.1f}%"
        
        # 更新下载速度和已下载大小
        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total / (1024 * 1024)
        self.progress_var.set(f"已下载: {downloaded_mb:.1f}MB / {total_mb:.1f}MB")
        
        self.root.update()
    
    def update_merge_progress(self, progress):
        """更新合并进度条"""
        self.merge_progress['value'] = progress
        self.merge_label['text'] = f"{progress:.1f}%"
        self.root.update()
    
    def reset_progress(self):
        """重置所有进度条"""
        self.video_progress['value'] = 0
        self.audio_progress['value'] = 0
        self.merge_progress['value'] = 0
        self.video_label['text'] = "0%"
        self.audio_label['text'] = "0%"
        self.merge_label['text'] = "0%"
        self.progress_var.set("准备就绪")
    
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("错误", "请输入视频链接！")
            return
        
        self.download_btn.configure(state='disabled')
        self.progress_var.set("下载中...")
        
        thread = threading.Thread(target=self.download_process, args=(url,))
        thread.daemon = True
        thread.start()
    
    def download_process(self, url):
        try:
            self.reset_progress()
            video_path = './videos'
            audio_path = './audio'
            os.makedirs(video_path, exist_ok=True)
            os.makedirs(audio_path, exist_ok=True)
            
            self.log(f"当前工作目录: {os.getcwd()}")
            
            self.log("正在获取视频信息...")
            video_url, audio_url, filename = get_play_url(url)
            
            self.log("\n=== 开始下载 ===")
            self.log(f"文件名: {filename}")
            
            download_files(video_url, audio_url, filename, video_path, audio_path, 
                         progress_callback=self.update_progress)
            
            self.progress_var.set("正在合并文件...")
            combin_video_audio(filename, video_path, audio_path, 
                             progress_callback=self.update_merge_progress)
            
            self.progress_var.set("下载完成！")
            messagebox.showinfo("成功", "视频下载和合并已完成！")
            
        except Exception as e:
            self.log(f"\n发生错误: {str(e)}")
            messagebox.showerror("错误", f"下载过程中发生错误：{str(e)}")
            self.progress_var.set("下载失败")
        
        finally:
            self.download_btn.configure(state='normal')

if __name__ == '__main__':
    root = tk.Tk()
    app = VideoDownloaderGUI(root)
    root.mainloop()