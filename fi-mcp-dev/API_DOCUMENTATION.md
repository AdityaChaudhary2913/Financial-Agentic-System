# FI MCP Server API Documentation

This document provides detailed instructions on how to interact with the FI MCP (Mock Control Plane) server API. It covers the authentication flow and how to make tool calls using both `curl` and Postman.

## Overview

The API uses a session-based authentication mechanism. To make an authenticated request, you must first obtain a unique `login_url`, authorize the session, and then use that session to make tool calls. The server uses a JSON-RPC 2.0 protocol for all tool-related communications over a streaming HTTP endpoint.

---

## API Workflow with `curl`

Make sure the Go server is running before you begin:
```sh
go run .
```

### Step 1: Get the Login URL

To start the authentication process, you first need to make an unauthenticated request to a tool endpoint. The server will deny access and respond with a unique `login_url` that contains a server-generated `sessionId`.

**Request:**

Send a `POST` request to the `/mcp/stream` endpoint. You must include a `Content-Type` header and a `Mcp-Session-Id` header. The session ID can be any unique string you generate.

```bash
curl -X POST \
-H "Content-Type: application/json" \
-H "Mcp-Session-Id: your-unique-session-id" \
-d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"fetch_net_worth","arguments":{}}}' \
http://localhost:8080/mcp/stream
```

**Response:**

The server will return a JSON-RPC response containing the `login_url`.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"status\": \"login_required\",\"login_url\": \"http://localhost:8080/mockWebPage?sessionId=your-unique-session-id\",\"message\": \"...\"}"
      }
    ]
  }
}
```

Extract the `login_url` from the response body. You will need the `sessionId` from this URL for the next step.

### Step 2: Authorize the Session

Now, use the `sessionId` to authorize your session. This is done by sending a `POST` request to the `/login` endpoint.

**Request:**

The request body must be `x-www-form-urlencoded` and contain the `sessionId` you received and a valid `phoneNumber` (which corresponds to a directory in the `test_data_dir/`).

```bash
curl -X POST \
-d 'sessionId=your-unique-session-id&phoneNumber=1010101010' \
http://localhost:8080/login
```

**Response:**

The server will return an HTML page indicating that the login was successful. You can redirect the output to `/dev/null` if you don't need to see the HTML.

```bash
# Example with output suppressed
curl -X POST -d 'sessionId=your-unique-session-id&phoneNumber=1010101010' http://localhost:8080/login > /dev/null
```

### Step 3: Make the Authenticated Tool Call

Once the session is authorized, you can make the same request as in Step 1. This time, because the `Mcp-Session-Id` is associated with an authenticated user, the server will process the tool call and return the requested data.

**Request:**

```bash
curl -X POST \
-H "Content-Type: application/json" \
-H "Mcp-Session-Id: your-unique-session-id" \
-d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"fetch_net_worth","arguments":{}}}' \
http://localhost:8080/mcp/stream
```

**Response:**

The server will now return the JSON data from the corresponding file in the `test_data_dir/`.

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "content": [
            {
                "type": "text",
                "text": "{\n  \"netWorthResponse\": {\n    \"assetValues\": [\n      {\"netWorthAttribute\": \"ASSET_TYPE_MUTUAL_FUND\", \"value\": {\"currencyCode\": \"INR\", \"units\": \"84642\"}},\n      {\"netWorthAttribute\": \"ASSET_TYPE_EPF\", \"value\": {\"currencyCode\": \"INR\", \"units\": \"211111\"}},\n      {\"netWorthAttribute\": \"ASSET_TYPE_SAVINGS_ACCOUNT\", \"value\": {\"currencyCode\": \"INR\", \"units\": \"169000\"}},\n      {\"netWorthAttribute\": \"ASSET_TYPE_FIXED_DEPOSIT\", \"value\": {\"currencyCode\": \"INR\", \"units\": \"500000\"}},\n      {\"netWorthAttribute\": \"ASSET_TYPE_RECURRING_DEPOSIT\", \"value\": {\"currencyCode\": \"INR\", \"units\": \"60000\"}}\n    ],\n    \"liabilityValues\": [],\n    \"totalNetWorthValue\": {\"currencyCode\": \"INR\", \""units\": \"1024753\"}\n  }\n}"
            }
        ]
    }
}
```