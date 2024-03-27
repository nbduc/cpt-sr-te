import ncs
from ncs.maapi import Maapi
import _ncs
from .cpt_sr_te_sr_policy import SrPolicy
from cisco_tsdn_core_fp_common.utils import check_service_cleanup_flag, get_action_timeout
import re

class InternalPolicyPlanChangeHandler(ncs.dp.Action):
    """
    Action handler for Policy internal plan change
    """
     
    @ncs.dp.Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info(f"Internal plan kicker changed for: {input.kicker_id} "
                      f"{input.path} {input.tid}")
        _ncs.dp.action_set_timeout(uinfo, get_action_timeout(self, uinfo.username))

        # Grab service name
        # Example: (Extract service_name='CS-STATIC'), input.path =
        # '/cisco-sr-te-cfp:sr-te/cisco-sr-te-cfp-sr-policies:policies/
        #  policy-plan{CS-STATIC-10.0.0.1-internal}'

        with Maapi() as m:
            with m.attach(input.tid, 0) as t:
                t.cd(input.path)
                sr_te_service_name = str(t.getcwd_kpath()[0][0])

        # Extract NB service name from internal service name
        # Ex. (service_name = CS-<service-name>-<endpoint role>-internal)
        # First check format
        match = re.search(r"\ACPT-SR-TE-SR-Policy-(.*)-internal\Z", sr_te_service_name)
        if not match:
            self.log.info(f"SR-TE Policy service {sr_te_service_name} not created by CPT SR-TE.")
            return
        
        policy_wrapper = SrPolicy(input.path, self.log)

        # If cleanup is in progress, do not take any action
        if check_service_cleanup_flag(self.log, policy_wrapper.service_kp, uinfo.username):
            return

        try:
            policy_wrapper.redeploy()
        except Exception as e:
            self.log.exception(f"Exception L3NMInternalPlanChangeHandler: {e}")

        self.log.info(f"Internal plan change handled for {input.path}")