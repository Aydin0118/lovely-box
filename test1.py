import tkinter as tk
import random


class RandomButtonApp:
    def __init__(self, master):
        """
        初始化主窗口和应用程序状态
        
        参数:
            master: 父窗口 (Tk 根窗口)
        """
        # 设置主窗口
        self.master = master
        self.master.title("afeel")
        self.master.geometry("600x400")  # 设置更大的窗口尺寸以便显示背景文本
        
        # 初始化按钮位置变量
        self.button_pos = (100, 100)  # 修复: 提前初始化位置变量
        
        # 创建背景标签 - 显示"你输了"大文字
        self.bg_label = tk.Label(
            master,
            text="你输了",  # 背景文字内容
            font=("Arial", 120, "bold"),  # 大号粗体
            fg="#000000",  # 红色字体
            bg='pink', 
             height=90,
             width=90, # 浅灰色背景
            anchor="center"  # 文字居中
        )
        self.bg_label.place(relx=0.5, rely=0.5, anchor="center")  # 固定在窗口中央
        
        # 按钮配置列表 - 定义按钮属性序列
        self.button_configs = [
            {"text": "按钮1", "bg": "lightcyan", "font": ("Arial", 14)},
            {"text": "按钮2", "bg": "lightcyan", "font": ("Arial", 14)},
            {"text": "按钮3", "bg": "lightcyan", "font": ("Arial", 14)}
        ]
        
        self.current_index = 0  # 当前按钮索引
        
        # 修复: 确保按钮已经创建后再进行位置计算
        self.button = None  # 初始化按钮变量
        
        # 创建第一个随机按钮
        self.create_random_button()
        
        # 绑定窗口大小变化事件 - 确保按钮位置正确
        self.master.bind("<Configure>", self.on_window_resize)
    
    def on_window_resize(self, event):
        """
        窗口大小变化时的回调函数
        确保按钮保持在窗口内
        
        参数:
            event: 窗口调整大小事件对象
        """
        # 只有窗口实际改变大小时才重新定位按钮
        if event.widget == self.master and self.button:
            # 重新计算按钮位置
            self.position_button()

    def create_random_button(self):
        """
        创建并放置随机按钮
        """
        # 获取当前按钮配置
        config = self.button_configs[self.current_index]
        
        # 创建按钮组件
        self.button = tk.Button(
            self.master,
            text=config["text"],
            bg=config["bg"],
            font=config["font"],
            command=self.next_button  # 点击时触发切换到下一个按钮
        )
        
        # 定位按钮在窗口内随机位置
        self.position_button()
    
    def position_button(self):
        """
        定位按钮到窗口内的随机位置
        """
        if not self.button:
            return
            
        # 获取当前窗口尺寸
        win_width = self.master.winfo_width()
        win_height = self.master.winfo_height()
        
        # 确保窗口已有实际尺寸
        if win_width > 1 and win_height > 1:
            # 获取按钮推荐尺寸
            btn_width = self.button.winfo_reqwidth()
            btn_height = self.button.winfo_reqheight()
            
            # 计算有效区域（确保按钮完全可见）
            max_x = max(1, win_width - btn_width)
            max_y = max(1, win_height - btn_height)
            
            # 生成随机位置
            rand_x = random.randint(0, max_x)
            rand_y = random.randint(0, max_y)
            
            # 记录位置
            self.button_pos = (rand_x, rand_y)
        else:
            # 使用之前的位置或默认值
            rand_x, rand_y = self.button_pos
        
        # 使用place布局管理器设置随机位置
        self.button.place(x=rand_x, y=rand_y)

    def next_button(self):
        """
        点击按钮后的回调函数 - 切换到下一个按钮
        """
        if self.button:
            # 销毁当前按钮
            self.button.destroy()
        
        # 更新到下一个按钮配置（循环）
        self.current_index = (self.current_index + 1) % len(self.button_configs)
        
        # 使用after代替sleep，避免阻塞UI线程
        self.master.after(200, self.create_random_button)

# 主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x400")  # 初始化窗口尺寸
    app = RandomButtonApp(root)
    root.mainloop()
