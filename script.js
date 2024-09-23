
import { Canvas } from 'fabric';
import { Spring } from './src/prairielearn/elements/pl-drawing/mechanicsObjects.js';
// Ensure mechanicsObjects exists

// Initialize the Fabric.js canvas
const canvas = new Canvas('fabricCanvas', {
    width: 600,
    height: 400,
    backgroundColor: 'white',
});

// Create a Spring object from mechanicsObjects
const spring = new Spring({
    x1: 100,          // Starting x-coordinate
    y1: 200,          // Starting y-coordinate
    x2: 500,          // Ending x-coordinate
    y2: 200,          // Ending y-coordinate
    dx: 15,           // Zigzag density
    height: 30,       // Zigzag height
    stroke: 'blue',   // Color of the spring
    drawPin: true,    // Draw pins at the ends
    selectable: true, // Make the spring interactive
});

// Add the spring to the canvas
canvas.add(spring);

// Optional: Enable object controls for scaling and rotating
spring.setControlsVisibility({
    mt: true, // Middle top
    mb: true, // Middle bottom
    ml: true, // Middle left
    mr: true, // Middle right
    bl: true, // Bottom left
    br: true, // Bottom right
    tl: true, // Top left
    tr: true, // Top right
    mtr: true, // Rotation control
});

// Update the spring properties when it's transformed
spring.on('modified', function () {
    // Recalculate length and angle
    this.length = Math.hypot(this.x2 - this.x1, this.y2 - this.y1);
    this.angleRad = Math.atan2(this.y2 - this.y1, this.x2 - this.x1);
    this.angle = (180 / Math.PI) * this.angleRad;
    this.dirty = true;
    canvas.renderAll();
});
