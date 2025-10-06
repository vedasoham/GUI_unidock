// Handle the grid generation
document.getElementById('grid-form').onsubmit = async (event) => {
    event.preventDefault(); // Prevent form submission from reloading the page

    const mode = "blind";

    if (!window.uploadedFilePath) {
        document.getElementById('grid-response').textContent = "Please upload a PDB file first.";
        document.getElementById('grid-response').classList.add('text-danger');
        return;
    }

    try {
        const response = await fetch('/grid', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                filepath: window.uploadedFilePath, // Use the uploaded file path
                mode: mode,
            }),
        });

        const result = await response.json();

        if (response.ok) {
            const message = result.message || "Grid generated successfully!";
            document.getElementById('grid-response').innerHTML = `
                ${message}`;
            document.getElementById('grid-response').classList.remove('text-danger');
            document.getElementById('grid-response').classList.add('text-success');

            // Save the grid dimensions
            window.gridDimensions = result.grid_dimensions;

            // Draw the grid box in the viewer
            drawGridBox(window.gridDimensions);

            // Set slider values to grid dimensions
            updateSliders(window.gridDimensions);

            // Show the slider for adjusting grid position and size
            document.getElementById('slider-container').style.display = 'block';
        } else {
            document.getElementById('grid-response').textContent = result.error || "Error occurred!";
            document.getElementById('grid-response').classList.remove('text-success');
            document.getElementById('grid-response').classList.add('text-danger');
        }
    } catch (error) {
        console.error("Error during grid generation:", error);
        document.getElementById('grid-response').textContent = "An error occurred. Check the console for details.";
        document.getElementById('grid-response').classList.add('text-danger');
    }
};

// Function to draw the grid box in the viewer
function drawGridBox(gridDimensions) {
    // Remove any existing shapes
    viewer.removeAllShapes();

    const { center_x, center_y, center_z, size_x, size_y, size_z } = gridDimensions;

    const xmin = (center_x - size_x / 2).toFixed(5);
    const xmax = (center_x + size_x / 2).toFixed(5);
    const ymin = (center_y - size_y / 2).toFixed(5);
    const ymax = (center_y + size_y / 2).toFixed(5);
    const zmin = (center_z - size_z / 2).toFixed(5);
    const zmax = (center_z + size_z / 2).toFixed(5);


    // Define the corners of the box
    const corners = [
        { x: xmin, y: ymin, z: zmin },
        { x: xmax, y: ymin, z: zmin },
        { x: xmax, y: ymax, z: zmin },
        { x: xmin, y: ymax, z: zmin },
        { x: xmin, y: ymin, z: zmax },
        { x: xmax, y: ymin, z: zmax },
        { x: xmax, y: ymax, z: zmax },
        { x: xmin, y: ymax, z: zmax },
    ];

    // Define the edges connecting the corners
    const edges = [
        [0, 1], [1, 2], [2, 3], [3, 0], // Bottom face edges
        [4, 5], [5, 6], [6, 7], [7, 4], // Top face edges
        [0, 4], [1, 5], [2, 6], [3, 7], // Side edges
    ];

    // Draw the edges
    edges.forEach(edge => {
        viewer.addLine({
            start: corners[edge[0]],
            end: corners[edge[1]],
            color: 'red',
            linewidth: 2,
            dashed: false,
        });
    });

    // Render the viewer
    viewer.render();
}