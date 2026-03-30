# OpenAI Python SDK Documentation

## Introduction

The OpenAI Python SDK (version 2.24.0) provides a comprehensive, type-safe interface for accessing the OpenAI REST API from Python 3.9+ applications. Built on top of the httpx library, the SDK offers both synchronous (`OpenAI`) and asynchronous (`AsyncOpenAI`) clients with full type definitions for all request parameters and response fields. The library is auto-generated from OpenAI's OpenAPI specification using Stainless, ensuring API consistency and completeness.

The SDK supports a wide range of AI capabilities including text generation, image creation and editing, audio transcription and synthesis, embeddings, fine-tuning, and real-time conversational experiences. With built-in support for streaming responses, automatic pagination, retry logic, webhook verification, and structured output parsing via Pydantic models, developers can quickly integrate OpenAI's powerful models into their applications with minimal boilerplate code.

---

## API Documentation

### Responses API

The primary API for interacting with OpenAI models, enabling text generation with customizable instructions.

```python
# Basic text generation with the Responses API
# The Responses API is the recommended way to generate text from OpenAI models
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # Can be omitted if env var is set
)

response = client.responses.create(
    model="gpt-5.2",
    instructions="You are a coding assistant that talks like a pirate.",
    input="How do I check if a Python object is an instance of a class?",
)

print(response.output_text)
# Access request ID for debugging: print(response._request_id)
```

### Chat Completions API

The previous standard API for generating conversational responses, supporting multi-turn conversations with different roles.

```python
# Chat Completions API for multi-turn conversations
# Supports developer, user, and assistant roles for structured dialogue
from openai import OpenAI

client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-5.2",
    messages=[
        {"role": "developer", "content": "Talk like a pirate."},
        {
            "role": "user",
            "content": "How do I check if a Python object is an instance of a class?",
        },
    ],
)

print(completion.choices[0].message.content)

# Additional methods available:
# client.chat.completions.retrieve(completion_id)  - Get a specific completion
# client.chat.completions.update(completion_id, **params)  - Update metadata
# client.chat.completions.list(**params)  - List completions with pagination
# client.chat.completions.delete(completion_id)  - Delete a completion
```

### Structured Outputs with Pydantic

Parse API responses directly into Pydantic models for type-safe data handling.

```python
# Structured output parsing with Pydantic models
# The .parse() method automatically converts responses to your defined schema
from typing import List
from pydantic import BaseModel
from openai import OpenAI

class Step(BaseModel):
    explanation: str
    output: str

class MathResponse(BaseModel):
    steps: List[Step]
    final_answer: str

client = OpenAI()
completion = client.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "You are a helpful math tutor."},
        {"role": "user", "content": "solve 8x + 31 = 2"},
    ],
    response_format=MathResponse,  # Pydantic model for structured output
)

message = completion.choices[0].message
if message.parsed:
    print(message.parsed.steps)  # List[Step] - typed access to parsed data
    print("answer: ", message.parsed.final_answer)
else:
    print(message.refusal)  # Handle model refusals gracefully
```

### Function Tool Calls with Auto-Parsing

Define function tools using Pydantic models for automatic argument parsing.

```python
# Auto-parsing function tool calls with Pydantic schemas
# Use pydantic_function_tool() to define tools with strict typing
from enum import Enum
from typing import List, Union
from pydantic import BaseModel
import openai

class Table(str, Enum):
    orders = "orders"
    customers = "customers"
    products = "products"

class Operator(str, Enum):
    eq = "="
    gt = ">"
    lt = "<"

class Condition(BaseModel):
    column: str
    operator: Operator
    value: Union[str, int]

class Query(BaseModel):
    table_name: Table
    columns: List[str]
    conditions: List[Condition]

client = openai.OpenAI()
completion = client.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "You help users query databases."},
        {"role": "user", "content": "Find all orders from May 2023"},
    ],
    tools=[
        openai.pydantic_function_tool(Query),  # Auto-generates JSON schema
    ],
)

tool_call = (completion.choices[0].message.tool_calls or [])[0]
print(tool_call.function.parsed_arguments.table_name)  # Typed as Query
```

