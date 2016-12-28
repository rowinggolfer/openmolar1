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

from PyQt5 import QtCore

LOGGER = logging.getLogger("openmolar")


try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
    LOGGER.info("Using QtWebEngineWidgets.QWebEngineView for QWebView")

    class OMWebPage(QWebEnginePage):
        delegate_links = False

        def __init__(self, parent=None):
            print("initiated OMWebPage")
            super().__init__(parent)

        def acceptNavigationRequest(self, url, type_, bool_):
            if self.delegate_links and \
                    type_ == self.NavigationTypeLinkClicked and \
                    url.url().startswith("om://"):
                LOGGER.debug("acceptNavigationRequest %s", url)
                self.parent().linkClicked.emit(url)
                return False
            return QWebEnginePage.acceptNavigationRequest(
                self, url, type_, bool_)

    class OMWebView(QWebEngineView):
        '''
        A wrapper for QtWebEngineWidgets.QWebEngineView
        to emulate functions of QtWebKitWidgets.QWebView
        '''
        linkClicked = QtCore.pyqtSignal(object)
        def __init__(self, parent=None):
            super().__init__(parent)
            self.om_web_page = OMWebPage(self)
            self.setPage(self.om_web_page)

        def scroll_to_bottom(self):
            '''
            Scroll the page contents down to the bottom.
            if this is called before the page is loaded, it won't work.
            '''
            self.om_web_page.loadFinished.connect(self._scroll)

        def _scroll(self):
            LOGGER.debug("scrolling webpage")
            self.om_web_page.runJavaScript(
                    "window.scrollTo(0,document.body.scrollHeight);")

        def delegate_links(self):
            self.om_web_page.delegate_links=True


except ImportError:
    # QtWebKitWidgets is deprecated in Qt5.6
    LOGGER.info("Using QtWebKitWidgets for QWebView")
    from PyQt5.QtWebKitWidgets import QWebView

    class OMWebView(QWebView):
        def __init__(self, parent=None):
            super().__init__(parent)

        def scroll_to_bottom(self):
            wf = self.page().mainFrame()
            orientation = QtCore.Qt.Vertical
            wf.setScrollBarValue(orientation,
                                 wf.scrollBarMaximum(orientation))

        def delegate_links(self):
            page = self.page()
            page.setLinkDelegationPolicy(page.DelegateAllLinks)


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication([])
    wv = OMWebView()
    wv.show()
    html = ("<html><body>%s<hr />"
            "<a href='om://clickhere'>click here</a></body></html>" %
            "<br />".join(["line %d" % i for i in range(200)]))
    wv.setHtml(html)
    wv.scroll_to_bottom()
    wv.delegate_links()
    wv.linkClicked.connect(print)
    app.exec_()
