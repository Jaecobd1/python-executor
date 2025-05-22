from flask import Flask, request, jsonify
import tempfile
import subprocess
import uuid
import os
import json
import shutil
import logging
import resource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def limit_resources():
    # Set resource limits
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))  # 5 seconds CPU time
    resource.setrlimit(resource.RLIMIT_AS, (50 * 1024 * 1024, 50 * 1024 * 1024))  # 50MB memory
    resource.setrlimit(resource.RLIMIT_NOFILE, (10, 10))  # Limit file descriptors

@app.route('/execute', methods=['POST'])
def execute():
    data = request.get_json()

    if not data or 'script' not in data:
        return jsonify({'error': 'No script provided'}), 400
    script = data['script']
    if 'def main()' not in script:
        return jsonify({'error': 'Script must contain a main() function'}), 400

    # Create a unique directory in the sandbox
    sandbox_dir = os.path.join('/sandbox', str(uuid.uuid4()))
    os.makedirs(sandbox_dir, exist_ok=True)
    os.chmod(sandbox_dir, 0o777)
    logger.info(f"Created sandbox directory: {sandbox_dir}")

    # Create the script file in the sandbox
    script_path = os.path.join(sandbox_dir, 'user_script.py')

    # Wrap the user's script with code to capture the result
    wrapped_script = f"""{script}

if __name__ == "__main__":
    import json
    import sys
    try:
        result = main()
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({{"error": str(e)}}), file=sys.stderr)
        sys.exit(1)
    """

    # Write the wrapped script to the sandbox
    with open(script_path, 'w') as f:
        f.write(wrapped_script)
    os.chmod(script_path, 0o666)
    logger.info(f"Wrote script to: {script_path}")

    try:
        # Execute the script with resource limits
        result = subprocess.run(
            [
                "python3",
                "-c",
                f"import resource; resource.setrlimit(resource.RLIMIT_CPU, (5, 5)); resource.setrlimit(resource.RLIMIT_AS, (50 * 1024 * 1024, 50 * 1024 * 1024)); resource.setrlimit(resource.RLIMIT_NOFILE, (10, 10)); exec(open('{script_path}').read())"
            ],
            capture_output=True,
            text=True,
            timeout=5
        )
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Execution timed out'}), 500
    finally:
        # Cleanup
        shutil.rmtree(sandbox_dir, ignore_errors=True)

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    logger.info(f"Script stdout: {stdout}")
    logger.info(f"Script stderr: {stderr}")

    if result.returncode != 0:
        return jsonify({
            "error": "Script execution failed",
            "stdout": stdout,
            "stderr": stderr
        }), 500

    try:
        result_json = json.loads(stdout)
        logger.info(f"Parsed result: {result_json}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse result: {e}")
        return jsonify({
            "error": "Script did not return valid JSON",
            "stdout": stdout,
            "stderr": stderr
        }), 400

    return jsonify({
        "result": result_json,
        "stdout": stdout,
    }), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
