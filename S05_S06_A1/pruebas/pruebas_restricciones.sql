\set ON_ERROR_STOP 0
\pset footer off
BEGIN;
INSERT INTO usuario (id,nombre,correo,rol,estado) VALUES ('00000000-0000-0000-0000-000000000001','Coord','coord@ampip.mx','coordinacion_ampip','pendiente_activacion');
INSERT INTO version_catalogo (id,nombre,cargado_por) VALUES ('00000000-0000-0000-0000-0000000000a1','cat-v1','00000000-0000-0000-0000-000000000001');
INSERT INTO estandar (id,version_catalogo_id,numero,nombre) VALUES ('00000000-0000-0000-0000-0000000000e1','00000000-0000-0000-0000-0000000000a1',2,'Seguridad física');
INSERT INTO subestandar (id,estandar_id,numero,nombre) VALUES ('00000000-0000-0000-0000-0000000000f1','00000000-0000-0000-0000-0000000000e1','2.8','CCTV');
INSERT INTO criterio (id,subestandar_id,clave,texto,metodo_verificacion,categoria_evidencia) VALUES ('00000000-0000-0000-0000-0000000000c1','00000000-0000-0000-0000-0000000000f1','2.8.1','Cámara en caseta','Inspección','seguridad');
INSERT INTO generacion (id,nombre,fecha_inicio,version_catalogo_id) VALUES ('00000000-0000-0000-0000-0000000000b1','2027','2027-02-01','00000000-0000-0000-0000-0000000000a1');
INSERT INTO parque (id,tipo_registro,nombre,region) VALUES ('00000000-0000-0000-0000-000000000101','activo','Parque X','MX-NLE'),('00000000-0000-0000-0000-000000000102','activo','Parque Y','MX-JAL');
INSERT INTO expediente (id,parque_id,generacion_id) VALUES ('00000000-0000-0000-0000-000000000201','00000000-0000-0000-0000-000000000101','00000000-0000-0000-0000-0000000000b1'),('00000000-0000-0000-0000-000000000202','00000000-0000-0000-0000-000000000102','00000000-0000-0000-0000-0000000000b1');
INSERT INTO criterio_parque (id,expediente_id,criterio_id) VALUES ('00000000-0000-0000-0000-000000000301','00000000-0000-0000-0000-000000000201','00000000-0000-0000-0000-0000000000c1'),('00000000-0000-0000-0000-000000000302','00000000-0000-0000-0000-000000000202','00000000-0000-0000-0000-0000000000c1');
INSERT INTO evidencia (id,expediente_id,fase,categoria) VALUES ('00000000-0000-0000-0000-000000000401','00000000-0000-0000-0000-000000000201','implementacion_estandares','seguridad');
INSERT INTO usuario (id,nombre,correo,rol,parque_id) VALUES ('00000000-0000-0000-0000-000000000011','APPI X','appi@x.mx','appi','00000000-0000-0000-0000-000000000101'),('00000000-0000-0000-0000-000000000012','APPI Y','appi@y.mx','appi','00000000-0000-0000-0000-000000000102');
COMMIT;
\echo '--- R-02 vínculo evidencia de X con criterio de Y (debe fallar)'
INSERT INTO vinculo_evidencia (evidencia_id,criterio_parque_id,expediente_id) VALUES ('00000000-0000-0000-0000-000000000401','00000000-0000-0000-0000-000000000302','00000000-0000-0000-0000-000000000201');
\echo '--- R-02 vínculo correcto (debe pasar)'
INSERT INTO vinculo_evidencia (evidencia_id,criterio_parque_id,expediente_id) VALUES ('00000000-0000-0000-0000-000000000401','00000000-0000-0000-0000-000000000301','00000000-0000-0000-0000-000000000201');
\echo '--- R-03 renglón con criterio de otro expediente (debe fallar)'
INSERT INTO renglon_plan_trabajo (expediente_id,criterio_parque_id,responsable_id,fecha_comprometida) VALUES ('00000000-0000-0000-0000-000000000201','00000000-0000-0000-0000-000000000302','00000000-0000-0000-0000-000000000011','2027-04-15');
\echo '--- R-04 borrar parque con expediente (debe fallar)'
DELETE FROM parque WHERE id='00000000-0000-0000-0000-000000000101';
\echo '--- R-05 contacto principal APPI de otro parque (debe fallar)'
UPDATE parque SET contacto_principal_id='00000000-0000-0000-0000-000000000012' WHERE id='00000000-0000-0000-0000-000000000101';
\echo '--- R-05 contacto principal correcto (debe pasar)'
UPDATE parque SET contacto_principal_id='00000000-0000-0000-0000-000000000011' WHERE id='00000000-0000-0000-0000-000000000101';
\echo '--- R-06 consultor con parque_id (debe fallar)'
INSERT INTO usuario (nombre,correo,rol,parque_id) VALUES ('Cons','c@x.mx','consultor','00000000-0000-0000-0000-000000000101');
\echo '--- R-01 parque histórico sin fecha de término (debe fallar)'
INSERT INTO parque (tipo_registro,nombre,region,estado,fecha_ultimo_dictamen) VALUES ('historico','Parque Z','MX-JAL','historico','2022-03-15');
\echo '--- R-07 dos fases en proceso (la segunda debe fallar)'
INSERT INTO fase_expediente (expediente_id,fase,estado) VALUES ('00000000-0000-0000-0000-000000000201','diagnostico','en_proceso');
INSERT INTO fase_expediente (expediente_id,fase,estado) VALUES ('00000000-0000-0000-0000-000000000201','plan_trabajo','en_proceso');
\echo '--- R-08 TRUNCATE bitácora (debe fallar)'
INSERT INTO registro_bitacora (accion,resultado) VALUES ('prueba','exitoso');
TRUNCATE registro_bitacora;
\echo '--- bitácora UPDATE (debe fallar)'
UPDATE registro_bitacora SET accion='x';
\echo '--- R-09 intento_login con mayúsculas (debe fallar)'
INSERT INTO intento_login (correo) VALUES ('Appi@X.mx');
\echo '--- correo duplicado sin distinguir mayúsculas (debe fallar)'
INSERT INTO usuario (nombre,correo,rol) VALUES ('Dup','COORD@ampip.mx','coordinacion_ampip');
\echo '--- D-17 dictamen "no otorgar" sin sesión de comité (RF-14-AC-8, debe pasar)'
INSERT INTO dictamen (expediente_id,tipo,motivo,capturado_por) VALUES ('00000000-0000-0000-0000-000000000201','no_otorgar','60 % de obligatorios','00000000-0000-0000-0000-000000000001');
\echo '--- D-17 segundo dictamen en el mismo expediente (debe fallar)'
INSERT INTO dictamen (expediente_id,tipo,motivo,capturado_por) VALUES ('00000000-0000-0000-0000-000000000201','no_otorgar','otro','00000000-0000-0000-0000-000000000001');
\echo '--- D-17 dictamen con la sesión de comité de otro expediente (debe fallar)'
INSERT INTO usuario (id,nombre,correo,rol) VALUES ('00000000-0000-0000-0000-000000000021','Ana Ruiz','ana@consultores.mx','consultor');
INSERT INTO sesion_comite (id,expediente_id,consultor_comite_id) VALUES ('00000000-0000-0000-0000-000000000501','00000000-0000-0000-0000-000000000201','00000000-0000-0000-0000-000000000021');
INSERT INTO dictamen (expediente_id,sesion_comite_id,tipo,motivo,capturado_por) VALUES ('00000000-0000-0000-0000-000000000202','00000000-0000-0000-0000-000000000501','otorgar','cumple','00000000-0000-0000-0000-000000000001');
\echo '--- D-19 reapertura del consultor sin motivo (debe fallar)'
INSERT INTO calificacion_criterio (criterio_parque_id,estado_anterior,estado_nuevo,origen,consultor_id) VALUES ('00000000-0000-0000-0000-000000000301','no_cumplido','en_revision','consultor','00000000-0000-0000-0000-000000000021');
\echo '--- D-19 cambio automático y reapertura con motivo (deben pasar)'
INSERT INTO calificacion_criterio (criterio_parque_id,estado_anterior,estado_nuevo,origen) VALUES ('00000000-0000-0000-0000-000000000301','pendiente','en_revision','sistema');
INSERT INTO calificacion_criterio (criterio_parque_id,estado_anterior,estado_nuevo,motivo,origen,consultor_id) VALUES ('00000000-0000-0000-0000-000000000301','no_cumplido','en_revision','cambió la configuración de accesos del parque','consultor','00000000-0000-0000-0000-000000000021');
\echo '--- D-19 editar o borrar el historial (deben fallar)'
UPDATE calificacion_criterio SET motivo='x';
DELETE FROM calificacion_criterio;
\echo '--- R-11 datos iniciales'
SELECT count(*) AS fases FROM catalogo_fase; SELECT tamano_maximo_evidencia_mb, vigencia_distintivo_anios FROM configuracion;
