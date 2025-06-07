from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from datetime import datetime, time as dt_time, timedelta
import time

# --- 配置参数 ---
CHROME_DRIVER_PATH = "/Users/lizhu/Downloads/CCR/taobao/chromedriver/chromedriver"  # 例如: "C:/webdrivers/chromedriver.exe" 或 "/usr/local/bin/chromedriver"
TAOBAO_CART_URL = "https://cart.taobao.com/cart.htm"
# --- 主逻辑 ---
def main():
    # 1. 初始化 WebDriver
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # 如果不想看到浏览器界面，可以启用无头模式，但初次调试建议不启用
    options.add_argument("--start-maximized")
    # 防止被检测为自动化工具的一些选项 (效果不一定)
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    # options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/YOUR_CHROME_VERSION Safari/537.36"') # 替换 YOUR_CHROME_VERSION

    service = Service(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10) # 设置一个默认的显式等待超时时间

    # 2. 手动登录、导航到购物车并选择商品
    driver.get("https://www.taobao.com") # 打开淘宝首页，方便登录
    input("请在浏览器中完成以下操作：\n" \
          "1. 手动登录您的淘宝账号。\n" \
          "2. 手动导航到您的购物车页面 (https://cart.taobao.com/cart.htm)。\n" \
          "3. 手动勾选您要抢购的商品，确保它们已正确选中。\n" \
          "全部完成后，回到此终端窗口，按Enter键继续抢购...")

    # --- 设置抢购时间 (精确到毫秒) ---
    while True:
        purchase_time_str = input("请输入今天的抢购时间 (HH:MM:SS.fff 格式，例如 22:15:00.500): ")
        try:
            # 解析时间字符串为 time 对象，包含毫秒
            target_time_obj = datetime.strptime(purchase_time_str, "%H:%M:%S.%f").time()
            break
        except ValueError:
            print("时间格式错误，请确保格式为 HH:MM:SS.fff (例如 22:15:00.500)。请重试。")

    # 获取今天的日期，并与目标时间合并成 datetime 对象
    now_for_combine = datetime.now() # Use a consistent 'now' for combining and checking 'tomorrow'
    target_datetime = datetime.combine(now_for_combine.date(), target_time_obj)

    # 如果设定的时间早于当前时间，则假定是第二天的这个时间
    if target_datetime < now_for_combine:
        print(f"设定的时间 {target_datetime.strftime('%H:%M:%S.%f')[:-3]} 已过当前时间 ({now_for_combine.strftime('%H:%M:%S.%f')[:-3]})，将自动设置为明天同一时间。")
        target_datetime = datetime.combine(now_for_combine.date() + timedelta(days=1), target_time_obj)

    print(f"抢购时间已设定为: {target_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
    print("正在等待抢购时间...")

    # 高精度倒计时循环
    display_update_interval = 0.1  # Update countdown display every 0.1 seconds
    last_display_update_time = time.monotonic()

    while datetime.now() < target_datetime:
        current_time_monotonic = time.monotonic()
        # Update display periodically for user visibility
        if current_time_monotonic - last_display_update_time >= display_update_interval:
            # Fetch fresh datetime.now() for display calculation
            current_datetime_for_display = datetime.now()
            if current_datetime_for_display < target_datetime:
                remaining_time = target_datetime - current_datetime_for_display
                # Format remaining_time to show H:MM:SS.milliseconds (3 digits)
                total_seconds = remaining_time.total_seconds()
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = int(total_seconds % 60)
                milliseconds = remaining_time.microseconds // 1000 # Convert microseconds to milliseconds
                print(f"倒计时: {hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}          ", end='\r', flush=True)
            last_display_update_time = current_time_monotonic
        
        # Sleep for a very short duration. This makes the loop check the time condition frequently.
        # The loop will exit as soon as datetime.now() >= target_datetime.
        time.sleep(0.001) # Sleep for 1 millisecond

    print("\n抢购时间到！开始执行结算...                                ") # 清除倒计时行并提示
    # --- 抢购时间等待结束 ---
    # 脚本现在假定浏览器已在正确的、选好商品的购物车页面

    # 5. 点击“结算”按钮

    #    你需要找到“结算”按钮的定位器 (ID, XPath, CSS Selector等)
    #    这里用一个占位符，实际需要用浏览器开发者工具查找
    time.sleep(0.3) # Adjusted pause for page to settle before clicking checkout
    try:
        print("正在查找并点击'结算'按钮...")
        # 示例: checkout_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='J_Go']//a[@id='J_GoToPay']")))
        # 或者更通用的可能是按文字内容查找，但要注意文字可能变化
        checkout_button_xpath = "//div[contains(@class, 'btn--QDjHtErD') and starts-with(normalize-space(.), '结算')]" # Corrected XPath for Checkout
        checkout_button = wait.until(EC.element_to_be_clickable((By.XPATH, checkout_button_xpath)))
        checkout_button.click()
        print("'结算'按钮已点击。")

        print("等待页面跳转到订单确认页...")
        try:
            # Wait for the URL to contain 'buy.' which is common for Taobao/Tmall order pages
            # Or, more specifically, wait for it NOT to be the cart URL anymore if 'buy.' is too generic
            # Let's try url_contains first as it's simpler.
            wait.until(EC.url_contains("buy."))
            print(f"已跳转到订单确认页，当前URL: {driver.current_url}")
        except TimeoutException:
            print("错误: 点击'结算'后页面未在10秒内跳转到订单确认页 (URL未包含 'buy.').")
            print(f"当前URL: {driver.current_url}")
            print("请检查购物车是否正确结算（例如，商品是否已选），或是否有弹窗/验证阻挡了跳转。")
            print("--- Page source at time of failure: ---")
            try:
                print(driver.page_source)
            except Exception as ps_e:
                print(f"无法获取页面源码: {ps_e}")
            print("--- End of page source ---")
            driver.quit()
            return

    except Exception as e:
        print(f"点击'结算'按钮时发生未预料的错误: {e}")
        print("Dumping page source for analysis...")
        print("-------------------- HTML START --------------------")
        try:
            print(driver.page_source)
        except Exception as ps_e:
            print(f"无法获取页面源码: {ps_e}")
        print("-------------------- HTML END --------------------")
        print("请将以上HTML内容复制并提供给我。脚本将在此处停止。")
        driver.quit()
        return

    # 6. 等待订单确认页面加载并点击“提交订单”
    #    同样需要找到“提交订单”按钮的定位器
    try:
        print("Attempting to find and click '提交订单' button...")
        # Current XPath for '提交订单' button
        submit_order_button_xpath = "//div[@id='submitOrder']//div[contains(@class, 'btn--QDjHtErD') and normalize-space(.)='提交订单']" # Reverted to correct XPath for Submit Order
        
        print(f"Waiting for '提交订单' button with XPath: {submit_order_button_xpath}")
        submit_order_button = wait.until(EC.element_to_be_clickable((By.XPATH, submit_order_button_xpath)))
        
        print("'提交订单' button found, attempting to click...")
        submit_order_button.click()
        print("'提交订单'按钮已点击！抢购流程初步完成。")
        
    except TimeoutException:
        print(f"Error: '提交订单'按钮 (XPath: {submit_order_button_xpath}) 未在规定时间内找到或变为可点击状态。")
        print("Dumping page source for analysis...")
        print("-------------------- HTML START --------------------")
        print(driver.page_source)
        print("-------------------- HTML END --------------------")
        print("请将以上HTML内容复制并提供给我。脚本将在此处停止。")
        # driver.quit() # Consider if quit is needed here or if user wants to inspect
        return # Stop script
        
    except Exception as e:
        print(f"An unexpected error occurred while trying to find/click '提交订单': {e}")
        print("Dumping page source for analysis...")
        print("-------------------- HTML START --------------------")
        print(driver.page_source)
        print("-------------------- HTML END --------------------")
        print("请将以上HTML内容复制并提供给我。脚本将在此处停止。")
        # driver.quit() # Consider if quit is needed here
        return # Stop script

    # 7. 后续：可以添加一些成功后的提示或保持浏览器打开
    print("请检查浏览器是否成功提交订单，并手动完成支付。")
    input("按Enter键关闭浏览器...")
    driver.quit()

if __name__ == "__main__":
    main()