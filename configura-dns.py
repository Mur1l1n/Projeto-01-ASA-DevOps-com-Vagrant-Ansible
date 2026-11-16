#!/usr/bin/env python3

import shutil
import subprocess
import sys

DOMINIO = "murilo.rian.devops"
DNS = "192.168.56.105"
INTERFACE = "vboxnet0"

IPS_ESPERADOS = {
    "arq": "192.168.56.105",
    "app": "192.168.56.152",
    "db": "192.168.56.102",
}


def main():
    for comando in ("dig", "sudo", "resolvectl", "getent"):
        if shutil.which(comando) is None:
            print(f"Comando necessário não encontrado: {comando}", file=sys.stderr)
            return 1

    print("Consultando o BIND do arq diretamente...", flush=True)

    for vm, esperado in IPS_ESPERADOS.items():
        nome = f"{vm}.{DOMINIO}"
        consulta = subprocess.run(
            ["dig", f"@{DNS}", nome, "A", "+short", "+time=2", "+tries=1"],
            capture_output=True,
            text=True,
        )
        resposta = consulta.stdout.strip()

        if consulta.returncode != 0 or resposta != esperado:
            recebido = resposta or consulta.stderr.strip() or "sem resposta"
            print(f"{nome}: esperado {esperado}, recebido {recebido}.", file=sys.stderr)
            print("Nenhuma configuração de DNS foi alterada.", file=sys.stderr)
            return 1

        print(f"{nome}: {resposta}")

    print(f"\nConfigurando o DNS da interface {INTERFACE}...", flush=True)

    for opcao, valor in (
        ("dns", DNS),
        ("domain", f"~{DOMINIO}"),
        ("default-route", "no"),
    ):
        resultado = subprocess.run(["sudo", "resolvectl", opcao, INTERFACE, valor])
        if resultado.returncode != 0:
            print(f"Falha em resolvectl {opcao}.", file=sys.stderr)
            return 1

    print("\nConferindo a resolução de nomes na máquina física...", flush=True)

    for vm, esperado in IPS_ESPERADOS.items():
        nome = f"{vm}.{DOMINIO}"
        consulta = subprocess.run(
            ["getent", "ahostsv4", nome], capture_output=True, text=True
        )
        ips = {linha.split()[0] for linha in consulta.stdout.splitlines() if linha.strip()}

        if consulta.returncode != 0 or ips != {esperado}:
            recebido = ", ".join(sorted(ips)) or "sem resposta"
            print(f"{nome}: esperado {esperado}, recebido {recebido}.", file=sys.stderr)
            return 1

        print(f"{nome}: {esperado}")

    print("\nDNS do projeto configurado na máquina física.")
    return 0


if __name__ == "__main__":
    sys.exit(main())