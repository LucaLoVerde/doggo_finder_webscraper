# doggo_finder_webscraper
[![License: GPL v3](https://img.shields.io/github/license/LucaLoVerde/doggo_finder_webscraper?style=plastic)](https://www.gnu.org/licenses/gpl-3.0)


<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [doggo_finder_webscraper](#doggo_finder_webscraper)
  - [Requirements](#requirements)
  - [Usage](#usage)
  - [Roadmap](#roadmap)
  - [License](#license)
  - [Contact](#contact)

<!-- /code_chunk_output -->


Exercising a bit with webscraping using selenium with python. I started this when I realized that one of my favorite local animal rescue websites doesn't really offer any way of receiving updates when a new dog is added to the list. It's being enough of a frustrating experience so far that I thought I could try to learn a bit of webscraping methods. If you are looking for rigorous, clean stuff, be advised that this might not be the right place (:

## Requirements
I'm using Python 3.8 with Anaconda. Dependencies so far are:
* selenium (version 3.141.0) [Project homepage](https://github.com/SeleniumHQ/selenium/), [PyPI page](https://pypi.org/project/selenium/)
* webdriver_manager (version 3.2.1) [Project homepage](https://github.com/SergeyPirogov/webdriver_manager), [PyPI page](https://pypi.org/project/webdriver-manager/)
* A supported web browser (for now, works with Firefox and Chrome)

I'm mainly developing under Linux and Windows.

## Usage
For now, only a barebone script exists. To run it, make sure you have the dependencies mentioned above installed, then run the script from the root folder:
```python
python doggo_finder_test.py
```

At the moment, it will open a background Selenium webdriver instance on the adoption page of the DPS Rescue. It will first print the current listed dogs, then it will enter a loop in which it will monitor the page for updates (adoptions and additions). The check interval is set to 120 seconds by default, but can be changed with the appropriate `interval` argument in the loop call.

I still don't have a clue if this works, as the website isn't updated that frequently to check the dog listing changes logic.

## Roadmap
Ideally, I'd want to run this thing in the background, and when it detects a change in the rescue dogs list (new dogs added to the list and adopted dogs removed from it) it should notify me reliably. I'd also like to parse the information a bit better to do some basic filtering of candidates.

## License

Distributed under the GPLv3 license. See `LICENSE` for more information.

## Contact

Luca Lo Verde - luca.loverde0@gmail.com

Project Link: [https://github.com/LucaLoVerde/doggo_finder_webscraper](https://github.com/LucaLoVerde/doggo_finder_webscraper)