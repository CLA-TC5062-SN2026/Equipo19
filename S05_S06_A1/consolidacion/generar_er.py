"""Genera er_sgpis.puml desde la base cargada con esquema_bd.sql.

Uso: python consolidacion/generar_er.py postgresql://usuario@localhost/base er_sgpis.puml
"""
import sys
import psycopg

dsn, salida = sys.argv[1], sys.argv[2]
with psycopg.connect(dsn) as c:
    tablas = [r[0] for r in c.execute(
        "select table_name from information_schema.tables where table_schema='public' and table_type='BASE TABLE' "
        "order by table_name")]
    pk = {(t, col) for t, col in c.execute(
        "select tc.table_name, kcu.column_name from information_schema.table_constraints tc "
        "join information_schema.key_column_usage kcu using (constraint_schema, constraint_name) "
        "where tc.constraint_type='PRIMARY KEY' and tc.table_schema='public'")}
    fkcols = {(t, col) for t, col in c.execute(
        "select tc.table_name, kcu.column_name from information_schema.table_constraints tc "
        "join information_schema.key_column_usage kcu using (constraint_schema, constraint_name) "
        "where tc.constraint_type='FOREIGN KEY' and tc.table_schema='public'")}
    cols = c.execute(
        "select table_name, column_name, udt_name, is_nullable "
        "from information_schema.columns where table_schema='public' order by table_name, ordinal_position").fetchall()
    fks = c.execute(
        "select cl.relname, rf.relname, con.conname from pg_constraint con "
        "join pg_class cl on cl.oid=con.conrelid join pg_class rf on rf.oid=con.confrelid "
        "join pg_namespace n on n.oid=cl.relnamespace "
        "where con.contype='f' and n.nspname='public' order by cl.relname, con.oid").fetchall()

lineas = ["' Diagrama entidad-relación generado desde la base cargada con esquema_bd.sql (no se edita a mano).",
          "' Generador: consolidacion/generar_er.py", "@startuml er_sgpis", "hide circle", "skinparam linetype ortho",
          "title SGPIS: entidad-relación (desde esquema_bd.sql)", ""]
for t in tablas:
    lineas.append(f"entity {t} {{")
    filas = [r for r in cols if r[0] == t]
    for r in [r for r in filas if (t, r[1]) in pk]:
        lineas.append(f"  * {r[1]} : {r[2]} <<PK>>")
    lineas.append("  --")
    for r in [r for r in filas if (t, r[1]) not in pk]:
        marca = "*" if r[3] == "NO" else " "
        fk = " <<FK>>" if (t, r[1]) in fkcols else ""
        lineas.append(f"  {marca} {r[1]} : {r[2]}{fk}")
    lineas.append("}")
lineas.append("")
for hija, padre, _ in fks:
    lineas.append(f"{padre} ||--o{{ {hija}")
lineas.append("@enduml")
open(salida, "w", encoding="utf-8").write("\n".join(lineas) + "\n")
print(len(tablas), "tablas,", len(fks), "FK")
