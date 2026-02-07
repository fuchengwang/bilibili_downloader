# 📺 Bilibili 视频下载器

一个简洁高效的 Bilibili 视频下载工具，支持多种登录方式、单视频及合集下载，自动选择最佳画质和编码格式。

![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)

---

## ✨ 功能特性

- 🔐 **多种登录方式**
  - 浏览器授权登录（推荐，支持手机验证码 + 拼图验证）
  - 手机 App 扫码登录
  - 本地 Cookie 文件导入

- 📥 **灵活的下载选项**
  - 支持单视频下载
  - 支持合集/播放列表批量下载
  - 自动识别链接类型

- 🎬 **智能格式选择**
  - 优先选择 H.264 (AVC) 编码，确保 macOS QuickTime 兼容性
  - 优先匹配 AAC 音频编码
  - 最高支持 1080p 分辨率

- 💾 **便捷的文件管理**
  - 默认保存至 `~/Downloads` 目录
  - 合集自动创建独立文件夹
  - Cookie 统一存储在 `~/.bili_cookies.txt`

---

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- pip 或 pnpm（用于安装依赖）

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/fuchengwang/bilibili_downloader.git
cd bilibili_downloader

# 2. 安装依赖
pip install -r requirements.txt
# 或使用 pnpm
# pnpm install yt-dlp requests qrcode
```

### 使用方法

#### 方式一：命令行参数

```bash
python bilibili_downloader.py "https://www.bilibili.com/video/BVxxxxxxx"
```

#### 方式二：交互式输入

```bash
python bilibili_downloader.py
# 根据提示输入视频链接
```

---

## 📖 详细使用说明

### 首次登录

首次运行时，程序会提示你选择登录方式：

```
==============================
      Bilibili 登录中心
==============================
1. 浏览器授权登录 (推荐：支持手机验证码+拼图)
2. 扫码登录 (需要手机 App)
3. 导入已有本地 Cookie (读取 ./cookie 文件)
==============================
请选择登录方式 (输入数字): 
```

| 方式 | 说明 | 适用场景 |
|------|------|----------|
| **1. 浏览器授权** | 自动打开浏览器登录页，完成后自动提取 Cookie | 推荐大多数用户使用 |
| **2. 扫码登录** | 终端显示二维码，用 Bilibili App 扫码 | 无法使用浏览器时 |
| **3. 导入 Cookie** | 从脚本目录下的 `cookie` 文件读取 | 高级用户手动管理 Cookie |

> 💡 登录成功后，Cookie 会自动保存，下次运行无需重复登录。

### 下载合集

当检测到链接是合集/播放列表时，程序会询问：

```
📂 检测到该链接是一个合集: 【合集标题】
请选择下载方式:
1. 下载当前单辑视频
2. 下载整个合集
请输入数字 (1 或 2): 
```

- 选择 `1`：只下载当前分 P 视频
- 选择 `2`：下载整个合集到独立文件夹

---

## 📂 文件结构

```
bilibili_downloader/
├── bilibili_downloader.py   # 主程序
├── requirements.txt         # Python 依赖
└── README.md                # 本文档
```

### Cookie 存储位置

- **自动保存位置**: `~/.bili_cookies.txt`（用户家目录下的隐藏文件）
- **手动导入位置**: 脚本目录下的 `cookie` 文件

### 下载文件位置

- **默认目录**: `~/Downloads/`
- **合集**: `~/Downloads/合集标题/`

---

## ⚙️ 配置说明

如需自定义配置，可直接修改脚本开头的常量：

```python
# Cookie 存储路径
COOKIE_FILE = os.path.expanduser("~/.bili_cookies.txt")

# 默认下载目录
DOWNLOAD_DIR = os.path.expanduser("~/Downloads")

# 手动 Cookie 导入路径（脚本所在目录下的 cookie 文件）
USER_MANUAL_COOKIE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookie")
```

---

## 🔧 常见问题

### Q: 提示"登录状态已失效"怎么办？
A: Cookie 已过期，请重新选择一种方式登录即可。

### Q: 下载的视频无法在 macOS 上播放？
A: 本工具已优先选择 H.264 编码，正常情况下可直接用 QuickTime 播放。如仍有问题，可尝试用 VLC 或 IINA 播放器。

### Q: 如何更新 yt-dlp？
A: 运行以下命令更新到最新版：
```bash
pip install -U yt-dlp
```

### Q: 从浏览器提取 Cookie 失败？
A: 请确保：
1. 已在浏览器中成功登录 Bilibili
2. 浏览器已关闭或刷新保存 Cookie
3. 支持的浏览器：Safari、Chrome、Edge、Firefox

---

## 📜 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m '添加某个特性'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

---

## ⭐ Star History

如果这个项目对你有帮助，请给个 ⭐ 支持一下！

---

## 📮 联系方式

如有问题或建议，欢迎通过 [Issues](https://github.com/fuchengwang/bilibili_downloader/issues) 提交反馈。
