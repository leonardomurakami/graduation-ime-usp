#!/usr/bin/env python3
"""Benchmark das implementacoes da equacao de onda (Mini EP1 - MAC0219).

Executa cada implementacao N vezes, mede o tempo real (wall clock) de cada
execucao e calcula media e desvio padrao (amostral). Ao final, escreve o
arquivo de resultados no formato pedido pelo enunciado:

    <numero USP>
    <linguagem>, <n_exec>, <media>, <desvio_padrao>
    ...

Uso:
    python3 benchmark.py [--runs N] [--usp NUMERO_USP]
"""

import argparse
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def measure_once(cmd: list[str]) -> float:
    """Executa `cmd` e retorna o tempo real (wall clock) em segundos."""
    start = time.perf_counter()
    subprocess.run(cmd, cwd=HERE, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return time.perf_counter() - start


def benchmark(name: str, cmd: list[str], runs: int) -> tuple[float, float]:
    print(f"-> Benchmark {name}: {runs} execucoes...", file=sys.stderr)
    times: list[float] = []
    for i in range(runs):
        t = measure_once(cmd)
        times.append(t)
        print(f"   [{i + 1:2d}/{runs}] {t:.6f} s", file=sys.stderr)
    mean = statistics.fmean(times)
    std = statistics.stdev(times) if len(times) > 1 else 0.0
    print(f"   media = {mean:.6f} s | desvio padrao = {std:.6f} s",
          file=sys.stderr)
    return mean, std


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=30,
                        help="numero de execucoes (default 30, minimo 20)")
    parser.add_argument("--usp", type=str, default="XXXXXXXXX",
                        help="numero USP para o arquivo de resultados")
    parser.add_argument("--out", type=str, default="resultado.txt",
                        help="arquivo de saida")
    args = parser.parse_args()

    if args.runs < 20:
        print("Aviso: o enunciado exige pelo menos 20 execucoes.",
              file=sys.stderr)

    # Compila os binarios nativos previamente para nao incluir o tempo de
    # compilacao nas medicoes.
    go_bin = HERE / "wave_go"
    cpp_bin = HERE / "wave_cpp"
    print("-> Compilando binario Go...", file=sys.stderr)
    subprocess.run(["go", "build", "-o", str(go_bin), "wave.go"],
                   cwd=HERE, check=True)
    print("-> Compilando binario C++...", file=sys.stderr)
    subprocess.run(["g++", "-O2", "-std=c++17", "-o", str(cpp_bin),
                    "wave.cpp"], cwd=HERE, check=True)

    node_bin = shutil.which("node") or "node"

    targets = [
        ("python", [sys.executable, str(HERE / "wave.py")]),
        ("go", [str(go_bin)]),
        ("cpp", [str(cpp_bin)]),
        ("javascript", [node_bin, str(HERE / "wave.js")]),
    ]

    results: list[tuple[str, int, float, float]] = []
    for name, cmd in targets:
        mean, std = benchmark(name, cmd, args.runs)
        results.append((name, args.runs, mean, std))

    # Escreve o arquivo de resultados no formato pedido
    out_path = HERE / args.out
    with open(out_path, "w") as f:
        f.write(f"{args.usp}\n")
        for name, n, mean, std in results:
            f.write(f"{name}, {n},{mean:.6f},{std:.6f}\n")

    print(f"\nArquivo de resultados escrito em: {out_path}", file=sys.stderr)
    print(out_path.read_text(), file=sys.stderr)

    # Limpa os binarios gerados
    for bin_path in (go_bin, cpp_bin):
        try:
            bin_path.unlink()
        except FileNotFoundError:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
