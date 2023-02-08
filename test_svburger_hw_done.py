import random
import time
import pytest
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By


################# UTILS #######################################

def random_email():
    """
    create random email for register
    :return: new email
    """
    dots = (".com", ".co.il", ".net")
    hosts = ("gmail", "walla", "sample")
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    name_len = random.randint(3, 7)
    name = ""
    for i in range(name_len):
        index = random.randint(0, len(alphabet) - 1)
        name += alphabet[index]
    host = hosts[name_len % len(dots)]
    dot = dots[name_len % len(hosts)]
    email = "%s@%s%s" % (name, host, dot)
    return email


################# DATA #######################################

coupons = ['150', '160', '170']

new_user = {
    "email": random_email(),
    "password": "!Edi2222",
    "firstname": "royier",
    "lastname": "coheniy"
}

valid_login_user = {
    "email": "shilatmaymon1234@gmail.com",
    "password": "Shilat123"
}

wrong_user = {
    "firstname": "sss",
    "lastname": "sss",
    "email": "shilatmaymon1234@gmail.com",
    "password": "Shilat123",
    "repassword": "Shilat123"

}  # sign up with dup account

wrong_user2 = {
    "firstname": "ssssss",
    "lastname": "sssssss",
    "email": "shilatmaymon1234@gmail.com",
    "password": "Shilat123",
    "repassword": "111111"

}  # reg with no match passwords.

wrong_user3 = {
    "firstname": "im",
    "lastname": "dandil",
    "email": random_email(),
    "password": "123456",
    "repassword": "123456"

}  # reg with no first name len < 6 (as 2 chars).

wrong_user4 = {
    "firstname": "ggggg",
    "lastname": "imasdsadsadasasds",
    "email": random_email(),
    "password": "123456",
    "repassword": "123456"

}  # reg with long last name len > 10 (as 17 chars).
wrong_user5 = {
    "firstname": "imasd",
    "lastname": "dandil",
    "email": random_email(),
    "password": "1234561111111111111111",
    "repassword": "1234561111111111111111"

}  # reg with long password len > 14 (as 22 chars).

wrong_user6 = {
    "firstname": "imasd",
    "lastname": "dandil",
    "email": random_email(),
    "password": "!",
    "repassword": "!"

}  # reg with no numbers and letters in password only special char .


################# FUNCTIONS #######################################

def get_text_from_alert(driver):
    alert = driver.switch_to.alert
    text = alert.text
    alert.accept()
    return text


def click_sign_in(driver):
    driver.find_element(By.CSS_SELECTOR, '[href="#/SignIn"] button').click()


def register(fname, lname, email, password, repassword, driver):
    """
    perform register operation

    """
    driver.find_element(By.CSS_SELECTOR, 'a[href="#/SignUp"] button').click()
    driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Type your first name"]').send_keys(fname)
    driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Type your last name"]').send_keys(lname)
    driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Enter your email"]').send_keys(email)
    driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Create Password"]').send_keys(password)
    driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Confirm Password"]').send_keys(repassword)
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()


def send_order(driver):
    driver.find_element(By.XPATH,
                        "//*[@id=\"root\"]/div[2]/div[1]/div/div/div[2]/div/div/div/div[2]/div[4]/div[1]/button")\
        .click()
    txt = driver.find_element(By.CSS_SELECTOR,
                              "#root > div.container > div:nth-child(1) > div > div > div.popup > div > div > div > "
                              "div:nth-child(2) > h3:nth-child(1)")
    return txt.text


def select_products(products_to_choose: tuple, driver: webdriver):
    """
    perform select products
    :param products_to_choose: products names to select in order
    :param driver:
    :return: list of prices in order
    """
    time.sleep(1)
    products = driver.find_elements(By.CLASS_NAME, "middle")
    selected = []
    color = []
    driver.execute_script(f"document.body.style.transform='scale(0.7)';")
    driver.execute_script(f"window.scroll(10,300);")
    for product in products:
        if not product:
            continue
        p_name = product.find_element(By.CLASS_NAME, "card-title")
        if p_name.text in products_to_choose:
            price = product.find_element(By.CLASS_NAME,
                                         "text-muted").text.replace("price: ", "")
            selected.append(int(price))
            time.sleep(1)
            product.click()
            if "background-color: white" in product.find_element(By.CLASS_NAME, "card").get_attribute("style"):
                color.append("white")
            else:
                color.append("lightblue")
    driver.find_element(By.XPATH, "//*[@id=\"root\"]/div[2]/div[1]/div/div/button[2]").click()

    time.sleep(1)
    return selected, color


