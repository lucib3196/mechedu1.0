// Setup canvas and load existing answers (if any)
const root_elem = document.getElementById('canvas-container');

// Options for the canvas (e.g., dimensions)
const elem_options = {
  width: 600,
  height: 400,
  backgroundColor: 'lightgray'
};

// Initialize the canvas using the PLDrawingApi
window.PLDrawingApi.setupCanvas(root_elem, elem_options, null); // 'null' if no existing submission
