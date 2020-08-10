"""Exercises to scrape and monitor a webpage in search of a rescue doggo.

Uses selenium with a browser instance to pull the available rescue doggos list
from my favorite local rescue service, whose website doesn't allow to receive
updates.


"""

import time
import sys
from datetime import datetime as dt
from typing import Tuple, Optional
import pandas as pd
from diskcache import Cache
from tabulate import tabulate
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver as WebDriverClass
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from termcolor import cprint, colored


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


def dog_list_to_df(in_list: list) -> pd.DataFrame:
    """Convert available dog list to pandas DataFrame.

    // TODO docs

    Parameters
    ----------
    in_list : list
        [description]

    Returns
    -------
    pd.DataFrame
        [description]

    Raises
    ------
    TypeError
        [description]
    AssertionError
        [description]
    """
    names = []
    breeds = []
    ages = []
    sexes = []
    for dog in in_list:
        tmp_sublist = dog.split('\n')
        names.append(tmp_sublist[0])
        breeds.append(tmp_sublist[1])
        tmp2_sublist = tmp_sublist[2].split('-')
        assert len(tmp2_sublist) <= 3, "Format for dog age/sex changed?"
        if len(tmp2_sublist) == 2:
            ages.append(tmp2_sublist[0].strip())
            tmp_sex = tmp2_sublist[1].strip()
        elif len(tmp2_sublist) == 3:
            tmp_age = [el.strip() for el in tmp2_sublist[:2]]
            ages.append('-'.join(tmp_age))
            tmp_sex = tmp2_sublist[-1]
        if 'Female' in tmp_sex:
            sexes.append('F')
        elif 'Male' in tmp_sex:
            sexes.append('M')
        else:
            raise TypeError("Cannot parse {}'s sex".format(names[-1]))
    dog_df = pd.DataFrame({'name': names, 'breed': breeds, 'age': ages,
        'sex': sexes})
    dog_df['sex'] = dog_df['sex'].astype('category')
    dog_df = dog_df.set_index('name')
    return dog_df


def df_pretty_print(in_df: pd.DataFrame, colored_sex: bool = False,
        header: bool = False):
    """Print dogs listing DataFrames.

    Parameters
    ----------
    in_df : pd.DataFrame
        [description]
    colored_sex : bool, optional
        [description], by default False
    header : bool, optional
        [description], by default False
    """
    if header:
        cols = ['idx'] + list(in_df.columns)
    else:
        cols = []
    tabulated = tabulate(in_df, headers=cols)
    if colored_sex:
        tabulated = tabulated.replace(
            ' M\n', ' ' + colored('M', 'blue') + '\n').replace(
            ' F\n', ' ' + colored('F', 'magenta') + '\n')
        if tabulated[-1] == 'F':
            colors_str = colored('-', 'magenta').split('-')
        else:
            colors_str = colored('-', 'blue').split('-')
        if tabulated[-1] in ['M', 'F']:
            tabulated = tabulated[:-1] + colors_str[0] + tabulated[-1:] + colors_str[1]
    print(tabulated)


def compare_dfs(old_df: pd.DataFrame, new_df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame]]:
    """Compare dogs dataframes for additions/adoptions.

    Parameters
    ----------
    old_df : pd.DataFrame
        [description]
    new_df : pd.DataFrame
        [description]

    Returns
    -------
    Tuple[Optional[pd.DataFrame]]
        [description]
    """
    old_keys = set(old_df.index)
    new_keys = set(new_df.index)
    new_dogs = new_keys.difference(old_keys)
    adopted_dogs = old_keys.difference(new_keys)
    if len(new_dogs) == 0:
        new_dogs_df = None
    else:
        new_dogs_df = pd.DataFrame(columns=old_df.columns)
        for key in new_dogs:
            new_dogs_df = new_dogs_df.append(new_df.loc[str(key)])
    if len(adopted_dogs) == 0:
        adopted_dogs_df = None
    else:
        adopted_dogs_df = pd.DataFrame(columns=old_df.columns)
        for key in adopted_dogs:
            adopted_dogs_df = adopted_dogs_df.append(old_df.loc[str(key)])
    return (new_dogs_df, adopted_dogs_df)


