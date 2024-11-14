import xlwings as xw
import yaml
import time
import keyboard
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

def column_letter_to_index(letter):
    """Convert a column letter to its numerical index."""
    index = 0
    for char in letter:
        index = index * 26 + (ord(char.upper()) - ord('A')) + 1
    return index

def create_driver():
    options = ChromeOptions()
    return webdriver.Chrome(options=options)

def login(driver, url, username, password):
    driver.get(url)
    # Wait until the username input field is present
    userin = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'username')))
    userin.send_keys(username)
        
    # Wait until the password input field is present
    passin = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'password')))
    passin.send_keys(password)
        
    # Wait until the login button is clickable
    logon = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-primary')))
    logon.click()

def search(driver, query, current_row, current_col, start_col, end_row, end_col, sheet):
    first_result = None
    try:
        # Click on the search button
        search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'nav_searchButton')))
        search_button.click()
            
        # Input the search query
        search_input = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, 'spotlightText')))
        search_input.clear()  # Clear the previous query
        search_input.send_keys(query)
            
        # Press Enter to perform the search
        search_input.send_keys(Keys.ENTER)
    
        # Wait for the presence of the search results
        first_result = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.spotlight-result-item')))
        first_result.click()

        # Wait for the generate declaration button and click it
        gen_dec = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'generateDeclaration-click')))
        gen_dec.click()
        
        # Wait for 4 seconds after clicking the generate declaration button
        time.sleep(4)

    except TimeoutException:
        print(f"TimeoutException: Unable to find search result for query: {query}")
        try:
            # Clear the search input field if no search result found
            search_input = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.ID, 'spotlightText')))
            search_input.clear()

            # Move to the next cell in Excel sheet
            if current_col < column_letter_to_index(end_col):
                current_col += 1
            elif current_row < end_row:
                current_row += 1
                current_col = column_letter_to_index(start_col)
            
            # Retrieve the value from the next cell
            next_query = sheet.range((current_row, current_col)).value
            
            # Fill the search input field with the next query value
            if next_query is not None:
                search_input.send_keys(str(next_query))

                first_result = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.spotlight-result-item')))
                first_result.click()

                gen_dec = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'generateDeclaration-click')))
                gen_dec.click()

                # Wait for 4 seconds after clicking the generate declaration button
                time.sleep(4)

        except Exception as clear_exception:
            print(f"An error occurred while clearing the search input: {clear_exception}")
        return False
    except Exception as e:
        print(f"An error occurred during the search: {e}")
        return False

def perform_searches(selected_range):
    if not selected_range:
        return

    # Load login details from YAML file
    with open(r'C:\Users\610161178\Downloads\Code\website_login\loginDetails.yml') as file:
        conf = yaml.load(file, Loader=yaml.SafeLoader)
    myAssentUsername = conf['assent_user']['email']
    myAssentPassword = conf['assent_user']['password']

    # Create Chrome WebDriver with options
    driver = create_driver()

    target_url = "https://core-authentication-ui.assentcompliance.com/#/login"

    # Log in once
    login(driver, target_url, myAssentUsername, myAssentPassword)

    if "!" in selected_range:
        sheet_name, cell_range = selected_range.split("!")
    else:
        sheet_name = None
        cell_range = selected_range

    # Split the selected range string into row and column indexes
    start, end = cell_range.split(":")
    start_row = int(''.join(filter(str.isdigit, start)))
    start_col = ''.join(filter(str.isalpha, start))
    end_row = int(''.join(filter(str.isdigit, end)))
    end_col = ''.join(filter(str.isalpha, end))

    current_row = start_row
    current_col = column_letter_to_index(start_col)

    # Open the Excel workbook
    wb = xw.Book(r'C:\Users\610161178\Downloads\current pec review.xlsm')  # Update with your Excel file path
    if sheet_name:
        sheet = wb.sheets[sheet_name]
    else:
        sheet = wb.sheets.active

    # Perform searches for each cell in the selected range
    while current_row <= end_row:
        while current_col <= column_letter_to_index(end_col):
            cell_value = sheet.range((current_row, current_col)).value
            if cell_value is not None:
                if not search(driver, str(cell_value), current_row, current_col, start_col, end_row, end_col, sheet):
                    # Move to the next cell if the search fails
                    current_col += 1
                    continue

            # Move to the next column or row if the search is successful or the cell value is None
            current_col += 1
        current_row += 1
        current_col = column_letter_to_index(start_col)

    while True:
        if keyboard.is_pressed('esc'):
            break

# Read the selected range from the text file
selected_range_file = r'C:\Users\610161178\Downloads\Code\selected_range.txt'
with open(selected_range_file, "r") as file:
    selected_range = file.readline().strip()

# Perform searches using the selected range
perform_searches(selected_range)