### Streaming Responses

Stream responses in real-time using Server Side Events (SSE) for progressive content delivery.

```python
# Streaming responses for real-time content delivery
# Use stream=True for progressive output or .stream() for event-based handling
from openai import OpenAI

client = OpenAI()

# Simple streaming with iteration
stream = client.responses.create(
    model="gpt-5.2",
    input="Write a one-sentence bedtime story about a unicorn.",
    stream=True,
)

for event in stream:
    print(event)

# Event-based streaming with .stream() context manager
# Provides granular control over different event types
from openai import AsyncOpenAI

async_client = AsyncOpenAI()

async with async_client.chat.completions.stream(
    model='gpt-4o-2024-08-06',
    messages=[{"role": "user", "content": "Tell me a story"}],
) as stream:
    async for event in stream:
        if event.type == 'content.delta':
            print(event.delta, flush=True, end='')  # Progressive text output
        elif event.type == 'content.done':
            print(event.parsed)  # Final parsed content

# Get accumulated completion after streaming
completion = await stream.get_final_completion()
```

### Async Usage

Use the asynchronous client for concurrent operations and improved performance.

```python
# Asynchronous client for concurrent API operations
# AsyncOpenAI provides identical functionality with async/await syntax
import os
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

async def main() -> None:
    response = await client.responses.create(
        model="gpt-5.2",
        input="Explain disestablishmentarianism to a smart five year old."
    )
    print(response.output_text)

asyncio.run(main())

# For improved concurrency, use aiohttp backend
# pip install openai[aiohttp]
from openai import DefaultAioHttpClient

async def with_aiohttp() -> None:
    async with AsyncOpenAI(
        http_client=DefaultAioHttpClient(),
    ) as client:
        completion = await client.chat.completions.create(
            messages=[{"role": "user", "content": "Say this is a test"}],
            model="gpt-5.2",
        )
        print(completion.choices[0].message.content)
```

### Vision API

Process images using URL references or base64-encoded data.

```python
# Vision capabilities for image understanding
# Supports both URL references and base64-encoded images
from openai import OpenAI
import base64

client = OpenAI()

# With an image URL
prompt = "What is in this image?"
img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/2023_06_08_Raccoon1.jpg/1599px-2023_06_08_Raccoon1.jpg"

response = client.responses.create(
    model="gpt-5.2",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": f"{img_url}"},
            ],
        }
    ],
)

# With base64-encoded image
with open("path/to/image.png", "rb") as image_file:
    b64_image = base64.b64encode(image_file.read()).decode("utf-8")

response = client.responses.create(
    model="gpt-5.2",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Describe this image"},
                {"type": "input_image", "image_url": f"data:image/png;base64,{b64_image}"},
            ],
        }
    ],
)
```

### Audio Transcription API

Convert audio files to text with support for multiple formats and languages.

```python
# Audio transcription for speech-to-text conversion
# Supports various audio formats and provides detailed transcription options
from openai import OpenAI

client = OpenAI()

# Basic transcription
transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=open("audio.mp3", "rb"),
)
print(transcription.text)

# Verbose transcription with timestamps and segments
# Available response formats: json, text, srt, verbose_json, vtt
transcription = client.audio.transcriptions.create(
    model="whisper-1",
    file=open("audio.mp3", "rb"),
    response_format="verbose_json",
    timestamp_granularities=["word", "segment"],
)
# Access detailed transcription data including word-level timestamps
```

### Audio Translation API

Translate audio from any supported language to English.

```python
# Audio translation converts non-English audio to English text
# Useful for multilingual content processing
from openai import OpenAI

client = OpenAI()

translation = client.audio.translations.create(
    model="whisper-1",
    file=open("german_audio.mp3", "rb"),
)
print(translation.text)  # English translation of the audio content
```

### Text-to-Speech API

Generate natural-sounding speech from text input.

