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

    hi = run_hopp_model(
        hopp_config=hybrid_config,
        pv_rating_kw=None,
        wind_turbine_rating_kw=None,
        battery_rating_kw=None,
        battery_rating_kwh=None,
        verbose=False
    )

    hybrid_plant = hi.system

    aeps = hybrid_plant.annual_energies
    npvs = hybrid_plant.net_present_values
    taxes = hybrid_plant.federal_taxes
    apv = hybrid_plant.energy_purchases
    debt = hybrid_plant.debt_payment
    esv = hybrid_plant.energy_sales
    depr = hybrid_plant.federal_depreciation_totals
    insr = hybrid_plant.insurance_expenses
    om = hybrid_plant.om_total_expenses
    rev = hybrid_plant.total_revenues
    tc = hybrid_plant.tax_incentives

    with subtests.test("pv aep"):
        assert aeps.pv == approx(10761987, rel=0.05)
    with subtests.test("wind aep"):    
        assert aeps.wind == approx(31951719, rel=0.05)
    with subtests.test("battery aep"):
        assert aeps.battery == approx(-99103, rel=0.05)
    with subtests.test("hybrid aep"):
        assert aeps.hybrid == approx(43489117, rel=0.05)

    with subtests.test("pv npv"):
        assert npvs.pv == approx(546682.31, rel=5e-2)
    with subtests.test("wind npv"):
        assert npvs.wind == approx(-1385231.71, rel=5e-2)
    with subtests.test("battery npv"):
        assert npvs.battery == approx(-4871034, rel=5e-2)
    with subtests.test("hybrid npv"):
        assert npvs.hybrid == approx(-5664495.73, rel=5e-2)

    with subtests.test("pv taxes"):
        assert taxes.pv[1] == approx(115320.51, rel=5e-2)
    with subtests.test("wind taxes"):
        assert taxes.wind[1] == approx(419276.09, rel=5e-2)
    with subtests.test("battery taxes"):
        assert taxes.battery[1] == approx(248373, rel=5e-2)
    with subtests.test("hybrid taxes"):
        assert taxes.hybrid[1] == approx(783576.67, rel=5e-2)

    with subtests.test("pv apv"):
        assert apv.pv[1] == approx(0, rel=5e-2)
    with subtests.test("wind apv"):
        assert apv.wind[1] == approx(0, rel=5e-2)
    with subtests.test("battery apv"):
        assert apv.battery[1] == approx(-4070354, rel=5e-2)
    with subtests.test("hybrid apv"):
        assert apv.hybrid[1] == approx(-348443, rel=5e-2)

    with subtests.test("pv debt"):
        assert debt.pv[1] == approx(0, rel=5e-2)
    with subtests.test("wind debt"):
        assert debt.wind[1] == approx(0, rel=5e-2)
    with subtests.test("battery debt"):
        assert debt.battery[1] == approx(0, rel=5e-2)
    with subtests.test("hybrid debt"):
        assert debt.hybrid[1] == approx(0, rel=5e-2)

    with subtests.test("pv esv"):
        assert esv.pv[1] == approx(10761987, rel=5e-2)
    with subtests.test("wind esv"):
        assert esv.wind[1] == approx(31951719, rel=5e-2)
    with subtests.test("battery esv"):
        assert esv.battery[1] == approx(3973442, rel=5e-2)
    with subtests.test("hybrid esv"):
        assert esv.hybrid[1] == approx(42058135, rel=5e-2)

    with subtests.test("pv depr"):
        assert depr.pv[1] == approx(875121.61, rel=5e-2)
    with subtests.test("wind depr"):
        assert depr.wind[1] == approx(2651114.55, rel=5e-2)
    with subtests.test("battery depr"):
        assert depr.battery[1] == approx(1266736, rel=5e-2)
    with subtests.test("hybrid depr"):
        assert depr.hybrid[1] == approx(4792972.69, rel=5e-2)

    with subtests.test("pv insr"):
        assert insr.pv[0] == approx(0, rel=5e-2)
    with subtests.test("wind insr"):
        assert insr.wind[0] == approx(0, rel=5e-2)
    with subtests.test("battery insr"):
        assert insr.battery[0] == approx(0, rel=5e-2)
    with subtests.test("hybrid insr"):
        assert insr.hybrid[0] == approx(0, rel=5e-2)

    with subtests.test("pv om"):
        assert om.pv[1] == approx(94991.92, rel=5e-2)
    with subtests.test("wind om"):
        assert om.wind[1] == approx(400000.0, rel=5e-2)
    with subtests.test("battery om"):
        assert om.battery[1] == approx(75000, rel=5e-2)
    with subtests.test("hybrid om"):
        assert om.hybrid[1] == approx(569993, rel=5e-2)

    with subtests.test("pv rev"):
        assert rev.pv[1] == approx(379541, rel=5e-2)
    with subtests.test("wind rev"):
        assert rev.wind[1] == approx(904283, rel=5e-2)
    with subtests.test("battery rev"):
        assert rev.battery[1] == approx(167939, rel=5e-2)
    with subtests.test("hybrid rev"):
        assert rev.hybrid[1] == approx(1334802, rel=5e-2)

    with subtests.test("pv tc"):
        assert tc.pv[1] == approx(322913.40, rel=5e-2)
    with subtests.test("wind tc"):
        assert tc.wind[1] == approx(958551.59, rel=5e-2)
    with subtests.test("battery tc"):
        assert tc.battery[1] == approx(2201850, rel=5e-2)
    with subtests.test("hybrid tc"):
        assert tc.hybrid[1] == approx(3491000.32, rel=5e-2)


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
