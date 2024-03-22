import ncs
import _ncs
from .cpt_sr_te_sr_policy import SrPolicy
from cisco_tsdn_core_fp_common.utils import check_service_cleanup_flag, get_action_timeout

class InternalPolicyPlanChangeHandler(ncs.dp.Action):
    """
    Action handler for Policy internal plan change
    """
     
    @ncs.dp.Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info(f"Internal plan kicker changed for: {input.kicker_id} "
                      f"{input.path} {input.tid}")
        _ncs.dp.action_set_timeout(uinfo, get_action_timeout(self, uinfo.username))

        policy_wrapper = SrPolicy(input.path, self.log)

        # If cleanup is in progress, do not take any action
        if check_service_cleanup_flag(self.log, policy_wrapper.service_kp, uinfo.username):
            return

        try:
            policy_wrapper.redeploy()
        except Exception as e:
            self.log.exception(e)

        self.log.info(f"Internal plan change handled for {input.path}")