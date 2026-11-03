#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Kuimuztion
#
# xdl - 下载 X (Twitter) 帖子中的图片、视频和 GIF
# 本程序是自由软件，依据 GNU GPL 第 3 版（仅此版本）发布。

import argparse
import os
import re
import shutil
import subprocess
import sys

STATUS_RE = re.compile(r"/status/(\d+)")


def tweet_id(url):
        m = STATUS_RE.search(url)
        return m.group(1) if m else None


def snapshot(directory):
        """返回目录下所有文件路径的集合，用于找出本次新下载的文件。"""
        files = set()
        for root, _, names in os.walk(directory):
                for name in names:
                        files.add(os.path.join(root, name))
        return files


def run(cmd):
        print("+", " ".join(cmd))
        try:
                return subprocess.run(cmd).returncode == 0
        except FileNotFoundError:
                print(f"未找到命令: {cmd[0]}", file=sys.stderr)
                return False


def add_auth(cmd, args):
        if args.cookies:
                cmd += ["--cookies", args.cookies]
        if args.cookies_from_browser:
                cmd += ["--cookies-from-browser", args.cookies_from_browser]
        return cmd


def dl_gallery_dl(url, outdir, args):
        cmd = add_auth(["gallery-dl", "-D", outdir], args)
        cmd.append(url)
        return run(cmd)


def dl_yt_dlp(url, outdir, args):
        cmd = add_auth(
                [
                        "yt-dlp",
                        "--no-playlist",
                        "-f", "bv*+ba/b",
                        "--merge-output-format", "mp4",
                        "-o", os.path.join(outdir, "%(id)s.%(ext)s"),
                ],
                args,
        )
        cmd.append(url)
        return run(cmd)


def fetch(url, outdir, args):
        """按引擎顺序尝试下载，返回本次新增的文件集合。"""
        if args.engine == "auto":
                engines = ["gallery-dl", "yt-dlp"]
        else:
                engines = [args.engine]

        before = snapshot(outdir)
        for eng in engines:
                if not shutil.which(eng):
                        print(f"跳过 {eng}：未安装", file=sys.stderr)
                        continue
                if eng == "gallery-dl":
                        dl_gallery_dl(url, outdir, args)
                else:
                        dl_yt_dlp(url, outdir, args)
                new = snapshot(outdir) - before
                if new:
                        return new
        return set()


def to_gif(src):
        dst = os.path.splitext(src)[0] + ".gif"
        vf = (
                "fps=15,scale=480:-1:flags=lanczos,"
                "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
        )
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", vf, dst]
        return run(cmd)


def process(url, args):
        tid = tweet_id(url)
        if not tid:
                print(f"无法解析帖子 ID，跳过: {url}", file=sys.stderr)
                return False

        outdir = os.path.join(args.outdir, tid)
        os.makedirs(outdir, exist_ok=True)

        new = fetch(url, outdir, args)
        if not new:
                print(f"未下载到任何文件: {url}", file=sys.stderr)
                return False

        for path in sorted(new):
                print("已保存:", path)
                if args.gif and path.lower().endswith((".mp4", ".webm")):
                        if to_gif(path):
                                print("已转换:", os.path.splitext(path)[0] + ".gif")
        return True


def main():
        parser = argparse.ArgumentParser(description="下载 X 帖子中的图片、视频和 GIF")
        parser.add_argument("urls", nargs="*", help="帖子链接，可写多个")
        parser.add_argument("-f", "--file", help="从文件读取链接，每行一个，# 开头为注释")
        parser.add_argument("-o", "--outdir", default="xdl_out", help="保存目录（默认 xdl_out）")
        parser.add_argument("--gif", action="store_true", help="把视频转换为 GIF（需要 ffmpeg）")
        parser.add_argument("--engine", choices=["auto", "gallery-dl", "yt-dlp"],
                            default="auto", help="下载引擎（默认 auto，先 gallery-dl 后 yt-dlp）")
        parser.add_argument("--cookies", metavar="FILE", help="Netscape 格式的 cookies 文件")
        parser.add_argument("--cookies-from-browser", metavar="BROWSER",
                            help="从浏览器读取 cookies，如 firefox、chromium")
        args = parser.parse_args()

        urls = list(args.urls)
        if args.file:
                with open(args.file, encoding="utf-8") as fh:
                        urls += [ln.strip() for ln in fh
                                 if ln.strip() and not ln.lstrip().startswith("#")]
        if not urls:
                parser.error("请提供至少一个链接")

        ok = sum(process(u, args) for u in urls)
        print(f"\n完成：{ok}/{len(urls)} 个帖子")
        return 0 if ok == len(urls) else 1


if __name__ == "__main__":
        sys.exit(main())
