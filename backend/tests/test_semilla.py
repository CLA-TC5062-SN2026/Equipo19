"""La semilla de desarrollo es idempotente y prepara una toma nueva del video de A2 cada vez que se corre."""

from tests.ayudas import sql


def test_semilla_demo_dos_veces(cliente, capsys, monkeypatch):
    from app import semilla

    monkeypatch.setenv("SEMILLA_CORREO", "semilla@ampip.local")
    monkeypatch.setenv("SEMILLA_CONTRASENA", "semilla-coordinacion-1")
    monkeypatch.setenv("SEMILLA_APPI_CONTRASENA", "semilla-appi-1")
    for _ in range(2):
        semilla.main(["--demo"])
        token = capsys.readouterr().out.strip().splitlines()[-1]
        r = cliente.post("/api/auth/register", json={"tokenInvitacion": token, "contrasena": "contrasena-demo-2026"},
                         headers={"Authorization": ""})
        assert r.status_code == 201, r.text
    assert sql("SELECT count(*) FROM parque WHERE nombre='Parque Demo'")[0][0] == 1
    assert sql("SELECT count(*) FROM generacion")[0][0] == 1
