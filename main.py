import os
import pprint
import re

# 1、爬取视频页的网页源代码
import requests
import json
from lxml import etree

header = {
    "referer": "https://www.bilibili.com",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
}


# 2、提取视频和音频的播放地址
def get_play_url(url):
    r = requests.get(url, headers=header)
    # print(r.text)
    info = re.findall('window.__playinfo__=(.*?)</script>', r.text)[0]
    video_url = json.loads(info)["data"]["dash"]["video"][0]["baseUrl"]
    audio_url = json.loads(info)["data"]["dash"]["audio"][0]["baseUrl"]
    # print(video_url)
    # print(audio_url)
    html = etree.HTML(r.text)
    filename = html.xpath('//h1/text()')[0]
    # 清理文件名中的非法字符
    filename = re.sub(r'[\\/:*?"<>|]', '', filename)
    # print(filename)
    return video_url, audio_url, filename


# 3、下载并保存视频和音频
def download_files(video_url, audio_url, filename, video_path, audio_path):
    print("\n=== 开始下载 ===")
    print(f"下载路径信息：")
    print(f"视频保存位置: {os.path.abspath(video_path)}")
    print(f"音频保存位置: {os.path.abspath(audio_path)}")
    print(f"文件名: {filename}")
    
    try:
        # 下载视频
        print("\n正在下载视频...")
        video_content = requests.get(video_url, headers=header).content
        video_file = f'{video_path}/{filename}.mp4'
        with open(video_file, 'wb') as f:
            f.write(video_content)
        video_size = os.path.getsize(video_file) / (1024*1024)  # 转换为MB
        print(f"视频下载完成！文件大小: {video_size:.2f}MB")
        
        # 下载音频
        print("\n正在下载音频...")
        audio_content = requests.get(audio_url, headers=header).content
        audio_file = f'{audio_path}/{filename}.mp3'
        with open(audio_file, 'wb') as f:
            f.write(audio_content)
        audio_size = os.path.getsize(audio_file) / (1024*1024)  # 转换为MB
        print(f"音频下载完成！文件大小: {audio_size:.2f}MB")
        
        # 验证文件
        if os.path.exists(video_file) and os.path.exists(audio_file):
            print("\n✓ 文件下载验证成功！")
            print(f"视频文件: {video_file}")
            print(f"音频文件: {audio_file}")
        else:
            print("\n❌ 警告：文件可能未正确保存！")
            
    except Exception as e:
        print(f"\n❌ 下载出错: {str(e)}")
        raise


# 4、合并视频和音频,使用ffmpeg模块
def combin_video_audio(filename, video_path, audio_path):
    print("\n=== 开始合并 ===")
    import subprocess
    ffmpeg_path = r"C:\Users\Administrator\Downloads\ffmpeg-master-latest-win64-gpl-shared\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe"
    
    # 使用时间戳作为临时文件名
    import time
    temp_name = str(int(time.time()))
    
    # 使用绝对路径
    video_file = os.path.abspath(os.path.join(video_path, f"{filename}.mp4"))
    audio_file = os.path.abspath(os.path.join(audio_path, f"{filename}.mp3"))
    temp_video = os.path.abspath(os.path.join(video_path, f"temp_{temp_name}.mp4"))
    temp_audio = os.path.abspath(os.path.join(audio_path, f"temp_{temp_name}.mp3"))
    output_file = os.path.abspath(os.path.join(video_path, f"output_{temp_name}.mp4"))
    
    try:
        print(f"处理文件：")
        print(f"视频文件：{video_file}")
        print(f"音频文件：{audio_file}")
        
        # 重命名文件为临时英文名
        os.rename(video_file, temp_video)
        os.rename(audio_file, temp_audio)
        
        print(f"临时文件：")
        print(f"临时视频：{temp_video}")
        print(f"临时音频：{temp_audio}")
        
        # 使用列表形式构建命令，避免字符串解析问题
        cmd = [
            ffmpeg_path,
            '-i', temp_video,
            '-i', temp_audio,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-map', '0:v:0',
            '-map', '1:a:0',
            output_file
        ]
        
        print(f"执行命令：{' '.join(cmd)}")
        
        # 使用subprocess执行命令
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if process.returncode == 0 and os.path.exists(output_file):
            output_size = os.path.getsize(output_file) / (1024*1024)
            
            # 将输出文件改回中文名
            final_output = os.path.join(video_path, f"完成-{filename}.mp4")
            os.rename(output_file, final_output)
            
            print(f"\n✓ 合并成功！")
            print(f"输出文件: {os.path.abspath(final_output)}")
            print(f"文件大小: {output_size:.2f}MB")
            
            # 删除临时文件
            os.remove(temp_video)
            os.remove(temp_audio)
            print('临时文件已清理')
        else:
            print(f"\n❌ 合并失败！错误代码: {process.returncode}")
            print("错误输出：")
            print(process.stderr)
            # 恢复原始文件
            os.rename(temp_video, video_file)
            os.rename(temp_audio, audio_file)
            
    except Exception as e:
        print(f"\n❌ 合并过程出错: {str(e)}")
        # 确保出错时也能将文件名改回原来的
        if os.path.exists(temp_video):
            os.rename(temp_video, video_file)
        if os.path.exists(temp_audio):
            os.rename(temp_audio, audio_file)


import tkinter as tk
from tkinter import ttk, messagebox
import threading

class VideoDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("B站视频下载器")
        self.root.geometry("600x400")
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL输入框
        ttk.Label(main_frame, text="请输入B站视频链接:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 下载按钮
        self.download_btn = ttk.Button(main_frame, text="开始下载", command=self.start_download)
        self.download_btn.grid(row=2, column=0, pady=10)
        
        # 进度显示
        self.progress_var = tk.StringVar(value="准备就绪")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # 日志显示框
        self.log_text = tk.Text(main_frame, height=15, width=60)
        self.log_text.grid(row=4, column=0, columnspan=2, pady=10)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("错误", "请输入视频链接！")
            return
        
        self.download_btn.configure(state='disabled')
        self.progress_var.set("下载中...")
        
        # 在新线程中执行下载
        thread = threading.Thread(target=self.download_process, args=(url,))
        thread.daemon = True
        thread.start()
    
    def download_process(self, url):
        try:
            # 创建保存文件的目录
            video_path = './videos'
            audio_path = './audio'
            os.makedirs(video_path, exist_ok=True)
            os.makedirs(audio_path, exist_ok=True)
            
            self.log(f"当前工作目录: {os.getcwd()}")
            
            # 获取视频信息
            self.log("正在获取视频信息...")
            video_url, audio_url, filename = get_play_url(url)
            
            # 下载文件
            self.log("\n=== 开始下载 ===")
            self.log(f"文件名: {filename}")
            download_files(video_url, audio_url, filename, video_path, audio_path)
            
            # 合并文件
            combin_video_audio(filename, video_path, audio_path)
            
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