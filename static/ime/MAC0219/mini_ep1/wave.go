package main

import (
	"fmt"
	"math"
)

func solveWave(nx int, x0, t0, xf, tf float64) ([]float64, []float64) {
	dx := (xf - x0) / float64(nx-1)
	dt := dx / 2.0

	nt := int((tf-t0)/dt) + 1

	x := make([]float64, nx)
	for i := 0; i < nx; i++ {
		x[i] = x0 + float64(i)*dx
	}

	u := make([]float64, nx)
	v := make([]float64, nx)
	a := make([]float64, nx)
	for i := 0; i < nx; i++ {
		u[i] = math.Exp(-((x[i] - 5.0) * (x[i] - 5.0)))
	}

	dx2 := dx * dx

	for step := 0; step < nt; step++ {
		dtLeapfrog := dt
		if step == 0 {
			dtLeapfrog = dt / 2.0
		}

		for i := 1; i < nx-1; i++ {
			a[i] = (u[i-1] + u[i+1] - 2.0*u[i]) / dx2
		}

		for i := 0; i < nx; i++ {
			v[i] += a[i] * dtLeapfrog
		}

		for i := 0; i < nx; i++ {
			u[i] += v[i] * dt
		}
	}

	center := nx / 2
	for i := center - 10; i <= center+10; i++ {
		fmt.Printf("%v %v\n", x[i], u[i])
	}

	return x, u
}

func main() {
	solveWave(500, 0.0, 0.0, 10.0, 10.0)
}
