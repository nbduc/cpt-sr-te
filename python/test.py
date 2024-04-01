import ncs
from pprint import pprint

with ncs.maapi.single_read_trans("", "system", db=ncs.RUNNING) as th:
    try:
        root = ncs.maagic.get_root(th)
        # device = root.ncs__devices.device['Node-1']
        # # Check whether loopback0 exists
        # loopback0 = device.config.cisco_ios_xr__interface.Loopback['1']
        # loopback0_ipv4_address = loopback0.ipv4.address.ip
        # print(loopback0_ipv4_address)

        # internal_plan_path = (root.cpt_sr_te__sr_policy_plan["123"].plan.component["cpt-sr-te-sr-policy-nano-plan:head-end", "Node-8"])
        # pprint(internal_plan_path.state)

        internal_plan_path = (
            root.cisco_sr_te_cfp_internal__sr_te.cisco_sr_te_cfp_sr_policies_internal__policies.policy_plan
        )
        service_name = "CPT-SR-TE-SR-Policy-121-internal"
        head_end = "Node-8"
        if (service_name, head_end) not in internal_plan_path:
            pprint(f"Internal plan for {service_name} {head_end} " "doesn't exist")
        else:
            state = (
                internal_plan_path[(service_name, head_end)]
                .plan.component["ncs:self", "self"]
                .state
            )
            for item in state:
                pprint(item.status)

        # internal_plan = internal_plan_path["110", "Node-8"].plan
        # pprint(dir(internal_plan))
        # pprint(internal_plan.service_location)
        # components = internal_plan.component
        # for component in components:
        #     pprint(component)

        # policies = root.cisco_sr_te_cfp_internal__sr_te.cisco_sr_te_cfp_sr_policies_internal__policies.policy
        # policies = ncs.maagic.as_pyval(policies)
        # for policy in policies:
        #     if policy["name"] == "CPT-SR-TE-SR-Policy-109-internal" and \
        #         policy["head_end"] == "Node-8":
        #         pprint(policy)
    except Exception as e:
        print(e)
