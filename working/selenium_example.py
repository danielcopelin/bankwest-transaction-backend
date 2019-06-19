import os
from time import sleep

import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

from dotenv import load_dotenv
load_dotenv()

def download_wait(directory, timeout, nfiles=None):
    """
    Wait for downloads to finish with a specified timeout.

    Args
    ----
    directory : str
        The path to the folder where the files will be downloaded.
    timeout : int
        How many seconds to wait until timing out.
    nfiles : int, defaults to None
        If provided, also wait for the expected number of files.

    """
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        sleep(1)
        dl_wait = False
        files = os.listdir(directory)
        if nfiles and len(files) != nfiles:
            dl_wait = True

        for fname in directory:
            if fname.endswith('.crdownload'):
                dl_wait = True

        seconds += 1
    return seconds

def download_transaction_history():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = "downloads"
    download_path = os.path.join(base_dir, download_dir)

    for f in os.listdir(download_path):
        os.remove(os.path.join(download_path, f))

    options = Options()
    options.add_experimental_option("prefs", {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
    })

    user = os.getenv("PAN")
    pwd = os.getenv("SECURE_CODE")
    driver = webdriver.Chrome(options=options)
    driver.get("https://ibs.bankwest.com.au/BWLogin/bib.aspx")

    elem = driver.find_element_by_id("AuthUC_txtUserID")

    elem.send_keys(user)
    elem = driver.find_element_by_id("AuthUC_txtData")
    elem.send_keys(pwd)

    elem = driver.find_element_by_id("AuthUC_btnLogin")
    elem.click()

    elem = driver.find_element_by_link_text("Transaction search")
    elem.click()

    s1 = Select(driver.find_element_by_id('_ctl0_ContentMain_ddlRangeOptions'))
    s1.select_by_visible_text('Last 7 Days')

    driver.execute_script('javascript:WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions("_ctl0:ContentButtonsLeft:btnExport", "", true, "", "", false, true))')
    download_wait(download_path, 20, nfiles=1)
    driver.close()

    downloaded_file = os.path.join(download_path, os.listdir(download_path)[0])
    df = pd.read_csv(downloaded_file)

    return df

if __name__ == "__main__":
    df = download_transaction_history()
    print(df)