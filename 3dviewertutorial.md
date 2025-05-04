# 3D Viewer Implementation Tutorial

This document details the implementation of the 3D viewer component in this project, covering the HTML structure, CSS styling, and JavaScript logic using Three.js.

## 1. HTML Structure (`templates/index.html`)

The main HTML file sets up the overall page layout and defines the containers for the chat interface and the viewer section. The viewer section initially shows an image viewer, which can be switched to the 3D model viewer.

```html
<!-- Right side: Viewer container (switches between image and 3D) -->
<section class="viewer-container glass-panel">
    <!-- Transition overlay element -->
    <div id="stageTransition" class="stage-transition"></div>
    
    <!-- Image viewer (initial stage) -->
    <div id="imageViewerSection" class="viewer-section active">
        <div class="viewer-header">
            <h2><i class="fas fa-image"></i> Image Viewer</h2>
            <div class="stage-hint">Type "next stage" to switch to 3D viewer</div>
        </div>
        
        <div class="viewer-content">
            <div id="imageViewer" class="image-container">
                <!-- Placeholder or generated image displayed here -->
                <div class="placeholder-message">
                    <i class="fas fa-image fa-3x"></i>
                    <p>Enter a prompt to generate an image</p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 3D viewer (hidden initially) -->
    <div id="modelViewerSection" class="viewer-section">
        <div class="viewer-header">
            <h2><i class="fas fa-cube"></i> 3D Model Viewer</h2>
            <!-- Button to trigger file input -->
            <label for="modelUpload" class="upload-btn">
                <i class="fas fa-upload"></i> Upload GLB
                <!-- Hidden file input -->
                <input type="file" id="modelUpload" accept=".glb" hidden>
            </label>
        </div>
        
        <div class="viewer-content">
            <!-- Three.js canvas will be inserted here by viewer.js -->
            <div id="modelViewer"></div> 
        </div>
    </div>
</section>
```

**Key elements:**

*   `viewer-container`: The main container for the right-hand side panel.
*   `imageViewerSection`: Contains the image display area. Initially visible (`active` class).
*   `modelViewerSection`: Contains the 3D model display area. Initially hidden.
*   `modelUpload`: A hidden file input triggered by a styled label (`upload-btn`) for loading GLB models.
*   `modelViewer`: The specific `div` where the Three.js canvas will be rendered.

### Importing Three.js

Three.js and its addons (OrbitControls, GLTFLoader, DRACOLoader, RoomEnvironment) are imported using ES6 modules and an import map defined in the `<head>` section. This allows for cleaner imports directly within the JavaScript modules.

```html
<!-- Import Map Shim and Definition -->
<script async src="https://unpkg.com/es-module-shims@1.6.3/dist/es-module-shims.js"></script>
<script type="importmap">
    {
      "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.174.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.174.0/examples/jsm/"
      }
    }
</script>

<!-- Module script to import Three.js components and setup viewer initialization -->
<script type="module">
    // Use import map defined short names
    import * as THREE from 'three';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
    import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
    import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
    import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
    
    // Expose an initialization function globally (called by chat.js when switching stages)
    window.initViewer = function() {
        // Pass the mapped modules to viewerMain
        return viewerMain(THREE, OrbitControls, GLTFLoader, DRACOLoader, RoomEnvironment);
    };
    
    // Import the main viewer logic from viewer.js
    import { viewerMain } from '/static/js/viewer.js';
</script>
```

## 2. CSS Styling (`static/css/style.css`)

The CSS file defines the appearance and layout, including the glassmorphism effect, flexbox layout, and specific styles for the viewer sections.