def reserve_order(amounts, coupon, table, driver):
    """
    perform order and returns the details
    :param driver:
    :param amounts: amount of each product in order
    make sure the order is same as order in select_products
    :param coupon: coupon value
    :param table: table number
    :return: dict of the details for the order
    """
    order_details = {"products": [], "p_amounts": [], "coupon": coupon, "table": table, "prices": []}
    container = driver.find_element(By.CLASS_NAME, "popup_inner")
    products = container.find_elements(By.CLASS_NAME, "row")[2:len(amounts) + 4:]
    for i, p in enumerate(products):
        add_amount = p.find_element(By.TAG_NAME, "input")
        if i < len(amounts):
            value = amounts[i]
            add_amount.clear()
            add_amount.send_keys(value)
            order_details['products'].append(p.find_element(By.TAG_NAME, "label").text)
            order_details["p_amounts"].append(amounts[i])
            order_details["prices"].append(int(p.text.split("\n")[1]))
        else:
            order_details["subtotal_price"] = int(p.find_element(By.TAG_NAME,
                                                                 "label").text.replace("Subtotal: ", "")[:-1:])
            field = p.find_elements(By.TAG_NAME, "input")
            field[0].clear()
            field[0].send_keys(coupon)
            field[1].clear()
            field[1].send_keys(table)
            break
    return order_details


def login(email: str, password: str, driver):
    """
    perform login operation

    """
    click_sign_in(driver)
    driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Enter your email"]').send_keys(email)
    driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Enter your password"').send_keys(password)
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()


################# FIXTURES #####################################


@pytest.fixture
def setup():
    driver = webdriver.Chrome()
    driver.get("https://svburger1.co.il/#/HomePage")
    driver.implicitly_wait(5)
    driver.maximize_window()
    yield driver
    driver.close()


################# TESTS #######################################

def test_sanity(setup):
    """
    sanity is login -> select product -> reserve -> send
    :return:
    """
    driver = setup
    login(valid_login_user["email"], valid_login_user["password"], driver)
    select_products(("Burger",), driver)
    reserve_order(("1",), coupon="", table="1", driver=driver)
    assert send_order(driver) == "Your order has been successfully received"


################# LOGIN SECTION ###############################


def test_forget_password_functional(setup):
    """
    verify forget password button are functional
    :param setup:
    :return:
    """
    driver = setup
    click_sign_in(driver)
    driver.find_element(By.ID, "forgotId").click()
    driver.find_element(By.ID, "inputForgotPassword").send_keys(valid_login_user['email'])
    time.sleep(1)
    btn = driver.find_element(By.XPATH, "//*[@id=\"email\"]/button")
    btn.click()
    time.sleep(2)
    assert "Check your inbox for further instructions" == get_text_from_alert(driver)


def test_login_page_show_up(setup):
    """
    verify elements of the page are displayed
    :param setup:
    :return:
    """
    driver = setup
    click_sign_in(driver)
    assert driver.find_element(By.CLASS_NAME, "card1").is_displayed()


def test_password_field(setup):
    """verify password field is asterix"""
    driver = setup
    click_sign_in(driver)
    password = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Enter your password"')
    assert password.get_attribute("type") == "password"


def test_login(setup):
    """
    test case login sanity with valid information
    expected to move to next page
    :param setup: driver
    """
    driver = setup
    login(valid_login_user["email"], valid_login_user["password"], driver)
    assert driver.find_element(By.CLASS_NAME, 'card3').is_displayed()


@pytest.mark.parametrize("email,password", [("shilatmaymon1234@gmail.com", ""), ("", "Shilat123"), ("", "")])
def test_login_invalid(setup, email, password):
    """
    test case login with email that not exists
    first with no password
    second with no email
    third without both
    :param setup:
    :return:
    """
    driver = setup
    login(email, password, driver)
    time.sleep(2)

    assert get_text_from_alert(driver) == "Failed to log in"


################# REGISTER SECTION ###############################

def test_signup(setup):
    """
    test case register with valid information
    :param setup: driver to driver
    :return:
    """
    driver = setup
    register(new_user["firstname"], new_user['lastname'],
             new_user['email'], new_user['password'], new_user['password'], driver)
    assert driver.find_element(By.CLASS_NAME, 'card3').is_displayed()


