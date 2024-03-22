import ncs
import _ncs
from core_fp_common import instrumentation
from .status_codes.cpt_sr_te_base_exception import UserErrorException
from .status_codes.cpt_sr_te_status_codes import StatusCodes
from . import utils

import logging

class ServiceCallback(ncs.application.Service):
    @ncs.application.Service.pre_modification
    @instrumentation.instrument_service(logging.INFO, utils.SR_POLICY_SERVICEPOINT)
    def cb_pre_modification(self, tctx, op, kp, root, proplist):
        opaque = dict(proplist)
        opaque["VALIDATION_ERROR"] = ""
        
        self.log.info(f"CPT SR Policy pre_mod external Opaque: {opaque}")
        return list(opaque.items())
    
    @ncs.application.Service.post_modification
    @instrumentation.instrument_service(logging.INFO, utils.SR_POLICY_SERVICEPOINT)
    # update state ("ready" or "not-reached") for device-component and self-component
    def cb_post_modification(self, tctx, op, kp, root, proplist):
        pass

class SelfCallback(ncs.application.NanoService):
    """
    NanoService callback handler for sr-policy plan
    """
    @ncs.application.NanoService.create
    @instrumentation.instrument_nano(logging.INFO, utils.SR_POLICY_SERVICEPOINT)
    def cb_nano_create(self, tctx, root, service, plan,
                       component, state, opaque, comp_vars):
        opaque_dict = dict(opaque)
        if opaque_dict.get("VALIDATION_ERROR") != "":
            return list(opaque_dict.items())
        
        try:
            new_opaque = None

            if state == utils.NCS_READY:
                new_opaque = self._create_ready(tctx, root, service, plan,
                                                component, state, opaque, comp_vars)
            elif state == utils.NCS_INIT:
                new_opaque = self._create_init(tctx, root, service, plan,
                                               component, state, opaque, comp_vars)

            if new_opaque is None:
                return opaque

            return new_opaque

        except Exception as e:
            self.log.exception(e)
            opaque_dict["VALIDATION_ERROR"] = str(e)
            return list(opaque_dict.items())
        
    # Applying kicker for sid-list changes redeploy
    def _create_init(self, _tctx, root, service, plan,
                     component, state, opaque, _comp_vars):
        return opaque
        
    def _create_ready(self, _tctx, _root, _service, plan,
                      component, state, opaque, _comp_vars):
        return opaque

class HeadEndCallback(ncs.application.NanoService):
    """
    NanoService callback handler for sr-policy plan head-end
    """

    @ncs.application.NanoService.create
    @instrumentation.instrument_nano(logging.INFO, utils.SR_POLICY_SERVICEPOINT)
    def cb_nano_create(self, tctx, root, service, plan,
                       component, state, opaque, comp_vars):
        opaque_dict = dict(opaque)
        if opaque_dict.get("VALIDATION_ERROR") != "":
            return list(opaque_dict.items())
        
        try:
            new_opaque = None
            comp_vars = dict(comp_vars)

            if state == utils.SR_POLICY_ST_CONFIG_APPLY:
                new_opaque = self._create_config_apply(tctx, root, service, plan,
                                                       component, state, opaque, comp_vars)
            elif state == utils.NCS_READY:
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
    @instrumentation.instrument_nano(logging.INFO, utils.SR_POLICY_SERVICEPOINT)
    def cb_nano_delete(self, tctx, root, service, plan,
                       component, state, opaque, comp_vars):
        new_opaque = None
        comp_vars = dict(comp_vars)

        if state == utils.NCS_INIT:
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