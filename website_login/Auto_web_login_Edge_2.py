import xlwings as xw
import yaml
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def column_letter_to_index(letter):
    """Convert a column letter to its numerical index."""
    index = 0
    for char in letter:
        index = index * 26 + (ord(char.upper()) - ord('A')) + 1
    return index

def create_driver():
    try:
        options = EdgeOptions()
        driver = webdriver.Edge(options=options)
        logging.info("Edge WebDriver initialized successfully.")
        return driver
    except WebDriverException as e:
        logging.error(f"Failed to initialize Edge WebDriver: {e}")
        raise

def login(driver, url, username, password):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'username'))).send_keys(username)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys(password)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-primary'))).click()
        logging.info("Logged in successfully.")
    except TimeoutException as e:
        logging.error(f"Timeout during login: {e}")
        raise
    except NoSuchElementException as e:
        logging.error(f"Login element not found: {e}")
        raise

def handle_search_result(result_items, pass_number):
    """Click on the appropriate result based on the pass number."""
    result_index = pass_number - 1  # Convert pass_number to zero-based index
    if len(result_items) > result_index:
        result_items[result_index].click()
        return True
    return False

def search_and_generate_declaration(driver, query, pass_number):
    """Perform search and attempt to generate a declaration."""
    try:
        search_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, 'nav_searchButton'))
        )
        search_button.click()

        search_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, 'spotlightText'))
        )
        search_input.clear()
        search_input.send_keys(query)

        result_items = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.spotlight-result-item'))
        )

        if handle_search_result(result_items, pass_number):
            try:
                gen_dec = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, 'generateDeclaration-click'))
                )
                gen_dec.click()
                time.sleep(2.5)
                logging.info(f"Declaration generated for query: {query}")
            except TimeoutException:
                logging.warning(f"Declaration not found for query: {query}")
        else:
            logging.warning(f"Not enough results to click for query: {query}")

    except TimeoutException:
        logging.warning(f"Search result not found for query: {query}")

def perform_searches(selected_range):
    if not selected_range:
        logging.error("Selected range is empty.")
        return

    # Load login details from YAML file
    try:
        with open(r'C:\Users\610161178\Downloads\Code\website_login\loginDetails.yml') as file:
            conf = yaml.load(file, Loader=yaml.SafeLoader)
        myAssentUsername = conf['assent_user']['email']
        myAssentPassword = conf['assent_user']['password']
    except FileNotFoundError as e:
        logging.error(f"Login details file not found: {e}")
        return

    driver = create_driver()
    target_url = "https://core-authentication-ui.assentcompliance.com/#/login"

    try:
        login(driver, target_url, myAssentUsername, myAssentPassword)
    except Exception as e:
        logging.error(f"Failed to login: {e}")
        driver.quit()
        return

    if "!" in selected_range:
        sheet_name, cell_range = selected_range.split("!")
    else:
        sheet_name = None
        cell_range = selected_range

    start, end = cell_range.split(":")
    start_row = int(''.join(filter(str.isdigit, start)))
    end_row = int(''.join(filter(str.isdigit, end)))
    start_col = ''.join(filter(str.isalpha, start))
    col_index = column_letter_to_index(start_col)

    wb = xw.Book(r'C:\Users\610161178\Downloads\current pec review.xlsm')
    if sheet_name:
        sheet = wb.sheets[sheet_name]
    else:
        sheet = wb.sheets.active

    for pass_number in range(1, 4):
        logging.info(f"Starting pass {pass_number}")
        current_row = start_row
        
        while current_row <= end_row:
            cell_value = sheet.range((current_row, col_index)).value
            if cell_value is not None:
                query = str(cell_value)
                search_and_generate_declaration(driver, query, pass_number)

            current_row += 1  # Move to the next query

        logging.info(f"Finished pass {pass_number}")

    driver.quit()

# Set the duration in seconds after which the program will quit
DURATION = 70  # seconds

# Read the selected range from the text file
selected_range_file = r'C:\Users\610161178\Downloads\Code\selected_range.txt'
with open(selected_range_file, "r") as file:
    selected_range = file.readline().strip()

# Perform searches using the selected range
perform_searches(selected_range)

# Pause the program for the specified duration before quitting
time.sleep(DURATION)