def test_sign_up_with_only_required_fields(setup):
    """try to sign up with only required fields"""
    driver = setup
    user = new_user
    user["firstname"] = ""
    user["lastname"] = ""
    register(user["firstname"], user["lastname"],
             user['email'], user['password'], user['password'], driver)
    flag = True
    try:
        assert driver.find_element(By.CLASS_NAME, 'card3').is_displayed()
    except selenium.common.exceptions.UnexpectedAlertPresentException:

        flag = False
    if not flag:
        raise AssertionError(f"got unexpected alert  ,"
                             f" expected to register success with only required fields\n{user}")


@pytest.mark.parametrize('user,expected',
                         [(wrong_user, "The email address is already in use by another account."),
                          (wrong_user2, "password and confirm error"),
                          (wrong_user3, "First name must be between 6 and 10 characters"),
                          (wrong_user4, "Last name must be between 6 and 10 characters"),
                          (wrong_user5, "Password should be at maxinum 10 characters"),
                          (wrong_user6, "Password should be at least 6 characters")])
def test_sign_up_invalid(setup, user, expected):
    """
    test cases sign up with used email and sign up with passwords that
    not match
    :param setup: driver
    :param user: information to send
    :param expected: message expect from the page
    :return:
    """
    driver = setup
    register(*user.values(), driver)
    time.sleep(1)
    flag = True
    try:

        assert expected in get_text_from_alert(driver)
    except selenium.common.exceptions.NoAlertPresentException:
        flag = False
    if not flag:
        raise AssertionError(f"alert not pop up with expected: {expected}\n with this user details:\t{user}")


################# ORDER SECTION ###############################

def test_selected_products_apears_in_reserve(setup):
    """test case selected products apears in reserve window
        and the prices equal to the prices in reserve window"""
    driver = setup
    login(valid_login_user["email"], valid_login_user["password"], driver)
    prices = select_products(("Kids Meal", "Burger"), driver)[0]
    details = reserve_order(("1", "1"), coupon="111", table="10", driver=driver)
    time.sleep(1)
    assert details["products"] == ["Kids Meal", "Burger"]
    assert details["prices"] == prices


def test_products_total_price(setup):
    """test case total prices of selected products and amounts are
        equal to subtotal price"""
    driver = setup
    login(valid_login_user["email"], valid_login_user["password"], driver)
    time.sleep(0.5)
    select_products(("Kids Meal", "Burger"), driver)
    time.sleep(0.5)
    details = reserve_order(("2", "2"), coupon="", table="4", driver=driver)
    assert sum(details["prices"]) == details["subtotal_price"]


def test_invalid_low_quantity_on_order(setup):
    """verify that cant send order with quantity of products that lower then 1"""
    driver = setup
    login(valid_login_user["email"], valid_login_user["password"], driver)
    select_products(("Vegan",), driver)
    details = reserve_order(("-150",), coupon=coupons[0], table="1", driver=driver)
    send_order(driver)
    flag = True
    try:
        assert "Invalid value in quantity" in get_text_from_alert(driver)
    except selenium.common.exceptions.NoAlertPresentException:
        flag = False
    if not flag:
        raise AssertionError(f"alert not pop up with expected: 'Invalid value in quantity' \ndetails={details}")


def test_invalid_high_quantity_on_order(setup):
    """verify that cant send order with quantity of products that greater 2"""
    driver = setup
    login(valid_login_user["email"], valid_login_user["password"], driver)
    select_products(("Burger",), driver)
    details = reserve_order(("5",), coupon="", table="1", driver=driver)
    send_order(driver)
    flag = True
    try:
        assert "Invalid value in quantity" in get_text_from_alert(driver)
    except selenium.common.exceptions.NoAlertPresentException:
        flag = False
    if not flag:
        raise AssertionError(f"alert not pop up with expected: 'Invalid value in quantity' \ndetails={details}")


def test_select_product_color_change(setup):
    """
    verify that bg color change to lightblue after clicked
    :param setup:
    :return:
    """
    driver = setup
    login(valid_login_user["email"], valid_login_user["password"], driver)
    colors = select_products(("Kids Meal",), driver)[1]
    assert colors[0] == "lightblue"


def test_select_5_products_color(setup):
    """verify cant highlight more than 4 products
        and the color of the fifth are stay white"""
    driver = setup
    login(valid_login_user["email"], valid_login_user["password"], driver)
    colors = select_products(("Kids Meal", "Burger", "Vegan", "Combo Meal", "Sides"), driver)[1]

    assert colors[4] == "white"
