from lifeguard.repositories import ValidationRepository
from lifeguard.validations import VALIDATIONS


def build_groups_summary():
    """
    Build validation summary
    """

    groups = {}

    validation_repository = ValidationRepository()
    for name, attributes in VALIDATIONS.items():
        if attributes["group"] not in groups:
            groups[attributes["group"]] = {
                "groupName": attributes["group"],
                "groupID": attributes["group"],
                "monitorsStateCount": {
                    "normal": 0,
                    "warning": 0,
                    "problem": 0,
                },
            }

        validation = validation_repository.fetch_last_validation_result(name)
        if validation:
            groups[attributes["group"]]["monitorsStateCount"][
                validation.status.lower()
            ] += 1

    return [group for group in groups.values()]


def build_group_validations_list(group):
    """
    Build validation list
    """

    result = {
        "groupName": group,
        "groupID": group,
        "monitors": [],
    }
    validation_repository = ValidationRepository()

    for name, attributes in VALIDATIONS.items():
        if attributes["group"] != group:
            continue

        validation = validation_repository.fetch_last_validation_result(name)
        if validation:
            result["monitors"].append(
                {
                    "id": name,
                    "name": name,
                    "description": attributes["description"],
                    "status": validation.status.lower(),
                    "content": (validation.settings or {}).get("content", {}),
                }
            )
    return result
