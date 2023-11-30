"""

    FIXME depending on selenium version we have to use a different import statement
    FIXME opera driver needs an older selenium version

"""
# from selenium.webdriver import Keys
import selenium
if selenium.__version__ == '3.141.0':
    from selenium.webdriver.common.keys import Keys
else:
    from selenium.webdriver import Keys