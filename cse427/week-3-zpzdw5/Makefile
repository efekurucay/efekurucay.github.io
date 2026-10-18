CONTIKI_PROJECT = energy-client energy-server
all: $(CONTIKI_PROJECT)

APPS += powertrace

# Scenario A: nullrdc_driver (radio always on). Scenarios B and C: contikimac_driver.
CFLAGS += -DNETSTACK_CONF_RDC=nullrdc_driver
CFLAGS += -DNETSTACK_CONF_MAC=csma_driver
# TCP is unused; dropping it lets the server fit the Sky ROM with ContikiMAC
CFLAGS += -DUIP_CONF_TCP=0

CONTIKI = ../..
CONTIKI_WITH_RIME = 0
CONTIKI_WITH_IPV6 = 1
include $(CONTIKI)/Makefile.include
