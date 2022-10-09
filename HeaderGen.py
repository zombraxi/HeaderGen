#!/usr/bin/env python3

from __future__ import annotations, print_function

"""

HeaderGen by Zombraxi

About:
    HeaderGen provides a tiny utility for automatically generating
    header files (particularly for C & C++) with proper "header guards",
    such that you won't forget to place them yourself!

License Info (see LICENSE file)

"""

__project_name__ = "HeaderGen"
if (__debug__):
    __release_type__="dev"
else:
    __release_type__="release"
__version__ = (1,0,0,__release_type__)
del __release_type__
__author__ = "zombraxi"

import os
import sys
import re
import io
from enum import Enum, auto
from typing import List, Tuple
from dataclasses import dataclass

"""

Useful base class wrappers

"""
class SingletonBase(object):
    single_instance = None

    def __new__(cls, *args):
        if cls.__is_instantiated(): return cls.single_instance

        NO_LOGGER_PRINT("SingletonBase.__new__",
            "Creating a new instance of {}".format(cls.__name__))
        return object.__new__(cls,*args)

    def __init__(self,*args):
        # MUST CHECK IN __INIT__,
        # AFTER __NEW__ RETURNS, IT RUNS __INIT__
        # AND DONT WANT THE OBJECT REINITIALIZING ITS VALUES !!
        if self.__is_self_instantiated(): return # self.__self_inst()
                                                # __init__ can only ret None

        # cant use Logger here because Logger inherits from SingletonBase
        # which means that SingletonBase cannot use the Logger LOL
        # otherwise recursion fuckery error
        NO_LOGGER_PRINT("SingletonBase.__init__",
        "Running the __SINGLETON_INIT__ wrapper of {}".format(self.__class__.__name__))
        self.__SINGLETON_INIT__(*args)
        self.__set_inst()

    # OVERRIDE THIS __SINGLETON_INIT__
    # IF YOU WANNA INITIALIZE YOUR SINGLETON
    # WITH SOME EXTRA STUFFS
    def __SINGLETON_INIT__(self):
        return

    # alternative to __new__... __new__
    # is more convenient though...
    # override if necessary...
    # ----- OLD -------
    #@classmethod
    #def INST(cls,*args) -> object:
    #    if cls.__is_instantiated(): return cls.single_instance
    #    return cls(*args) # if not instantiated, return an instance
                     # of the class !

    def __self_inst(self):
        return self.__class__.INST()

    # override if necessary...
    @classmethod
    def __is_instantiated(cls) -> bool:
        if (cls.single_instance != None): return True
        return False

    def __is_self_instantiated(self) -> bool:
        return self.__class__.__is_instantiated()

    def __set_inst(self) -> None:
        self.__class__.single_instance = self

class WEnum(Enum):
    @classmethod
    def get( cls, attrib: str ):
        return cls.__dict__[attrib].value

class TypedVar(object):
    __name__ ='TypedVar'
    __slots__=('__type','__value',)
    def __init__(self, _type, value=None) -> None:
        ASSERT_T(_type,value)
        self.__type = _type
        self.__value = value

    def get(self):
        return self.__value

    def set(self,value):
        ASSERT_T(self.__type, value)
        self.__value = value

    def typeof(self):
        return self.__type

    @staticmethod
    def auto_gen(cls,value) -> None:
        return TypedVar(type(value),value)

    def __repr__(self):
        return (
            'TypedVar('
            f'type={self.__type}'
            f'value={self.__value}'
            ')'
        )


class Struct(object):
    __name__ =('Struct')
    __slots__=('__variables')
    def __init__(self) -> None:
        self.__variables: List[TypedVar] = []

    def add_auto_var(self, value):
        self.__variables.append(
            TypedVar.auto_gen(value)
        )

    def add_typed_var(self, _type, value=None):
        if isinstance(_type, TypedVar):
            self.__variables.append(_type)
        else:
            self.__variables.append(
                TypedVar(_type, value)
            )

    def get_var(self, index: int):
        return self.__variables[index].get()

    def set_var(self, index: int, val) -> None:
        self.__variables[index].set(val)

