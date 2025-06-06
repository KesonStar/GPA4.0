Reference code for importing the 3Djs library.
```
"three": "https://cdn.jsdelivr.net/npm/three@0.174.0/build/three.module.js",
"three/addons/": "https://cdn.jsdelivr.net/npm/three@0.174.0/examples/jsm/"
```


Reference code for the 3D model viewer.
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Model Viewer</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <script async src="https://unpkg.com/es-module-shims@1.6.3/dist/es-module-shims.js"></script>
    <script type="importmap">
        {
          "imports": {
            "three": "https://cdn.jsdelivr.net/npm/three@0.174.0/build/three.module.js",
            "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.174.0/examples/jsm/"
          }
        }
      </script>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            overflow: hidden;
            width: 100%;
            height: 100%;
        }
        #info {
            position: absolute;
            top: 10px;
            width: 100%;
            text-align: center;
            color: white;
            z-index: 100;
        }
        #info a {
            color: #f0f0f0;
        }
        #scene-container {
            position: absolute;
            width: 100%;
            height: 100%;
        }
        .btn-back {
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 100;
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
        }
        #loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            color: white;
            background-color: rgba(0, 0, 0, 0.7);
            padding: 20px;
            border-radius: 10px;
            z-index: 200;
        }
        #progress-bar {
            width: 300px;
            height: 20px;
            background-color: #333;
            border-radius: 10px;
            margin: 10px auto;
            overflow: hidden;
        }
        #progress {
            height: 100%;
            width: 0%;
            background-color: #3498db;
            transition: width 0.3s;
        }
        #gui-container {
            position: absolute;
            top: 50px;
            right: 10px;
            z-index: 150;
        }
        #menu {
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            border-radius: 5px;
            padding: 15px;
            width: 200px;
            z-index: 100;
        }
        #menu h3 {
            margin-top: 0;
            margin-bottom: 10px;
            color: #3498db;
            border-bottom: 1px solid #555;
            padding-bottom: 5px;
        }
        .control-group {
            margin-bottom: 15px;
        }
        .view-buttons {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 5px;
            margin-bottom: 10px;
        }
        .view-btn {
            flex: 1;
            background: #3498db;
            color: white;
            border: none;
            padding: 5px;
            border-radius: 3px;
            cursor: pointer;
        }
        .view-btn:hover {
            background: #2980b9;
        }
        .control-label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="range"] {
            width: 100%;
        }
        select {
            width: 100%;
            padding: 5px;
            background-color: #333;
            color: white;
            border: 1px solid #555;
            border-radius: 3px;
        }
        .range-value {
            display: inline-block;
            width: 40px;
            text-align: right;
        }
        #controls {
            position: absolute;
            bottom: 20px;
            right: 20px;
            background-color: rgba(0, 0, 0, 0.5);
            padding: 10px;
            border-radius: 5px;
            z-index: 100;
            color: white;
        }
    </style>
