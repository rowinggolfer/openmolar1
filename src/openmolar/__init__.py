import os
import sys
import logging
import gettext

if "neil" in os.path.expanduser("~"):
    FORMAT = \
    '%(levelname)s {%(filename)s:%(lineno)d} %(funcName)s  - %(message)s'
else:
    FORMAT = '%(levelname)s - %(message)s'

stream_handler = logging.StreamHandler()
formatter = logging.Formatter(FORMAT)
stream_handler.setFormatter(formatter)
#logging.basicConfig(level = logging.INFO, format=FORMAT)

LOGGER = logging.getLogger("openmolar")
LOGGER.addHandler(stream_handler)

if "-q" in sys.argv:
    LOGGER.setLevel(logging.WARNING)
elif "-v" in sys.argv:
    LOGGER.setLevel(logging.DEBUG)
else:
    LOGGER.setLevel(logging.INFO)

LOGGER.info("running openmolar base module = %s"% os.path.dirname(__file__))

lang = os.environ.get("LANG")
if lang:
    try:
        LOGGER.debug("trying to install your environment language", lang)
        lang1 = gettext.translation('openmolar', languages=[lang,])
        lang1.install(unicode=True)
    except IOError:
        LOGGER.warning("%s not found, using default"% lang)
        gettext.install('openmolar', unicode=True)
else:
    #-- on windows.. os.environ.get("LANG") is None
    LOGGER("no language environment found")
    gettext.install('openmolar', unicode=True)


