$(AS_CPU_PATH)/asfw.br: \
	$(AS_PROJECT_PATH)/Physical/heating_io/Hardware.hc \
	FORCE
	@$(AS_BIN_PATH)/BR.AS.ConfigurationBuilder.exe  "$(AS_PROJECT_PATH)/Physical/$(AS_CONFIGURATION)/Hardware.hc" -v V1.00.0 -S modbus_bc -o "$(AS_CPU_PATH)/asfw.br" -T SGC -B V2.00 -P "$(AS_PROJECT_PATH)"  -s modbus_bc -firmware  -extOptions  -W 6848 6751 -W 6848 6751 -W 6848 6751 -secret "$(AS_PROJECT_PATH)_br.as.configurationbuilder.exe"

FORCE:
