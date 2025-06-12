import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
from datetime import datetime, timezone

# --- 核心依赖，与原脚本保持一致 ---
try:
    import requests
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException
    from email.utils import parsedate_to_datetime
except ImportError as e:
    messagebox.showerror("依赖缺失", f"必需的库未安装: {e}\n请运行 'pip install selenium requests' 来安装。")
    exit()

# --- 全局配置 ---
CHROME_DRIVER_PATH = "/Users/lizhu/Downloads/CCR/taobao/chromedriver/chromedriver"

class TaobaoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("淘宝抢购助手 v2.0")
        self.root.geometry("600x500")

        self.log_queue = queue.Queue()
        self.driver = None
        self.wait = None

        # --- UI 元素 ---
        # 1. 准备阶段
        self.prepare_frame = ttk.LabelFrame(root, text="第一步: 准备浏览器")
        self.prepare_frame.pack(fill="x", padx=10, pady=5)
        self.prepare_button = ttk.Button(self.prepare_frame, text="打开浏览器并手动准备", command=self.start_browser_thread)
        self.prepare_button.pack(pady=10)

        # 2. 抢购阶段
        self.purchase_frame = ttk.LabelFrame(root, text="第二步: 设置时间并抢购")
        self.purchase_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(self.purchase_frame, text="抢购时间 (HH:MM:SS.fff):", font=("Helvetica", 12)).pack(pady=(10, 2))
        self.time_entry = ttk.Entry(self.purchase_frame, width=30, font=("Helvetica", 12))
        self.time_entry.pack()
        self.time_entry.insert(0, datetime.now().strftime("%H:%M:%S.000"))
        
        self.start_button = ttk.Button(self.purchase_frame, text="开始倒计时抢购", command=self.start_purchase_thread)
        self.start_button.pack(pady=10)

        # 3. 日志输出
        self.log_frame = ttk.LabelFrame(root, text="运行日志")
        self.log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.log_area = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD, font=("Courier New", 14))
        self.log_area.pack(pady=5, padx=5, expand=True, fill='both')
        self.log_area.configure(state='disabled')

        # 倒计时显示
        self.countdown_var = tk.StringVar()
        self.countdown_var.set("")
        self.countdown_label = ttk.Label(self.purchase_frame, textvariable=self.countdown_var, font=("Helvetica", 18, "bold"), foreground="red")
        self.countdown_label.pack(pady=(5, 0))

        # 初始化UI状态
        self.time_entry.config(state=tk.DISABLED)
        self.start_button.config(state=tk.DISABLED)

        self.process_queue()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if messagebox.askokcancel("退出", "确定要退出吗？如果浏览器是本程序打开的，它将会关闭。"):
            if self.driver:
                try:
                    self.driver.quit()
                except Exception as e:
                    self.log(f"关闭浏览器时出错: {e}")
            self.root.destroy()

    def log(self, message):
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.log_queue.put(f"[{now}] {message}")

    def process_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_area.configure(state='normal')
                self.log_area.insert(tk.END, msg + '\n')
                self.log_area.see(tk.END)
                self.log_area.configure(state='disabled')
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)

    def start_browser_thread(self):
        self.prepare_button.config(state=tk.DISABLED)
        self.log("正在启动浏览器准备流程...")
        thread = threading.Thread(target=self.browser_setup_logic)
        thread.daemon = True
        thread.start()

    def browser_setup_logic(self):
        try:
            self.log("正在初始化Chrome浏览器...")
            service = Service(executable_path=CHROME_DRIVER_PATH)
            options = webdriver.ChromeOptions()
            options.add_argument("start-maximized")
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 10)
            
            self.driver.get("https://www.taobao.com")
            self.log("浏览器已打开。")
            self.log("请在浏览器中完成以下操作：")
            self.log("1. 手动登录您的淘宝账号。")
            self.log("2. 手动导航到您的购物车页面。")
            self.log("3. 手动勾选您要抢购的商品。")
            self.log("完成后，回到本窗口，在第二步中设置时间并开始抢购。")

            # 更新UI，激活第二步
            self.time_entry.config(state=tk.NORMAL)
            self.start_button.config(state=tk.NORMAL)

        except Exception as e:
            self.log(f"浏览器初始化失败: {e}")
            messagebox.showerror("浏览器错误", f"无法启动Chrome浏览器，请检查ChromeDriver路径和版本。\n错误: {e}")
            self.prepare_button.config(state=tk.NORMAL) # 允许重试

    def start_purchase_thread(self):
        if not self.driver or not self.wait:
            messagebox.showerror("错误", "浏览器尚未初始化，请先点击第一步中的按钮。")
            return
            
        purchase_time_str = self.time_entry.get()
        try:
            datetime.strptime(purchase_time_str, "%H:%M:%S.%f")
        except ValueError:
            messagebox.showerror("时间格式错误", "请输入正确的时间格式 HH:MM:SS.fff")
            return

        self.start_button.config(state=tk.DISABLED)
        self.log("抢购任务已启动...")
        thread = threading.Thread(target=self.purchase_logic, args=(purchase_time_str,))
        thread.daemon = True
        thread.start()
        
    def purchase_logic(self, purchase_time_str):
        try:
            time_offset = self.get_taobao_time_offset()

            self.log("准备就绪，开始倒计时...")
            today_str = datetime.now().strftime('%Y-%m-%d')
            target_time_naive = datetime.strptime(f"{today_str} {purchase_time_str}", '%Y-%m-%d %H:%M:%S.%f')
            local_trigger_time = target_time_naive - time_offset if time_offset else target_time_naive
            self.log(f"目标抢购时间 (服务器时间): {target_time_naive.strftime('%H:%M:%S.%f')}")
            self.log(f"本地触发时间 (已校准): {local_trigger_time.strftime('%H:%M:%S.%f')}")

            # 倒计时实时刷新
            while True:
                now = datetime.now()
                remaining = (local_trigger_time - now).total_seconds()
                if remaining <= 0:
                    self.countdown_var.set("00:00:00.000")
                    self.log("时间到！开始执行抢购！")
                    break
                else:
                    ms = int((remaining - int(remaining)) * 1000)
                    h = int(remaining // 3600)
                    m = int((remaining % 3600) // 60)
                    s = int(remaining % 60)
                    self.countdown_var.set(f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}")
                time.sleep(0.01)

            self.click_checkout(self.wait)
            self.click_submit_order(self.wait)

            self.log("抢购流程执行完毕。请检查浏览器确认最终状态。")
            messagebox.showinfo("流程结束", "抢购流程已执行完毕，请检查浏览器并手动完成后续操作。")

        except Exception as e:
            self.log(f"发生严重错误: {e}")
            messagebox.showerror("严重错误", f"程序发生未处理的异常: {e}")
        finally:
            self.start_button.config(state=tk.NORMAL)
            self.log("--------------------✨ 当前流程结束 ✨--------------------")

    def get_taobao_time_offset(self):
        self.log("正在同步淘宝服务器时间...")
        try:
            response = requests.head("http://www.taobao.com", timeout=3)
            response.raise_for_status()
            server_date_str = response.headers.get('Date')
            if not server_date_str:
                self.log("警告: 未能获取淘宝服务器时间，将使用本地时间。")
                return None
            server_time_utc = parsedate_to_datetime(server_date_str)
            local_time_utc = datetime.now(timezone.utc)
            offset = server_time_utc - local_time_utc
            self.log(f"时间同步成功。本地时间与服务器时间差: {offset.total_seconds():.3f} 秒")
            return offset
        except Exception as e:
            self.log(f"警告: 时间同步失败: {e}。将使用本地时间。")
            return None

    def click_checkout(self, wait):
        MAX_ATTEMPTS = 5
        attempts = 0
        successful = False
        while attempts < MAX_ATTEMPTS and not successful:
            attempts += 1
            self.log(f"第 {attempts}/{MAX_ATTEMPTS} 次尝试点击 '结算'...")
            try:
                                                # 使用 taobao_qg.py 旧版的结算按钮 XPath
                xpath = "//div[contains(@class, 'btn--QDjHtErD') and starts-with(normalize-space(.), '结算')]"
                button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                # 增强点击逻辑
                self.driver.execute_script("arguments[0].scrollIntoView();", button)
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).move_to_element(button).perform()
                try:
                    button.click()
                    self.log("'结算' 按钮已点击，等待跳转...")
                except Exception as click_e:
                    self.log(f"常规点击失败，尝试JS点击: {click_e}")
                    self.driver.execute_script("arguments[0].click();", button)
                    self.log("'结算' 按钮已通过JS点击。等待跳转...")
                wait.until(EC.url_contains("buy."))
                self.log("成功跳转到订单确认页。")
                successful = True
            except Exception as e:
                self.log(f"第 {attempts} 次尝试失败，错误: {str(e).splitlines()[0]}")
                if attempts < MAX_ATTEMPTS:
                    self.log("刷新页面后重试...")
                    self.driver.refresh()
                    time.sleep(1)
        if not successful:
            self.log("所有结算尝试均失败！保存页面源码到 checkout_page_source.html")
            try:
                with open("checkout_page_source.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                self.log("页面源码已保存。请在项目文件夹下查找该文件。")
            except Exception as dump_e:
                self.log(f"保存页面源码失败: {dump_e}")
            raise Exception("所有结算尝试均失败！")

    def click_submit_order(self, wait):
        MAX_ATTEMPTS = 5
        attempts = 0
        successful = False
                # 使用 taobao_qg.py 旧版的提交订单按钮 XPath
        xpath = "//div[@id='submitOrder']//div[contains(@class, 'btn--QDjHtErD') and normalize-space(.)='提交订单']"
        while attempts < MAX_ATTEMPTS and not successful:
            attempts += 1
            self.log(f"第 {attempts}/{MAX_ATTEMPTS} 次尝试点击 '提交订单'...")
            try:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                # 增强点击逻辑
                self.driver.execute_script("arguments[0].scrollIntoView();", button)
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).move_to_element(button).perform()
                try:
                    button.click()
                    self.log("'提交订单' 按钮已点击。")
                except Exception as click_e:
                    self.log(f"常规点击失败，尝试JS点击: {click_e}")
                    self.driver.execute_script("arguments[0].click();", button)
                    self.log("'提交订单' 按钮已通过JS点击。")
                successful = True
            except Exception as e:
                self.log(f"第 {attempts} 次尝试失败，错误: {str(e).splitlines()[0]}")
                if attempts < MAX_ATTEMPTS:
                    self.log("刷新页面后重试...")
                    self.driver.refresh()
                    time.sleep(1)
        if not successful:
            self.log("所有提交订单尝试均失败！保存页面源码到 submit_page_source.html")
            try:
                with open("submit_page_source.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                self.log("页面源码已保存。请在项目文件夹下查找该文件。")
            except Exception as dump_e:
                self.log(f"保存页面源码失败: {dump_e}")
            raise Exception("所有提交订单尝试均失败！")

if __name__ == "__main__":
    root = tk.Tk()
    app = TaobaoApp(root)
    root.mainloop()
