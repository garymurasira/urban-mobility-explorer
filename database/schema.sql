CREATE TABLE zones (
    location_id   INT PRIMARY KEY,
    borough       VARCHAR(50) NOT NULL,
    zone          VARCHAR(100) NOT NULL,
    service_zone  VARCHAR(50),
    centroid_lat  DECIMAL(9,6),
    centroid_lon  DECIMAL(9,6)
) ENGINE=InnoDB;