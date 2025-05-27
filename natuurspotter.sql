CREATE DATABASE
IF NOT EXISTS natuurspotter;
USE natuurspotter;

CREATE TABLE soort
(
    id INT
    AUTO_INCREMENT PRIMARY KEY,
  naam_nl VARCHAR
    (100) UNIQUE NOT NULL,
  naam_lat VARCHAR
    (100) NOT NULL,
  zeldzaamheid ENUM
    ('algemeen','vrij algemeen','zeldzaam','zeer zeldzaam')
    DEFAULT 'algemeen',
  beschrijving TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

    CREATE TABLE waarneming
    (
        id INT
        AUTO_INCREMENT PRIMARY KEY,
  soort_id INT NOT NULL,
  datum DATE NOT NULL,
  plaatsnaam VARCHAR
        (100),
  lat DECIMAL
        (9,6),
  lon DECIMAL
        (9,6),
  bron VARCHAR
        (50),
  media_url VARCHAR
        (255),
  FOREIGN KEY
        (soort_id) REFERENCES soort
        (id) ON
        DELETE CASCADE
) ENGINE=InnoDB
        DEFAULT CHARSET=utf8mb4;

        CREATE INDEX idx_datum_soort ON waarneming(datum, soort_id);
