import json
import os
import urllib.request
import importlib
import sys


def load_handler(handler_name):
    """Dynamically loads the handler function from the module."""
    try:
        module_name, func_name = handler_name.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, func_name)
    except (ImportError, AttributeError) as e:
        print(f"Error loading handler '{handler_name}': {e}", file=sys.stderr)
        sys.exit(1)

def main():
    while True:
        # Get event data from Lambda runtime API
        req = urllib.request.Request(
            os.environ["AWS_LAMBDA_RUNTIME_API"] + "/2018-06-01/runtime/invocation/next"
        )
        with urllib.request.urlopen(req) as res:
            event = json.load(res)
            request_id = res.headers["Lambda-Runtime-Aws-Request-Id"]

        # Invoke the handler function (Lambda service will route to the correct handler)
        try:
            # Assuming your function code is in 'app.py'
            
            context = {}
            handler = load_handler(os.environ["_HANDLER"])
            response = handler(event, context)

            # Send response to Lambda runtime API
            req = urllib.request.Request(
                os.environ["AWS_LAMBDA_RUNTIME_API"]
                + "/2018-06-01/runtime/invocation/"
                + request_id
                + "/response",
                data=json.dumps(response).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Transfer-Encoding": "chunked",
                    "Lambda-Runtime-Function-Response-Mode": "streaming",
                },
            )
            with urllib.request.urlopen(req):
                pass

        except Exception as e:
            # Send error to Lambda runtime API
            req = urllib.request.Request(
                os.environ["AWS_LAMBDA_RUNTIME_API"]
                + "/2018-06-01/runtime/invocation/"
                + request_id
                + "/error",
                data=json.dumps({"errorMessage": str(e)}).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Lambda-Runtime-Function-Error-Type": "Unhandled",
                },
            )
            with urllib.request.urlopen(req):
                pass


if __name__ == "__main__":
    main()
