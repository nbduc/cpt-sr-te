SR_POLICY_SERVICEPOINT = "cpt-sr-te-sr-policy-servicepoint"
SR_POLICY_COMP_HEADEND = "cpt-sr-te-sr-policy-nano-plan:head-end"
SR_POLICY_ST_CONFIG_APPLY = "cpt-sr-te-sr-policy-nano-plan:config-apply"

from cisco_tsdn_core_fp_common.constants import ZOMBIE_PATH


CPT_SR_TE_SR_POLICY_PLAN_PATH = "/cpt-sr-te:sr-policy-plan"
CPT_SR_TE_SR_POLICY_SERVICE_PATH = "/cpt-sr-te:sr-policy"


def get_cpt_sr_te_sr_policy_service_kp(service_name):
    return f"{CPT_SR_TE_SR_POLICY_SERVICE_PATH}{{{service_name}}}"


def get_cpt_sr_te_sr_policy_plan_kp(service_name):
    return f"{CPT_SR_TE_SR_POLICY_PLAN_PATH}{{{service_name}}}"


def get_cpt_sr_te_sr_policy_zombie_kp(service_name):
    zombie_service_path = f"{CPT_SR_TE_SR_POLICY_SERVICE_PATH}[name='{service_name}']"
    return f'{ZOMBIE_PATH}{{"{zombie_service_path}"}}'
