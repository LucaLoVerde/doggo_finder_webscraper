"""Exercises to scrape and monitor a webpage in search of a rescue doggo.

Uses selenium with a browser instance to pull the available rescue doggos list
from my favorite local rescue service, whose website doesn't allow to receive
updates.


"""

import time
import sys
from datetime import datetime as dt
import pandas as pd
from diskcache import Cache
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver as WebDriverClass
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
try:
    from termcolor import cprint
except ImportError:
    print('\ntermcolor library not found, color output will not be available.\n')


def open_connection(target_url: str, instance_type: str) -> WebDriverClass:
    """Open connection with a selenium webdriver (Firefox for now) to a URL.

    Creates and returns a selenium webdriver object after initializing and
    getting the webpage passed as argument.

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


def dict_pretty_print(in_dict: dict, colored_gender: bool = False):
    """Print a report of dogs in dictionary.

    Parameters
    ----------
    in_dict : dict
        Input dogs dictionary
    colored_gender : bool
        Print lines in blue for good boys and pink for good girls (REQUIRES the
        termcolor module installed)
    """
    for dog_name, attrs in in_dict.items():
        if colored_gender:
            gender: str = attrs[1]
            if 'Female' in gender:
                cprint("{}: {}, {}".format(dog_name, attrs[0], attrs[1]), 'magenta')
            elif 'Male' in gender:
                cprint("{}: {}, {}".format(dog_name, attrs[0], attrs[1]), 'blue')
        else:
            print("{}: {}, {}".format(dog_name, attrs[0], attrs[1]))


def compare_dicts(old_dict: dict, new_dict: dict) -> tuple:
    """Compare dogs dicts for additions/adoptions.

    Compares two dogs dictionaries to find new additions and adoptions, then
    it returns a tuple containing two elements, the first element representing
    additions and the second representing adoptions. These elements will be None
    if there are no additions/adoptions, or dictionaries containing the dogs that
    were added/adopted, respectively.

    Parameters
    ----------
    old_dict : dict
        Original dictionary to compare to new one
    new_dict : dict
        New dictionary to compare to original

    Returns
    -------
    tuple
        Tuple of length 2 containing changes for each category (either None or a
        changes dictionary for each element)
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


