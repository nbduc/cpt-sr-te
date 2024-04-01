import ncs
from ncs import ITER_CONTINUE, ITER_RECURSE, ITER_STOP
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
from cisco_tsdn_core_fp_common.diff_iterate_wrapper import DiffIterateWrapper

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

        if op == NCS_SERVICE_UPDATE:
            th = get_trans(root)
            service = get_node(th, kp)

            is_redeploy = self.diff_iterate_redeploy(th, service).is_redeploy

            # Define plan kp
            plan_kp = f"/cpt-sr-te:sr-policy-plan{{{service.name}}}"
            # If not redeploy, detect modified devices/components
            if not is_redeploy:
                updated_devices = []

                # Generate service keypath for tail-end and head-end
                sr_te_policy_kp = "/cisco-sr-te-cfp:sr-te/cisco-sr-te-cfp-sr-policies:" \
                                           f"policies/policy{{CPT-SR-TE-SR-Policy-{service.name}-internal}}"

                # Iterate through diffset for each internal service
                if self.diff_iterate(th, sr_te_policy_kp).updated:
                    updated_devices.append(service.head_end.device)

                # Check updated devices for CQ settings
                device_cq_details = \
                    is_cq_enabled(self, root, updated_devices, th, utils.is_lsa_setup())

                # Update plan
                if th.exists(plan_kp):
                    plan = get_node(th, plan_kp).plan
                    # Update components
                    for device, cq_enabled in device_cq_details:
                        # If device updated and CQ enabled, set ready state to not-reached
                        # for both device component and self
                        if cq_enabled:
                            plan.component[("cpt-sr-te-sr-policy-nano-plan:head-end", device)] \
                                .state["ncs:ready"].status = "not-reached"
                            plan.component[("ncs:self", "self")] \
                                .state["ncs:ready"].status = "not-reached"
                        # If device updated and no CQ, update ready state timestamp
                        # for both device component and self
                        else:
                            update_state_when_timestamp(
                                self, plan.component[("cpt-sr-te-sr-policy-nano-plan:head-end", device)].name,
                                plan.component[("cpt-sr-te-sr-policy-nano-plan:head-end", device)]
                                .state["ncs:ready"], "due to no CQ")
                            update_state_when_timestamp(
                                self, plan.component[("ncs:self", "self")].name,
                                plan.component[("ncs:self", "self")].state["ncs:ready"],
                                "due to no CQ")

    @staticmethod
    def diff_iterate(th, service_kp) -> DiffIterateWrapper:
        def diter(self, keypath, op, oldv, newv):
            if len(keypath) < 5:
                return ITER_RECURSE
            elif len(keypath) >= 5 and str(keypath[-5]) != "private":
                # EX LSA and non LSA site level modification kp:
                self.updated = True
                return ITER_STOP
            return ITER_CONTINUE

        diff_iter = DiffIterateWrapper(diter, updated=False)
        th.keypath_diff_iterate(diff_iter, 0, service_kp)

        return diff_iter

    @staticmethod
    def diff_iterate_redeploy(th, service) -> DiffIterateWrapper:
        def diter(self, keypath, op, oldv, newv):
            # Check if redeploy
            self.is_redeploy = True
            return ITER_CONTINUE

        diff_iter = DiffIterateWrapper(diter, is_redeploy=False)
        redeploy_kp = f"/cpt-sr-te:sr-policy{{{service.name}}}/" \
                               "private/re-deploy-counter"
        th.keypath_diff_iterate(diff_iter, 0, redeploy_kp)

        return diff_iter


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
        state_node = plan.component[component].state[state]

        sr_te_cfp_plan_list = (root.cisco_sr_te_cfp__sr_te
                              .cisco_sr_te_cfp_sr_policies__policies
                              .policy_plan)
        
        # Build sr-te-cfp internal service name
        sr_te_cfp_service_name = f"CPT-SR-TE-SR-Policy-{service.name}-internal"
        self.log.info(sr_te_cfp_service_name)
    
        # Check if sr-te-cfp internal plan is initialized
        if sr_te_cfp_service_name not in sr_te_cfp_plan_list:
            self.log.info(f"cisco-sr-te-cfp policy-plan doesn't exist for {sr_te_cfp_service_name}")
            state_node.status = "not-reached"
            return opaque
        
        # Sync plan status codes from cisco-sr-te-cfp plan
        # if sr_te_cfp_plan_list[sr_te_cfp_service_name].plan.status_code_detail:
        #     update_plan_status_codes(self, root, plan, sr_te_cfp_plan_list, sr_te_cfp_service_name)

        # Sync internal cisco-sr-te-cfp plan endpoint component with external cisco-cs-sr-te-cfp
        # plan endpoint component
        sr_te_cfp_plan = sr_te_cfp_plan_list[sr_te_cfp_service_name].plan
        # for sr_te_cfp_plan_endpoint_component in sr_te_cfp_plan.component:
        #     if not (sr_te_cfp_plan_endpoint_component.name == "self" and
        #             sr_te_cfp_plan_endpoint_component.type == "ncs:self"):
        #         state_node.status = sr_te_cfp_plan_endpoint_component.state["ncs:ready"].status
        #         # Sync component status codes from cisco-sr-te-cfp plan
        #         update_component_status_codes(self, root, sr_te_cfp_plan_list,
        #                                       sr_te_cfp_service_name, plan.component[component],
        #                                       (sr_te_cfp_plan_endpoint_component.type,
        #                                        sr_te_cfp_plan_endpoint_component.name))
        
        # If internal cisco-sr-te-cfp plan failed, mark cpt-sr-te:sr-policy headend component failed
        if sr_te_cfp_plan.failed:
            self.log.debug(f"cisco-sr-te-cfp policy-plan {sr_te_cfp_service_name} failed, marking "
                           f"{component} ready failed")
            state_node.status = "failed"
            plan.failed.create()
            if sr_te_cfp_plan.error_info:
                plan.error_info.create()
                plan.error_info.message = sr_te_cfp_plan.error_info.message

        return opaque