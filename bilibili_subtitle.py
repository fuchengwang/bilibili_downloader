import yt_dlp
import os
import sys
import requests
import time
import qrcode
import json
import re
import webbrowser
from http.cookiejar import MozillaCookieJar
import shutil
import argparse

# Cookie 存储路径：使用用户家目录下的隐藏文件，避免污染当前工作目录
COOKIE_FILE = os.path.expanduser("~/.bili_cookies.txt")
OLD_COOKIE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bili_cookies.txt")
# 默认下载目录：用户目录下的 Downloads 文件夹
DOWNLOAD_DIR = os.path.expanduser("~/Downloads")

def migrate_cookie():
    """如果存在旧的 cookie 文件且新的不存在，则进行迁移"""
    if os.path.exists(OLD_COOKIE_FILE) and not os.path.exists(COOKIE_FILE):
        try:
            # 尝试直接移动
            try:
                shutil.move(OLD_COOKIE_FILE, COOKIE_FILE)
            except:
                # 如果移动失败（可能是跨分区或权限限制），尝试复制并删除
                with open(OLD_COOKIE_FILE, 'rb') as f_src:
                    with open(COOKIE_FILE, 'wb') as f_dst:
                        f_dst.write(f_src.read())
                os.remove(OLD_COOKIE_FILE)
            print(f"📦 已将 Cookie 文件迁移至固定隐藏位置: {COOKIE_FILE}")
        except Exception as e:
            print(f"⚠️ 迁移 Cookie 文件失败: {e}")
    elif os.path.exists(OLD_COOKIE_FILE):
        # 如果两个都存在，尝试删除旧的以保持整洁
        try:
            os.remove(OLD_COOKIE_FILE)
        except:
            pass

# 执行迁移
migrate_cookie()

# 手动 Cookie 导入路径：脚本所在目录下的 cookie 文件
USER_MANUAL_COOKIE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookie")

def is_login(session):
    """检查是否登录"""
    try:
        url = "https://api.bilibili.com/x/web-interface/nav"
        resp = session.get(url, timeout=10).json()
        if resp.get('code') == 0:
            print(f"✅ 登录成功，用户: {resp['data']['uname']}")
            return True
        return False
    except:
        return False

def save_cookies_as_netscape(session, file_path):
    """将 requests session 中的 cookies 保存为 Netscape 格式，供 yt-dlp 使用"""
    cj = MozillaCookieJar(file_path)
    for cookie in session.cookies:
        cj.set_cookie(cookie)
    cj.save(ignore_discard=True, ignore_expires=True)

def parse_raw_cookie_to_session(raw_cookie_str, session):
    """解析原始 Cookie 字符串并填充到 session 中"""
    try:
        # 处理可能存在的前导数字或其他干扰字符
        clean_cookie = re.sub(r'^\d+→', '', raw_cookie_str).strip()
        items = clean_cookie.split(';')
        for item in items:
            if '=' in item:
                key, value = item.strip().split('=', 1)
                session.cookies.set(key, value, domain='.bilibili.com')
        return True
    except Exception as e:
        print(f"❌ 解析 Cookie 失败: {e}")
        return False

def load_manual_cookie():
    """从用户手动提供的文件加载 Cookie"""
    if not os.path.exists(USER_MANUAL_COOKIE_PATH):
        print(f"❌ 未找到手动 Cookie 文件: {USER_MANUAL_COOKIE_PATH}")
        return None
    
    print(f"📂 正在尝试从 {USER_MANUAL_COOKIE_PATH} 加载 Cookie...")
    with open(USER_MANUAL_COOKIE_PATH, 'r') as f:
        content = f.read().strip()
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.bilibili.com/'
    })
    
    if parse_raw_cookie_to_session(content, session):
        if is_login(session):
            save_cookies_as_netscape(session, COOKIE_FILE)
            return session
    return None

