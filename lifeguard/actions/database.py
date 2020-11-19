from lifeguard.repositories import ValidationRepository


def save_result_into_database(validation_response):
    repository = ValidationRepository()
    repository.save_validation_result(validation_response)
