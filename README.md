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
import requests
from lifeguard import NORMAL, PROBLEM, change_status
from lifeguard.actions.database import save_result_into_database
from lifeguard.actions.notifications import notify_in_single_message
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
        "pudim_is_alive",
        NORMAL,
        {status: result.status_code},
        {"notification": {"notify": True}},
    )
```

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

### Settings

To see all settings avaiable run command:

`lifeguard -d`