def qr_login():
    """Bilibili 扫码登录逻辑"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.bilibili.com/'
    })

    print("📺 正在获取登录二维码...")
    try:
        url = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
        resp = session.get(url).json()
        qr_url = resp['data']['url']
        qr_key = resp['data']['qrcode_key']

        qr = qrcode.QRCode()
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)
        print(f"🔗 扫码链接: {qr_url}")
        print("💡 请使用 Bilibili 手机端 App 扫码登录")

        poll_url = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
        while True:
            poll_resp = session.get(poll_url, params={'qrcode_key': qr_key}).json()
            code = poll_resp['data']['code']
            if code == 0:
                print("🎉 扫码登录成功！")
                save_cookies_as_netscape(session, COOKIE_FILE)
                return session
            elif code == 86101: pass
            elif code == 86038:
                print("❌ 二维码已失效。")
                return None
            elif code == 86090:
                print("📱 扫码成功，请在手机上确认。")
            time.sleep(2)
    except Exception as e:
        print(f"❌ 扫码登录出错: {e}")
        return None

def login_via_browser():
    """跳转到浏览器登录并提取 Cookie"""
    print("\n🌐 正在为您打开 Bilibili 登录页面...")
    webbrowser.open("https://passport.bilibili.com/login")
    print("💡 请在打开的浏览器中完成登录（支持手机号验证码 + 拼图验证）。")
    input("✅ 登录完成后，请回到这里按 [回车] 键继续...")
    
    print("\n🚀 正在尝试从您的浏览器中提取登录状态...")
    # 按照 macOS 常用浏览器排序
    browsers = ["safari", "chrome", "edge", "firefox"]
    
    for browser in browsers:
        try:
            print(f"🔍 正在检查 {browser} 浏览器...")
            ydl_opts = {
                'cookiesfrombrowser': (browser,),
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 触发一次请求以加载 cookie
                ydl.extract_info("https://api.bilibili.com/x/web-interface/nav", download=False)
                
                if hasattr(ydl, 'cookiejar'):
                    # 将提取到的 cookie 存入 session 进行验证
                    session = requests.Session()
                    session.headers.update({
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Referer': 'https://www.bilibili.com/'
                    })
                    for cookie in ydl.cookiejar:
                        session.cookies.set_cookie(cookie)
                    
                    if is_login(session):
                        print(f"🎉 成功从 {browser} 提取到有效的登录状态！")
                        save_cookies_as_netscape(session, COOKIE_FILE)
                        return session
        except Exception:
            continue
            
    print("❌ 未能在浏览器中找到有效的登录状态。")
    print("💡 请确保：1. 您在浏览器中已成功登录 2. 浏览器已关闭或保存了最新的 Cookie。")
    return None

def get_session():
    """获取有效的 session，支持多种方式"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.bilibili.com/'
    })

    # 1. 尝试加载自动保存的 Cookie
    if os.path.exists(COOKIE_FILE):
        cj = MozillaCookieJar(COOKIE_FILE)
        try:
            cj.load(ignore_discard=True, ignore_expires=True)
            session.cookies.update(cj)
            if is_login(session): return session
            print("⚠️ 登录状态已失效。")
        except: pass

    # 2. 提供登录选项
    print("\n" + "="*30)
    print("      Bilibili 登录中心")
    print("="*30)
    print("1. 浏览器授权登录 (推荐：支持手机验证码+拼图)")
    print("2. 扫码登录 (需要手机 App)")
    print("3. 导入已有本地 Cookie (读取 ./cookie 文件)")
    print("="*30)
    choice = input("请选择登录方式 (输入数字): ").strip()

    if choice == '1': return login_via_browser()
    elif choice == '2': return qr_login()
    elif choice == '3': return load_manual_cookie()
    else:
        print("❌ 无效选择")
        return None

def srt_to_text(srt_path):
    """Simple SRT to Text converter"""
    try:
        txt_path = os.path.splitext(srt_path)[0] + ".txt"
        print(f"📄 正在转换字幕为纯文本: {txt_path}")
        
        with open(srt_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        text_lines = []
        is_text = False
        for line in lines:
            line = line.strip()
            # Skip empty lines
            if not line:
                is_text = False
                continue
            # Skip numeric counters
            if line.isdigit():
                is_text = False
                continue
            # Skip timestamps
            if '-->' in line:
                is_text = True
                continue
            
            # Content lines
            if is_text:
                text_lines.append(line)
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(text_lines))
            
        print(f"✅ 纯文本导出成功: {txt_path}")
    except Exception as e:
        print(f"❌ 转换纯文本失败: {e}")

