from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from datetime import datetime, time as dt_time, timedelta
import time
import requests
from email.utils import parsedate_to_datetime
from datetime import timezone

# --- 配置参数 ---
CHROME_DRIVER_PATH = "/Users/lizhu/Downloads/CCR/taobao/chromedriver/chromedriver"  # 例如: "C:/webdrivers/chromedriver.exe" 或 "/usr/local/bin/chromedriver"
TAOBAO_CART_URL = "https://cart.taobao.com/cart.htm"

# --- 时间同步函数 ---
def get_taobao_time_offset():
    """获取淘宝服务器时间与本地时间的差值"""
    try:
        # 尝试从淘宝获取服务器时间 (HTTP HEAD请求，更轻量)
        response = requests.head("http://www.taobao.com", timeout=3) # 设置超时
        response.raise_for_status() # 如果请求失败则引发HTTPError
        
        server_date_str = response.headers.get('Date')
        if not server_date_str:
            print("警告: 未能从淘宝服务器响应头中获取Date字段。将使用本地时间。")
            return None

        # 将HTTP Date格式的字符串转换为datetime对象 (aware datetime in UTC)
        server_time_utc = parsedate_to_datetime(server_date_str)
        
        # 获取本地当前的UTC时间 (aware datetime in UTC)
        local_time_utc = datetime.now(timezone.utc)
        
        # 计算时间差
        offset = server_time_utc - local_time_utc
        print(f"成功获取淘宝服务器时间。本地时间与服务器时间差: {offset.total_seconds():.3f} 秒")
        if abs(offset.total_seconds()) > 300: # 如果差值过大 (例如超过5分钟)，可能存在问题
            print(f"警告: 检测到本地时间与服务器时间差异较大 ({offset.total_seconds():.1f}秒)。请检查本地时间设置。")
        return offset
    except requests.exceptions.RequestException as e:
        print(f"警告: 获取淘宝服务器时间失败: {e}。将使用本地时间。")
        return None
    except Exception as e:
        print(f"警告: 处理淘宝服务器时间时发生未知错误: {e}。将使用本地时间。")
        return None

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

    # 获取与淘宝服务器的时间差
    print("正在尝试与淘宝服务器同步时间...")
    time_offset = get_taobao_time_offset()

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

            # 将用户输入的时间（本地时区）与今天的日期结合
            now_local = datetime.now()
            user_target_datetime_local = now_local.replace(hour=target_time_obj.hour,
                                                           minute=target_time_obj.minute,
                                                           second=target_time_obj.second,
                                                           microsecond=target_time_obj.microsecond,
                                                           tzinfo=None) # Naive datetime for local

            # 如果今天这个时间已经过去，则假定是明天 (简单处理，实际复杂场景可能需要更完善逻辑)
            if user_target_datetime_local < now_local:
                print("注意: 您输入的时间点在今天已经过去，将目标日期设置为明天。")
                user_target_datetime_local += timedelta(days=1)
            
            print(f"您设定的本地抢购时间: {user_target_datetime_local.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

            calibrated_target_datetime_local = user_target_datetime_local
            if time_offset is not None:
                # 应用时间差来校准本地触发时间
                # 如果本地时间比服务器快 (offset为负)，我们需要更早触发 (user_target - (负数) = user_target + 正数)
                # 如果本地时间比服务器慢 (offset为正)，我们需要更晚触发 (user_target - (正数) = user_target - 正数)
                # 实际上，我们希望的是：本地实际触发时间 + offset = 用户期望的服务器时间点
                # 所以，本地实际触发时间 = 用户期望的服务器时间点 - offset
                # 假设用户输入的是期望的服务器时间点对应到他本地显示的时间
                calibrated_target_datetime_local = user_target_datetime_local - time_offset
                print(f"校准后，将在本地时间 {calibrated_target_datetime_local.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} 触发操作")
            else:
                print("时间同步失败，将直接使用您输入的本地时间进行倒计时。")
            
            purchase_time_dt = calibrated_target_datetime_local # 更新倒计时用的时间点
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
    try:
        MAX_CHECKOUT_ATTEMPTS = 5  # 最多尝试5次
        checkout_successful = False
        checkout_attempts = 0

        while checkout_attempts < MAX_CHECKOUT_ATTEMPTS and not checkout_successful:
            checkout_attempts += 1
            print(f"\n第 {checkout_attempts}/{MAX_CHECKOUT_ATTEMPTS} 次尝试结算...")

            time.sleep(0.3)  # 页面稳定时间, 确保在点击前页面已准备好

            try:
                print("正在查找并点击'结算'按钮...")
                # 使用之前确定的XPath
                checkout_button_xpath = "//div[contains(@class, 'btn--QDjHtErD') and starts-with(normalize-space(.), '结算')]"
                checkout_button = wait.until(EC.element_to_be_clickable((By.XPATH, checkout_button_xpath)))
                checkout_button.click()
                print("'结算'按钮已点击。")

                print("等待页面跳转到订单确认页...")
                try:
                    # 等待URL包含"buy."，表明已进入订单确认流程
                    wait.until(EC.url_contains("buy."))
                    print(f"已成功跳转到订单确认页，当前URL: {driver.current_url}")
                    checkout_successful = True  # 标记结算成功，准备退出重试循环
                except TimeoutException:
                    # 当前尝试未成功跳转
                    print(f"第 {checkout_attempts} 次尝试：点击'结算'后页面未在预定时间内跳转到订单确认页 (URL未包含 'buy.').")
                    print(f"当前URL: {driver.current_url}")
                    if checkout_attempts < MAX_CHECKOUT_ATTEMPTS:
                        print("准备刷新页面并重试...")
                        driver.refresh()
                        # 可选: time.sleep(1) # 刷新后短暂等待，让页面有时间开始加载
                    else:
                        # 所有重试次数已用完
                        print("已达到最大重试次数，结算失败。")
                        print("请检查购物车是否正确结算（例如，商品是否已选），或是否有弹窗/验证阻挡了跳转。")
                        print("--- Page source at time of failure: ---")
                        try:
                            print(driver.page_source)
                        except Exception as ps_e:
                            print(f"无法获取页面源码: {ps_e}")
                        print("--- End of page source ---")
                        driver.quit()
                        return  # 退出主函数

            except Exception as e_click:  # 处理在查找或点击'结算'按钮过程中发生的其他异常
                print(f"第 {checkout_attempts} 次尝试：处理'结算'按钮时发生错误: {e_click}")
                if checkout_attempts < MAX_CHECKOUT_ATTEMPTS:
                    print("准备刷新页面并重试...")
                    driver.refresh()
                    # 可选: time.sleep(1)
                else:
                    print("已达到最大重试次数，因处理'结算'按钮时持续发生错误而导致结算失败。")
                    print("--- Page source at time of failure: ---")
                    try:
                        print(driver.page_source)
                    except Exception as ps_e:
                        print(f"无法获取页面源码: {ps_e}")
                    print("--- End of page source ---")
                    driver.quit()
                    return  # 退出主函数

        # 检查最终结算状态，如果所有尝试都失败了（理论上上面的return会先执行）
        if not checkout_successful:
            print("所有结算尝试均已失败。程序退出。")
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

    # 6. 尝试点击“提交订单”按钮，带重试机制
    MAX_SUBMIT_ATTEMPTS = 5  # 最多尝试5次
    submit_attempts = 0
    submit_successful = False
    # 之前确认可用的“提交订单”按钮XPath
    submit_order_button_xpath = "//div[@id='submitOrder']//div[contains(@class, 'btn--QDjHtErD') and normalize-space(.)='提交订单']"

    while submit_attempts < MAX_SUBMIT_ATTEMPTS and not submit_successful:
        submit_attempts += 1
        print(f"\n第 {submit_attempts}/{MAX_SUBMIT_ATTEMPTS} 次尝试提交订单...")
        
        try:
            print(f"等待 '提交订单' 按钮 (XPath: {submit_order_button_xpath})")
            # 使用全局的wait对象，其超时时间应已在之前设置 (例如10秒)
            submit_order_button = wait.until(EC.element_to_be_clickable((By.XPATH, submit_order_button_xpath)))
            
            print("'提交订单' 按钮已找到，尝试点击...")
            submit_order_button.click()
            print("'提交订单' 按钮已点击。")
            
            # TODO: 此处可以添加更明确的成功状态检查，例如等待URL变化或特定成功提示元素出现
            # 例如: wait.until(EC.url_contains("alipay.com"))
            # 或: wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'订单提交成功')]")))
            # 目前，我们假设点击本身未抛出异常即为初步成功
            print("初步认为点击操作成功。建议后续根据实际页面流程添加更精确的成功状态验证。")
            submit_successful = True # 标记提交成功，将退出重试循环

        except TimeoutException:
            print(f"第 {submit_attempts} 次尝试：'提交订单' 按钮未在规定时间内找到或变为可点击。")
            if submit_attempts < MAX_SUBMIT_ATTEMPTS:
                print("准备刷新页面并重试...")
                driver.refresh()
                time.sleep(1) # 刷新后等待1秒，给页面一点加载时间
            else:
                print("已达到最大重试次数，'提交订单' 操作因按钮未找到或不可点击而失败。")
                print("Dumping page source for analysis...")
                print("-------------------- HTML START --------------------")
                try:
                    print(driver.page_source)
                except Exception as ps_e:
                    print(f"无法获取页面源码: {ps_e}")
                print("-------------------- HTML END --------------------")

        except Exception as e:
            print(f"第 {submit_attempts} 次尝试：点击 '提交订单' 时发生未预料的错误: {e}")
            if submit_attempts < MAX_SUBMIT_ATTEMPTS:
                print("准备刷新页面并重试...")
                driver.refresh()
                time.sleep(1) # 刷新后等待1秒
            else:
                print("已达到最大重试次数，'提交订单' 操作因发生未知错误而失败。")
                print("Dumping page source for analysis...")
                print("-------------------- HTML START --------------------")
                try:
                    print(driver.page_source)
                except Exception as ps_e:
                    print(f"无法获取页面源码: {ps_e}")
                print("-------------------- HTML END --------------------")

    # 根据最终提交状态决定后续操作
    if not submit_successful:
        print("\n所有提交订单的尝试均已失败。脚本将在此处停止。")
        print("请检查最后一次尝试失败时的页面源码和错误信息。")
        input("按Enter键关闭浏览器并退出脚本...") # 给用户机会查看浏览器
        driver.quit()
        return # 退出主函数

    # 如果 submit_successful 为 True，则执行到这里
    # 7. 后续：提示用户检查并手动完成支付
    print("\n'提交订单' 操作初步完成（至少按钮被点击了）。")
    print("请立即检查浏览器中的订单状态，并手动完成任何后续支付步骤。")
    input("按Enter键关闭浏览器...")
    driver.quit()

if __name__ == "__main__":
    main()