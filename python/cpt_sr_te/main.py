# -*- mode: python; python-indent: 4 -*-
import ncs
from . import utils
from . import cpt_sr_te_sr_policy_nano_plan

class Main(ncs.application.Application):
    def setup(self):
        self.log.info("cpt-sr-te RUNNING")

        # SR POLICY NANO PREMOD
        self.register_service(utils.SR_POLICY_SERVICEPOINT, cpt_sr_te_sr_policy_nano_plan.ServiceCallback)

        # SR POLICY EXTERNAL PLAN NANO
        self.register_nano_service(
            utils.SR_POLICY_SERVICEPOINT, utils.NCS_SELF, utils.NCS_INIT,
            cpt_sr_te_sr_policy_nano_plan.SelfCallback,
        )
        self.register_nano_service(
            utils.SR_POLICY_SERVICEPOINT, utils.NCS_SELF, utils.NCS_READY,
            cpt_sr_te_sr_policy_nano_plan.SelfCallback,
        )
        self.register_nano_service(
            utils.SR_POLICY_SERVICEPOINT, utils.SR_POLICY_COMP_HEADEND, utils.NCS_INIT, 
            cpt_sr_te_sr_policy_nano_plan.HeadEndCallback,
        )
        self.register_nano_service(
            utils.SR_POLICY_SERVICEPOINT, utils.SR_POLICY_COMP_HEADEND, utils.SR_POLICY_ST_CONFIG_APPLY,
            cpt_sr_te_sr_policy_nano_plan.HeadEndCallback,
        )
        self.register_nano_service(
            utils.SR_POLICY_SERVICEPOINT, utils.SR_POLICY_COMP_HEADEND, utils.NCS_READY, 
            cpt_sr_te_sr_policy_nano_plan.HeadEndCallback,
        )

    def teardown(self):
        self.log.info('Main FINISHED')
