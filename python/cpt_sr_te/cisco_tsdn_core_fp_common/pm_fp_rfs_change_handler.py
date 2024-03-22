# -*- mode: python; python-indent: 4 -*-
import ncs
from . import utils as Utils
from core_fp_common.common_utils import get_local_user
from lsa_utils_pkg.dmap import dm_utils as LsaUtils

from .pm import Pm


def handle_pm_plan(changed_path, rfs_node, log):
    try:
        log.info(f"Update local RFS plan copy for: {changed_path}")

        profile_key = Pm.get_service_key_from_path(changed_path)
        profile_service_name = profile_key[0]
        device = profile_key[1]
        update_pm_template_plan(log, profile_service_name, device, rfs_node)
        log.info(f"Successfully updated local RFS plan copy for: {changed_path}")
    except Exception as e:
        log.exception(e)
        raise e


def update_pm_template_plan(log, profile_service_name, device, rfs_node=None):
    log.info(f"Updating profile plan for service={profile_service_name} device={device}")
    try:
        # Writing with maapi here instead of Cdb APIs because a partial update could be read
        # incorrectly by the service if an external redeploy happens from outside
        # Partial plan could cause issues if written with Cdbsession APIs.
        with ncs.maapi.single_write_trans(get_local_user(), "system", db=ncs.OPERATIONAL) as wr_th:
            wr_root = ncs.maagic.get_root(wr_th)
            # Read live-status data & write to rfs-pm-plan
            if rfs_node is None:
                rfs_live_status = LsaUtils.get_remote_nso_live_status(wr_root, device)
            else:
                rfs_live_status = wr_root.ncs__devices.device[rfs_node].live_status

            local_rfs_plan_path = wr_root.cisco_tsdn_core_fp_common__rfs_pm_plan

            rfs_plan_path = (rfs_live_status.cisco_pm_fp_internal__pm_internal
                             .pm_internal_plan)
            # Remove old rfs plan if exists
            if (profile_service_name, device) in local_rfs_plan_path:
                del local_rfs_plan_path[(profile_service_name, device)]

            # Copy over new plan if exists under live-status
            if (profile_service_name, device) in rfs_plan_path:
                # Copy latest plan over to local copy
                rfs_plan = rfs_plan_path[(profile_service_name, device)].plan
                local_rfs_plan = None
                if (profile_service_name, device) not in local_rfs_plan_path:
                    local_plan_instance = local_rfs_plan_path.create(profile_service_name, device)
                    local_rfs_plan = local_plan_instance.plan
                else:
                    local_rfs_plan = local_rfs_plan_path[(profile_service_name, device)].plan

                internal_zombie_service = []
                internal_zombie_service.append("/pm-internal/device-profiles"
                                               f"[name='{profile_service_name}']"
                                               f"[device='{device}']")

                Utils.copy_rfs_plan_to_local(log, local_rfs_plan, rfs_plan,
                                             internal_zombie_service, rfs_live_status)

            wr_th.apply()
    except Exception as e:
        log.exception(e)
        raise e
