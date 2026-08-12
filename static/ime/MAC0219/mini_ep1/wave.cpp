#include <cstdio>
#include <cmath>
#include <vector>
#include <utility>

using std::vector;
using std::pair;

pair<vector<double>, vector<double>>
solveWave(int nx, double x0, double t0, double xf, double tf) {
    double dx = (xf - x0) / (nx - 1);
    double dt = dx / 2.0;

    int nt = static_cast<int>((tf - t0) / dt) + 1;

    vector<double> x(nx);
    for (int i = 0; i < nx; i++) {
        x[i] = x0 + static_cast<double>(i) * dx;
    }

    vector<double> u(nx), v(nx, 0.0), a(nx, 0.0);
    for (int i = 0; i < nx; i++) {
        u[i] = std::exp(-((x[i] - 5.0) * (x[i] - 5.0)));
    }

    double dx2 = dx * dx;

    for (int step = 0; step < nt; step++) {
        double dtLeapfrog = dt;
        if (step == 0) {
            dtLeapfrog = dt / 2.0;
        }

        for (int i = 1; i < nx - 1; i++) {
            a[i] = (u[i - 1] + u[i + 1] - 2.0 * u[i]) / dx2;
        }

        for (int i = 0; i < nx; i++) {
            v[i] += a[i] * dtLeapfrog;
        }

        for (int i = 0; i < nx; i++) {
            u[i] += v[i] * dt;
        }
    }

    int center = nx / 2;
    for (int i = center - 10; i <= center + 10; i++) {
        std::printf("%.17g %.17g\n", x[i], u[i]);
    }

    return {x, u};
}

int main() {
    solveWave(500, 0.0, 0.0, 10.0, 10.0);
    return 0;
}
