#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #


import logging

LOGGER = logging.getLogger("openmolar")

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    LOGGER.info("Using QtWebEngineWidgets.QWebEngineView for QWebView")

    class OMWebView(QWebEngineView):
        '''
        A wrapper for QtWebEngineWidgets.QWebEngineView
        to emulate functions of QtWebKitWidgets.QWebView
        '''

        def __init__(self, parent=None):
            super().__init__(self, parent)


except ImportError:
    # QtWebKitWidgets is deprecated in Qt5.6
    LOGGER.info("Using QtWebKitWidgets for QWebView")
    from PyQt5.QtWebKitWidgets import QWebView as OMWebView


if __name__ == "__main__":
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication([])
    wv = OMWebView()
    wv.show()
    app.exec_()
