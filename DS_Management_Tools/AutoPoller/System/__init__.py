import logging, unittest

from AutoPoller.System.YamlWatcher import YamlWatcher


logging.basicConfig(level=logging.INFO)
def main():
    YamlWatcher().run()
    
class Test(unittest.TestCase):
    def test_main(self):
        main()