class Union(object):
    __name__='Union'
    __slots__=('__value', '__current_type',)
    def __init__(self):
        self.__value: List[TypedVar] = []
        self.__current_type = None

    def set(self, value):
        self.__current_type = type(value)

        # get index of typed var
        found_index = False
        for index,tv in enumerate(self.__value,start=0):
            if tv.typeof() == self.__current_type:
                self.__value[index].set(value)
                found_index = True

        # create a variable with that type
        # if not already exist
        if not found_index:
            self.__value.append(
                TypedVar(
                    self.__current_type, value
                )
            )

    # Returns a tuple that is the
    # (type, value)
    def get(self) -> Tuple[type,object]:

        ret = None
        for v in self.__value:
            if (v.typeof() == self.__current_type):
                ret = v.get()
                break
        return (self.__current_type, ret)

    @staticmethod
    def value_from_tuple(t: Tuple[type, object]) -> object:
        return t[1]

    @staticmethod
    def type_from_tuple(t: Tuple[type,object]) -> type:
        return t[0]

    def typeof(self) -> type:
        return self.__current_type

"""

Logging mechanism

"""
def NO_LOGGER_PRINT(func_name="DEBUG", text="") -> None:
    ASSERT_STR(func_name)
    ASSERT_STR(text)

    if (__debug__):
        print(
            "FUNCTION {} : {}".format(func_name, text)
        )

class Logger(SingletonBase):

    # override singletonbase...
    def __SINGLETON_INIT__(self):
        self.GLOBAL_LOG: str = ""

    def add_to_log(self, t: str) -> None:
        if (__debug__):
            self.GLOBAL_LOG += "{}\n".format(t)

    def print(self, func_name: str = None, text: str = "") -> None:
        assert type(func_name) is str or func_name is None, "func_name must be `str`"
        ASSERT_STR(text)
        if (__debug__):
            text = "FUNCTION {}: {}".format(func_name,text) if (func_name != None) else (
                "DEBUG: {}".format(text)
            )
            print(text)
            self.add_to_log(text)

    def dump(self) -> None:
        if (__debug__):
            Swrite_to("headergen_log_dump.txt",self.GLOBAL_LOG)


"""

Assertion wrappers

"""
def ASSERT_T(t: type, o: object) -> bool:
    # skip entirety and return true if not debugging...
    if (__debug__):
        if t == None:
            assert o is t, "object must be of type None"
        assert type(o) is t, "object must be of type {}".format(t.__name__)
    return True

def ASSERT_BOOL(o) -> bool:
    return ASSERT_T(bool, o)

def ASSERT_STR(o) -> bool:
    return ASSERT_T(str, o)

def ASSERT_INT(o) -> bool:
    return ASSERT_T(int, o)

def ASSERT_FLOAT(o) -> bool:
    return ASSERT_T(float, o)

def ASSERT_LIST(o) -> bool:
    return ASSERT_T(list, o)

def ASSERT_DICT(o) -> bool:
    return ASSERT_T(dict, o)

def ASSERT_TUPLE(o) -> bool:
    return ASSERT_T(tuple, o)

def ASSERT_NONE(o) -> bool:
    return ASSERT_T(None, o)

"""

Errors

"""

class InvalidActionError(Exception):
    pass

class UnknownError(Exception):
    def __init__(self):
        super().__init__(
            "An unknown error has occurred! Please report to Issues!"
        )

"""

File I/O wrappers

"""
def Swrite_to(filepath: str, text: str) -> None:
    ASSERT_STR(text)
    ASSERT_STR(filepath)

    Logger().print("Swrite_to","Writing to {}".format(filepath))

    f = io.open(filepath, "w")
    f.write(text)
    f.close()

