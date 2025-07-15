import tkinter as tk
import random



class RandomButtonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("随机位置交替按钮")
        self.root.geometry("800x400")  # 更大的窗口空间

        """
        初始化主窗口和应用程序状态
        
        参数:
            master: 父窗口 (Tk 根窗口)
        """
        # 设置主窗口
        self.root = root
        self.root.title("afeel")
        self.root.geometry("600x400")  # 设置更大的窗口尺寸以便显示背景文本
        
        # 初始化按钮位置变量
        self.button_pos = (100, 100)  # 修复: 提前初始化位置变量
        
        # 创建背景标签 - 显示"你输了"大文字
        self.bg_label = tk.Label(
            root,
            text="你输了",  # 背景文字内容
            font=("Arial", 120, "bold"),  # 大号粗体
            fg="#000000",  # 红色字体
            bg='pink', 
             height=90,
             width=90, # 浅灰色背景
            anchor="center"  # 文字居中
        )
        self.bg_label.place(relx=0.5, rely=0.5, anchor="center")  # 固定在窗口中央
        
        
        # 按钮配置
        self.button_configs = [
            {"text": "点击我消失", "bg": "lightpink", "command": self.next_button},
            {"text": "现在点击我", "bg": "lightpink", "command": self.next_button},
            {"text": "再次点击", "bg": "lightpink", "command": self.next_button}
        ]
        self.current_index = 0
        
        # 创建第一个按钮
        self.create_random_button()
    
    def create_random_button(self):
        """在随机位置创建新按钮"""
        # 获取窗口尺寸
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # 确保窗口至少有一定大小
        if window_width < 100 or window_height < 100:
            window_width = 600
            window_height = 400
        
        # 创建按钮（如果已有按钮则先销毁）
        if hasattr(self, 'current_button'):
            self.current_button.destroy()
        
        config = self.button_configs[self.current_index]
        self.current_button = tk.Button(
            self.root, 
            text=config["text"], 
            command=config["command"],
            bg=config["bg"],
            font=("宋体", 14),
           
        )
        
        # 随机位置放置按钮
        max_x = max(50, window_width - 150)  # 确保按钮完全可见
        max_y = max(50, window_height - 50)
        pos_x = random.randint(20, max_x)
        pos_y = random.randint(20, max_y)
        
        self.current_button.place(x=pos_x, y=pos_y)
    
    def next_button(self):
        """切换到下一个按钮"""
        # 循环按钮索引
        self.current_index = (self.current_index + 1) % len(self.button_configs)
        self.create_random_button()

if __name__ == "__main__":
    root = tk.Tk()
    app = RandomButtonApp(root)
    root.mainloop()
  