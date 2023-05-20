import pytest
from pathlib import Path

from hopp.sites import SiteInfo
from hopp.mhk_wave_source import MHKWavePlant

data = {
    "lat": 44.6899,
    "lon": 124.1346,
    "year": 2010,
    "tz": -7,
    'no_solar': "True",
    'no_wind': "True"
}

wave_resource_file = Path(__file__).absolute().parent.parent.parent / "resource_files" / "wave" / "Wave_resource_timeseries.csv"
site = SiteInfo(data, wave_resource_file=wave_resource_file)

mhk_config = {
    'device_rating_kw': 286, 
    'num_devices': 100, 
    'wave_power_matrix': [
				[0.000000, 0.500000, 1.500000, 2.500000, 3.500000, 4.500000, 5.500000, 6.500000, 7.500000, 8.500000, 9.500000, 10.500000, 11.500000, 12.500000, 13.500000, 14.500000, 15.500000, 16.500000, 17.500000, 18.500000, 19.500000, 20.500000],
				[0.250000, 0.000000, 0.000000, 0.000000, 0.000000, 0.400000, 0.600000, 0.800000, 1.000000, 1.100000, 1.100000, 1.000000, 0.800000, 0.700000, 0.600000, 0.500000, 0.400000, 0.300000, 0.300000, 0.200000, 0.200000, 0.000000],
				[0.750000, 0.000000, 0.000000, 0.000000, 0.000000, 3.200000, 5.300000, 7.400000, 9.100000, 9.800000, 9.500000, 8.600000, 7.400000, 6.200000, 5.100000, 4.100000, 3.400000, 2.800000, 2.300000, 1.900000, 1.600000, 0.000000],
				[1.250000, 0.000000, 0.000000, 0.000000, 0.000000, 9.000000, 14.800000, 20.500000, 25.000000, 26.800000, 25.900000, 23.300000, 20.000000, 16.800000, 13.800000, 11.300000, 9.200000, 7.600000, 6.300000, 5.200000, 4.300000, 0.000000],
				[1.750000, 0.000000, 0.000000, 0.000000, 0.000000, 17.600000, 28.900000, 39.900000, 48.300000, 51.600000, 49.700000, 44.700000, 38.400000, 32.200000, 26.500000, 21.700000, 17.800000, 14.600000, 12.100000, 10.000000, 8.400000, 0.000000],
				[2.250000, 0.000000, 0.000000, 0.000000, 0.000000, 29.000000, 47.500000, 65.400000, 78.800000, 83.800000, 80.600000, 72.400000, 62.300000, 52.200000, 43.000000, 35.300000, 28.900000, 23.800000, 19.700000, 16.300000, 13.700000, 0.000000],
				[2.750000, 0.000000, 0.000000, 0.000000, 0.000000, 43.200000, 70.700000, 97.000000, 116.300000, 123.100000, 118.100000, 106.100000, 91.300000, 76.500000, 63.200000, 51.900000, 42.500000, 35.000000, 28.900000, 24.100000, 20.100000, 0.000000],
				[3.250000, 0.000000, 0.000000, 0.000000, 0.000000, 60.200000, 98.300000, 134.500000, 160.500000, 169.300000, 162.100000, 145.500000, 125.200000, 105.000000, 86.800000, 71.300000, 58.500000, 48.200000, 39.900000, 33.200000, 27.800000, 0.000000],
				[3.750000, 0.000000, 0.000000, 0.000000, 0.000000, 79.900000, 130.400000, 177.800000, 211.200000, 222.000000, 212.200000, 190.400000, 164.000000, 137.600000, 113.800000, 93.600000, 76.900000, 63.300000, 52.500000, 43.700000, 36.600000, 0.000000],
				[4.250000, 0.000000, 0.000000, 0.000000, 0.000000, 102.400000, 166.700000, 226.700000, 268.300000, 281.100000, 268.200000, 240.500000, 207.200000, 174.100000, 144.100000, 118.500000, 97.400000, 80.300000, 66.600000, 55.500000, 46.500000, 0.000000],
				[4.750000, 0.000000, 0.000000, 0.000000, 0.000000, 127.600000, 207.400000, 281.200000, 286.000000, 286.000000, 286.000000, 286.000000, 255.000000, 214.300000, 177.500000, 146.100000, 120.200000, 99.200000, 82.200000, 68.600000, 57.600000, 0.000000],
				[5.250000, 0.000000, 0.000000, 0.000000, 0.000000, 155.400000, 252.400000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 258.200000, 214.000000, 176.300000, 145.100000, 119.800000, 99.400000, 83.000000, 69.700000, 0.000000],
				[5.750000, 0.000000, 0.000000, 0.000000, 0.000000, 186.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 253.600000, 209.000000, 172.200000, 142.200000, 118.100000, 98.600000, 82.800000, 0.000000],
				[6.250000, 0.000000, 0.000000, 0.000000, 0.000000, 219.200000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 244.200000, 201.200000, 166.400000, 138.200000, 115.500000, 97.100000, 0.000000],
				[6.750000, 0.000000, 0.000000, 0.000000, 0.000000, 255.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 281.900000, 232.400000, 192.200000, 159.700000, 133.500000, 112.300000, 0.000000],
				[7.250000, 0.000000, 0.000000, 0.000000, 0.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 265.600000, 219.800000, 182.800000, 152.900000, 128.700000, 0.000000],
				[7.750000, 0.000000, 0.000000, 0.000000, 0.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 249.000000, 207.200000, 173.400000, 146.000000, 0.000000],
				[8.250000, 0.000000, 0.000000, 0.000000, 0.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 279.900000, 233.000000, 195.100000, 164.400000, 0.000000],
				[8.750000, 0.000000, 0.000000, 0.000000, 0.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 260.200000, 218.000000, 183.800000, 0.000000],
				[9.250000, 0.000000, 0.000000, 0.000000, 0.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 242.100000, 204.100000, 0.000000],
				[9.750000, 0.000000, 0.000000, 0.000000, 0.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 286.000000, 267.400000, 225.600000, 0.000000]
			]
        }

