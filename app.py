from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pandas as pd
import preprocessing, quadtree, ml_model, fairness
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global store for processed data (In-memory for demo)
STORAGE = {"data": None}
USERS = {}  # Simple in-memory user store for demo

@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('signup'))  # Redirect to signup first
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match')
        if email in USERS:
            return render_template('signup.html', error='Email already exists')
        USERS[email] = {'full_name': full_name, 'password': password}
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in USERS and USERS[email]['password'] == password:
            session['logged_in'] = True
            session['user'] = email
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload():
    if 'logged_in' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    file = request.files['file']
    df = pd.read_csv(file)
    STORAGE['data'] = preprocessing.process_data(df)
    return jsonify({"status": "success", "rows": len(df)})

@app.route('/partition', methods=['POST'])
def partition():
    if 'logged_in' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    df = STORAGE['data']
    threshold = int(request.json.get('threshold', 1000))
    
    boundary = [df['latitude'].min(), df['latitude'].max(), 
                df['longitude'].min(), df['longitude'].max()]
    
    tree = quadtree.build_quadtree(df, boundary, threshold)
    leaves = quadtree.get_leaf_nodes(tree)
    
    # Prep data for ML
    leaf_summaries = []
    for i, leaf in enumerate(leaves):
        leaf_summaries.append({
            'leaf_id': i,
            'avg_lat': leaf.points['latitude'].mean(),
            'avg_lon': leaf.points['longitude'].mean(),
            'population': leaf.points['population'].sum(),
            'avg_socio': leaf.points['socio_score'].mean()
        })
    
    STORAGE['leaves'] = pd.DataFrame(leaf_summaries)
    return jsonify(leaf_summaries)

@app.route('/generate-boundaries', methods=['POST'])
def generate():
    if 'logged_in' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    leaves_df = STORAGE['leaves']
    n_const = int(request.json.get('count', 5))
    
    labels = ml_model.group_into_constituencies(leaves_df, n_clusters=n_const)
    leaves_df['constituency_id'] = labels
    
    metrics = fairness.calculate_metrics(leaves_df)
    
    return jsonify({
        "results": leaves_df.to_dict(orient='records'),
        "metrics": metrics
    })

if __name__ == '__main__':
    app.run(debug=True)