CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.gios_measurements (
    sensor_id       integer         NOT NULL,
    station_code    text            NOT NULL,
    measured_local  text            NOT NULL,
    measured_at     timestamptz     NOT NULL,
    value           double precision,
    payload         jsonb           NOT NULL,
    first_seen_at   timestamptz     NOT NULL    DEFAULT now(),
    last_seen_at    timestamptz     NOT NULL    DEFAULT now(),
    PRIMARY KEY   (sensor_id, measured_at)
);

CREATE TABLE IF NOT EXISTS raw.openmeteo_forecasts (
    station_id      integer             NOT NULL,
    fetched_hour    timestamptz         NOT NULL,
    fetched_at      timestamptz         NOT NULL,
    latitude        double precision    NOT NULL,
    longtitude      double precision    NOT NULL,
    request_params  jsonb               NOT NULL,
    payload         jsonb               NOT NULL,
    PRIMARY KEY (station_id, fetched_hour)
);