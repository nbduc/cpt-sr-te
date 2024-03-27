# -*- mode: python; python-indent: 4 -*-
import ncs
from .status_codes.cpt_sr_te_status_codes import StatusCodes
from .status_codes.cpt_sr_te_base_exception import get_status_code_class

def is_lsa_setup():
    with ncs.maapi.single_read_trans("", "system", db=ncs.RUNNING) as th:
        try:
            root = ncs.maagic.get_root(th)
            # If this path exists, it is not LSA
            non_lsa_path = root.cisco_sr_te_cfp_internal__sr_te
            if non_lsa_path:
                return False
        except Exception:
            return True


def save_status_code(error_msg, plan, component, log, device_name):
    # populate plan with status code details
    if "out of sync" in error_msg:
        status_code = StatusCodes[StatusCodes.DEVICE_OUT_OF_SYNC.name]
    elif "connection refused" in error_msg:
        status_code = StatusCodes[StatusCodes.CONNECTION_FAILURE.name]
    else:
        status_code = StatusCodes[StatusCodes.CONFIG_FAILURE.name]

    status_class = get_status_code_class(status_code)
    e = status_class(log, status_code, error_msg)
    e = e.set_context(e.statusCode.reason, error_msg).finish()
    e.save_to_plan(plan, component, device_name)

def get_loopback0_ip_address(device_name, err_log):
    with ncs.maapi.single_read_trans("", "system", db=ncs.RUNNING) as th:
        try:
            root = ncs.maagic.get_root(th)
            device = root.ncs__devices.device[device_name]
            loopback0 = device.config.cisco_ios_xr__interface.Loopback['0']
            loopback0_ipv4_address = loopback0.ipv4.address.ip
            return loopback0_ipv4_address
        except Exception as e:
            err_log(e)