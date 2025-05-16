from hopp.simulation.hopp_interface import HoppInterface
from hopp.simulation.technologies.financial.mhk_cost_model import MHKCostModelInputs
from hopp.utilities import load_yaml
from hopp.utilities.keys import set_nrel_key_dot_env
from copy import deepcopy
import numpy as np
# Set API key
set_nrel_key_dot_env()

def recreate_hopp_config_for_optimization(hopp_config, pv_rating_kw=None, wind_turbine_rating_kw=None, battery_rating_kw=None, battery_rating_kwh=None):

    hopp_config_internal = deepcopy(hopp_config) 
    rating_tol = 50.0
    min_tol = 50.0
    smooth_tol = 1.0
    if pv_rating_kw is not None:

        if pv_rating_kw <= min_tol and wind_turbine_rating_kw <= min_tol:
            hopp_config_internal["technologies"]["pv"]["system_capacity_kw"] = min_tol
        elif pv_rating_kw <= rating_tol:
            if pv_rating_kw <= smooth_tol:
                hopp_config_internal["technologies"].pop("pv")
                hopp_config_internal["site"]["solar"] = False
                hopp_config_internal["site"].pop("solar_resource_file")
                hopp_config_internal["config"]["cost_info"].pop("solar_installed_cost_mw")
                hopp_config_internal["config"]["cost_info"].pop("pv_om_per_kw")
            else:
                pv_rating_kw = np.interp(pv_rating_kw, [smooth_tol, rating_tol], [smooth_tol, 0.1*rating_tol])
        else:
            hopp_config_internal["technologies"]["pv"]["system_capacity_kw"] = pv_rating_kw
    if wind_turbine_rating_kw is not None and "wind" in hopp_config_internal["technologies"]:
        if pv_rating_kw <= min_tol and wind_turbine_rating_kw <= min_tol:
            hopp_config_internal["technologies"]["wind"]["turbine_rating_kw"] = min_tol
        elif wind_turbine_rating_kw <= rating_tol:
            if wind_turbine_rating_kw <= smooth_tol:
                hopp_config_internal["technologies"].pop("wind")
                hopp_config_internal["site"]["wind"] = False
                hopp_config_internal["config"]["cost_info"].pop("wind_installed_cost_mw")
                hopp_config_internal["config"]["cost_info"].pop("wind_om_per_kw")
                hopp_config_internal["config"]["simulation_options"]["wind"]["skip_financial"] = True
            else:
                wind_turbine_rating_kw = np.interp(wind_turbine_rating_kw, [smooth_tol, rating_tol], [smooth_tol, 0.1*rating_tol])
        else:
            hopp_config_internal["technologies"]["wind"]["turbine_rating_kw"] = wind_turbine_rating_kw
    if battery_rating_kw is not None:
        if battery_rating_kw <= rating_tol:
            if battery_rating_kw <= smooth_tol:
                hopp_config_internal["technologies"].pop("battery")
                hopp_config_internal["config"].pop("dispatch_options")
                hopp_config_internal["config"]["cost_info"].pop("storage_installed_cost_mwh")
                hopp_config_internal["config"]["cost_info"].pop("storage_installed_cost_mw")
                hopp_config_internal["config"]["cost_info"].pop("battery_om_per_kw")
            else:
                battery_rating_kw = np.interp(battery_rating_kw, [smooth_tol, rating_tol], [smooth_tol, 0.1*rating_tol])
        else:
            if hopp_config_internal["config"]["cost_info"] and "battery_om_per_kwh" in hopp_config_internal["config"]["cost_info"]:
                batt_om_per_kwh = hopp_config_internal["config"]["cost_info"]["battery_om_per_kwh"]
                batt_om_per_kw = hopp_config_internal["config"]["cost_info"]["battery_om_per_kw"]
                total_batt_om_per_kw = (battery_rating_kw*batt_om_per_kw + battery_rating_kwh*batt_om_per_kwh)/battery_rating_kw
                hopp_config_internal["config"]["cost_info"]["battery_om_per_kw"] = total_batt_om_per_kw

            hopp_config_internal["technologies"]["battery"]["system_capacity_kw"] = battery_rating_kw
        if hopp_config_internal["config"]["cost_info"] and "battery_om_per_kwh" in hopp_config_internal["config"]["cost_info"]:
            hopp_config_internal["config"]["cost_info"].pop("battery_om_per_kwh")
    if battery_rating_kwh is not None and "battery" in hopp_config_internal["technologies"]:
        if battery_rating_kwh <= rating_tol:
            if battery_rating_kwh <= smooth_tol:
                hopp_config_internal["technologies"].pop("battery")
                hopp_config_internal["config"].pop("dispatch_options")
                hopp_config_internal["config"]["cost_info"].pop("storage_installed_cost_mwh")
                hopp_config_internal["config"]["cost_info"].pop("storage_installed_cost_mw")
                hopp_config_internal["config"]["cost_info"].pop("battery_om_per_kw")
            else:
                battery_rating_kwh = np.interp(battery_rating_kwh, [smooth_tol, rating_tol], [smooth_tol, 0.1*rating_tol])
        else:
            hopp_config_internal["technologies"]["battery"]["system_capacity_kwh"] = battery_rating_kwh

    return hopp_config_internal

