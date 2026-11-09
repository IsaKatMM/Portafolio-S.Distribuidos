package com.fleet.monitor.controller;

import com.fleet.monitor.model.GpsEntity;
import com.fleet.monitor.repository.GpsRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/fleet")
public class FleetController {

    @Autowired
    private GpsRepository gpsRepository;

    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> getFleetStatus() {
        Map<String, Object> status = new HashMap<>();
        long totalVehicles = gpsRepository.countDistinctVehicleId();
        long activeAlerts = 0; // Se puede ampliar con una tabla de alertas
        status.put("totalVehicles", totalVehicles);
        status.put("activeAlerts", activeAlerts);
        status.put("timestamp", new Date());
        return ResponseEntity.ok(status);
    }

    @GetMapping("/vehicle/{id}/telemetria")
    public ResponseEntity<List<Map<String, Object>>> getTelemetria(@PathVariable String id) {
        List<GpsEntity> registros = gpsRepository.findTop10ByVehicleId(id);
        List<Map<String, Object>> resultado = new ArrayList<>();
        for (GpsEntity g : registros) {
            Map<String, Object> punto = new HashMap<>();
            punto.put("vehicleId", g.getVehicleId());
            punto.put("lat", g.getLat());
            punto.put("lng", g.getLng());
            punto.put("speed", g.getSpeed());
            punto.put("timestamp", g.getTimestamp());
            resultado.add(punto);
        }
        return ResponseEntity.ok(resultado);
    }
}
