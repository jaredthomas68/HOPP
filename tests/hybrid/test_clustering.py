import pytest
from pytest import approx
import hybrid.clustering as clustering
import numpy as np
import pandas as pd
import copy
import csv


def parse_price_data(price_data_file=None):
    price_data = []
    if price_data_file is not None:
        with open(price_data_file) as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                price_data.append(float(row[0]))
    else:
        np.random.seed(0)
        for i in range(int(8)):
            price_data.extend([np.random.rand()]*3)
        P_day = copy.deepcopy(price_data)
        for i in range(364):
            price_data.extend(P_day)
        price_data = [x/10. for x in price_data]  # [$/kWh]
    return price_data

def parse_wind_file(filename):
    """Outputs a numpy array of wind speeds"""
    df = pd.read_csv(filename, sep=',', skiprows=4, header=0)
    df.columns = ['Temperature', 'Pressure', 'Speed', 'Direction']
    return df['Speed'].to_numpy()


def test_minimum_specification():
    clusterer = clustering.Clustering(
        power_sources=['tower'],
        solar_resource_file="resource_files/solar/35.2018863_-101.945027_psmv3_60_2012.csv")
    clusterer.run_clustering()
    n_clusters = len(clusterer.clusters['count'])
    assert n_clusters == 20
    assert clusterer.get_sim_start_end_times(0) == (864, 960)
    assert clusterer.get_sim_start_end_times(n_clusters - 1) == (8496, 8592)
    assert list(clusterer.clusters['exemplars']) == \
        [18,  21,  23,  29,  34,  42,  64,  69,  96, 107, 111, 118, 131, 134, 139, 147, 164, 172, 175, 177]


def test_alternate_solar_file():
    clusterer = clustering.Clustering(
        power_sources=['tower'],
        solar_resource_file="resource_files/solar/daggett_ca_34.865371_-116.783023_psmv3_60_tmy.csv")
    clusterer.run_clustering()
    n_clusters = len(clusterer.clusters['count'])
    assert n_clusters == 20
    assert clusterer.get_sim_start_end_times(0) == (48, 144)
    assert clusterer.get_sim_start_end_times(n_clusters - 1) == (8016, 8112)
    assert list(clusterer.clusters['exemplars']) == \
        [1, 5, 6, 15, 19, 23, 39, 78, 89, 95, 102, 124, 131, 136, 139, 143, 158, 162, 164, 167]


def test_hybrid():
    clusterer = clustering.Clustering(
        power_sources=['trough', 'pv', 'battery'],
        solar_resource_file="resource_files/solar/daggett_ca_34.865371_-116.783023_psmv3_60_tmy.csv")
    clusterer.run_clustering()
    n_clusters = len(clusterer.clusters['count'])
    assert n_clusters == 19
    assert clusterer.get_sim_start_end_times(0) == (48, 144)
    assert clusterer.get_sim_start_end_times(n_clusters - 1) == (8016, 8112)
    assert list(clusterer.clusters['exemplars']) == \
        [1, 2, 23, 27, 34, 39, 57, 58, 89, 95, 102, 124, 131, 147, 155, 158, 163, 164, 167]


def test_too_high_clusters():
    clusterer = clustering.Clustering(
        power_sources=['tower'],
        solar_resource_file="resource_files/solar/35.2018863_-101.945027_psmv3_60_2012.csv")
    clusterer.n_cluster = 1000                              # make unachievably high
    clusterer.run_clustering()
    n_clusters = len(clusterer.clusters['count'])
    assert n_clusters == 181
    assert clusterer.get_sim_start_end_times(0) == (0, 96)
    assert clusterer.get_sim_start_end_times(n_clusters - 1) == (8640, 8736)


def test_various_simulation_days():
    clusterer = clustering.Clustering(
        power_sources=['tower'],
        solar_resource_file="resource_files/solar/35.2018863_-101.945027_psmv3_60_2012.csv")

    clusterer.ndays = 1
    clusterer.run_clustering()
    n_clusters = len(clusterer.clusters['count'])
    assert n_clusters == 20
    assert clusterer.get_sim_start_end_times(0) == (72, 144)
    assert clusterer.get_sim_start_end_times(n_clusters - 1) == (8688, 8760)
    assert list(clusterer.clusters['exemplars']) == \
        [3, 7, 8, 23, 42, 65, 84, 117, 126, 190, 237, 254, 259, 281, 282, 294, 306, 310, 333, 362]

    clusterer.ndays = 3
    clusterer.run_clustering()
    n_clusters = len(clusterer.clusters['count'])
    assert n_clusters == 20
    assert clusterer.get_sim_start_end_times(0) == (0, 120)
    assert clusterer.get_sim_start_end_times(n_clusters - 1) == (8424, 8544)
    assert list(clusterer.clusters['exemplars']) == \
        [0, 7, 15, 26, 27, 42, 43, 63, 73, 74, 75, 77, 78, 80, 84, 89, 103, 107, 112, 117]


