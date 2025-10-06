from flask import Flask, request, jsonify, send_file, render_template, session
from flask import send_from_directory, abort
from werkzeug.utils import safe_join, secure_filename
import os
import re
import glob # Import glob
import subprocess # Import subprocess
from Bio.PDB import PDBParser
import numpy as np
import time
import json
import webbrowser
import threading

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.urandom(24)  # Change this to a secure random value
running_processes = {}

@app.route('/')
def home():
    return render_template('index.html')

# # Folder for uploaded files
# UPLOAD_FOLDER = './uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# Workspace & Project directories
WORKSPACE = './workspace'
PROJECT = './workspace/projects'
# UPLOAD_FOLDER = './uploads'

app.config['WORKSPACE'] = WORKSPACE
app.config['PROJECT'] = PROJECT
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create directories if missing
os.makedirs(WORKSPACE, exist_ok=True)
os.makedirs(PROJECT, exist_ok=True)

# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# if not os.path.exists(WORKSPACE):
#     os.makedirs(WORKSPACE)

@app.route('/create-project', methods=['POST'])
def create_project():
    data = request.get_json()
    project_name = data.get('project_name', '').strip()

    if not project_name:
        return jsonify({'error': 'Project name is required'}), 400

    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', project_name)
    path = os.path.join(app.config['PROJECT'], safe_name)

    try:
        os.makedirs(path, exist_ok=False)
        session['project_path'] = path  #Save in session
        return jsonify({'message': f'Project "{safe_name}" created successfully.'})
    except FileExistsError:
        return jsonify({'error': 'Project already exists.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route for receptor uploading files
@app.route('/rec_upload', methods=['POST'])
def upload_rec():
    project_path = session.get('project_path') 
    if not project_path:
        return jsonify({'error': 'No active project. Please create a project first.'}), 400

    file = request.files.get('file')
    if not file or not file.filename.endswith('.pdb'):
        return jsonify({'error': 'Invalid file type. Please upload a PDB file.'}), 400
    
    upload_folder = os.path.join(project_path, 'receptor')
    os.makedirs(upload_folder, exist_ok=True)

    filepath = os.path.join(upload_folder, file.filename)
    file.save(filepath)

    return jsonify({'message': 'File uploaded successfully!', 'filepath': filepath})

# Route for ligand uploading files
@app.route('/lig_upload', methods=['POST'])
def upload_lig():
    project_path = session.get('project_path')
    if not project_path:
        return jsonify({'error': 'No active project found.'}), 400

    files = request.files.getlist('files[]')  # FIXED: getlist for multiple files

    if not files or all(file.filename == '' for file in files):
        return jsonify({'error': 'No files uploaded.'}), 400

    allowed_extensions = {'.pdbqt'}
    upload_folder = os.path.join(project_path, 'ligand')
    os.makedirs(upload_folder, exist_ok=True)

    saved_files = []

    for file in files:
        filename = secure_filename(file.filename)
        if filename == '':
            continue

        ext = os.path.splitext(filename)[1].lower()
        if ext not in allowed_extensions:
            return jsonify({'error': f'Invalid file type for {filename}. Allowed: .pdbqt'}), 400

        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        saved_files.append(filepath)

    return jsonify({
        'message': f'{len(saved_files)} file(s) uploaded successfully!',
        'filepaths': saved_files,
        'filenames': [os.path.basename(f) for f in saved_files]
    })


@app.route('/grid', methods=['POST'])
def generate_grid():
    project_path = session.get('project_path')
    try:
        # Parse incoming JSON request
        data = request.json
        filepath = data.get('filepath')  # Path to the uploaded file
        mode = data.get('mode')  # Docking mode: "blind" or "targeted"
        residues = data.get('residues', [])  # Targeted residues as a list

        # Check if file exists
        if not filepath or not os.path.exists(filepath):
            return jsonify({'error': 'File not found. Please upload a valid file.'}), 400

        # Parse the PDB file
        parser = PDBParser()
        structure = parser.get_structure('protein', filepath)

        coords = []
        if mode == 'blind':
            # Collect all atom coordinates for blind docking
            for atom in structure.get_atoms():
                coords.append(atom.coord)
        elif mode == 'targeted':
            if not residues:
                return jsonify({'error': 'No residues specified for targeted docking.'}), 400
            # Extract coordinates of specific residues
            for residue in residues:
                residue = residue.strip()
                chain_id, res_id = residue.split(':')
                chain_id = chain_id.strip()
                res_id = res_id.strip()
                for chain in structure.get_chains():
                    if chain.id == chain_id:
                        for res in chain.get_residues():
                            if res.id[1] == int(res_id):  # Match residue number
                                for atom in res:
                                    coords.append(atom.coord)
        else:
            return jsonify({'error': 'Invalid mode selected.'}), 400

        if not coords:
            return jsonify({'error': 'No atoms found for the specified residues.'}), 400

        coords = np.array(coords)
        min_coords = coords.min(axis=0) - 5  # Add buffer
        max_coords = coords.max(axis=0) + 5  # Add buffer

        center = (min_coords + max_coords) / 2
        size = max_coords - min_coords

        # Create configuration file for grid box
        config = f"""
center_x = {center[0]}
center_y = {center[1]}
center_z = {center[2]}
size_x = {size[0]}
size_y = {size[1]}
size_z = {size[2]}
"""

        # Generate a unique filename using timestamp and mode
        timestamp = int(time.time())
        config_filename = f'config_{mode}_{timestamp}.txt'
        config_path = os.path.join(project_path, config_filename)
        with open(config_path, 'w') as f:
            f.write(config)

        # Extract grid dimensions to send to the client
        grid_dimensions = {
        'center_x': float(center[0]),
        'center_y': float(center[1]),
        'center_z': float(center[2]),
        'size_x': float(size[0]),
        'size_y': float(size[1]),
        'size_z': float(size[2]),
        }

        # Return the filename to the client for reference or download
        return jsonify({
            'message': 'Grid configuration generated!',
            'config_file': config_filename,
            'config_path': config_path,
            'grid_dimensions': grid_dimensions
        })
    except Exception as e:
        app.logger.error(f"Error during grid generation: {e}")
        return jsonify({'error': 'An error occurred during grid generation.'}), 500

@app.route('/save_grid', methods=['POST'])
def save_adjusted_grid():
    project_path = session.get('project_path')
    data = request.json
    filepath = data.get('filepath')
    grid = data.get('grid')

    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'Invalid file path'}), 400

    # Get project directory from filepath
    # project_folder = os.path.dirname(filepath)
    # upload_folder = os.path.join(project_folder, 'grid')
    # os.makedirs(upload_folder, exist_ok=True)
    upload_folder = os.path.join(project_path, 'params')
    os.makedirs(upload_folder, exist_ok=True)

    # Always save as grid.json
    filename = "grid.json"
    save_path = os.path.join(upload_folder, filename)

    with open(save_path, 'w') as f:
        json.dump(grid, f, indent=4)

    return jsonify({'message': 'Grid saved successfully!', 'grid_file': filename, 'save_path': save_path})

