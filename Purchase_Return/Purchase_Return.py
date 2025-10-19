from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# إعداد ChromeOptions مع بروفايل مخصص
options = Options()
options.add_argument(r"user-data-dir=D:\selenium\chrome_profile")  # مسار البروفايل
options.add_argument("--profile-directory=Default")  # أو Profile 1 حسب جهازك
options.add_argument("--start-maximized")

# استخدام webdriver-manager لتثبيت ChromeDriver المناسب تلقائيًا
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 5)

# فتح المتصفح الأول
driver.maximize_window()
print("✅ فتح المتصفح")
time.sleep(1)

# فتح صفحة تسجيل الدخول (لو فيه سيشن محفوظة مش هيطلب Login)
driver.get("https://app.skeyerp.com/auth/Dev/login")
print("✅ فتح صفحة تسجيل الدخول")

# لو محتاج أول مرة تسجل الدخول بالكود بتاعك
try:
    # تسجيل الدخول
    wait.until(EC.visibility_of_element_located((By.ID, "usrCode"))).send_keys("admin")
    driver.find_element(By.ID, "usrPswrd").send_keys("123456")

    login_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//*[@id='index']/div[1]/div/div[1]/div/div/div/div[2]/form/div[4]/button")
    ))
    login_btn.click()

    # انتظار ظهور Dashboard
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="theme_Basic_theme"]')))
    print("✅ دخلت Dashboard")
except Exception:
    print("ℹ️ غالبًا السيشن محفوظة بالفعل ومش محتاج Login")

time.sleep(1)

# الذهاب لقائمة المشتريات
pur_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "(//*[@id='sidebar-menu']/li[7]/a/span)[1]")))
pur_menu.click()
print("✅ فتحت قائمة المشتريات")
time.sleep(2)

# فتح شاشة مرتجعات المشتريات
sub_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='sidebar-menu']/li[7]/ul/li[2]/a/span")))
sub_menu.click()
print("✅ فتح شاشة مرتجعات المشتريات")
time.sleep(3)

# الضغط على زر جديد
new_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='e-toolbar-item e-template' and @title='إضافة']")))
new_btn.click()
print("✅ ضغطت جديد")
time.sleep(3)  # خليته أبطأ شوية

# اختيار من الفاواتير عن طريق f9
return_type_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="rtrnTypeLst"]/i')))
return_type_dropdown.click()
print("✅ فتحت قائمة نوع المرتجع")
time.sleep(2)

# اختيار اول فاتورة في القائمة
first_invoice = wait.until(EC.element_to_be_clickable((By.XPATH, "(//tr[contains(@class,'p-selectable-row')])[3]")))
first_invoice.click()
print("✅ ضغطت على ثاني فاتورة في القائمة")
time.sleep(2)

#تنزيل كل الاصناف التي في الافاتورة 
download_all_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="purchase-return"]/form/div/div/div[4]/div/div/div/div/div/div/div[2]/div/button[2]/span')))
download_all_btn.click()
print("✅ ضغطت تنزيل كل الاصناف")
time.sleep(2)

# فتح تابة طرق الدفع
payment_tab = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//button[normalize-space(text())='طريقة الدفع']")))
payment_tab.click()
print("✅ فتحت تاب طريقة الدفع")
time.sleep(1)

#الضغط علي حفظ المرتجع
save_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title='حفظ']")))
save_btn.click()
print("✅ ضغطت حفظ المرتجع")
time.sleep(3)
