from scripts.core.constants.app_constants import MongoQueryConstants


class CustomerProjectAggregate:
    @staticmethod
    def get_hierarchy_level(project_id):
        return [
            {MongoQueryConstants.match: {"customer_project_id": project_id}},
            {
                MongoQueryConstants.lookup: {
                    "from": "template_levels",
                    "localField": "n_level_hierarchy_template_id",
                    "foreignField": "template_id",
                    "as": "stepper_data",
                }
            },
            {
                MongoQueryConstants.unwind: {
                    "path": "$stepper_data",
                    "preserveNullAndEmptyArrays": True,
                }
            },
            {
                MongoQueryConstants.add_fields: {
                    "level_key": "$stepper_data.level_key",
                    "level_name": "$stepper_data.level_name",
                }
            },
            {"$project": {"_id": 0, "level_name": 1, "level_key": 1}},
        ]
