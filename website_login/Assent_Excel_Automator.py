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

wb = None
# USE THIS CODE AS TEMPLATE FOR NEW CODE AUTO FILLING EXCEL SHEET WITH VALUES

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def column_letter_to_index(letter):
    """Convert a column letter to its numerical index."""
    index = 0
    for char in letter:
        index = index * 26 + (ord(char.upper()) - ord('A')) + 1
    return index

def create_driver():
    """Initialize the Edge WebDriver with options."""
    try:
        options = EdgeOptions()
        driver = webdriver.Edge(options=options)
        logging.info("Edge WebDriver initialized successfully.")
        return driver
    except WebDriverException as e:
        logging.error(f"Failed to initialize Edge WebDriver: {e}")
        raise

def login(driver, url, username, password):
    """Log into the specified URL using provided credentials."""
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

def search_part(driver, query):
        print('searching for part')
    # Open search modal
        search_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, 'nav_searchButton'))
        )
        search_button.click()

        # Clear and refill search input
        search_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, 'spotlightText'))
        )
        search_input.clear()
        search_input.send_keys(query)
def not_submitted(driver):
    text=WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, 'moduleStatus-text'))
        ).text
    if text=='Not Submitted':
        return True
    else:
        return False
#adress scenario with the pie chart of substances found vs not found for some part numbers
#find way to see if substances are detected or not
#maybe use part list in Assent that already has all parts with susbstances found
def sub_status(driver):
    sub=None
    #no subs found REACH
    NO= WebDriverWait(driver, 5).until(
             EC.presence_of_element_located((By.XPATH, '/html/body/div/aci-root/ng-component/div[3]/ng-component/div/div[1]/div[1]/aci-part-modules-panel/ux-tabset/span/div/div[1]/div/aci-part-dsl-panel-component/aci-part-module-status-component/div[2]/div[2]/div[1]/div/div/div[1]/div'))
         )

    #subs found REACH
    YES= WebDriverWait(driver, 5).until(
             EC.presence_of_element_located((By.XPATH, '/html/body/div/aci-root/ng-component/div[3]/ng-component/div/div[1]/div[1]/aci-part-modules-panel/ux-tabset/span/div/div/div/aci-part-dsl-panel-component/aci-part-module-status-component/div[2]/div[2]/div[1]/div/div/div[1]/div'))
         )
    #WebDriverWait(driver, 5).until(
        #     EC.presence_of_element_located((By.ID, 'moduleStatus-text'))
        # ).text
    if sub==NO:
        return True
    elif sub==YES:
        return False

def find_children(driver, query):
    try:
        print('Getting Search Results')
        time.sleep(2)
        search_result = driver.find_element(By.CSS_SELECTOR, 'aci-root > ng-component > div.container.main-content > aci-spotlight-search > div > div > div > div.spotlight-results > div > div:nth-child(3) > div')
        children = search_result.find_elements(By.CLASS_NAME, 'col-md-4')
        return children
    except:
        print('No Results Found')
        close_button=WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div/aci-root/ng-component/div[2]/aci-spotlight-search/div/div/div/div[2]/button')))
        close_button.click()
        logging.warning(f"No results found for query: {query}")
        return None
    
def click_REACH_tab(driver):
    REACH_button=WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div/aci-root/ng-component/div[3]/ng-component/div/div[1]/div[1]/aci-part-modules-panel/ux-tabset/span/ul/li[1]/a')))
    REACH_button.click()
    #driver.find_elements_by_xpath("//*[contains(text(), 'My Button')]")

def click_ROHS_tab(driver):
    ROHS_button=WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div/aci-root/ng-component/div[3]/ng-component/div/div[1]/div[1]/aci-part-modules-panel/ux-tabset/span/ul/li[2]/a')))
    ROHS_button.click()
    #driver.find_elements_by_xpath("//*[contains(text(), 'My Button')]")

def click_status_drop(driver):
    time.sleep(2)
    Status_drop_button=WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div/aci-root/ng-component/div[3]/ng-component/div/div[1]/div[1]/aci-part-modules-panel/ux-tabset/span/div/div[1]/div/aci-part-dsl-panel-component/aci-part-module-status-component/div[1]/div/button')))
    Status_drop_button.click()
    time.sleep(2)
    R240_version_button=WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, 'submoduleDropdown-scipDsl-item-click-96')))
    R240_version_button.click()
    
def search_and_generate_declaration(driver, query): 
    print('search&generate')
    """Perform search and attempt to generate a declaration."""
    children = None
    try:
        search_part(driver, query)
        # Wait for results to appear
        children=find_children(driver,query)

        if children is not None:
            try:
                # zero-indexes array of selenium object children
                for index in range(len(children)):
                    # Attempt to generate declaration
                    children=find_children(driver,query)
                    child=children[index]
                    print('Clicking on search result')
                    child.click()
                    click_REACH_tab(driver)
                    click_status_drop(driver)
                    #REACH tab
                    if not_submitted(driver):
                        click_ROHS_tab(driver)
                    else:
                        if sub_status(driver)==True:
                            sh = wb.sheets['Review']
                            sh.range['$B2'].value = 'R240N' # make the cell input dynamic
                            click_ROHS_tab(driver)
                        elif sub_status(driver)==False:
                            sh = wb.sheets['Review']
                            sh.range['$B2'].value = 'R240' # make the cell input dynamic
                            print('Generating Declaration')
                            gen_dec = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.ID, 'generateDeclaration-click'))
                            )
                            gen_dec.click()
                            time.sleep(2.5)
                            logging.info(f"Declaration generated for query: {query}")
                            click_ROHS_tab(driver)
                        else:
                            logging.info(f"REACH not submitted for {query}")
                            click_ROHS_tab(driver)

                    #ROHS tab
                    if not_submitted(driver):
                        continue
                    else:
                        if sub_status(driver)==True:
                            sh = wb.sheets['Review']
                            sh.range['$D2'].value = 'ROHS10' # make the cell input dynamic
                        elif sub_status(driver)==False:
                            sh = wb.sheets['Review']
                            sh.range['$D2'].value = 'ROHS10W' # make the cell input dynamic
                            print('Generating Declaration')
                            gen_dec = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.ID, 'generateDeclaration-click'))
                            )
                            gen_dec.click()
                            time.sleep(2.5)
                            logging.info(f"Declaration generated for query: {query}")
                        else:
                            logging.info(f"ROHS not submitted for {query}")
                            continue
                            

                    # check submission status
                    # IF status= 'No substances found' then fill appropriate excel cell with ROHS10
                    # ELSE status = 'Substances found' then download declaration and fill excel cell with ROHS10W
                        # IF status='No substances found' fill excel cell with R240N
                        # ELSE status= 'Substances found' download declaration and fill excel cell with R240

                    if index<(len(children)-1):
                        search_part(driver, query)
            except Exception as e:
                print(e)
                print('hello')
                logging.warning(f"Declaration not found for query: {query}")
                return "declaration_failed"
        else:
            logging.warning(f"Not enough results to click for query: {query}")
            return "Not enough results"
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return "unexpected_error"

def perform_searches(selected_range):
    """Perform searches based on the selected range from the Excel file."""
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

    driver = webdriver.Edge()
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

    wb = xw.Book(r'C:\Users\610161178\Downloads\current_pec_review.xlsm')
    if sheet_name:
        sheet = wb.sheets[sheet_name]
    else:
        sheet = wb.sheets.active

    for current_row in range(start_row, end_row):
        cell_value = sheet.range((current_row, col_index)).value
        if cell_value is not None:
            query = str(cell_value)
            search_and_generate_declaration(driver, query)

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