def Sread_from(filepath: str) -> str:
    ASSERT_STR(filepath)
    Logger().print("Sread_from","Reading from {}".format(filepath))
    f = io.open(filepath,"r")
    dat = f.read()
    f.close()
    return dat

"""

HeaderGen data structures

"""

# Attributes:
#     macro_prefix (str)
#     file_prefix (str)
#     file_ext (str)
#     license_notice (str)
class HGenState(SingletonBase):
    __name__='HGenState'
    def __SINGLETON_INIT__(self) -> None:

        # implicit Struct inheritance...
        # singleton is incompatible with Struct so...
        self.state = Struct()

        """
        macro_prefix - 0
        file_prefix - 1
        file_ext - 2
        license_notice - 3
        """
        self.state.add_typed_var(str, "") # some reasonable defaults
        self.state.add_typed_var(str, "")
        self.state.add_typed_var(str, "H")
        self.state.add_typed_var(str,"")

    @property
    def macro_prefix(self):
        return self.state.get_var(0)

    @macro_prefix.setter
    def macro_prefix(self,v: str):
        self.state.set_var(0,v)

    @property
    def file_prefix(self):
        return self.state.get_var(1)

    @file_prefix.setter
    def file_prefix(self, v: str):
        self.state.set_var(1,v)

    @property
    def file_ext(self):
        return self.state.get_var(2)

    @file_ext.setter
    def file_ext(self,v: str):
        self.state.set_var(2,v)

    @property
    def license_notice(self):
        return self.state.get_var(3)

    @license_notice.setter
    def license_notice(self,v: str):
        self.state.set_var(3,v)

class HGenBuiltIns(object):
    #__builtins
    pass

# Attributes
#   name (str)
#   datatype
#   required (bool)
class HGenFunctionParameter(Struct):
    """
    name - 0
    type - 1
    required - 2
    """
    def __init__(self):
        self.add_typed_var()

# Attributes
#   parameters (List[HGenFunctionParameter])
class HGenFunction(Struct):
    """
    parameters - 0
    """
    def __init__(self):
        self.add_typed_var(list,[])

    def add_param(self, param_info: HGenFunctionParameterInfo) -> None:
        self.parameters.append(HGenFunctionParameter.from_info(param_info))

    @property
    def parameters(self):
        return self.get_var(0)

    @parameters.setter
    def parameters(self,v):
        self.set_var(0,v)

# Attributes
#    name (str)
#    type (HGenSymbolType)
class HGenSymbol(object):
    __name__ = 'HGenSymbol'
    def __init__(self):
        self.__type = None

    #@classmethod
    #def from(cls, )


# Attributes
#    ScriptFile (str)
class HGenEnvars(WEnum):
    DefaultScriptFilename: str = "HGenScript.hgen"

"""

*THE* Header Generator

"""

class HeaderGenerator(SingletonBase):
    __available_builtin_actions: List[str] = [
        "SET_MACRO_PREFIX","SET_FILE_PREFIX",
        "SET_FILE_EXT","SET_LICENSE_NOTICE_SOURCE",
        "GENERATE_HEADERS"
    ]

    def __SINGLETON_INIT__(self):
        self.ACTION_FUNC_TBL = {
            "SET_MACRO_PREFIX":self.SET_MACRO_PREFIX,
            "SET_FILE_PREFIX":self.SET_FILE_PREFIX,
            "SET_FILE_EXT":self.SET_FILE_EXT,
            "SET_LICENSE_NOTICE_SOURCE":self.SET_LICENSE_NOTICE_SOURCE,
            "GENERATE_HEADERS":self.GENERATE_HEADERS
        }
    def execute_action_type(self,t: str, args: tuple) -> None:
        #self.__dict__[t](args)
        self.ACTION_FUNC_TBL[t](args)

    def SET_MACRO_PREFIX(self,v) -> None:
        HGenState().macro_prefix = v[0]

    def SET_FILE_PREFIX(self,v) -> None:
        HGenState().file_prefix = v[0]

    def SET_FILE_EXT(self, v) -> None:
        HGenState().file_ext = v[0]

    def SET_LICENSE_NOTICE_SOURCE(self, v) -> None:
        HGenState().license_notice = Sread_from(v[0])

    def GENERATE_HEADERS(self, vtuple: tuple) -> None:#*args) -> None:
        #files_to_gen: tuple = args # no "*" makes it pass as Tuple
        genstate = HGenState()
        fprfx = genstate.file_prefix
        fext = ("."+genstate.file_ext) if (genstate.file_ext != "") else (
            ""
        )
        for _f in vtuple:
            Swrite_to(
                fprfx+_f+fext,
                generate_templated_header(_f)
            )

    @property
    def builtin_actions(self):
        return self.__available_builtin_actions

