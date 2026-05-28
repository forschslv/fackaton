import { execSync, spawn } from 'child_process';
import * as path from 'path';

console.log("=== STARTING SANDBOX ENVIRONMENT INIT ===");

function checkCommand(command: string): boolean {
    try {
        execSync(command, { stdio: 'ignore' });
        return true;
    } catch (e) {
        return false;
    }
}

async function startApp() {
    console.log("Detecting system environments...");
    
    const hasPython = checkCommand("python3 --version");
    if (!hasPython) {
        console.error("CRITICAL ERROR: python3 is not installed or accessible in this container container sandbox.");
        process.exit(1);
    }
    
    console.log("Python 3 found. Running dependency installation process...");
    
    // Install python requirements dynamically at runtime startup
    try {
        console.log("Executing pip installer for requirements...");
        execSync("python3 -m pip install --break-system-packages --no-cache-dir -r requirements.txt --user || pip3 install --break-system-packages --no-cache-dir -r requirements.txt || python3 -m pip install --no-cache-dir -r requirements.txt --user || pip3 install --no-cache-dir -r requirements.txt", { stdio: 'inherit' });
        console.log("Dependency installation completed successfully!");
    } catch (e) {
        console.warn("WARNING: Dependency installer exited with codes. Attempting to run app with fallback packages:", e);
    }

    console.log("Launching Flask Application on dedicated Port 3000...");
    
    // Spawn the python process as a daemon
    const appPath = path.join(process.cwd(), "app.py");
    const flaskProcess = spawn("python3", [appPath], {
        stdio: 'inherit',
        env: {
            ...process.env,
            FLASK_APP: "app.py",
            FLASK_ENV: "development",
            PYTHONUNBUFFERED: "1"
        }
    });

    flaskProcess.on('close', (code) => {
        console.log(`Flask application process exited with status code ${code}`);
        process.exit(code || 0);
    });

    process.on('SIGINT', () => {
        flaskProcess.kill('SIGINT');
        process.exit(0);
    });

    process.on('SIGTERM', () => {
        flaskProcess.kill('SIGTERM');
        process.exit(0);
    });
}

startApp().catch(err => {
    console.error("Unexpected operational breakdown during sandbox booting: ", err);
    process.exit(1);
});
