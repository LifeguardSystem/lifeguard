"""
Actions executed after validations thats save data into database
"""
from lifeguard.repositories import ValidationRepository


def save_result_into_database(validation_response, _settings):
    """
    Save last validation result into database

    :param validation_response: a validation response
    :param _settings: not used in this action
    """

    repository = ValidationRepository()
    repository.save_validation_result(validation_response)
