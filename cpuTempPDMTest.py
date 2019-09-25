# getting temperature module
from gpiozero import CPUTemperature
cpu = CPUTemperature()

# getting UNIX time modules
from time import sleep, strftime, time

# using matplotlib to plot a live graph
import matplotlib.pyplot as plt
plt.ion()
x = []
y = []

# entering data into a csv file
def write_temp(temp):
    print(f"Time: {strftime("%Y-%m-%d %H:%M:%S")}, CPU Temperature: {str(temp)}")
    with open("files/cpu_temp.csv", "a") as log:
        log.write("{0}, {1}\n".format(strftime("%Y-%m-%d %H:%M:%S"), str(temp)))


# creating the graph
def plot_graph(temp):
    y.append(temp)
    x.append(time())
    plt.clf()
    plt.scatter(x,y)
    plt.plot(x,y)
    plt.draw()
    plt.pause(0.05)

while True:
    temp = cpu.temperature
    write_temp(temp)
    plot_graph(temp)
    sleep(1)
