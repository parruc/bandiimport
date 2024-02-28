import logging

import transaction
from collective.exportimport.import_other import \
    ImportOrdering as BaseImportOrdering
from OFS.interfaces import IOrderedContainer
from plone import api

logger = logging.getLogger(__name__)


class ImportOrdering(BaseImportOrdering):

    def import_ordering(self, data):
        results = 0
        total = len(data)
        for index, item in enumerate(data, start=1):
            obj = api.content.get(UID=item["uuid"])
            if not obj:
                continue
            ordered = IOrderedContainer(obj.__parent__, None)
            if not ordered:
                continue
            ordered.moveObjectToPosition(obj.getId(), item["order"])
            if not index % 1000:
                logger.info(
                    u"Ordered {} ({}%) of {} items".format(
                        index, round(index / total * 100, 2), total
                    )
                )
                transaction.commit()
            results += 1
        return results
