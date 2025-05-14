import openmdao.api as om
import numpy as np
import os 
import datetime
from .model import run_hopp_model

class HoppOpenmdao(om.ExplicitComponent):

    def initialize(self):
        self.options.declare(
            "hopp_config",
            types=dict,
            recordable=False,
            desc="HOPP config file",
        )

    def setup(self):
        
        pv_capacity_kw_init = self.options["hopp_config"]["technologies"]["pv"]["system_capacity_kw"]
        self.add_input("pv_capacity_kw", val=pv_capacity_kw_init, units="kW")

        battery_capacity_kw_init = self.options["hopp_config"]["technologies"]["battery"]["system_capacity_kw"]
        self.add_input("battery_capacity_kw", val=battery_capacity_kw_init, units="kW")

        battery_capacity_kwh_init = self.options["hopp_config"]["technologies"]["battery"]["system_capacity_kwh"]
        self.add_input("battery_capacity_kwh", val=battery_capacity_kwh_init, units="kW*h")

        wind_turbine_rating_kw_init = self.options["hopp_config"]["technologies"]["wind"]["turbine_rating_kw"]
        self.add_input("wind_turbine_rating_kw", val=wind_turbine_rating_kw_init, units="kW")

        # self.add_output("profitability_index", val=0.0, units="unitless")
        self.add_output("lcoe", val=0.0, units="USD/(kW*h)")
        self.add_output("percent_load_missed", units="percent", val=0.0)
        self.add_output("curtailment_percent", units="percent", val=0.0)
        self.add_output("aep", units="(kW*h)", val=0.0)
        # self.add_output("pv_batt_mass", val=0.0, units="kg")
        # self.add_output("pv_area", val=0.0, units="m*m")
        # self.add_output("batt_area", val=0.0, units="m*m")

    def setup_partials(self):
        self.declare_partials(['lcoe', 'aep', 'percent_load_missed'], '*', method="fd", form="central", step=1.0)

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        
        hi = run_hopp_model(self.options["hopp_config"], 
                            pv_rating_kw=inputs["pv_capacity_kw"][0], 
                            wind_turbine_rating_kw=inputs["wind_turbine_rating_kw"][0], 
                            battery_rating_kw=inputs["battery_capacity_kw"][0], 
                            battery_rating_kwh=inputs["battery_capacity_kwh"][0], 
                            verbose=False)
        
        # outputs["prifitability_index"] = hi.system.
        outputs["lcoe"] = hi.system.lcoe_nom["hybrid"]*1E-2 # convert from cents/kWh to USD/kWh
        # outputs["lcoe"] = (inputs["pv_capacity_kw"][0] - 2515.0)**2
        
        # outputs["percent_load_missed"] = (inputs["pv_capacity_kw"][0] - 2515.0)**2

        outputs["percent_load_missed"] = hi.system.grid.missed_load_percentage

        # outputs["curtailment_percent"] = hi.system.grid.curtailment_percent
        outputs["curtailment_percent"] = hi.system.grid.schedule_curtailed_percentage
        outputs["aep"] = hi.system.annual_energies.hybrid

        # outputs["pv_batt_mass"] = 0.0
        # outputs["pv_area"] = 0.0
        # outputs["batt_area"] = 0.0

        # if inputs["pv_capacity_kw"] > 0.001:
        #     outputs["pv_batt_mass"] += hi.system.pv.system_mass 
        #     outputs["pv_area"] = hi.system.pv.footprint_area
            
        # if inputs["battery_capacity_kw"] > 0.001 and inputs["battery_capacity_kwh"] > 0.001:
        #     outputs["pv_batt_mass"] += hi.system.battery.system_mass
        #     outputs["batt_area"] = hi.system.battery.footprint_area
    
