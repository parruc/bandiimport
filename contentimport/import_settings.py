import json
from logging import getLogger

from plone import api
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.utils import get_installer
from Products.Five import BrowserView
from zope.component import getUtility
from ZPublisher.HTTPRequest import FileUpload

logger = getLogger(__name__)


class ImportSettings(BrowserView):
    """Import various settings"""

    def __call__(self, jsonfile=None, return_json=False):
        if jsonfile:
            self.portal = api.portal.get()
            status = "success"
            try:
                if isinstance(jsonfile, str):
                    return_json = True
                    data = json.loads(jsonfile)
                elif isinstance(jsonfile, FileUpload):
                    data = json.loads(jsonfile.read())
                else:
                    raise ("Data is neither text nor upload.")
            except Exception as e:
                status = "error"
                logger.error(e)
                api.portal.show_message(
                    "Failure while uploading: {}".format(e),
                    request=self.request,
                )
            else:
                self.import_settings(data)
                msg = "Imported registry settings"
                api.portal.show_message(msg, self.request)
            if return_json:
                msg = {"state": status, "msg": msg}
                return json.dumps(msg)

        return self.index()

    def import_settings(self, data):
        installer = get_installer(self.context)
        for addon in data["addons"]:
            if not installer.is_product_installed(addon) and installer.is_product_installable(addon):
                installer.install_product(addon)
                logger.info(f"Installed addon {addon}")
        registry = getUtility(IRegistry)
        for key, value in data["registry"].items():
            registry[key] = value
            logger.info(f"Imported record {key}: {value}")
