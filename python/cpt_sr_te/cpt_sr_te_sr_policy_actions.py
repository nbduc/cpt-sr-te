import ncs
from ncs import RUNNING, OPERATIONAL
from ncs.maapi import Maapi, single_read_trans
from ncs.maagic import get_root, get_node
import _ncs

# from .cpt_sr_te_sr_policy import SrPolicy
from cisco_tsdn_core_fp_common.utils import (
    check_service_cleanup_flag,
    get_action_timeout,
)
from core_fp_common.common_utils import get_local_user
import re
from . import constants as const


class InternalPolicyPlanChangeHandler(ncs.dp.Action):
    """
    Action handler for Policy internal plan change
    """

    @ncs.dp.Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info(
            f"Internal plan kicker changed for: {input.kicker_id} "
            f"{input.path} {input.tid}"
        )
        _ncs.dp.action_set_timeout(uinfo, get_action_timeout(self, uinfo.username))

        # Grab service name

        with Maapi() as m:
            with m.attach(input.tid, 0) as t:
                t.cd(input.path)
                sr_te_service_name = str(t.getcwd_kpath()[0][0])

        # Extract NB service name from internal service name
        # First check format
        match = re.search(r"\ACPT-SR-TE-SR-Policy-(.*)-internal\Z", sr_te_service_name)
        if not match:
            self.log.info(
                f"SR-TE Policy service {sr_te_service_name} not created by CPT SR-TE."
            )
            return

        # Next extract service name
        try:
            service_name = match.group(1).rsplit("-", 2)[0]
        except Exception:
            self.log.info(
                f"SR-TE Policy service {sr_te_service_name} not created by CPT SR-TE."
            )
            return

        # If cleanup is in progress, do not take any action
        service_kp = const.get_cpt_sr_te_sr_policy_service_kp(service_name)
        if check_service_cleanup_flag(self.log, service_kp, uinfo.username):
            return

        try:
            username = get_local_user()
            # Redeploy zombie if exists
            with single_read_trans(username, "system", db=OPERATIONAL) as th:
                zombie_kp = const.get_cpt_sr_te_sr_policy_zombie_kp(service_name)
                if th.exists(zombie_kp):
                    zombie = get_node(th, zombie_kp)
                    zombie.reactive_re_deploy()
                    self.log.info(
                        f"CPT SR-TE SR Policy Zombie Service Redeploy done for: "
                        f"{service_name}"
                    )
                    return

            # Redeploy service if exists
            with single_read_trans(username, "system", db=RUNNING) as th:
                plan_kp = const.get_cpt_sr_te_sr_policy_plan_kp(service_name)
                if th.exists(plan_kp):
                    if th.exists(service_kp):
                        service = get_node(th, service_kp)
                        service.reactive_re_deploy()
                        self.log.info(
                            f"CPT SR-TE SR Policy Service Redeploy done for: "
                            f"{service_kp}"
                        )

        except Exception as e:
            self.log.exception(
                f"Exception CPTSRTESRPolicyInternalPlanChangeHandler: {e}"
            )

        # policy_wrapper = SrPolicy(input.path, self.log)

        # # If cleanup is in progress, do not take any action
        # if check_service_cleanup_flag(self.log, policy_wrapper.service_kp, uinfo.username):
        #     return

        # try:
        #     policy_wrapper.redeploy()
        # except Exception as e:
        #     self.log.exception(f"Exception CPTSRTESRPolicyInternalPlanChangeHandler: {e}")

        self.log.info(f"Internal plan change handled for {input.path}")
