from pathlib import Path

import pytest
from pytest import approx, fixture

from hopp.tools.optimization.openmdao.model import run_hopp_model
from hopp.tools.optimization.openmdao.optimization import run_openmdao_problem
from hopp.utilities import load_yaml

from hopp import ROOT_DIR

@fixture
def hybrid_config():
    """Loads the config YAML and updates site info to use resource files."""
    hybrid_config_path = (
        ROOT_DIR.parent / "tests" / "hopp" / "inputs" / "hybrid_run.yaml"
    )
    hybrid_config = load_yaml(hybrid_config_path)

    return hybrid_config

def test_hopp_openmdao_component(hybrid_config, subtests):

    technologies = hybrid_config["technologies"]
    wind_pv_battery = {
        key: technologies[key] for key in ("pv", "wind", "battery", "grid")
    }
    hybrid_config["technologies"] = wind_pv_battery
    hybrid_config["technologies"]["grid"]["ppa_price"] = 0.03
    hybrid_config["config"]["dispatch_options"] = {"battery_dispatch": "load_following_heuristic"}
    hybrid_config["site"]["desired_schedule"] = [5000]*8760
    hi = run_hopp_model(
        hopp_config=hybrid_config,
        pv_rating_kw=5000,
        wind_turbine_rating_kw=2000,
        battery_rating_kw=5000,
        battery_rating_kwh=20000,
        verbose=False
    )

    hybrid_plant = hi.system

    aeps = hybrid_plant.annual_energies

    with subtests.test("pv aep"):
        assert aeps.pv == approx(10763780.074, abs=0.05)
    with subtests.test("wind aep"):    
        assert aeps.wind == approx(31951719.852, abs=0.05)
    with subtests.test("battery aep"):
        assert aeps.battery == approx(117.959, abs=0.05)
    with subtests.test("hybrid aep"):
        assert aeps.hybrid == approx(42715617.886, abs=0.05)


# def test_openmdao(subtests):
#     note = sys.argv[1]
#     load_type = note.split("_")[0]
#     # hopp_config_path = f"./input-files/plant/hopp_config_wind_solar_battery_MN_{load_type}.yaml"
#     hopp_config_path = f"./input-files/plant/hopp_config_wind_solar_battery_baseline_{load_type}.yaml"

#     print(hopp_config_path)

#     hopp_config = load_yaml(hopp_config_path)

#     design_variables = ["pv_capacity_kw", "wind_turbine_rating_kw", "battery_capacity_kw", "battery_capacity_kwh"]

#     constraints = {
#         "battery_duration": {"lower": None, "upper": 10.0, "units": "h", "linear":False},
#         "c2i": {"lower": 0.2, "upper": None, "units": "unitless", "linear":True}, # capacity to interconnect_kw ratio
#         "e2i": {"lower": 0.2, "upper": None, "units": "unitless", "linear":True}, # aep to interconnect_kwh ratio (counts non-zero schedule hours only)
#     }

#     if "ML" in note:
#         constraints["percent_load_missed"] = {"lower": None, "upper": 20, "units": "percent", "linear":False}

#     prob = run_openmdao_problem(hopp_config=hopp_config, mode="optimize", run_once=False, obj="lcoe", optimizer='cobyla', design_variables=design_variables, note=note, constraints=constraints)
