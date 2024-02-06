import inspect
import logging
import pprint
import threading
import traceback
import typer

####################################################################
####################################################################
####################################################################
####################################################################
####################################################################
####################################################################


def getTestCase():
    import inspect
    for entry in inspect.stack():
        args = inspect.getargvalues(entry[0])
        if 'Test_Case' in args[3]:
            return args[3]['Test_Case']['Test_Case_ID']
    raise ValueError('Could not determine current test case.')


class Logger:

    def __init__(self, File_List=None, Harness_Object=None, To_Screen=False, Pause_On_Error=False, Pause_On_Warning=False, Labels=True):

        self.warn = self.warning  # Python logger supports warn and warning

        if File_List == None:
            raise ValueError('No File_List passed to Logger constructor.')

        self.Harness_Object = Harness_Object
        self.Labels = Labels
        self.Pause_On_Error = Pause_On_Error
        self.Pause_On_Warning = Pause_On_Warning

        self.To_Screen = To_Screen
        self.File_List = File_List
        self.Default = None
        self.PP = pprint.PrettyPrinter()

        for Entry in self.File_List:

            if ('Filename' in Entry) == False:
                raise ValueError('File entry passed to Logger constructor missing Filename key. Entry was: ' + str(Entry))

            elif ('Default' in Entry) == False:
                Entry['Default'] = False

            if ('Name' in Entry) == False:
                raise ValueError('File entry passed to Logger constructor missing Name key. Entry was: ' + str(Entry))

            if Entry['Default'] == True:
                self.Default = Entry['Name']

        if self.Default == None:
            self.Default = self.File_List[0]['Name']

        self.LoggerList = []
        Formatter = logging.Formatter('%(threadid)s||%(asctime)s||%(topic)s||%(level)s||%(prefix)s||%(message)s||%(file)s||%(line)i')
        Default_Formatter = logging.Formatter('%(funcName)s||%(asctime)s|| ||%(levelname)s|| ||%(message)s||%(filename)s||%(lineno)i')

        for Entry in self.File_List:
            self.LoggerList.append(logging.getLogger(Entry['Name']))
            Entry['File'] = logging.FileHandler(Entry['Filename'])
            if Entry['Name'] in ['harness', 'user']:
                Entry['File'].setFormatter(Formatter)
            else:
                Entry['File'].setFormatter(Default_Formatter)
            self.LoggerList[-1].addHandler(Entry['File'])
            self.LoggerList[-1].setLevel(logging.DEBUG)
            self.LoggerList[-1].propagate = False

    ####################################
    ####################################
    ####################################

    def getTestCaseId(self):
        if self.Harness_Object.Current_Test_Case == None:
            return 'Harness'
        try:
            return getTestCase()
        except:
            return 'Harness'

    ####################################
    ####################################
    ####################################

    def __del__(self):

        for Output_File in self.File_List:
            try: Output_File['File'].close()
            except: pass

    ####################################
    ####################################
    ####################################

    def prep(self, *args, **keywords):

        if 'Output_Name_List' in keywords:
            logfiles = keywords['Output_Name_List']
        else:
            logfiles = list(set([self.Default, 'harness']))

        if 'Text' in keywords:
            text = keywords['Text']
        else:
            if len(args[0]) > 1:
                try:
                    text = args[0][0] % tuple(args[0][1:])
                except TypeError:
                    text = args[0][0]
            else:
                text = args[0][0]

        testCaseId = 'dummyTC'
        filename = 'NA'
        lineno = 0
        try:
            Frame = inspect.getouterframes(inspect.currentframe())
            if len(Frame) > 0:
                if Frame[2][1] == 'ifabric/support/logger.py':
                    filename = Frame[3][1]
                    lineno = Frame[3][2]
                else:
                    filename = Frame[2][1]
                    lineno = Frame[2][2]
        except:
            pass

        extra = {'threadid': testCaseId,
                 'topic': keywords.get('topic', 'default'),
                 'prefix': threading.current_thread().name,
                 'file': filename,
                 'line': lineno}

        if self.To_Screen or ('To_Screen' in keywords and keywords['To_Screen'] == True):
            try:
                typer.echo(text)
                #print(text)
            except Exception as e:
                text = text.encode('utf-8')
                typer.echo(text)
                #print(text)
        
        return logfiles, text, extra

    ####################################
    ####################################
    ####################################

    def exception(self, data):
        self.LoggerList[0].exception(data)

    ####################################
    ####################################
    ####################################

    def info(self, *args, **keywords):

        logfiles, text, extra = self.prep(args, **keywords)
        for Log in logfiles:
            logObj = logging.getLogger(Log)
            extra['level'] = 'INFO'
            logObj.info(text, extra=extra)

    ####################################
    ####################################
    ####################################

    def debug(self, *args, **keywords):

        self.debug4(*args, **keywords)

    ####################################
    ####################################
    ####################################

    def warning(self, *args, **keywords):

        logfiles, text, extra = self.prep(args, **keywords)
        for Log in logfiles:
            logObj = logging.getLogger(Log)
            extra['level'] = 'WARNING'
            logObj.warning(text, extra=extra)

        if self.Pause_On_Warning:
            eval(input('User requested to pause on using log level WARNING. Press return to continue......'))

    ####################################
    ####################################
    ####################################

    def error(self, *args, **keywords):

        logfiles, text, extra = self.prep(args, **keywords)
        for Log in logfiles:
            logObj = logging.getLogger(Log)
            extra['level'] = 'ERROR'
            logObj.error(text, extra=extra)

        if self.Pause_On_Error:
            eval(input('User requested to pause on using log level ERROR. Press return to continue......'))

    ####################################
    ####################################
    ####################################

    def debug4(self, *args, **keywords):

        logfiles, text, extra = self.prep(args, **keywords)
        for Log in logfiles:
            logObj = logging.getLogger(Log)
            extra['level'] = 'DBG4'
            logObj.debug(text, extra=extra)

    ####################################
    ####################################
    ####################################

    def debug3(self, *args, **keywords):

        logfiles, text, extra = self.prep(args, **keywords)
        for Log in logfiles:
            logObj = logging.getLogger(Log)
            extra['level'] = 'DBG3'
            logObj.debug(text, extra=extra)

    ####################################
    ####################################
    ####################################

    def debug2(self, *args, **keywords):

        logfiles, text, extra = self.prep(args, **keywords)
        for Log in logfiles:
            logObj = logging.getLogger(Log)
            extra['level'] = 'DBG2'
            logObj.debug(text, extra=extra)
