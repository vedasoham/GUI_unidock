// Initialize the 3Dmol viewer
var viewer = null;
window.onload = function () {
    viewer = $3Dmol.createViewer("viewer", {
        defaultcolors: $3Dmol.rasmolElementColors
    });
};

// Function to load the protein structure into the viewer
async function loadProteinStructure(filepath) {
    try {
        const response = await fetch(`/get_pdb?filepath=${encodeURIComponent(filepath)}`);
        if (!response.ok) {
            throw new Error("Failed to fetch PDB file from the server.");
        }
        const pdbText = await response.text();

        // Clear any existing models
        viewer.clear();

        // Load the PDB data into the viewer
        viewer.addModel(pdbText, "pdb");

        // Set display styles
        viewer.setStyle({}, { cartoon: { color: 'spectrum' } });

        // Zoom to fit the structure
        viewer.zoomTo();
        viewer.render();

        // Show the viewer
        document.getElementById('viewer').style.display = 'block';

    } catch (error) {
        console.error("Error loading protein structure:", error);
    }
}