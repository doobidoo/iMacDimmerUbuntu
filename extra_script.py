Import("env")
import os

# Parse .env file manually
env_vars = {}
# Get the project directory from the environment
project_dir = env.subst("$PROJECT_DIR")
env_file = os.path.join(project_dir, '.env')

if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()

# Get WiFi credentials from parsed .env or fallback
wifi_ssid = env_vars.get('WIFI_SSID', 'YOUR_SSID_HERE')
wifi_password = env_vars.get('WIFI_PASSWORD', 'YOUR_PASSWORD_HERE')

# Add build flags
env.Append(
    BUILD_FLAGS=[
        f'-D WIFI_SSID=\\"{wifi_ssid}\\"',
        f'-D WIFI_PASSWORD=\\"{wifi_password}\\"'
    ]
)