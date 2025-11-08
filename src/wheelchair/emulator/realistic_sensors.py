"""Enhanced realistic sensor suite with comprehensive sensor simulation."""

import math
import random
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from wheelchair.interfaces import SensorSuite, SensorData, WheelchairState
from wheelchair.config import SensorConfig


@dataclass
class GPSData:
    """GPS sensor data."""
    latitude: float = 0.0
    longitude: float = 0.0
    altitude: float = 0.0
    accuracy: float = 3.0  # meters
    satellites: int = 8
    hdop: float = 1.0


@dataclass
class CameraData:
    """Simulated camera sensor data."""
    objects_detected: List[Dict] = field(default_factory=list)
    lanes_detected: bool = False
    lane_deviation: float = 0.0  # meters from center
    visibility: float = 1.0  # 0.0 = no visibility, 1.0 = perfect


@dataclass
class LidarData:
    """LiDAR sensor data."""
    distances: List[float] = field(default_factory=list)  # 360 degree scan
    angles: List[float] = field(default_factory=list)
    intensity: List[float] = field(default_factory=list)
    scan_time: float = 0.0


@dataclass
class EnhancedSensorData(SensorData):
    """Extended sensor data with additional realistic sensors."""
    
    # GPS data
    gps: GPSData = field(default_factory=GPSData)
    
    # Camera data
    camera: CameraData = field(default_factory=CameraData)
    
    # LiDAR data
    lidar: LidarData = field(default_factory=LidarData)
    
    # Enhanced IMU data
    magnetometer_x: float = 0.0
    magnetometer_y: float = 0.0
    magnetometer_z: float = 0.0
    
    # Encoder data (wheel encoders)
    left_encoder_ticks: int = 0
    right_encoder_ticks: int = 0
    left_encoder_velocity: float = 0.0
    right_encoder_velocity: float = 0.0
    
    # Battery/electrical sensors
    battery_voltage: float = 24.0
    battery_current: float = 0.0
    battery_temperature: float = 25.0
    motor_temperatures: Tuple[float, float] = (25.0, 25.0)
    
    # Environmental sensors
    ambient_temperature: float = 20.0
    humidity: float = 0.5
    barometric_pressure: float = 1013.25  # hPa
    
    # System health
    cpu_temperature: float = 45.0
    system_load: float = 0.3
    available_memory: float = 0.7  # fraction available


