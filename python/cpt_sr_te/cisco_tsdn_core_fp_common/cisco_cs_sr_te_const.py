from cisco_tsdn_core_fp_common.constants import ZOMBIE_PATH


CS_SR_TE_PLAN_PATH = "/cs-sr-te-plan"
CS_SR_TE_SERVICE_PATH = "/cs-sr-te-policy"


def get_cs_sr_te_service_kp(service_name):
    return f"{CS_SR_TE_SERVICE_PATH}{{{service_name}}}"


def get_cs_sr_te_plan_kp(service_name):
    return (f"{CS_SR_TE_PLAN_PATH}{{{service_name}}}")


def get_cs_sr_te_zombie_kp(service_name):
    zombie_service_path = (f"{CS_SR_TE_SERVICE_PATH}[name='{service_name}']")
    return f'{ZOMBIE_PATH}{{"{zombie_service_path}"}}'
