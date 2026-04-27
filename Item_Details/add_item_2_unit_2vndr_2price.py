import os
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# تجنب UnicodeEncodeError على طُرفيات Windows (cp1256) عند طباعة الرموز التعبيرية
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# مهلة انتظار منطقية (ثوانٍ) — العنصر يُستدعى فور جاهزيته دون نوم ثابت
MAX_WAIT = 120
# توقف ثابت قبل كل عملية (نقر / قائمة / كتابة). الافتراضي 1ث؛ خفّضه لتسريع التشغيل.
# مثال PowerShell: $env:STEP_DELAY="0.25"; python add_item_2_unit_2vndr_2price.py
STEP_DELAY = float(os.environ.get("STEP_DELAY", "0.5"))


def step_pause() -> None:
    time.sleep(STEP_DELAY)


def wait_click(driver, wait, locator):
    """نقرة مع انتظار (مثل pur_cash.py) — scroll + JS click عند الحجب."""
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


def click_when_ready(xpath: str) -> None:
    step_pause()
    wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()


def _visible_list_candidates():
    """عناصر قائمة Syncfusion المحتملة (القائمة المفتوحة غالبًا تحتوي e-list-item)."""
    return driver.find_elements(
        By.XPATH,
        (
            "//div[contains(@class,'e-popup-open')]//li"
            " | //li[contains(@class,'e-list-item')]"
            " | //div[contains(@class,'e-list-item')]"
            " | //*[@role='option']"
        ),
    )


def click_visible_list_option(exact_text: str) -> None:
    """
    يختار خيارًا من القائمة المفتوحة حسب النص الكامل.
    لا يعتمد على أول //li في DOM (قد يكون مخفيًا) — فقط عناصر ظاهرة.
    """
    step_pause()

    def pick() -> bool:
        for el in _visible_list_candidates():
            try:
                if not el.is_displayed():
                    continue
                t = (el.text or "").strip()
                if t == exact_text:
                    driver.execute_script("arguments[0].click();", el)
                    return True
            except StaleElementReferenceException:
                continue
        return False

    wait.until(lambda _: pick())


def click_visible_list_option_contains(substring: str) -> None:
    """مثل click_visible_list_option لكن يطابق إذا كان substring جزءًا من نص الخيار."""
    step_pause()

    def pick() -> bool:
        for el in _visible_list_candidates():
            try:
                if not el.is_displayed():
                    continue
                if substring in (el.text or ""):
                    driver.execute_script("arguments[0].click();", el)
                    return True
            except StaleElementReferenceException:
                continue
        return False

    wait.until(lambda _: pick())