```python
# Text-to-speech synthesis for audio generation
# Returns binary audio content that can be saved or streamed
from pathlib import Path
from openai import OpenAI

client = OpenAI()

speech = client.audio.speech.create(
    model="tts-1",  # Use "tts-1-hd" for higher quality
    voice="alloy",  # Available: alloy, echo, fable, onyx, nova, shimmer
    input="Hello world! This is a test of text to speech.",
)

# Save the audio to a file
speech_file = Path("output.mp3")
speech.stream_to_file(speech_file)

# Or work with the raw bytes
audio_bytes = speech.content
```

### Embeddings API

Generate vector representations of text for semantic search and similarity comparisons.

```python
# Embeddings API for vector representations of text
# Useful for semantic search, clustering, and similarity comparisons
from openai import OpenAI

client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-small",  # Or "text-embedding-3-large" for higher dimensions
    input="The quick brown fox jumps over the lazy dog.",
    encoding_format="float",  # Or "base64" for compact representation
)

embedding_vector = response.data[0].embedding
print(f"Embedding dimension: {len(embedding_vector)}")
print(f"Usage: {response.usage.total_tokens} tokens")

# Batch embedding for multiple texts
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=["First text", "Second text", "Third text"],
)
# Access embeddings: response.data[0].embedding, response.data[1].embedding, etc.
```

### Images API

Generate, edit, and create variations of images.

```python
# Image generation and manipulation
# Supports DALL-E models for creating and editing images
from openai import OpenAI

client = OpenAI()

# Generate a new image
response = client.images.generate(
    model="dall-e-3",
    prompt="A white siamese cat sitting on a windowsill at sunset",
    size="1024x1024",  # Options: 256x256, 512x512, 1024x1024, 1792x1024, 1024x1792
    quality="standard",  # Or "hd" for higher detail
    n=1,  # Number of images to generate
)
image_url = response.data[0].url

# Edit an existing image (requires mask for inpainting)
response = client.images.edit(
    model="dall-e-2",
    image=open("original.png", "rb"),
    mask=open("mask.png", "rb"),
    prompt="Add a rainbow in the sky",
    n=1,
    size="1024x1024",
)

# Create variations of an image
response = client.images.create_variation(
    image=open("image.png", "rb"),
    n=2,
    size="1024x1024",
)
```

### Files API

Upload and manage files for use with other API features.

```python
# File management for uploads and retrieval
# Files are used with fine-tuning, assistants, and batch processing
from pathlib import Path
from openai import OpenAI

client = OpenAI()

# Upload a file
file = client.files.create(
    file=Path("training_data.jsonl"),
    purpose="fine-tune",  # Options: fine-tune, assistants, batch
)
print(f"File ID: {file.id}")

# List all files
files = client.files.list()
for f in files:
    print(f"{f.id}: {f.filename} ({f.purpose})")

# Retrieve file metadata
file_info = client.files.retrieve(file.id)
print(f"Status: {file_info.status}")

# Download file content
content = client.files.content(file.id)
# Or as text: content_text = client.files.retrieve_content(file.id)

# Delete a file
client.files.delete(file.id)

# Wait for file processing to complete
file = client.files.wait_for_processing(file.id)
```

### Fine-Tuning API

Create custom models trained on your specific data.

```python
# Fine-tuning API for creating custom models
# Train models on your data for specialized tasks
from openai import OpenAI

client = OpenAI()

# Create a fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file="file-abc123",  # ID from files.create()
    model="gpt-4o-mini-2024-07-18",
    hyperparameters={
        "n_epochs": 3,
    },
)
print(f"Job ID: {job.id}")

# Monitor job status
job = client.fine_tuning.jobs.retrieve(job.id)
print(f"Status: {job.status}")

# List all fine-tuning jobs
for job in client.fine_tuning.jobs.list(limit=10):
    print(f"{job.id}: {job.status}")

# List events for a job
for event in client.fine_tuning.jobs.list_events(job.id):
    print(f"{event.created_at}: {event.message}")

# Cancel a running job
client.fine_tuning.jobs.cancel(job.id)

# Pause and resume jobs
client.fine_tuning.jobs.pause(job.id)
client.fine_tuning.jobs.resume(job.id)
```