# create a hgen script based on a template...
def create_templated_hgen_script(xfile: str) -> None:
    TEMPLATE = """
# i am a comment!
SET_MACRO_PREFIX(
    HGEN_DEFAULT
)

SET_FILE_PREFIX(example_)

SET_FILE_EXT(H)

SET_LICENSE_NOTICE_SOURCE()

GENERATE_HEADERS(
    test1,
    test2,
    test3,test4,tes5
)
    """
    Swrite_to(xfile, TEMPLATE)

def isolate_arguments(act: str) -> str or None:
    try:
        return act.split("(")[1][0:-1]
    except IndexError:
        return ""
    except:
        pass

def isolate_action(act: str) -> str:
    return act.split("(")[0]

def separate_arguments(args: str) -> List[str]:
    return args.split(",")

def remove_spaces(tmpL: List[str]):
    for i in range(len(tmpL)):
        tmpL[i] = tmpL[i].replace(" ","")
    return tmpL

def do_action(act: str) -> None:
    actype = isolate_action(act)
    tmp: str = isolate_arguments(act)
    if tmp == "":
        HeaderGenerator().execute_action_type(actype,tuple([tmp]))
        return
    tmp = separate_arguments(tmp)
    tmp = remove_spaces(tmp)

    #print(tmp)

    # send as tuple...
    ASSERT_LIST(tmp)
    HeaderGenerator().execute_action_type(actype, tuple(tmp))

def do_actions(actions: List[str]) -> None:
    for x in actions:
        do_action(x)

def generate_templated_header(xfile: str) -> str:
    hgenst = HGenState()
    macro_define = hgenst.macro_prefix + "_" + xfile + "_H_"
    licnot = hgenst.license_notice

    ret: str = ""
    if licnot != "":
        ret+="/*\n{}\n*/\n\n".format(licnot)
    ret+="#ifndef {}\n#define {}\n\n#endif".format(
        macro_define,macro_define
    )

    return ret


# run the hgen from this script file...
def run_from_hgen_script(xfile: str) -> None:
    scriptD: str = Sread_from(xfile)

    actions: List[str] = find_actions(parse_script(scriptD))
    are_actions_valid(actions)
    do_actions(actions)

def parse_script(d: str) -> str:
    d = lose_comments(d)
    return lose_newlines(d)

def lose_comments(d: str) -> str:
    slist: List[str] = d.split("\n")
    ret: str = ""
    for x in slist:
        x = x+"\n"
        if x.startswith("#"):
            x = ""
        else:
            # search for the comment start
            for index,c in enumerate(x,start=0):
                if c == "#":
                    x = x[0:index]+"\n"
                    break

        ret+=x
    return ret

def lose_newlines(d: str) -> str:
    slist: List[str] = d.split("\n")
    ret: str = ""
    for x in slist:
        ret+=x
    return ret

def find_actions(d: str) -> List[str]:
    actions_pat = re.compile(r'[a-zA-Z0-9_]+\([a-zA-Z0-9/_,\. ]+\)')

    actionList: List[str] = []
    for x in re.findall(actions_pat,d):
        actionList.append(x)

    return actionList

