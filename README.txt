Taobao Flash Sale Checkout Script (taobao_qg.py)
淘宝抢购脚本 (taobao_qg.py)

## Purpose
This Python script is designed to automate the checkout process on Taobao for flash sales or time-sensitive purchases. It aims to click the "结算" (Checkout) button at a precise, user-specified time and then proceed to the order submission page.

## 目的
此 Python 脚本旨在为淘宝上的抢购或时间敏感的购买自动执行结账流程。它的目标是在用户精确指定的时间点击“结算”按钮，然后进入订单提交页面。

## Algorithm / How it Works
1.  **Initialization**: The script uses the Selenium WebDriver to control a Chrome browser instance.
2.  **Manual Setup by User**:
    *   Upon running, the script launches a new Chrome browser window.
    *   The user must manually log in to their Taobao account within this script-launched browser window.
    *   The user then navigates to their shopping cart.
    *   The user manually selects all the item(s) they intend to purchase.
3.  **User Confirmation**: After completing the manual setup in the browser, the user returns to the terminal and presses the "Enter" key to signal the script to proceed.
4.  **Target Time Input**: The script prompts the user to enter the desired purchase time in `YYYY-MM-DD HH:MM:SS` format.
5.  **Countdown**: The script continuously checks the current system time against the target purchase time and displays a live countdown in the terminal.
6.  **Checkout Action (at Target Time)**:
    *   Precisely at the target time, the script first introduces a short, optimized pause (currently 0.3 seconds) to ensure page stability.
    *   It then attempts to locate and click the "结算" (Checkout) button using a predefined XPath.
7.  **Order Confirmation Page**:
    *   After clicking "结算", the script waits for the page to navigate to the order confirmation page. It currently does this by checking if the URL contains "buy.".
    *   It then attempts to find and click the "提交订单" (Submit Order) button. **Note**: The XPath for the "提交订单" button in the current version of the script is a placeholder and likely needs to be updated with the correct one from the Taobao website for this step to function reliably.
8.  **Error Handling**: The script includes basic error handling, such as for timeouts when elements are not found or pages do not load as expected. If an error occurs during critical steps like clicking "结算" or "提交订单", it may print the page source to the terminal for debugging and then exit.

## 算法 / 工作原理
1.  **初始化**: 脚本使用 Selenium WebDriver 控制一个 Chrome 浏览器实例。
2.  **用户手动设置**:
    *   运行后，脚本会启动一个新的 Chrome 浏览器窗口。
    *   用户必须在此脚本启动的浏览器窗口内手动登录其淘宝账户。
    *   然后用户导航到其购物车。
    *   用户手动选择所有他们打算购买的商品。
3.  **用户确认**: 在浏览器中完成手动设置后，用户返回终端并按“Enter”键以示脚本继续。
4.  **目标时间输入**: 脚本提示用户以 `YYYY-MM-DD HH:MM:SS` 格式输入期望的抢购时间。
5.  **倒计时**: 脚本持续检查当前系统时间与目标抢购时间，并在终端中显示实时倒计时。
6.  **结账操作 (在目标时间)**:
    *   在目标时间精确到达时，脚本首先引入一个短暂的优化暂停（当前为0.3秒）以确保页面稳定。
    *   然后它尝试使用预定义的 XPath 定位并点击“结算”按钮。
7.  **订单确认页面**:
    *   点击“结算”后，脚本等待页面导航到订单确认页面。当前它通过检查 URL 是否包含 "buy." 来实现此目的。
    *   然后它尝试查找并点击“提交订单”按钮。**注意**: 当前版本脚本中“提交订单”按钮的 XPath 是一个占位符，可能需要根据淘宝网站的实际情况更新正确的 XPath，此步骤才能可靠运行。
8.  **错误处理**: 脚本包含基本的错误处理，例如当未找到元素或页面未按预期加载时的超时。如果在点击“结算”或“提交订单”等关键步骤中发生错误，它可能会将页面源代码打印到终端以供调试，然后退出。

## Prerequisites
1.  **Python 3**: Ensure Python 3 is installed on your system.
2.  **Selenium Library**: Install the Selenium library for Python:
    ```bash
    pip install selenium
    ```
3.  **ChromeDriver**:
    *   Download the ChromeDriver executable that matches your Chrome browser version.
    *   Ensure ChromeDriver is placed in a directory listed in your system's PATH environment variable, or modify the script to point to its explicit location.

## 先决条件
1.  **Python 3**: 确保您的系统上安装了 Python 3。
2.  **Selenium 库**: 安装 Python 的 Selenium 库:
    ```bash
    pip install selenium
    ```
