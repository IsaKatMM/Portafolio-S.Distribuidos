package com.fleet.monitor.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "gps_data")
public class GpsEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String vehicleId;
    private double lat;
    private double lng;
    private double speed;
    private String timestamp;

    public GpsEntity() {}
    public GpsEntity(String vehicleId, double lat, double lng, double speed, String timestamp) {
        this.vehicleId = vehicleId;
        this.lat = lat;
        this.lng = lng;
        this.speed = speed;
        this.timestamp = timestamp;
    }
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getVehicleId() { return vehicleId; }
    public void setVehicleId(String vehicleId) { this.vehicleId = vehicleId; }
    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }
    public double getLat() { return lat; }
    public void setLat(double lat) { this.lat = lat; }
    public double getLng() { return lng; }
    public void setLng(double lng) { this.lng = lng; }
    public double getSpeed() { return speed; }
    public void setSpeed(double speed) { this.speed = speed; }
}