class RealisticSensorSuite(SensorSuite):
    """
    Enhanced sensor suite with comprehensive sensor simulation.
    
    Features:
    - Realistic IMU with bias drift and temperature effects
    - GPS simulation with multipath and atmospheric effects
    - LiDAR simulation with environmental obstacles
    - Camera simulation with object detection
    - Wheel encoders with realistic noise and slip detection
    - Environmental sensors (temperature, humidity, pressure)
    - System health monitoring
    """

    def __init__(self, config: SensorConfig, state: WheelchairState, seed: int = None):
        """Initialize enhanced sensor suite."""
        self.config = config
        self.state = state
        self._rng = random.Random(seed)
        self._sensor_data = EnhancedSensorData()
        
        # Sensor update timing
        self._time_since_proximity_update = 0.0
        self._time_since_gps_update = 0.0
        self._time_since_lidar_update = 0.0
        self._time_since_camera_update = 0.0
        
        # IMU state (bias drift, etc.)
        self._imu_bias_x = 0.0
        self._imu_bias_y = 0.0
        self._imu_bias_z = 0.0
        self._gyro_bias_x = 0.0
        self._gyro_bias_y = 0.0
        self._gyro_bias_z = 0.0
        
        # GPS state
        self._gps_base_lat = 37.7749  # San Francisco coordinates as example
        self._gps_base_lon = -122.4194
        self._gps_base_alt = 10.0
        
        # Encoder state
        self._left_encoder_count = 0
        self._right_encoder_count = 0
        self._encoder_resolution = 1000  # ticks per wheel revolution
        
        # Environmental simulation
        self._world_obstacles = self._generate_world_obstacles()
        
        # Magnetometer calibration (simulate hard/soft iron effects)
        self._mag_hard_iron = [0.1, -0.05, 0.02]  # Bias offset
        self._mag_soft_iron = [[1.0, 0.01, 0.01],  # Scale/cross-axis errors
                               [0.01, 1.02, 0.01],
                               [0.01, 0.01, 0.98]]

    def read_sensors(self) -> EnhancedSensorData:
        """Read all sensor data."""
        return self._sensor_data

    def update(self, dt: float) -> None:
        """Update all sensors with realistic timing and noise."""
        # Update IMU at high frequency (typically 100-1000 Hz)
        self._update_imu(dt)
        
        # Update encoders at high frequency
        self._update_encoders(dt)
        
        # Update proximity sensors at medium frequency
        self._time_since_proximity_update += dt
        if self._time_since_proximity_update >= 1.0 / self.config.proximity_update_rate:
            self._time_since_proximity_update = 0.0
            self._update_proximity_sensors()
        
        # Update GPS at low frequency (1-10 Hz)
        self._time_since_gps_update += dt
        if self._time_since_gps_update >= 0.1:  # 10 Hz
            self._time_since_gps_update = 0.0
            self._update_gps()
        
        # Update LiDAR at medium frequency (10-40 Hz)
        self._time_since_lidar_update += dt
        if self._time_since_lidar_update >= 0.05:  # 20 Hz
            self._time_since_lidar_update = 0.0
            self._update_lidar()
        
        # Update camera at lower frequency (30 Hz)
        self._time_since_camera_update += dt
        if self._time_since_camera_update >= 0.033:  # 30 Hz
            self._time_since_camera_update = 0.0
            self._update_camera()
        
        # Update environmental and system sensors
        self._update_environmental_sensors(dt)
        self._update_system_health(dt)
        self._update_battery_sensors(dt)

    def _update_imu(self, dt: float) -> None:
        """Update IMU with realistic physics and noise models."""
        # Simulate IMU bias drift (temperature dependent)
        temp_effect = (self._sensor_data.ambient_temperature - 25.0) * 0.0001
        bias_drift_rate = 0.001 + abs(temp_effect)
        
        self._imu_bias_x += self._rng.gauss(0.0, bias_drift_rate) * dt
        self._imu_bias_y += self._rng.gauss(0.0, bias_drift_rate) * dt
        self._imu_bias_z += self._rng.gauss(0.0, bias_drift_rate) * dt
        
        # Gyroscope bias drift
        self._gyro_bias_x += self._rng.gauss(0.0, 0.01) * dt
        self._gyro_bias_y += self._rng.gauss(0.0, 0.01) * dt
        self._gyro_bias_z += self._rng.gauss(0.0, 0.01) * dt
        
        # Accelerometer - include gravity, linear acceleration, and vibration
        gravity_x = -9.81 * math.sin(self.state.theta)  # Simplified tilt
        gravity_y = 0.0  # Assume no roll
        gravity_z = -9.81 * math.cos(self.state.theta)
        
        # Linear acceleration (derivative of velocity)
        if hasattr(self, '_last_velocity'):
            linear_accel = (self.state.linear_velocity - self._last_velocity) / dt
        else:
            linear_accel = 0.0
        self._last_velocity = self.state.linear_velocity
        
        # Add motor vibration
        vibration_freq = 30.0  # Hz
        vibration_amplitude = abs(self.state.linear_velocity) * 0.1
        vibration = vibration_amplitude * math.sin(time.time() * 2 * math.pi * vibration_freq)
        
        # Apply to accelerometer
        self._sensor_data.accel_x = self._add_noise(
            gravity_x + linear_accel + self._imu_bias_x + vibration,
            self.config.imu_noise_stddev
        )
        self._sensor_data.accel_y = self._add_noise(
            gravity_y + self._imu_bias_y + vibration,
            self.config.imu_noise_stddev
        )
        self._sensor_data.accel_z = self._add_noise(
            gravity_z + self._imu_bias_z + vibration,
            self.config.imu_noise_stddev
        )
        
        # Gyroscope
        self._sensor_data.gyro_x = self._add_noise(self._gyro_bias_x, 0.01)
        self._sensor_data.gyro_y = self._add_noise(self._gyro_bias_y, 0.01)
        self._sensor_data.gyro_z = self._add_noise(
            self.state.angular_velocity + self._gyro_bias_z, 0.01
        )
        
        # Magnetometer (simulated with hard/soft iron effects)
        self._update_magnetometer()

    def _update_magnetometer(self) -> None:
        """Update magnetometer with realistic distortions."""
        # Earth's magnetic field (simplified)
        mag_field_strength = 50.0  # microTesla
        magnetic_declination = 0.2  # radians (local declination)
        
        # Ideal magnetic field in body frame
        mag_x_ideal = mag_field_strength * math.cos(self.state.theta + magnetic_declination)
        mag_y_ideal = mag_field_strength * math.sin(self.state.theta + magnetic_declination)
        mag_z_ideal = 30.0  # Vertical component
        
        # Apply hard iron effects (constant offset)
        mag_x = mag_x_ideal + self._mag_hard_iron[0]
        mag_y = mag_y_ideal + self._mag_hard_iron[1]
        mag_z = mag_z_ideal + self._mag_hard_iron[2]
        
        # Apply soft iron effects (scaling and cross-axis coupling)
        mag_corrected = [
            self._mag_soft_iron[0][0] * mag_x + self._mag_soft_iron[0][1] * mag_y + self._mag_soft_iron[0][2] * mag_z,
            self._mag_soft_iron[1][0] * mag_x + self._mag_soft_iron[1][1] * mag_y + self._mag_soft_iron[1][2] * mag_z,
            self._mag_soft_iron[2][0] * mag_x + self._mag_soft_iron[2][1] * mag_y + self._mag_soft_iron[2][2] * mag_z,
        ]
        
        # Add noise
        self._sensor_data.magnetometer_x = self._add_noise(mag_corrected[0], 0.5)
        self._sensor_data.magnetometer_y = self._add_noise(mag_corrected[1], 0.5)
        self._sensor_data.magnetometer_z = self._add_noise(mag_corrected[2], 0.5)

    def _update_encoders(self, dt: float) -> None:
        """Update wheel encoders with realistic characteristics."""
        # Calculate theoretical wheel rotations
        wheel_circumference = 2 * math.pi * 0.15  # Wheel radius from config
        
        left_rotations = (self.state.left_motor_speed * self.state.linear_velocity * dt) / wheel_circumference
        right_rotations = (self.state.right_motor_speed * self.state.linear_velocity * dt) / wheel_circumference
        
        # Add encoder noise and quantization
        encoder_noise = 0.01  # 1% noise
        left_ticks = int(left_rotations * self._encoder_resolution * 
                        (1.0 + self._rng.gauss(0.0, encoder_noise)))
        right_ticks = int(right_rotations * self._encoder_resolution * 
                         (1.0 + self._rng.gauss(0.0, encoder_noise)))
        
        # Update encoder counts
        self._left_encoder_count += left_ticks
        self._right_encoder_count += right_ticks
        
        # Calculate velocities from encoder data
        if dt > 0:
            self._sensor_data.left_encoder_velocity = (left_ticks / self._encoder_resolution) * wheel_circumference / dt
            self._sensor_data.right_encoder_velocity = (right_ticks / self._encoder_resolution) * wheel_circumference / dt
        
        self._sensor_data.left_encoder_ticks = self._left_encoder_count
        self._sensor_data.right_encoder_ticks = self._right_encoder_count

    def _update_gps(self) -> None:
        """Update GPS with realistic error models."""
        # Convert local position to GPS coordinates (simplified)
        meters_per_degree_lat = 111320.0
        meters_per_degree_lon = 111320.0 * math.cos(math.radians(self._gps_base_lat))
        
        lat_offset = self.state.y / meters_per_degree_lat
        lon_offset = self.state.x / meters_per_degree_lon
        
        # GPS accuracy depends on satellite count and atmospheric conditions
        base_accuracy = 3.0
        atmospheric_error = self._rng.uniform(0.5, 2.0)  # Ionospheric delays
        multipath_error = self._rng.uniform(0.0, 1.5)    # Urban multipath
        
        total_accuracy = base_accuracy + atmospheric_error + multipath_error
        
        # Add GPS noise based on accuracy
        gps_noise = total_accuracy / 3.0  # Convert accuracy to 1-sigma noise
        
        self._sensor_data.gps.latitude = self._add_noise(
            self._gps_base_lat + lat_offset, gps_noise / meters_per_degree_lat
        )
        self._sensor_data.gps.longitude = self._add_noise(
            self._gps_base_lon + lon_offset, gps_noise / meters_per_degree_lon
        )
        self._sensor_data.gps.altitude = self._add_noise(self._gps_base_alt, gps_noise)
        self._sensor_data.gps.accuracy = total_accuracy
        
        # Simulate satellite count (affects accuracy)
        self._sensor_data.gps.satellites = max(4, min(12, int(self._rng.gauss(8, 2))))
        self._sensor_data.gps.hdop = max(0.8, min(4.0, self._rng.gauss(1.5, 0.5)))

    def _update_lidar(self) -> None:
        """Update LiDAR sensor with 360-degree scan."""
        num_rays = 360  # 1 degree resolution
        max_range = 30.0  # meters
        
        distances = []
        angles = []
        intensities = []
        
        for i in range(num_rays):
            angle = math.radians(i)
            world_angle = self.state.theta + angle
            
            # Cast ray and check for obstacles
            distance = self._cast_lidar_ray(world_angle, max_range)
            
            # Add noise based on distance and surface properties
            distance_noise = 0.02 + distance * 0.001  # Noise increases with distance
            noisy_distance = self._add_noise(distance, distance_noise)
            
            distances.append(max(0.1, min(max_range, noisy_distance)))
            angles.append(angle)
            
            # Simulate intensity based on surface reflectivity
            intensity = self._rng.uniform(0.3, 1.0)
            intensities.append(intensity)
        
        self._sensor_data.lidar.distances = distances
        self._sensor_data.lidar.angles = angles
        self._sensor_data.lidar.intensity = intensities
        self._sensor_data.lidar.scan_time = time.time()

    def _cast_lidar_ray(self, angle: float, max_range: float) -> float:
        """Cast a single LiDAR ray and return distance to obstacle."""
        step_size = 0.1  # meters
        
        for distance in [step_size * i for i in range(int(max_range / step_size))]:
            ray_x = self.state.x + distance * math.cos(angle)
            ray_y = self.state.y + distance * math.sin(angle)
            
            # Check against world obstacles
            for obstacle in self._world_obstacles:
                obs_x, obs_y, obs_radius = obstacle
                if math.sqrt((ray_x - obs_x)**2 + (ray_y - obs_y)**2) < obs_radius:
                    return distance
        
        return max_range

    def _update_camera(self) -> None:
        """Update camera sensor with object detection simulation."""
        # Simulate object detection in field of view
        fov_angle = math.radians(60)  # 60 degree field of view
        detection_range = 10.0  # meters
        
        objects = []
        
        # Check for objects in camera field of view
        for obstacle in self._world_obstacles:
            obs_x, obs_y, obs_radius = obstacle
            
            # Calculate relative position
            rel_x = obs_x - self.state.x
            rel_y = obs_y - self.state.y
            distance = math.sqrt(rel_x**2 + rel_y**2)
            
            if distance < detection_range:
                # Check if in field of view
                angle_to_object = math.atan2(rel_y, rel_x)
                relative_angle = angle_to_object - self.state.theta
                
                # Normalize angle
                while relative_angle > math.pi:
                    relative_angle -= 2 * math.pi
                while relative_angle < -math.pi:
                    relative_angle += 2 * math.pi
                
                if abs(relative_angle) < fov_angle / 2:
                    # Object detected
                    confidence = max(0.5, 1.0 - distance / detection_range)
                    objects.append({
                        "type": "obstacle",
                        "distance": distance,
                        "angle": relative_angle,
                        "confidence": confidence,
                        "size": obs_radius * 2
                    })
        
        self._sensor_data.camera.objects_detected = objects
        
        # Simulate visibility based on environmental conditions
        base_visibility = 1.0
        # Weather effects would go here
        self._sensor_data.camera.visibility = base_visibility

    def _update_proximity_sensors(self) -> None:
        """Update proximity sensors with enhanced obstacle detection."""
        sensor_positions = {
            "front": (0.3, 0.0),    # 30cm in front of center
            "rear": (-0.3, 0.0),    # 30cm behind center
            "left": (0.0, 0.3),     # 30cm to the left
            "right": (0.0, -0.3)    # 30cm to the right
        }
        
        for sensor_name, (local_x, local_y) in sensor_positions.items():
            # Transform sensor position to world coordinates
            world_x = (self.state.x + 
                      local_x * math.cos(self.state.theta) - 
                      local_y * math.sin(self.state.theta))
            world_y = (self.state.y + 
                      local_x * math.sin(self.state.theta) + 
                      local_y * math.cos(self.state.theta))
            
            min_distance = self.config.proximity_range
            
            # Check distance to all obstacles
            for obstacle in self._world_obstacles:
                obs_x, obs_y, obs_radius = obstacle
                distance = math.sqrt((world_x - obs_x)**2 + (world_y - obs_y)**2) - obs_radius
                
                if distance > 0 and distance < min_distance:
                    min_distance = distance
            
            # Add noise and set sensor reading
            if min_distance < self.config.proximity_range:
                noisy_distance = self._add_noise(min_distance, self.config.proximity_noise_stddev)
                noisy_distance = max(0.0, min(self.config.proximity_range, noisy_distance))
                setattr(self._sensor_data, f"proximity_{sensor_name}", noisy_distance)
            else:
                setattr(self._sensor_data, f"proximity_{sensor_name}", None)

    def _update_environmental_sensors(self, dt: float) -> None:
        """Update environmental sensors."""
        # Simulate temperature drift
        self._sensor_data.ambient_temperature += self._rng.gauss(0.0, 0.1) * dt
        
        # Simulate humidity changes
        self._sensor_data.humidity = max(0.0, min(1.0, 
            self._sensor_data.humidity + self._rng.gauss(0.0, 0.01) * dt))
        
        # Simulate barometric pressure changes
        self._sensor_data.barometric_pressure += self._rng.gauss(0.0, 0.1) * dt

    def _update_system_health(self, dt: float) -> None:
        """Update system health monitoring."""
        # Simulate CPU temperature based on load
        load_factor = abs(self.state.linear_velocity) / 2.0  # Normalize to load
        base_temp = 35.0 + self._sensor_data.ambient_temperature
        load_temp = load_factor * 20.0
        
        self._sensor_data.cpu_temperature = base_temp + load_temp + self._rng.gauss(0.0, 1.0)
        
        # Simulate system load
        self._sensor_data.system_load = max(0.1, min(1.0, 
            0.3 + load_factor * 0.4 + self._rng.gauss(0.0, 0.1)))
        
        # Simulate memory usage
        self._sensor_data.available_memory = max(0.1, min(1.0,
            0.7 - load_factor * 0.2 + self._rng.gauss(0.0, 0.05)))

    def _update_battery_sensors(self, dt: float) -> None:
        """Update battery and electrical sensors."""
        # Simulate battery voltage drop under load
        load_factor = abs(self.state.linear_velocity) / 2.0
        base_voltage = 24.0
        voltage_drop = load_factor * 1.5
        
        self._sensor_data.battery_voltage = base_voltage - voltage_drop + self._rng.gauss(0.0, 0.1)
        
        # Simulate current draw
        self._sensor_data.battery_current = load_factor * 10.0 + self._rng.gauss(0.0, 0.5)
        
        # Battery temperature
        self._sensor_data.battery_temperature = (self._sensor_data.ambient_temperature + 
                                               self._sensor_data.battery_current * 0.1 +
                                               self._rng.gauss(0.0, 0.5))

    def _generate_world_obstacles(self) -> List[Tuple[float, float, float]]:
        """Generate a simple world with obstacles for testing."""
        obstacles = []
        
        # Add some random obstacles
        for _ in range(10):
            x = self._rng.uniform(-20, 20)
            y = self._rng.uniform(-20, 20)
            radius = self._rng.uniform(0.5, 2.0)
            obstacles.append((x, y, radius))
        
        # Add walls
        for x in [-25, 25]:
            for y in range(-25, 25, 2):
                obstacles.append((x, y, 0.5))
        
        for y in [-25, 25]:
            for x in range(-25, 25, 2):
                obstacles.append((x, y, 0.5))
        
        return obstacles

    def _add_noise(self, value: float, stddev: float) -> float:
        """Add Gaussian noise to a value."""
        return value + self._rng.gauss(0.0, stddev)

    # Enhanced control methods
    def inject_gps_error(self, error_type: str, magnitude: float) -> None:
        """Inject GPS errors for testing."""
        if error_type == "multipath":
            self._sensor_data.gps.accuracy += magnitude
        elif error_type == "atmospheric":
            # Add systematic bias
            self._sensor_data.gps.latitude += magnitude / 111320.0
            self._sensor_data.gps.longitude += magnitude / 111320.0

    def set_visibility(self, visibility: float) -> None:
        """Set camera visibility (0.0 = no visibility, 1.0 = perfect)."""
        self._sensor_data.camera.visibility = max(0.0, min(1.0, visibility))

    def get_sensor_diagnostics(self) -> Dict:
        """Get comprehensive sensor diagnostics."""
        return {
            "imu": {
                "bias_x": self._imu_bias_x,
                "bias_y": self._imu_bias_y,
                "bias_z": self._imu_bias_z,
                "gyro_bias_z": self._gyro_bias_z,
            },
            "gps": {
                "accuracy": self._sensor_data.gps.accuracy,
                "satellites": self._sensor_data.gps.satellites,
                "hdop": self._sensor_data.gps.hdop,
            },
            "encoders": {
                "left_count": self._left_encoder_count,
                "right_count": self._right_encoder_count,
                "resolution": self._encoder_resolution,
            },
            "system": {
                "cpu_temp": self._sensor_data.cpu_temperature,
                "system_load": self._sensor_data.system_load,
                "memory_available": self._sensor_data.available_memory,
            }
        }