__author__ = 'harold'
from PyQt4 import QtCore, QtGui, uic
from myGenSettingsDlg import *
import os




class Project :
    """ Project.py
    Class containing utilities to get the image base from a input file name and to return a filename
    based upon the image base
    """






    def __init__(self):
        self.ubFlag = False
        self.calFlag = False
        self.projFile = ''
        self.ubFile = ''
        self.calFile = ''
        self.settingsArray = [0.,0.,0.,0.,0.,0.,0]
        self.filenum = 0
        self.curimage = QtCore.QString('')
        self.projFlag = False
        self.numDigits = 3
        self.imFile =''
        self.omega0 = 0
        self.omegaR = 15
        self.expos = 10.
        self.chi = 0.
        self.detector = 0.
        self.base = ""
        self.h5Flag = False
        self.minImageNum =1E9
        self.maxImageNum =-1E9
        self.numImages = 0

    def getImageBase (self, filename) :
        """
        getImageBase returns the prefix which will be used for subsequent file naming based upon
        an input filename
        :param filename:
        :return:
        """
        self.imFile = filename
        ind_of_suffx = filename.lastIndexOf ('.')
        ind_of_start_num = filename.lastIndexOf ('_') +1
        extension = os.path.splitext(filename.toLatin1().data())[1]
        if "h5" in extension :
            self.h5Flag = True
        else :
            self.h5Flag = False

        newbase = filename.left(ind_of_start_num)
        if not self.h5Flag :
            imstringFilt = '*.tif'%newbase
        else :
            imstringFilt = '*.h5'%newbase
        curimage = filename
        self.filenum = self.getFileNumber (filename)
        #print 'Debug : %s'%self.filenum
        qfinfo = QtCore.QFileInfo (filename)
        apath = qfinfo.absolutePath()
        fileonly = qfinfo.fileName ()
        tmpind = fileonly.lastIndexOf('_')+1
        tmpbase = fileonly.left(tmpind)
        qd = QtCore.QDir (apath)
        qd.setNameFilters (QtCore.QStringList()<<imstringFilt)
        imfiles = qd.entryList()
        n = imfiles.count()
        self.minImageNum = 1E10
        self.maxImageNum = -1
        for i in imfiles :
            if (i.contains(tmpbase) == False) :
                continue
            startInd = i.lastIndexOf ('_')+1
            endInd = i.lastIndexOf ('.')
            self.numDigits = endInd - startInd
            num = i.mid(startInd, self.numDigits).toInt()[0]
            print num, '   ',i
            if (num < self.minImageNum) :
                self.minImageNum = num
            if (num > self.maxImageNum) :
                self.maxImageNum = num
        print 'min image : ', self.minImageNum
        print 'max image : ', self.maxImageNum
        self.numImages = self.maxImageNum - self.minImageNum + 1
        print 'num images : ',self.numImages
        if (self.base != newbase) :
            self.base = QtCore.QString (newbase)
            self.checkForFiles()

        else :
            setfile = filename+'.txt'
            qf = QtCore.QFile (setfile)
            if (qf.exists()) :
                self.readFileSettings (setfile)
        return self.base

    def getFileNameFromNum (self, number) :
        if self.h5Flag :
            tempfile = QtCore.QString('%1%2.h5').arg(self.base).arg(int(number), self.numDigits, 10, QtCore.QChar('0'))
        else :
            tempfile = QtCore.QString('%1%2.tif').arg(self.base).arg(int(number), self.numDigits, 10, QtCore.QChar('0'))
        self.filenum = number
        #print 'debug :', tempfile
        return tempfile

    def getFileNumber (self, filename) :
        ind_of_suffix = filename.lastIndexOf ('.')
        ind_of_start_num = filename.lastIndexOf ('_') +1
        self.numDigits = ind_of_suffix - ind_of_start_num
        left = filename.mid (ind_of_start_num, self.numDigits)
        self.filenum = left.toInt()[0]
        #print "Debug : %d" % self.filenum
        return self.filenum

    def checkForFiles (self) :
        self.prjFile = QtCore.QString ('%1_projset.txt').arg (self.base)
        self.ubFile = QtCore.QString ('%1_ub.txt').arg (self.base)
        cFile = QtCore.QString ('%1.cal').arg (self.base)
        qfil = QtCore.QFile (self.prjFile)
        if (qfil.exists()==False) :
            print 'Debug : project settings file does not exist'
            self.projFlag = False
        else :
            self.projFlag = True
        print 'Project settings flag is : %r'%self.projFlag
        qfil = QtCore.QFile (self.ubFile)
        if (qfil.exists()==False) :
            print 'Debug : ub file does not exist'
            self.ubFlag = False
        else :
            self.ubFlag = True
        print 'UB flag is : %r'%self.ubFlag

        qfil = QtCore.QFile (cFile)

        if (qfil.exists()):
            self.calFile = cFile
            self.calFlag = True
        else :
            self.calFlag = False


        imsettingsFile = QtCore.QString ('%1.txt').arg (self.imFile)
        qfil = QtCore.QFile (imsettingsFile)
        if (qfil.exists()==False) :
            gsdlg = myGenSettingsDlg ()
            gsdlg.setInitialVals (0., 15., self.minImageNum, self.maxImageNum-self.minImageNum + 1, 5., 3., 10.)
            gsdlg.setArr (self.settingsArray)
            gsdlg.exec_()
            if (gsdlg.status > 0) :
                self.writeSettingsFiles()
            print self.settingsArray
            self.omega0 = self.settingsArray[0]
            self.omegaR = self.settingsArray[1]
            self.chi = self.settingsArray[4]
            self.detector = self.settingsArray[5]
            self.expos = self.settingsArray[6]

        else :
            qfil.close()
            self.readFileSettings(imsettingsFile)

    def readFileSettings (self, fname) :
        f = open (fname, 'r')
        str = f.readline()
        a = str.split('=')
        self.omega0 = float(a[1])
        str = f.readline()
        a = str.split('=')
        self.omegaR = float(a[1])
        str = f.readline()
        a = str.split('=')
        self.chi = float(a[1])
        str = f.readline()
        a = str.split('=')
        self.detector = float(a[1])
        str = f.readline()
        a = str.split('=')
        self.expos = float(a[1])
        f.close()


    def writeSettingsFiles (self) :
        z = QtCore.QChar ('0')
        for i in range (self.minImageNum, self.maxImageNum+1) :
            filename = QtCore.QString("%1%2.tif.txt").arg(self.base).arg(i, self.numDigits, 10, z)
            outfil = file (filename.toLatin1().data(), 'w')
            om0 = self.settingsArray [0] + (i - self.minImageNum) * self.settingsArray[1]
            str = 'OMEGA0 = %f\r\n'%om0
            outfil.write (str)
            om1 = self.settingsArray[1]
            str = 'OMEGAR = %f\r\n'%om1
            outfil.write (str)
            expos = self.settingsArray[6]
            chi = self.settingsArray [4]
            detector = self.settingsArray[5]
            str = 'chi = %f\r\n'%chi
            outfil.write (str)
            str = 'detector = %f\r\n'%detector
            outfil.write (str)
            str = 'exp. time = %f\r\n'%expos
            outfil.write (str)
            outfil.close()






