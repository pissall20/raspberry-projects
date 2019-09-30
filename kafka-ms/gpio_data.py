from gpiozero import (
        CPUTemperature, PingServer,
        LoadAverage, DiskUsage
    )

cpu = CPUTemperature()
print(cpu.temperature)

# ps = PingServer(host="localhost")
# print(ps.pin_factory)

la = LoadAverage()
print(la.load_average)

du = DiskUsage()
print(du.value)

