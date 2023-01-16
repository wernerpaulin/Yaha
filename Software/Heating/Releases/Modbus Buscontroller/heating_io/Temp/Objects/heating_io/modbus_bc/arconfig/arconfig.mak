$(AS_CPU_PATH)/arconfig.br: \
	FORCE \
	$(AS_PROJECT_PATH)/physical/$(AS_CONFIGURATION)/$(AS_PLC)/arconfig.rtc \
	$(AS_PROJECT_PATH)/physical/$(AS_CONFIGURATION)/hardware.hc \
	$(AS_PROJECT_PATH)/physical/$(AS_CONFIGURATION)/$(AS_PLC)/iomap.iom 
	@$(AS_BIN_PATH)/BR.AS.ConfigurationBuilder.exe "$(AS_PROJECT_PATH)/Physical/$(AS_CONFIGURATION)/$(AS_PLC)/ArConfig.rtc" "$(AS_PROJECT_PATH)/Physical/$(AS_CONFIGURATION)/Hardware.hc" "$(AS_ACTIVE_CONFIG_PATH)/IoMap.iom"  -c heating_io -arconfig -E Fieldbus -v V1.00.0 -S modbus_bc -o "$(AS_CPU_PATH)/arconfig.br" "$(AS_CPU_PATH)/ChannelConfiguration.xml" -T SGC -B V2.00 -P "$(AS_PROJECT_PATH)" -s modbus_bc  -extOptions  -W 6848 6751 -W 6848 6751 -secret "$(AS_PROJECT_PATH)_br.as.configurationbuilder.exe"

FORCE:

-include $(AS_CPU_PATH)/Force.mak 
