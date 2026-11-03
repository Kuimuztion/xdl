# xdl

下载 X (Twitter) 帖子中的图片、视频和 GIF。

## 安装（Fedora 44）

    sudo dnf install pipx ffmpeg
    pipx ensurepath
    source ~/.bashrc
    pipx install gallery-dl
    pipx install yt-dlp

`ffmpeg` 仅在使用 `--gif` 时需要。`pipx ensurepath` 之后需要重新打开终端，或执行 `source ~/.bashrc`，让 `~/.local/bin` 进入 PATH。

## 用法

    chmod +x xdl.py
    ./xdl.py https://x.com/i/status/2117246495770751085
    ./xdl.py https://x.com/xxx/status/123 --gif -o ~/Pictures/x
    ./xdl.py -f links.txt --gif

文件按帖子 ID 分目录保存在输出目录下。

## 需要登录的内容

部分内容需要登录才能看到。可在浏览器登录 X 后导出 cookies：

    ./xdl.py URL --cookies-from-browser firefox
    ./xdl.py URL --cookies cookies.txt

## 注意

- X 经常改版，下载失败时先执行 `pipx upgrade gallery-dl` 和 `pipx upgrade yt-dlp`。
- 请仅将下载内容用于个人用途，并尊重原作者的版权。
- 许可证：GPL-3.0-only。