```css
/* Base Styles & Layout */
body {
    background: linear-gradient(135deg, #6e8efb, #a777e3);
    min-height: 100vh;
    /* ... other styles */
}
.glass-panel { /* Applied to chat and viewer containers */
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    border: 1px solid rgba(255, 255, 255, 0.18);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
}
main {
    display: flex; /* Side-by-side layout for chat and viewer */
    gap: 20px;
    height: calc(100vh - 120px); /* Adjust height */
}

/* Viewer Section Styles */
.viewer-container {
    flex: 1; /* Take up available space */
    display: flex;
    flex-direction: column;
    overflow: hidden; /* Prevent content overflow */
    position: relative; /* Needed for absolute positioning of viewer sections */
}

.viewer-section { /* Base styles for both image and model viewers */
    display: none; /* Hidden by default */
    flex-direction: column;
    height: 100%;
    width: 100%;
    position: absolute; /* Overlay each other */
    top: 0;
    left: 0;
    opacity: 0;
    transform: scale(0.95);
    transition: opacity 0.4s ease, transform 0.4s ease; /* Fade/scale transition */
}

.viewer-section.active { /* Style for the currently visible section */
    display: flex;
    opacity: 1;
    transform: scale(1);
    z-index: 10;
}

.viewer-header { /* Header within the viewer panel */
    padding: 15px 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.viewer-content { /* Container for the actual image or 3D canvas */
    flex: 1; /* Take remaining height */
    position: relative; /* Needed for absolute positioning of canvas/image */
}

/* Specific container for the Three.js canvas */
#modelViewer {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex; /* Used for centering loading message? */
    align-items: center;
    justify-content: center;
}

/* Style for the upload button */
.upload-btn {
    background: rgba(255, 255, 255, 0.1);
    color: white;
    padding: 8px 15px;
    border-radius: 20px;
    cursor: pointer;
    transition: background 0.2s;
    font-size: 0.9rem;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}
.upload-btn:hover {
    background: rgba(255, 255, 255, 0.2);
}
```

**Key points:**

*   Flexbox is used for the main layout (`main`) and within the `viewer-container`.
*   `viewer-section` elements are positioned absolutely within `viewer-container` to allow switching between them using the `active` class.
*   CSS transitions (`opacity`, `transform`) provide a smooth fade/scale effect when switching between image and 3D views.
*   `#modelViewer` is set to fill its parent (`viewer-content`) completely using absolute positioning.
*   The upload button is styled to look like a button, hiding the actual file input element.

## 3. JavaScript Logic (`static/js/viewer.js`)

This file contains the core Three.js setup and model loading logic. It's structured as an ES6 module and exports a `viewerMain` function.

```javascript
// Exported function, receives Three.js components as arguments
export function viewerMain(THREE, OrbitControls, GLTFLoader, DRACOLoader, RoomEnvironment) {
    // Get the container element where the canvas will be added
    const container = document.getElementById('modelViewer');
    const clock = new THREE.Clock();
    let mixer; // For animations

    // --- Scene Setup ---
    const scene = new THREE.Scene();
    scene.background = null; // Use CSS background

    // --- Camera Setup ---
    const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(0, 1.5, 3); // Initial position

    // --- Renderer Setup ---
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true }); // Alpha: true for transparent background
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setClearColor(0x000000, 0); // Transparent
    // PBR settings
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1;
    renderer.outputColorSpace = THREE.SRGBColorSpace; 
    container.appendChild(renderer.domElement); // Add canvas to the div

    // --- Environment and Lighting ---
    // Using RoomEnvironment for simple, good-looking lighting
    const pmremGenerator = new THREE.PMREMGenerator(renderer);
    const environment = pmremGenerator.fromScene(new RoomEnvironment(renderer), 0.04).texture;
    scene.environment = environment; // Apply environment map for reflections

    // --- Controls --- 
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true; // Smooth camera movement
    controls.minDistance = 0.5;
    controls.maxDistance = 50;
    controls.target.set(0, 0.5, 0); // Initial focus point

    // --- Loader Setup ---
    // DRACOLoader for compressed models (needs decoder path)
    const dracoLoader = new DRACOLoader();
    dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.5/');
    // GLTFLoader for loading GLB/GLTF files
    const gltfLoader = new GLTFLoader();
    gltfLoader.setDRACOLoader(dracoLoader);

    // --- Model Loading Logic ---
    let currentModel = null;
    let initialCameraPosition = camera.position.clone(); // Store initial state for potential reset
    let initialTarget = controls.target.clone();

    function loadModel(file) {
        // Display loading message
        const loadingMessage = document.createElement('div');
        // ... (loading message styling) ...
        container.appendChild(loadingMessage);

        const url = URL.createObjectURL(file); // Create temporary URL for the file

        // Remove previous model if exists
        if (currentModel) {
            scene.remove(currentModel);
            if (mixer) mixer.stopAllAction(); mixer = null;
        }

        gltfLoader.load(
            url,
            (gltf) => { // Success callback
                container.removeChild(loadingMessage);
                currentModel = gltf.scene;

                // --- Auto-center and scale model ---
                const box = new THREE.Box3().setFromObject(currentModel);
                const center = box.getCenter(new THREE.Vector3());
                const size = box.getSize(new THREE.Vector3());
                const maxDim = Math.max(size.x, size.y, size.z);
                const fov = camera.fov * (Math.PI / 180);
                let cameraZ = Math.abs(maxDim / 1.5 / Math.tan(fov / 2));
                cameraZ *= 1.1; // Extra distance

                currentModel.position.sub(center); // Center model at origin

                // Adjust camera position and target to view the model
                camera.position.set(center.x, center.y + size.y * 0.1, center.z + cameraZ);
                controls.target.copy(center);
                controls.update();

                // Store initial state after loading
                initialCameraPosition = camera.position.clone();
                initialTarget = controls.target.clone();
                // --- End Centering/Scaling ---

                scene.add(currentModel); // Add model to the scene

                // Handle animations if present
                if (gltf.animations && gltf.animations.length) {
                    mixer = new THREE.AnimationMixer(currentModel);
                    gltf.animations.forEach((clip) => mixer.clipAction(clip).play());
                }

                URL.revokeObjectURL(url); // Clean up temporary URL
            },
            (progress) => { // Progress callback
                // Update loading message percentage
                // ...
            },
            (error) => { // Error callback
                container.removeChild(loadingMessage);
                console.error('Error loading model:', error);
                alert('Failed to load the model.');
                URL.revokeObjectURL(url);
            }
        );
    }

    // --- Event Listeners ---
    // Listen for changes on the hidden file input
    const uploadInput = document.getElementById('modelUpload');
    uploadInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file && file.name.toLowerCase().endsWith('.glb')) {
            loadModel(file); // Load the selected GLB file
        } else if (file) {
            alert('Please select a GLB file (.glb)');
        }
    });

    // Handle window resize to keep viewer correctly sized
    window.addEventListener('resize', () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });

    // --- Animation Loop ---
    function animate() {
        requestAnimationFrame(animate); // Request next frame
        const delta = clock.getDelta(); // Time since last frame

        if (mixer) {
            mixer.update(delta); // Update animations
        }

        controls.update(); // Update camera controls (important for damping)
        renderer.render(scene, camera); // Render the scene
    }

    animate(); // Start the loop
}
```

