from selenium import webdriver
import random
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

# إعداد ChromeOptions مع بروفايل مخصص
options = Options()
options.add_argument(r"user-data-dir=D:\selenium\chrome_profile")  # مسار البروفايل
options.add_argument("--profile-directory=Default")  # أو Profile 1 حسب جهازك
options.add_argument("--start-maximized")

# استخدام webdriver-manager لتثبيت ChromeDriver المناسب تلقائيًا
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

wait = WebDriverWait(driver, 15)
short_wait = WebDriverWait(driver, 3)


def wait_click(locator):
    for attempt in range(3):
        try:
            element = wait.until(EC.element_to_be_clickable(locator))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            try:
                element.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", element)
            return
        except StaleElementReferenceException:
            if attempt == 2:
                raise


def wait_type(locator, value):
    for attempt in range(3):
        try:
            field = wait.until(EC.element_to_be_clickable(locator))
            field.clear()
            field.send_keys(value)
            return
        except StaleElementReferenceException:
            if attempt == 2:
                raise


def wait_click_any(locators):
    for locator in locators:
        try:
            wait_click(locator)
            return
        except TimeoutException:
            continue
    raise TimeoutException(f"No clickable locator matched: {locators}")


def get_open_list_options():
    return wait.until(
        lambda d: [
            el for el in d.find_elements(
                By.XPATH,
                "//div[contains(@class,'e-popup-open')]//li[contains(@class,'e-list-item') and not(contains(@class,'e-disabled')) and normalize-space()]"
            )
            if el.is_displayed()
        ]
    )


def wait_save_complete():
    spinner_locator = (By.XPATH, "//div[contains(@class,'e-spinner-pane')]")
    # أحيانًا الـ spinner لا يظهر، لذلك لا نفشل إذا لم يظهر.
    try:
        short_wait.until(EC.visibility_of_element_located(spinner_locator))
    except TimeoutException:
        pass
    wait.until(EC.invisibility_of_element_located(spinner_locator))
    # مهلة بصرية قصيرة لتأكيد الحفظ على الشاشة.
    time.sleep(0.8)

# فتح المتصفح الأول
print("✅ فتح المتصفح")

# فتح صفحة تسجيل الدخول (لو فيه سيشن محفوظة مش هيطلب Login)
driver.get("https://app.skeyerp.com/auth/ismailtest/login")
print("✅ فتح صفحة تسجيل الدخول")

# لو محتاج أول مرة تسجل الدخول بالكود بتاعك
try:
    usr_code = short_wait.until(EC.visibility_of_element_located((By.ID, "usrCode")))
    # تسجيل الدخول
    usr_code.send_keys("admin")
    driver.find_element(By.ID, "usrPswrd").send_keys("123456")

    wait_click(
        (By.XPATH, "//*[@id='index']/div[1]/div/div[1]/div/div/div/div[2]/form/div[4]/button")
    )

    # انتظار ظهور Dashboard
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="theme_Basic_theme"]')))
    print("✅ دخلت Dashboard")
except TimeoutException:
    print("ℹ️ غالبًا السيشن محفوظة بالفعل ومش محتاج Login")

# تأكيد وجود القائمة الجانبية قبل خطوات المشتريات
wait.until(EC.presence_of_element_located((By.ID, "sidebar-menu")))

# الذهاب لقائمة المشتريات
wait_click_any([
    (By.XPATH, "//ul[@id='sidebar-menu']//span[contains(normalize-space(.),'إدارة أنظمة المشتريات')]/ancestor::a[1]"),
    (By.XPATH, "//ul[@id='sidebar-menu']//span[contains(normalize-space(.),'المشتريات')]/ancestor::a[1]"),
    (By.XPATH, "//*[@id='sidebar-menu']/li[7]/a"),
])
print("✅ فتحت قائمة المشتريات")

# فتح شاشة إنشاء فاتورة جديدة
wait_click_any([
    (By.XPATH, "//ul[@id='sidebar-menu']//a[.//span[contains(normalize-space(.),'فاتورة المشتريات')]]"),
    (By.XPATH, "//ul[@id='sidebar-menu']//li[contains(@class,'open')]//a[.//span[contains(normalize-space(),'فاتورة')]]"),
    (By.XPATH, "//ul[@id='sidebar-menu']//li[contains(@class,'open')]//a[.//span[contains(normalize-space(),'شراء')]]"),
    (By.XPATH, "//*[@id='sidebar-menu']/li[7]/ul/li[2]/a"),
])
print("✅ فتح شاشة الفواتير")

