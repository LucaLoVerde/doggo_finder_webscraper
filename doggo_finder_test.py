"""Exercises to scrape and monitor a webpage in search of a rescue doggo.

Uses selenium with a browser instance to pull the available rescue doggos list
from my favorite local rescue service, whose website doesn't allow to receive
updates.

// TODO use colored text to highlight events
// TODO put timestamps on each event reported

"""

import time
import sys
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver as WebDriverClass
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from datetime import datetime as dt
try:
    from termcolor import cprint
except ImportError:
    print('\ntermcolor library not found, color output will not be available.\n')


def open_connection(target_url: str, instance_type: str) -> WebDriverClass:
    """Open connection with a selenium webdriver (Firefox for now) to a URL.

    Creates and returns a selenium webdriver object after initializing and
    getting the webpage passed as argument.
    // TODO support different browsers/webdrivers?

    Parameters
    ----------
    target_url : str
        URL of page to fetch
    instance_type : str
        Type of webdriver instance ('firefox' or 'chrome')

    Returns
    -------
    WebDriverClass
        webdriver instance on target URL

    Raises
    ------
    ValueError
        Raised if a wrong 'instance_type' argument is provided
    """
    if instance_type.lower() == 'firefox':
        capabilities_argument = DesiredCapabilities().FIREFOX
        capabilities_argument["marionette"] = True
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(),
            capabilities=capabilities_argument)
    elif instance_type.lower() == 'chrome':
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
    else:
        raise ValueError("'instance_type' can be either 'firefox' or 'chrome'")
    driver.minimize_window()
    time.sleep(1)
    driver.get(target_url)
    time.sleep(1)
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
    time.sleep(2)
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


def compare_dicts(old_dict: dict, new_dict: dict) -> tuple:
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
        added_dogs_dict = None
    else:
        for dog in new_dogs:
            added_dogs_dict[dog] = new_dict[dog]
    if len(adopted_dogs) == 0:
        adopted_dogs_dict = None
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
    driver.quit()
    time.sleep(1)


def print_refresh_report(changes: tuple, verbose: bool = False, mode: str = None):
    """Print a somewhat formatted report of adopted/added dogs.

    Parameters
    ----------
    changes : tuple
        tuple containing the two changes dicts, or None if no changes for each
        of the two categories (added dogs, adopted dogs)
    verbose : bool, optional
        [ NOT IMPLEMENTED ] print additional debug information, by default False
    mode : str, optional
        printed report mode, for now supports default print and colored print
        (mode = "red"), by default None
    """
    if verbose:
        pass
    if changes[0]:
        if mode == 'color':
            cprint('*' * 80, 'red')
            cprint(dt.strftime(dt.now(), '%Y-%m-%d %H:%M:%S'), 'red')
            cprint('{} new dogs added!!'.format(len(changes[0])), 'red')
            cprint('*' * 80, 'red')
        else:
            print('*' * 80)
            print(dt.strftime(dt.now(), '%Y-%m-%d %H:%M:%S'))
            print('{} new dogs added!!'.format(len(changes[0])))
            print('*' * 80)
        dict_pretty_print(changes[0])
        print()
    if changes[1]:
        if mode == 'color':
            cprint(dt.strftime(dt.now(), '%Y-%m-%d %H:%M:%S'), 'yellow')
            cprint('{} new dogs adopted!!'.format(len(changes[1])), 'yellow')
        else:
            print('{} new dogs adopted!!'.format(len(changes[1])))
        dict_pretty_print(changes[1])
        print()


def simple_loop(driver: WebDriverClass, interval: float, verbose: bool = False,
        print_mode: str = None):
    """Dog list monitoring loop.

    Parameters
    ----------
    driver : WebDriverClass
        selenium webdriver instance
    interval : float
        Time interval for checking for updates in the dog list
    verbose : bool, optional
        Print additional info, by default False
    print_mode : str, optional
        printing mode for changes in the dogs listing (currently can be: "color"
        for colored console output)
    """
    first_run = True
    try:
        while True:
            curr_dict = dog_list_to_dict(fetch_dogs_list(driver))
            if first_run:
                print('\n\n\nstarting loop...')
                if print_mode == 'color':
                    cprint('detected {} dogs available\n'.format(len(curr_dict)), 'green')
                else:
                    print('detected {} dogs available\n'.format(len(curr_dict)))
                dict_pretty_print(curr_dict)
                first_run = False
                old_dict = curr_dict
                continue
            curr_dict = dog_list_to_dict(fetch_dogs_list(driver))
            changes = compare_dicts(old_dict, curr_dict)
            if verbose:
                print('comparison says {}, continuing...'.format(changes))
            print_refresh_report(changes, mode=print_mode)
            old_dict = curr_dict
            time.sleep(interval)
    except KeyboardInterrupt:
        print('\nquitting...')
        return


if __name__ == "__main__":
    TARGET_URL = 'http://dpsrescue.org/adopt/available/'
    CHECK_INTERVAL = 120

    my_driver = open_connection(TARGET_URL, 'chrome')
    simple_loop(my_driver, CHECK_INTERVAL, False, print_mode='color')
    time.sleep(1)
    close_connection(my_driver)
    sys.exit(0)
