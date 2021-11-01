import html2text
import logging
from scrapy.utils.project import get_project_settings

from converter.constants import Constants
from converter.es_connector import EduSharing
from converter.items import *
from converter.web_tools import *


class LomBase:
    name = None
    friendlyName = "LOM Based spider"
    ranking = 1
    version = (
        "1.0"  # you can override this locally and use it for your getHash() function
    )

    uuid = None
    remoteId = None
    forceUpdate = False

    def __init__(self, **kwargs):
        if self.name is None:
            raise NotImplementedError(f'{self.__class__.__name__}.name is not defined on crawler')
        if "uuid" in kwargs:
            self.uuid = kwargs["uuid"]
        if "remoteId" in kwargs:
            self.remoteId = kwargs["remoteId"]
        if "cleanrun" in kwargs and kwargs["cleanrun"] == "true":
            logging.info(
                "cleanrun requested, will force update for crawler " + self.name
            )
            # EduSharing().deleteAll(self)
            self.forceUpdate = True
        if "resetVersion" in kwargs and kwargs["resetVersion"] == "true":
            logging.info(
                "resetVersion requested, will force update + reset versions for crawler "
                + self.name
            )
            # EduSharing().deleteAll(self)
            EduSharing.resetVersion = True
            self.forceUpdate = True

    # override to improve performance and automatically handling id
    def getId(self, response=None) -> str:
        raise NotImplementedError(f'{self.__class__.__name__}.getId callback is not defined')

    # override to improve performance and automatically handling hash
    def getHash(self, response=None) -> str:
        raise NotImplementedError(f'{self.__class__.__name__}.getHash callback is not defined')

    # return the unique uri for the entry
    def getUri(self, response=None) -> str:
        return response.url

    def getUUID(self, response=None) -> str:
        return EduSharing.buildUUID(self.getUri(response))

    def hasChanged(self, response=None) -> bool:
        if self.forceUpdate:
            return True
        if self.uuid:
            if self.getUUID(response) == self.uuid:
                logging.info("matching requested id: " + self.uuid)
                return True
            return False
        if self.remoteId:
            if str(self.getId(response)) == self.remoteId:
                logging.info("matching requested id: " + self.remoteId)
                return True
            return False
        db = EduSharing().findItem(self.getId(response), self)
        changed = db == None or db[1] != self.getHash(response)
        if not changed:
            logging.info("Item " + db[0] + " has not changed")
        return changed

    # you might override this method if you don't want to import specific entries
    def shouldImport(self, response=None) -> bool:
        return True

    def parse(self, response):
        if self.shouldImport(response) is False:
            logging.debug(
                "Skipping entry {} because shouldImport() returned false".format(str(self.getId(response)))
            )
            return None
        if self.getId(response) is not None and self.getHash(response) is not None:
            if not self.hasChanged(response):
                return None
        main = self.getBase(response)
        main.add_value("lom", self.getLOM(response).load_item())
        main.add_value("valuespaces", self.getValuespaces(response).load_item())
        main.add_value("license", self.getLicense(response).load_item())
        main.add_value("permissions", self.getPermissions(response).load_item())
        logging.debug(main.load_item())
        main.add_value("response", self.mapResponse(response).load_item())
        return main.load_item()

    # @deprecated
    # directly use WebTools instead
    def html2Text(self, html):
        return WebTools.html2Text(html)

    # @deprecated
    # directly use WebTools instead
    def getUrlData(self, url):
        return WebTools.getUrlData(url)
    def mapResponse(self, response, fetchData=True):
        r = ResponseItemLoader(response=response)
        r.add_value("status", response.status)
        # r.add_value('body',response.body.decode('utf-8'))

        # render via splash to also get the full javascript rendered content.
        if fetchData:
            data = self.getUrlData(response.url)
            r.add_value("html", data["html"])
            r.add_value("text", data["text"])
            r.add_value("cookies", data["cookies"])
            r.add_value("har", data["har"])
        r.add_value("headers", response.headers)
        r.add_value("url", self.getUri(response))
        return r

    def getValuespaces(self, response):
        return ValuespaceItemLoader(response=response)

    def getLOM(self, response) -> LomBaseItemloader:
        lom = LomBaseItemloader(response=response)
        lom.add_value("general", self.getLOMGeneral(response).load_item())
        lifecycle = self.getLOMLifecycle(response)
        if isinstance(lifecycle, LomLifecycleItemloader):
            lom.add_value("lifecycle", lifecycle.load_item())
        else:
            # support yield and generator for multiple values
            for contribute in lifecycle:
                lom.add_value("lifecycle" ,contribute.load_item())
        lom.add_value("technical", self.getLOMTechnical(response).load_item())
        lom.add_value("educational", self.getLOMEducational(response).load_item())
        lom.add_value("classification", self.getLOMClassification(response).load_item())
        lom.add_value("relation", self.getLOMRelation(response).load_item())
        lom.add_value("annotation", self.getLOMAnnotation(response).load_item())
        return lom

    def getBase(self, response=None) -> BaseItemLoader:
        base = BaseItemLoader()
        base.add_value("sourceId", self.getId(response))
        base.add_value("hash", self.getHash(response))
        # we assume that content is imported. Please use replace_value if you import something different
        base.add_value("type", Constants.TYPE_MATERIAL)
        return base

    def getLOMGeneral(self, response=None) -> LomGeneralItemloader:
        return LomGeneralItemloader(response=response)

    """
    return one or more lifecycle element
    If you want to return more than one, use yield and generate multiple LomLifecycleItemloader
    """
    def getLOMLifecycle(self, response=None) -> LomLifecycleItemloader:
        return LomLifecycleItemloader(response=response)

    def getLOMTechnical(self, response=None) -> LomTechnicalItemLoader:
        return LomTechnicalItemLoader(response=response)

    def getLOMEducational(self, response=None) -> LomEducationalItemLoader:
        return LomEducationalItemLoader(response=response)

    def getLicense(self, response=None) -> LicenseItemLoader:
        return LicenseItemLoader(response=response)

    def getLOMClassification(self, response=None) -> LomClassificationItemLoader:
        return LomClassificationItemLoader(response=response)

    def getLOMRelation(self, response=None) -> LomRelationItemLoader:
        return LomRelationItemLoader(response=response)

    def getLOMAnnotation(self, response=None) -> LomAnnotationItemLoader:
        return LomAnnotationItemLoader(response=response)

    def getPermissions(self, response=None) -> PermissionItemLoader:
        permissions = PermissionItemLoader(response=response)
        # default all materials to public, needs to be changed depending on the spider!
        settings = get_project_settings()
        permissions.add_value("public", settings.get("DEFAULT_PUBLIC_STATE"))
        return permissions
