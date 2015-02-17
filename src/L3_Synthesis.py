#!/usr/bin/env pythonimport osimport sysimport Imagefrom numpy import *from scipy.misc import imresizefrom scipy.ndimage.filters import median_filterfrom scipy.ndimage.morphology import *from time import timefrom L3_Borg import Borgfrom L3_Library import stdoutWrite, stdoutWrite, showImage, rectBivariateSplinefrom L3_XmlParser import L3_XmlParserset_printoptions(precision = 7, suppress = True)class L3_Synthesis(Borg):    def __init__(self, config, tables):        self._config = config        self._tables = tables        self._badPixelMask = None        self._goodPixelMask = None        self._aotArr = None        self._szaArr = None        self._sza = None        self.filter =  None        self.LOWEST = 0.000001        self._noData = self.config.classifier['NO_DATA']        self._saturatedDefective = self.config.classifier['SATURATED_DEFECTIVE']        self._darkFeatures = self.config.classifier['DARK_FEATURES']        self._bareSoils = self.config.classifier['BARE_SOILS']        self._snowIce = self.config.classifier['SNOW_ICE']        self._vegetation = self.config.classifier['VEGETATION']        self._water = self.config.classifier['WATER']        self._lowProbaClouds = self.config.classifier['LOW_PROBA_CLOUDS']        self._medProbaClouds = self.config.classifier['MEDIUM_PROBA_CLOUDS']        self._highProbaClouds = self.config.classifier['HIGH_PROBA_CLOUDS']        self._thinCirrus = self.config.classifier['THIN_CIRRUS']        self._cloudShadows = self.config.classifier['CLOUD_SHADOWS']        self.config.logger.debug('Module L3_STP initialized')        self._processingStatus = True        def get_config(self):        return self._config    def get_tables(self):        return self._tables    def set_config(self, value):        self._config = value    def set_tables(self, value):        self._tables = value    def del_config(self):        del self._config    def del_tables(self):        del self._tables    config = property(get_config, set_config, del_config, "config's docstring")    tables = property(get_tables, set_tables, del_tables, "tables's docstring")    def setPixelMasks(self):        scl2A = self.tables.getBand('L2A', self.tables.SCL)        scl03 = self.tables.getBand('L3', self.tables.SCL)        bareSoils = self._bareSoils        vegetation = self._vegetation        water = self._water        cirrus = self._thinCirrus        darkFeatures = self._darkFeatures        cloudShadows = self._cloudShadows        snowIce = self._snowIce                GPM = zeros_like(scl2A)        GPM[(scl2A == bareSoils) | (scl2A == vegetation) | (scl2A == water)] = 1        if self.config.cirrusRemoval == False:            GPM[scl2A == cirrus] = 1        if self.config.shadowRemoval == False:            GPM[(scl2A == darkFeatures) | (scl2A == cloudShadows)] = 1        if  self.config.snowRemoval == False:            GPM[scl2A == snowIce] = 1                nrL03 = scl03.shape[0]        ncL03 = scl03.shape[1]        scl2Ar = imresize(scl2A, (nrL03,ncL03), interp='nearest')        shape = generate_binary_structure(2,1)        GPM = binary_dilation(GPM, shape)                       GPMr = imresize(GPM, (nrL03,ncL03), interp='nearest')              GPMr = median_filter(GPMr,3)        GPMr = clip(GPMr,0,1)        BPMr = ones_like(GPMr)        BPMr -= GPMr        scl03[BPMr > 0] = scl2Ar[BPMr > 0]        self._goodPixelMask = GPMr        self._badPixelMask  = BPMr        self.tables.setBand('L3', self.tables.SCL, scl03)        return    def replaceBadPixels(self, bandIndex):        GPM = self._goodPixelMask        BL2A = self.tables.getBand('L2A', bandIndex)        BL03 = self.tables.getBand('L3', bandIndex)        nrL03 = BL03.shape[0]        ncL03 = BL03.shape[1]        BL2Ar = imresize(BL2A, (nrL03,ncL03), interp='nearest')        BL03[GPM > 0] = BL2Ar[GPM > 0]        if self.config.priority == 'MOST_RECENT':            pass # todo        elif self.config.priority == 'TEMP_HOMOGENEITY':            pass # todo        elif self.config.priority == 'RADIOMETRIC_QUALITY':              pass# todo        self.tables.setBand('L3', bandIndex, BL03)        return        def replaceGoodPixels(self, bandIndex):        BPM = self._badPixelMask        BL2A = self.tables.getBand('L2A', bandIndex)        BL03 = self.tables.getBand('L3', bandIndex)        nrL03 = BL03.shape[0]        ncL03 = BL03.shape[1]        BL2Ar = imresize(BL2A, (nrL03,ncL03), interp='nearest')        BL03[BPM > 0] = BL2Ar[BPM > 0]        self.tables.setBand('L3', bandIndex, BL03)        return    def readSolarZenithAngle(self):        xp = L3_XmlParser(self, 'T2A')        ang = xp.getTree('Geometric_Info', 'Tile_Angles')        sza = float32(ang.Mean_Sun_Angle.ZENITH_ANGLE.text)        sza = absolute(sza)        if sza > 70.0: sza = 70.0        return sza            def preProcessing(self):        self.setPixelMasks()        if self.config.priority == 'MOST_RECENT':            return        elif self.config.priority == 'TEMP_HOMOGENEITY':            return        elif self.config.priority == 'RADIOMETRIC_QUALITY':            self._aotArr = self.tables.getBand('L2', self.tables.AOT)            self._sza = self.readSolarZenithAngle()            return    def forwardProcessing(self):        # this is the default processing routine: it removes clouds and dark features        # from an input image        for i in self.tables.bandIndex:            self.replaceBadPixels(i)        return True    def inverseProcessing(self):        # This is the other way round: it applies clouds and dark features        # to an input image in order to generate suitable test images.        if self.tables.testBand('L2A', 1) == False:            return False        for i in self.tables.bandIndex:            self.replaceGoodPixels(i)        return True    def postProcessing(self):        # ToDo: Implement here ...        if(self._processingStatus == False):            return False        return True        def __exit__(self):        sys.exit(-1)    def __del__(self):        self.config.logger.info('Module L3_Synthesis deleted')            def process(self):        ts = time()        self.config.timestamp('L3_Synthesis Pre-processing    ')        self.preProcessing()        self.config.timestamp('L3_Synthesis Inverse Processing')        self.inverseProcessing()        #self.config.timestamp('L3_Synthesis Process          ')        #self.forwardProcessing()        self.config.timestamp('L3_Synthesis Post-processing   ')        self.postProcessing()        tDelta = time() - ts        self.config.logger.info('Procedure L3_Synthesis overall time [s]: %0.3f' % tDelta)        if(self.config.loglevel == 'DEBUG'):            stdoutWrite('Procedure L3_Synthesis, overall time[s]: %0.3f\n.' % tDelta)        return True