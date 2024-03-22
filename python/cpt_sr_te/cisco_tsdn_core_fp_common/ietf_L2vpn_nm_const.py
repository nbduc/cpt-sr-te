from cisco_tsdn_core_fp_common.constants import ZOMBIE_PATH

L2NM_PLAN_PATH = "/l2vpn-ntw/vpn-services/vpn-service-plan"
L2NM_SERVICE_PATH = "/l2vpn-ntw/vpn-services/vpn-service"

L2VPN_LSA_PLAN_PATH = "/cisco-tsdn-core-fp-common:rfs-flat-L2vpn-"
L2VPN_LSA_LOCAL_SITE_PLAN_PATH = "/cisco-tsdn-core-fp-common:rfs-flat-L2vpn-local-site-plan"
L2VPN_LSA_REMOTE_SITE_PLAN_PATH = "/cisco-tsdn-core-fp-common:rfs-flat-L2vpn-remote-site-plan"
L2VPN_LSA_SITE_PLAN_PATH = "/cisco-tsdn-core-fp-common:rfs-flat-L2vpn-site-plan"

LOCAL_SITE = "local-site"
REMOTE_SITE = "remote-site"
SITE = "site"

P2P = "p2p"
EVPN_VPWS = "evpn-vpws"
EVPN_MULTIPOINT = "evpn-multipoint"

L2NM_VPN_NODE_COMP_TYPE = "ietf-l2vpn-ntw-nano-services:vpn-node"

RP_STMNT_PATH = ("/l2vpn-routing-policy/policy-definitions/"
                 + "policy-definition/statements/statement/")
RP_DS_PATH = ("/cisco-l2vpn-routing-policy:l2vpn-routing-policy/"
              + "cisco-l2vpn-routing-policy:defined-sets/")
RP_POLICY_PATH = ("/l2vpn-ntw:l2vpn-ntw/l2vpn-ntw:vpn-services/l2vpn-ntw:vpn-service"
                  + "[vpn-nodes/vpn-node/te-service-mapping/te-mapping/odn/route-policy=")

TAG_SET = "tag-set"
EVPN_RT_SET = "evpn-route-type-set"
RD_SET = "rd-set"


def get_l2nm_service_kp(service_name):
    return f"{L2NM_SERVICE_PATH}{{{service_name}}}"


def get_l2nm_plan_kp(service_name):
    return (f"{L2NM_PLAN_PATH}{{{service_name}}}")


def get_l2nm_zombie_kp(service_name):
    zombie_service_path = (f"{L2NM_SERVICE_PATH}[vpn-id='{service_name}']")
    return f'{ZOMBIE_PATH}{{"{zombie_service_path}"}}'


def get_l2vpn_lsa_plan_path(site_type):
    return f"{L2VPN_LSA_PLAN_PATH}{site_type}-plan"
