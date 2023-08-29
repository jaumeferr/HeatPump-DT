class Constants(object):

    def __init__(self):
        ### HOUSE ###
        self.LAT = '39.63' #'39.636941'
        self.LON = '2.64'#'2.643352'

        ### NETWORK ###
        self.NETWORK_FLUIDS_LIST = ['R410a', 'water',
                           'Ar', 'N2', 'O2', 'CO2', 'CH4', 'H2']
        self.NETWORK_REFRIG_MASS = 1.20
        self.NETWORK_T_UNIT = 'C'
        self.NETWORK_P_UNIT = 'Pa'
        self.NETWORK_H_UNIT = 'kJ / kg'
        self.NETWORK_M_UNIT = 'kg / s'
        self.NETWORK_V_UNIT = 'l / s'

        ### COMPRESSOR ###
        self.COMP_RATED_OUTPUT = 0.9

        ### HEAT EXCHANGER ###
        # OUT
        self.HE_OUT_HEATING_COP_A7W35 = 3.98
        self.HE_OUT_HEATING_COP_A2W35 = 2.67
        self.HE_OUT_COOLING_EER = 2.32
        self.HE_OUT_SCOP_W35 = 1.95
        self.HE_OUT_SCOP_W55 = 1.30
        self.HE_OUT__T_ANNUAL_CONS_W35 = 2116
        self.HE_OUT_T_ANNUAL_CONS_W55 = 2541
        self.HE_OUT_MAX_INPUT_POWER = 2.59
        self.HE_OUT_FAN_OUTPUT_POWER = 0.04
        self.HE_OUT_INPUT_POWER_A35W7 = 1.67  # cooling
        self.HE_OUT_INPUT_POWER_A7W35 = 1.08  # heating
        self.HE_OUT_INPUT_POWER_A2W35 = 1.35  # heating

        # IN
        self.HE_IN_PRESS_DIFF_COOLING = 9500
        self.HE_IN_PRESS_DIFF_HEATING = 12300

        ### EXPANSION VALVE ###

        ### WATER PUMP ###
        self.WATER_PUMP_POWER = 0.034
        self.WATER_FLOW_RATE_HEATING = 0.238
        self.WATER_FLOW_RATE_COOLING = 0.215
        self.ACTIVE_SYS_MIN_CONS = 0.03

        ### UNITS ###
        self.PRESS_UNIT = 'Pa'
        self.POWER_UNIT = 'kW'
        self.ANNUAL_CONS_UNIT = 'kW / h'
        self.EER_UNIT = 'kcal / W'
        self.COP_UNIT = 'kcal / W'
        self.RATE_UNIT = 'kW'

    def getValues(self):
        return([])

    def parseVFlow(self,value):
        # V flow given from specs as: l / min
        # Converted into: l / min ---> l / s
        return value / 60

    def parsePressure(self,value):
        # P given from specs as: kPa
        # Converted into: kPa ---> Pa
        return value * 1000
