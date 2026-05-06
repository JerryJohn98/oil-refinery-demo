from scripts.core.constants.app_constants import CollectionNames, DatabaseNames
from scripts.utils.mongo_util import MongoCollectionBaseClass


class AccessibleHierarchyCollection(MongoCollectionBaseClass):
    def __init__(self, mongo_client, project_id=None):
        super().__init__(
            mongo_client,
            database=DatabaseNames.ilens_configuration,
            collection=CollectionNames.accessible_hierarchy,
        )
        self.project_id = project_id

    def find_by_condition(self, query=None, projection=None):
        try:
            if not query:
                query = {}
            record = self.find(query=query, filter_dict=projection)
            if not record:
                return None
            record = self.fetch_records_from_object(record)
            return record
        except Exception:
            return None
