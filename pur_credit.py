from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# إعداد ChromeDriver مع بروفايل مخصص عشان يحتفظ بالسيشن
service = Service("D:/chromedriver-win64/chromedriver.exe")
options = Options()
options.add_argument(r"user-data-dir=D:\selenium\chrome_profile")  # مسار البروفايل
options.add_argument("--profile-directory=Default")  # أو Profile 1 حسب جهازك

driver = webdriver.Chrome(service=service, options=options)

wait = WebDriverWait(driver, 1)

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

# ✅ انتظر Dashboard يفتح
wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="theme_Basic_theme"]')))
print("✅ دخلت Dashboard")
time.sleep(2)

# الذهاب لقائمة المشتريات
pur_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//ul[@id='sidebar-menu']/li[7]/a/span")))
pur_menu.click()
print("✅ فتحت قائمة المشتريات")
time.sleep(2)

# فتح شاشة إنشاء فاتورة جديدة
sub_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//ul[@id='sidebar-menu']/li[7]/ul/li/a/span")))
sub_menu.click()
print("✅ فتح شاشة الفواتير")
time.sleep(2)

# الضغط على زر جديد
# الضغط على زر جديد (إضافة)
new_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='e-toolbar-item e-template' and @title='إضافة']")))
new_btn.click()
print("✅ ضغطت جديد")
time.sleep(1)  # خليته أبطأ شوية

# 1- اضغط على السهم لفتح القائمة
store_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[contains(@class,'e-input-group-icon')])[4]")))
store_dropdown.click()

# 2- انتظر الـ <ul> الخاصة بالقائمة تنزل (بتبقى غالباً class='e-dropdownbase' أو حاجة زي كده)
dropdown_list = wait.until(EC.presence_of_element_located((By.XPATH, "//ul[contains(@id,'listbox')]")))

# 3- لما تنزل، دور على الخيار بالمخزن
store_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[contains(., '201 - المخزن الرئيسي')]")))

# 4- اضغط عليه
store_option.click()

# 1- افتح سهم المورد
supplier_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[contains(@class,'e-ddl-icon') and contains(@class,'e-search-icon')])[4]")))
supplier_dropdown.click()
time.sleep(1)

# 2- استنى القائمة تنزل واختار المورد بالنص أو بالكود
supplier_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), '200004 - مورد جديد معفي ضرئب')]")))
driver.execute_script("arguments[0].click();", supplier_option)

print("✅ اخترت المورد 200004 - مورد جديد معفي ضرئب")
time.sleep(1)

# فتح دروب داون الصنف
product_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(),'الصنف')]/following::span[contains(@class,'e-ddl-icon')][1]")))
product_dropdown.click()
time.sleep(1)

# اختيار الصنف المطلوب من القائمة
product_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[normalize-space()='001000007 - صنف جديد جدا']")))
product_option.click()
print("✅ اخترت الصنف")
time.sleep(1)

# كتابة الكمية في حقل الكمية
qty_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='grid-cellitmQty0']/input")))
qty_input.clear()     # تنظيف الحقل أولاً
qty_input.send_keys("10")
print("✅ أدخلت الكمية 10")
time.sleep(1)

# كتابة السعر في حقل السعر
price_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='grid-cellitmPrice0']/input")))
price_input.clear()     # تنظيف الحقل أولاً
price_input.send_keys("10")
print("✅ أدخلت السعر 10")
time.sleep(1)

# العثور على input "طريقة الدفع" وفتح الـ dropdown
# فتح قائمة طرق الدفع
payment_tab = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//button[normalize-space(text())='طريقة الدفع']")
))
payment_tab.click()
print("✅ فتحت تاب طريقة الدفع")
time.sleep(1)

payment_dropdown_icon = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//input[@placeholder='طريقة الدفع']/following-sibling::span[contains(@class,'e-ddl-icon')]")
))
payment_dropdown_icon.click()

# اختيار القيمة "1 - Cash2522" من القائمة
payment_option = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//li[normalize-space(text())='2 - Credit']")  # ممكن كمان تكتب contains(text(),'1 - Cash2522')
))
payment_option.click()

print("✅ اخترت طريقة الدفع")
time.sleep(1)


# حفظ الفاتورة
save_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//ul[@id='quick-menu-body']/li[5]/button")))
save_btn.click()
print("✅ حفظت الفاتورة")

time.sleep(6)
driver.quit()
