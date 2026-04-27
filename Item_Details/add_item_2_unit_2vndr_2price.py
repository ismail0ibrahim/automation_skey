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

wait = WebDriverWait(driver, 5)
short_wait = WebDriverWait(driver, 3)

# توقف قصير بين خطوات الواجهة (زِد القيمة لو الواجهة بطيئة)
STEP_DELAY = 0.5

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


def click_dynamic_list_option(get_options, pick_option, max_attempts=4):
    """
    Re-locate popup options on each retry to avoid stale references.
    """
    last_error = None
    for _ in range(max_attempts):
        try:
            options = get_options()
            if not options:
                raise TimeoutException("No visible options in open popup list.")
            selected = pick_option(options)
            selected_text = selected.text.strip()
            driver.execute_script("arguments[0].click();", selected)
            return selected_text
        except StaleElementReferenceException as exc:
            last_error = exc
            time.sleep(0.3)
    if last_error:
        raise last_error
    raise TimeoutException("Failed to click dynamic list option.")


def wait_save_complete():
    spinner_locator = (By.XPATH, "//div[contains(@class,'e-spinner-pane')]")
    # أحيانًا الـ spinner لا يظهر، لذلك لا نفشل إذا لم يظهر.
    try:
        short_wait.until(EC.visibility_of_element_located(spinner_locator))
    except TimeoutException:
        pass
    wait.until(EC.invisibility_of_element_located(spinner_locator))
    # مهلة بصرية قصيرة لتأكيد الحفظ على الشاشة.
    time.sleep(0.5)


def open_invoice_edit_mode():
    # نجرب عدة locators لأن زر "تعديل" قد يختلف شكله بين الشاشات.
    wait_click_any([
        (By.XPATH, "//button[@title='تعديل-']"),
        (By.XPATH, "//button[contains(@title,'تعديل')]"),
        (By.XPATH, "//button[i[contains(@class,'fa-edit')]]"),
        (By.XPATH, "//ul[@id='quick-menu-body']//button[contains(normalize-space(.), 'تعديل')]"),
        (By.XPATH, "//ul[@id='quick-menu-body']//button[contains(normalize-space(.), 'تحرير')]"),
    ])


def change_payment_method_after_second_edit(previous_payment_name):
    # افتح تبويب طريقة الدفع أثناء التعديل الثاني.
    wait_click_any([
        (By.XPATH, "//button[normalize-space(text())='طريقة الدفع']"),
        (By.XPATH, "//button[contains(normalize-space(.),'طريقة الدفع')]"),
    ])

    # حاول حذف الطريقة الحالية حتى نضمن اختيار قيمة جديدة.
    try:
        wait_click_any([
            (By.XPATH, "//button[i[contains(@class,'fa-trash-alt')]]"),
            (By.XPATH, "//i[contains(@class,'fa-trash-alt')]/ancestor::button[1]"),
        ])
        print("[OK] حذفت طريقة الدفع القديمة")
    except TimeoutException:
        print("[INFO] لا توجد طريقة دفع قديمة لحذفها")

    # افتح dropdown الخاص بطريقة الدفع.
    wait_click_any([
        (By.XPATH, "//input[@placeholder='طريقة الدفع']/following-sibling::span[contains(@class,'e-ddl-icon')]"),
        (By.XPATH, "//input[contains(@placeholder,'الدفع')]/following-sibling::span[contains(@class,'e-ddl-icon')]"),
    ])

    # اختَر طريقة مختلفة عن السابقة، وإن لم توجد اختر أول خيار.
    new_payment_name = click_dynamic_list_option(
        get_options=get_open_list_options,
        pick_option=lambda options: next(
            (opt for opt in options if opt.text.strip() != previous_payment_name),
            options[0]
        ),
    )
    print(f"[OK] غيرت طريقة الدفع إلى: {new_payment_name}")
    return new_payment_name

# فتح المتصفح الأول
print("[OK] فتح المتصفح")


# فتح صفحة تسجيل الدخول (لو فيه سيشن محفوظة مش هيطلب Login)
driver.get("https://app.skeyerp.com/auth/ismailtest/login")
print("[OK] فتح صفحة تسجيل الدخول")

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
    print("[OK] دخلت Dashboard")
except TimeoutException:
    print("[INFO] غالبًا السيشن محفوظة بالفعل ومش محتاج Login")

# تأكيد وجود القائمة الجانبية قبل خطوات المشتريات
wait.until(EC.presence_of_element_located((By.ID, "sidebar-menu")))

# الذهاب لقائمة المشتريات
wait_click_any([
    (By.XPATH, "//ul[@id='sidebar-menu']//span[contains(normalize-space(.),'إدارة أنظمة المشتريات')]/ancestor::a[1]"),
    (By.XPATH, "//ul[@id='sidebar-menu']//span[contains(normalize-space(.),'المشتريات')]/ancestor::a[1]"),
    (By.XPATH, "//*[@id='sidebar-menu']/li[7]/a"),
])
print("[OK] فتحت قائمة المشتريات")

# فتح شاشة إنشاء فاتورة جديدة
wait_click_any([
    (By.XPATH, "//ul[@id='sidebar-menu']//a[.//span[contains(normalize-space(.),'فاتورة المشتريات')]]"),
    (By.XPATH, "//ul[@id='sidebar-menu']//li[contains(@class,'open')]//a[.//span[contains(normalize-space(),'فاتورة')]]"),
    (By.XPATH, "//ul[@id='sidebar-menu']//li[contains(@class,'open')]//a[.//span[contains(normalize-space(),'شراء')]]"),
    (By.XPATH, "//*[@id='sidebar-menu']/li[7]/ul/li[2]/a"),
])
print("[OK] فتح شاشة الفواتير")

