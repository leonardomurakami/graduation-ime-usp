#!/usr/bin/env python3
import math


def solve_wave(nx: int = 500, x0: float = 0.0, t0: float = 0.0,
               xf: float = 10.0, tf: float = 10.0):
    dx = (xf - x0) / (nx - 1)
    dt = dx / 2.0

    nt = int((tf - t0) / dt) + 1

    x = [x0 + i * dx for i in range(nx)]
    u = [math.exp(-((xi - 5.0) ** 2)) for xi in x]
    v = [0.0] * nx
    a = [0.0] * nx

    dx2 = dx * dx

    for step in range(nt):
        dt_leapfrog = dt / 2.0 if step == 0 else dt

        for i in range(1, nx - 1):
            a[i] = (u[i - 1] + u[i + 1] - 2.0 * u[i]) / dx2

        for i in range(nx):
            v[i] += a[i] * dt_leapfrog

        for i in range(nx):
            u[i] += v[i] * dt

    center = nx // 2
    for i in range(center - 10, center + 11):
        print(f"{x[i]} {u[i]}")

    return x, u


if __name__ == "__main__":
    solve_wave()