def are_actions_valid(actions: List[str]) -> bool:
    for x in actions:
        if not is_valid_action(x):return False
    return True

def is_valid_action(action: str) -> bool:
    a = action.split("(")[0]
    if not (a in HeaderGenerator().builtin_actions):
        raise InvalidActionError("{} is not a valid Action!".format(a))
    return True


"""

entry-entry-point

"""

def HELP_MESSAGE() -> NoReturn:
    global __project_name__
    global __version__
    global __author__
    print(
"""
{} {}.{}.{}-{} by {}
--------------------------------------------------------
Help:
        --help :
            Provides a help dialog
        --new (optional: file) :
            Creates a new templated HeaderGen script!
        --run (required: file) :
            Runs the templated HeaderGen script!
""".format(
    __project_name__,
    __version__[0],__version__[1],__version__[2],__version__[3],
    __author__)
)
    sys.exit() # exit after help message...

def HELP_MESSAGE2() -> NoReturn:
    print(
"""
ERROR:
    No arguments were detected.
    Run with argument \'--help\' for a list of parameters!
"""
)
    sys.exit()

def does_need_help(args: List[str]) -> bool:
    # no args provided
    if not (len(args) > 0):return True
    elif (args[0] == "--help"):return True
    else:return False

# returns the argument passed if the arg exists...
def does_arg_or_not(what_arg: str, args: List[str]) -> Tuple[str, bool]:
    what_arg = "--"+what_arg
    for index,x in enumerate(args,start=0):
        if (x == what_arg):
            # check if the arg list is even long enough,
            # if so, return the supplied value to that arg
            # along with true
            if (len(args) > index+1):
                return (args[index], True)
            else:return (None, True)
    return (None, False)

def did_arg_exist(v: Tuple[str, bool]) -> bool:
    return v[1]

def did_arg_supply_value(v: Tuple[str, bool]):
    if (v[0] != "" and v[0] != None):return True
    return False

def get_arg_value(v: Tuple[str, bool]) -> str:
    return v[0]

def act_on_parse(args: List[str]) -> None:
    Logger().print("act_on_parse","Parsing ARGV")

    if (does_need_help(args)):
        HELP_MESSAGE()
    else: # catch all...
        new_arg: Tuple[str, bool] = does_arg_or_not("new",args)
        run_arg: Tuple[str, bool] = does_arg_or_not("run",args)

        # CREATE NEW TEMPLATED HEADER GEN SCRIPT
        if did_arg_exist(new_arg):
            if did_arg_supply_value(new_arg):
                create_templated_hgen_script(get_arg_value(new_arg))
            else: # create with default filename
                create_templated_hgen_script(HGenEnvars.get("DefaultScriptFilename"))

        # RUN HGEN SCRIPT
        elif did_arg_exist(run_arg):
            if did_arg_supply_value(run_arg):
                run_from_hgen_script(get_arg_value(run_arg))
            else: # assume default script name
                run_from_hgen_script(HGenEnvars.get("DefaultScriptFilename"))

        # still display help even if they didnt ask,
        # given they couldnt supply anything else
        else:
            HELP_MESSAGE2()

def HGEN_ENTRY() -> None:
    # parse sys.argv...
    _ARGS: List[str] = sys.argv[1:] # ignore first arg, its useless
                         # (name of script ran)

    act_on_parse(_ARGS)


"""

Entry-Point

"""
def begin() -> None:
    Logger() # pre-emptively create single logger instance
    HGenState() # single state instance
    HeaderGenerator() # single hgen instance
def end() -> None:
    Logger().dump() # dump the entirety of log
def main() -> NoReturn:
    begin() # pre-emptive initialize

    HGEN_ENTRY()

    end() # perform necessary end actions
    sys.exit()

if __name__ == "__main__":
    main()
