failed_device = "/cisco-tsdn-core-fp-common:commit-queue-recovery-data/failed-device"
impacted_service = "/impacted-service-path"
failed_cq_id = "/failed-commit-queue-id"
current_poller = (
    "/cisco-tsdn-core-fp-common:commit-queue-recovery-data/current-device-poller"
)
poller_recovery_result = "/poller-recovery-result"

# TODO: how to differentiate between internal and external services
# for the case where CQ is enabled between CFS and RFS.
odn_service_alarm_id = "cisco-sr-te-cfp-sr-odn-internal:odn"
policy_service_alarm_id = "cisco-sr-te-cfp-sr-policies-internal:policies"
pm_service_alarm_id = "perf-measure-profile"
l3vpn_service_alarm_id = "flat-L3vpn"
l2vpn_remote_service_alarm_id = "flat-L2vpn-internal-remote-site-service"
l2vpn_local_service_alarm_id = "flat-L2vpn-internal-local-site-service"
tunnel_service_alarm_id = "tunnel-te"
pce_service_alarm_id = "sr-pce"
setting_service_alarm_id = "sr-setting"
transient_error_message = [
    "connection refused", "timed out", "host is unreachable",
    "no route to host", "host unreachable", "transport timeout",
    "host key mismatch", "read timeout"
]

cq_alarm_services = [
    odn_service_alarm_id,
    policy_service_alarm_id,
    pm_service_alarm_id,
    l3vpn_service_alarm_id,
    l2vpn_remote_service_alarm_id,
    l2vpn_local_service_alarm_id,
    tunnel_service_alarm_id,
    pce_service_alarm_id,
    setting_service_alarm_id
]

NCS_SELF = "ncs:self"
NCS_INIT = "ncs:init"
NCS_READY = "ncs:ready"
SELF = "self"

SELF_COMP_KEY = (NCS_SELF, SELF)

STATUS_REACHED = "reached"
STATUS_FAILED = "failed"
STATUS_NOT_REACHED = "not-reached"

ZOMBIE_PATH = "/ncs:zombies/ncs:service"

TEN_GIGABIT_ETHERNET = "TenGigabitEthernet"
TEN_GIG_E = "TenGigE"

FORTY_GIGABIT_ETHERNET = "FortyGigabitEthernet"
FORTY_GIG_E = "FortyGigE"

AUTO_HUB_RT = "auto-hub-rt"
AUTO_SPOKE_RT = "auto-spoke-rt"

# Identities
VPN_COMMON_HUB_SPOKE = "vpn-common:hub-spoke"
VPN_COMMON_ANY_TO_ANY = "vpn-common:any-to-any"

VPN_COMMON_HUB_ROLE = "vpn-common:hub-role"
VPN_COMMON_SPOKE_ROLE = "vpn-common:spoke-role"

VPN_COMMON_VPWS_EVPN = "vpn-common:vpws-evpn"
VPN_COMMON_MPLS_EVPN = "vpn-common:mpls-evpn"

VPN_COMMON_IPV4 = "vpn-common:ipv4"
VPN_COMMON_IPV6 = "vpn-common:ipv6"

PROTOCOL_PREFIX = "protocol/protocol_type/"
DELAY_INTERFACE_PREFIX = "delay-profile/interface/"
DELAY_RSVP_TE_PREFIX = "delay-profile/rsvp-te/"
DELAY_ENDPOINT_PREFIX = "delay-profile/endpoint/"
DELAY_SR_POLICY_PREFIX = "delay-profile/sr-policy/"
LIVENESS_SR_POLICY_PREFIX = "liveness-profile/sr-policy/"
LIVENESS_ENDPOINT_PREFIX = "liveness-profile/endpoint/"
LOSS_INTERFACE_PREFIX = "loss-profile/interface/"
LOSS_RSVP_TE_PREFIX = "loss-profile/rsvp-te/"
LOSS_SR_POLICY_PREFIX = "loss-profile/interface/"

PM_INTERNAL_SVC_PATH = "/pm-internal/device-profiles"
PROFILE_PATH = "Profile_Paths_Changed"
SVC_PATH = "Service_Paths_Changed"

# Error Messages
ERR_PRESERVATION = "preservation cannot be changed if monitoring state value is already 'disable' "
ERR_MONITORING_STATE = "monitoring state 'pause' can be set only when current state is 'enable' "


def join(values):
    return "".join(values)
