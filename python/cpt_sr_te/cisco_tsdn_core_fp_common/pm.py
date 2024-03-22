from cisco_tsdn_core_fp_common import utils as utils
from cisco_tsdn_core_fp_common.cnc_service import CncService
import ncs
import re


class Pm(CncService):
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
        return re.search("pm-internal-plan{(.*) ", path).group(1)

    @staticmethod
    def get_service_key_from_path(path):
        re_search = re.search("pm-internal-plan{(.*?) (.*?)}", path)
        return re_search.group(1), re_search.group(2)

    @staticmethod
    def get_service_kp(profile_service_name):
        return (f"/pm/svc-profiles{{{profile_service_name}}}")

    @staticmethod
    def get_service_xpath(profile_service_name):
        return (f"/pm/svc-profiles[name='{profile_service_name}']")

    @staticmethod
    def get_plan_kp(profile_service_name):
        return (f"/pm/pm-plan{{{profile_service_name}}}")

    @staticmethod
    def get_plan_path():
        return "/pm/pm-plan"

    @staticmethod
    def get_internal_plan_path():
        if Pm.is_lsa_setup():
            return "/cisco-tsdn-core-fp-common:rfs-pm-plan"
        else:
            return "/pm-internal/pm-internal-plan"

    @staticmethod
    def is_lsa_setup():
        with ncs.maapi.single_read_trans("", "system", db=ncs.RUNNING) as th:
            try:
                root = ncs.maagic.get_root(th)
                # If this path exists, it is not LSA
                non_lsa_path = root.cisco_pm_fp_internal__pm_internal
                if non_lsa_path:
                    return False
            except AttributeError:
                return True

    @staticmethod
    def pm_cleanup_attached_svc(self, service_path, th):
        """Delete the attached-pm-svc data of northbound service """
        self.log.info(f"Deleting attached-pm-svc for {service_path}")
        attached_pm_svc_path = "/pm/pm-profiles/attached-pm-svc"
        if th.exists(attached_pm_svc_path):
            attached_pm_svc_node = ncs.maagic.get_node(th, attached_pm_svc_path)
            try:
                for profile_path in attached_pm_svc_node:
                    service_name = str(service_path[-3][0])
                    profile_name = profile_path.profile
                    if service_name in profile_path.services:
                        profile_path.services.remove(service_name)
                        self.log.info(f"deleted {service_name} under {profile_name}")
                    if len(profile_path.services) == 0:
                        delete_path = f'/pm/pm-profiles/attached-pm-svc{{"{profile_name}"}}'
                        th.delete(delete_path)
                        self.log.info(f"deleted {profile_name} from attached-pm-svc")
            except Exception as e:
                self.log.exception(e)