def print_refresh_report_df(changes: tuple, verbose: bool = False, mode: str = None) -> bool:
    """Print a somewhat formatted report of adopted/added dogs (dataframe).

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
    if changes[0] is not None:
        print()
        if mode == 'color':
            cprint('*' * 80, 'red')
            cprint(dt.strftime(dt.now(), '%Y-%m-%d %H:%M:%S'), 'red')
            cprint('{} new dog(s) added!!'.format(len(changes[0])), 'red')
            df_pretty_print(changes[0], colored_sex=True)
        else:
            print('*' * 80)
            print(dt.strftime(dt.now(), '%Y-%m-%d %H:%M:%S'))
            print('{} new dog(s) added!!'.format(len(changes[0])))
            df_pretty_print(changes[0])
    if changes[1] is not None:
        print()
        if mode == 'color':
            cprint(dt.strftime(dt.now(), '%Y-%m-%d %H:%M:%S'), 'yellow')
            cprint('{} new dog(s) adopted!!'.format(len(changes[1])), 'yellow')
            df_pretty_print(changes[1], colored_sex=True)
        else:
            print('{} new dog(s) adopted!!'.format(len(changes[1])))
            df_pretty_print(changes[1])
    # return any([any(df.any()) for df in changes])
    return (changes[0] is not None) or (changes[1] is not None)


def close_connection(driver: WebDriverClass):
    """Close webdriver instance.

    Parameters
    ----------
    driver : WebDriverClass
        selenium webdriver instance to close
    """
    driver.quit()
    time.sleep(1)


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
            curr_df = dog_list_to_df(fetch_dogs_list(driver))
            if first_run:
                print('\n\n\nstarting loop...')
                if 'data' in cache:
                    cached_df = cache['data']
                    cached_time = cache['time']
                    if color_print == 'color':
                        cprint('found cache from {} with {} available dogs'.format(
                            cached_time, len(cached_df)), 'green')
                        df_pretty_print(cached_df, colored_sex=True)
                        curr_df = dog_list_to_df(fetch_dogs_list(driver))
                        changes = compare_dfs(cached_df, curr_df)
                        print_refresh_report_df(changes, mode=color_print)
                    else:
                        print('found cache from {} with {} available dogs'.format(
                            cached_time, len(cached_df)))
                        df_pretty_print(cached_df, colored_sex=False)
                        curr_df = dog_list_to_df(fetch_dogs_list(driver))
                        changes = compare_dfs(cached_df, curr_df)
                        print_refresh_report_df(changes)
                else:
                    if color_print == 'color':
                        cprint('monitoring loop started: {}'.format(dt.strftime(dt.now(),
                            '%Y-%m-%d %H:%M:%S')), 'green')
                        cprint('detected {} dogs available\n'.format(len(curr_df)), 'green')
                        df_pretty_print(curr_df, colored_sex=True)
                    else:
                        print('monitoring loop started: {}'.format(dt.strftime(dt.now(),
                            '%Y-%m-%d %H:%M:%S')))
                        print('detected {} dogs available\n'.format(len(curr_df)))
                        df_pretty_print(curr_df)
                first_run = False
                old_df = curr_df
                continue
            curr_df = dog_list_to_df(fetch_dogs_list(driver))
            changes = compare_dfs(old_df, curr_df)
            if verbose:
                print('comparison says {}, continuing...'.format(changes))
            changed = print_refresh_report_df(changes, mode=color_print)
            if changed:
                if color_print == 'color':
                    cprint('Available dogs: {}'.format(len(curr_df)), 'green')
                else:
                    print('Available dogs: {}'.format(len(curr_df)))
            old_df = curr_df
            time.sleep(interval)
    except KeyboardInterrupt:
        print('\nsaving cache...')
        save_to_cache(cache, curr_df)
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
