SHELL = C:/BrAutomation/AS30080FD/As/GnuInst/V2.95.3/bin/sh
CYGWIN=nontsec
export PATH := C:\ProgramData\Oracle\Java\javapath;C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0\;C:\Program Files (x86)\Common Files\Roxio Shared\DLLShared\;C:\Program Files\Dell\Dell Data Protection\Drivers\TSS\bin\;C:\Program Files (x86)\Skype\Phone\;C:\Program Files (x86)\QuickTime\QTSystem\;C:\Program Files (x86)\Common Files\Hilscher GmbH\TLRDecode;C:\Program Files (x86)\Common Files\Hilscher GmbH\TLRDecode
export AS_COMPANY_NAME := Bernecker + Rainer
export AS_USER_NAME := paulinw
export AS_PATH := C:/BrAutomation/AS30080FD
export AS_BIN_PATH := C:/BrAutomation/AS30080FD/Bin-en
export AS_PROJECT_PATH := C:/projects/heating_io
export AS_PROJECT_NAME := heating_io
export AS_SYSTEM_PATH := C:/BrAutomation/AS30080FD/As/System
export AS_VC_PATH := C:/BrAutomation/AS30080FD/As/VC
export AS_TEMP_PATH := C:/projects/heating_io/Temp
export AS_CONFIGURATION := heating_io
export AS_BINARIES_PATH := C:/projects/heating_io/Binaries
export AS_GNU_INST_PATH := C:/BrAutomation/AS30080FD/As/GnuInst/V2.95.3
export AS_GNU_BIN_PATH := $(AS_GNU_INST_PATH)/bin
export AS_INSTALL_PATH := C:/BrAutomation/AS30080FD
export WIN32_AS_PATH := C:\\BrAutomation\\AS30080FD
export WIN32_AS_BIN_PATH := C:\\BrAutomation\\AS30080FD\\Bin-en
export WIN32_AS_PROJECT_PATH := C:\\projects\\heating_io
export WIN32_AS_SYSTEM_PATH := C:\\BrAutomation\\AS30080FD\\As\\System
export WIN32_AS_VC_PATH := C:\\BrAutomation\\AS30080FD\\As\\VC
export WIN32_AS_TEMP_PATH := C:\\projects\\heating_io\\Temp
export WIN32_AS_BINARIES_PATH := C:\\projects\\heating_io\\Binaries
export WIN32_AS_GNU_INST_PATH := C:\\BrAutomation\\AS30080FD\\As\\GnuInst\\V2.95.3
export WIN32_AS_GNU_BIN_PATH := $(WIN32_AS_GNU_INST_PATH)\\bin
export WIN32_AS_INSTALL_PATH := C:\\BrAutomation\\AS30080FD

.suffixes:

ProjectMakeFile:

	@$(AS_BIN_PATH)/./BR.FS.PrebuildMgr.exe

	@$(AS_BIN_PATH)/BR.AS.AnalyseProject.exe "$(AS_PROJECT_PATH)/heating_io.apj" -t "$(AS_TEMP_PATH)" -c "$(AS_CONFIGURATION)" -o "$(AS_BINARIES_PATH)"  

	@$(AS_GNU_BIN_PATH)/make.exe -r -f "C:/projects/heating_io/Temp/Objects/$(AS_CONFIGURATION)/modbus_bc/#cpu.mak" -k