@app.route('/upload-params', methods=['POST'])
def upload_params():
    project_path = session.get('project_path')
    if not project_path:
        return jsonify({'error': 'No active project. Please create a project first.'}), 400

    try:
        data = {
            'search_mode': request.form.get('search_mode'),
            'scoring_method': request.form.get('scoring_method'),
            'num_modes': request.form.get('num_modes'),
            'gpu_check': request.form.get('defaultCheck1') == 'on'
        }

        if not data['search_mode'] or not data['scoring_method'] or not data['num_modes']:
            return jsonify({'error': 'Missing required form fields.'}), 400

        upload_folder = os.path.join(project_path, 'params')
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, 'param.json')

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

        return jsonify({'message': 'Parameters saved as JSON successfully.'}), 200
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/run-docking', methods=['POST'])
def run_docking():
    project_path = session.get('project_path')
    if not project_path:
        return jsonify({'error': 'No active project found.'}), 400

    # Prevent multiple simultaneous runs for the same project
    if project_path in running_processes and running_processes[project_path].poll() is None:
        return jsonify({'error': 'A docking process is already running for this project.'}), 409

    try:
        # --- Step 1: Define paths and create results directory ---
        params_dir = os.path.join(project_path, 'params')
        receptor_dir = os.path.join(project_path, 'receptor')
        ligand_dir = os.path.join(project_path, 'ligand')
        results_dir = os.path.join(project_path, 'results')
        os.makedirs(results_dir, exist_ok=True)

        grid_config_path = os.path.join(params_dir, 'grid.json')
        docking_params_path = os.path.join(params_dir, 'param.json')
        
        receptor_files = glob.glob(os.path.join(receptor_dir, '*.pdb'))
        if not receptor_files:
            return jsonify({'error': 'Receptor PDB file not found.'}), 404
        receptor_file = receptor_files[0]
        
        # --- Step 2: Load and consolidate configurations ---
        with open(grid_config_path, 'r') as f: grid_config = json.load(f)
        with open(docking_params_path, 'r') as f: docking_params = json.load(f)

        master_config = {
            "receptor": os.path.abspath(receptor_file),
            "ligand_dir": os.path.abspath(ligand_dir),
            "results_dir": os.path.abspath(results_dir),
            **grid_config,
            **docking_params
        }

        master_config_path = os.path.join(project_path, 'config.json')
        with open(master_config_path, 'w') as f:
            json.dump(master_config, f, indent=4)
        
        # --- Step 3: Execute script and capture logs ---
        script_path = os.path.join(os.path.dirname(__file__), 'unidock_multi.py')
        command = ['python', '-u', script_path, master_config_path]
        
        # Define a log file to capture both stdout and stderr
        log_file_path = os.path.join(results_dir, 'docking_run.log')
        log_file = open(log_file_path, 'w')
        
        # Popen runs the command in a new process and redirects output.
        process = subprocess.Popen(command, stdout=log_file, stderr=subprocess.STDOUT)
        
        # Store the process object to track its status later
        running_processes[project_path] = process

        return jsonify({'message': 'Docking process started successfully!'}), 200

    except FileNotFoundError as e:
        return jsonify({'error': f'A required configuration file is missing: {e.filename}'}), 500
    except Exception as e:
        app.logger.error(f"Error starting docking process: {e}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

# --- NEW: Route for the frontend to poll for status updates ---
# (in app.py)

@app.route('/run-status', methods=['GET'])
def run_status():
    project_path = session.get('project_path')
    if not project_path:
        return jsonify({'error': 'No active project found.'}), 400

    if project_path not in running_processes:
        return jsonify({'status': 'not_found', 'message': 'No active run found for this project.'})

    process = running_processes[project_path]
    return_code = process.poll()

    results_dir = os.path.join(project_path, 'results')
    log_file_path = os.path.join(results_dir, 'docking_run.log')
    log_content = ""
    try:
        with open(log_file_path, 'r') as f:
            log_content = f.read()
    except FileNotFoundError:
        log_content = "Log file has not been created yet..."

    if return_code is None:
        return jsonify({
            'status': 'running',
            'log': log_content
        })
    else:
        del running_processes[project_path]
        
        if return_code == 0:
            # --- NEW: Add the absolute results path to the success response ---
            results_path = os.path.abspath(results_dir)
            return jsonify({
                'status': 'completed', 
                'message': 'Docking run finished successfully!',
                'log': log_content,
                'results_path': results_path  # <-- ADD THIS LINE
            })
        else:
            return jsonify({
                'status': 'error', 
                'message': f'Docking run failed with exit code {return_code}.',
                'log': log_content
            })



# @app.route('/download/<filename>', methods=['GET'])
# def download_file(filename):
#     try:
#         # Log the filename
#         app.logger.debug(f"Requested filename: {filename}")

#         # Use safe_join to construct the file path
#         file_path = safe_join(app.config['UPLOAD_FOLDER'], filename)
#         app.logger.debug(f"Constructed file path: {file_path}")

#         # Check if the file exists
#         if not os.path.isfile(file_path):
#             app.logger.error(f"File not found at path: {file_path}")
#             abort(404)

#         # Send the file
#         return send_from_directory(
#             app.config['UPLOAD_FOLDER'],
#             filename,
#             as_attachment=True
#         )
#     except Exception as e:
#         app.logger.error(f"Error during file download: {e}")
#         return jsonify({'error': 'An error occurred during file download.'}), 500

@app.route('/get_pdb', methods=['GET'])
def get_pdb():
    filepath = request.args.get('filepath')
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'File not found.'}), 404
    return send_file(filepath, mimetype='chemical/x-pdb')

@app.route('/get-project-path')
def get_project_path():
    project_path = session.get('project_path')
    if project_path:
        return jsonify({'project_path': project_path})
    else:
        return jsonify({'error': 'No active project'}), 400

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True, use_reloader=False)

