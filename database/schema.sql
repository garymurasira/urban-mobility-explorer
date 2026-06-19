CREATE TABLE zones (
    location_id INT PRIMARY KEY,
    borough VARCHAR(50) NOT NULL,
    zone VARCHAR(100) NOT NULL,
    service_zone VARCHAR(50),
    centroid_lat DECIMAL(9,6),
    centroid_lon DECIMAL(9,6)
) ENGINE=InnoDB;

CREATE TABLE vendors (
    vendor_id INT PRIMARY KEY,
    vendor_name VARCHAR(50) NOT NULL
) ENGINE=InnoDB;



CREATE TABLE rate_codes (
    rate_code_id INT PRIMARY KEY,
    description VARCHAR(50) NOT NULL
) ENGINE=InnoDB;


CREATE TABLE payment_types (
    payment_type_id INT PRIMARY KEY,
    description VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