### Assistants API

Create AI assistants with persistent memory, tools, and file access.

```python
# Assistants API for stateful AI interactions
# Assistants can use tools, access files, and maintain conversation context
from openai import OpenAI

client = OpenAI()

# Create an assistant
assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Help students with algebra.",
    tools=[{"type": "code_interpreter"}],  # Enable code execution
    model="gpt-4o",
)

# Create a thread for conversation
thread = client.beta.threads.create()

# Add a message to the thread
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Solve the equation 3x + 11 = 14",
)

# Run the assistant and wait for completion
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
)

if run.status == "completed":
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    for msg in messages:
        print(f"{msg.role}: {msg.content[0].text.value}")

# Clean up
client.beta.assistants.delete(assistant.id)
client.beta.threads.delete(thread.id)
```

### Assistant Streaming

Stream assistant responses with event-based handling.

```python
# Streaming assistant responses with event handlers
# Subscribe to specific events during assistant execution
from typing_extensions import override
from openai import AssistantEventHandler, OpenAI
from openai.types.beta.threads import Text, TextDelta
from openai.types.beta.threads.runs import ToolCall, ToolCallDelta

client = OpenAI()

class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text: Text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta: TextDelta, snapshot: Text):
        print(delta.value, end="", flush=True)

    @override
    def on_tool_call_created(self, tool_call: ToolCall):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    @override
    def on_tool_call_delta(self, delta: ToolCallDelta, snapshot: ToolCall):
        if delta.type == "code_interpreter" and delta.code_interpreter:
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)

# Stream with event handler
with client.beta.threads.runs.stream(
    thread_id="thread_id",
    assistant_id="assistant_id",
    event_handler=EventHandler(),
) as stream:
    stream.until_done()
```

### Vector Stores API

Create and manage vector stores for semantic search over documents.

```python
# Vector stores for document retrieval and semantic search
# Store and search through large document collections
from openai import OpenAI

client = OpenAI()

# Create a vector store
vector_store = client.vector_stores.create(
    name="Product Documentation",
)

# Upload and add a file to the vector store
file = client.files.create(file=open("docs.pdf", "rb"), purpose="assistants")
vs_file = client.vector_stores.files.create_and_poll(
    vector_store_id=vector_store.id,
    file_id=file.id,
)

# Search the vector store
results = client.vector_stores.search(
    vector_store_id=vector_store.id,
    query="How do I reset my password?",
)
for result in results:
    print(f"Score: {result.score}, Content: {result.content}")

# Batch file upload with polling
batch = client.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id,
    files=[open("doc1.pdf", "rb"), open("doc2.pdf", "rb")],
)

# Delete vector store
client.vector_stores.delete(vector_store.id)
```

### Realtime API

Build low-latency, multi-modal conversational experiences using WebSockets.

```python
# Realtime API for low-latency conversational AI
# Supports text and audio input/output via WebSocket connections
import asyncio
from openai import AsyncOpenAI

async def main():
    client = AsyncOpenAI()

    async with client.realtime.connect(model="gpt-realtime") as connection:
        # Configure the session
        await connection.session.update(
            session={"type": "realtime", "output_modalities": ["text"]}
        )

        # Send a message
        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Say hello!"}],
            }
        )
        await connection.response.create()

        # Process events
        async for event in connection:
            if event.type == "response.output_text.delta":
                print(event.delta, flush=True, end="")
            elif event.type == "response.output_text.done":
                print()
            elif event.type == "response.done":
                break
            elif event.type == "error":
                # Handle errors - connection stays open
                print(f"Error: {event.error.message}")

asyncio.run(main())
```

### Batch API

Process large numbers of requests asynchronously with cost savings.

