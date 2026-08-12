#!/usr/bin/env node

function solveWave(nx = 500, x0 = 0.0, t0 = 0.0, xf = 10.0, tf = 10.0) {
  const dx = (xf - x0) / (nx - 1);
  const dt = dx / 2.0;

  const nt = Math.floor((tf - t0) / dt) + 1;

  const x = new Array(nx);
  for (let i = 0; i < nx; i++) {
    x[i] = x0 + i * dx;
  }

  const u = new Array(nx);
  const v = new Array(nx);
  const a = new Array(nx);
  for (let i = 0; i < nx; i++) {
    u[i] = Math.exp(-((x[i] - 5.0) * (x[i] - 5.0)));
    v[i] = 0.0;
    a[i] = 0.0;
  }

  const dx2 = dx * dx;

  for (let step = 0; step < nt; step++) {
    const dtLeapfrog = step === 0 ? dt / 2.0 : dt;

    for (let i = 1; i < nx - 1; i++) {
      a[i] = (u[i - 1] + u[i + 1] - 2.0 * u[i]) / dx2;
    }

    for (let i = 0; i < nx; i++) {
      v[i] += a[i] * dtLeapfrog;
    }

    for (let i = 0; i < nx; i++) {
      u[i] += v[i] * dt;
    }
  }

  const center = Math.floor(nx / 2);
  let out = "";
  for (let i = center - 10; i <= center + 10; i++) {
    out += `${x[i]} ${u[i]}\n`;
  }
  process.stdout.write(out);

  return { x, u };
}

solveWave();
