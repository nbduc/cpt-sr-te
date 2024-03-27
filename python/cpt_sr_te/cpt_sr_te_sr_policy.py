from cisco_tsdn_core_fp_common import utils as utils
from cisco_tsdn_core_fp_common.cnc_service import CncService
import ncs
import re

class SrPolicy(CncService):
    def __init__(self, path, log):
        super().__init__(path)
        self.log = log

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
        internal_service_name = re.search("policy-plan{(.*) ", path).group(1)
        if internal_service_name[:20] == "CPT-SR-TE-SR-Policy-" and internal_service_name[-9:] == "-internal":
            # Remove 'CPT-SR-TE-SR-Policy-' and '-internal'
            service_name = internal_service_name[20:-9]
        else:
            # service_name = CPT-SR-TE-SR-Policy-<service-name>-internal
            service_name = internal_service_name
        return service_name
    
    @staticmethod
    def get_service_key_from_path(path):
        re_search = re.search("policy-plan{(.*?) (.*?)}", path)
        internal_service_name = re_search.group(1)
        if internal_service_name[:20] == "CPT-SR-TE-SR-Policy-" and internal_service_name[-9:] == "-internal":
            # Remove 'CPT-SR-TE-SR-Policy-' and '-internal'
            service_name = internal_service_name[20:-9]
        else:
            # service_name = CPT-SR-TE-SR-Policy-<service-name>-internal
            service_name = internal_service_name
        return service_name, re_search.group(2)

    @staticmethod
    def get_service_kp(service_name):
        return f"/cpt-sr-te:sr-policy{{{service_name}}}"

    @staticmethod
    def get_service_xpath(policy_service_name):
        return (f"/cpt-sr-te:sr-policy[name='{policy_service_name}']")

    @staticmethod
    def get_plan_kp(policy_service_name):
        return (f"/cpt-sr-te:sr-policy-plan{{{policy_service_name}}}")

    @staticmethod
    def get_plan_path():
        return "/cpt-sr-te:sr-policy-plan"

    @staticmethod
    def get_internal_plan_path():
        if SrPolicy.is_lsa_setup():
            return "/cisco-tsdn-core-fp-common:rfs-policy-plan"
        else:
            return (
                "/cisco-sr-te-cfp-internal:sr-te/cisco-sr-te-cfp-sr-policies-internal:policies"
                "/cisco-sr-te-cfp-sr-policies-internal:policy-plan"
            )

    @staticmethod
    def is_lsa_setup():
        with ncs.maapi.single_read_trans("", "system", db=ncs.RUNNING) as th:
            try:
                root = ncs.maagic.get_root(th)
                # If this path exists, it is not LSA
                non_lsa_path = root.cisco_sr_te_cfp__sr_te
                if non_lsa_path:
                    return False
            except AttributeError:
                return True