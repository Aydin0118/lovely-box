import tkinter as tk
import random
from concurrent.futures import ThreadPoolExecutor
#import time
xc=100

def root():
    root=tk.Tk()
    root.title('love')
    #root.iconbitmap()
    try:
        root.iconbitmap(r'D:\党培祥\tkinter教程\窗口跳动\狗.ico')
    except:
      
        pass



    root.attributes('-alpha',0.85)
    a=root.winfo_screenwidth()
    b=root.winfo_screenheight()
    ran_a=random.randint(0,a)
    ran_b=random.randint(0,b)
    root.geometry("250x200+" + str(ran_a) + "+" + str(ran_b))
    tk.Label(root,text='我爱你',bg='pink',height=50,width=50,font=('宋体',20)).pack()
    root.mainloop()

with ThreadPoolExecutor(max_workers=xc) as tp:
     
    for i in range(xc):
        tp.submit(root)  
        #time.sleep(0.1)


# root()
