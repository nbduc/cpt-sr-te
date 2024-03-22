from .internet_access_service import InternetAccessService
from .utils import copy_rfs_plan_to_local
from ncs import maapi, maagic, OPERATIONAL
from core_fp_common.common_utils import get_local_user
from lsa_utils_pkg.dmap.dm_utils import get_remote_nso_live_status


def handle_dia_plan(changed_path, rfs_node, log):
    # Plan Update
    try:
        log.info(f"Update local RFS plan copy for: {changed_path}")

        # Grab service name
        service_name = InternetAccessService.get_service_name_from_path(changed_path)

        # Update plan
        update_dia_plan(log, service_name, rfs_node)
        log.info(f"Successfully updated local RFS plan copy for: {changed_path}")
    except Exception as e:
        log.exception(e)
        raise e


def update_dia_plan(log, service_name, rfs_node=None):
    log.info(f"Updating internet access service plan for service={service_name}")
    try:
        # Writing with maapi here instead of Cdb APIs because a partial update could be read
        # incorrectly by the service if an external redeploy happens from outside
        # Partial plan could cause issues if written with Cdbsession APIs.

        with maapi.single_write_trans(get_local_user(), "system", db=OPERATIONAL) as th:
            root = maagic.get_root(th)
            if rfs_node is None:
                plan = root.cisco_internet_access_service_fp__internet_access_services.\
                    internet_access_service_plan[service_name].plan
                device = plan.\
                    component["ncs:self"].private.property_list.property["DEVICE"].value

                rfs_live_status = get_remote_nso_live_status(root, device)
            else:
                # Read live-status data & write to rfs-dia-plan
                rfs_live_status = root.ncs__devices.device[rfs_node].live_status

            local_rfs_plan_path = root.cisco_tsdn_core_fp_common__rfs_dia_plan
            rfs_plan_path = rfs_live_status.\
                cisco_internet_access_service_fp_internal__internet_access_service_internal.\
                internet_access_service_plan
            # Remove old rfs plan if exists
            if service_name in local_rfs_plan_path:
                del local_rfs_plan_path[service_name]
            # Copy over new plan if exists under live-status
            if service_name in rfs_plan_path:
                # Copy latest plan over to local copy
                rfs_plan = rfs_plan_path[service_name].plan
                if service_name not in local_rfs_plan_path:
                    local_plan_instance = local_rfs_plan_path.create(service_name)
                    local_rfs_plan = local_plan_instance.plan
                else:
                    local_rfs_plan = local_rfs_plan_path[service_name].plan
                # Define zombie paths
                internal_zombie_services = ["/internet-access-service-internal/"
                                            f"internet-access-service[name='{service_name}']"]
                copy_rfs_plan_to_local(log, local_rfs_plan, rfs_plan,
                                       internal_zombie_services, rfs_live_status)

            th.apply()
    except Exception as e:
        log.exception(e)
        raise e
