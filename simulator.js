import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

class WheelchairSimulator {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.wheelchair = null;
        this.pathLine = null;
        this.pathPoints = [];
        this.ws = null;
        this.isConnected = false;
        
        // State
        this.state = {
            x: 0,
            y: 0,
            theta: 0,
            linear_velocity: 0,
            angular_velocity: 0,
            left_motor_speed: 0,
            right_motor_speed: 0,
            battery_voltage: 24.0,
            battery_percent: 100.0
        };

        this.init();
        this.setupUI();
        this.animate();
    }

    init() {
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x87ceeb);
        this.scene.fog = new THREE.Fog(0x87ceeb, 50, 200);

        // Camera
        this.camera = new THREE.PerspectiveCamera(
            60,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        this.camera.position.set(20, 10, 20);
        this.camera.lookAt(0, 0, 0);

        // Renderer
        const container = document.getElementById('canvas-container');
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(this.renderer.domElement);

        // Controls
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.maxPolarAngle = Math.PI / 2 - 0.1;
        this.controls.target.set(0, 0, 0);

        // Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(50, 50, 50);
        dirLight.castShadow = true;
        dirLight.shadow.camera.left = -50;
        dirLight.shadow.camera.right = 50;
        dirLight.shadow.camera.top = 50;
        dirLight.shadow.camera.bottom = -50;
        dirLight.shadow.camera.near = 0.1;
        dirLight.shadow.camera.far = 200;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        this.scene.add(dirLight);

        // Ground
        this.createGround();

        // Grid
        const gridHelper = new THREE.GridHelper(100, 100, 0x444444, 0x888888);
        this.scene.add(gridHelper);

        // Axes helper
        const axesHelper = new THREE.AxesHelper(5);
        this.scene.add(axesHelper);

        // Create wheelchair
        this.createWheelchair();

        // Create path trace
        this.createPathTrace();

        // Window resize handler
        window.addEventListener('resize', () => this.onWindowResize());

        // Hide loading screen
        document.getElementById('loading').classList.add('hidden');
    }

    createGround() {
        const groundGeometry = new THREE.PlaneGeometry(200, 200);
        const groundMaterial = new THREE.MeshStandardMaterial({
            color: 0x4a7c59,
            roughness: 0.8,
            metalness: 0.2
        });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        this.scene.add(ground);
    }

    createWheelchair() {
        this.wheelchair = new THREE.Group();

        // Main body (seat/base)
        const bodyGeometry = new THREE.BoxGeometry(0.8, 0.4, 1.0);
        const bodyMaterial = new THREE.MeshStandardMaterial({
            color: 0x2a5298,
            roughness: 0.5,
            metalness: 0.3
        });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.position.y = 0.6;
        body.castShadow = true;
        body.receiveShadow = true;
        this.wheelchair.add(body);

        // Backrest
        const backrestGeometry = new THREE.BoxGeometry(0.8, 0.8, 0.1);
        const backrestMaterial = new THREE.MeshStandardMaterial({
            color: 0x1e3c72,
            roughness: 0.6,
            metalness: 0.2
        });
        const backrest = new THREE.Mesh(backrestGeometry, backrestMaterial);
        backrest.position.set(0, 1.0, -0.45);
        backrest.castShadow = true;
        this.wheelchair.add(backrest);

        // Wheels
        const wheelGeometry = new THREE.CylinderGeometry(0.3, 0.3, 0.1, 16);
        const wheelMaterial = new THREE.MeshStandardMaterial({
            color: 0x333333,
            roughness: 0.9,
            metalness: 0.1
        });

        // Left wheel
        const leftWheel = new THREE.Mesh(wheelGeometry, wheelMaterial);
        leftWheel.rotation.z = Math.PI / 2;
        leftWheel.position.set(-0.5, 0.3, 0);
        leftWheel.castShadow = true;
        this.wheelchair.leftWheel = leftWheel;
        this.wheelchair.add(leftWheel);

        // Right wheel
        const rightWheel = new THREE.Mesh(wheelGeometry, wheelMaterial);
        rightWheel.rotation.z = Math.PI / 2;
        rightWheel.position.set(0.5, 0.3, 0);
        rightWheel.castShadow = true;
        this.wheelchair.rightWheel = rightWheel;
        this.wheelchair.add(rightWheel);

        // Small front wheels (casters)
        const casterGeometry = new THREE.SphereGeometry(0.1, 8, 8);
        const casterMaterial = new THREE.MeshStandardMaterial({
            color: 0x666666,
            roughness: 0.8
        });

        const frontLeftCaster = new THREE.Mesh(casterGeometry, casterMaterial);
        frontLeftCaster.position.set(-0.3, 0.1, 0.4);
        frontLeftCaster.castShadow = true;
        this.wheelchair.add(frontLeftCaster);

        const frontRightCaster = new THREE.Mesh(casterGeometry, casterMaterial);
        frontRightCaster.position.set(0.3, 0.1, 0.4);
        frontRightCaster.castShadow = true;
        this.wheelchair.add(frontRightCaster);

        // Direction indicator (arrow pointing forward)
        const arrowGeometry = new THREE.ConeGeometry(0.15, 0.4, 8);
        const arrowMaterial = new THREE.MeshStandardMaterial({
            color: 0xff4444,
            emissive: 0xff0000,
            emissiveIntensity: 0.5
        });
        const arrow = new THREE.Mesh(arrowGeometry, arrowMaterial);
        arrow.rotation.x = -Math.PI / 2;
        arrow.position.set(0, 1.2, 0.6);
        arrow.castShadow = true;
        this.wheelchair.add(arrow);

        this.scene.add(this.wheelchair);
    }

    createPathTrace() {
        // Note: The 'linewidth' property has no effect in WebGL for LineBasicMaterial.
        // If you need variable line width, use THREE.Line2 from three/examples/jsm/lines/Line2.js.
        const material = new THREE.LineBasicMaterial({
            color: 0xffff00,
            linewidth: 2, // No-op in WebGL
            transparent: true,
            opacity: 0.7
        });
        const geometry = new THREE.BufferGeometry();
        this.pathLine = new THREE.Line(geometry, material);
        this.scene.add(this.pathLine);
    }

    updatePathTrace() {
        if (this.pathPoints.length > 1000) {
            this.pathPoints.shift();
        }

        this.pathPoints.push(new THREE.Vector3(this.state.x, 0.05, this.state.y));

        const positions = new Float32Array(this.pathPoints.length * 3);
        this.pathPoints.forEach((point, i) => {
            positions[i * 3] = point.x;
            positions[i * 3 + 1] = point.y;
            positions[i * 3 + 2] = point.z;
        });

        this.pathLine.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        this.pathLine.geometry.attributes.position.needsUpdate = true;
    }

    setupUI() {
        // Connection
        const connectBtn = document.getElementById('connectBtn');
        const wsUrl = document.getElementById('wsUrl');

        connectBtn.addEventListener('click', () => {
            if (this.isConnected) {
                this.disconnect();
            } else {
                this.connect(wsUrl.value);
            }
        });

        // Reset button
        document.getElementById('resetBtn').addEventListener('click', () => {
            this.resetPosition();
        });

        // Camera controls
        const cameraDistance = document.getElementById('cameraDistance');
        const cameraDistanceValue = document.getElementById('cameraDistanceValue');
        cameraDistance.addEventListener('input', (e) => {
            const distance = parseFloat(e.target.value);
            cameraDistanceValue.textContent = distance;
            this.updateCameraPosition();
        });

        const cameraHeight = document.getElementById('cameraHeight');
        const cameraHeightValue = document.getElementById('cameraHeightValue');
        cameraHeight.addEventListener('input', (e) => {
            const height = parseFloat(e.target.value);
            cameraHeightValue.textContent = height;
            this.updateCameraPosition();
        });

        // Show trace toggle
        document.getElementById('showTrace').addEventListener('change', (e) => {
            this.pathLine.visible = e.target.checked;
        });
    }

    updateCameraPosition() {
        const distance = parseFloat(document.getElementById('cameraDistance').value);
        const height = parseFloat(document.getElementById('cameraHeight').value);
        
        const angle = Math.PI / 4;
        this.camera.position.set(
            distance * Math.cos(angle),
            height,
            distance * Math.sin(angle)
        );
        this.controls.target.set(this.state.x, 0, this.state.y);
        this.controls.update();
    }

    connect(url) {
        try {
            this.ws = new WebSocket(url);

            this.ws.onopen = () => {
                console.log('Connected to emulator');
                this.isConnected = true;
                this.updateConnectionStatus(true);
                document.getElementById('connectBtn').textContent = 'Disconnect';
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.updateState(data);
                } catch (e) {
                    console.error('Error parsing message:', e);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus(false);
            };

            this.ws.onclose = () => {
                console.log('Disconnected from emulator');
                this.isConnected = false;
                this.updateConnectionStatus(false);
                document.getElementById('connectBtn').textContent = 'Connect to Emulator';
            };
        } catch (error) {
            console.error('Connection error:', error);
            alert('Failed to connect to emulator. Make sure the WebSocket server is running.');
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    updateConnectionStatus(connected) {
        const indicator = document.getElementById('statusIndicator');
        const text = document.getElementById('statusText');
        
        if (connected) {
            indicator.classList.add('connected');
            indicator.classList.remove('disconnected');
            text.textContent = 'Connected';
        } else {
            indicator.classList.remove('connected');
            indicator.classList.add('disconnected');
            text.textContent = 'Disconnected';
        }
    }

    updateState(data) {
        // Update state
        this.state = { ...this.state, ...data };

        // Update wheelchair position and orientation
        this.wheelchair.position.set(this.state.x, 0, this.state.y);
        this.wheelchair.rotation.y = -this.state.theta;

        // Animate wheels based on motor speeds
        if (this.wheelchair.leftWheel) {
            this.wheelchair.leftWheel.rotation.x += this.state.left_motor_speed * 0.1;
        }
        if (this.wheelchair.rightWheel) {
            this.wheelchair.rightWheel.rotation.x += this.state.right_motor_speed * 0.1;
        }

        // Update path trace
        if (document.getElementById('showTrace').checked) {
            this.updatePathTrace();
        }

        // Update UI
        this.updateUI();
    }

    updateUI() {
        document.getElementById('posX').textContent = `${this.state.x.toFixed(2)} m`;
        document.getElementById('posY').textContent = `${this.state.y.toFixed(2)} m`;
        document.getElementById('heading').textContent = `${(this.state.theta * 180 / Math.PI).toFixed(1)}°`;
        
        document.getElementById('linearVel').textContent = `${this.state.linear_velocity.toFixed(2)} m/s`;
        document.getElementById('angularVel').textContent = `${this.state.angular_velocity.toFixed(2)} rad/s`;
        
        document.getElementById('leftMotor').textContent = `${(this.state.left_motor_speed * 100).toFixed(0)}%`;
        document.getElementById('rightMotor').textContent = `${(this.state.right_motor_speed * 100).toFixed(0)}%`;
        
        document.getElementById('batteryVoltage').textContent = `${this.state.battery_voltage.toFixed(1)} V`;
        document.getElementById('batteryPercent').textContent = `${this.state.battery_percent.toFixed(0)}%`;
    }

    resetPosition() {
        this.state.x = 0;
        this.state.y = 0;
        this.state.theta = 0;
        this.wheelchair.position.set(0, 0, 0);
        this.wheelchair.rotation.y = 0;
        this.pathPoints = [];
        this.pathLine.geometry.setFromPoints([]);
        this.controls.target.set(0, 0, 0);
        this.updateUI();
    }

    onWindowResize() {
        const container = document.getElementById('canvas-container');
        this.camera.aspect = container.clientWidth / container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(container.clientWidth, container.clientHeight);
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
}

// Initialize simulator when page loads
window.addEventListener('DOMContentLoaded', () => {
    new WheelchairSimulator();
});
