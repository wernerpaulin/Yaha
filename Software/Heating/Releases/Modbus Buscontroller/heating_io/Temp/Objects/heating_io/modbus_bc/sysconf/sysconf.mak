$(AS_CPU_PATH)/sysconf.br: \
	FORCE \
	$(AS_PROJECT_PATH)/physical/$(AS_CONFIGURATION)/$(AS_PLC)/sysconf.br \
	$(AS_PROJECT_PATH)/physical/$(AS_CONFIGURATION)/hardware.hc 
	@$(AS_BIN_PATH)/BR.AS.ConfigurationBuilder.exe "$(AS_PROJECT_PATH)/Physical/$(AS_CONFIGURATION)/$(AS_PLC)/sysconf.br" "$(AS_PROJECT_PATH)/Physical/$(AS_CONFIGURATION)/Hardware.hc"  -sysconf -E Fieldbus -S modbus_bc -o "$(AS_CPU_PATH)/sysconf.br" -T SGC -B V2.00 -P "$(AS_PROJECT_PATH)" -s modbus_bc  -extOptions  -W 6848 6751 -secret "$(AS_PROJECT_PATH)_br.as.configurationbuilder.exe"

FORCE:

-include $(AS_CPU_PATH)/Force.mak 