def setup_openmdao_problem(hopp_config, driver, driver_options, mode, obj="", formatted_date="", optimizer="", design_variables=[], constraints={}, note=""):

    model = om.Group()
    model.add_subsystem("hopp", HoppOpenmdao(hopp_config=hopp_config), promotes=["*"])

    # if "c2i" in constraints.keys():
    c2i_str = "c2i = (0"
    for v in design_variables:
        if "h" not in v:
            if "wind_turbine" in v:
                c2i_str += f" + {v}*{hopp_config['technologies']['wind']['num_turbines']}"
            else:
                c2i_str += f" + {v}"
    c2i_str += f")/{hopp_config['technologies']['grid']['interconnect_kw']}"
    
    model.add_subsystem('c2i_comp', om.ExecComp(c2i_str, c2i={'units': 'unitless'}), promotes=["*"])

    if np.any(["battery" in v for v in design_variables]):
        batt_str = "battery_duration = battery_capacity_kwh/battery_capacity_kw"
        batt_kw = hopp_config['technologies']['battery']['system_capacity_kw']
        batt_kwh = hopp_config['technologies']['battery']['system_capacity_kwh']
        model.add_subsystem("batt_duration_comp", om.ExecComp(batt_str, 
                                                              battery_duration={"val": batt_kwh/batt_kw, "units": "h"},
                                                              battery_capacity_kw={"val": batt_kw, "units": "kW"},
                                                              battery_capacity_kwh={"val": batt_kwh, "units": "kW*h"}), promotes=["*"])

    # if "e2i" in constraints.keys():
    uphours = np.count_nonzero(hopp_config["site"]["desired_schedule"])
    interconnect_kw = hopp_config["technologies"]["grid"]["interconnect_kw"]
    interconnect_kwh = interconnect_kw * uphours
    e2i_str = f"e2i = aep/{interconnect_kwh}"
    model.add_subsystem('e2i_comp', om.ExecComp(e2i_str, 
                                                e2i={'units': 'unitless'},
                                                aep={"units": "kW*h"}), promotes=["aep", "e2i"])


    # model.add_subsystem("hopp", om.ExecComp("lcoe=(pv_capacity_kw - 2510)**2", lcoe={'units': 'USD/(kW*h)'}, pv_capacity_kw={'val':2500, 'units': "kW"}), promotes=["*"])

    # if obj == "lcoe":
        # model.add_constraint("percent_load_missed", units="percent",  upper=20)
        # model.add_constraint("curtailment_percent", units="percent",  upper=20)
    for var in design_variables:
        units = var.split("_")[-1]
        tech = var.split("_")[0]

        units2=list(units)     
        for i, v in enumerate(units):    
            if v == "w":                                  
                units2[i]=units2[i].upper()
            if v == "h":
                units2[i]="*"
                units2.append(v)
        units2 = ''.join(str(i) for i in units2)

        if tech == "wind":
            model.set_input_defaults(var, units=units2, val=hopp_config["technologies"][tech]["turbine_rating_kw"])
        if tech == "pv":
            model.set_input_defaults(var, units=units2, val=hopp_config["technologies"][tech]["system_capacity_kw"])
        if tech == "battery":
            model.set_input_defaults(var, units=units2, val=hopp_config["technologies"][tech][f"system_capacity_{units}"])
        
        if var == "pv_capacity_kw":
            model.add_design_var("pv_capacity_kw", lower=0.0, upper=22000.0, units="kW")#, scaler=1E-2)#, ref=3000)#, ref=3)
            # prob.model.add_constraint("pv_batt_mass", upper=1000.0, units="kg", scaler=1E-5)
            # prob.model.add_constraint("pv_area", upper=20.0, units="m*m", scaler=1E-2)
        if var == "wind_turbine_rating_kw":
            model.add_design_var("wind_turbine_rating_kw", lower=0.0, upper=22000.0, units="kW")#, scaler=1E-1)#, ref=3000)
        if var == "battery_capacity_kw":
            model.add_design_var("battery_capacity_kw", lower=0.0, upper=22000.0, units="kW")#, scaler=1E-4)#, ref=3000)#, scaler=1E-3)
        if var == "battery_capacity_kwh":
            model.add_design_var("battery_capacity_kwh", lower=0.0, upper=22000.0, units="kW*h")#, scaler=1E-4)#, ref=12000)#, scaler=1E-2)
            # prob.model.add_constraint("batt_area", upper=20.0, units="m*m", scaler=1E-2)

    for con in constraints.keys():
        model.add_constraint(con, lower=constraints[con]["lower"], upper=constraints[con]["upper"], units=constraints[con]["units"], linear=constraints[con]["linear"])
        

    if obj == "lcoe":
        model.add_objective("lcoe", units="USD/(MW*h)")#, ref=6)
    elif obj == "percent_load_missed":
        model.add_objective("percent_load_missed", units="percent")#, ref=100)#, ref=0.1)
    else:
        raise(ValueError(f"Invalid objective string provided '{obj}'"))
    
    prob = om.Problem(model=model, driver=driver)

    for key in driver_options.keys():
        prob.driver.opt_settings[key] = driver_options[key]

    # Create a recorder
    
    output_path = f'./output/'
    os.makedirs(output_path, exist_ok=True)
    recorder = om.SqliteRecorder(output_path + f'cases_{mode}_{obj}_{optimizer}_{formatted_date}_{note}.sql')

    # Attach recorder to the problem
    prob.add_recorder(recorder)

    # set variables to include
    includes = list(["lcoe", "percent_load_missed", "curtailment_percent", "c2i", "e2i", "aep", "battery_duration"])

    # Attach recorder to the driver
    prob.driver.add_recorder(recorder)
    prob.driver.recording_options['includes'] = includes
    prob.driver.options['debug_print'] = ['desvars','ln_cons','nl_cons','objs']

    prob.setup()

    return prob

