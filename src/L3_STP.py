#!/usr/bin/env pythonimport osimport sysimport L3_UserProductimport L3_Datastripimport L3_Tilefrom numpy import *from scipy.ndimage.morphology import *from scipy.ndimage.interpolation import *from scipy.ndimage.filters import median_filterfrom time import timefrom L3_Borg import Borgfrom L3_Config import L3_Configfrom L3_Library import *from L3_Tables import L3_Tablesfrom L3_XmlParser import L3_XmlParserfrom PIL import *set_printoptions(precision = 7, suppress = True)class L3_STP(Borg):    def __init__(self, config, tables):        self._notClassified = 100        self._config = config        self._tables = tables        x,y = tables.getBandSize('L2A', self.tables.B02)        a = tables.getBand('L2A', self.tables.B02)        self.classificationMask = ones([x,y], uint8) * self._notClassified        self.filter =  None        self.LOWEST = 0.000001        self._noData = self.config.getInt('Scene_Classification/Classificators', 'NO_DATA')        self._saturatedDefective = self.config.getInt('Scene_Classification/Classificators', 'SATURATED_DEFECTIVE')        self._darkFeatures = self.config.getInt('Scene_Classification/Classificators', 'DARK_FEATURES')        self._bareSoils = self.config.getInt('Scene_Classification/Classificators', 'BARE_SOILS')        self._snowIce = self.config.getInt('Scene_Classification/Classificators', 'SNOW_ICE')        self._vegetation = self.config.getInt('Scene_Classification/Classificators', 'VEGETATION')        self._water = self.config.getInt('Scene_Classification/Classificators', 'WATER')        self._lowProbaClouds = self.config.getInt('Scene_Classification/Classificators', 'LOW_PROBA_CLOUDS')        self._medProbaClouds = self.config.getInt('Scene_Classification/Classificators', 'MEDIUM_PROBA_CLOUDS')        self._highProbaClouds = self.config.getInt('Scene_Classification/Classificators', 'HIGH_PROBA_CLOUDS')        self._thinCirrus = self.config.getInt('Scene_Classification/Classificators', 'THIN_CIRRUS')        self._cloudShadows = self.config.getInt('Scene_Classification/Classificators', 'CLOUD_SHADOWS')        self.config.logger.debug('Module L3_STP initialized')        self._processingStatus = True    def assignClassifcation(self, arr, treshold, classification):        cm = self.classificationMask        cm[(arr == treshold) & (cm == self._notClassified)] = classification        self.confidenceMaskCloud[(cm == classification)] = 0        return    def get_config(self):        return self._config    def get_tables(self):        return self._tables    def set_config(self, value):        self._config = value    def set_tables(self, value):        self._tables = value    def del_config(self):        del self._config    def del_tables(self):        del self._tables    config = property(get_config, set_config, del_config, "config's docstring")    tables = property(get_tables, set_tables, del_tables, "tables's docstring")    def preProcess(self):        # ToDo: Implement here ...        if(self._processingStatus == False):            return False        return True    def mainProcess(self):        # ToDo: Implement here ...        if(self._processingStatus == False):            return False        return True    def postProcess(self):        # ToDo: Implement here ...        if(self._processingStatus == False):            return False        return True    def __exit__(self):        sys.exit(-1)    def __del__(self):        self.config.logger.info('Module L3_STP deleted')    '''    def L3_CSND_6(self):        # Step 6: Ratio Band 8 / Band 11 for rocks and sands in deserts        T1_R_B8A_B11 = self.config.getFloat('Scene_Classification/Thresholds', 'T1_R_B8A_B11')        T2_R_B8A_B11 = self.config.getFloat('Scene_Classification/Thresholds', 'T2_R_B8A_B11')        B8A = self.tables.getBand(self.tables.B8A)        B11 = self.tables.getBand(self.tables.B11)        R_B8A_B11 = B8A/maximum(B11,self.LOWEST)        CMC = clip(R_B8A_B11, T1_R_B8A_B11, T2_R_B8A_B11)        CMC = (CMC - T1_R_B8A_B11) / (T2_R_B8A_B11 - T1_R_B8A_B11)        self.assignClassifcation(CMC, 0, self._bareSoils)        self.confidenceMaskCloud *= CMC        self.config.tracer.debug(statistics(self.confidenceMaskCloud, 'CM Cloud step 6'))        return    '''    def process(self):        ts = time.time()        self.config.timestamp('L3_STP Pre-process ')        self.preProcess()        self.config.timestamp('L3_STP Process     ')        self.mainProcess()        self.config.timestamp('L3_STP Post-process')        self.postProcess()        tDelta = time.time() - ts        self.config.logger.info('Procedure L3_STP overall time [s]: %0.3f' % tDelta)        if(self.config.traceLevel == 'DEBUG'):            print 'Procedure L3_STP, overall time[s]: %0.3f' % tDelta        return True