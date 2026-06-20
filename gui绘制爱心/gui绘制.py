import tkinter as tk
import random
import time
import threading
import math

# ================= 配置区域 =================
WINDOW_W = 160      # 小窗口的宽度
WINDOW_H = 80       # 小窗口的高度
SCALE = 14          # 爱心的大小缩放比例
DRAW_SPEED = 80     # 首次绘制速度 (80毫秒/个，较慢)
CORNER_RADIUS = 20  # 圆角半径

# 祝福语列表
MESSAGES = [
    "保持好心情", "顺顺利利", "天天开心", "多喝水哦~",
    "按时吃饭", "早睡早起", "加油鸭", "心想事成",
    "万事如意", "好运连连", "未来可期", "平安喜乐",
    "暴富", "变瘦", "不脱发", "永远热恋"
]

# 冷色系颜色池 (蓝/绿/紫)
COLD_COLORS = [
    '#87CEFA', '#00BFFF', '#1E90FF', '#ADD8E6',  # 蓝色系
    '#98FB98', '#3CB371', '#20B2AA', '#00CED1',  # 绿色系
    '#DDA0DD', '#BA55D3', '#9370DB', '#E6E6FA'   # 紫色系
]


class HeartApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口
        
        # 初始化窗口列表
        self.windows = []
        
        # 获取屏幕尺寸
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        
        # 启动绘制
        self.start_drawing()
        self.root.mainloop()

    def create_rounded_window(self, x, y, text):
       
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)  # 去掉标题栏和边框
        win.attributes("-topmost", True)
        win.attributes("-alpha", 0.9)  # 90% 透明度

        # 随机选择冷色背景
        bg_color = random.choice(COLD_COLORS)
        
        # 使用 Canvas 绘制圆角矩形 (使用多边形平滑曲线模拟)
        canvas = tk.Canvas(win, width=WINDOW_W, height=WINDOW_H, 
                           bg=bg_color, highlightthickness=0)
        canvas.pack(expand=True, fill="both")
        
        # 定义圆角矩形的四个角的控制点
        r = CORNER_RADIUS
        points = [
            r, 0, WINDOW_W - r, 0, WINDOW_W, 0, WINDOW_W, r,
            WINDOW_W, WINDOW_H - r, WINDOW_W, WINDOW_H, WINDOW_W - r, WINDOW_H,
            r, WINDOW_H, 0, WINDOW_H, 0, WINDOW_H - r,
            0, r, 0, 0
        ]
        
        # 绘制平滑的圆角矩形
        canvas.create_polygon(points, smooth=True, fill=bg_color, outline=bg_color)

        # 添加文字标签
        label = tk.Label(
            win, text=text, font=("微软雅黑", 10, "bold"),
            bg=bg_color, fg="#FFFFFF"
        )
        label.place(relx=0.5, rely=0.5, anchor="center")

        # 设置窗口位置和大小
        win.geometry(f"{WINDOW_W}x{WINDOW_H}+{int(x)}+{int(y)}")
        
        # 将窗口加入列表
        self.windows.append(win)

    def start_drawing(self):
        """使用 after 方法启动非阻塞绘制"""
        self.current_t = -math.pi
        self.max_t = math.pi
        self.step = 0.075  # 步长变小，窗口数量增加约30个
        
        # 启动第一帧
        self.root.after(100, self.draw_next_point)

    def draw_next_point(self):
        """递归绘制爱心的每一个点"""
        if self.current_t > self.max_t:
            # 绘制完成，启动打散线程
            self.scatter_windows()
            return

        # 心形公式计算
        x = 16 * (math.sin(self.current_t) ** 3)
        y = -(13 * math.cos(self.current_t) - 5 * math.cos(2 * self.current_t) - 2 * math.cos(3 * self.current_t) - math.cos(4 * self.current_t))

        # 坐标转换：放大 + 居中
        center_x = self.screen_w / 2
        center_y = self.screen_h / 2
        final_x = center_x + x * SCALE - WINDOW_W / 2
        final_y = center_y + y * SCALE - WINDOW_H / 2

        # 随机选取文字并创建窗口
        text = random.choice(MESSAGES)
        self.create_rounded_window(final_x, final_y, text)

        # 递增参数 t
        self.current_t += self.step
        
        # 安排下一帧的绘制
        self.root.after(DRAW_SPEED, self.draw_next_point)

    def scatter_windows(self):
       
        def do_scatter():
            for win in self.windows:
                try:
                    # 生成屏幕范围内的随机坐标
                    rand_x = random.randint(0, self.screen_w - WINDOW_W)
                    rand_y = random.randint(0, self.screen_h - WINDOW_H)
                    # 移动窗口
                    win.geometry(f"{WINDOW_W}x{WINDOW_H}+{rand_x}+{rand_y}")
                    # 稍微延迟一点产生错落感
                    time.sleep(random.uniform(0.01, 0.05))
                except tk.TclError:
                    pass  # 忽略被用户手动关闭的窗口

        # 开启后台守护线程执行打散，避免卡住界面
        thread = threading.Thread(target=do_scatter, daemon=True)
        thread.start()


if __name__ == "__main__":
    app = HeartApp()
