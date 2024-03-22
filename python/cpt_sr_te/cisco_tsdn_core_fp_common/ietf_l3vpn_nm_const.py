from cisco_tsdn_core_fp_common.constants import ZOMBIE_PATH

L3NM_PLAN_PATH = "/l3vpn-ntw/vpn-services/vpn-service-plan"
L3NM_SERVICE_PATH = "/l3vpn-ntw/vpn-services/vpn-service"

L3NM_VPN_NODE_COMP_TYPE = "ietf-l3vpn-ntw-nano-services:vpn-node"

L3NM_HUB_SPOKE = "vpn-common:hub-spoke"
L3NM_ANY_TO_ANY = "vpn-common::any-to-any"

L3NM_HUB_ROLE = "vpn-common:hub-role"
L3NM_SPOKE_ROLE = "vpn-common:spoke-role"

RP_STMNT_PATH = ("/l3vpn-routing-policy/policy-definitions/"
                 + "policy-definition/statements/statement/")
RP_DS_PATH = ("/cisco-l3vpn-routing-policy:l3vpn-routing-policy/"
              + "cisco-l3vpn-routing-policy:defined-sets/")

IMPORT_VP_INST_RP_PATH = ("/l3nm:l3vpn-ntw/l3nm:vpn-services/l3nm:vpn-service[vpn-instance-profiles"
                          + "/vpn-instance-profile/address-family/vpn-targets/vpn-policies/"
                          + "import-policy=")
IMPORT_ACTIVE_VP_INST_RP_PATH = ("/l3nm:l3vpn-ntw/l3nm:vpn-services/l3nm:vpn-service[vpn-nodes"
                                 + "/vpn-node/active-vpn-instance-profiles/vpn-instance-profile/"
                                 + "address-family/vpn-targets/vpn-policies/import-policy=")

EXPORT_VP_INST_RP_PATH = ("/l3nm:l3vpn-ntw/l3nm:vpn-services/l3nm:vpn-service[vpn-instance-profiles"
                          + "/vpn-instance-profile/address-family/vpn-targets/vpn-policies"
                          + "/export-policy=")
EXPORT_ACTIVE_VP_INST_RP_PATH = ("/l3nm:l3vpn-ntw/l3nm:vpn-services/l3nm:vpn-service[vpn-nodes"
                                 + "/vpn-node/active-vpn-instance-profiles/vpn-instance-profile/"
                                 + "address-family/vpn-targets/vpn-policies/export-policy=")
MVPN_RP_PATH = ("/l3nm:l3vpn-ntw/l3nm:vpn-services/l3nm:vpn-service[multicast/ipv4/"
                + "mvpn-spmsi-tunnels-ipv4/mvpn-spmsi-tunnel-ipv4/route-policy=")

TAG_SET = "tag-set"
SOURCE_PREFIX_SET = "source-prefix-set"
DEST_PREFIX_SET = "dest-prefix-set"


def get_l3nm_service_kp(service_name):
    return f"{L3NM_SERVICE_PATH}{{{service_name}}}"


def get_l3nm_plan_kp(service_name):
    return (f"{L3NM_PLAN_PATH}{{{service_name}}}")


def get_l3nm_zombie_kp(service_name):
    zombie_service_path = (f"{L3NM_SERVICE_PATH}[vpn-id='{service_name}']")
    return f'{ZOMBIE_PATH}{{"{zombie_service_path}"}}'


def get_internal_l3vpn_name(vpn_id):
    if vpn_id[-9:] == "-internal":
        return vpn_id
    else:
        return f"L3NM-{vpn_id}-internal"
