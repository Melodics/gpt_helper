from .ssm import get_ssm_parameter, get_secrets_manager_parameter


# config_ssm = {
#     "GPT_KEY": get_ssm_parameter("CONFIG_OPENAI_KEY"),
#     "SLACK_APP_TOKEN": get_ssm_parameter("CONFIG_GPT3PO_SLACK_APP_TOKEN"),
#     "SLACK_BOT_TOKEN": get_ssm_parameter("CONFIG_GPT3PO_SLACK_BOT_TOKEN"),
#     "SLACK_SIGNING_SECRET": get_ssm_parameter("CONFIG_GPT3PO_SLACK_SIGNING"),
# }

config_secrets_manager = {
    "GPT_KEY": get_secrets_manager_parameter("CONFIG_OPENAI_KEY"),
    "SLACK_APP_TOKEN": get_secrets_manager_parameter("CONFIG_GPT3PO_SLACK_APP_TOKEN"),
    "SLACK_BOT_TOKEN": get_secrets_manager_parameter("CONFIG_GPT3PO_SLACK_BOT_TOKEN"),
    "SLACK_SIGNING_SECRET": get_secrets_manager_parameter("CONFIG_GPT3PO_SLACK_SIGNING"),
}