</head>
<body>
    <a href="{{ url_for('index') }}" class="btn-back">Back to Home</a>
    <div id="info">
        <span id="model-name">3D Model Viewer</span>
    </div>
    <div id="scene-container"></div>
    <div id="loading">
        <div>Loading 3D Model...</div>
        <div id="progress-bar"><div id="progress"></div></div>
        <div id="progress-text">0%</div>
    </div>
    <div id="menu">
        <h3>Model Controls</h3>
        <div class="control-group">
            <div class="view-buttons">
                <button id="view-front" class="view-btn">Front</button>
                <button id="view-back" class="view-btn">Back</button>
                <button id="view-left" class="view-btn">Left</button>
                <button id="view-right" class="view-btn">Right</button>
                <button id="view-top" class="view-btn">Top</button>
                <button id="view-bottom" class="view-btn">Bottom</button>
                <button id="reset-camera" class="view-btn" style="grid-column: span 3; background-color: #e67e22;">Reset Camera</button>
            </div>
        </div>
        
        <div class="control-group">
            <label class="control-label">Scale: <span id="scale-value" class="range-value">1.0</span></label>
            <input type="range" id="scale" min="0.1" max="5" step="0.1" value="1">
        </div>
        
        <div class="control-group">
            <label class="control-label">Position Y: <span id="position-y-value" class="range-value">0.0</span></label>
            <input type="range" id="position-y" min="-5" max="5" step="0.1" value="0">
        </div>
        
        <div class="control-group">
            <label class="control-label">Model Rotation</label>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px; margin-top: 5px;">
                <button id="rotate-x-minus" class="view-btn">X-</button>
                <button id="rotate-y-minus" class="view-btn">Y-</button>
                <button id="rotate-z-minus" class="view-btn">Z-</button>
                <button id="rotate-x-plus" class="view-btn">X+</button>
                <button id="rotate-y-plus" class="view-btn">Y+</button>
                <button id="rotate-z-plus" class="view-btn">Z+</button>
            </div>
        </div>
        
        <div class="control-group">
            <label class="control-label">Rotation Speed:</label>
            <input type="range" id="rotation-speed" min="0" max="5" step="0.5" value="2">
        </div>
        
        <div class="control-group">
            <label class="control-label">Background:</label>
            <select id="background-color">
                <option value="0x1a1a1a">Dark</option>
                <option value="0x000000">Black</option>
                <option value="0xffffff">White</option>
                <option value="0x2c3e50">Navy</option>
                <option value="0x27ae60">Green</option>
            </select>
        </div>
        
        <div class="control-group">
            <label>
                <input type="checkbox" id="autoRotate"> Auto-rotate
            </label>
        </div>
        
        <div class="control-group">
            <label>
                <input type="checkbox" id="wireframe"> Wireframe
            </label>
        </div>
        
        <div class="control-group">
            <button id="reset-model" style="width: 100%; background: #e74c3c; color: white; border: none; padding: 5px; border-radius: 3px; cursor: pointer;">Reset Model</button>
        </div>
    </div>

    <script type="module">
        import * as THREE from 'three';
        import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
        import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
        import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
        import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

        // Define THREE.js path
        const THREE_VERSION = '0.174.0';
        const THREE_PATH = `https://unpkg.com/three@${THREE_VERSION}`;
        
        // Get the model path from the Flask template
        const modelPath = "{{ model_path }}";
        const modelNameParts = modelPath.split('/');
        const modelName = modelNameParts[modelNameParts.length - 1];
        document.getElementById('model-name').textContent = `Viewing: ${modelName}`;

        // Set up the scene, camera, and renderer
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a1a1a);  // Dark background
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 5, 10);

        // Background color control
        const backgroundSelector = document.getElementById('background-color');
        backgroundSelector.addEventListener('change', function() {
            scene.background = new THREE.Color(parseInt(this.value));
        });

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1;
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        document.getElementById('scene-container').appendChild(renderer.domElement);

        // Set up environment lighting
        const pmremGenerator = new THREE.PMREMGenerator(renderer);
        const environment = pmremGenerator.fromScene(new RoomEnvironment()).texture;
        scene.environment = environment;
        
        // Add ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);
        
        // Add directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(5, 10, 7.5);
        scene.add(directionalLight);

        // Set up controls
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.screenSpacePanning = true;
        controls.minDistance = 1;
        controls.maxDistance = 50;
        controls.maxPolarAngle = Math.PI;
        controls.minPolarAngle = 0;
        
        // Auto-rotation control
        const autoRotateCheckbox = document.getElementById('autoRotate');
        autoRotateCheckbox.addEventListener('change', function() {
            controls.autoRotate = this.checked;
        });
        
        // Set rotation speed
        const rotationSpeedSlider = document.getElementById('rotation-speed');
        rotationSpeedSlider.addEventListener('input', function() {
            controls.autoRotateSpeed = parseFloat(this.value);
        });
        controls.autoRotateSpeed = parseFloat(rotationSpeedSlider.value);

        // Set up model loader
        const dracoLoader = new DRACOLoader();
        dracoLoader.setDecoderPath(`${THREE_PATH}/examples/jsm/libs/draco/gltf/`);
        
        const loader = new GLTFLoader();
        loader.setDRACOLoader(dracoLoader);

        // Load the model
        let mixer;
        let model; // Store the model reference
        
        loader.load(
            modelPath,
            function (gltf) {
                document.getElementById('loading').style.display = 'none';
                
                model = gltf.scene;
                
                // Center the model
                const box = new THREE.Box3().setFromObject(model);
                const center = box.getCenter(new THREE.Vector3());
                const size = box.getSize(new THREE.Vector3());
                const maxDim = Math.max(size.x, size.y, size.z);
                const fov = camera.fov * (Math.PI / 180);
                let cameraZ = Math.abs(maxDim / Math.sin(fov / 2));
                
                // Store original position for view controls
                const originalCameraPos = {
                    front: new THREE.Vector3(center.x, center.y, center.z + cameraZ * 1.5),
                    back: new THREE.Vector3(center.x, center.y, center.z - cameraZ * 1.5),
                    left: new THREE.Vector3(center.x - cameraZ * 1.5, center.y, center.z),
                    right: new THREE.Vector3(center.x + cameraZ * 1.5, center.y, center.z),
                    top: new THREE.Vector3(center.x, center.y + cameraZ * 1.5, center.z),
                    bottom: new THREE.Vector3(center.x, center.y - cameraZ * 1.5, center.z)
                };
                
                // Position camera to see all of the model - start with front view
                camera.position.copy(originalCameraPos.front);
                camera.position.y += maxDim * 0.1; // Slight elevation for better viewing
                controls.target.copy(center);
                
                // Store initial position for reset
                const initialCameraPosition = camera.position.clone();
                const initialTarget = center.clone();
                
                // Reset camera after centering
                camera.lookAt(center);
                controls.update();
                
                // Reset camera button
                document.getElementById('reset-camera').addEventListener('click', function() {
                    cameraMove(initialCameraPosition, initialTarget);
                    
                    // Reset model orientation too
                    model.rotation.set(0, 0, 0);
                });
                
                // Check if model needs auto-orientation
                // Some models load with wrong orientation, try to fix
                if (size.y > size.x * 1.5 && size.y > size.z * 1.5) {
                    // Model is likely oriented vertically when it should be horizontal
                    model.rotation.x = -Math.PI / 2;
                }
                
                // View control buttons
                document.getElementById('view-front').addEventListener('click', function() {
                    cameraMove(originalCameraPos.front, center);
                });
                
                document.getElementById('view-back').addEventListener('click', function() {
                    cameraMove(originalCameraPos.back, center);
                });
                
                document.getElementById('view-left').addEventListener('click', function() {
                    cameraMove(originalCameraPos.left, center);
                });
                
                document.getElementById('view-right').addEventListener('click', function() {
                    cameraMove(originalCameraPos.right, center);
                });
                
                document.getElementById('view-top').addEventListener('click', function() {
                    cameraMove(originalCameraPos.top, center);
                });
                
                document.getElementById('view-bottom').addEventListener('click', function() {
                    cameraMove(originalCameraPos.bottom, center);
                });
                
                // Model rotation controls
                const rotationStep = Math.PI / 12; // 15 degrees
                
                document.getElementById('rotate-x-plus').addEventListener('click', function() {
                    model.rotation.x += rotationStep;
                });
                
                document.getElementById('rotate-x-minus').addEventListener('click', function() {
                    model.rotation.x -= rotationStep;
                });
                
                document.getElementById('rotate-y-plus').addEventListener('click', function() {
                    model.rotation.y += rotationStep;
                });
                
                document.getElementById('rotate-y-minus').addEventListener('click', function() {
                    model.rotation.y -= rotationStep;
                });
                
                document.getElementById('rotate-z-plus').addEventListener('click', function() {
                    model.rotation.z += rotationStep;
                });
                
                document.getElementById('rotate-z-minus').addEventListener('click', function() {
                    model.rotation.z -= rotationStep;
                });
                
                // Function to smoothly move camera
                function cameraMove(targetPos, lookAt) {
                    const duration = 1.0;
                    const currentPos = camera.position.clone();
                    const currentTarget = controls.target.clone();
                    
                    // Animation steps
                    let progress = 0;
                    const interval = setInterval(() => {
                        progress += 0.02;
                        if (progress >= 1) {
                            clearInterval(interval);
                            camera.position.copy(targetPos);
                            controls.target.copy(lookAt);
                            camera.lookAt(lookAt);
                            controls.update();
                            return;
                        }
                        
                        // Interpolate positions
                        camera.position.lerpVectors(currentPos, targetPos, progress);
                        const newTarget = new THREE.Vector3().lerpVectors(currentTarget, lookAt, progress);
                        controls.target.copy(newTarget);
                        camera.lookAt(newTarget);
                        controls.update();
                    }, 20);
                }
                
                // Scale control
                const scaleSlider = document.getElementById('scale');
                const scaleValue = document.getElementById('scale-value');
                
                scaleSlider.addEventListener('input', function() {
                    const scale = parseFloat(this.value);
                    model.scale.set(scale, scale, scale);
                    scaleValue.textContent = scale.toFixed(1);
                });
                
                // Position Y control
                const positionYSlider = document.getElementById('position-y');
                const positionYValue = document.getElementById('position-y-value');
                const originalY = model.position.y;
                
                positionYSlider.addEventListener('input', function() {
                    const posY = parseFloat(this.value);
                    model.position.y = originalY + posY;
                    positionYValue.textContent = posY.toFixed(1);
                });
                
                // Reset model button
                const resetButton = document.getElementById('reset-model');
                resetButton.addEventListener('click', function() {
                    // Reset scale
                    model.scale.set(1, 1, 1);
                    scaleSlider.value = 1;
                    scaleValue.textContent = '1.0';
                    
                    // Reset position Y
                    model.position.y = originalY;
                    positionYSlider.value = 0;
                    positionYValue.textContent = '0.0';
                    
                    // Reset rotation
                    model.rotation.set(0, 0, 0);
                    
                    // Reset wireframe
                    const wireframeCheckbox = document.getElementById('wireframe');
                    wireframeCheckbox.checked = false;
                    model.traverse(function(child) {
                        if (child.isMesh) {
                            child.material.wireframe = false;
                        }
                    });
                });
                
                // Wireframe control
                const wireframeCheckbox = document.getElementById('wireframe');
                wireframeCheckbox.addEventListener('change', function() {
                    model.traverse(function(child) {
                        if (child.isMesh) {
                            child.material.wireframe = wireframeCheckbox.checked;
                        }
                    });
                });
                
                // Handle animations if they exist
                if (gltf.animations && gltf.animations.length) {
                    mixer = new THREE.AnimationMixer(model);
                    const action = mixer.clipAction(gltf.animations[0]);
                    action.play();
                }
                
                scene.add(model);
            },
            function (xhr) {
                if (xhr.lengthComputable) {
                    const percentComplete = xhr.loaded / xhr.total * 100;
                    document.getElementById('progress').style.width = percentComplete + '%';
                    document.getElementById('progress-text').textContent = Math.round(percentComplete) + '%';
                }
            },
            function (error) {
                document.getElementById('loading').innerHTML = '<div style="color: red;">Error loading model</div>';
                console.error('An error happened', error);
            }
        );

        // Handle window resizing
        window.addEventListener('resize', onWindowResize);
        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        // Animation loop
        const clock = new THREE.Clock();
        function animate() {
            requestAnimationFrame(animate);
            
            controls.update();
            
            if (mixer) {
                mixer.update(clock.getDelta());
            }
            
            renderer.render(scene, camera);
        }
        
        animate();
    </script>
</body>
</html> 
```


Reference code for gpt-image-1's image generation.
```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            quality="low"
        )
image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)
```

Reference code for gpt-image-1's image editing.
```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
with open(current_image_path, "rb") as image_file:
    result = client.images.edit(
                        model="gpt-image-1",
                        image=image_file,
                        prompt=prompt
                    )
image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)
```

Reference code for gemini-image editing.
```python
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

import PIL.Image

image = PIL.Image.open('/path/to/image.png')

client = genai.Client(api_key="AIzaSyC_UzB4eXWc03oYVqHW8lfURigw5xDAuGM")

text_input = ('Hi, This is a picture of me.'
            'Can you add a llama next to me?',)

response = client.models.generate_content(
    model="gemini-2.0-flash-exp-image-generation",
    contents=[text_input, image],
    config=types.GenerateContentConfig(
      response_modalities=['TEXT', 'IMAGE']
    )
)

for part in response.candidates[0].content.parts:
  if part.text is not None:
    print(part.text)
  elif part.inline_data is not None:
    image = Image.open(BytesIO(part.inline_data.data))
    image.show()
```