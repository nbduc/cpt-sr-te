import ncs

from cisco_tsdn_core_fp_common import utils as utils
from cisco_tsdn_core_fp_common.cnc_service import CncService
import re


class InternetAccessService(CncService):
    def __init__(self, path, log):
        super().__init__(path)
        self.log = log

    def redeploy(self):
        # Skip re-deploy if internal plan error-info/message matched NB plan error-info/message
        # to avoid re-deploy loops on failure
        if utils.match_plan_err_msg(self.plan_path, self.service_name,
                                    self.internal_plan_path, self.service_key) and \
                utils.is_failed_plan_converged(self.plan_path, self.service_name, self.log):
            return

        utils.redeploy_if_needed(self)

    @staticmethod
    def get_service_name_from_path(path):
        return re.search("internet-access-service-plan{(.*?)}", path).group(1)

    @staticmethod
    def get_service_key_from_path(path):
        re_search = re.search("internet-access-service-plan{(.*?)}", path)
        return re_search.group(1)

    @staticmethod
    def get_service_kp(dia_service_name):
        return (f"/cisco-internet-access-service-fp:internet-access-services/"
                f"internet-access-service{{{dia_service_name}}}")

    @staticmethod
    def get_service_xpath(dia_service_name):
        return f"/internet-access-services/internet-access-service[name='{dia_service_name}']"

    @staticmethod
    def get_plan_kp(dia_service_name):
        return (f"/cisco-internet-access-service-fp:internet-access-services/"
                f"internet-access-service-plan{{{dia_service_name}}}")

    @staticmethod
    def get_plan_path():
        return ("/cisco-internet-access-service-fp:internet-access-services/"
                "internet-access-service-plan")

    @staticmethod
    def get_internal_plan_path():
        if InternetAccessService.is_lsa_setup():
            return "/cisco-tsdn-core-fp-common:rfs-dia-plan"
        else:
            return ("/cisco-internet-access-service-fp-internal:internet-access-service-internal/"
                    "/internet-access-service-plan")

    @staticmethod
    def is_lsa_setup():
        with ncs.maapi.single_read_trans("", "system", db=ncs.RUNNING) as th:
            try:
                root = ncs.maagic.get_root(th)
                # If this path exists, it is not LSA
                non_lsa_path = \
                    root.cisco_internet_access_service_fp_internal__internet_access_service_internal
                if non_lsa_path:
                    return False
            except AttributeError:
                return True
