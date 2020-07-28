"""Exercises to scrape and monitor a webpage in search of a rescue doggo.

Uses selenium with a browser instance to pull the available rescue doggos list
from my favorite local rescue service, whose website doesn't allow to receive
updates.

"""

import time
import sys
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver as WebDriverClass


def open_connection(target_url: str) -> WebDriverClass:
    """Open connection with a selenium webdriver (Firefox for now) to a URL.

    Creates and returns a selenium webdriver object after initializing and
    getting the webpage passed as argument.
    // TODO support different browsers/webdrivers?

    Parameters
    ----------
    target_url : str
        Webpage to fetch

    Returns
    -------
    WebDriverClass
        webdriver object initialized, window is minimized
    """
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    driver.minimize_window()
    time.sleep(1)
    driver.get(target_url)
    return driver


def fetch_dogs_list(driver: WebDriverClass) -> list:
    """Fetch list of available rescue dogs.

    Refreshes the webdriver instance and parses the pages for available rescue
    dogs. For now, it's implemented by first matching a <div> of class
    "dogs col-md-12" (hope it doesn't change) and then matching all the children
    span elements.

    Parameters
    ----------
    driver : WebDriverClass
        selenium webdriver instance (already initialized)

    Returns
    -------
    list
        List of elements matching the spans containing dogs
    """
    driver.refresh()
    time.sleep(1)
    dog_list = driver.find_elements_by_xpath("//div[@class='dogs col-md-12']/span")
    dog_list = [dog.text for dog in dog_list]
    return dog_list


def dog_list_to_dict(in_list: list) -> dict:
    """Convert dog list to dictionary.

    For now, we split each element with newline as separator, then we use each
    first element (dog's name) as a key in the returned dictionary, where the
    rest of the elements (a string containing the breed and another containing
    the age and gender of the dog).
    // TODO maybe create a class for containing the dogs' information?

    Parameters
    ----------
    in_list : list
        Dog list as extracted from the rescue web page

    Returns
    -------
    dict
        Dictionary where keys are each dog's names and values are lists with the
        breed and age/gender of the dogs
    """
    dog_dict = {}
    for dog in in_list:
        tmp_sublist = dog.split('\n')
        dog_dict[tmp_sublist[0]] = tmp_sublist[1:]
    return dog_dict


def dict_pretty_print(in_dict: dict):
    """Print a report of dogs in dictionary.

    Parameters
    ----------
    in_dict : dict
        Input dogs dictionary
    """
    for dog_name, attrs in in_dict.items():
        print("{}: {}, {}".format(dog_name, attrs[0], attrs[1]))


def print_dicts_comparison(old_dict: dict, new_dict: dict) -> tuple:
    """[summary].

    // TODO docs

    Parameters
    ----------
    old_dict : dict
        [description]
    new_dict : dict
        [description]

    Returns
    -------
    tuple
        [description]
    """
    old_keys = set(old_dict.keys())
    new_keys = set(new_dict.keys())
    new_dogs = new_keys.difference(old_keys)
    adopted_dogs = old_keys.difference(new_keys)
    added_dogs_dict = {}
    adopted_dogs_dict = {}
    if len(new_dogs) == 0:
        print('no dogs added.')
    else:
        for dog in new_dogs:
            added_dogs_dict[dog] = new_dict[dog]
    if len(adopted_dogs) == 0:
        print("no dogs adopted.")
    else:
        for dog in adopted_dogs:
            adopted_dogs_dict[dog] = old_dict[dog]
    return (added_dogs_dict, adopted_dogs_dict)


def close_connection(driver: WebDriverClass):
    """Close webdriver instance.

    Parameters
    ----------
    driver : WebDriverClass
        selenium webdriver instance to close
    """
    driver.close()
    time.sleep(1)


if __name__ == "__main__":
    TARGET_URL = 'http://dpsrescue.org/adopt/available/'

    my_driver = open_connection(TARGET_URL)
    lista = fetch_dogs_list(my_driver)
    diz = dog_list_to_dict(lista)
    dict_pretty_print(diz)
    close_connection(my_driver)
    sys.exit(0)
