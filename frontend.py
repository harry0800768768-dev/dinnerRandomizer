import customtkinter as ctk
import random
import os
import datetime
import asyncio
from randomizer import get_opened, nearby_search


class DinnerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 視窗基本設定
        self.title("晚餐雷達 3000")
        self.geometry("400x450")
        self.resizable(False, False) # 固定視窗大小
        
        # 設定外觀主題 (Dark, Light, 或 System)
        ctk.set_appearance_mode("System") 
        ctk.set_default_color_theme("blue")

        # 特效相關的內部變數
        self.opened_cache = []      # 快取目前有開的清單
        self.spin_counter = 0      # 特效執行的次數計數器
        self.total_spins = 15      # 特效總共要轉幾次 (例如轉 15 次文字)
        self.is_spinning = False   # 鎖定狀態，防止重複點擊

        # 標題文字
        self.title_label = ctk.CTkLabel(self, text="🍔 今晚吃什麼？", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(30, 10))

        # 提示文字
        self.subtitle_label = ctk.CTkLabel(self, text="點擊下方按鈕，把命運交給雷達！", text_color="gray")
        self.subtitle_label.pack(pady=(0, 20))

        # 顯示抽籤結果的超大區塊
        self.result_label = ctk.CTkLabel(
            self, 
            text="等待抽籤...", 
            font=ctk.CTkFont(size=30, weight="bold"),
            fg_color=("gray85", "gray25"), # 淺色/深色模式的背景色
            corner_radius=10,
            width=300,
            height=100
        )
        self.result_label.pack(pady=20)

        # 抽籤按鈕
        self.draw_button = ctk.CTkButton(
            self, 
            text="🎲 隨機挑選晚餐", 
            font=ctk.CTkFont(size=18),
            height=50,
            command=self.start_spin_effect # 點擊時執行的函數
        )
        self.draw_button.pack(pady=20)
        
        # 狀態列 (顯示找到幾家店)
        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12), text_color="gray")
        self.status_label.pack(side="bottom", pady=10)
    

    def start_spin_effect(self):
        # 0. 防止重複點擊
        if self.is_spinning:
            return
            
        # 1. 初始化狀態
        self.is_spinning = True
        self.draw_button.configure(state="disabled") # 按鈕反灰
        self.result_label.configure(text_color=("gray20", "gray80")) # 特效期間文字用中性色
        self.spin_counter = 0 
        
        # 2. 準備資料
        self.opened_cache = get_opened()
        
        # 錯誤處理 (無資料)
        if not self.opened_cache:
            self.result_label.configure(text="😭 附近沒半家開的", text_color="red")
            self.status_label.configure(text="請確認 csv 資料或放寬搜尋條件")
            self.draw_button.configure(state="normal")
            self.is_spinning = False
            return
            
        # 3. 呼叫第一下特效迴圈
        self.animate_spin()

    def animate_spin(self):
        """核心迴圈：利用 .after() 飛速更換 label 文字"""
        if self.spin_counter < self.total_spins:
            # 從列表隨機挑一個名字顯示 (模擬滾動)
            temp_winner = random.choice(self.opened_cache)
            self.result_label.configure(text=temp_winner)
            
            self.spin_counter += 1
            
            # --- 速度控制 (可以越轉越慢，增加緊張感) ---
            # 初始速度飛快 (50ms)，最後幾下放慢 (200ms)
            if self.spin_counter > self.total_spins - 3:
                speed = 200 # 最後三下放慢
            else:
                speed = 50  # 飛速滾動 (50 毫秒換一次文字)
            # 關鍵：在 speed 毫秒後，再次呼叫自己 (animate_spin)
            self.after(speed, self.animate_spin)
        else:
            # 特效結束，顯示最終結果
            self.show_final_result()

    def show_final_result(self):
        """最後定格，高亮結果"""
        # 最終定格 (重新真正抽一次，以免剛好特效停在同一家)
        final_winner = random.choice(self.opened_cache)
        
        # 醒目顯示最終結果 (黑色/白色)
        self.result_label.configure(text=final_winner, text_color=("black", "#FFD700")) # 深色模式用金色
        
        # 恢復按鈕和狀態
        self.draw_button.configure(state="normal")
        self.status_label.configure(text=f"✅ 目前附近有 {len(self.opened_cache)} 家餐廳營業中")
        self.is_spinning = False
        
        # 💡 清空快取以節省記憶體
        self.opened_cache = []

# --- 3. 啟動應用程式 ---
if __name__ == "__main__":
    m_timestamp = os.path.getmtime("result.csv")
    today_timestamp = datetime.datetime.today().timestamp()
    if today_timestamp >= m_timestamp + 604800:
        asyncio.run(nearby_search())
    app = DinnerApp()
    app.mainloop()