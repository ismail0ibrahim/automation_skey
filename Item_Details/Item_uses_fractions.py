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

wait = WebDriverWait(driver, 3)

# فتح الصفحة
driver.get("https://app.skeyerp.com/auth/Dev/login")
time.sleep(3)

# ✅ الدخول إلى القائمة الجانبية
driver.find_element(By.XPATH, "//*[@id='sidebar-menu']/li[5]/a").click()
time.sleep(2)

driver.find_element(By.XPATH, "//ul[@id='sidebar-menu']/li[5]/ul/li/a/span").click()
time.sleep(2.5)

# ✅ الضغط على زر الإضافة (أو أيقونة معينة)
driver.find_element(By.XPATH, "//div[@id='itemData70_toolbarItems']/div/div/div/i").click()
time.sleep(1.5)

# ✅ فتح قائمة منسدلة
driver.find_element(By.XPATH, "//ejs-combobox[@id='ej2_dropdownlist_0']//span[contains(@class, 'e-ddl-icon')]").click()
time.sleep(1.5)

# انتظار ظهور القائمة ثم اختيار اسم المجموعة
group_option = WebDriverWait(driver, 3).until(
    EC.element_to_be_clickable((By.XPATH, "//li[contains(., '001 - مجموعة عامة11')]")))
# الضغط على اسم المجموعة
group_option.click()
time.sleep(1)

# ✅ قراءة آخر رقم من الملف (أو البدء من 0)
try:
    with open("counter.txt", "r", encoding="utf-8") as f:
        counter = int(f.read().strip())
except:
    counter = 0

# ✅ زيادة الرقم واحد
counter += 1

# ✅ توليد اسم الصنف الجديد
item_name = f"item use fractions {counter}"

# ✅ حفظ الرقم الجديد في الملف
with open("counter.txt", "w", encoding="utf-8") as f:
    f.write(str(counter))

# ✅ تحديد الحقل وكتابة الاسم الجديد
itm_name = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='اسم الصنف']"))
)
itm_name.clear()
itm_name.send_keys(item_name)

print(f"✅ تمت كتابة اسم الصنف: {item_name}")

# إدخال التكلفة الأولية = 10
cost_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='itmPrmryCost']")))
cost_field.clear()
cost_field.send_keys("10")
time.sleep(1)
print("✅ تم إدخال التكلفة الأولية بنجاح (10)")

# التمرير إلى خانة "يستخدم الكسور"

uses_fractions_checkbox = driver.find_element(By.XPATH, "(//*[@id='_name'])[7]")
driver.execute_script("arguments[0].scrollIntoView(true);", uses_fractions_checkbox)
time.sleep(0.5)

# إدخال خانة "يستخدم الكسور" = نعم
uses_fractions_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@id='_name'])[7]")))
# التحقق مما إذا كانت خانة الاختيار غير محددة، ثم النقر عليها لتحديدها
if not uses_fractions_checkbox.is_selected():
    uses_fractions_checkbox.click()
    print("✅ تم تحديد خانة 'يستخدم الكسور'")
else:
    print("✅ خانة 'يستخدم الكسور' محددة بالفعل")
time.sleep(1)


# ✅ افتح تبويب "وحدات القياس"
driver.find_element(By.XPATH, "//a[@id='InvItmMunt']/span").click()
time.sleep(1)

# ✅ فتح وحدات القياس
open_units_dropdown_xpath = "(//span[contains(@class,'e-ddl-icon') and contains(@class,'e-search-icon')])[11]"
driver.find_element(By.XPATH, open_units_dropdown_xpath).click()
time.sleep(1)

# ✅ الآن اختر العنصر "Unit"
unit_option = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//li[normalize-space(.)='Unit']"))
)
unit_option.click()
print("✅ تم اختيار وحدة القياس: Unit ✅")
time.sleep(0.5)

# ✅ الضغط على زر الإضافة داخل تبويب وحدات القياس
driver.find_element(By.XPATH, "(//*[@id='Word'])[1]").click()
time.sleep(0.5)

#فتح قائمة البحث عن الوحدة
driver.find_element(By.XPATH, "(//span[contains(@class,'e-input-group-icon') and contains(@class,'e-ddl-icon') and contains(@class,'e-search-icon')])[12]").click()
time.sleep(0.5)

# ✅ الآن اختر العنصر "جديد"
unit_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[normalize-space(.)='جديد']")))
unit_option.click()
time.sleep(1)

# ✅ اضافة العبوة للوحده الجديده
cost_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='grid-cellitmSz1']/input")))
cost_field.clear()
cost_field.send_keys("12")
time.sleep(1)
print("✅ تم إدخال العبوة بنجاح (12)")


# ✅ حفظ أو تنفيذ العملية النهائية
driver.find_element(By.XPATH, "//ul[@id='quick-menu-body']/li[5]/button/i").click()

time.sleep(3)
driver.quit()