def download_bilibili_subtitle(url, to_txt=False):
    """灵活下载 Bilibili 视频字幕"""
    session = get_session()
    if not session: return

    base_ydl_opts = {
        'skip_download': True,        # 不下载视频
        'writesubtitles': True,       # 下载字幕
        'writeautomaticsub': True,    # 下载自动生成的字幕 (AI字幕)
        'subtitleslangs': ['all'],    # 下载所有可用的字幕语言
        'subtitlesformat': 'srt/ass/best', # 字幕格式
        'cookiefile': COOKIE_FILE,
        'ignoreerrors': True,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        # Since yt-dlp doesn't easily return the subtitle path in the hook for subtitles-only,
        # we will infer it or scan for it after download.
        
        download_dir = DOWNLOAD_DIR
        choice = None
        is_playlist = False
        
        with yt_dlp.YoutubeDL(base_ydl_opts) as ydl:
            print(f"\n🔍 正在解析链接信息...")
            info = ydl.extract_info(url, download=False)
            if not info:
                print("❌ 无法获取视频信息，请检查链接或网络。")
                return
                
            is_playlist = 'entries' in info and info['entries']
            title = info.get('title', '未命名视频')
            
            if is_playlist:
                print(f"📂 检测到该链接是一个合集: 【{title}】")
                print("请选择下载方式:")
                print("1. 下载当前单辑字幕")
                print("2. 下载整个合集字幕")
                choice = input("请输入数字 (1 或 2): ").strip()
                
                if choice == '2':
                    save_dir_name = title.replace("/", "_") + "_subtitles"
                    save_dir = os.path.join(DOWNLOAD_DIR, save_dir_name)
                    print(f"🚀 开始下载整个合集字幕到文件夹: {save_dir}")
                    if not os.path.exists(save_dir):
                        os.makedirs(save_dir)
                    
                    ydl_opts = base_ydl_opts.copy()
                    ydl_opts.update({
                        'quiet': False, 
                        'outtmpl': f'{save_dir}/%(title)s.%(ext)s', 
                        'noplaylist': False,
                        'replace_in_metadata': [
                            ('title', f'^{re.escape(title)}\\s*', ''),
                            ('title', r'^[ \-_]+', ''),
                        ]
                    })
                    download_dir = save_dir
                else:
                    print(f"🚀 开始下载单辑字幕...")
                    ydl_opts = base_ydl_opts.copy()
                    ydl_opts.update({
                        'quiet': False, 
                        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'), 
                        'noplaylist': True
                    })
            else:
                print(f"🎬 正在下载单视频字幕: 【{title}】")
                ydl_opts = base_ydl_opts.copy()
                ydl_opts.update({
                    'quiet': False, 
                    'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'), 
                    'noplaylist': True
                })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl_executor:
            print(f"🚀 开始提取字幕...")
            ydl_executor.download([url])
        
        print("\n" + "✨"*20)
        print(f"✅ 字幕下载任务已完成！")
        
        if to_txt:
            print("🔄 正在寻找并转换字幕文件为 TXT...")
            # Use os.scandir to find .srt files
            found_subtitles = []
            if os.path.exists(download_dir):
                for entry in os.scandir(download_dir):
                    if entry.is_file() and entry.name.endswith('.srt'):
                         # Simple heuristic: modified in last 60 seconds
                         if os.path.getmtime(entry.path) > time.time() - 60:
                            found_subtitles.append(entry.path)

            if not found_subtitles:
                print("⚠️ 未找到刚下载的 SRT 字幕文件，跳过转换。")
            else:
                for sub_file in found_subtitles:
                    srt_to_text(sub_file)

        print(f"📂 文件已保存至: {download_dir}")
        print("✨"*20)
    except Exception as e:
        print(f"❌ 处理过程中出现错误: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bilibili Subtitle Downloader")
    parser.add_argument("url", nargs="?", help="Bilibili video URL")
    parser.add_argument("--txt", action="store_true", help="Convert subtitles to plain text")
    
    args = parser.parse_args()
    
    target_url = args.url
    if not target_url:
        # Fallback to input if not provided
        if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
             # This case handles mixed usage
             pass
        else:
             target_url = input("请输入 Bilibili 视频链接: ").strip()
    
    if not target_url:
        print("❌ 未提供有效的链接，程序退出。")
        sys.exit(1)
        
    download_bilibili_subtitle(target_url, to_txt=args.txt)
