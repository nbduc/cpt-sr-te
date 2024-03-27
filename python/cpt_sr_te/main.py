# -*- mode: python; python-indent: 4 -*-
import ncs
from . import constants
from . import cpt_sr_te_sr_policy_nano_plan
from . import cpt_sr_te_sr_policy_actions

class Main(ncs.application.Application):
    def setup(self):
        self.log.info("cpt-sr-te RUNNING")

        # SR POLICY NANO PREMOD
        self.register_service(constants.SR_POLICY_SERVICEPOINT, cpt_sr_te_sr_policy_nano_plan.ServiceCallback)

        # SR POLICY EXTERNAL PLAN NANO
        self.register_nano_service(
            constants.SR_POLICY_SERVICEPOINT, "ncs:self", "ncs:init",
            cpt_sr_te_sr_policy_nano_plan.SelfCallback,
        )
        self.register_nano_service(
            constants.SR_POLICY_SERVICEPOINT, "ncs:self", "ncs:ready",
            cpt_sr_te_sr_policy_nano_plan.SelfCallback,
        )
        self.register_nano_service(
            constants.SR_POLICY_SERVICEPOINT, constants.SR_POLICY_COMP_HEADEND, "ncs:init", 
            cpt_sr_te_sr_policy_nano_plan.HeadEndCallback,
        )
        self.register_nano_service(
            constants.SR_POLICY_SERVICEPOINT, constants.SR_POLICY_COMP_HEADEND, constants.SR_POLICY_ST_CONFIG_APPLY,
            cpt_sr_te_sr_policy_nano_plan.HeadEndCallback,
        )
        self.register_nano_service(
            constants.SR_POLICY_SERVICEPOINT, constants.SR_POLICY_COMP_HEADEND, "ncs:ready", 
            cpt_sr_te_sr_policy_nano_plan.HeadEndCallback,
        )

        # CPT SR-TE Actions
        self.register_action(
            "policy-internal-plan-change-handler", 
            cpt_sr_te_sr_policy_actions.InternalPolicyPlanChangeHandler
        )

    def teardown(self):
        self.log.info('Main FINISHED')
