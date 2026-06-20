# -*- coding: utf-8 -*-
"""
美化版爱心祝福弹窗（tkinter）
- 更平滑的圆角和阴影
- 窗口淡入、悬停高亮、点击关闭
- 更柔和的冷色系（自动调整文字颜色）
- 完成绘制后可选择立即随机分布窗口或保留平滑打散动画
"""
import tkinter as tk
import random
import time
import math

# ================= 配置区域 =================
WINDOW_W = 160      # 小窗口的宽度
WINDOW_H = 80       # 小窗口的高度
SCALE = 14          # 爱心的大小缩放比例
DRAW_SPEED = 60     # 每个点绘制间隔 (毫秒)
CORNER_RADIUS = 14  # 圆角半径
FADE_STEPS = 8      # 窗口淡入步数
SHADOW_OFFSET = 6   # 阴影偏移

# 是否在爱心画完后立即随机分布窗口（True：立即分布；False：使用平滑插值动画打散）
SCATTER_IMMEDIATE = True

# 祝福语列表
MESSAGES = [
    "保持好心情", "顺顺利利", "天天开心", "多喝水哦~",
    "按时吃饭", "早睡早起", "加油鸭", "心想事成",
    "万事如意", "好运连连", "未来可期", "平安喜乐",
    "暴富", "变瘦", "不脱发", "永远热恋"
]

# 冷色系颜色池 (蓝/绿/紫) - 作为基色
COLD_COLORS = [
    '#87CEFA', '#00BFFF', '#1E90FF', '#ADD8E6',
    '#98FB98', '#3CB371', '#20B2AA', '#00CED1',
    '#DDA0DD', '#BA55D3', '#9370DB', '#E6E6FA'
]


def lighten(hexcolor, factor=0.15):
    """将十六进制颜色稍微变亮（0-1）"""
    hexcolor = hexcolor.lstrip('#')
    r = int(hexcolor[0:2], 16)
    g = int(hexcolor[2:4], 16)
    b = int(hexcolor[4:6], 16)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return f'#{r:02x}{g:02x}{b:02x}'


def luminance(hexcolor):
    """估算颜色亮度（0-1），用于决定文字颜色黑/白"""
    hexcolor = hexcolor.lstrip('#')
    r = int(hexcolor[0:2], 16) / 255.0
    g = int(hexcolor[2:4], 16) / 255.0
    b = int(hexcolor[4:6], 16) / 255.0
    # 相对亮度
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


class HeartApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口

        # 窗口列表
        self.windows = []

        # 屏幕尺寸
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        # 绘制参数
        self.current_t = -math.pi
        self.max_t = math.pi
        self.step = 0.06  # 步长：较小步长带来更多点和更顺滑的心形

        # 启动绘制
        self.root.after(120, self.draw_next_point)
        self.root.mainloop()

    # ---------- 窗口 / 绘制辅助函数 ----------
    def create_rounded_rect(self, canvas, x1, y1, x2, y2, r, fill, outline=None):
        """在 canvas 上绘制圆角矩形（使用弧和矩形组合）"""
        # 中间矩形
        canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline=outline)
        canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=fill, outline=outline)
        # 四个角的弧
        canvas.create_arc(x2 - 2*r, y1, x2, y1 + 2*r, start=0, extent=90, style='pieslice', fill=fill, outline=fill)
        canvas.create_arc(x1, y1, x1 + 2*r, y1 + 2*r, start=90, extent=90, style='pieslice', fill=fill, outline=fill)
        canvas.create_arc(x1, y2 - 2*r, x1 + 2*r, y2, start=180, extent=90, style='pieslice', fill=fill, outline=fill)
        canvas.create_arc(x2 - 2*r, y2 - 2*r, x2, y2, start=270, extent=90, style='pieslice', fill=fill, outline=fill)

    def create_rounded_window(self, x, y, text):
        """创建具有阴影、圆角、淡入、悬停高亮与点击关闭的小窗口"""
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        # 初始几乎透明，后面淡入
        win.attributes("-alpha", 0.02)

        # 随机选择一个冷色并稍微变亮作为渐变基色
        base = random.choice(COLD_COLORS)
        bg_color = lighten(base, factor=random.uniform(0.06, 0.18))
        # 计算文字颜色：亮色背景用深色文字，暗色背景用白字
        txt_color = "#222222" if luminance(bg_color) > 0.55 else "#FFFFFF"

        # 包含阴影和主体的 Canvas
        # 修复点：不要使用空字符串作为 bg，改为使用窗口默认背景色
        canvas_bg = win.cget("bg")
        canvas = tk.Canvas(win, width=WINDOW_W + SHADOW_OFFSET, height=WINDOW_H + SHADOW_OFFSET,
                           bg=canvas_bg, highlightthickness=0)
        canvas.pack(expand=True, fill="both")

        # 绘制阴影（在主体下方，略微偏移）
        self.create_rounded_rect(canvas,
                                 SHADOW_OFFSET, SHADOW_OFFSET,
                                 WINDOW_W + SHADOW_OFFSET, WINDOW_H + SHADOW_OFFSET,
                                 CORNER_RADIUS, fill="#101820" if luminance(bg_color) > 0.5 else "#000000")

        # 主体（比阴影更亮）
        self.create_rounded_rect(canvas,
                                 0, 0, WINDOW_W, WINDOW_H, CORNER_RADIUS,
                                 fill=bg_color)

        # 文本显示（使用 Label 放置在 Toplevel 上，便于字体渲染）
        label = tk.Label(win, text=text, font=("微软雅黑", 11, "bold"), bg=bg_color, fg=txt_color)
        label.place(x=WINDOW_W/2, y=WINDOW_H/2, anchor="center", width=WINDOW_W - 12)

        # 鼠标交互：悬停时高亮（提高 alpha），离开时恢复；点击关闭
        def on_enter(_):
            try:
                current = float(win.attributes("-alpha"))
                target = min(1.0, current + 0.18)
                win.attributes("-alpha", target)
            except Exception:
                pass

        def on_leave(_):
            try:
                win.attributes("-alpha", 0.9)
            except Exception:
                pass

        def on_click(_):
            try:
                win.destroy()
            except Exception:
                pass

        win.bind("<Enter>", on_enter)
        win.bind("<Leave>", on_leave)
        label.bind("<Button-1>", on_click)
        canvas.bind("<Button-1>", on_click)

        # 设置位置（Toplevel 的 geometry 以主窗口左上为参考）
        geometry_x = int(x)
        geometry_y = int(y)
        win.geometry(f"{WINDOW_W}x{WINDOW_H}+{geometry_x}+{geometry_y}")

        # 保存并启动淡入动画
        self.windows.append(win)
        self.fade_in(win, target_alpha=0.9, steps=FADE_STEPS)

    def fade_in(self, win, target_alpha=0.9, steps=8):
        """在主线程中渐进改变窗口 alpha"""
        try:
            step = (target_alpha - 0.02) / float(steps)
        except ZeroDivisionError:
            step = target_alpha
        def _step(i=0):
            try:
                a = min(target_alpha, 0.02 + step * i)
                win.attributes("-alpha", a)
                if i < steps:
                    win.after(30, _step, i+1)
            except Exception:
                pass
        _step(0)

    # ---------- 爱心绘制逻辑 ----------
    def draw_next_point(self):
        """逐点绘制爱心，并创建小窗口显示文字"""
        if self.current_t > self.max_t:
            # 完成绘制后，稍作停顿然后打散/分布
            self.root.after(600, self.scatter_windows)
            return

        # 心形参数方程
        t = self.current_t
        x = 16 * (math.sin(t) ** 3)
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))

        # 居中与缩放
        center_x = self.screen_w / 2
        center_y = self.screen_h / 2 - 40  # 上移一点，使整体更居中视觉
        final_x = center_x + x * SCALE - WINDOW_W / 2
        final_y = center_y + y * SCALE - WINDOW_H / 2

        # 随机选一条祝福并创建窗口
        text = random.choice(MESSAGES)
        self.create_rounded_window(final_x, final_y, text)

        # 递增 t：使用可变步长在曲线弯曲处加密点
        curvature = abs(math.sin(t)) + abs(math.cos(t))
        dynamic_step = max(0.035, self.step * (0.9 - 0.35 * (curvature - 0.5)))
        self.current_t += dynamic_step

        # 安排下一帧
        self.root.after(DRAW_SPEED, self.draw_next_point)

    # ---------- 打散 / 随机分布 ----------
    def scatter_windows(self):
        """根据配置，选择立即随机分布或使用平滑插值动画打散窗口"""
        if SCATTER_IMMEDIATE:
            # 立即随机分布：直接为每个窗口设置随机位置（在主线程）
            for w in list(self.windows):
                try:
                    rx = random.randint(0, max(0, self.screen_w - WINDOW_W))
                    ry = random.randint(0, max(0, self.screen_h - WINDOW_H))
                    w.geometry(f"{WINDOW_W}x{WINDOW_H}+{rx}+{ry}")
                except tk.TclError:
                    # 窗口可能已被关闭，忽略
                    continue
            return

        # 否则使用平滑动画（保留原有插值版本）
        targets = []
        for _ in self.windows:
            tx = random.randint(0, max(0, self.screen_w - WINDOW_W))
            ty = random.randint(0, max(0, self.screen_h - WINDOW_H))
            targets.append((tx, ty))

        duration = 700  # 整体动画时长 ms
        frames = 18
        interval = max(8, duration // frames)

        start_positions = []
        for w in self.windows:
            try:
                geom = w.geometry()  # e.g. "160x80+123+456"
                parts = geom.split('+')
                if len(parts) >= 3:
                    sx = int(parts[1])
                    sy = int(parts[2])
                else:
                    sx = random.randint(0, max(0, self.screen_w - WINDOW_W))
                    sy = random.randint(0, max(0, self.screen_h - WINDOW_H))
            except Exception:
                sx = random.randint(0, max(0, self.screen_w - WINDOW_W))
                sy = random.randint(0, max(0, self.screen_h - WINDOW_H))
            start_positions.append((sx, sy))

        def animate_frame(frame_idx=0):
            if frame_idx > frames:
                return
            for idx, w in enumerate(self.windows):
                try:
                    sx, sy = start_positions[idx]
                    tx, ty = targets[idx]
                    nx = int(sx + (tx - sx) * (frame_idx / frames))
                    ny = int(sy + (ty - sy) * (frame_idx / frames))
                    w.geometry(f"{WINDOW_W}x{WINDOW_H}+{nx}+{ny}")
                except tk.TclError:
                    continue
            if frame_idx < frames:
                self.root.after(interval, animate_frame, frame_idx + 1)

        animate_frame(0)


if __name__ == "__main__":
    HeartApp()
