# Lifeguard

![Build Status](https://github.com/LifeguardSystem/lifeguard/workflows/Lifeguard%20Core%20CI/badge.svg)
![Lifeguard Core Publish](https://github.com/LifeguardSystem/lifeguard/workflows/Lifeguard%20Core%20Publish/badge.svg)
[![PyPI version](https://badge.fury.io/py/lifeguard.svg)](https://badge.fury.io/py/lifeguard)

## Examples of Usage

See a complete example at: https://github.com/LifeguardSystem/lifeguard-example

### Settings File

In the root of project should be exists a file called `lifeguard_settings.py` like the example:

```python
"""
Lifeguard Settings
"""
import lifeguard_mongodb
# other dependecies

# Plugins modules
PLUGINS = [
    lifeguard_mongodb,
    # other plugins
]

# You can execute code in the lifeguard startup process
def setup(_lifeguard_context):
    pass
```

### Create a validation

To create a validation you should create a file into `validations` directory. The file should ends with `_validation.py`.
Example:

```python
from lifeguard import NORMAL, PROBLEM, change_status
from lifeguard.actions.database import save_result_into_database
from lifeguard.actions.notifications import notify_in_single_message
from lifeguard.http_client import get
from lifeguard.logger import lifeguard_logger as logger
from lifeguard.validations import ValidationResponse, validation


@validation(
    "check if pudim is alive",
    actions=[save_result_into_database, notify_in_single_message],
    schedule={"every": {"minutes": 1}},
)
def pudim_is_alive():
    status = NORMAL
    result = requests.get("http://pudim.com.br")
    logger.info("pudim status code: %s", result.status_code)

    if result.status_code != 200:
        status = change_status(status, PROBLEM)

    return ValidationResponse(
        status,
        {status: result.status_code},
    )
```

Starting with version 1.3.0, it is possible to create validations using yaml files. The file should ends with `_validation.yaml`. See the example:

```yaml
validations:
  - validation_name: "validation_name"
    description: "description of validation"
    actions:
      - lifeguard.actions.database.save_result_into_database
    schedule:
      every:
        minutes: 1
    settings:
      notification:
        update_thread_interval: 3600
    execute:
      command: path.to.module.function
      args:
        - "arg1"
        - "arg2"
```

### Validation Actions

Action is a simple python function with only 2 arguments: a validation response and a dict called settings. These settings are the parameter called settings in validation.

```python
def custom_action(validation_response, settings):
    pass
```

Builtin validations can be found in [Wiki](https://github.com/LifeguardSystem/lifeguard/wiki).

### Create a custom controller

To create a custom controller with decorators see the example

```python
import json

from lifeguard.controllers import controller


@controller("/hello/<name>")
def hello(name):
    return json.dumps({"name": name})
```

This file should be in the `controllers` directory and should ends with `_controller.py`.

### Init Lifeguard

Execute: `lifeguard`

To init only web server: `lifeguard --no-scheduler`

To init only scheduler: `lifeguard --no-server`

### Settings

To see all settings avaiable run command:

`lifeguard -d`

## Builtin Endpoints

### Recover Status

__To get global status and all validations.__

`GET /lifeguard/status/complete`

```json
{

    "status": "NORMAL",
    "validations": [
        {
            "validation_name": "pudim",
            "status": "NORMAL",
            "details": {
                "NORMAL": 200
            },
            "settings": {
                "notification": {
                    "notify": true
                }
            },
            "last_execution": "2021-06-15T10:46"
        },
        {
            "validation_name": "my site",
            "status": "NORMAL",
            "details": {
                "NORMAL": 200
            },
            "settings": {
                "notification": {
                    "notify": true
                }
            },
            "last_execution": "2021-06-15T10:46"
        }
    ]
}
```

__To get global status and only non normal validations.__

`GET /lifeguard/status`

```json
{

    "status": "PROBLEM",
    "validations": [
        {
            "validation_name": "my site",
            "status": "PROBLEM",
            "details": {
                "NORMAL": 200
            },
            "settings": {
                "notification": {
                    "notify": true
                }
            },
            "last_execution": "2021-06-15T10:46"
        }
    ]
}
```

## Authentication

### Builtin Methods

#### Basic Authentication

Set users in lifeguard context like in the example:

```python
# in lifeguard_settings.py
from lifeguard.auth import BASIC_AUTH_METHOD

def setup(lifeguard_context):
    lifeguard_context.auth_method = BASIC_AUTH_METHOD
    lifeguard_context.users = [{"username": "test", "password": "pass"}]
```

## Cors

To enable cors use the following settings:

```python
# in lifeguard_settings.py
def setup(lifeguard_context):
    lifeguard_context.cors_settings = {r"/*": {"origins": "*"}}
```
