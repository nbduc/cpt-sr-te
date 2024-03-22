from cisco_tsdn_core_fp_common import utils as utils
from cisco_tsdn_core_fp_common.cnc_service import CncService
import ncs
import re


class IETFL2NM(CncService):
    def __init__(self, path, log):
        super().__init__(path)
        self.log = log

        if "cisco-flat-L2vpn-fp-internal-local-site" in path:
            self.internal_plan_path = self.get_internal_local_plan_path()
            self.site = "local"
        elif "cisco-flat-L2vpn-fp-internal-remote-site" in path:
            self.internal_plan_path = self.get_internal_remote_plan_path()
            self.site = "remote"
        elif "cisco-flat-L2vpn-fp-internal-site" in path:
            self.internal_plan_path = self.get_internal_site_plan_path()
            self.site = "site"

    def redeploy(self):
        # Skip re-deploy if internal plan error-info/message matched NB plan error-info/message
        # to avoid re-deploy loops on failure
        if utils.match_plan_err_msg(self.plan_path, self.service_name, self.internal_plan_path,
                                    self.service_key) and \
                utils.is_failed_plan_converged(self.plan_path, self.service_name, self.log):
            return

        utils.redeploy_if_needed(self)

    @staticmethod
    def get_service_name_from_path(path):
        l2vpn_service_name = re.search("flat-L2vpn-plan{(.*?) (.*?)}", path).group(1)
        return l2vpn_service_name[5:-9]

    @staticmethod
    def get_service_key_from_path(path):
        re_search = re.search("flat-L2vpn-plan{(.*?) (.*?)}", path)
        return re_search.group((1)), re_search.group(2)

    @staticmethod
    def get_service_kp(l2nm_service_name):
        return "/l2vpn-ntw:l2vpn-ntw/l2vpn-ntw:vpn-services" \
               f"/l2vpn-ntw:vpn-service{{{l2nm_service_name}}}"

    @staticmethod
    def get_service_xpath(l2nm_service_name):
        return f"/l2vpn-ntw/vpn-services/vpn-service[vpn-id='{l2nm_service_name}']"

    @staticmethod
    def get_plan_kp(l2nm_service_name):
        return f"/l2vpn-ntw/vpn-services/vpn-service-plan{{{l2nm_service_name}}}"

    @staticmethod
    def get_plan_path():
        return "/l2vpn-ntw:l2vpn-ntw/l2vpn-ntw:vpn-services/cisco-l2vpn-ntw:vpn-service-plan"

    @staticmethod
    def get_internal_plan_path(site_type="local"):
        if site_type == "local":
            return IETFL2NM.get_internal_local_plan_path()
        elif site_type == "remote":
            return IETFL2NM.get_internal_remote_plan_path()
        else:
            return IETFL2NM.get_internal_site_plan_path()

    @staticmethod
    def get_internal_local_plan_path():
        if IETFL2NM.is_lsa_setup():
            return "/cisco-tsdn-core-fp-common:rfs-flat-L2vpn-local-site-plan"
        else:
            return (
                "/cisco-flat-L2vpn-fp-internal-local-site:flat-L2vpn-internal-local-site"
                "/cisco-flat-L2vpn-fp-internal-local-site:flat-L2vpn-plan"
            )

    @staticmethod
    def get_internal_remote_plan_path():
        if IETFL2NM.is_lsa_setup():
            return "/cisco-tsdn-core-fp-common:rfs-flat-L2vpn-remote-site-plan"
        else:
            return (
                "/cisco-flat-L2vpn-fp-internal-remote-site:flat-L2vpn-internal-remote-site"
                "/cisco-flat-L2vpn-fp-internal-remote-site:flat-L2vpn-plan"
            )

    @staticmethod
    def get_internal_site_plan_path():
        if IETFL2NM.is_lsa_setup():
            return "/cisco-tsdn-core-fp-common:rfs-flat-L2vpn-site-plan"
        else:
            return (
                "/cisco-flat-L2vpn-fp-internal-site:flat-L2vpn-internal-site"
                "/cisco-flat-L2vpn-fp-internal-site:flat-L2vpn-plan"
            )

    @staticmethod
    def is_lsa_setup():
        with ncs.maapi.single_read_trans("", "system", db=ncs.RUNNING) as th:
            try:
                root = ncs.maagic.get_root(th)
                # If this internal service path exists, it is not LSA
                non_lsa_path = root.\
                    cisco_flat_L2vpn_fp_internal_local_site__flat_L2vpn_internal_local_site_service
                if non_lsa_path:
                    return False
            except AttributeError:
                return True
