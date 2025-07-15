import tkinter as tk
import random
from concurrent.futures import ThreadPoolExecutor
import time
xc=50


root=tk.Tk()
root.title('按钮跳动')
    
root.geometry("250x200")


root.attributes('-alpha',0.85)
def jumping():
    pass
bu1=tk.Button(root,text='没有',command=jumping)
a=root.winfo_screenwidth()
b=root.winfo_screenheight()
ran_a=random.randint(0,a)
ran_b=random.randint(0,b)
   
tk.Label(root,text='你失败过吗？',bg='pink',height=50,width=50,font=('宋体',20)).pack()
root.mainloop()

with ThreadPoolExecutor(max_workers=xc) as tp:
    for i in range(xc):
        tp.submit(root)  
        time.sleep(0.1)



