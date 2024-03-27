import ncs
from ncs.maagic import get_node, get_trans
import _ncs
from _ncs.dp import NCS_SERVICE_CREATE, NCS_SERVICE_UPDATE
from core_fp_common import instrumentation
from .status_codes.cpt_sr_te_base_exception import UserErrorException
from .status_codes.cpt_sr_te_status_codes import StatusCodes
from . import utils, constants
from cisco_tsdn_core_fp_common.utils import validate_service, update_plan_status_codes, \
    update_component_status_codes, remove_status_code_detail, is_cq_enabled, \
    update_state_when_timestamp

import logging

class ServiceCallback(ncs.application.Service):
    @ncs.application.Service.pre_modification
    @instrumentation.instrument_service(logging.INFO, constants.SR_POLICY_SERVICEPOINT)
    def cb_pre_modification(self, tctx, op, kp, root, proplist):
        opaque = dict(proplist)
        opaque["VALIDATION_ERROR"] = ""
        
        self.log.info(f"CPT SR Policy pre_mod external Opaque: {opaque}")
        return list(opaque.items())
    
    @ncs.application.Service.post_modification
    @instrumentation.instrument_service(logging.INFO, constants.SR_POLICY_SERVICEPOINT)
    def cb_post_modification(self, tctx, op, kp, root, proplist):
        #update lai service plan sau khi edit service instance

        # if op == NCS_SERVICE_UPDATE:
        #     th = get_trans(root)
        #     service = get_node(th, kp)

        #     is_redeploy = self.diff_iterate_redeploy(th, service).is_redeploy

        #     # Define plan kp
        #     cs_sr_te_plan_kp = f"/cs-sr-te-plan{{{service.name}}}"

        #     if th.exists
        pass

class SelfCallback(ncs.application.NanoService):
    """
    NanoService callback handler for sr-policy plan
    """
    @ncs.application.NanoService.create
    @instrumentation.instrument_nano(logging.INFO, constants.SR_POLICY_SERVICEPOINT)
    def cb_nano_create(self, tctx, root, service, plan,
                       component, state, opaque, comp_vars):
        opaque_dict = dict(opaque)
        if opaque_dict.get("VALIDATION_ERROR") != "":
            return list(opaque_dict.items())
        
        try:
            new_opaque = None

            if state == "ncs:ready":
                new_opaque = self._create_ready(tctx, root, service, plan,
                                                component, state, opaque, comp_vars)

            if new_opaque is None:
                return opaque

            return new_opaque

        except Exception as e:
            self.log.exception(e)
            opaque_dict["VALIDATION_ERROR"] = str(e)
            return list(opaque_dict.items())
        
    def _create_ready(self, _tctx, root, service, plan,
                      component, state, opaque, _comp_vars):
        state_node = plan.component[component].state[state]
        
        # Build sr-te-cfp internal service name
        internal_service_name = f"CPT-SR-TE-SR-Policy-{service.name}-internal"

        internal_plan_list = (root.cisco_sr_te_cfp__sr_te
                              .cisco_sr_te_cfp_sr_policies__policies
                              .policy_plan)
        
        if internal_plan_list.exists(internal_service_name):
            sr_te_cfp_plan = internal_plan_list[internal_service_name].plan
            self_key = ("ncs:self", "self")
            if (sr_te_cfp_plan.component.exists(self_key) and sr_te_cfp_plan.component[self_key]
                    .state["ncs:ready"].status == "failed") or sr_te_cfp_plan.failed:
                state_node.status = "failed"
                return opaque
            
        for plan_component in plan.component:
            if not (plan_component.name == "self" and plan_component.type == "ncs:self"):
                for plan_state in plan_component.state:
                    if plan_state.status == "failed":
                        self.log.info(f"Component '{plan_component.name}' state '{plan_state.name}'"
                                      " failed, setting self ready state to failed")
                        state_node.status = "failed"
                        return opaque

        for plan_component in plan.component:
            if not (plan_component.name == "self" and plan_component.type == "ncs:self"):
                if plan_component.state["ncs:ready"].status == "not-reached":
                    self.log.info(f"Component '{plan_component.name}' state ncs:ready not-reached, "
                                  "setting self ready state to not-reached")
                    state_node.status = "not-reached"
                    return opaque
                
        return opaque

class HeadEndCallback(ncs.application.NanoService):
    """
    NanoService callback handler for sr-policy plan head-end
    """

    @ncs.application.NanoService.create
    @instrumentation.instrument_nano(logging.INFO, constants.SR_POLICY_SERVICEPOINT)
    def cb_nano_create(self, tctx, root, service, plan,
                       component, state, opaque, comp_vars):
        opaque_dict = dict(opaque)
        if opaque_dict.get("VALIDATION_ERROR") != "":
            return list(opaque_dict.items())
        
        try:
            new_opaque = None
            comp_vars = dict(comp_vars)

            if state == constants.SR_POLICY_ST_CONFIG_APPLY:
                new_opaque = self._create_config_apply(tctx, root, service, plan,
                                                       component, state, opaque, comp_vars)
            elif state == "ncs:ready":
                new_opaque = self._create_ready(tctx, root, service, plan,
                                                component, state, opaque, comp_vars)
            if new_opaque is None:
                return opaque

            return new_opaque
        except Exception as e:
            self.log.exception(e)
            opaque_dict["VALIDATION_ERROR"] = str(e)
            return list(opaque_dict.items())
        
    @ncs.application.NanoService.delete
    @instrumentation.instrument_nano(logging.INFO, constants.SR_POLICY_SERVICEPOINT)
    def cb_nano_delete(self, tctx, root, service, plan,
                       component, state, opaque, comp_vars):
        new_opaque = None
        comp_vars = dict(comp_vars)

        if state == "ncs:init":
            new_opaque = self._delete_init(tctx, root, service, plan,
                                           component, state, opaque, comp_vars)
        if new_opaque is None:
            return opaque

        return new_opaque
    
    def _delete_init(self, _tctx, root, service, plan,
                     component, state, opaque, comp_vars):
        
        return opaque

    def _create_config_apply(self, _tctx, root, service, plan,
                             component, state, opaque, comp_vars):
        # Gather and parse required service config
        comp_vars = dict(comp_vars)
        name = comp_vars["NAME"]
        head_end = comp_vars["HEAD_END"]
        tail_end = utils.get_loopback0_ip_address(service.tail_end, err_log=self.log.error)
        color = str(service.color)

        # Start building template
        template = ncs.template.Template(service)
        variables = ncs.template.Variables()

        # Add color to template variables
        variables.add("NAME", name)
        variables.add("HEAD_END", head_end)
        variables.add("TAIL_END", tail_end)
        variables.add("COLOR", color)

        self.log.info(f"TEMPLATE VARS : {variables}")

        # Apply Service Template
        template.apply("cpt-sr-te-sr-policy-template", variables)

        return opaque
    
    def _create_ready(self, _tctx, root, service, plan,
                      component, state, opaque, comp_vars):
        return opaque