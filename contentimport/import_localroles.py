import logging

import transaction
from collective.exportimport.export_other import PORTAL_PLACEHOLDER
from collective.exportimport.import_other import \
    ImportLocalRoles as BaseImportLocalRoles
from plone import api
from Products.ZCatalog.ProgressHandler import ZLogHandler

logger = logging.getLogger(__name__)


class ImportLocalRoles(BaseImportLocalRoles):
    """Import local roles"""

    def import_localroles(self, data):
        results = 0
        total = len(data)
        for index, item in enumerate(data, start=1):
            obj = api.content.get(UID=item["uuid"])
            if not obj:
                if item["uuid"] == PORTAL_PLACEHOLDER:
                    obj = api.portal.get()
                else:
                    logger.info("Could not find object to set localroles on. UUID: {}".format(item["uuid"]))
                    continue
            if item.get("localroles"):
                localroles = item["localroles"]
                for userid in localroles:
                    obj.manage_setLocalRoles(userid=userid, roles=localroles[userid])
                logger.debug(
                    u"Set roles on {}: {}".format(obj.absolute_url(), localroles)
                )
            if item.get("block"):
                obj.__ac_local_roles_block__ = 1
                logger.debug(
                    u"Disable acquisition of local roles on {}".format(
                        obj.absolute_url()
                    )
                )
            if not index % 1000:
                logger.info(
                    u"Set local roles on {} ({}%) of {} items".format(
                        index, round(index / total * 100, 2), total
                    )
                )
                transaction.commit()
            results += 1
        transaction.commit()
        if results:
            logger.info("Reindexing Security")
            catalog = api.portal.get_tool("portal_catalog")
            pghandler = ZLogHandler(1000)
            catalog.reindexIndex("allowedRolesAndUsers", None, pghandler=pghandler)
        return results
