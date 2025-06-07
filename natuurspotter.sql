-- NatuurSpotter Database Schema
-- Database voor het opslaan van keverwaarnemingen en soortinformatie

-- Maak database
CREATE DATABASE natuurspotter;
USE natuurspotter;

CREATE TABLE soort (
    id INT AUTO_INCREMENT PRIMARY KEY,
    naam_nl VARCHAR(100) UNIQUE NOT NULL COMMENT 'Nederlandse naam van de soort',
    naam_lat VARCHAR(100) NOT NULL COMMENT 'Latijnse naam van de soort',
    zeldzaamheid ENUM('algemeen', 'vrij algemeen', 'zeldzaam', 'zeer zeldzaam') DEFAULT 'algemeen' COMMENT 'Zeldzaamheidsstatus van de soort',
    beschrijving TEXT COMMENT 'Beschrijving van de soort',
    photo_link VARCHAR(255) COMMENT 'URL naar foto van de soort',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE waarneming (
    id INT AUTO_INCREMENT PRIMARY KEY,
    soort_id INT NOT NULL,
    datum DATE NOT NULL COMMENT 'Datum van de waarneming',
    plaatsnaam VARCHAR(100) COMMENT 'Plaats waar de waarneming is gedaan',
    lat DECIMAL(9,6) COMMENT 'Latitude coördinaat',
    lon DECIMAL(9,6) COMMENT 'Longitude coördinaat',
    aantal INT DEFAULT 1 COMMENT 'Aantal waargenomen exemplaren',
    waarnemer VARCHAR(100) COMMENT 'Naam van de waarnemer',
    bron VARCHAR(50) COMMENT 'Bron van de waarneming (bijv. waarnemingen.be)',
    media_url VARCHAR(255) COMMENT 'URL naar media (foto/video) van de waarneming',
    beschrijving TEXT COMMENT 'Extra beschrijving van de waarneming',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (soort_id) REFERENCES soort(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE seizoensanalyse (
    id INT AUTO_INCREMENT PRIMARY KEY,
    soort_id INT NOT NULL,
    seizoen ENUM('lente', 'zomer', 'herfst', 'winter') NOT NULL,
    jaar INT NOT NULL,
    waarnemingskans DECIMAL(5,2) COMMENT 'Percentage kans op waarneming in dit seizoen',
    analyse TEXT COMMENT 'Seizoensanalyse tekst',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (soort_id) REFERENCES soort(id) ON DELETE CASCADE,
    UNIQUE KEY unique_seizoen_soort (soort_id, seizoen, jaar)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_waarneming_datum ON waarneming(datum);
CREATE INDEX idx_waarneming_soort ON waarneming(soort_id);
CREATE INDEX idx_waarneming_plaats ON waarneming(plaatsnaam);
CREATE INDEX idx_seizoensanalyse_soort ON seizoensanalyse(soort_id);
CREATE INDEX idx_seizoensanalyse_jaar ON seizoensanalyse(jaar);

INSERT INTO soort (naam_nl, naam_lat, zeldzaamheid, beschrijving) VALUES
('Zevenstippelig lieveheersbeestje', 'Coccinella septempunctata', 'algemeen', 'Het meest voorkomende lieveheersbeestje in België. Rood met zeven zwarte stippen.'),
('Tweestippelig lieveheersbeestje', 'Adalia bipunctata', 'vrij algemeen', 'Kleiner dan het zevenstippelig lieveheersbeestje. Rood met twee zwarte stippen.'),
('Veelkleurig Aziatisch lieveheersbeestje', 'Harmonia axyridis', 'algemeen', 'Invasieve soort uit Azië. Zeer variabel in kleur en aantal stippen.');

INSERT INTO waarneming (soort_id, datum, plaatsnaam, lat, lon, aantal, waarnemer) VALUES
(1, '2024-03-15', 'Mons', 50.4542, 3.9522, 5, 'Yorbe'),
(2, '2024-03-15', 'Charleroi', 50.4108, 4.4445, 3, 'Yorbe'),
(3, '2024-03-15', 'La Louvière', 50.4797, 4.1879, 2, 'Yorbe');
