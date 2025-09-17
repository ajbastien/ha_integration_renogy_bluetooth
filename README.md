# Renogy Bluetooth Integration

**THIS INTGRATION IS IN ALPHA PHASE CURRENTLY - EXPECT BUGS**

This integration supports the Renogy Bluetooth communication.  It currently supports:
1. Smart Shunt 300
2. DC to DC Charger with Bluetooth module
3. Inverter with built in Bluetooth

## Plans

I plan on adding more from Cyrils sensors if the need is there, however I cannot test them as I do not have the equipment.  Please post any requests in the feature requests log.

##  Installation

Copy the files to /config/custom_components/renogy_bluetooth

## Configuration

You must specify the MAC address and select the appropriate device type.  
**Note:** I only support single device Bluetooth and not the master slave devices at this time.

## Note on Raspberry Pi Bluetooth

 I have found that the Raspberry Pi bluetooth adapter barely works. The use of a Bluetooth Proxy ESPHome device enhances the connectivity 100 fold. It connects 95+% of the time while Raspberry Pi seems to connect maybe 30% of the time.

# Special Thanks To:

1. https://github.com/cyrils/renogy-bt for providing the Inverter and DC to DC Charger parsing and the understanding of the flow for Renogy devices
2. https://github.com/antflix/ha_renogy_smart_shunt for providing the Shunt parsing and the understanding that it is different from the other devices
3. https://github.com/msp1974/HAIntegrationExamples for providing the well documented HA integration 101 template
