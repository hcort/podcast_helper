"""
    depending on selenium version we have to use a different import statement
    opera driver needs an older selenium version

    FIXME
"""
# pylint: disable=unused-import
import selenium
if selenium.__version__ == '3.141.0':
    from selenium.webdriver.common.keys import Keys
else:
    from selenium.webdriver import Keys