# الضغط على زر جديد
# الضغط على زر جديد (إضافة)
wait_click((By.XPATH, "//div[@class='e-toolbar-item e-template' and @title='إضافة']"))
print("[OK] ضغطت جديد")

# 1- اضغط على السهم لفتح القائمة
wait_click((By.XPATH, "(//span[contains(@class,'e-input-group-icon')])[4]"))

# 3- لما تنزل، دور على الخيار بالمخزن
wait_click((By.XPATH, "//li[contains(., '201 - المخزن الرئيسي')]"))

# 1- افتح سهم المورد
wait_click((By.XPATH, "(//span[contains(@class,'e-ddl-icon') and contains(@class,'e-search-icon')])[4]"))

# 2- استنى القائمة تنزل واختار مورد عشوائي من العناصر الظاهرة
supplier_name = click_dynamic_list_option(
    get_options=get_open_list_options,
    pick_option=lambda options: random.choice(options),
)
print(f"[OK] اخترت المورد عشوائيًا: {supplier_name}")

# فتح دروب داون الصنف
wait_click((By.XPATH, "//label[contains(text(),'الصنف')]/following::span[contains(@class,'e-ddl-icon')][1]"))

# اختيار صنف عشوائي من العناصر الظاهرة
item_name = click_dynamic_list_option(
    get_options=get_open_list_options,
    pick_option=lambda options: random.choice(options),
)
print(f"[OK] اخترت الصنف عشوائيًا: {item_name}")

# تجهيز كميات مختلفة لكل مرة
qty_values = random.sample(range(5, 25), 3)
initial_qty, first_edit_qty, second_edit_qty = [str(q) for q in qty_values]

# كتابة الكمية في حقل الكمية
wait_type((By.XPATH, "//*[@id='grid-cellitmQty0']/input"), initial_qty)
print(f"[OK] أدخلت الكمية {initial_qty}")

# كتابة السعر في حقل السعر
wait_type((By.XPATH, "//*[@id='grid-cellitmPrice0']/input"), "10")
print("[OK] أدخلت السعر 10")
########################################################


# العثور على input "طريقة الدفع" وفتح الـ dropdown
# فتح قائمة طرق الدفع
wait_click_any([
    (By.XPATH, "//button[normalize-space(text())='طريقة الدفع']"),
    (By.XPATH, "//button[contains(normalize-space(.),'طريقة الدفع')]"),
])
print("[OK] فتحت تاب طريقة الدفع")

wait_click_any([
    (By.XPATH, "//input[@placeholder='طريقة الدفع']/following-sibling::span[contains(@class,'e-ddl-icon')]"),
    (By.XPATH, "//input[contains(@placeholder,'الدفع')]/following-sibling::span[contains(@class,'e-ddl-icon')]"),
])

# اختيار طريقة دفع مرنة: يفضل Cash، وإلا يختار أول قيمة ظاهرة
payment_name = click_dynamic_list_option(
    get_options=get_open_list_options,
    pick_option=lambda options: next((opt for opt in options if "cash" in opt.text.lower()), options[0]),
)
print(f"[OK] اخترت طريقة الدفع: {payment_name}")


# افتح السهم الخاص برقم الصندوق
wait_click_any([
    (By.XPATH, "//input[@placeholder='رقم الصندوق']/following-sibling::span[contains(@class,'e-ddl-icon')]"),
    (By.XPATH, "//input[contains(@placeholder,'الصندوق')]/following-sibling::span[contains(@class,'e-ddl-icon')]"),
])

# اختيار صندوق مرن: يفضل 2001/رئيسي، وإلا يختار أول صندوق ظاهر
box_name = click_dynamic_list_option(
    get_options=get_open_list_options,
    pick_option=lambda options: next(
        (opt for opt in options if "2001" in opt.text or "رئيسي" in opt.text),
        options[0]
    ),
)
print(f"[OK] اخترت الصندوق: {box_name}")

# حفظ الفاتورة
wait_click((By.XPATH, "//ul[@id='quick-menu-body']/li[5]/button"))
print("[OK] حفظت الفاتورة")

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

open_invoice_edit_mode()
print("[OK] فتحت وضع تعديل الفاتورة")

# تحديث الكمية والسعر ثم إعادة الحفظ
wait_type((By.XPATH, "//*[@id='grid-cellitmQty0']/input"), first_edit_qty)
wait_type((By.XPATH, "//*[@id='grid-cellitmPrice0']/input"), "11")
print(f"[OK] عدلت الكمية إلى {first_edit_qty} والسعر")

wait_click_any([
    (By.XPATH, "//ul[@id='quick-menu-body']/li[5]/button"),
    (By.XPATH, "//ul[@id='quick-menu-body']//button[contains(normalize-space(.), 'حفظ')]"),
])
print("[OK] حفظت التعديل على الفاتورة")

wait_save_complete()

# تعديل ثاني: تغيير طريقة الدفع + كمية مختلفة
open_invoice_edit_mode()
print("[OK] فتحت وضع تعديل الفاتورة مرة ثانية")

wait_type((By.XPATH, "//*[@id='grid-cellitmQty0']/input"), second_edit_qty)
print(f"[OK] عدلت الكمية مرة ثانية إلى {second_edit_qty}")

# نفذ تغيير طريقة الدفع في دالة مستقلة لسهولة الفهم وإعادة الاستخدام.
payment_name_second = change_payment_method_after_second_edit(payment_name)

wait_click_any([
    (By.XPATH, "//ul[@id='quick-menu-body']/li[5]/button"),
    (By.XPATH, "//ul[@id='quick-menu-body']//button[contains(normalize-space(.), 'حفظ')]"),
])
print("[OK] حفظت التعديل الثاني على الفاتورة")

wait_save_complete()
driver.quit()
