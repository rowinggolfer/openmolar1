import os
import sys
import logging
import gettext

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger("openmolar")

if "-q" in sys.argv:
    LOGGER.setLevel(logging.WARNING)
elif "-v" in sys.argv:
    LOGGER.setLevel(logging.DEBUG)
else:
    LOGGER.setLevel(logging.INFO)
    
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