def run_hopp_model(hopp_config, pv_rating_kw=None, wind_turbine_rating_kw=None, battery_rating_kw=None, battery_rating_kwh=None, verbose=True):

    hopp_config_internal = recreate_hopp_config_for_optimization(hopp_config, pv_rating_kw, wind_turbine_rating_kw, battery_rating_kw, battery_rating_kwh)
    
    hi = HoppInterface(hopp_config_internal)

    hi.simulate(project_life=30)
    hybrid_plant = hi.system

    # Save the outputs
    annual_energies = hybrid_plant.annual_energies

    if verbose:
        print("Annual Energies:")
        print(annual_energies)

        print("LCOE")
        print(hybrid_plant.lcoe_nom)
        print(hybrid_plant.lcoe_real)
        
        print("Total Cost")
        print(hi.print_output())

    
    return hi

if __name__ == "__main__":
    hopp_config = load_yaml("./input-files/plant/hopp_config_wind_solar_battery_baseline.yaml")
    hi1 = run_hopp_model(hopp_config, pv_rating_kw=0.0, battery_rating_kw=0.0, battery_rating_kwh=0.0, wind_turbine_rating_kw=0.0, verbose=False)
    # hi2 = run_hopp_model(hopp_config, pv_rating_kw=3, battery_rating_kw=10, battery_rating_kwh=30, wind_turbine_rating_kw=1500, verbose=False)
    print("aep: ", hi1.system.annual_energies)
    print("schedule_curtailed_percentage: ", hi1.system.grid.schedule_curtailed_percentage)
    print("generation_curtailed: ", sum(hi1.system.grid.generation_curtailed[:8760]))
    print("curtailment_percent: ", hi1.system.grid.curtailment_percent)
    print("generation_profile_pre_curtailment : ", sum(hi1.system.grid.generation_profile_pre_curtailment[:8760]))
    print("generation_profile: ", sum(hi1.system.grid.generation_profile[:8760]))
    print("capacity_factor_at_interconnect: ", (hi1.system.grid.capacity_factor_at_interconnect))
    print("curtailment_ts_kw: ", sum(hi1.system.grid.curtailment_ts_kw[:8760]))
    print("missed_load_percentage: ", (hi1.system.grid.missed_load_percentage))
    

    # generation_curtailed
    # print("2: ", hi2.system.annual_energies)
    # import pdb; pdb.set_trace()
    # 1:  {"pv": 4311.335959899603, "wind": 6275.180227367345, "battery": 3.394572774872447, "hybrid": 10589.910760041843}
    # 2:  {"pv": 4311.335959899603, "wind": 6275.180227367345, "battery": 3.394572774872447, "hybrid": 10589.910760041843}