**Key logic:**

1.  **Initialization (`viewerMain`)**: Sets up the core Three.js components: `Scene`, `PerspectiveCamera`, `WebGLRenderer` (with transparent background), `RoomEnvironment` for lighting, and `OrbitControls` for camera interaction.
2.  **Loaders**: Initializes `DRACOLoader` (for compressed meshes) and `GLTFLoader`. The `DRACOLoader` requires a path to the decoder files.
3.  **`loadModel(file)` function**:
    *   Takes a `File` object (from the input).
    *   Creates a temporary `ObjectURL` for the file.
    *   Removes any previously loaded model.
    *   Uses `gltfLoader.load` to load the model asynchronously.
    *   Includes callbacks for success, progress, and error handling.
    *   **Auto-centering/scaling**: On successful load, calculates the model's bounding box, centers the model at the origin, and adjusts the camera position and target to frame the model appropriately.
    *   Handles model animations using `AnimationMixer` if animations exist in the GLTF data.
    *   Adds the loaded model (`gltf.scene`) to the main `scene`.
4.  **Event Listeners**:
    *   Attaches a listener to the `modelUpload` file input. When a `.glb` file is selected, it calls `loadModel`.
    *   Attaches a listener to the `window`'s `resize` event to update the camera's aspect ratio and the renderer's size, ensuring the view doesn't get distorted.
5.  **Animation Loop (`animate`)**:
    *   Uses `requestAnimationFrame` for efficient rendering updates.
    *   Updates the `OrbitControls` (necessary for damping).
    *   Updates the `AnimationMixer` if a model with animations is loaded.
    *   Calls `renderer.render` to draw the scene from the camera's perspective onto the canvas.

## 4. Integration (`chat.js` - relevant parts)

While `chat.js` primarily handles the chat functionality, it's also responsible for switching between the image viewer and the 3D viewer stage and initializing the 3D viewer when needed.

*   It listens for the "next stage" command in the chat.
*   When detected, it hides the `imageViewerSection` and shows the `modelViewerSection` using CSS classes (`active`).
*   Crucially, it calls `window.initViewer()` (which was defined in the `index.html` module script) the *first time* the switch to the 3D stage occurs. This ensures the Three.js setup runs only when needed.

(Note: The specific code from `chat.js` for stage switching is not included here but is essential for the transition.)

This structure allows the 3D viewer to be lazily initialized, improving initial page load performance. 