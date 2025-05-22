# Python Executor

A secure Python script execution service that runs user-provided Python code with resource limits and security measures.

## Features

- 🔒 Secure execution environment with resource limits
- 📝 JSON input/output format
- 🚫 Restricted access to system resources
- 🔄 Automatic cleanup of temporary files

## Installation

1. Clone the repository:

```bash
git clone https://github.com/jaecobd1/python-executor.git
cd python-executor
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### API Endpoint

The service exposes a single endpoint:

```
POST /execute
```

#### Request Format

```json
{
  "script": "def main():\n    return {'message': 'Hello, World!'}"
}
```

The script must contain a `main()` function that returns a JSON-serializable value.

#### Response Format

Success (200):

```json
{
    "result": <script_output>,
    "stdout": <stdout_output>
}
```

Error (400/500):

```json
{
    "error": <error_message>,
    "stdout": <stdout_output>,
    "stderr": <stderr_output>
}
```

### Examples

#### Example Request

![Example Request](Example%20Request.png)

#### Using curl

```bash
curl -X POST https://python-executor-685779681998.us-east1.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    return {\"message\": \"Hello from curl!\"}"
  }'
```

#### Using Python

```python
import requests

script = """
def main():
    return {'message': 'Hello from the sandbox!'}
"""

response = requests.post('http://localhost:8080/execute', json={'script': script})
print(response.json())
```

## Security

The service implements several security measures:

1. **Resource Limits**:
   - 5-second CPU time limit
   - 50MB memory limit
   - Limited file descriptors (10 max)
2. **Input Validation**: Checks for required `main()` function
3. **Output Validation**: Ensures JSON-serializable output
4. **Isolated Execution**: Scripts run in temporary directories that are automatically cleaned up
5. **Error Handling**: Comprehensive error catching and reporting

### IAM

IAM authentication has been added to the Google Cloud code runner.
It is a security concern to have an openly accessible URL.

## Running the application

### Docker

Build and run with Docker:

```bash
docker build -t python-executor .
docker run -p 8080:8080 python-executor
```
