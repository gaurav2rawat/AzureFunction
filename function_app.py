import azure.functions as func
import logging
import json
import uuid

# Instantiate the primary Function App context
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="submit", methods=["POST"])
# Declaratively bind the output straight to an Azure Table Storage container
@app.table_output(arg_name="tableOut", table_name="UserProfiles", connection="AzureWebJobsStorage")
def submit_profile(req: func.HttpRequest, tableOut: func.Out[str]) -> func.HttpResponse:
    logging.info("Processing incoming user registration payload...")

    try:
        req_body = req.get_json()
        if not isinstance(req_body, dict):
            return func.HttpResponse("Request body must be a JSON object.", status_code=400)

        username = req_body.get('username')
        email = req_body.get('email')

        if not isinstance(username, str) or not username.strip() or not isinstance(email, str) or not email.strip():
            return func.HttpResponse("Missing username or email fields.", status_code=400)

        # Structure the payload targeting Table Storage rules (Requires PartitionKey & RowKey)
        row_key = str(uuid.uuid4())
        profile_entity = {
            "PartitionKey": "WebRegistration",
            "RowKey": row_key,
            "Username": username,
            "Email": email
        }

        # Convert entity to string representation and flush it via output binding plumbing
        tableOut.set(json.dumps(profile_entity))

        return func.HttpResponse(
            body=f"Profile registered successfully under record ID {row_key}!",
            status_code=201
        )

    except ValueError:
        return func.HttpResponse("Invalid payload structure.", status_code=400)