def click_add_row_sales_price_grid() -> None:
    """
    إضافة سطر في جدول أسعار البيع.
    يجرّب المسارات بالترتيب؛ أول محاولة تُظهر السطر الثاني (grid-cellitmPrice1) تنجح ثم
    return يوقف الدالة — لا يُجرَّب [5] إذا نجح [4] ولا أي مسار بعد أول نجاح.
    """
    step_pause()
    candidate_xpaths = [
        "(//*[@id='grid-cellitmPrice0']/ancestor::div[contains(@class,'e-grid')]//*[@id='Word'])[last()]",
        "(//*[@id='grid-cellitmPrice0']/ancestor::*[contains(@class,'e-grid')]//*[@id='Word'])[last()]",
        "//*[@id='SalItmPrice']/following::*//*[@id='grid-cellitmPrice0']/ancestor::div[contains(@class,'e-content')]//*[@id='Word'][last()]",
        "(//*[@id='Word'])[4]",
        "(//*[@id='Word'])[5]",
    ]

    row2_input_xpath = "//*[@id='grid-cellitmPrice1']/input"
    wait_row = WebDriverWait(driver, 15)
    last_exc: Exception | None = None

    def second_row_already_there() -> bool:
        return bool(driver.find_elements(By.XPATH, row2_input_xpath))

    def try_one_click(xp: str) -> bool:
        """نقرة واحدة؛ نجاح = ظهور سطر السعر الثاني بعد النقرة (وليس كان موجودًا من قبل)."""
        nonlocal last_exc
        if second_row_already_there():
            return True
        try:
            el = wait.until(EC.presence_of_element_located((By.XPATH, xp)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            driver.execute_script("arguments[0].click();", el)
            wait_row.until(EC.presence_of_element_located((By.XPATH, row2_input_xpath)))
            return True
        except (TimeoutException, StaleElementReferenceException) as exc:
            last_exc = exc
            return False

    for xp in candidate_xpaths:
        if try_one_click(xp):
            return

    raise TimeoutException(
        "تعذر إضافة سطر جديد في أسعار البيع (زر Word داخل جدول السعر أو [4]/[5])."
        + (f" آخر خطأ: {last_exc!r}" if last_exc else "")
    )


def sign_out_via_profile(driver, wait) -> None:
    """
    بعد الحفظ: النقر على صورة البروفايل في الهيدر ثم «تسجيل خروج» / «تسجيل الخروج».
    يطابق صورة المستخدم الافتراضية (defualt-img.jpg في المسار كما في التطبيق).
    """
    step_pause()
    profile_locators = [
        (
            By.XPATH,
            "//img[@alt='image' and contains(@class,'rounded-circle') and contains(@src,'defualt-img.jpg')]",
        ),
        (By.XPATH, "//img[contains(@class,'rounded-circle') and contains(@src,'defualt-img.jpg')]"),
        (By.XPATH, "//img[@alt='image' and contains(@class,'rounded-circle')]"),
    ]
    last_prof: Exception | None = None
    for loc in profile_locators:
        try:
            wait_click(driver, WebDriverWait(driver, 12), loc)
            break
        except TimeoutException as exc:
            last_prof = exc
    else:
        raise TimeoutException("لم يُعثر على صورة البروفايل في الهيدر") from last_prof

    step_pause()
    # الواجهة تعرض النص في <span>تسجيل خروج</span> (بدون «ال») — نفضّل الأسلاف القابلة للنقر ثم الـ span.
    sign_out_locators = [
        (By.XPATH, "//span[normalize-space()='تسجيل خروج']/ancestor::a[1]"),
        (By.XPATH, "//span[normalize-space()='تسجيل خروج']/ancestor::button[1]"),
        (By.XPATH, "//span[normalize-space()='تسجيل خروج']/ancestor::li[1]"),
        (By.XPATH, "//span[normalize-space()='تسجيل خروج']"),
        (By.XPATH, "//a[normalize-space()='تسجيل الخروج']"),
        (By.XPATH, "//button[normalize-space()='تسجيل الخروج']"),
        (By.XPATH, "//*[contains(normalize-space(.),'تسجيل الخروج') and (self::a or self::button)]"),
        (By.XPATH, "//a[contains(normalize-space(.),'Sign out')]"),
        (By.XPATH, "//a[contains(normalize-space(.),'Logout')]"),
    ]
    last_out: Exception | None = None
    short = WebDriverWait(driver, 6)
    for loc in sign_out_locators:
        try:
            wait_click(driver, short, loc)
            print("[OK] تم تسجيل الخروج")
            try:
                short.until(EC.presence_of_element_located((By.ID, "usrCode")))
            except TimeoutException:
                pass
            return
        except TimeoutException as exc:
            last_out = exc
    # لو الـ span ظاهر لكن Selenium لا يعتبره clickable، ننقر بـ JS على نفس النص.
    try:
        el = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//span[normalize-space()='تسجيل خروج']"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        driver.execute_script("arguments[0].click();", el)
        print("[OK] تم تسجيل الخروج")
        try:
            short.until(EC.presence_of_element_located((By.ID, "usrCode")))
        except TimeoutException:
            pass
        return
    except TimeoutException:
        pass
    raise TimeoutException("لم يُعثر على خيار تسجيل الخروج في قائمة المستخدم") from last_out


LOOP_COUNT = 10

for run in range(1, LOOP_COUNT + 1):
    print(f"\n=== تشغيل الدورة {run}/{LOOP_COUNT} — السيناريو كامل من فتح المتصفح ===\n")

    # إعداد المتصفح وفتحه — بداية كل دورة (ليس فقط إعادة تحميل الموقع)
    options = Options()
    options.add_argument(r"user-data-dir=D:\selenium\chrome_profile")  # مسار البروفايل
    options.add_argument("--profile-directory=Default")  # أو Profile 1 حسب جهازك
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, MAX_WAIT)
    short_wait = WebDriverWait(driver, 5)

    print("[OK] فتح المتصفح")

    # فتح صفحة تسجيل الدخول (لو فيه سيشن محفوظة مش هيطلب Login) — نفس منطق pur_cash.py
    driver.get("https://app.skeyerp.com/auth/ismailtest/login")
    print("[OK] فتح صفحة تسجيل الدخول")

    try:
        usr_code = short_wait.until(EC.visibility_of_element_located((By.ID, "usrCode")))
        usr_code.send_keys("admin")
        driver.find_element(By.ID, "usrPswrd").send_keys("123456")
        wait_click(
            driver,
            wait,
            (By.XPATH, "//*[@id='index']/div[1]/div/div[1]/div/div/div/div[2]/form/div[4]/button"),
        )
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="theme_Basic_theme"]')))
        print("[OK] دخلت Dashboard")
    except TimeoutException:
        print("[INFO] غالبًا السيشن محفوظة بالفعل ومش محتاج Login")

    wait.until(EC.presence_of_element_located((By.ID, "sidebar-menu")))
    step_pause()

    # ✅ الدخول إلى القائمة الجانبية
    click_when_ready("//*[@id='sidebar-menu']/li[5]/a")
    click_when_ready("//ul[@id='sidebar-menu']/li[5]/ul/li/a/span")

    # ✅ الضغط على زر الإضافة (أو أيقونة معينة)
    click_when_ready("//div[@id='itemData70_toolbarItems']/div/div/div/i")
    step_pause()
    # ✅ فتح قائمة منسدلة
    click_when_ready("(//span[contains(@class,'e-search-icon')])[2]")

    # انتظار ظهور القائمة ثم اختيار اسم المجموعة (خيار ظاهر فقط — لا أول li في DOM)
    click_visible_list_option_contains("001 - مجموعة عامة")

    # ✅ قراءة آخر رقم من الملف (أو البدء من 0)
    try:
        with open("counter.txt", "r", encoding="utf-8") as f:
            counter = int(f.read().strip())
    except Exception:
        counter = 0

    # ✅ زيادة الرقم واحد
    counter += 1

    # ✅ توليد اسم الصنف الجديد
    item_name = f"item {counter}"
    item_code = str(counter)

    # ✅ حفظ الرقم الجديد في الملف
    with open("counter.txt", "w", encoding="utf-8") as f:
        f.write(str(counter))

    # ✅ تحديد حقل رقم الصنف وكتابة الرقم
    step_pause()
    itm_code = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//input[@name='itmCode' and @placeholder='رقم الصنف']"))
    )
    itm_code.clear()
    itm_code.send_keys(item_code)
    print(f"✅ تم إدخال رقم الصنف: {item_code}")

    # ✅ تحديد الحقل وكتابة الاسم الجديد
    step_pause()
    itm_name = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='اسم الصنف']"))
    )
    itm_name.clear()
    itm_name.send_keys(item_name)

    print(f"✅ تمت كتابة اسم الصنف: {item_name}")

    # إدخال التكلفة الأولية = 10
    step_pause()
    cost_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='itmPrmryCost']")))
    cost_field.clear()
    cost_field.send_keys("10")
    print("✅ تم إدخال التكلفة الأولية بنجاح (10)")

    # ✅ افتح تبويب "وحدات القياس"
    click_when_ready("//a[@id='InvItmMunt']/span")

    # ✅ فتح وحدات القياس
    open_units_dropdown_xpath = "(//span[contains(@class,'e-ddl-icon') and contains(@class,'e-search-icon')])[9]"
    click_when_ready(open_units_dropdown_xpath)

    # ✅ الآن اختر العنصر "Unit"
    click_visible_list_option("Unit")
    print("✅ تم اختيار وحدة القياس: Unit ✅")

    # ✅ الضغط على زر الإضافة داخل تبويب وحدات القياس
    click_when_ready("(//*[@id='Word'])[1]")

    # فتح قائمة البحث عن الوحدة
    click_when_ready(
        "(//span[contains(@class,'e-input-group-icon') and contains(@class,'e-ddl-icon') and contains(@class,'e-search-icon')])[10]"
    )

    # ✅ الآن اختر العنصر "Box"
    click_visible_list_option("Box")

    # ✅ اضافة العبوة للوحده الجديده
    step_pause()
    cost_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='grid-cellitmSz1']/input")))
    cost_field.clear()
    cost_field.send_keys("12")
    print("✅ تم إدخال العبوة بنجاح (12)")

    # ✅ فتح تبويب "الموردين"
    click_when_ready("//*[@id='InvItmVndr']")

    # فتح قائمة البحث عن المورد الاول
    click_when_ready(
        "(//span[contains(@class,'e-input-group-icon') and contains(@class,'e-ddl-icon') and contains(@class,'e-search-icon')])[11]"
    )

    # ✅ الآن اختر العنصر "200001 - المورد الاول"
    click_visible_list_option("200001 - المورد الاول")
      
    # ✅ فتح تابة وحدة قياس المورد
    InvItmVndr_units_dropdown_xpath = "(//span[contains(@class,'e-input-group-icon') and contains(@class,'e-ddl-icon') and contains(@class,'e-search-icon')])[12]"
    click_when_ready(InvItmVndr_units_dropdown_xpath)

    # ✅ الآن اختر العنصر "Unit"
    click_visible_list_option("Unit")
    print("✅ تم اختيار وحدة قياس المورد: Unit ✅")

    # إدخال سعر المورد = 20
    step_pause()
    cost_field_InvItmVndr = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='grid-cellvndrItmPrice0']/input")))
    cost_field_InvItmVndr.clear()
    cost_field_InvItmVndr.send_keys("10")

    print("✅ تم إدخال سعر المورد بنجاح (10)")


    # ✅ الضغط على زر الإضافة داخل تبويب موردين الوحدة الثانية
    click_when_ready("(//*[@id='Word'])[2]")

    # فتح قائمة البحث عن المورد الثاني
    click_when_ready(
        "(//span[contains(@class,'e-input-group-icon') and contains(@class,'e-ddl-icon') and contains(@class,'e-search-icon')])[13]"
    )

    # ✅ الآن اختر العنصر "200001 - المورد الاول"
    click_visible_list_option("200001 - المورد الاول")

    # ✅ فتح تابة وحدة قياس المورد
    InvItmVndr_units_dropdown_xpath = "(//span[contains(@class,'e-input-group-icon') and contains(@class,'e-ddl-icon') and contains(@class,'e-search-icon')])[14]"
    click_when_ready(InvItmVndr_units_dropdown_xpath)


    # ✅ الآن اختر العنصر "Box"
    click_visible_list_option("Box")
    print("✅ تم اختيار وحدة قياس المورد:جديد")


    # ✅دخال سعر المورد للوحدة جديد = 240
    step_pause()
    cost_field_InvItmVndr = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='grid-cellvndrItmPrice1']/input")))
    cost_field_InvItmVndr.clear()
    cost_field_InvItmVndr.send_keys("120")
    print("✅ تم إدخال سعر المورد بنجاح (120)")
    step_pause()

    # ✅فتح تبويب "الأسعار"
    click_when_ready("//*[@id='SalItmPrice']")
    step_pause()
    # ✅فتح قائمة البحث عن سعر البيع الاول (فهارس محدّثة — [17] كان يطابق عنصرًا مخفيًا/غير قابل للنقر)
    sal_price_dd = "(//span[contains(@class,'e-input-group-icon') and contains(@class,'e-ddl-icon') and contains(@class,'e-search-icon')])[19]"
    click_when_ready(sal_price_dd)

    # ✅ الآن اختر العنصر "Unit"
    click_visible_list_option("Unit")
    print("✅ تم اختيار وحدة قياس السعر: Unit ✅")
    step_pause()
    # ✅فتح تبويب مستوي السعر الاول
    click_when_ready(
        "(//span[contains(@class,'e-input-group-icon') and contains(@class,'e-ddl-icon') and contains(@class,'e-search-icon')])[20]"
    )

    # ✅ الآن اختر العنصر "مستوي السعر الاول"
    click_visible_list_option("1 - عام")
    print("✅ تم اختيار مستوي السعر الاول: 1 - عام ✅")


    # ✅ اكتب السعر للمستوي الاول = 20

    price_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='grid-cellitmPrice0']/input")))
    price_field.clear()
    price_field.send_keys("20")
    print("✅ تم إدخال السعر للمستوي الاول بنجاح (20)")

    # ✅ الضغط على زر الإضافة داخل تبويب السعر بوحدة الثانية
    click_when_ready("(//*[@id='Word'])[5]")

    # ✅فتح التابة الخاصة بوحدة السعر الثانية
    click_when_ready(
        "(//span[contains(@class,'e-input-group-icon') and contains(@class,'e-ddl-icon') and contains(@class,'e-search-icon')])[21]"
    )


    # ✅اختيار وحدة جديد في السعر الثاني
    click_visible_list_option("Box")
    print("✅ تم اختيار وحدة قياس السعر: جديد")

    # ✅اضغط علي تابة المستوي الثاني من التسعيره
    click_when_ready(
        "(//span[contains(@class,'e-input-group-icon') and contains(@class,'e-ddl-icon') and contains(@class,'e-search-icon')])[22]"
    )

    # ✅اختيار مستوي السعر الثاني
    click_visible_list_option("1 - عام")
    print("✅ تم اختيار مستوي السعر الثاني: 1 - عام ✅")

    # ✅ اكتب السعر للمستوي الثاني = 240

    price_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='grid-cellitmPrice1']/input")))
    price_field.clear()
    price_field.send_keys("240")
    print("✅ تم إدخال السعر للمستوي الثاني بنجاح (240)")

    # ✅ حفظ أو تنفيذ العملية النهائية
    click_when_ready("//ul[@id='quick-menu-body']/li[5]/button/i")

    # انتظار اختياري لرسالة نجاح أو أي إشعار ظاهر بعد الحفظ (لا يوقف السكربت إن لم يظهر)
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@class,'e-toast-success')]"))
        )
    except TimeoutException:
        pass

    try:
        sign_out_via_profile(driver, wait)
    except Exception as exc:
        print(f"[WARN] تعذر تسجيل الخروج بعد الحفظ: {exc}")

    driver.quit()