```python
# Batch API for asynchronous bulk processing
# Submit multiple requests for later processing at reduced cost
from openai import OpenAI

client = OpenAI()

# Create a batch from a JSONL file of requests
batch = client.batches.create(
    input_file_id="file-abc123",  # JSONL file with request objects
    endpoint="/v1/chat/completions",
    completion_window="24h",
)
print(f"Batch ID: {batch.id}")

# Check batch status
batch = client.batches.retrieve(batch.id)
print(f"Status: {batch.status}")
print(f"Completed: {batch.request_counts.completed}/{batch.request_counts.total}")

# List all batches
for b in client.batches.list():
    print(f"{b.id}: {b.status}")

# Cancel a pending batch
client.batches.cancel(batch.id)

# When complete, download results from batch.output_file_id
```

### Moderations API

Check content for policy compliance and safety.

```python
# Content moderation for safety and policy compliance
# Analyze text and images for potentially harmful content
from openai import OpenAI

client = OpenAI()

# Text moderation
response = client.moderations.create(
    model="omni-moderation-latest",
    input="Sample text to check for policy violations",
)

result = response.results[0]
print(f"Flagged: {result.flagged}")
print(f"Categories: {result.categories}")
print(f"Scores: {result.category_scores}")

# Multi-modal moderation with images
response = client.moderations.create(
    model="omni-moderation-latest",
    input=[
        {"type": "text", "text": "Check this image"},
        {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}},
    ],
)
```

### Models API

List and manage available models.

```python
# Models API for listing and managing available models
from openai import OpenAI

client = OpenAI()

# List all available models
models = client.models.list()
for model in models:
    print(f"{model.id}: owned by {model.owned_by}")

# Retrieve specific model details
model = client.models.retrieve("gpt-4o")
print(f"Model: {model.id}")
print(f"Created: {model.created}")

# Delete a fine-tuned model
client.models.delete("ft:gpt-4o:my-org:custom-suffix:id")
```

### Webhooks

Verify and process webhook events from OpenAI.

```python
# Webhook verification and event handling
# Verify webhook signatures to ensure events are from OpenAI
from openai import OpenAI
from flask import Flask, request

app = Flask(__name__)
client = OpenAI()  # Uses OPENAI_WEBHOOK_SECRET env var

@app.route("/webhook", methods=["POST"])
def webhook():
    request_body = request.get_data(as_text=True)

    try:
        # Unwrap verifies signature and parses the event
        event = client.webhooks.unwrap(request_body, request.headers)

        if event.type == "response.completed":
            print("Response completed:", event.data)
        elif event.type == "response.failed":
            print("Response failed:", event.data)
        else:
            print("Unhandled event type:", event.type)

        return "ok"
    except Exception as e:
        print("Invalid signature:", e)
        return "Invalid signature", 400

# Alternative: verify signature separately
@app.route("/webhook2", methods=["POST"])
def webhook2():
    request_body = request.get_data(as_text=True)

    # Just verify, don't parse
    client.webhooks.verify_signature(request_body, request.headers)
    # Then parse manually if needed
    import json
    event = json.loads(request_body)
    return "ok"
```

### Error Handling

Handle API errors gracefully with specific exception types.

```python
# Comprehensive error handling for API operations
# All errors inherit from openai.APIError for easy catching
import openai
from openai import OpenAI

client = OpenAI()

try:
    client.fine_tuning.jobs.create(
        model="gpt-4o",
        training_file="file-abc123",
    )
except openai.APIConnectionError as e:
    # Network connectivity issues
    print("The server could not be reached")
    print(e.__cause__)
except openai.RateLimitError as e:
    # 429 status code - rate limit exceeded
    print("Rate limit exceeded, back off and retry")
    print(f"Request ID: {e.request_id}")
except openai.BadRequestError as e:
    # 400 status code - invalid request
    print(f"Bad request: {e.message}")
except openai.AuthenticationError as e:
    # 401 status code - invalid API key
    print("Authentication failed")
except openai.PermissionDeniedError as e:
    # 403 status code - insufficient permissions
    print("Permission denied")
except openai.NotFoundError as e:
    # 404 status code - resource not found
    print("Resource not found")
except openai.APIStatusError as e:
    # Catch-all for other non-200 status codes
    print(f"Status {e.status_code}: {e.message}")
    print(f"Request ID: {e.request_id}")
```

