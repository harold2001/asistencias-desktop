-- detalle_grados
CREATE TABLE detalle_grados (
    detalle_grado_id INTEGER PRIMARY KEY AUTOINCREMENT,
    grado_id INTEGER,
    seccion VARCHAR(10),
    FOREIGN KEY (grado_id) REFERENCES grados (grado_id)
);

INSERT INTO
    detalle_grados (grado_id, seccion)
VALUES (1, "A"),
    (1, "B"),
    (1, "C"),
    (1, "D"),
    (1, "E"),
    (1, "F"),
    (1, "G"),
    (1, "H"),
    (1, "I"),
    (1, "J"),
    (2, "A"),
    (2, "B"),
    (2, "C"),
    (2, "D"),
    (2, "E"),
    (2, "F"),
    (2, "G"),
    (2, "H"),
    (2, "I"),
    (2, "J"),
    (3, "A"),
    (3, "B"),
    (3, "C"),
    (3, "D"),
    (3, "E"),
    (3, "F"),
    (3, "G"),
    (3, "H"),
    (3, "I"),
    (3, "J"),
    (4, "A"),
    (4, "B"),
    (4, "C"),
    (4, "D"),
    (4, "E"),
    (4, "F"),
    (4, "G"),
    (4, "H"),
    (4, "I"),
    (4, "J"),
    (5, "A"),
    (5, "B"),
    (5, "C"),
    (5, "D"),
    (5, "E"),
    (5, "F"),
    (5, "G"),
    (5, "H"),
    (5, "I"),
    (5, "J"),
    (6, "A"),
    (6, "B"),
    (6, "C"),
    (6, "D"),
    (6, "E"),
    (6, "F"),
    (6, "G"),
    (6, "H"),
    (6, "I"),
    (6, "J"),
    (7, "A"),
    (7, "B"),
    (7, "C"),
    (7, "D"),
    (7, "E"),
    (7, "F"),
    (7, "G"),
    (7, "H"),
    (7, "I"),
    (7, "J"),
    (8, "A"),
    (8, "B"),
    (8, "C"),
    (8, "D"),
    (8, "E"),
    (8, "F"),
    (8, "G"),
    (8, "H"),
    (8, "I"),
    (8, "J"),
    (9, "A"),
    (9, "B"),
    (9, "C"),
    (9, "D"),
    (9, "E"),
    (9, "F"),
    (9, "G"),
    (9, "H"),
    (9, "I"),
    (9, "J"),
    (10, "A"),
    (10, "B"),
    (10, "C"),
    (10, "D"),
    (10, "E"),
    (10, "F"),
    (10, "G"),
    (10, "H"),
    (10, "I"),
    (10, "J"),
    (11, "A"),
    (11, "B"),
    (11, "C"),
    (11, "D"),
    (11, "E"),
    (11, "F"),
    (11, "G"),
    (11, "H"),
    (11, "I"),
    (11, "J");

-- alumnos
-- CREATE TABLE alumnos (
--     alumno_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     codigo VARCHAR(150) UNIQUE,
--     nombres VARCHAR(250),
--     apellido_paterno VARCHAR(250),
--     apellido_materno VARCHAR(250),
--     fecha_ingreso DATE,
--     foto TEXT,
--     detalle_grado_id INTEGER,
--     FOREIGN KEY (detalle_grado_id) REFERENCES detalle_grados (detalle_grado_id)
-- );

CREATE TABLE alumnos (
    alumno_id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo VARCHAR(150),
    nombres VARCHAR(250),
    apellido_paterno VARCHAR(250),
    apellido_materno VARCHAR(250),
    fecha_ingreso DATE,
    foto TEXT,
    grupo TEXT,
    grado TEXT,
    detalle_grado_id INTEGER DEFAULT 1,
    FOREIGN KEY (detalle_grado_id) REFERENCES detalle_grados (detalle_grado_id)
);

ALTER TABLE alumnos DROP COLUMN grupo;

ALTER TABLE alumnos DROP COLUMN grado;

UPDATE alumnos
SET
    detalle_grado_id = (
        SELECT dg.detalle_grado_id
        FROM detalle_grados dg
            INNER JOIN grados g ON dg.grado_id = g.grado_id
        WHERE
            LOWER(g.grado) = LOWER(alumnos.grado)
            AND dg.seccion = alumnos.grupo
    );

UPDATE alumnos
SET fecha_ingreso = 
    SUBSTR(fecha_ingreso, 7, 4) || '-' || 
    SUBSTR(fecha_ingreso, 4, 2) || '-' || 
    SUBSTR(fecha_ingreso, 1, 2)
WHERE fecha_ingreso LIKE '%%/%%/%%%%';