def test_custom_weights_and_divisions():
    clusterer = clustering.Clustering(
        power_sources=['tower'],
        solar_resource_file="resource_files/solar/35.2018863_-101.945027_psmv3_60_2012.csv")
    clusterer.use_default_weights = True
    clusterer.run_clustering()
    n_clusters = len(clusterer.clusters['count'])
    sim_start_end_times_first = clusterer.get_sim_start_end_times(0)
    sim_start_end_times_last = clusterer.get_sim_start_end_times(n_clusters - 1)
    exemplars = list(clusterer.clusters['exemplars'])
    weights, divisions, bounds = clusterer.get_default_weights()

    # Reinstantiate clusterer object
    clusterer = clustering.Clustering(
        power_sources=['tower'],
        solar_resource_file="resource_files/solar/35.2018863_-101.945027_psmv3_60_2012.csv")
    clusterer.use_default_weights = False
    clusterer.weights = weights
    clusterer.divisions = divisions
    clusterer.bounds = bounds
    clusterer.run_clustering()
    assert len(clusterer.clusters['count']) == n_clusters
    assert clusterer.get_sim_start_end_times(0) == sim_start_end_times_first
    assert clusterer.get_sim_start_end_times(n_clusters - 1) == sim_start_end_times_last
    assert list(clusterer.clusters['exemplars']) == exemplars


def test_initial_state_heuristics():
    # Battery heuristics
    clusterer = clustering.Clustering(
        power_sources=['tower', 'pv', 'battery'],
        solar_resource_file="resource_files/solar/35.2018863_-101.945027_psmv3_60_2012.csv")
    clusterer.run_clustering()
    n_clusters = len(clusterer.clusters['count'])
    cluster_id = 0
    assert clusterer.battery_soc_heuristic(clusterid=cluster_id) == 20
    assert clusterer.battery_soc_heuristic(clusterid=n_clusters-1) == 20
    initial_battery_states = {
        'day': [clusterer.sim_start_days[cluster_id] - 4, clusterer.sim_start_days[cluster_id] - 3],
        'soc': [0, 100],             # state-of-charge [%]
    }
    # Note: sim_start_days has the day of the year (Jan. 1 = 0) of the first 'production' day in each exemplar group, not the 'previous' day.
    #  The initial state given by the heuristic is for the beginning of the 'previous' day.
    #  Therefore, if you want to get the initial state for the cluster ID corresponding to days 2-5 (production days 3 and 4),
    #   the closest states you can provide are for (the beginning of) days 0 and 1, as the calculated initial state would be for
    #   the beginning of day 2, the 'previous' day.
    assert clusterer.battery_soc_heuristic(clusterid=cluster_id, initial_states=initial_battery_states) == approx(98.18, rel=1e-3)

    # CSP heuristics
    clusterer = clustering.Clustering(
        power_sources=['tower', 'pv', 'battery'],
        solar_resource_file="resource_files/solar/35.2018863_-101.945027_psmv3_60_2012.csv")
    clusterer.run_clustering()
    n_clusters = len(clusterer.clusters['count'])
    cluster_id = 0
    assert clusterer.csp_initial_state_heuristic(clusterid=cluster_id) == (10, False, 0.)    # == (initial_soc, is_cycle_on, initial_cycle_load)
    assert clusterer.csp_initial_state_heuristic(clusterid=n_clusters-1) == (10, False, 0.)
    initial_csp_states = {
        'day': [clusterer.sim_start_days[cluster_id] - 4, clusterer.sim_start_days[cluster_id] - 3],
        'soc': [20, 89],              # state-of-charge [%]
        'load': [0, 0],                 # power cycle load [%]
    }
    assert clusterer.csp_initial_state_heuristic(clusterid=cluster_id, solar_multiple=3, initial_states=initial_csp_states) == \
        (approx(89., 1e-3), False, 0.)   # == (initial_soc, is_cycle_on, initial_cycle_load)