# الضغط على زر جديد
# الضغط على زر جديد (إضافة)
wait_click((By.XPATH, "//div[@class='e-toolbar-item e-template' and @title='إضافة']"))
print("✅ ضغطت جديد")

# 1- اضغط على السهم لفتح القائمة
wait_click((By.XPATH, "(//span[contains(@class,'e-input-group-icon')])[4]"))

# 3- لما تنزل، دور على الخيار بالمخزن
wait_click((By.XPATH, "//li[contains(., '201 - المخزن الرئيسي')]"))

# 1- افتح سهم المورد
wait_click((By.XPATH, "(//span[contains(@class,'e-ddl-icon') and contains(@class,'e-search-icon')])[4]"))

# 2- استنى القائمة تنزل واختار مورد عشوائي من العناصر الظاهرة
supplier_options = wait.until(
    lambda d: [
        el for el in d.find_elements(
            By.XPATH,
            "//div[contains(@class,'e-popup-open')]//li[contains(@class,'e-list-item') and not(contains(@class,'e-disabled')) and normalize-space()]"
        )
        if el.is_displayed()
    ]
)
random_supplier = random.choice(supplier_options)
supplier_name = random_supplier.text.strip()
driver.execute_script("arguments[0].click();", random_supplier)
print(f"✅ اخترت المورد عشوائيًا: {supplier_name}")

# فتح دروب داون الصنف
wait_click((By.XPATH, "//label[contains(text(),'الصنف')]/following::span[contains(@class,'e-ddl-icon')][1]"))

# اختيار صنف عشوائي من العناصر الظاهرة
item_options = wait.until(
    lambda d: [
        el for el in d.find_elements(
            By.XPATH,
            "//div[contains(@class,'e-popup-open')]//li[contains(@class,'e-list-item') and not(contains(@class,'e-disabled')) and normalize-space()]"
        )
        if el.is_displayed()
    ]
)
random_item = random.choice(item_options)
item_name = random_item.text.strip()
driver.execute_script("arguments[0].click();", random_item)
print(f"✅ اخترت الصنف عشوائيًا: {item_name}")

# تجهيز كميات مختلفة لكل مرة
qty_values = random.sample(range(5, 25), 3)
initial_qty, first_edit_qty, second_edit_qty = [str(q) for q in qty_values]

# كتابة الكمية في حقل الكمية
wait_type((By.XPATH, "//*[@id='grid-cellitmQty0']/input"), initial_qty)
print(f"✅ أدخلت الكمية {initial_qty}")

# كتابة السعر في حقل السعر
wait_type((By.XPATH, "//*[@id='grid-cellitmPrice0']/input"), "10")
print("✅ أدخلت السعر 10")
########################################################


# العثور على input "طريقة الدفع" وفتح الـ dropdown
# فتح قائمة طرق الدفع
wait_click_any([
    (By.XPATH, "//button[normalize-space(text())='طريقة الدفع']"),
    (By.XPATH, "//button[contains(normalize-space(.),'طريقة الدفع')]"),
])
print("✅ فتحت تاب طريقة الدفع")

wait_click_any([
    (By.XPATH, "//input[@placeholder='طريقة الدفع']/following-sibling::span[contains(@class,'e-ddl-icon')]"),
    (By.XPATH, "//input[contains(@placeholder,'الدفع')]/following-sibling::span[contains(@class,'e-ddl-icon')]"),
])

# اختيار طريقة دفع مرنة: يفضل Cash، وإلا يختار أول قيمة ظاهرة
payment_options = get_open_list_options()
preferred_payment = next((opt for opt in payment_options if "cash" in opt.text.lower()), None)
selected_payment = preferred_payment or payment_options[0]
payment_name = selected_payment.text.strip()
driver.execute_script("arguments[0].click();", selected_payment)
print(f"✅ اخترت طريقة الدفع: {payment_name}")


# افتح السهم الخاص برقم الصندوق
wait_click_any([
    (By.XPATH, "//input[@placeholder='رقم الصندوق']/following-sibling::span[contains(@class,'e-ddl-icon')]"),
    (By.XPATH, "//input[contains(@placeholder,'الصندوق')]/following-sibling::span[contains(@class,'e-ddl-icon')]"),
])

# اختيار صندوق مرن: يفضل 2001/رئيسي، وإلا يختار أول صندوق ظاهر
box_options = get_open_list_options()
preferred_box = next(
    (opt for opt in box_options if "2001" in opt.text or "رئيسي" in opt.text),
    None
)
selected_box = preferred_box or box_options[0]
box_name = selected_box.text.strip()
driver.execute_script("arguments[0].click();", selected_box)
print(f"✅ اخترت الصندوق: {box_name}")

