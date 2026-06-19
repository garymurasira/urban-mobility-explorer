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

CREATE TABLE trips (
    trip_id INT PRIMARY KEY AUTO_INCREMENT,
    vendor_id INT,
    pickup_datetime DATETIME NOT NULL,
    dropoff_datetime DATETIME NOT NULL,
    passenger_count INT,
    trip_distance DECIMAL(8,2) NOT NULL,
    rate_code_id INT,
    pu_location_id INT NOT NULL,
    do_location_id INT NOT NULL,
    payment_type_id INT,
    fare_amount DECIMAL(8,2) NOT NULL,
    extra DECIMAL(8,2),
    mta_tax DECIMAL(8,2),
    tip_amount DECIMAL(8,2),
    tolls_amount DECIMAL(8,2),
    improvement_surcharge DECIMAL(8,2),
    congestion_surcharge DECIMAL(8,2),
    total_amount DECIMAL(8,2) NOT NULL,
    trip_duration_min DECIMAL(8,2),
    avg_speed_mph DECIMAL(8,2),
    fare_per_mile DECIMAL(8,2),
    tip_pct DECIMAL(6,4),
    is_cross_borough BOOLEAN,
    pickup_hour TINYINT,
    day_of_week TINYINT,

    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id),
    FOREIGN KEY (rate_code_id) REFERENCES rate_codes(rate_code_id),
    FOREIGN KEY (pu_location_id) REFERENCES zones(location_id),
    FOREIGN KEY (do_location_id) REFERENCES zones(location_id),
    FOREIGN KEY (payment_type_id) REFERENCES payment_types(payment_type_id)
) ENGINE=InnoDB;



CREATE INDEX idx_trips_pickup_datetime ON trips(pickup_datetime);
CREATE INDEX idx_trips_pu_location ON trips(pu_location_id);
CREATE INDEX idx_trips_do_location ON trips(do_location_id);
CREATE INDEX idx_trips_payment_type ON trips(payment_type_id);