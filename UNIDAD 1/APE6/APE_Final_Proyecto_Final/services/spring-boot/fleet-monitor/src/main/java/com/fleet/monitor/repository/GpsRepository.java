package com.fleet.monitor.repository;

import com.fleet.monitor.model.GpsEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface GpsRepository extends JpaRepository<GpsEntity, Long> {

    @Query(value = "SELECT COUNT(DISTINCT vehicle_id) FROM gps_data", nativeQuery = true)
    Long countDistinctVehicleId();

    @Query("SELECT g FROM GpsEntity g WHERE g.vehicleId = ?1 ORDER BY g.id DESC")
    List<GpsEntity> findTop10ByVehicleId(String vehicleId);
}
