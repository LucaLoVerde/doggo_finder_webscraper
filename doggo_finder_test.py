"""Exercises to scrape and monitor a webpage in search of a rescue doggo.

Uses selenium with a browser instance to pull the available rescue doggos list
from my favorite local rescue service, whose website doesn't allow to receive
updates.

"""

import time
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager

TARGET_URL = 'http://dpsrescue.org/adopt/available/'

# Invece che installare manualmente il webdriver, la componente che permette
# a selenium di usare un vero browser presente sul client, possiamo usare la
# magia offerta da webdriver_manager, che permette di installare il
# webdriver at runtime senza menate di cazzo.
driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
driver.minimize_window()
time.sleep(1)
# Andiamo alla pagina web target
driver.get(TARGET_URL)
time.sleep(1)
lista = driver.find_elements_by_xpath("//div[@class='dogs col-md-12']/span")
print("found {} dogs listed".format(len(lista)))
for cane in lista:
    print(cane.text)
    print()

driver.close()
