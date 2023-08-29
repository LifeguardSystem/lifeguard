import traceback

from lifeguard.controllers import register_custom_controller, send_status
from lifeguard.groups import build_groups_summary, build_group_validations_list
from lifeguard.logger import lifeguard_logger as logger


def groups_summary_controller():
    try:
        return build_groups_summary()
    except Exception as error:
        logger.error(
            "error on build groups summary: %s",
            error,
            extra={"traceback": traceback.format_exc()},
        )
        return send_status(
            500,
            content_type="application/json",
        )


def groups_controller(group):
    try:
        return build_group_validations_list(group)
    except Exception as error:
        logger.error(
            "error on build group validations list: %s",
            error,
            extra={"traceback": traceback.format_exc()},
        )
        return send_status(
            500,
            content_type="application/json",
        )

    return {
        "groupName": "Abelinhas",
        "groupID": "bees",
        "monitors": [
            {
                "name": "Checando filas de processamento do Abelinhas",
                "id": "queues_validation",
                "status": "normal",
                "description": "As filas de processamento do Abelinhas são parte fundamental do sistema, elas são responsáveis para gerar os valores apresentados em tela e também processar os arquivos. Por isso é de extrema importancia as elas estejam funcionando corretamente. Essa validação fica monitorando as filas e se caso as filas não estejam com a vazão correta, uma alerta será disparado.",
                "content": {
                    "queue": [
                        {
                            "description": "bees:consolidation_spreadsheet_entries_queue",
                            "value": 92029,
                        },
                        {
                            "description": "bees:consolidation_entries_queue",
                            "value": 2892,
                        },
                        {
                            "description": "bees:spreadsheets_queue",
                            "value": 110,
                        },
                    ],
                    "action": [
                        {
                            "description": "Ver detalhes das filas",
                            "linkTo": "https://google.com.br/",
                        },
                    ],
                },
            }
        ],
    }


def load_groups_controllers():
    register_custom_controller(
        "/lifeguard/groups/summary", groups_summary_controller, {"methods": ["GET"]}
    )
    register_custom_controller(
        "/lifeguard/groups/<group>", groups_controller, {"methods": ["GET"]}
    )
