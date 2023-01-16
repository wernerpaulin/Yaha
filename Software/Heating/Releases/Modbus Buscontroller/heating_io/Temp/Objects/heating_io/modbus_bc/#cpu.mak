SHELL = C:/BrAutomation/AS30080FD/As/GnuInst/V2.95.3/bin/sh
export AS_PLC := modbus_bc
export AS_CPU_PATH := $(AS_TEMP_PATH)/Objects/$(AS_CONFIGURATION)/$(AS_PLC)
export AS_ACTIVE_CONFIG_PATH := $(AS_PROJECT_PATH)/Physical/$(AS_CONFIGURATION)/$(AS_PLC)
export WIN32_AS_CPU_PATH := $(WIN32_AS_TEMP_PATH)\Objects\$(AS_CONFIGURATION)\$(AS_PLC)
export WIN32_AS_ACTIVE_CONFIG_PATH := $(WIN32_AS_PROJECT_PATH)\Physical\$(AS_CONFIGURATION)\$(AS_PLC)


CpuMakeFile: \
$(AS_CPU_PATH)/asfw.br \
$(AS_CPU_PATH)/sysconf.br \
$(AS_CPU_PATH)/arconfig.br \
$(AS_CPU_PATH)/iomap.br \
$(AS_BINARIES_PATH)/$(AS_CONFIGURATION)/$(AS_PLC)/Transfer.lst \
CpuPostBuildStep

$(AS_BINARIES_PATH)/$(AS_CONFIGURATION)/$(AS_PLC)/Transfer.lst: \
	$(AS_CPU_PATH)/asfw.br \
	$(AS_CPU_PATH)/sysconf.br \
	$(AS_CPU_PATH)/arconfig.br \
	$(AS_CPU_PATH)/iomap.br \
	$(AS_PROJECT_PATH)/Physical/heating_io/modbus_bc/Cpu.sw
	@$(AS_BIN_PATH)/BR.AS.FinalizeBuild.exe "$(AS_PROJECT_PATH)/heating_io.apj" -t "$(AS_TEMP_PATH)" -o "$(AS_BINARIES_PATH)" -c "$(AS_CONFIGURATION)" -i "C:/BrAutomation/AS30080FD" -S modbus_bc -all    -C "/RT=1000" -D "/IF=COM1 /BD=57600 /RS=0 /PA=2 /IT=20"


CpuPostBuildStep:
	@$(AS_BIN_PATH)/./BR.FS.PostbuildMgr.exe

#nothing to do (just call module make files)

include $(AS_CPU_PATH)/iomap/iomap.mak
include $(AS_CPU_PATH)/arconfig/arconfig.mak
include $(AS_CPU_PATH)/sysconf/sysconf.mak
include $(AS_CPU_PATH)/AsFw/AsFw.mak

.DEFAULT:
#nothing to do (need this target for prerequisite files that don't exit)
