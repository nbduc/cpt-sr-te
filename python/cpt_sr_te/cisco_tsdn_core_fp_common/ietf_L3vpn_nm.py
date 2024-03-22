import ncs

from cisco_tsdn_core_fp_common import utils as utils
from cisco_tsdn_core_fp_common import ietf_l3vpn_nm_const as l3nm_utils
from cisco_tsdn_core_fp_common.cnc_service import CncService
import re


class IETFL3vpn(CncService):
    def __init__(self, path, log):
        super().__init__(path)
        self.log = log

    def redeploy(self):
        # Skip re-deploy if internal plan error-info/message matched NB plan error-info/message
        # to avoid re-deploy loops on failure
        internal_service_key = (l3nm_utils.get_internal_l3vpn_name(self.service_key[0]),
                                self.service_key[1])
        if utils.match_plan_err_msg(self.plan_path, self.service_name,
                                    self.internal_plan_path, internal_service_key) and \
                utils.is_failed_plan_converged(self.plan_path, self.service_name, self.log):
            return

        utils.redeploy_if_needed(self)

    @staticmethod
    def get_service_name_from_path(path):
        l3vpn_service_name = re.search("flat-L3vpn-plan{(.*?) (.*?)}", path).group(1)
        # Remove 'L3NM-' and '-internal'
        if l3vpn_service_name[:5] == "L3NM-" and l3vpn_service_name[-9:] == "-internal":
            service_name = l3vpn_service_name[5:-9]
        else:
            # service_name = L3NM-<service-name>-internal
            service_name = l3vpn_service_name
        return service_name

    @staticmethod
    def get_service_key_from_path(path):
        re_search = re.search("flat-L3vpn-plan{(.*?) (.*?)}", path)
        l3vpn_service_name = re_search.group(1)
        # Remove 'L3NM-' and '-internal'
        if l3vpn_service_name[:5] == "L3NM-" and l3vpn_service_name[-9:] == "-internal":
            service_name = l3vpn_service_name[5:-9]
        else:
            # service_name = L3NM-<service-name>-internal
            service_name = l3vpn_service_name
        return service_name, re_search.group(2)

    @staticmethod
    def get_service_kp(l3vpn_service_name):
        return f"/l3vpn-ntw/vpn-services/vpn-service{{{l3vpn_service_name}}}"

    @staticmethod
    def get_service_xpath(l3vpn_service_name):
        return f"/l3vpn-ntw/vpn-services/vpn-service[vpn-id='{l3vpn_service_name}']"

    @staticmethod
    def get_plan_kp(l3vpn_service_name):
        return f"/l3vpn-ntw/vpn-services/vpn-service-plan{{{l3vpn_service_name}}}"

    @staticmethod
    def get_plan_path():
        return "/l3vpn-ntw/vpn-services/vpn-service-plan"

    @staticmethod
    def get_internal_plan_path():
        if IETFL3vpn.is_lsa_setup():
            return "/cisco-tsdn-core-fp-common:rfs-flat-L3vpn-plan"
        else:
            return (
                "/cisco-flat-L3vpn-fp-internal:flat-L3vpn-internal"
                "/cisco-flat-L3vpn-fp-internal:flat-L3vpn-plan"
            )

    @staticmethod
    def is_lsa_setup():
        with ncs.maapi.single_read_trans("", "system", db=ncs.RUNNING) as th:
            try:
                root = ncs.maagic.get_root(th)
                # If this path exists, it is not LSA
                non_lsa_path = root.cisco_flat_L3vpn_fp_internal__flat_L3vpn
                if non_lsa_path:
                    return False
            except AttributeError:
                return True
