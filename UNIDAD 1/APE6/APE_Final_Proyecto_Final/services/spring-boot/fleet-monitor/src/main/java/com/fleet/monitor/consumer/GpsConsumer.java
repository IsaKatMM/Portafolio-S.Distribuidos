package com.fleet.monitor.consumer;

import com.fleet.monitor.config.RabbitMQConfig;
import com.fleet.monitor.model.GpsEntity;
import com.fleet.monitor.model.GpsMessage;
import com.fleet.monitor.repository.GpsRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
public class GpsConsumer {
    private static final Logger log = LoggerFactory.getLogger(GpsConsumer.class);
    private final GpsRepository gpsRepository;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public GpsConsumer(GpsRepository gpsRepository) {
        this.gpsRepository = gpsRepository;
    }

    @RabbitListener(queues = RabbitMQConfig.GPS_QUEUE)
    public void consumeGps(String message) {
        try {
            GpsMessage msg = objectMapper.readValue(message, GpsMessage.class);
            GpsEntity entity = new GpsEntity(msg.getVehicleId(), msg.getLat(), msg.getLng(), msg.getSpeed(), msg.getTimestamp());
            gpsRepository.save(entity);
            log.info("GPS guardado: {}", msg.getVehicleId());
        } catch (Exception e) {
            log.error("Error procesando GPS: {}", e.getMessage());
        }
    }
}