### Pagination

Navigate through large result sets with auto-pagination.

```python
# Auto-pagination for large result sets
# The SDK handles pagination automatically when iterating
from openai import OpenAI

client = OpenAI()

# Automatic pagination - fetches pages as needed
all_jobs = []
for job in client.fine_tuning.jobs.list(limit=20):
    all_jobs.append(job)

# Manual pagination control
first_page = client.fine_tuning.jobs.list(limit=20)
print(f"Next page cursor: {first_page.after}")

if first_page.has_next_page():
    print(f"Next page info: {first_page.next_page_info()}")
    next_page = first_page.get_next_page()
    print(f"Items on next page: {len(next_page.data)}")

# Async pagination
import asyncio
from openai import AsyncOpenAI

async def list_jobs():
    client = AsyncOpenAI()
    async for job in client.fine_tuning.jobs.list(limit=20):
        print(job.id)

asyncio.run(list_jobs())
```

### Azure OpenAI

Use the SDK with Microsoft Azure OpenAI Service.

```python
# Azure OpenAI integration
# Use AzureOpenAI class for Azure-hosted models
from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2023-07-01-preview",
    azure_endpoint="https://example-endpoint.openai.azure.com",
    # API key from AZURE_OPENAI_API_KEY env var
)

completion = client.chat.completions.create(
    model="deployment-name",  # Your Azure deployment name
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.to_json())

# Azure AD authentication
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")

client = AzureOpenAI(
    api_version="2023-07-01-preview",
    azure_endpoint="https://example-endpoint.openai.azure.com",
    azure_ad_token=token.token,
)
```

### Configuration and Advanced Usage

Configure retries, timeouts, and HTTP client options.

```python
# Advanced client configuration
# Customize retries, timeouts, and HTTP behavior
import httpx
from openai import OpenAI, DefaultHttpxClient

# Configure retries and timeout
client = OpenAI(
    max_retries=5,  # Default is 2
    timeout=20.0,   # Default is 10 minutes (600 seconds)
)

# Granular timeout control
client = OpenAI(
    timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0),
)

# Custom HTTP client with proxy
client = OpenAI(
    base_url="http://my.test.server.example.com:8083/v1",
    http_client=DefaultHttpxClient(
        proxy="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)

# Per-request configuration
response = client.with_options(
    max_retries=10,
    timeout=30.0,
).chat.completions.create(
    messages=[{"role": "user", "content": "Hello"}],
    model="gpt-5.2",
)

# Access raw response headers
response = client.chat.completions.with_raw_response.create(
    messages=[{"role": "user", "content": "Hello"}],
    model="gpt-5.2",
)
print(response.headers.get("X-Request-ID"))
completion = response.parse()

# Context manager for resource cleanup
with OpenAI() as client:
    response = client.responses.create(
        model="gpt-5.2",
        input="Hello",
    )
# HTTP client is automatically closed
```

---

## Summary

The OpenAI Python SDK enables seamless integration of OpenAI's powerful AI models into Python applications, supporting use cases from simple text generation to complex multi-modal conversational systems. Common integration patterns include building chatbots and virtual assistants using the Chat Completions or Responses API, implementing semantic search with embeddings and vector stores, creating content moderation pipelines with the Moderations API, and developing real-time voice applications using the Realtime API with WebSocket connections.

For production deployments, the SDK provides robust error handling with typed exceptions, automatic retries with exponential backoff, webhook verification for secure event processing, and comprehensive logging capabilities. Developers can choose between synchronous and asynchronous clients based on their concurrency requirements, leverage streaming responses for improved user experience in real-time applications, and use polling helpers for long-running operations like fine-tuning jobs. The SDK's type definitions and Pydantic integration ensure type safety throughout the development process, while the modular architecture allows for easy customization of HTTP clients, timeouts, and retry policies to meet specific production requirements.
