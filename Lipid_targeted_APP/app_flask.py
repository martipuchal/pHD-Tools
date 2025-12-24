from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import os
import io
from datetime import datetime
from flask import session

from statics.style import polars_to_styled_html
from statics.polars_df import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'

directory = "uploads/"
selected_file_id = ""

current_results = None
processed_data = None

current_dataframe_area = None
current_dataframe_istd = None

@app.route('/', methods=['GET', 'POST'])
def index():
    # Initialize files list
    files = []
    
    if request.method == 'POST':
        # Check if files were uploaded
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        uploaded_files = request.files.getlist('file')
        
        # Create upload folder if it doesn't exist
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
        
        # Save each file
        for file in uploaded_files:
            if file.filename:
                # Add timestamp to filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{file.filename}"
                file.save(os.path.join('uploads', filename))
        
        flash(f'Successfully uploaded {len(uploaded_files)} file(s)')
        return redirect(url_for('index'))
    
    # Read existing files from uploads folder
    if os.path.exists('uploads'):
        for filename in os.listdir('uploads'):
            filepath = os.path.join('uploads', filename)
            if os.path.isfile(filepath):
                # Get file size in KB
                size_kb = os.path.getsize(filepath) / 1024
                
                # Get modification time
                mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                # Add to files list
                files.append({
                    'name': filename,
                    'size': f'{size_kb:.1f} KB',
                    'uploaded': mod_time.strftime('%Y-%m-%d %H:%M')
                })
    
    # Sort files by upload time (newest first)
    files.sort(key=lambda x: x['uploaded'], reverse=True)
    
    return render_template('home.html', files=files)

@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    """Analysis page - you can customize this based on your needs"""
    
    # Get file stats for analysis
    file_stats = {}
    if os.path.exists('uploads'):
        files = os.listdir('uploads')
        file_stats = {
            'total_files': len(files),
            'total_size_mb': sum(os.path.getsize(os.path.join('uploads', f)) for f in files) / (1024 * 1024),
            'file_types': {},
            "file_ids" : set()
        }
        
        # Count file types
        for filename in files:
            if '.' in filename:
                file_ext = filename.split('.')[-1].lower()
                file_stats['file_types'][file_ext] = file_stats['file_types'].get(file_ext, 0) + 1
            if "_" in filename:
                file_id_list = filename.split("_")[:2]
                file_stats['file_ids'].add("_".join(file_id_list))
        file_stats['file_ids'] = list(file_stats['file_ids'])


    selected_file_id = request.form.get('selected_file_id')
    session['selected_file_id'] = selected_file_id
            
    return render_template('analysis.html', file_stats=file_stats)

@app.route('/save_selection', methods=['POST'])
def save_selection():
    """Save selected file ID to session"""
    selected_id = request.form.get('selected_file_id')
    
    if selected_id:
        session['selected_file_id'] = selected_id
        print(f"✅ Saved to session: {selected_id}")
    
    # Redirect back or to another page
    return redirect(url_for('process'))

@app.route('/process')
def process():
    # Retrieve from session
    selected_file_id = session['selected_file_id']
    df_sample_list = {}

    # Iterate over files in directory
    for name in os.listdir(directory):
        file_path = os.path.join(directory, name)
        if os.path.isfile(file_path) and selected_file_id:
            if selected_file_id in name:
                
                print(f"Content of '{name}':")
                try:
                    df_sample_dicc = scehmaC("uploads/"+name)
                except:
                    clearance("uploads/"+name)
                    df_sample_dicc = scehmaC("uploads/"+name)
           
        
    
    return(render_template('process.html', file_stats=selected_file_id))


@app.route('/run_qc_pipeline', methods=['POST'])
def run_qc_pipeline():

    global current_dataframe_area

    try:
        data = request.get_json()
        for file in  os.listdir('uploads/'):
            # select the the file or the patern is going to be used to identify the Area files
            if session['selected_file_id'] in file and "area" in file:
                Area_df_name = file
               
        
        # Get parameters
        area_threshold = data.get('area_threshold', 500)
        rsd_threshold = data.get('rsd_threshold', 20)
        blank_threshold = data.get('blank_threshold', 50)
        
        # YOUR EXISTING CODE: Process data with Polars
        # This is where you run your QC functions

        df = Ratio_B_QC(QC_rsd_R(min_area_R(scehmaC("uploads/"+Area_df_name),area_threshold),rsd_threshold),blank_threshold)
        
        # Save the df to download
        current_dataframe_area = df.clone()

        # Generate HTML table from Polars DataFrame
        html_table = polars_to_styled_html(df,"")
        
        # Return success with HTML table
        return jsonify({
            'success': True,
            'message': 'QC pipeline completed',
            'html_table': html_table,
            'row_count': df.height,
            'col_count': df.width
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    


@app.route('/run_ISTD_pipeline', methods=['POST'])
def run_ISTD_pipeline():
    try:
        global current_dataframe_istd
        data = request.get_json()
        for file in  os.listdir('uploads/'):
            # select the the file or the patern is going to be used to identify the Area files
            if session['selected_file_id'] in file and "ISTD" in file:
                ISTD_df_name = file


        itsd_threshold = data.get('ISTD_threshold', 30)

        df = curation_ISTD(scehmaC("uploads/" + ISTD_df_name),itsd_threshold)
        
        # Save the df to download
        current_dataframe_istd = df.clone()
        
        html_table = polars_to_styled_html(df,"Istd")

        # Return success with HTML table
        return jsonify({
            'success': True,
            'message': 'ISTD pipeline completed',
            'html_table': html_table,
            'row_count': df.height,
            'col_count': df.width
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/export_table_area', methods=['POST'])
def export_table_area():
    """Export the current DataFrame as CSV"""
    # Get your current DataFrame (you need to store it somewhere)
    global current_dataframe_area
    
    if current_dataframe_area is None:
        return jsonify({'error': 'No data available'}), 400
    
    # Convert Polars DataFrame to CSV string
    csv_string = current_dataframe_area.write_csv()
    
    # Create in-memory file
    buffer = io.BytesIO()
    buffer.write(csv_string.encode('utf-8'))
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name='qc_results.csv',
        mimetype='text/csv'
    )


@app.route('/export_table_istd', methods=['POST'])
def export_table_istd():
    """Export the current DataFrame as CSV"""
    # Get your current DataFrame (you need to store it somewhere)
    global current_dataframe_istd
    
    
    if current_dataframe_istd is None:
        return jsonify({'error': 'No data available'}), 400
    
    # Convert Polars DataFrame to CSV string
    csv_string = current_dataframe_istd.write_csv()
    
    # Create in-memory file
    buffer = io.BytesIO()
    buffer.write(csv_string.encode('utf-8'))
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name='qc_results.csv',
        mimetype='text/csv'
    )




if __name__ == '__main__':
    app.run(debug=True)