def test_price_parameter():
    clusterer = clustering.Clustering(
        power_sources=['tower'],
        solar_resource_file="resource_files/solar/35.2018863_-101.945027_psmv3_60_2012.csv",
        price_data=parse_price_data("resource_files/grid/pricing-data-2015-IronMtn-002_factors.csv"))
    clusterer.run_clustering()
    n_clusters = len(clusterer.clusters['count'])
    assert n_clusters == 20
    assert clusterer.get_sim_start_end_times(0) == (960, 1056)
    assert clusterer.get_sim_start_end_times(n_clusters - 1) == (8496, 8592)
    assert list(clusterer.clusters['exemplars']) == \
        [20, 21, 22, 29, 34, 42, 62, 69, 95, 96, 110, 111, 120, 131, 138, 139, 151, 164, 166, 177]


def test_wind_defaults():
    clusterer = clustering.Clustering(
        power_sources=['wind'],
        solar_resource_file="resource_files/solar/35.2018863_-101.945027_psmv3_60_2012.csv")
    clusterer.run_clustering()
    n_clusters = len(clusterer.clusters['count'])
    assert n_clusters == 20
    assert clusterer.get_sim_start_end_times(0) == (240, 336)
    assert clusterer.get_sim_start_end_times(n_clusters - 1) == (7920, 8016)
    assert list(clusterer.clusters['exemplars']) == \
        [5, 6, 7, 10, 28, 32, 41, 52, 57, 72, 86, 90, 108, 111, 121, 126, 131, 134, 154, 165]


def test_wind_resource_parameter():
    clusterer = clustering.Clustering(
        power_sources=['wind'],
        solar_resource_file="resource_files/solar/35.2018863_-101.945027_psmv3_60_2012.csv",
        wind_resource_data=parse_wind_file("resource_files/wind/35.2018863_-101.945027_windtoolkit_2012_60min_100m.srw"))
    clusterer.run_clustering()
    n_clusters = len(clusterer.clusters['count'])
    assert n_clusters == 20
    assert clusterer.get_sim_start_end_times(0) == (336, 432)
    assert clusterer.get_sim_start_end_times(n_clusters - 1) == (8640, 8736)
    assert list(clusterer.clusters['exemplars']) == \
        [7, 38, 41, 54, 55, 58, 61, 86, 95, 116, 125, 138, 146, 154, 158, 159, 162, 174, 175, 180]


def test_annual_array_from_cluster_exemplars():
    # Output data gotten from SSC runs for the respective exemplar groups (each with 2 production days)
    # Note: day 0 = Jan 1
    cluster_model_output = []
    with open('tests/hybrid/clustering_exemplar_output.csv') as file:
        reader = csv.reader(file, quoting=csv.QUOTE_NONNUMERIC)
        for row in reader:
            cluster_model_output += row

    clusterer = clustering.Clustering(
        power_sources=['tower'],
        solar_resource_file="resource_files/solar/daggett_ca_34.865371_-116.783023_psmv3_60_tmy.csv")
    clusterer.ndays = 2
    clusterer.run_clustering()
    annual_output_from_clusters = clusterer.compute_annual_array_from_cluster_exemplar_data(cluster_model_output)
    assert hash(tuple(annual_output_from_clusters)) == 6434885153350809457
    
    write_output_to_file = False
    if write_output_to_file == True:
        annual_output_per_day = np.array_split(annual_output_from_clusters, 365)
        annual_output_per_day = [list(array) for array in annual_output_per_day]
        with open('tests/hybrid/clustering_annual_output.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(annual_output_per_day)


def test_cluster_avgs_from_timeseries():
    # Output data gotten from SSC runs for the respective exemplar groups (each with 2 production days)
    # Note: day 0 = Jan 1
    cluster_model_output = []
    with open('tests/hybrid/clustering_exemplar_output.csv') as file:
        reader = csv.reader(file, quoting=csv.QUOTE_NONNUMERIC)
        for row in reader:
            cluster_model_output += row

    clusterer = clustering.Clustering(
        power_sources=['tower'],
        solar_resource_file="resource_files/solar/daggett_ca_34.865371_-116.783023_psmv3_60_tmy.csv")
    clusterer.ndays = 2
    clusterer.run_clustering()
    annual_output_from_clusters = clusterer.compute_annual_array_from_cluster_exemplar_data(cluster_model_output)
    cluster_averages = clusterer.compute_cluster_avg_from_timeseries(annual_output_from_clusters)
    assert len(cluster_averages) == len(clusterer.clusters['count'])
    list_lengths = [len(list_) for list_ in cluster_averages]
    assert min(list_lengths) == (1 + clusterer.ndays + 1) * 24 * int(len(annual_output_from_clusters) / 8760)
    assert max(list_lengths) == min(list_lengths)
    assert sum(cluster_averages[0]) == approx(1368000, 1e-3)
    assert sum(cluster_averages[-1]) == approx(3071000, 1e-3)