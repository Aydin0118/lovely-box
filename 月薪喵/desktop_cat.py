"""
月薪喵 - 桌面跳舞宠物 (GIF动画版)
使用预制GIF动画的桌面宠物猫，支持多种状态和丰富交互
支持循环背景音乐播放
"""
import tkinter as tk
from tkinter import Menu
from PIL import Image, ImageTk, ImageDraw
import random
import math
import sys
import os
import time
import threading

# 尝试导入音频库
try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
    try:
        import winsound
        HAS_WINSOUND = True
    except ImportError:
        HAS_WINSOUND = False


def resource_path(relative_path):
    """获取资源文件的绝对路径（支持PyInstaller打包）"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)


class GifAnimation:
    """GIF动画管理器 - 从GIF文件提取所有帧"""

    def __init__(self, gif_path, target_size=130):
        self.frames = []
        self.durations = []
        self.current_frame = 0

        try:
            img = Image.open(gif_path)
            # 提取所有帧
            frame_count = 0
            while True:
                try:
                    img.seek(frame_count)
                    # 获取帧持续时间（毫秒）
                    duration = img.info.get('duration', 100)
                    self.durations.append(max(duration, 30))  # 最少30ms

                    # 转换为RGBA
                    frame = img.copy().convert("RGBA")
                    # 缩放到目标大小
                    frame.thumbnail((target_size, target_size), Image.LANCZOS)
                    # 居中放到正方形画布
                    canvas = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
                    ox = (target_size - frame.width) // 2
                    oy = (target_size - frame.height) // 2
                    canvas.paste(frame, (ox, oy), frame)
                    self.frames.append(canvas)

                    frame_count += 1
                except EOFError:
                    break

        except Exception as e:
            print(f"加载GIF失败 {gif_path}: {e}")
            # 创建一个占位帧
            placeholder = Image.new("RGBA", (target_size, target_size), (255, 100, 100, 200))
            self.frames.append(placeholder)
            self.durations.append(100)

    def get_frame(self):
        """获取当前帧"""
        if not self.frames:
            return None
        return self.frames[self.current_frame % len(self.frames)]

    def advance(self):
        """前进到下一帧"""
        self.current_frame = (self.current_frame + 1) % len(self.frames)

    def reset(self):
        """重置到第一帧"""
        self.current_frame = 0

    def get_duration(self):
        """获取当前帧的持续时间"""
        if not self.durations:
            return 100
        return self.durations[self.current_frame % len(self.durations)]

    @property
    def total_duration(self):
        """整个动画一次循环的总时长（毫秒）"""
        return sum(self.durations) if self.durations else 1000

    @property
    def frame_count(self):
        return len(self.frames)


class Particle:
    """粒子效果基类"""

    def __init__(self, x, y, lifetime=30):
        self.x = x
        self.y = y
        self.lifetime = lifetime
        self.age = 0
        self.alive = True

    def update(self):
        self.age += 1
        if self.age >= self.lifetime:
            self.alive = False

    def get_alpha(self):
        if self.age < self.lifetime * 0.3:
            return 1.0
        return max(0, 1.0 - (self.age - self.lifetime * 0.3) / (self.lifetime * 0.7))


class HeartParticle(Particle):
    """爱心粒子"""

    def __init__(self, x, y):
        super().__init__(x, y, lifetime=40)
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-3, -1.5)
        self.size = random.randint(8, 14)

    def update(self):
        super().update()
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.02


class StarParticle(Particle):
    """星星粒子"""

    def __init__(self, x, y):
        super().__init__(x, y, lifetime=25)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.size = random.randint(4, 8)

    def update(self):
        super().update()
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.92
        self.vy *= 0.92


class DesktopCat:
    """桌面宠物猫主类 - GIF动画版"""

    # 状态常量
    STATE_IDLE = "idle"
    STATE_WALKING_LEFT = "walking_left"
    STATE_WALKING_RIGHT = "walking_right"
    STATE_DANCING = "dancing"
    STATE_JUMPING = "jumping"
    STATE_WAVING = "waving"
    STATE_WAITING = "waiting"
    STATE_FAILED = "failed"
    STATE_REVIEW = "review"
    STATE_FALLING = "falling"

    # 配置
    CAT_SIZE = 130
    MOVE_SPEED = 3
    FRAME_DELAY = 80  # 基础帧间隔
    TRANSPARENT_COLOR = "#01FF00"
    GRAVITY = 1.2
    MAX_FALL_SPEED = 18
    GROUND_Y_OFFSET = 60

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("月薪喵")

        # 窗口配置
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", self.TRANSPARENT_COLOR)
        self.root.config(bg=self.TRANSPARENT_COLOR)

        # 屏幕尺寸
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # 窗口大小
        self.win_size = self.CAT_SIZE + 60
        self.root.geometry(f"{self.win_size}x{self.win_size}")

        # 初始位置
        self.x = (self.screen_width - self.win_size) // 2
        self.y = self.screen_height - self.win_size - self.GROUND_Y_OFFSET
        self.root.geometry(f"+{self.x}+{self.y}")

        # 画布
        self.canvas = tk.Canvas(
            self.root,
            width=self.win_size,
            height=self.win_size,
            bg=self.TRANSPARENT_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack()

        # 加载GIF动画
        self.load_animations()

        # 状态机
        self.state = self.STATE_IDLE
        self.frame_count = 0

        # 走动相关
        self.target_x = self.x

        # 物理相关
        self.velocity_y = 0
        self.velocity_x = 0

        # 拖拽相关
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.drag_velocity_x = 0
        self.drag_velocity_y = 0

        # 交互
        self.pet_count = 0
        self.particles = []

        # 绑定事件
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.canvas.bind("<ButtonPress-3>", self.on_right_click)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)

        # 右键菜单
        self.menu = Menu(self.root, tearoff=0)
        self.menu.add_command(label="🐱 月薪喵在此！", state="disabled")
        self.menu.add_separator()
        self.menu.add_command(label="💃 跳舞", command=self.force_dance)
        self.menu.add_command(label="🚶 散步", command=self.force_walk)
        self.menu.add_command(label="🦘 跳跳", command=self.force_jump)
        self.menu.add_command(label="👋 招手", command=self.force_wave)
        self.menu.add_command(label="⏳ 等待", command=self.force_wait)
        self.menu.add_command(label="😿 失败", command=self.force_failed)
        self.menu.add_command(label="🔍 审查", command=self.force_review)
        self.menu.add_separator()
        self.menu.add_command(label=f"❤️ 被摸次数: {self.pet_count}", state="disabled")
        self.menu.add_separator()
        self.music_playing = False
        self.menu.add_command(label="🎵 播放音乐", command=self.toggle_music)
        self.menu.add_command(label="❌ 退出", command=self.quit)

        # 显示
        self.current_photo = None

        # 启动背景音乐
        self.init_music()

        # 开始
        self.schedule_state_change()
        self.animate()

    def _find_bgm(self):
        """查找背景音乐文件（优先mp3，其次wav）"""
        for name in ("music.mp3", "bgm.mp3", "bgm.wav"):
            path = resource_path(name)
            if os.path.exists(path):
                return path
        return None

    def init_music(self):
        """初始化并播放背景音乐"""
        bgm_path = self._find_bgm()
        if not bgm_path:
            print("提示: 未找到背景音乐文件，跳过")
            return

        if HAS_PYGAME:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
                pygame.mixer.music.load(bgm_path)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)  # -1 表示无限循环
                self.music_playing = True
                self._update_music_menu()
            except Exception as e:
                print(f"pygame音乐初始化失败: {e}")
        elif HAS_WINSOUND and bgm_path.endswith(".wav"):
            # winsound 只支持wav格式
            self.music_playing = True
            self._update_music_menu()
            self._winsound_thread = threading.Thread(
                target=self._winsound_loop, args=(bgm_path,), daemon=True
            )
            self._winsound_thread.start()

    def _winsound_loop(self, path):
        """winsound 后台循环播放"""
        while self.music_playing:
            try:
                winsound.PlaySound(path, winsound.SND_FILENAME)
            except Exception:
                break

    def toggle_music(self):
        """切换音乐开关"""
        if self.music_playing:
            self.stop_music()
        else:
            self.start_music()

    def start_music(self):
        """开始播放音乐"""
        bgm_path = self._find_bgm()
        if not bgm_path:
            return

        if HAS_PYGAME:
            try:
                pygame.mixer.music.load(bgm_path)
                pygame.mixer.music.play(-1)
                self.music_playing = True
            except Exception:
                pass
        elif HAS_WINSOUND and bgm_path.endswith(".wav"):
            self.music_playing = True
            self._winsound_thread = threading.Thread(
                target=self._winsound_loop, args=(bgm_path,), daemon=True
            )
            self._winsound_thread.start()
        self._update_music_menu()

    def stop_music(self):
        """停止音乐"""
        self.music_playing = False
        if HAS_PYGAME:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        elif HAS_WINSOUND:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
        self._update_music_menu()

    def _update_music_menu(self):
        """更新菜单中音乐按钮的文字"""
        label = "🔇 关闭音乐" if self.music_playing else "🎵 播放音乐"
        # 音乐菜单项的索引（倒数第2个，退出前面）
        try:
            self.menu.entryconfigure(11, label=label)
        except Exception:
            pass

    def load_animations(self):
        """加载所有GIF动画"""
        gifs_dir = resource_path("gifs")
        self.animations = {}

        gif_mapping = {
            self.STATE_IDLE: "idle.gif",
            self.STATE_WALKING_LEFT: "running-left.gif",
            self.STATE_WALKING_RIGHT: "running-right.gif",
            self.STATE_DANCING: "running.gif",  # 用running作为跳舞
            self.STATE_JUMPING: "jumping.gif",
            self.STATE_WAVING: "waving.gif",
            self.STATE_WAITING: "waiting.gif",
            self.STATE_FAILED: "failed.gif",
            self.STATE_REVIEW: "review.gif",
        }

        for state, filename in gif_mapping.items():
            path = os.path.join(gifs_dir, filename)
            if os.path.exists(path):
                self.animations[state] = GifAnimation(path, self.CAT_SIZE)
            else:
                print(f"警告: 找不到 {path}")

        # falling状态复用jumping动画
        if self.STATE_JUMPING in self.animations:
            self.animations[self.STATE_FALLING] = self.animations[self.STATE_JUMPING]

    def _compose_frame(self, cat_img, offset_y=0, offset_x=0):
        """将猫猫图片合成到带透明色背景的帧上，包含粒子效果"""
        bg = Image.new("RGBA", (self.win_size, self.win_size), (1, 255, 0, 255))
        cx = (self.win_size - cat_img.width) // 2 + offset_x
        cy = (self.win_size - cat_img.height) // 2 + offset_y
        if cat_img.mode == "RGBA":
            bg.paste(cat_img, (cx, cy), cat_img)
        else:
            bg.paste(cat_img, (cx, cy))

        # 绘制粒子
        if self.particles:
            draw = ImageDraw.Draw(bg)
            for p in self.particles:
                alpha = p.get_alpha()
                if alpha <= 0:
                    continue
                px = int(p.x - self.x + self.win_size // 2)
                py = int(p.y - self.y + self.win_size // 2)

                if isinstance(p, HeartParticle):
                    self._draw_heart(draw, px, py, p.size, alpha)
                elif isinstance(p, StarParticle):
                    self._draw_star(draw, px, py, p.size, alpha)

        # 转为RGB
        result = Image.new("RGB", (self.win_size, self.win_size), (1, 255, 0))
        result.paste(bg, (0, 0), bg)
        return result

    def _draw_heart(self, draw, x, y, size, alpha):
        """绘制爱心"""
        color = (255, int(80 * alpha + 50), int(80 * alpha + 50))
        r = size // 3
        draw.ellipse([x - r * 2, y - r, x, y + r], fill=color)
        draw.ellipse([x, y - r, x + r * 2, y + r], fill=color)
        draw.polygon([(x - r * 2, y), (x + r * 2, y), (x, y + r * 2)], fill=color)

    def _draw_star(self, draw, x, y, size, alpha):
        """绘制星星"""
        color = (255, int(220 * alpha), int(50 * alpha))
        draw.line([(x - size, y), (x + size, y)], fill=color, width=2)
        draw.line([(x, y - size), (x, y + size)], fill=color, width=2)
        s2 = size // 2
        draw.line([(x - s2, y - s2), (x + s2, y + s2)], fill=color, width=1)
        draw.line([(x + s2, y - s2), (x - s2, y + s2)], fill=color, width=1)

    def animate(self):
        """主动画循环"""
        self.frame_count += 1

        if not self.dragging:
            if self.state == self.STATE_FALLING:
                self._update_falling()
            elif self.state in (self.STATE_WALKING_LEFT, self.STATE_WALKING_RIGHT):
                self._update_walking()

        # 更新粒子
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]

        # 获取当前动画帧
        anim = self.animations.get(self.state)
        if anim:
            frame = anim.get_frame()
            anim.advance()
        else:
            # 回退到idle
            anim = self.animations.get(self.STATE_IDLE)
            frame = anim.get_frame() if anim else Image.new("RGBA", (self.CAT_SIZE, self.CAT_SIZE), (255, 0, 0, 200))
            if anim:
                anim.advance()

        # 下落时添加旋转效果
        offset_y = 0
        offset_x = 0
        if self.state == self.STATE_FALLING:
            angle = 5 * math.sin(self.frame_count * 0.5)
            frame = frame.rotate(angle, expand=True, resample=Image.BICUBIC)

        # 合成显示
        display = self._compose_frame(frame, offset_y, offset_x)
        self.current_photo = ImageTk.PhotoImage(display)

        # 更新画布
        self.canvas.delete("all")
        self.canvas.create_image(
            self.win_size // 2, self.win_size // 2, image=self.current_photo
        )

        # 根据GIF帧速率决定下一帧延迟
        delay = self.FRAME_DELAY
        if anim and anim.durations:
            delay = anim.get_duration()

        self.root.after(delay, self.animate)

    def _update_falling(self):
        """更新下落物理"""
        self.velocity_y = min(self.velocity_y + self.GRAVITY, self.MAX_FALL_SPEED)
        self.x += int(self.velocity_x)
        self.y += int(self.velocity_y)
        self.velocity_x *= 0.95

        ground_y = self.screen_height - self.win_size - self.GROUND_Y_OFFSET
        if self.y >= ground_y:
            self.y = ground_y
            self.velocity_y = 0
            self.velocity_x = 0
            self.change_state(self.STATE_IDLE)
            self.schedule_state_change()

        if self.x <= 0:
            self.x = 0
            self.velocity_x = abs(self.velocity_x) * 0.5
        elif self.x >= self.screen_width - self.win_size:
            self.x = self.screen_width - self.win_size
            self.velocity_x = -abs(self.velocity_x) * 0.5

        self.root.geometry(f"+{self.x}+{self.y}")

    def _update_walking(self):
        """更新走动"""
        dx = self.target_x - self.x
        if abs(dx) < self.MOVE_SPEED * 2:
            self.change_state(self.STATE_IDLE)
            self.schedule_state_change()
        else:
            step = self.MOVE_SPEED if dx > 0 else -self.MOVE_SPEED
            self.x += step
            self.root.geometry(f"+{self.x}+{self.y}")

    def schedule_state_change(self):
        """定时切换状态 - 确保至少播放完一个完整动画循环"""
        # 获取当前动画的一次循环时长
        anim = self.animations.get(self.state)
        min_duration = anim.total_duration * 2 if anim else 2000  # 至少播放2遍

        # 额外随机延迟
        extra_delays = {
            self.STATE_IDLE: (1000, 3000),
            self.STATE_DANCING: (2000, 5000),
            self.STATE_JUMPING: (1000, 2000),
            self.STATE_WAVING: (2000, 4000),
            self.STATE_WAITING: (2000, 5000),
            self.STATE_FAILED: (1500, 3000),
            self.STATE_REVIEW: (2000, 4000),
        }
        extra = extra_delays.get(self.state, (1000, 3000))
        delay = min_duration + random.randint(*extra)
        self.root.after(delay, self.auto_state_change)

    def auto_state_change(self):
        """自动切换到下一个状态"""
        if self.dragging:
            self.root.after(1000, self.auto_state_change)
            return

        if self.state == self.STATE_IDLE:
            # 随机选择下一个动作
            choices = [
                (self.STATE_WALKING_LEFT, 0.2),
                (self.STATE_WALKING_RIGHT, 0.2),
                (self.STATE_DANCING, 0.2),
                (self.STATE_JUMPING, 0.1),
                (self.STATE_WAVING, 0.15),
                (self.STATE_WAITING, 0.1),
                (self.STATE_REVIEW, 0.05),
            ]
            r = random.random()
            cumulative = 0
            next_state = self.STATE_WALKING_RIGHT
            for state, prob in choices:
                cumulative += prob
                if r < cumulative:
                    next_state = state
                    break
            self.change_state(next_state)
        else:
            self.change_state(self.STATE_IDLE)

        self.schedule_state_change()

    def change_state(self, new_state):
        """切换状态"""
        self.state = new_state

        # 重置动画帧
        anim = self.animations.get(new_state)
        if anim:
            anim.reset()

        if new_state == self.STATE_WALKING_LEFT:
            margin = 80
            self.target_x = random.randint(margin, max(margin + 1, self.x - 200))
        elif new_state == self.STATE_WALKING_RIGHT:
            margin = 80
            self.target_x = random.randint(
                min(self.x + 50, self.screen_width - self.win_size - margin),
                self.screen_width - self.win_size - margin
            )

    # --- 右键菜单命令 ---

    def force_dance(self):
        self.change_state(self.STATE_DANCING)
        self.schedule_state_change()

    def force_walk(self):
        if random.random() < 0.5:
            self.change_state(self.STATE_WALKING_LEFT)
        else:
            self.change_state(self.STATE_WALKING_RIGHT)

    def force_jump(self):
        self.change_state(self.STATE_JUMPING)
        self.schedule_state_change()

    def force_wave(self):
        self.change_state(self.STATE_WAVING)
        self.schedule_state_change()

    def force_wait(self):
        self.change_state(self.STATE_WAITING)
        self.schedule_state_change()

    def force_failed(self):
        self.change_state(self.STATE_FAILED)
        self.schedule_state_change()

    def force_review(self):
        self.change_state(self.STATE_REVIEW)
        self.schedule_state_change()

    # --- 鼠标交互 ---

    def on_mouse_press(self, event):
        self.dragging = True
        self.drag_offset_x = event.x
        self.drag_offset_y = event.y
        self.drag_velocity_x = 0
        self.drag_velocity_y = 0

    def on_drag_motion(self, event):
        if self.dragging:
            new_x = self.root.winfo_x() + event.x - self.drag_offset_x
            new_y = self.root.winfo_y() + event.y - self.drag_offset_y
            self.drag_velocity_x = (new_x - self.x) * 0.5
            self.drag_velocity_y = (new_y - self.y) * 0.5
            self.x = new_x
            self.y = new_y
            self.root.geometry(f"+{self.x}+{self.y}")

    def on_mouse_release(self, event):
        if self.dragging:
            self.dragging = False
            ground_y = self.screen_height - self.win_size - self.GROUND_Y_OFFSET
            if self.y < ground_y - 20:
                self.velocity_y = self.drag_velocity_y
                self.velocity_x = self.drag_velocity_x
                self.change_state(self.STATE_FALLING)
            else:
                self.y = ground_y
                self.root.geometry(f"+{self.x}+{self.y}")
                self.change_state(self.STATE_IDLE)
                self.schedule_state_change()

    def on_double_click(self, event):
        """双击抚摸"""
        self.pet_count += 1
        # 产生爱心
        center_x = self.x + self.win_size // 2
        center_y = self.y + self.win_size // 4
        for _ in range(5):
            px = center_x + random.randint(-20, 20)
            py = center_y + random.randint(-10, 10)
            self.particles.append(HeartParticle(px, py))
        # 更新菜单
        self.menu.entryconfigure(8, label=f"❤️ 被摸次数: {self.pet_count}")
        # 切换到招手
        self.change_state(self.STATE_WAVING)
        self.schedule_state_change()

    def on_right_click(self, event):
        self.menu.post(event.x_root, event.y_root)

    def quit(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    cat = DesktopCat()
    cat.run()