# حفظ الفاتورة
wait_click((By.XPATH, "//ul[@id='quick-menu-body']/li[5]/button"))
print("✅ حفظت الفاتورة")

# تأكيد أن الحفظ اكتمل
wait_save_complete()

# تعديل الفاتورة بعد الحفظ
# بعض الشاشات تتطلب تحديد السطر الحالي قبل تفعيل زر التعديل
try:
    wait_click_any([
        (By.XPATH, "//tr[contains(@class,'e-row') and @aria-rowindex='1']"),
        (By.XPATH, "(//tr[contains(@class,'e-row')])[1]"),
    ])
except TimeoutException:
    pass

wait_click_any([
    (By.XPATH, "//button[@title='تعديل-']"),
    (By.XPATH, "//button[contains(@title,'تعديل')]"),
    (By.XPATH, "//button[i[contains(@class,'fa-edit')]]"),
    (By.XPATH, "//ul[@id='quick-menu-body']//button[contains(normalize-space(.), 'تعديل')]"),
    (By.XPATH, "//ul[@id='quick-menu-body']//button[contains(normalize-space(.), 'تحرير')]"),
])
print("✅ فتحت وضع تعديل الفاتورة")

# تحديث الكمية والسعر ثم إعادة الحفظ
wait_type((By.XPATH, "//*[@id='grid-cellitmQty0']/input"), first_edit_qty)
wait_type((By.XPATH, "//*[@id='grid-cellitmPrice0']/input"), "11")
print(f"✅ عدلت الكمية إلى {first_edit_qty} والسعر")

wait_click_any([
    (By.XPATH, "//ul[@id='quick-menu-body']/li[5]/button"),
    (By.XPATH, "//ul[@id='quick-menu-body']//button[contains(normalize-space(.), 'حفظ')]"),
])
print("✅ حفظت التعديل على الفاتورة")

wait_save_complete()

# تعديل ثاني: تغيير طريقة الدفع + كمية مختلفة
wait_click_any([
    (By.XPATH, "//button[@title='تعديل-']"),
    (By.XPATH, "//button[contains(@title,'تعديل')]"),
    (By.XPATH, "//button[i[contains(@class,'fa-edit')]]"),
    (By.XPATH, "//ul[@id='quick-menu-body']//button[contains(normalize-space(.), 'تعديل')]"),
    (By.XPATH, "//ul[@id='quick-menu-body']//button[contains(normalize-space(.), 'تحرير')]"),
])
print("✅ فتحت وضع تعديل الفاتورة مرة ثانية")

wait_type((By.XPATH, "//*[@id='grid-cellitmQty0']/input"), second_edit_qty)
print(f"✅ عدلت الكمية مرة ثانية إلى {second_edit_qty}")

wait_click_any([
    (By.XPATH, "//button[normalize-space(text())='طريقة الدفع']"),
    (By.XPATH, "//button[contains(normalize-space(.),'طريقة الدفع')]"),
])

# احذف طريقة الدفع الحالية أولًا ثم أضف طريقة جديدة
try:
    wait_click_any([
        (By.XPATH, "//button[i[contains(@class,'fa-trash-alt')]]"),
        (By.XPATH, "//i[contains(@class,'fa-trash-alt')]/ancestor::button[1]"),
    ])
    print("✅ حذفت طريقة الدفع القديمة")
except TimeoutException:
    print("ℹ️ لا توجد طريقة دفع قديمة لحذفها")

wait_click_any([
    (By.XPATH, "//input[@placeholder='طريقة الدفع']/following-sibling::span[contains(@class,'e-ddl-icon')]"),
    (By.XPATH, "//input[contains(@placeholder,'الدفع')]/following-sibling::span[contains(@class,'e-ddl-icon')]"),
])

payment_options_second = get_open_list_options()
alternative_payment = next(
    (opt for opt in payment_options_second if opt.text.strip() != payment_name),
    None
)
selected_payment_second = alternative_payment or payment_options_second[0]
payment_name_second = selected_payment_second.text.strip()
driver.execute_script("arguments[0].click();", selected_payment_second)
print(f"✅ غيرت طريقة الدفع إلى: {payment_name_second}")

wait_click_any([
    (By.XPATH, "//ul[@id='quick-menu-body']/li[5]/button"),
    (By.XPATH, "//ul[@id='quick-menu-body']//button[contains(normalize-space(.), 'حفظ')]"),
])
print("✅ حفظت التعديل الثاني على الفاتورة")

wait_save_complete()
driver.quit()
