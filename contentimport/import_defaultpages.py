import logging

import six
import transaction
from collective.exportimport import config
from collective.exportimport.import_other import \
    ImportDefaultPages as BaseImportDefaultPages
from plone import api

logger = logging.getLogger(__name__)


class ImportDefaultPages(BaseImportDefaultPages):

    def import_default_pages(self, data):
        results = 0
        for index, item in enumerate(data, start=1):
            if index % 1000 == 0:
                transaction.commit()
            obj = api.content.get(UID=item["uuid"])
            if not obj:
                if item["uuid"] == config.SITE_ROOT:
                    obj = api.portal.get()
                else:
                    continue
            if "default_page_uuid" in item:
                default_page_obj = api.content.get(UID=item["default_page_uuid"])
                if not default_page_obj:
                    logger.info("Default page missing: %s", item["default_page_uuid"])
                    continue
                default_page = default_page_obj.id
            else:
                # fallback for old export versions
                default_page = item["default_page"]
            if default_page not in obj:
                logger.info(
                    u"Default page not a child: %s not in %s",
                    default_page,
                    obj.absolute_url(),
                )
                continue

            if default_page == "index_html":
                # index_html is automatically used as default page
                continue

            if six.PY2:
                obj.setDefaultPage(default_page.encode("utf-8"))
            else:
                obj.setDefaultPage(default_page)
            logger.debug(
                u"Set %s as default page for %s", default_page, obj.absolute_url()
            )
            results += 1
        return results