3.  **ChromeDriver**:
    *   下载与您的 Chrome 浏览器版本匹配的 ChromeDriver 可执行文件。
    *   确保 ChromeDriver 放置在系统 PATH 环境变量中列出的目录中，或者修改脚本以指向其显式位置。

## Usage Instructions
1.  **Save the Script**: Place the `taobao_qg.py` file in a directory on your computer.
2.  **Open Terminal**: Open a terminal or command prompt.
3.  **Navigate to Directory**: Change to the directory where you saved `taobao_qg.py`.
    ```bash
    cd path/to/script_directory
    ```
4.  **Run the Script**:
    ```bash
    python taobao_qg.py
    ```
5.  **Manual Browser Setup**:
    *   A Chrome browser window will open, controlled by the script.
    *   In THIS window:
        *   Manually **log in** to your Taobao account.
        *   Navigate to your **shopping cart**.
        *   Manually **select the item(s)** you wish to purchase. Ensure all desired items are checked.
6.  **Confirm Setup in Terminal**:
    *   Once you have completed the login and item selection in the browser, switch back to the terminal.
    *   Press the **Enter** key.
7.  **Enter Purchase Time**:
    *   The script will prompt you: `请输入抢购时间 (YYYY-MM-DD HH:MM:SS):`
    *   Enter the exact date and time you want the script to click "结算", then press Enter.
8.  **Monitor Countdown**: The script will display a countdown to the target time.
9.  **Automatic Checkout**: At the specified time, the script will attempt to perform the checkout and submit the order.

## 使用说明
1.  **保存脚本**: 将 `taobao_qg.py` 文件放置在您计算机上的一个目录中。
2.  **打开终端**: 打开终端或命令提示符。
3.  **导航到目录**: 切换到您保存 `taobao_qg.py` 的目录。
    ```bash
    cd path/to/script_directory
    ```
4.  **运行脚本**:
    ```bash
    python taobao_qg.py
    ```
5.  **手动浏览器设置**:
    *   一个由脚本控制的 Chrome 浏览器窗口将会打开。
    *   在此窗口中:
        *   手动**登录**您的淘宝账户。
        *   导航到您的**购物车**。
        *   手动**选择您希望购买的商品**。确保所有期望的商品都已勾选。
6.  **在终端中确认设置**:
    *   在浏览器中完成登录和商品选择后，切换回终端。
    *   按 **Enter** 键。
7.  **输入抢购时间**:
    *   脚本将提示您: `请输入抢购时间 (YYYY-MM-DD HH:MM:SS):`
    *   输入您希望脚本点击“结算”的确切日期和时间，然后按 Enter。
8.  **监控倒计时**: 脚本将显示到目标时间的倒计时。
9.  **自动结账**: 在指定时间，脚本将尝试执行结账并提交订单。

## Important Notes
*   **Website Changes**: Taobao frequently updates its website structure. If the script fails to find buttons (especially "结算" or "提交订单"), their XPaths in `taobao_qg.py` likely need to be updated. You can find XPaths using browser developer tools (right-click on the element -> Inspect).
*   **"提交订单" Button**: As mentioned, the XPath for the "提交订单" button is currently a placeholder. For the final step of order submission to work, you will need to inspect this button on the order confirmation page and update the `submit_order_button_xpath` variable in the script.
*   **Internet Connection**: A stable and fast internet connection is crucial for the script's success, especially for time-sensitive purchases.
*   **Timing Accuracy**: While the script aims for precision, system load and network latency can introduce minor variations in timing. The 0.3-second pause before clicking "结算" is for stability and was determined through testing; adjust if necessary.
*   **Ethical Use**: Use this script responsibly and in accordance with Taobao's terms of service.

## 重要提示
*   **网站变更**: 淘宝会频繁更新其网站结构。如果脚本未能找到按钮（特别是“结算”或“提交订单”），则 `taobao_qg.py` 中的 XPath 可能需要更新。您可以使用浏览器开发者工具（在元素上右键点击 -> 检查）找到 XPath。
*   **“提交订单”按钮**: 如前所述，“提交订单”按钮的 XPath 当前是一个占位符。为了使订单提交的最后一步能够工作，您需要在订单确认页面上检查此按钮，并更新脚本中的 `submit_order_button_xpath` 变量。
*   **网络连接**: 稳定且快速的网络连接对于脚本的成功至关重要，特别是对于时间敏感的购买。
*   **计时准确性**: 虽然脚本力求精确，但系统负载和网络延迟可能会引入微小的时间差异。点击“结算”前的0.3秒暂停是为了稳定性，并通过测试确定；如有必要请进行调整。
*   **道德使用**: 请负责任地使用此脚本，并遵守淘宝的服务条款。
