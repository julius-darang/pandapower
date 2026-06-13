import pandapower.networks as nw
import pandapower as pp

net = nw.simple_four_bus_system()
print(net.bus)