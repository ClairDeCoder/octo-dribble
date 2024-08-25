from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'secretkey'  # Change this to something secure

BACKEND_URL = "http://127.0.0.1:8000"  # URL for the backend API

@app.route('/')
def index():
    if 'token' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        response = requests.post(f"{BACKEND_URL}/users/token", data={"username": email, "password": password})
        if response.status_code == 200:
            session['token'] = response.json()['access_token']
            return redirect(url_for('dashboard'))
        else:
            return "Login Failed", 401
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'token' not in session:
        return redirect(url_for('login'))
    
    headers = {'Authorization': f"Bearer {session['token']}"}
    response = requests.get(f"{BACKEND_URL}/devices/", headers=headers)
    devices = response.json() if response.status_code == 200 else []
    
    return render_template('dashboard.html', devices=devices)

@app.route('/add_device', methods=['GET', 'POST'])
def add_device():
    if 'token' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Log the received form data
        print("Form data received:", request.form)
        
        device_name = request.form.get('device_name')
        device_type = request.form.get('device_type')
        model = request.form.get('model')
        version = request.form.get('version')

        # Make sure the data is captured correctly
        print("Captured data:", device_name, device_type, model, version)

        headers = {'Authorization': f"Bearer {session['token']}"}
        data = {
            "device_name": device_name,
            "device_type": device_type,
            "model": model,
            "version": version,
        }
        
        # Log the data to be sent to the backend
        print("Data being sent to backend:", data)
        
        response = requests.post(f"{BACKEND_URL}/devices/", json=data, headers=headers)
        
        # Log the backend response
        print("Backend response status:", response.status_code)
        print("Backend response text:", response.text)
        
        if response.status_code == 200:
            device = response.json()
            return redirect(url_for('setup_device', device_id=device['id']))
        else:
            return "Failed to Add Device", 400

    # Simulate nearby Bluetooth devices for GET request
    nearby_devices = [
        ("00:11:22:33:44:55", "newhome-planter"),
        ("66:77:88:99:AA:BB", "newhome-blind"),
        ("CC:DD:EE:FF:00:11", "newhome-voice-assistant")
    ]

    return render_template('add_device.html', nearby_devices=nearby_devices)


@app.route('/control_device/<int:device_id>', methods=['GET', 'POST'])
def control_device(device_id):
    if 'token' not in session:
        return redirect(url_for('login'))

    headers = {'Authorization': f"Bearer {session['token']}"}
    if request.method == 'POST':
        action = request.form['action']
        # Implement control logic here
        # This is a placeholder for whatever actions you need to send to the backend or device
        return redirect(url_for('dashboard'))
    
    response = requests.get(f"{BACKEND_URL}/devices/{device_id}", headers=headers)
    device = response.json() if response.status_code == 200 else None
    return render_template('control_device.html', device=device)

@app.route('/setup_device/<int:device_id>', methods=['GET', 'POST'])
def setup_device(device_id):
    if 'token' not in session:
        return redirect(url_for('login'))

    headers = {'Authorization': f"Bearer {session['token']}"}
    
    if request.method == 'POST':
        # Capture only the necessary setup data from the form
        setup_data = {
            "data": {
                "user_info": {
                    "mode": request.form.get('mode'),
                    # Add other fields depending on the selected mode
                }
            }
        }

        # Send the setup data directly to the IoT device via Bluetooth
        device_response = requests.post(f"http://127.0.0.1:5000/simulate_bluetooth/{device_id}", json=setup_data)
        
        if device_response.status_code == 200:
            # Send the IoT data to the backend
            response = requests.post(f"{BACKEND_URL}/devices/{device_id}/setup", json=setup_data, headers=headers)
            
            if response.status_code == 200:
                return redirect(url_for('dashboard'))
            else:
                print("Failed to add device to backend:", response.text)
                return "Failed to add device to backend", 400
        else:
            print("Failed to setup device via Bluetooth:", device_response.text)
            return "Failed to setup device via Bluetooth", 400

    return render_template('setup.html', device_id=device_id)


@app.route('/simulate_bluetooth/<int:device_id>', methods=['POST'])
def simulate_bluetooth(device_id):
    setup_data = request.json
    print(f"Received setup data for device {device_id}:", setup_data)
    
    # Simulate setup confirmation
    return "Device setup successful", 200


@app.route('/delete_device/<int:device_id>', methods=['POST'])
def delete_device(device_id):
    if 'token' not in session:
        return redirect(url_for('login'))
    
    headers = {'Authorization': f"Bearer {session['token']}"}
    response = requests.delete(f"{BACKEND_URL}/devices/{device_id}", headers=headers)
    
    if response.status_code == 200:
        return redirect(url_for('dashboard'))
    else:
        return "Failed to Delete Device", 400

@app.route('/logout')
def logout():
    session.pop('token', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