def run_openmdao_problem(hopp_config, mode="optimize", doe_levels=10, run_once=False, obj="", optimizer="", design_variables=[], constraints={}, note=""):

    date_obj = datetime.today()
    formatted_date = date_obj.strftime("%Y%m%d%H%M")

    if mode == "optimize":
        if optimizer == "snopt":
            driver_options = {
                "optimizer": "SNOPT",
                "Verify level": 3,
                "Major optimality tolerance": 1E-6,
                "Print file": f"./output/SNOPT_{obj}_print_{formatted_date}_{note}.out",
                "Summary file": f"./output/SNOPT_{obj}_summary{formatted_date}_{note}.out",
            }
            driver = om.pyOptSparseDriver(optimizer=driver_options.pop("optimizer"))
            if obj == "percent_load_missed":
                driver_options["Major optimality tolerance"] = 5E-5
        elif optimizer == "slsqp":
                driver_options = {}
                driver = om.ScipyOptimizeDriver()
                driver.options['optimizer'] = 'SLSQP'
                driver.options['tol'] = 1e-10
                driver.options['disp'] = True
                driver.options['maxiter'] = 15
                driver_options["Major optimality tolerance"] = 1E-10
                if obj == "percent_load_missed":
                    driver_options["Major optimality tolerance"] = 5E-5
            # elif optimizer == "":
        elif optimizer == "cobyla":
                driver_options = {}
                driver = om.ScipyOptimizeDriver()
                driver.options['optimizer'] = 'COBYLA'
                driver.options['tol'] = 1e-6
                driver.options['maxiter'] = 1500
                driver.options['disp'] = True
                driver.opt_settings['rhobeg'] = 1000
                driver.opt_settings['catol'] = 1E-3
                if obj == "percent_load_missed":
                    driver_options["Major optimality tolerance"] = 5E-5
                else:
                    driver_options["Major optimality tolerance"] = driver.options['tol']

            # elif optimizer == "":
        # elif optimizer == "cobyqa":
        #         driver_options = {}
        #         driver = om.ScipyOptimizeDriver()
        #         driver.options['optimizer'] = 'COBYQA'
        #         driver.options['tol'] = 1e-2
        #         driver.options['maxiter'] = 10
        #         driver.options['disp'] = True
        #         driver.opt_settings['initial_tr_radius'] = 50
        #         if obj == "percent_load_missed":
        #             driver_options["Major optimality tolerance"] = 5E-5
        elif optimizer == "ga":
            # setup the optimization

            prob.driver = om.SimpleGADriver()
            prob.driver.options['max_gen'] = 10
            # prob.driver.options['bits'] = {'length': 8, 'width': 8, 'height': 8}
            # prob.driver.options['penalty_parameter'] = 10.
            prob.driver.options['compute_pareto'] = True
        else:
            raise(ValueError(f"optimizer {optimizer} is not available"))
    elif mode == "doe":
        driver = om.DOEDriver(om.FullFactorialGenerator(levels=doe_levels))
        driver_options = {}
        # prob.driver.options['run_parallel'] = bool(MPI)
        # prob.driver.options['procs_per_model'] = 1

    prob = setup_openmdao_problem(hopp_config, 
                                  driver=driver, 
                                  driver_options=driver_options, 
                                  mode=mode, 
                                  obj=obj, 
                                  formatted_date=formatted_date, 
                                  optimizer=optimizer, 
                                  design_variables=design_variables,
                                  constraints=constraints,
                                  note=note)

    if run_once:
        prob.run_model()
    else:
        prob.run_driver()

    return prob