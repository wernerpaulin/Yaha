$(AS_CPU_PATH)/iomap.br: \
	FORCE \
	$(AS_PROJECT_PATH)/physical/$(AS_CONFIGURATION)/$(AS_PLC)/iomap.iom \
	$(AS_PROJECT_PATH)/Physical/$(AS_CONFIGURATION)/Hardware.hc \
	$(AS_PROJECT_PATH)/physical/$(AS_CONFIGURATION)/$(AS_PLC)/cpu.sw \
	$(AS_CPU_PATH)/ChannelConfiguration.xml 
	@$(AS_BIN_PATH)/BR.AS.IOMapBuilder.exe "$(AS_PROJECT_PATH)/Physical/$(AS_CONFIGURATION)/$(AS_PLC)/IoMap.iom"  -m "$(AS_CPU_PATH)/ConfigInfo.cfi" -x "$(AS_CPU_PATH)/ChannelConfiguration.xml" -v V1.00.0 -o "$(AS_CPU_PATH)/iomap.br" -T SGC -B V2.00 -P "$(AS_PROJECT_PATH)" -s modbus_bc  -extOptions  -W 6848 6751 -W 6848 6751 -W 6848 6751

FORCE:

-include $(AS_CPU_PATH)/Force.mak 
