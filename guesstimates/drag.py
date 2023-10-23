#!/usr/bin/python3
import math

rho = 1.225 # kg/m^3  atmospheric density, at sea level
A = 2.209874355967494 # m^2
Cd = 0.13
mass=816 # kg
g0 = 9.80665 # m/s**2

mph_to_mps = 0.44704
miles_to_meters = 1609.34
joules_to_kwh = 2.77778e-7


def drag_force(v, rho=rho, A=A, Cd=Cd):
    return 0.5 * rho * v*v * A * Cd

def drag_work(v, d, rho=rho, A=A, Cd=Cd):
    return drag_force(v, rho=rho, A=A, Cd=Cd) * d

def estimate_cr(v_mps, mass=mass, range=400 * miles_to_meters, energy=40/joules_to_kwh):
    """Given range estimate of 400mi with a 40kWh battery is at input
speed v_mps (m/s), estimate the coefficient of rolling resistance Cr by
assuming that the entire energy capacity is used between drag and
rolling resistance losses.
    """
    rolling_work = energy - drag_work(v_mps, range)
    assert rolling_work > 0
    # F_r = Cr * m * g0; W_r = Cr * m * g0 * range
    Cr = rolling_work / mass / g0 / range
    return Cr

def theoretical_range(v, mass=mass, energy=40/joules_to_kwh, rho=rho, A=A, Cd=Cd, Cr=0.016):
    fd = 0.5 * rho * v * v * A * Cd
    fr = mass * g0 * Cr
    f_net = fd + fr
    d = energy / f_net
    return d

def theoretical_range_table(mph_start, mph_end, mph_step, Cd=Cd, Cr=0.017, mass=mass, energy=40/joules_to_kwh, rho=rho):
    mph = mph_start
    print(f'{"Speed (mph)":12s} | {"Distance (miles)":16s}')
    print(f'{"":-<12s} | {"":-<16s}')
    while mph < mph_end:
        v = mph * mph_to_mps
        d = theoretical_range(v, Cd=Cd, Cr=Cr, mass=mass, energy=energy, rho=rho)
        dimperial = d / miles_to_meters

        print(f'{mph:^12d} | {dimperial:^16.0f}')
        mph += mph_step

def optimal_speed(Pr, cd=Cd, A=A, rho=rho):
    """Pr is the rest or idle power consumption, in Watts. The other
parameters are cd, the drag coefficient, and A, the frontal area.
    """
    return math.pow(Pr/(rho * cd * A), 1/3)