cost_model_inputs = {
	'reference_model_num':3,
	'water_depth': 100,
	'distance_to_shore': 80,
    'number_rows': 10,
	'devices_per_row':10,
	'device_spacing':600,
	'row_spacing': 600,
	'cable_system_overbuild': 20
}


def test_changing_n_devices():
    # test with gridded layout
    model = MHKWavePlant(site = site, mhk_config=mhk_config,cost_model_inputs=cost_model_inputs)
    assert(model.system_capacity_kw == 28600)
    for n in range(1, 20):
        model.number_devices = n
        assert model.number_devices == n, "n turbs should be " + str(n)
        assert model.system_capacity_kw == pytest.approx(28600, 1), "system capacity different when n turbs " + str(n)

def test_changing_device_rating():
    # powercurve scaling
    model = MHKWavePlant(site = site, mhk_config=mhk_config,cost_model_inputs=cost_model_inputs)
    n_devices = model.number_devices
    for n in range(1000, 3000, 150):
        model.device_rated_power = n
        assert model.system_capacity_kw == model.device_rated_power * n_devices, "system size error when rating is " + str(n)

def test_changing_wave_power_matrix():
	model = MHKWavePlant(site = site, mhk_config=mhk_config,cost_model_inputs=cost_model_inputs)
	model.power_matrix = [
	[0, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.5, 20.5],
	[0.25, 0, 0, 0, 0, 4.8, 6.7, 7.9, 9.3, 10.2, 10.1, 9.7, 9, 8.8, 7.6, 7.3, 6.4, 5.6, 5, 4.5, 4, 0],
	[0.75, 0, 0, 0, 0, 12.3, 16.5, 18.8, 21.2, 22.9, 22.2, 20.9, 19.4, 18.7, 16.5, 16, 14.2, 12.8, 11.5, 10.4, 9.4, 0],
	[1.25, 0, 0, 0, 0, 31.8, 40.7, 44.6, 48.5, 51.7, 48.8, 45.1, 41.8, 40.1, 36.2, 35.1, 31.9, 29.2, 26.5, 24.3, 22, 0],
	[1.75, 0, 0, 0, 0, 58.3, 72.3, 77.1, 81.7, 86.5, 80.8, 74, 69.7, 66.7, 59.7, 57.6, 52.7, 48.7, 44.5, 41.1, 37.6, 0],
	[2.25, 0, 0, 0, 0, 91.3, 110.4, 115.7, 119.3, 126.5, 117.3, 107.9, 102, 97.1, 86.4, 82.6, 75.6, 70.5, 64.7, 60.3, 55.3, 0],
	[2.75, 0, 0, 0, 0, 130.5, 154.9, 160, 162.7, 171.7, 158.5, 145.4, 137.5, 130.4, 115.6, 109.7, 101.4, 94.6, 86.6, 80.8, 74, 0],
	[3.25, 0, 0, 0, 0, 174.9, 204.4, 208.9, 210.4, 220.5, 202.7, 185.4, 175.4, 165.9, 148, 140.3, 129.7, 120.5, 110.1, 102.2, 93.4, 0],
	[3.75, 0, 0, 0, 0, 223.9, 258.5, 261.9, 261.6, 272.4, 249.5, 227.7, 215.3, 204.5, 183.2, 173, 159.8, 147.9, 134.8, 124.8, 113.7, 0],
	[4.25, 0, 0, 0, 0, 277.2, 316.8, 318.5, 316, 327, 298.4, 271.6, 257.2, 245.5, 220.2, 207.3, 191.5, 177.1, 161.8, 149.7, 136.8, 0],
	[4.75, 0, 0, 0, 0, 334.5, 360, 360, 360, 360, 349.4, 317.2, 302.2, 288.2, 258.7, 243.1, 225.4, 208.6, 190.3, 176.1, 160.7, 0],
	[5.25, 0, 0, 0, 0, 360, 360, 360, 360, 360, 360, 360, 348.9, 332.4, 298.6, 280.1, 261.3, 241.4, 220, 203.3, 185.2, 0],
	[5.75, 0, 0, 0, 0, 360, 360, 360, 360, 360, 360, 360, 360, 360, 339.7, 319.1, 298.4, 275.5, 250.8, 231.5, 210.7, 0],
	[6.25, 0, 0, 0, 0, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 340.8, 314.3, 285.8, 263.5, 239.7, 0],
	[6.75, 0, 0, 0, 0, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 358.6, 325.8, 300.1, 272.6, 0],
	[7.25, 0, 0, 0, 0, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 341.6, 310.1, 0],
	[7.75, 0, 0, 0, 0, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 352.8, 0],
	[8.25, 0, 0, 0, 0, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 0],
	[8.75, 0, 0, 0, 0, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 0],
	[9.25, 0, 0, 0, 0, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 0],
	[9.75, 0, 0, 0, 0, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 360, 0]
		]
	model.simulate(25)
	assert model.annual_energy_kw == pytest.approx(76319798.5,1)

def test_changing_system_capacity():
    # adjust number of devices, system capacity won't be exactly as requested
    model = MHKWavePlant(site, mhk_config,cost_model_inputs=cost_model_inputs)
    rating = model.device_rated_power
    for n in range(1000, 20000, 1000):
        model.system_capacity_by_num_devices(n)
        assert model.device_rated_power == rating, str(n)
        assert model.system_capacity_kw == rating * round(n/rating)

def test_system_outputs():
	# Test to see if there have been changes to PySAM MhkWave model and it is able to handle 1-hr 
	# Timeseries data. Right now have to divide hourly data outputs by 3 to get the same values
	model = MHKWavePlant(site, mhk_config,cost_model_inputs=cost_model_inputs)
	model.simulate(25)

	assert model.annual_energy_kw == pytest.approx(121325260.0)
	assert model.capacity_factor == pytest.approx(48.42,1)
	assert model.numberHours == pytest.approx(8760)