def print_refresh_report(changes: tuple, verbose: bool = False, mode: str = None) -> bool:
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
        (mode = "color", REQUIRES the termcolor module installed), by default None
    Returns
    -------
    bool
        True if dogs were added or adopted
    """
    if verbose:
        pass
    if changes[0]:
        print()
        if mode == 'color':
            cprint('*' * 80, 'red')
            cprint(dt.strftime(dt.now(), '%Y-%m-%d %H:%M:%S'), 'red')
            cprint('{} new dog(s) added!!'.format(len(changes[0])), 'red')
            dict_pretty_print(changes[0], colored_gender=True)
        else:
            print('*' * 80)
            print(dt.strftime(dt.now(), '%Y-%m-%d %H:%M:%S'))
            print('{} new dog(s) added!!'.format(len(changes[0])))
            dict_pretty_print(changes[0])
    if changes[1]:
        print()
        if mode == 'color':
            cprint(dt.strftime(dt.now(), '%Y-%m-%d %H:%M:%S'), 'yellow')
            cprint('{} new dog(s) adopted!!'.format(len(changes[1])), 'yellow')
            dict_pretty_print(changes[1], colored_gender=True)
        else:
            print('{} new dog(s) adopted!!'.format(len(changes[1])))
            dict_pretty_print(changes[1])
    return any(changes)


def simple_loop(driver: WebDriverClass, interval: float, cache: Cache, verbose: bool = False,
        color_print: str = None):
    """Dog list monitoring loop.

    Heavy lifting of the update checking loop. On first run, it checks the cache,
    then fetches and reports the current listing (and any changes compared to the
    cached data), then waits for the specified interval and then print any new
    changes detected.

    Parameters
    ----------
    driver : WebDriverClass
        selenium webdriver instance
    interval : float
        Time interval for checking for updates in the dog list
    cache : Cache
        diskcache Cache object containing last session's dogs listing
    verbose : bool, optional
        Print additional info, by default False
    color_print : str, optional
        printing mode for changes in the dogs listing (currently can be: "color"
        for colored console output, REQUIRES the termcolor module installed)
    """
    first_run = True
    try:
        while True:
            curr_dict = dog_list_to_dict(fetch_dogs_list(driver))
            if first_run:
                print('\n\n\nstarting loop...')
                if 'data' in cache:
                    cached_dict = cache['data']
                    cached_time = cache['time']
                    if color_print == 'color':
                        cprint('found cache from {} with {} available dogs'.format(
                            cached_time, len(cached_dict)), 'green')
                        dict_pretty_print(cached_dict, colored_gender=True)
                        curr_dict = dog_list_to_dict(fetch_dogs_list(driver))
                        changes = compare_dicts(cached_dict, curr_dict)
                        print_refresh_report(changes, mode=color_print)
                    else:
                        print('found cache from {} with {} available dogs'.format(
                            cached_time, len(cached_dict)))
                        dict_pretty_print(cached_dict, colored_gender=False)
                        curr_dict = dog_list_to_dict(fetch_dogs_list(driver))
                        changes = compare_dicts(cached_dict, curr_dict)
                        print_refresh_report(changes)
                else:
                    if color_print == 'color':
                        cprint('monitoring loop started: {}'.format(dt.strftime(dt.now(),
                            '%Y-%m-%d %H:%M:%S')), 'green')
                        cprint('detected {} dogs available\n'.format(len(curr_dict)), 'green')
                        dict_pretty_print(curr_dict, colored_gender=True)
                    else:
                        print('monitoring loop started: {}'.format(dt.strftime(dt.now(),
                            '%Y-%m-%d %H:%M:%S')))
                        print('detected {} dogs available\n'.format(len(curr_dict)))
                        dict_pretty_print(curr_dict)
                first_run = False
                old_dict = curr_dict
                continue
            curr_dict = dog_list_to_dict(fetch_dogs_list(driver))
            changes = compare_dicts(old_dict, curr_dict)
            if verbose:
                print('comparison says {}, continuing...'.format(changes))
            changed = print_refresh_report(changes, mode=color_print)
            if changed:
                if color_print == 'color':
                    cprint('Available dogs: {}'.format(len(curr_dict)), 'green')
                else:
                    print('Available dogs: {}'.format(len(curr_dict)))
            old_dict = curr_dict
            time.sleep(interval)
    except KeyboardInterrupt:
        print('\nsaving cache...')
        save_to_cache(cache, curr_dict)
        print('quitting...')
        return


def load_cache(path: str, verbose: bool = False) -> Cache:
    """Load cached data from disk, or create new cache.

    Loads an existing cache from disk from the specified path. Initializes a new
    cache at that path if none exists.

    Parameters
    ----------
    path : str
        Path to the cache folder
    verbose : bool, optional
        Print additional debug info, by default False

    Returns
    -------
    Cache
        Cache object ready for use.
    """
    cache = Cache(directory=path)
    if verbose:
        if 'data' in cache:
            print('found cached data from {}'.format(cache['time']))
            print('{} dogs in cache'.format(len(cache['data'])))
        else:
            print('no cached data found.')
    return cache


def save_to_cache(cache: Cache, data: dict):
    """Save dogs listing in persistent cache.

    Saves a diskcache Cache instance on disk. The available dogs dictionary is
    saved ('data' key) together with a timestamp ('time' key).

    Parameters
    ----------
    cache : Cache
        Cache object containing the dogs listing info.
    data : dict
        Dogs listing dictionary to cache for future use.
    """
    cache['data'] = data
    cache['time'] = dt.strftime(dt.now(), '%Y-%m-%d %H:%M:%S')
    cache.close()


if __name__ == "__main__":
    TARGET_URL = 'http://dpsrescue.org/adopt/available/'
    CHECK_INTERVAL = 120  # check every 120 s
    CACHE_PATH = 'cache'  # for now, 'cache' subfolder in current dif

    my_driver = open_connection(TARGET_URL, 'chrome')
    my_cache = load_cache(path=CACHE_PATH, verbose=False)
    simple_loop(driver=my_driver, interval=CHECK_INTERVAL, cache=my_cache,
        verbose=False, color_print='color')
    time.sleep(1)
    close_connection(my_driver)
    sys.exit(0)
