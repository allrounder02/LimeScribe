### Python Function Calling Example Setup

Source: https://developers.openai.com/api/docs/guides/function-calling

This snippet demonstrates the initial setup for using function calling with the OpenAI API in Python. It imports necessary libraries and initializes the OpenAI client. This is the starting point for making API requests that involve tool usage.

```python
from openai import OpenAI
import json

client = OpenAI()

```

--------------------------------

### Install OpenAI Library for Go

Source: https://developers.openai.com/api/docs/api-reference/chat/completions/responses

Installs the OpenAI Go library using the go get command. This prepares your Go environment to use the OpenAI API.

```bash
go get -u 'github.com/openai/openai-go@v0.0.1'
```

--------------------------------

### Setup Playwright Browser Instance

Source: https://developers.openai.com/api/docs/guides/tools-computer-use

Code examples for setting up a Playwright browser instance, a common method for integrating the Computer Use tool in a local browsing environment. This requires installing the Playwright SDK for Python or JavaScript.

```python
from playwright import sync_api

browser = sync_api.sync_playwright().start()
context = browser.new_context()
page = context.new_page()

# ... your automation code ...

browser.close()
```

```javascript
import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  // ... your automation code ...

  await browser.close();
})();
```

--------------------------------

### Configure ChatKit Starter Prompts

Source: https://developers.openai.com/api/docs/guides/chatkit-themes

Display suggested prompts on the start screen to guide users on what they can ask or do. This enhances user experience by providing clear starting points.

```js
const options: Partial<ChatKitOptions> = {
  startScreen: {
    greeting: "What can I help you build today?",
    prompts: [
      {
        name: "Check on the status of a ticket",
        prompt: "Can you help me check on the status of a ticket?",
        icon: "search"
      },
      {
        name: "Create Ticket",
        prompt: "Can you help me create a new support ticket?",
        icon: "write"
      },
    ],
  },
};
```

--------------------------------

### POST /v1/chat/completions - Audio Input Example

Source: https://developers.openai.com/api/docs/guides/audio

This example demonstrates how to fetch an audio file, convert it to a base64 encoded string, and then use it as input for the chat completions API.

```APIDOC
## POST /v1/chat/completions

### Description
This endpoint allows for chat-based interactions, including the ability to process audio input alongside text.

### Method
POST

### Endpoint
https://api.openai.com/v1/chat/completions

### Parameters
#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The ID of the model to use for this API call. 
- **modalities** (array) - Required - Specifies the modalities to be used in the conversation. Must include "text" and "audio".
- **audio** (object) - Required - Configuration for audio processing.
  - **voice** (string) - Required - The voice to use for audio output (e.g., "alloy").
  - **format** (string) - Required - The audio format (e.g., "wav").
- **messages** (array) - Required - A list of messages comprising the conversation.
  - **role** (string) - Required - The role of the author of the message (e.g., "user", "assistant").
  - **content** (array) - Required - The content of the message, which can include text and audio.
    - **type** (string) - Required - The type of content (e.g., "text", "input_audio").
    - **text** (string) - Optional - The text content of the message.
    - **input_audio** (object) - Optional - The audio input object.
      - **data** (string) - Required - The base64 encoded audio data.
      - **format** (string) - Required - The format of the audio data (e.g., "wav").

### Request Example
```json
{
  "model": "gpt-audio",
  "modalities": ["text", "audio"],
  "audio": { "voice": "alloy", "format": "wav" },
  "messages": [
    {
      "role": "user",
      "content": [
        { "type": "text", "text": "What is in this recording?" },
        {
          "type": "input_audio",
          "input_audio": {
            "data": "<base64 bytes here>",
            "format": "wav"
          }
        }
      ]
    }
  ]
}
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the completion.
- **object** (string) - Type of object returned, e.g. `chat.completion`.
- **created** (integer) - Unix timestamp of when the completion was created.
- **model** (string) - The model used for the completion.
- **choices** (array) - A list of completion choices.
  - **index** (integer) - Index of the choice.
  - **message** (object) - The message content.
    - **role** (string) - The role of the author of the message.
    - **content** (string) - The content of the message.
  - **logprobs** (object) - Null or object containing log probabilities.
- **usage** (object) - Usage statistics for the request.
  - **prompt_tokens** (integer) - Number of tokens in the prompt.
  - **completion_tokens** (integer) - Number of tokens in the completion.
  - **total_tokens** (integer) - Total number of tokens.

#### Response Example
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-audio",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "This recording contains the sound of a dog barking."
      },
      "logprobs": null
    }
  ],
  "usage": {
    "prompt_tokens": 30,
    "completion_tokens": 10,
    "total_tokens": 40
  }
}
```
```

--------------------------------

### Combined Contextualization and Retrieval Prompt Example (Chat Format)

Source: https://developers.openai.com/api/docs/guides/latency-optimization

This example demonstrates a system prompt for a chat-based model that combines query contextualization and retrieval determination. It specifies the desired JSON output format and includes examples for clarity.

```chat
SYSTEM: Given the previous conversation, re-write the last user query so it contains
all necessary context. Then, determine whether the full request requires doing a
realtime lookup to respond to.

Respond in the following form:
{
  query:"[contextualized query]",
  retrieval:"[true/false - whether retrieval is required]"
}

# Examples

History: [{user: "What is your return policy?"},{assistant: "..."}]
User Query: "How long does it cover?"
Response: {query: "How long does the return policy cover?", retrieval: "true"}

History: [{user: "How can I return this item after 30 days?"},{assistant: "..."}]
User Query: "Thank you!"
Response: {query: "Thank you!", retrieval: "false"}

# Conversation
[last 3 messages of conversation]

# User Query
[last user query]

USER: [JSON-formatted input conversation here]
```

--------------------------------

### Multi-turn Image Generation with OpenAI API

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=rooftop-garden

Illustrates how to perform multi-turn image generation, starting with an initial request and then providing follow-up instructions to modify the generated image. This example uses the OpenAI API and saves the resulting images. Requires the OpenAI client library.

```python
import base64

response = openai.responses.create(
    model="gpt-5",
    input="Generate an image of gray tabby cat hugging an otter with an orange scarf",
    tools=[{"type": "image_generation"}],
)

image_generation_calls = [
    output
    for output in response.output
    if output.type == "image_generation_call"
]

image_data = [output.result for output in image_generation_calls]

if image_data:
    image_base64 = image_data[0]

    with open("cat_and_otter.png", "wb") as f:
        f.write(base64.b64decode(image_base64))


# Follow up

response_fwup = openai.responses.create(
    model="gpt-5",
    input=[
        {
            "role": "user",
            "content": [{"type": "input_text", "text": "Now make it look realistic"}],
        },
        {
            "type": "image_generation_call",
            "id": image_generation_calls[0].id,
        },
    ],
    tools=[{"type": "image_generation"}],
)

image_data_fwup = [
    output.result
    for output in response_fwup.output
    if output.type == "image_generation_call"
]

if image_data_fwup:
    image_base64 = image_data_fwup[0]
    with open("cat_and_otter_realistic.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
```

--------------------------------

### Node.js Example - Image Generation with Transparency

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=cosmic-ballet

Node.js code example demonstrating how to generate an image with a transparent background using the OpenAI Node.js client.

```APIDOC
## Node.js Example

```javascript
import OpenAI from "openai";
import fs from "fs";

const client = new OpenAI();

const result = await client.images.generate({
    model: "gpt-image-1",
    prompt: "Draw a 2D pixel art style sprite sheet of a tabby gray cat",
    size: "1024x1024",
    background: "transparent",
    quality: "high",
});

// Save the image to a file
const image_base64 = result.data[0].b64_json;
const image_buffer = Buffer.from(image_base64, "base64");
fs.writeFileSync("sprite.png", image_buffer);
```
```

--------------------------------

### GPT-4 Response Prompt Example

Source: https://developers.openai.com/api/docs/guides/latency-optimization

This example shows a system prompt for GPT-4 that uses pre-classified fields from a previous GPT-3.5 call and retrieved context to formulate a final response. It includes 'enough_information_in_context' and 'response' fields, and takes the reasoning JSON and relevant information as input.

```chat-example
SYSTEM: You are a helpful customer service bot.

Use the retrieved context, as well as these pre-classified fields, to respond to
the user's query.

# Reasoning Fields
` ` `
[reasoning json determined in previous GPT-3.5 call]
` ` `

# Example

User: "My freaking computer screen is cracked!"

Assistant Response:
{
  "enough_information_in_context": "True",
  "response": "..."
}

USER: # Relevant Information
` ` `
[retrieved context]
` ` `

```

--------------------------------

### POST /videos - Start a Render Job

Source: https://developers.openai.com/api/docs/guides/video-generation_gallery=open&galleryItem=Cozy-Coffee-Shop-Interior

Initiates a video render job by sending a text prompt and desired video parameters to the API. The response indicates the job has started.

```APIDOC
## POST /videos

### Description
Starts a video generation job using a text prompt and specified parameters like size and duration.

### Method
POST

### Endpoint
/videos

### Parameters
#### Query Parameters
- **prompt** (string) - Required - The text description of the desired video content, including subject, action, setting, and lighting.
- **model** (string) - Required - The video generation model to use (e.g., 'sora-2').
- **size** (string) - Optional - The resolution of the video (e.g., '1280x720').
- **seconds** (integer) - Optional - The desired length of the video in seconds.

### Request Example
```json
{
  "model": "sora-2",
  "prompt": "A video of the words 'Thank you' in sparkling letters"
}
```

### Response
#### Success Response (200)
- **id** (string) - The unique identifier for the video job.
- **object** (string) - The type of object, always 'video'.
- **created_at** (integer) - Timestamp of creation.
- **status** (string) - The initial status of the job (e.g., 'queued', 'in_progress').
- **model** (string) - The model used for generation.
- **progress** (integer) - The current progress percentage (if available).
- **seconds** (string) - The requested duration of the video.
- **size** (string) - The requested resolution of the video.

#### Response Example
```json
{
  "id": "video_68d7512d07848190b3e45da0ecbebcde004da08e1e0678d5",
  "object": "video",
  "created_at": 1758941485,
  "status": "queued",
  "model": "sora-2-pro",
  "progress": 0,
  "seconds": "8",
  "size": "1280x720"
}
```
```

--------------------------------

### Execute Web Search via Curl (Chat Completions)

Source: https://developers.openai.com/api/docs/guides/migrate-to-responses

This bash command demonstrates how to perform a web search using curl, simulating the backend call for a web search tool. It sends a GET request to an example search API, URL-encoding the query parameter. It also shows how to include an API key, though it's not directly used in the example API call.

```bash
curl https://api.example.com/search \
  -G \
  --data-urlencode "q=your+search+term" \
  --data-urlencode "key=$SEARCH_API_KEY"
```

--------------------------------

### GPT-3.5 Reasoning Prompt Example

Source: https://developers.openai.com/api/docs/guides/latency-optimization

This example demonstrates a system prompt for GPT-3.5 designed to determine required fields for a customer service bot. It excludes 'enough_information_in_context' and 'response' fields, focusing on pre-classification based on conversation history. The output is a JSON object.

```chat-example
SYSTEM: You are a helpful customer service bot.

Based on the previous conversation, respond in a JSON to determine the required
fields.

# Example

User: "My freaking computer screen is cracked!"

Assistant Response:
{
  "message_is_conversation_continuation": "True",
  "number_of_messages_in_conversation_so_far": "1",
  "user_sentiment": "Aggravated",
  "query_type": "Hardware Issue",
  "response_tone": "Validating and solution-oriented",
  "response_requirements": "Propose options for repair or replacement.",
  "user_requesting_to_talk_to_human": "False",
}
```

--------------------------------

### Configure Realtime Session with Audio and Instructions

Source: https://developers.openai.com/api/docs/api-reference/realtime-server-events/input_audio_buffer/speech_started

Creates a realtime session with specified audio configuration and system instructions. The audio configuration includes input and output settings, while instructions guide the model's response style and behavior.

```json
{
  "type": "realtime",
  "audio": {
    "input": "linear16",
    "output": "ulaw"
  },
  "instructions": "Respond concisely and in a friendly tone."
}
```

--------------------------------

### OAuth Authentication

Source: https://developers.openai.com/api/docs/actions/authentication

Comprehensive guide to implementing OAuth sign-in for GPT Actions, enabling personalized experiences and access to powerful features. Includes setup, request details, and response examples.

```APIDOC
## OAuth Authentication

### Description
Actions support OAuth sign-in for users, providing personalized experiences and enabling powerful features. This involves configuring OAuth credentials in the GPT editor and handling the OAuth flow.

### Method
N/A (Configuration via GPT Editor UI, subsequent requests handled by ChatGPT)

### Endpoint
N/A (Configuration via GPT Editor UI)

### Parameters
#### Configuration Parameters (via GPT Editor UI)
- **OAuth Client ID** (string) - Required - Your application's client ID.
- **OAuth Client Secret** (string) - Required - Your application's client secret (encrypted when stored).
- **Authorization URL** (string) - Required - The URL for initiating the OAuth authorization flow.
- **Token URL** (string) - Required - The URL for exchanging the authorization code for an access token.
- **Scope** (string) - Optional - The scope of permissions requested.

#### Request Body (Example of OAuth request made by ChatGPT)
```json
{
  "grant_type": "authorization_code",
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "code": "abc123",
  "redirect_uri": "https://chat.openai.com/aip/{g-YOUR-GPT-ID-HERE}/oauth/callback"
}
```

### Request Example (User invoking an action)
When a user invokes an action requiring OAuth, they will be presented with a "Sign in to [domain]" button. After signing in, subsequent requests to the action will include the user's token in the Authorization header.

### Response
#### Success Response (Authorization URL)
- **access_token** (string) - The access token for the user.
- **token_type** (string) - The type of token (e.g., "bearer").
- **refresh_token** (string) - Optional - A token to refresh the access token.
- **expires_in** (integer) - Optional - The expiration time of the access token in seconds.

#### Response Example (Authorization URL)
```json
{
  "access_token": "example_token",
  "token_type": "bearer",
  "refresh_token": "example_token",
  "expires_in": 59
}
```

#### Response Example (Action Request with User Token)
```json
{
  "Authorization": "[Bearer/Basic] [user’s token]"
}
```

### Error Handling
- **Redirect URL Issues**: Ensure the following redirect URLs are enabled in your OAuth application:
  - `https://chat.openai.com/aip/{g-YOUR-GPT-ID-HERE}/oauth/callback`
  - `https://chatgpt.com/aip/{g-YOUR-GPT-ID-HERE}/oauth/callback`
- Debugging: Check your Auth Provider's logs for errors like 'redirect_uri is not registered for client'.
```

--------------------------------

### Enable Preambles with System Instruction (Text)

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=csv-to-charts

This example shows how to enable preambles in GPT-5.2 by providing a system or developer instruction. Preambles are brief explanations generated by the model before invoking a tool, outlining its intent. This enhances transparency, debuggability, and user confidence.

```text
System: Before you call a tool, explain why you are calling it.
```

--------------------------------

### Analyze Image with File ID (C#)

Source: https://developers.openai.com/api/docs/guides/images-vision_api-mode=responses

This C# example shows how to analyze an image by uploading it using the Files API to get a file ID, which is then used in the request.

```APIDOC
## POST /v1/responses

### Description
Analyzes the content of an image by referencing a file ID that was previously uploaded using the Files API.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for the response (e.g., "gpt-5").
- **input** (array) - Required - An array of message objects.
  - **role** (string) - Required - The role of the message author ("user").
  - **content** (array) - Required - An array of content parts.
    - **type** (string) - Required - The type of content part ("input_text" or "input_image").
    - **text** (string) - Optional - The text content for "input_text" type.
    - **image_url** (object) - Optional - The image URL for "input_image" type.
      - **file_id** (string) - Required - The ID of the uploaded file.

### Request Example
```csharp
using OpenAI.Files;
using OpenAI.Responses;
using System;
using System.Net.Http;
using System.Threading.Tasks;

string key = Environment.GetEnvironmentVariable("OPENAI_API_KEY")!;
OpenAIResponseClient client = new(model: "gpt-5", apiKey: key);

string filename = "cat_and_otter.png";
Uri imageUrl = new($"https://openai-documentation.vercel.app/images/{filename}");
using var http = new HttpClient();

// Download an image as stream
using var stream = await http.GetStreamAsync(imageUrl);

OpenAIFileClient files = new(key);
OpenAIFile file = await files.UploadFileAsync(BinaryData.FromStream(stream), filename, FileUploadPurpose.Vision);

OpenAIResponse response = (OpenAIResponse)client.CreateResponse([
    ResponseItem.CreateUserMessageItem([
        ResponseContentPart.CreateInputTextPart("what's in this image?"),
        ResponseContentPart.CreateInputImagePart(file.Id)
    ])
]);

Console.WriteLine(response.GetOutputText());
```

### Response
#### Success Response (200)
- **output_text** (string) - The analysis of the image content.
```

--------------------------------

### Voice Agent Prompt Example

Source: https://developers.openai.com/api/docs/guides/voice-agents_voice-agent-architecture=chained

An example of a detailed prompt for a voice agent, covering personality, tone, and specific instructions. This prompt is designed to guide the agent's behavior and response style in speech-to-speech interactions.

```text
# Personality and Tone
## Identity
// Who or what the AI represents (e.g., friendly teacher, formal advisor, helpful assistant). Be detailed and include specific details about their character or backstory.

## Task
// At a high level, what is the agent expected to do? (e.g. "you are an expert at accurately handling user returns")

## Demeanor
// Overall attitude or disposition (e.g., patient, upbeat, serious, empathetic)

## Tone
// Voice style (e.g., warm and conversational, polite and authoritative)

## Level of Enthusiasm
// Degree of energy in responses (e.g., highly enthusiastic vs. calm and measured)

## Level of Formality
// Casual vs. professional language (e.g., “Hey, great to see you!” vs. “Good afternoon, how may I assist you?”)

## Level of Emotion
// How emotionally expressive or neutral the AI should be (e.g., compassionate vs. matter-of-fact)

## Filler Words
// Helps make the agent more approachable, e.g. “um,” “uh,” "hm," etc.. Options are generally "none", "occasionally", "often", "very often"

## Pacing
// Rhythm and speed of delivery

## Other details
// Any other information that helps guide the personality or tone of the agent.

# Instructions
- If a user provides a name or phone number, or something else where you need to know the exact spelling, always repeat it back to the user to confirm you have the right understanding before proceeding. // Always include this
- If the caller corrects any detail, acknowledge the correction in a straightforward manner and confirm the new spelling or value.
```

--------------------------------

### Image Generation with Mask - Python

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=neon

This example demonstrates using the `responses.create` method for image generation with a mask. This approach allows for more complex interactions where the mask guides the generation process within a broader conversational context.

```APIDOC
## POST /v1/responses

### Description
Generates an image based on a text prompt and an input image, using a mask to specify areas for editing. This method is part of a broader conversational API.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for generation. e.g., "gpt-4o"
- **input** (array) - Required - An array of message objects representing the conversation history and input.
  - **role** (string) - Required - The role of the message author ('user' or 'assistant').
  - **content** (array) - Required - An array of content blocks.
    - **type** (string) - Required - The type of content ('input_text' or 'input_image').
    - **text** (string) - Required if type is 'input_text' - The text content.
    - **file_id** (string) - Required if type is 'input_image' - The ID of the uploaded image file.
- **tools** (array) - Required - An array of tool definitions. For image generation, this includes `image_generation`.
  - **type** (string) - Required - Must be `image_generation`.
  - **quality** (string) - Optional - The quality of the generated image ('standard' or 'high').
  - **input_image_mask** (object) - Optional - Specifies the mask for image editing.
    - **file_id** (string) - Required - The ID of the uploaded mask file.

### Request Example
```python
from openai import OpenAI
client = OpenAI()

fileId = create_file("sunlit_lounge.png")
maskId = create_file("mask.png")

response = client.responses.create(
    model="gpt-4o",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "generate an image of the same sunlit indoor lounge area with a pool but the pool should contain a flamingo",
                },
                {
                    "type": "input_image",
                    "file_id": fileId,
                }
            ],
        },
    ],
    tools=[
        {
            "type": "image_generation",
            "quality": "high",
            "input_image_mask": {
                "file_id": maskId,
            }
        },
    ],
)

image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if image_data:
    image_base64 = image_data[0]
    with open("lounge.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
```

### Response
#### Success Response (200)
- **id** (string) - The ID of the response.
- **model** (string) - The model used for the response.
- **output** (array) - An array of output objects.
  - **type** (string) - The type of output ('image_generation_call').
  - **result** (string) - The base64 encoded image data.

#### Response Example
```json
{
  "id": "resp_abc123",
  "model": "gpt-4o",
  "output": [
    {
      "type": "image_generation_call",
      "result": "...base64_encoded_image_data..."
    }
  ]
}
```
```

--------------------------------

### Analyze Image with File ID (Node.js)

Source: https://developers.openai.com/api/docs/guides/images-vision_api-mode=responses

This example demonstrates how to analyze an image in Node.js by first uploading the image using the Files API to get a file ID, and then referencing that file ID in the request.

```APIDOC
## POST /v1/responses

### Description
Analyzes the content of an image by referencing a file ID that was previously uploaded using the Files API.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for the response (e.g., "gpt-4.1-mini").
- **input** (array) - Required - An array of message objects.
  - **role** (string) - Required - The role of the message author ("user").
  - **content** (array) - Required - An array of content parts.
    - **type** (string) - Required - The type of content part ("input_text" or "input_image").
    - **text** (string) - Optional - The text content for "input_text" type.
    - **file_id** (string) - Optional - The ID of the file for "input_image" type.

### Request Example
```javascript
import OpenAI from "openai";
import fs from "fs";

const openai = new OpenAI();

// Function to create a file with the Files API
async function createFile(filePath) {
  const fileContent = fs.createReadStream(filePath);
  const result = await openai.files.create({
    file: fileContent,
    purpose: "vision",
  });
  return result.id;
}

// Getting the file ID
const fileId = await createFile("path_to_your_image.jpg");

const response = await openai.responses.create({
  model: "gpt-4.1-mini",
  input: [
    {
      role: "user",
      content: [
        { type: "input_text", text: "what's in this image?" },
        {
          type: "input_image",
          file_id: fileId,
        },
      ],
    },
  ],
});

console.log(response.output_text);
```

### Response
#### Success Response (200)
- **output_text** (string) - The analysis of the image content.
```

--------------------------------

### Python Example: Local Shell Request/Response Loop

Source: https://developers.openai.com/api/docs/guides/tools-local-shell

A minimal Python example demonstrating the request-response loop for the local shell tool. It includes setting up the OpenAI client and preparing for command execution. Note: Error handling and security checks are omitted for brevity and should be implemented in production.

```python
import os
import shlex
import subprocess
from openai import OpenAI

client = OpenAI()
```

--------------------------------

### Generate a Background Response (Python)

Source: https://developers.openai.com/api/docs/guides/webhooks

Example Python code using the OpenAI SDK to generate a background response.

```APIDOC
## Generate a Background Response (Python)

### Description
This Python code snippet demonstrates how to use the OpenAI SDK to request a background response. It initiates a long-running task and prints the initial status of the job.

### Method
POST

### Endpoint
`/v1/responses` (via SDK)

### Parameters
#### Request Body (via SDK)
- **model** (string) - Required - The model to use (e.g., `gpt-5.2`).
- **input** (string) - Required - The prompt for the model.
- **background** (boolean) - Required - Set to `true` for background processing.

### Request Example
```python
from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
  model="gpt-5.2",
  input="Write a very long novel about otters in space.",
  background=True,
)

print(resp.status)
```

### Response
#### Success Response
Prints the status of the background response job (e.g., 'processing').

#### Response Example
(Output will be the status string, e.g., 'processing')
```

--------------------------------

### Make First API Request (Python)

Source: https://developers.openai.com/api/docs/index

This Python code snippet illustrates how to use the OpenAI Python client to generate text. It covers client initialization and making a request to the `responses.create` endpoint with a specified model and input.

```python
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-5.2",
    input="Write a short bedtime story about a unicorn."
)

print(response.output_text)
```

--------------------------------

### Responses API - Image Generation with Mask - Python

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=abstract-orbit

This example uses the `responses.create` method with a tool for image generation, incorporating an input image and a mask for guided editing.

```APIDOC
## POST /v1/responses

### Description
This endpoint allows for complex interactions, including image generation guided by input images and masks, using specified tools.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for the response generation (e.g., "gpt-4o").
- **input** (array) - Required - An array of input objects, which can include text and images.
  - **role** (string) - Required - The role of the input (e.g., "user").
  - **content** (array) - Required - Content of the input.
    - **type** (string) - Required - Type of content (e.g., "input_text", "input_image").
    - **text** (string) - Required if type is "input_text" - The text content.
    - **file_id** (string) - Required if type is "input_image" - The ID of the uploaded image file.
- **tools** (array) - Required - An array of tools to use for the response.
  - **type** (string) - Required - The type of tool (e.g., "image_generation").
  - **quality** (string) - Optional - The quality of the generated image (e.g., "high").
  - **input_image_mask** (object) - Optional - Configuration for the input image mask.
    - **file_id** (string) - Required - The ID of the uploaded mask file.

### Request Example
```python
from openai import OpenAI
client = OpenAI()

fileId = create_file("sunlit_lounge.png")
maskId = create_file("mask.png")

response = client.responses.create(
    model="gpt-4o",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "generate an image of the same sunlit indoor lounge area with a pool but the pool should contain a flamingo",
                },
                {
                    "type": "input_image",
                    "file_id": fileId,
                }
            ],
        },
    ],
    tools=[
        {
            "type": "image_generation",
            "quality": "high",
            "input_image_mask": {
                "file_id": maskId,
            }
        },
    ],
)

image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if image_data:
    image_base64 = image_data[0]
    with open("lounge.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
```

### Response
#### Success Response (200)
- **output** (array) - An array of tool outputs.
  - **type** (string) - The type of output (e.g., "image_generation_call").
  - **result** (string) - The result of the tool execution (e.g., base64 encoded image data).

#### Response Example
```json
{
  "output": [
    {
      "type": "image_generation_call",
      "result": "...base64_encoded_image..."
    }
  ]
}
```
```

--------------------------------

### POST /responses/create (Image Generation with High Input Fidelity - Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=cafe-friends

This example demonstrates how to generate an image with high input fidelity using the `responses.create` endpoint in Python. It includes multiple input images and specifies `input_fidelity: "high"` to preserve details.

```APIDOC
## POST /responses/create

### Description
Generates an image with high input fidelity, preserving details from multiple input images.

### Method
POST

### Endpoint
/responses/create

### Parameters
#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for image generation (e.g., "gpt-4.1").
- **input** (list) - Required - A list of input objects, each containing a role and content. Content can include `input_text` and `input_image`.
  - **role** (string) - Required - The role of the input (e.g., "user").
  - **content** (list) - Required - A list of content objects.
    - **type** (string) - Required - The type of content (e.g., "input_text", "input_image").
    - **text** (string) - Required if type is "input_text" - The text prompt.
    - **image_url** (string) - Required if type is "input_image" - The URL of the input image.
- **tools** (list) - Required - A list of tool objects.
  - **type** (string) - Required - The type of tool (e.g., "image_generation").
  - **input_fidelity** (string) - Required - Set to "high" for high input fidelity.
  - **action** (string) - Required - The action to perform (e.g., "edit").

### Request Example
```python
{
    "model": "gpt-4.1",
    "input": [
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Add the logo to the woman's top, as if stamped into the fabric."},
                {
                    "type": "input_image",
                    "image_url": "https://cdn.openai.com/API/docs/images/woman_futuristic.jpg",
                },
                {
                    "type": "input_image",
                    "image_url": "https://cdn.openai.com/API/docs/images/brain_logo.png",
                },
            ],
        }
    ],
    "tools": [{"type": "image_generation", "input_fidelity": "high", "action": "edit"}],
}
```

### Response
#### Success Response (200)
- **output** (list) - A list of output objects. Contains `image_generation_call` type with `result` field holding the base64 encoded image.
  - **type** (string) - The type of output (e.g., "image_generation_call").
  - **result** (string) - Base64 encoded image data.

#### Response Example
```python
{
    "output": [
        {
            "type": "image_generation_call",
            "result": "<base64_encoded_image_data>"
        }
    ]
}
```
```

--------------------------------

### Create FastMCP Server with Search Tool

Source: https://developers.openai.com/api/docs/mcp

Defines and configures a FastMCP server named 'Sample MCP Server'. It includes a 'search' tool that utilizes the initialized OpenAI client to query a vector store. The tool returns a list of relevant document snippets based on the provided query.

```python
from fastmcp import FastMCP
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)
VECTOR_STORE_ID = "YOUR_VECTOR_STORE_ID" # Replace with your actual Vector Store ID

server_instructions = """
This MCP server provides search and document retrieval capabilities
for chat and deep research connectors. Use the search tool to find relevant documents
based on keywords, then use the fetch tool to retrieve complete
document content with citations.
"""


def create_server():
    """Create and configure the MCP server with search and fetch tools."""

    # Initialize the FastMCP server
    mcp = FastMCP(name="Sample MCP Server",
                  instructions=server_instructions)

    @mcp.tool()
    async def search(query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for documents using OpenAI Vector Store search.

        This tool searches through the vector store to find semantically relevant matches.
        Returns a list of search results with basic information. Use the fetch tool to get
        complete document content.

        Args:
            query: Search query string. Natural language queries work best for semantic search.

        Returns:
            Dictionary with 'results' key containing list of matching documents.
            Each result includes id, title, text snippet, and optional URL.
        """
        if not query or not query.strip():
            return {"results": []}

        if not openai_client:
            logger.error("OpenAI client not initialized - API key missing")
            raise ValueError(
                "OpenAI API key is required for vector store search")

        # Search the vector store using OpenAI API
        logger.info(f"Searching {VECTOR_STORE_ID} for query: '{query}'")

        response = openai_client.vector_stores.search(
            vector_store_id=VECTOR_STORE_ID, query=query)

        results = []

        # Process the vector store search results
        if hasattr(response, 'data') and response.data:
            for i, item in enumerate(response.data):
                # Extract file_id, filename, and content
                item_id = getattr(item, 'file_id', f"vs_{i}")
                item_filename = getattr(item, 'filename', f"Document {i+1}")

                # Extract text content from the content array
                content_list = getattr(item, 'content', [])
                text_content = ""
                if content_list and len(content_list) > 0:
                    # Get text from the first content item
                    first_content = content_list[0]
                    if hasattr(first_content, 'text'):
                        text_content = first_content.text
                    elif isinstance(first_content, dict):
                        text_content = first_content.get('text', '')

                if not text_content:
                    text_content = "No content available"

                # Create a snippet from content
                text_snippet = text_content[:200] + "..." if len(
                    text_content) > 200 else text_content

                result = {
                    "id": item_id,
                    "title": item_filename,
                    "text": text_snippet,
                    "url":
                    f"https://platform.openai.com/storage/files/{item_id}"
                }

                results.append(result)

        logger.info(f"Vector store search returned {len(results)} results")
        return {"results": results}

    @mcp.tool()
    async def fetch(id: str) -> Dict[str, Any]:
        """
        Retrieve complete document content by ID for detailed
        analysis and citation. This tool fetches the full document
        content from OpenAI Vector Store. Use this after finding
        relevant documents with the search tool to get complete
        information for analysis and proper citation.

        Args:
            id: File ID from vector store (file-xxx) or local document ID

        Returns:
            Complete document with id, title, full text content,
            optional URL, and metadata

        Raises:
            ValueError: If the specified ID is not found
        """
        if not id:
            raise ValueError("Document ID is required")

        if not openai_client:
            logger.error("OpenAI client not initialized - API key missing")
            raise ValueError(
                "OpenAI API key is required for vector store file retrieval")

        logger.info(f"Fetching content from vector store for file ID: {id}")

        # Fetch file content from vector store
        content_response = openai_client.vector_stores.files.content(
            vector_store_id=VECTOR_STORE_ID, file_id=id)

        # Get file metadata
        file_info = openai_client.vector_stores.files.retrieve(
            vector_store_id=VECTOR_STORE_ID, file_id=id)

        # Extract content from paginated response
        file_content = ""
        if hasattr(content_response, 'data') and content_response.data:
            # The content response might be paginated, iterate through pages if necessary
            # For simplicity, this example assumes the first page contains the full content
            # or concatenates content from all pages if available.
            for chunk in content_response.data:
                if hasattr(chunk, 'content'):
                    file_content += chunk.content
                elif isinstance(chunk, dict) and 'content' in chunk:
                    file_content += chunk.get('content', '')

        if not file_content:
            file_content = "No content available for this ID."

        # Construct the response dictionary
        document_data = {
            "id": id,
            "title": file_info.filename if file_info else "Unknown Title",
            "content": file_content,
            "url": f"https://platform.openai.com/storage/files/{id}",
            "metadata": file_info.metadata if file_info else {}
        }

        logger.info(f"Successfully fetched content for file ID: {id}")
        return document_data

    return mcp

# Example of how to create and run the server (assuming you have a way to run FastMCP)
# if __name__ == "__main__":
#     server = create_server()
#     # Add code here to run the server, e.g., using uvicorn or another ASGI server
#     print("MCP Server created with search and fetch tools.")

```

--------------------------------

### Generate a Background Response (JavaScript)

Source: https://developers.openai.com/api/docs/guides/webhooks

Example JavaScript code using the OpenAI SDK to generate a background response.

```APIDOC
## Generate a Background Response (JavaScript)

### Description
This JavaScript code snippet utilizes the OpenAI SDK to create a background response. It sends a request to the API to generate content asynchronously and logs the status of the background job.

### Method
POST

### Endpoint
`/v1/responses` (via SDK)

### Parameters
#### Request Body (via SDK)
- **model** (string) - Required - The model to use (e.g., `gpt-5.2`).
- **input** (string) - Required - The prompt for the model.
- **background** (boolean) - Required - Set to `true` for background processing.

### Request Example
```javascript
import OpenAI from "openai";
const client = new OpenAI();

const resp = await client.responses.create({
  model: "gpt-5.2",
  input: "Write a very long novel about otters in space.",
  background: true,
});

console.log(resp.status);
```

### Response
#### Success Response
Logs the status of the background response job (e.g., 'processing').

#### Response Example
(Output will be the status string, e.g., 'processing')
```

--------------------------------

### Install ChatKit React Bindings (Bash)

Source: https://developers.openai.com/api/docs/guides/chatkit

This command installs the ChatKit React bindings using npm. Ensure you have Node.js and npm installed in your project directory.

```bash
npm install @openai/chatkit-react
```

--------------------------------

### Make First API Request (JavaScript)

Source: https://developers.openai.com/api/docs/index

This JavaScript code snippet shows how to initialize the OpenAI client and make an API request for text generation. It uses the `openai` npm package and demonstrates how to specify the model and input prompt.

```javascript
import OpenAI from "openai";
const client = new OpenAI();

const response = await client.responses.create({
  model: "gpt-5.2",
  input: "Write a short bedtime story about a unicorn.",
});

console.log(response.output_text);
```

--------------------------------

### Setting up a Local Virtual Machine with Docker

Source: https://developers.openai.com/api/docs/guides/tools-computer-use

Instructions for setting up a local virtual machine using Docker for the Computer Use API.

```APIDOC
## Setting up a Local Virtual Machine with Docker

### Description
Set up a local virtual machine using Docker to execute computer use actions beyond a browser interface. This involves creating a Dockerfile, building an image, and running a container.

### Docker Installation
Install Docker from the [official website](https://www.docker.com/) and ensure it is running.

### Example Dockerfile

```dockerfile
# Dockerfile Example
FROM ubuntu:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    x11vnc \
    supervisor \
    # Add any other necessary dependencies for your environment
    && rm -rf /var/lib/apt/lists/*

# Configure VNC server (example)
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 5900

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
```

### Build Docker Image
Navigate to the directory containing your Dockerfile and run:

```bash
docker build -t cua-image .
```

### Run Docker Container
Start the Docker container with the following command:

```bash
docker run --rm -it --name cua-image -p 5900:5900 -e DISPLAY=:99 cua-image
```

**Note:** The `supervisord.conf` file needs to be created separately to configure the VNC server and other processes within the container.
```

--------------------------------

### Download Supporting Assets (CLI)

Source: https://developers.openai.com/api/docs/guides/video-generation_gallery=open&galleryItem=zebra-chase

Command-line examples for downloading specific assets like thumbnails and spritesheets using cURL.

```APIDOC
## GET /videos/{video_id}/content?variant={asset_type}

### Description
Download specific assets related to a completed video generation job using cURL.

### Method
GET

### Endpoint
/videos/{video_id}/content

### Parameters
#### Path Parameters
- **video_id** (string) - Required - The unique identifier of the completed video job.

#### Query Parameters
- **variant** (string) - Required - Specifies the type of asset to download. Options: 'video' (MP4), 'thumbnail' (webp), 'spritesheet' (jpg).

### Request Example (Download Thumbnail)
```bash
curl -L "https://api.openai.com/v1/videos/video_abc123/content?variant=thumbnail" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  --output thumbnail.webp
```

### Request Example (Download Spritesheet)
```bash
curl -L "https://api.openai.com/v1/videos/video_abc123/content?variant=spritesheet" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  --output spritesheet.jpg
```
```

--------------------------------

### POST /responses/create with High Input Fidelity (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=cafe-friends

This Python example demonstrates using the `responses.create` endpoint with high input fidelity. It shows how to pass text and image inputs and configure the image generation tool for editing.

```APIDOC
## POST /responses/create

### Description
Generates an edited image with high input fidelity using Python, preserving details from input images.

### Method
POST

### Endpoint
/responses/create

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation (e.g., "gpt-4.1").
- **input** (list) - Required - A list of message dictionaries, each containing role and content.
  - **role** (string) - Required - The role of the message sender (e.g., "user").
  - **content** (list) - Required - A list of content blocks.
    - **type** (string) - Required - The type of content (e.g., "input_text", "input_image").
    - **text** (string) - Required if type is "input_text" - The text content.
    - **image_url** (string) - Required if type is "input_image" - The URL of the input image.
- **tools** (list) - Required - A list of tool definitions.
  - **type** (string) - Required - The type of tool (e.g., "image_generation").
  - **input_fidelity** (string) - Required - Sets the input fidelity to "high" or "low".
  - **action** (string) - Required - The action to perform (e.g., "edit").

### Request Example
```python
{
    "model": "gpt-4.1",
    "input": [
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Add the logo to the woman's top, as if stamped into the fabric."},
                {
                    "type": "input_image",
                    "image_url": "https://cdn.openai.com/API/docs/images/woman_futuristic.jpg",
                },
                {
                    "type": "input_image",
                    "image_url": "https://cdn.openai.com/API/docs/images/brain_logo.png",
                },
            ],
        }
    ],
    "tools": [{"type": "image_generation", "input_fidelity": "high", "action": "edit"}],
}
```

### Response
#### Success Response (200)
- **output** (list) - A list of output dictionaries.
  - **type** (string) - The type of output (e.g., "image_generation_call").
  - **result** (string) - The base64 encoded image data.

#### Response Example
```python
{
  "output": [
    {
      "type": "image_generation_call",
      "result": "<base64_encoded_image_data>"
    }
  ]
}
```
```

--------------------------------

### Make First API Request (C#)

Source: https://developers.openai.com/api/docs/index

This C# code snippet demonstrates how to make an API request for text generation using the OpenAI SDK for .NET. It shows how to set up the API key, create an `OpenAIResponseClient`, and call the `CreateResponse` method.

```csharp
using OpenAI.Responses;

string apiKey = Environment.GetEnvironmentVariable("OPENAI_API_KEY")!;
var client = new OpenAIResponseClient(model: "gpt-5.2", apiKey: apiKey);

OpenAIResponse response = client.CreateResponse(
    "Write a short bedtime story about a unicorn."
);

Console.WriteLine(response.GetOutputText());
```

--------------------------------

### Edit Image with Mask (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=alien

This example demonstrates how to edit an image using a mask in Python. You provide an input image, a mask image, and a prompt to guide the editing process.

```APIDOC
## POST /v1/images/edits

### Description
Edits an image based on a provided mask and prompt.

### Method
POST

### Endpoint
/v1/images/edits

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for image editing (e.g., "gpt-image-1").
- **image** (file) - Required - The image to edit. Must be a PNG image, less than 4MB.
- **mask** (file) - Required - An additional image for the API to touch up. Must be a PNG image, less than 4MB. The transparent index in the mask file will be the area of the `image` that can be edited, though edge cases will be padded by 1 pixel in the alpha channel. Use the same dimensions as the `image`.
- **prompt** (string) - Required - A text description of the desired image modifications.
- **n** (integer) - Optional - The number of images to generate. Must be between 1 and 10.
- **size** (string) - Optional - The desired size of the generated images. Must be one of `256x256`, `512x512`, or `1024x1024`.
- **response_format** (string) - Optional - The format in which the generated images are returned. Must be one of `url` or `b64_json`.

### Request Example
```python
from openai import OpenAI
import base64

client = OpenAI()

result = client.images.edit(
    model="gpt-image-1",
    image=open("sunlit_lounge.png", "rb"),
    mask=open("mask.png", "rb"),
    prompt="A sunlit indoor lounge area with a pool containing a flamingo"
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("composition.png", "wb") as f:
    f.write(image_bytes)
```

### Response
#### Success Response (200)
- **created** (integer) - The Unix timestamp of when the image was created.
- **data** (array) - An array of image objects.
  - **b64_json** (string) - The generated image data as a base64 encoded string.
  - **url** (string) - The URL of the generated image.

#### Response Example
```json
{
  "created": 1678886400,
  "data": [
    {
      "url": "https://example.com/image.png",
      "b64_json": "...base64_encoded_image_data..."
    }
  ]
}
```
```

--------------------------------

### Remote MCP Server Integration

Source: https://developers.openai.com/api/docs/quickstart

Enables calling a remote MCP (Multi-Channel Protocol) server, such as for dice rolling in games. This example demonstrates integration with a Dungeons and Dragons MCP server. Supported in Bash, JavaScript, Python, and C#.

```bash
curl https://api.openai.com/v1/responses \ 
-H "Content-Type: application/json" \ 
-H "Authorization: Bearer $OPENAI_API_KEY" \ 
-d '{
  "model": "gpt-5",
    "tools": [
      {
        "type": "mcp",
        "server_label": "dmcp",
        "server_description": "A Dungeons and Dragons MCP server to assist with dice rolling.",
        "server_url": "https://dmcp-server.deno.dev/sse",
        "require_approval": "never"
      }
    ],
    "input": "Roll 2d4+1"
}'
```

```javascript
import OpenAI from "openai";
const client = new OpenAI();

const resp = await client.responses.create({
  model: "gpt-5",
  tools: [
    {
      type: "mcp",
      server_label: "dmcp",
      server_description: "A Dungeons and Dragons MCP server to assist with dice rolling.",
      server_url: "https://dmcp-server.deno.dev/sse",
      require_approval: "never",
    },
  ],
  input: "Roll 2d4+1",
});

console.log(resp.output_text);
```

```python
from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
    model="gpt-5",
    tools=[
        {
            "type": "mcp",
            "server_label": "dmcp",
            "server_description": "A Dungeons and Dragons MCP server to assist with dice rolling.",
            "server_url": "https://dmcp-server.deno.dev/sse",
            "require_approval": "never",
        },
    ],
    input="Roll 2d4+1",
)

print(resp.output_text)
```

```csharp
using OpenAI.Responses;

string key = Environment.GetEnvironmentVariable("OPENAI_API_KEY")!;
OpenAIResponseClient client = new(model: "gpt-5", apiKey: key);

ResponseCreationOptions options = new();
options.Tools.Add(ResponseTool.CreateMcpTool(
    serverLabel: "dmcp",
    serverUri: new Uri("https://dmcp-server.deno.dev/sse"),
    toolCallApprovalPolicy: new McpToolCallApprovalPolicy(GlobalMcpToolCallApprovalPolicy.NeverRequireApproval)
));

OpenAIResponse response = (OpenAIResponse)client.CreateResponse([
    ResponseItem.CreateUserMessageItem([
        ResponseContentPart.CreateInputTextPart("Roll 2d4+1")
    ])
], options);

Console.WriteLine(response.GetOutputText());
```

--------------------------------

### Python - Edit Image

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=lavender-sunrise

This example demonstrates how to edit an image using the OpenAI Python client library. You provide a base image, a mask image (optional), and a prompt to guide the edits.

```APIDOC
## POST /v1/images/edits

### Description
Edits an image by adding or removing elements from an existing image. You must provide a `model`, an `image`, and a `prompt`.

### Method
POST

### Endpoint
/v1/images/edits

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for image editing. Currently, only `gpt-image-1` is supported.
- **image** (file) - Required - The image to edit. Must be a PNG file, less than 2MB in size, and square.
- **prompt** (string) - Required - A text description of the desired image(s).
- **mask** (file) - Optional - An additional image for the API to edit into the source image. Must be the same dimensions as the `image` parameter, and must be a PNG file.
- **n** (integer) - Optional - The number of images to generate. Must be between 1 and 10.
- **size** (string) - Optional - The size of the generated images. Must be one of `256x256`, `512x512`, or `1024x1024`.
- **response_format** (string) - Optional - The format in which the generated images are returned. Must be one of `url` or `b64_json`.
- **temperature** (number) - Optional - The sampling temperature of the model. Higher values result in more creative outputs. Must be between 0 and 2.
- **user** (string) - Optional - A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse.

### Request Example
```python
import base64
from openai import OpenAI
client = OpenAI()

prompt = """
Generate a photorealistic image of a gift basket on a white background 
labeled 'Relax & Unwind' with a ribbon and handwriting-like font, 
containing all the items in the reference pictures.
"""

result = client.images.edit(
    model="gpt-image-1",
    image=[
        open("body-lotion.png", "rb"),
        open("bath-bomb.png", "rb"),
        open("incense-kit.png", "rb"),
        open("soap.png", "rb"),
    ],
    prompt=prompt
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("gift-basket.png", "wb") as f:
    f.write(image_bytes)
```

### Response
#### Success Response (200)
- **created** (integer) - The Unix timestamp of when the image was created.
- **data** (array) - An array of image objects.
  - **url** (string) - The URL of the generated image.
  - **b64_json** (string) - The base64 encoded JSON of the generated image.

#### Response Example
```json
{
  "created": 1589478378,
  "data": [
    {
      "url": "https://oaidalleapiprodscus.blob.core.windows.net/private/org-xxxxx/user-xxxxx/img-xxxxx.png?st=2023-05-15T14%3A30%3A00Z&se=2023-05-15T16%3A30%3A00Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaad505-4b65-4554-8287-91d733159821&sktid=a48cca56-e6da-484e-a824-31e01f454770&skt=2023-05-15T14%3A30%3A00Z&ske=2023-05-15T16%3A30%3A00Z&sks=b&skv=2021-08-06&sig=xxxxx%3D"
    }
  ]
}
```
```

--------------------------------

### Initialize OpenAI Client and Create Response (C#)

Source: https://developers.openai.com/api/docs/guides/tools-connectors-mcp

Initializes an OpenAI client with a specified model and API key, configures MCP tools for response creation, and generates a response based on user input. The output text from the response is then printed to the console.

```csharp
OpenAIResponseClient client = new(model: "gpt-5", apiKey: key);

ResponseCreationOptions options = new();
options.Tools.Add(ResponseTool.CreateMcpTool(
    serverLabel: "Dropbox",
    connectorId: McpToolConnectorId.Dropbox,
    authorizationToken: dropboxToken,
    toolCallApprovalPolicy: new McpToolCallApprovalPolicy(GlobalMcpToolCallApprovalPolicy.NeverRequireApproval)
));

OpenAIResponse response = (OpenAIResponse)client.CreateResponse([
    ResponseItem.CreateUserMessageItem([
        ResponseContentPart.CreateInputTextPart("Summarize the Q2 earnings report.")
    ])
], options);

Console.WriteLine(response.GetOutputText());
```

--------------------------------

### Customize ChatKit Composer and Start Screen Text

Source: https://developers.openai.com/api/docs/guides/chatkit-themes

Modify the placeholder text in the composer and the greeting message on the start screen. This helps guide user input and welcome them to the chat.

```jsx
const options: Partial<ChatKitOptions> = {
  composer: {
    placeholder: "Ask anything about your data…",
  },
  startScreen: {
    greeting: "Welcome to FeedbackBot!",
  },
};
```

--------------------------------

### Handling Incoming Webhook Request (Example)

Source: https://developers.openai.com/api/docs/guides/webhooks

This example demonstrates the structure of an incoming HTTP POST request from OpenAI when a subscribed event occurs. It includes essential headers like `webhook-id`, `webhook-timestamp`, and `webhook-signature`, along with the JSON payload containing event details. Your server endpoint should process this payload and respond with a 2xx status code.

```http
POST https://yourserver.com/webhook
user-agent: OpenAI/1.0 (+https://platform.openai.com/docs/webhooks)
content-type: application/json
webhook-id: wh_685342e6c53c8190a1be43f081506c52
webhook-timestamp: 1750287078
webhook-signature: v1,K5oZfzN95Z9UVu1EsfQmfVNQhnkZ2pj9o9NDN/H/pI4=
{
  "object": "event",
  "id": "evt_685343a1381c819085d44c354e1b330e",
  "type": "response.completed",
  "created_at": 1750287018,
  "data": { "id": "resp_abc123" }
}
```

--------------------------------

### Create Assistant with File Search

Source: https://developers.openai.com/api/docs/api-reference/assistants/createAssistant

This snippet shows how to create an assistant that can search through files using the `file_search` tool. It specifies the assistant's purpose, the `file_search` tool, and a vector store ID for retrieving relevant information. The example includes the HTTP request and the resulting JSON response.

```HTTP
curl https://api.openai.com/v1/assistants \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2" \
  -d '{
    "instructions": "You are an HR bot, and you have access to files to answer employee questions about company policies.",
    "tools": [{"type": "file_search"}],
    "tool_resources": {"file_search": {"vector_store_ids": ["vs_123"]}},
    "model": "gpt-4o"
  }'
```

```JSON
{
  "id": "asst_abc123",
  "object": "assistant",
  "created_at": 1699009403,
  "name": "HR Helper",
  "description": null,
  "model": "gpt-4o",
  "instructions": "You are an HR bot, and you have access to files to answer employee questions about company policies.",
  "tools": [
    {
      "type": "file_search"
    }
  ],
  "tool_resources": {
    "file_search": {
      "vector_store_ids": ["vs_123"]
    }
  },
  "metadata": {},
  "top_p": 1.0,
  "temperature": 1.0,
  "response_format": "auto"
}
```

--------------------------------

### POST /responses/create (Image Generation with High Input Fidelity - Node.js)

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=cafe-friends

This example demonstrates how to generate an image with high input fidelity using the `responses.create` endpoint in Node.js. It includes multiple input images and specifies `input_fidelity: "high"` to preserve details.

```APIDOC
## POST /responses/create

### Description
Generates an image with high input fidelity, preserving details from multiple input images.

### Method
POST

### Endpoint
/responses/create

### Parameters
#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for image generation (e.g., "gpt-4.1").
- **input** (array) - Required - An array of input objects, each containing a role and content. Content can include `input_text` and `input_image`.
  - **role** (string) - Required - The role of the input (e.g., "user").
  - **content** (array) - Required - An array of content objects.
    - **type** (string) - Required - The type of content (e.g., "input_text", "input_image").
    - **text** (string) - Required if type is "input_text" - The text prompt.
    - **image_url** (string) - Required if type is "input_image" - The URL of the input image.
- **tools** (array) - Required - An array of tool objects.
  - **type** (string) - Required - The type of tool (e.g., "image_generation").
  - **input_fidelity** (string) - Required - Set to "high" for high input fidelity.
  - **action** (string) - Required - The action to perform (e.g., "edit").

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": [
    {
      "role": "user",
      "content": [
        { "type": "input_text", "text": "Add the logo to the woman's top, as if stamped into the fabric." },
        { "type": "input_image", "image_url": "https://cdn.openai.com/API/docs/images/woman_futuristic.jpg" },
        { "type": "input_image", "image_url": "https://cdn.openai.com/API/docs/images/brain_logo.png" }
      ]
    }
  ],
  "tools": [{ "type": "image_generation", "input_fidelity": "high", "action": "edit" }]
}
```

### Response
#### Success Response (200)
- **output** (array) - An array of output objects. Contains `image_generation_call` type with `result` field holding the base64 encoded image.
  - **type** (string) - The type of output (e.g., "image_generation_call").
  - **result** (string) - Base64 encoded image data.

#### Response Example
```json
{
  "output": [
    {
      "type": "image_generation_call",
      "result": "<base64_encoded_image_data>"
    }
  ]
}
```
```

--------------------------------

### Analyze Image with Base64 Encoding (Python)

Source: https://developers.openai.com/api/docs/guides/images-vision_api-mode=responses

This example shows how to analyze an image by encoding it into a Base64 string and sending it directly within the API request.

```APIDOC
## POST /v1/responses

### Description
Analyzes the content of an image by sending its Base64 encoded string as part of the user's input.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for the response (e.g., "gpt-4.1").
- **input** (array) - Required - An array of message objects.
  - **role** (string) - Required - The role of the message author ("user").
  - **content** (array) - Required - An array of content parts.
    - **type** (string) - Required - The type of content part ("input_text" or "input_image").
    - **text** (string) - Optional - The text content for "input_text" type.
    - **image_url** (object) - Optional - The image URL for "input_image" type.
      - **url** (string) - Required - The URL of the image.
      - **detail** (string) - Optional - The detail level of the image analysis.

### Request Example
```python
from openai import OpenAI
import base64

client = OpenAI()

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Path to your image
image_path = "path_to_your_image.jpg"

# Getting the Base64 string
base64_image = encode_image(image_path)

response = client.responses.create(
    model="gpt-4.1",
    input=[
        {
            "role": "user",
            "content": [
                { "type": "input_text", "text": "what's in this image?" },
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        }
    ],
)

print(response.output_text)
```

### Response
#### Success Response (200)
- **output_text** (string) - The analysis of the image content.
```

--------------------------------

### Webhook Server Implementation (JavaScript)

Source: https://developers.openai.com/api/docs/guides/webhooks

Example Node.js Express server code to receive and process 'response.completed' webhook events from OpenAI, including signature verification.

```APIDOC
## Webhook Server (JavaScript)

### Description
This Node.js Express application provides an example of a server-side webhook handler for OpenAI. It listens for POST requests on the `/webhook` endpoint, verifies the incoming webhook signature, and processes the `response.completed` event.

### Method
POST

### Endpoint
`/webhook`

### Parameters
#### Query Parameters
None

#### Request Body
Expects a JSON payload representing the webhook event.

### Request Example
(The request body is processed internally for signature verification.)

### Response
#### Success Response (200)
Indicates successful processing of the webhook.

#### Error Response (400)
Sent when the webhook signature is invalid.

#### Response Example
(Success: HTTP 200 OK)
(Error: HTTP 400 Bad Request with 'Invalid signature' message)

### Code Example
```javascript
import OpenAI from "openai";
import express from "express";

const app = express();
const client = new OpenAI({ webhookSecret: process.env.OPENAI_WEBHOOK_SECRET });

// Don't use express.json() because signature verification needs the raw text body
app.use(express.text({ type: "application/json" }));

app.post("/webhook", async (req, res) => {
  try {
    const event = await client.webhooks.unwrap(req.body, req.headers);

    if (event.type === "response.completed") {
      const response_id = event.data.id;
      const response = await client.responses.retrieve(response_id);
      const output_text = response.output
        .filter((item) => item.type === "message")
        .flatMap((item) => item.content)
        .filter((contentItem) => contentItem.type === "output_text")
        .map((contentItem) => contentItem.text)
        .join("");

      console.log("Response output:", output_text);
    }
    res.status(200).send();
  } catch (error) {
    if (error instanceof OpenAI.InvalidWebhookSignatureError) {
      console.error("Invalid signature", error);
      res.status(400).send("Invalid signature");
    } else {
      throw error;
    }
  }
});

app.listen(8000, () => {
  console.log("Webhook server is running on port 8000");
});
```
```

--------------------------------

### Create Dockerfile for Virtual Machine

Source: https://developers.openai.com/api/docs/guides/tools-computer-use

An example Dockerfile used to define the configuration of a virtual machine for the Computer Use tool. This specific example sets up an Ubuntu virtual machine with a VNC server, enabling remote access and interaction.

```dockerfile
FROM ubuntu:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    x11vnc \
    supervisor \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]

EXPOSE 5900
```

--------------------------------

### Image Generation with Mask - Node.js

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=neon

This example demonstrates using the `responses.create` method for image generation with a mask in Node.js. This approach allows for more complex interactions where the mask guides the generation process within a broader conversational context.

```APIDOC
## POST /v1/responses

### Description
Generates an image based on a text prompt and an input image, using a mask to specify areas for editing. This method is part of a broader conversational API.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for generation. e.g., "gpt-4o"
- **input** (array) - Required - An array of message objects representing the conversation history and input.
  - **role** (string) - Required - The role of the message author ('user' or 'assistant').
  - **content** (array) - Required - An array of content blocks.
    - **type** (string) - Required - The type of content ('input_text' or 'input_image').
    - **text** (string) - Required if type is 'input_text' - The text content.
    - **file_id** (string) - Required if type is 'input_image' - The ID of the uploaded image file.
- **tools** (array) - Required - An array of tool definitions. For image generation, this includes `image_generation`.
  - **type** (string) - Required - Must be `image_generation`.
  - **quality** (string) - Optional - The quality of the generated image ('standard' or 'high').
  - **input_image_mask** (object) - Optional - Specifies the mask for image editing.
    - **file_id** (string) - Required - The ID of the uploaded mask file.

### Request Example
```javascript
import OpenAI from "openai";
const openai = new OpenAI();

const fileId = await createFile("sunlit_lounge.png");
const maskId = await createFile("mask.png");

const response = await openai.responses.create({
  model: "gpt-4o",
  input: [
    {
      role: "user",
      content: [
        {
          type: "input_text",
          text: "generate an image of the same sunlit indoor lounge area with a pool but the pool should contain a flamingo",
        },
        {
          type: "input_image",
          file_id: fileId,
        }
      ],
    },
  ],
  tools: [
    {
      type: "image_generation",
      quality: "high",
      input_image_mask: {
        file_id: maskId,
      }
    },
  ],
});

const imageData = response.output
  .filter((output) => output.type === "image_generation_call")
  .map((output) => output.result);

if (imageData.length > 0) {
  const imageBase64 = imageData[0];
  const fs = await import("fs");
  fs.writeFileSync("lounge.png", Buffer.from(imageBase64, "base64"));
}
```

### Response
#### Success Response (200)
- **id** (string) - The ID of the response.
- **model** (string) - The model used for the response.
- **output** (array) - An array of output objects.
  - **type** (string) - The type of output ('image_generation_call').
  - **result** (string) - The base64 encoded image data.

#### Response Example
```json
{
  "id": "resp_abc123",
  "model": "gpt-4o",
  "output": [
    {
      "type": "image_generation_call",
      "result": "...base64_encoded_image_data..."
    }
  ]
}
```
```

--------------------------------

### Generate a Background Response (cURL)

Source: https://developers.openai.com/api/docs/guides/webhooks

Example cURL command to trigger a background response generation using the OpenAI API.

```APIDOC
## Generate a Background Response (cURL)

### Description
This command demonstrates how to initiate a background response generation task using the OpenAI API. This is useful for long-running tasks where you don't need an immediate response and can be notified via webhooks upon completion.

### Method
POST

### Endpoint
`/v1/responses`

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for generating the response (e.g., `gpt-5.2`).
- **input** (string) - Required - The prompt or input for the model.
- **background** (boolean) - Required - Set to `true` to enable background mode.

### Request Example
```bash
curl https://api.openai.com/v1/responses \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $OPENAI_API_KEY" \
-d '{
  "model": "gpt-5.2",
  "input": "Write a very long novel about otters in space.",
  "background": true
}'
```

### Response
#### Success Response (200)
Returns a status indicating the background job has been initiated.

#### Response Example
```json
{
  "id": "resp_abc123",
  "object": "response",
  "created": 1678886400,
  "model": "gpt-5.2",
  "status": "processing",
  "error": null
}
```
```

--------------------------------

### Run Object Example

Source: https://developers.openai.com/api/docs/assistants/migration

Example JSON structure for a Run object in the Assistants API.

```APIDOC
## Run Object Example

### Description
This is an example of the JSON response for a run object when using the Assistants API.

### Method
GET (Implied)

### Endpoint
/assistants/runs/{run_id}

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the run.
- **assistant_id** (string) - The ID of the assistant used for the run.
- **cancelled_at** (null) - Timestamp when the run was cancelled.
- **completed_at** (integer) - Timestamp when the run was completed.
- **created_at** (integer) - Timestamp when the run was created.
- **expires_at** (null) - Timestamp when the run expires.
- **failed_at** (null) - Timestamp when the run failed.
- **incomplete_details** (null) - Details about incomplete runs.
- **instructions** (null) - Instructions provided for the run.
- **last_error** (null) - Information about the last error encountered.
- **max_completion_tokens** (null) - Maximum completion tokens allowed.
- **max_prompt_tokens** (null) - Maximum prompt tokens allowed.
- **metadata** (object) - Key-value pairs for storing additional data.
- **model** (string) - The model used for the run.
- **object** (string) - The type of object, 'thread.run'.
- **parallel_tool_calls** (boolean) - Whether parallel tool calls are enabled.
- **required_action** (null) - Details about any required actions.
- **response_format** (string) - The response format, 'auto'.
- **started_at** (integer) - Timestamp when the run started.
- **status** (string) - The current status of the run (e.g., 'completed').
- **thread_id** (string) - The ID of the thread associated with the run.
- **tool_choice** (string) - The tool choice, 'auto'.
- **tools** (array) - List of tools used in the run.
- **truncation_strategy** (object) - Strategy for truncating content.
- **usage** (object) - Token usage details for the run.
- **temperature** (float) - The sampling temperature.
- **top_p** (float) - The nucleus sampling parameter.
- **tool_resources** (object) - Resources used by tools.
- **reasoning_effort** (null) - Effort level for reasoning.

#### Response Example
```json
{
  "id": "run_FKIpcs5ECSwuCmehBqsqkORj",
  "assistant_id": "asst_8fVY45hU3IM6creFkVi5MBKB",
  "cancelled_at": null,
  "completed_at": 1752857327,
  "created_at": 1752857322,
  "expires_at": null,
  "failed_at": null,
  "incomplete_details": null,
  "instructions": null,
  "last_error": null,
  "max_completion_tokens": null,
  "max_prompt_tokens": null,
  "metadata": {},
  "model": "gpt-4.1",
  "object": "thread.run",
  "parallel_tool_calls": true,
  "required_action": null,
  "response_format": "auto",
  "started_at": 1752857324,
  "status": "completed",
  "thread_id": "thread_CrXtCzcyEQbkAcXuNmVSKFs1",
  "tool_choice": "auto",
  "tools": [],
  "truncation_strategy": {
    "type": "auto",
    "last_messages": null
  },
  "usage": {
    "completion_tokens": 130,
    "prompt_tokens": 34,
    "total_tokens": 164,
    "prompt_token_details": {
      "cached_tokens": 0
    },
    "completion_tokens_details": {
      "reasoning_tokens": 0
    }
  },
  "temperature": 1.0,
  "top_p": 1.0,
  "tool_resources": {},
  "reasoning_effort": null
}
```
```

--------------------------------

### Edit an image using a mask (inpainting) - Python

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=construction-crew

This example demonstrates how to edit an image by providing a mask to indicate which part of the image should be edited. Additional instructions are sent to the model to guide the editing process.

```APIDOC
## POST /v1/images/edits

### Description
Edit an image using a mask to indicate which part of the image should be edited. The model uses the mask as guidance, but may not follow its exact shape with complete precision. If multiple input images are provided, the mask will be applied to the first image.

### Method
POST

### Endpoint
/v1/images/edits

### Parameters
#### Form Data
- **model** (string) - Required - The model to use for image editing. e.g., "gpt-image-1"
- **prompt** (string) - Required - A description of the desired image.
- **image** (file) - Required - The image to edit. Must be a PNG image, less than 4MB in size, and square.
- **mask** (file) - Required - A PNG image, less than 4MB in size, and square. The transparent areas of the mask indicate where the image should be edited. 

### Request Example
```python
from openai import OpenAI
client = OpenAI()

result = client.images.edit(
    model="gpt-image-1",
    image=open("sunlit_lounge.png", "rb"),
    mask=open("mask.png", "rb"),
    prompt="A sunlit indoor lounge area with a pool containing a flamingo"
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("composition.png", "wb") as f:
    f.write(image_bytes)
```

### Response
#### Success Response (200)
- **data** (array) - Contains the edited image data.
  - **b64_json** (string) - The edited image in base64 encoded JSON format.

#### Response Example
```json
{
  "created": 1589478378,
  "data": [
    {
      "b64_json": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    }
  ]
}
```
```

--------------------------------

### POST /v1/responses

Source: https://developers.openai.com/api/docs/index

This endpoint allows you to send a prompt to a specified model and receive a text-based response. It's the primary method for generating text content.

```APIDOC
## POST /v1/responses

### Description
This endpoint allows you to send a prompt to a specified model and receive a text-based response. It's the primary method for generating text content.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The ID of the model to use for generating the response (e.g., "gpt-5.2").
- **input** (string) - Required - The prompt that will be sent to the model.

### Request Example
```json
{
  "model": "gpt-5.2",
  "input": "Write a short bedtime story about a unicorn."
}
```

### Response
#### Success Response (200)
- **output_text** (string) - The generated text response from the model.

#### Response Example
```json
{
  "output_text": "Once upon a time, in a land filled with sparkling rivers and candy-floss clouds, lived a unicorn named Sparklehoof..."
}
```
```

--------------------------------

### File Search Tool

Source: https://developers.openai.com/api/docs/quickstart

This endpoint allows the model to search through your files. You need to provide a list of vector store IDs to specify which files to search.

```APIDOC
## POST /v1/responses

### Description
Enables the model to search through specified files using vector stores.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for the response.
- **input** (string) - Required - The user's input query.
- **tools** (array) - Required - A list of tools to attach. For file search, this should include:
  - **type** (string) - Must be "file_search".
  - **vector_store_ids** (array of strings) - Required - The IDs of the vector stores to search within.

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": "What is deep research by OpenAI?",
  "tools": [
    {
      "type": "file_search",
      "vector_store_ids": ["<vector_store_id>"]
    }
  ]
}
```

### Response
#### Success Response (200)
- **output_text** (string) - The model's response based on file search results.

#### Response Example
```json
{
  "output_text": "Deep research by OpenAI refers to..."
}
```
```

--------------------------------

### GPT-5.1-Codex-Max Code Generation

Source: https://developers.openai.com/api/docs/guides/code-generation

This section details how to use the GPT-5.1-Codex-Max model for code generation tasks, including examples for JavaScript, Python, and cURL.

```APIDOC
## POST /v1/responses

### Description
This endpoint allows you to generate code or receive code-related assistance using the GPT-5.1-Codex-Max model. It's suitable for high-reasoning tasks.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use for code generation (e.g., "gpt-5.1-codex-max").
- **input** (string) - Required - The prompt or code snippet to process.
- **reasoning** (object) - Optional - Specifies the reasoning effort for the task.
  - **effort** (string) - Required - The level of effort for reasoning (e.g., "high").

### Request Example
```json
{
  "model": "gpt-5.1-codex-max",
  "input": "Find the null pointer exception: ...your code here...",
  "reasoning": { "effort": "high" }
}
```

### Response
#### Success Response (200)
- **output_text** (string) - The generated code or the result of the code-related task.

#### Response Example
```json
{
  "output_text": "// Your generated code or analysis here..."
}
```

### Error Handling
- **400 Bad Request**: Invalid request parameters.
- **401 Unauthorized**: Invalid API key.
- **404 Not Found**: Model not found.
- **500 Internal Server Error**: Server-side issue.
```

--------------------------------

### Analyze Image from Stream/Byte Array (C#)

Source: https://developers.openai.com/api/docs/guides/images-vision_api-mode=responses

This example demonstrates how to analyze an image in C# by downloading it as a stream or byte array and sending it directly within the API request.

```APIDOC
## POST /v1/responses

### Description
Analyzes the content of an image by sending its data as a stream or byte array as part of the user's input.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for the response (e.g., "gpt-5").
- **input** (array) - Required - An array of message objects.
  - **role** (string) - Required - The role of the message author ("user").
  - **content** (array) - Required - An array of content parts.
    - **type** (string) - Required - The type of content part ("input_text" or "input_image").
    - **text** (string) - Optional - The text content for "input_text" type.
    - **image_url** (object) - Optional - The image URL for "input_image" type.
      - **url** (string) - Required - The URL of the image.
      - **detail** (string) - Optional - The detail level of the image analysis.

### Request Example
```csharp
using OpenAI.Responses;
using System;
using System.Net.Http;
using System.Threading.Tasks;

string key = Environment.GetEnvironmentVariable("OPENAI_API_KEY")!;
OpenAIResponseClient client = new(model: "gpt-5", apiKey: key);

Uri imageUrl = new("https://openai-documentation.vercel.app/images/cat_and_otter.png");
using HttpClient http = new();

// Download an image as stream
using var stream = await http.GetStreamAsync(imageUrl);

OpenAIResponse response1 = (OpenAIResponse)client.CreateResponse([
    ResponseItem.CreateUserMessageItem([
        ResponseContentPart.CreateInputTextPart("What is in this image?"),
        ResponseContentPart.CreateInputImagePart(BinaryData.FromStream(stream), "image/png")
    ])
]);

Console.WriteLine($"From image stream: {response1.GetOutputText()}");

// Download an image as byte array
byte[] bytes = await http.GetByteArrayAsync(imageUrl);

OpenAIResponse response2 = (OpenAIResponse)client.CreateResponse([
    ResponseItem.CreateUserMessageItem([
        ResponseContentPart.CreateInputTextPart("What is in this image?"),
        ResponseContentPart.CreateInputImagePart(BinaryData.FromBytes(bytes), "image/png")
    ])
]);

Console.WriteLine($"From byte array: {response2.GetOutputText()}");
```

### Response
#### Success Response (200)
- **output_text** (string) - The analysis of the image content.
```

--------------------------------

### Prompt Structure Example (Markdown)

Source: https://developers.openai.com/api/docs/guides/realtime-models-prompting

Illustrates a structured format for system prompts using Markdown. This organization helps the model understand context and maintain consistency by using clear, labeled sections for different aspects of the interaction.

```markdown
# Role & Objective — who you are and what “success” means

# Personality & Tone — the voice and style to maintain

# Context — retrieved context, relevant info

# Reference Pronunciations — phonetic guides for tricky words

# Tools — names, usage rules, and preambles

# Instructions / Rules — do’s, don’ts, and approach

# Conversation Flow — states, goals, and transitions

# Safety & Escalation — fallback and handoff logic
```

--------------------------------

### Tool Choice Configuration (JSON)

Source: https://developers.openai.com/api/docs/guides/function-calling_api-mode=chat

Example JSON configuration for 'tool_choice' parameter, demonstrating 'allowed_tools' mode with specific function definitions. This restricts the model's tool usage.

```json
"tool_choice": {
    "type": "allowed_tools",
    "mode": "auto",
    "tools": [
        { "type": "function", "name": "get_weather" },
        { "type": "function", "name": "search_docs" }
    ]
  }
}
```

--------------------------------

### Image Generation with Mask - Python

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=animation

This example demonstrates using the `responses.create` method with image generation and a mask. It allows for more complex interactions where text, images, and masks are combined.

```APIDOC
## POST /v1/responses/create

### Description
Generates content using a multimodal model, supporting text, images, and tools like image generation with masks.

### Method
POST

### Endpoint
/v1/responses/create

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The multimodal model to use. Example: `gpt-4o`
- **input** (array) - Required - An array of input messages, each with a role and content.
  - **role** (string) - Required - The role of the message sender (`user` or `assistant`).
  - **content** (array) - Required - An array of content blocks, which can be text or images.
    - **type** (string) - Required - The type of content (`input_text` or `input_image`).
    - **text** (string) - Required if type is `input_text` - The text content.
    - **file_id** (string) - Required if type is `input_image` - The ID of the uploaded image file.
- **tools** (array) - Optional - A list of tools to use for the response.
  - **type** (string) - Required - The type of tool (`image_generation`).
  - **quality** (string) - Optional - The quality of the generated image (`standard` or `high`).
  - **input_image_mask** (object) - Optional - Configuration for the image mask.
    - **file_id** (string) - Required - The ID of the uploaded mask file.

### Request Example
```python
from openai import OpenAI
client = OpenAI()

fileId = create_file("sunlit_lounge.png")
maskId = create_file("mask.png")

response = client.responses.create(
    model="gpt-4o",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "generate an image of the same sunlit indoor lounge area with a pool but the pool should contain a flamingo",
                },
                {
                    "type": "input_image",
                    "file_id": fileId,
                }
            ],
        },
    ],
    tools=[
        {
            "type": "image_generation",
            "quality": "high",
            "input_image_mask": {
                "file_id": maskId,
            }
        },
    ],
)

image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if image_data:
    image_base64 = image_data[0]
    with open("lounge.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
```

### Response
#### Success Response (200)
- **output** (array) - An array of tool outputs.
  - **type** (string) - The type of output (`image_generation_call`).
  - **result** (string) - The base64 encoded image data.

#### Response Example
```json
{
  "output": [
    {
      "type": "image_generation_call",
      "result": "/9j/4AAQSkZJRgABAQEASABIAAD..."
    }
  ]
}
```
```

--------------------------------

### Image Generation with Transparent Background (CLI)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=alien-rock

This example shows how to generate an image with a transparent background using `curl` and `jq` for command-line interaction with the OpenAI API.

```APIDOC
## POST /v1/images (CLI Example)

### Description
Generates an image with a transparent background using `curl` and `jq` for command-line execution.

### Method
POST

### Endpoint
/v1/images

### Parameters
#### Request Body (JSON Payload)
- **prompt** (string) - Required - Text description of the image.
- **quality** (string) - Optional - "standard" or "high". "high" recommended for transparency.
- **size** (string) - Optional - Image dimensions (e.g., "1024x1024").
- **background** (string) - Optional - Set to "transparent" for transparent backgrounds.

### Request Example
```bash
curl -X POST "https://api.openai.com/v1/images" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-type: application/json" \
    -d '{ 
        "prompt": "Draw a 2D pixel art style sprite sheet of a tabby gray cat", 
        "quality": "high", 
        "size": "1024x1024", 
        "background": "transparent" 
    }' | jq -r '.data[0].b64_json' | base64 --decode > sprite.png
```

### Response
#### Success Response (200)
- The command line example pipes the `b64_json` output directly to `base64 --decode` and saves it to `sprite.png`.
```

--------------------------------

### Webhook Server Implementation (Python)

Source: https://developers.openai.com/api/docs/guides/webhooks

Example Python Flask server code to receive and process 'response.completed' webhook events from OpenAI, including signature verification.

```APIDOC
## Webhook Server (Python)

### Description
This Python Flask application demonstrates how to set up an HTTP endpoint to receive and process webhook events from OpenAI. It specifically handles the `response.completed` event and verifies the signature of incoming requests to ensure authenticity.

### Method
POST

### Endpoint
`/webhook`

### Parameters
#### Query Parameters
None

#### Request Body
This endpoint expects a JSON payload containing the webhook event data.

### Request Example
(The request body is handled internally by the webhook signature verification process)

### Response
#### Success Response (200)
Returns a 200 OK status if the webhook is successfully processed.

#### Error Response (400)
Returns a 400 Bad Request status if the webhook signature is invalid.

#### Response Example
(Success: HTTP 200 OK)
(Error: HTTP 400 Bad Request with 'Invalid signature' message)

### Code Example
```python
import os
from openai import OpenAI, InvalidWebhookSignatureError
from flask import Flask, request, Response

app = Flask(__name__)
client = OpenAI(webhook_secret=os.environ["OPENAI_WEBHOOK_SECRET"])

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # with webhook_secret set above, unwrap will raise an error if the signature is invalid
        event = client.webhooks.unwrap(request.data, request.headers)

        if event.type == "response.completed":
            response_id = event.data.id
            response = client.responses.retrieve(response_id)
            print("Response output:", response.output_text)

        return Response(status=200)
    except InvalidWebhookSignatureError as e:
        print("Invalid signature", e)
        return Response("Invalid signature", status=400)

if __name__ == "__main__":
    app.run(port=8000)
```
```

--------------------------------

### Install ChatKit Server Package

Source: https://developers.openai.com/api/docs/guides/custom-chatkit

Installs the necessary Python package for running the ChatKit server. This is the first step in setting up a self-hosted ChatKit environment.

```bash
pip install openai-chatkit
```

--------------------------------

### Analyze Image with File ID (Python)

Source: https://developers.openai.com/api/docs/guides/images-vision_api-mode=responses

This Python example shows how to analyze an image by uploading it using the Files API to obtain a file ID, which is then used in the request.

```APIDOC
## POST /v1/responses

### Description
Analyzes the content of an image by referencing a file ID that was previously uploaded using the Files API.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for the response (e.g., "gpt-4.1-mini").
- **input** (array) - Required - An array of message objects.
  - **role** (string) - Required - The role of the message author ("user").
  - **content** (array) - Required - An array of content parts.
    - **type** (string) - Required - The type of content part ("input_text" or "input_image").
    - **text** (string) - Optional - The text content for "input_text" type.
    - **file_id** (string) - Optional - The ID of the file for "input_image" type.

### Request Example
```python
from openai import OpenAI

client = OpenAI()

# Function to create a file with the Files API
def create_file(file_path):
  with open(file_path, "rb") as file_content:
    result = client.files.create(
        file=file_content,
        purpose="vision",
    )
    return result.id

# Getting the file ID
file_id = create_file("path_to_your_image.jpg")

response = client.responses.create(
    model="gpt-4.1-mini",
    input=[{
        "role": "user",
        "content": [
            {"type": "input_text", "text": "what's in this image?"},
            {
                "type": "input_image",
                "file_id": file_id,
            },
        ],
    }],
)

print(response.output_text)
```

### Response
#### Success Response (200)
- **output_text** (string) - The analysis of the image content.
```

--------------------------------

### JavaScript Tool Calling Example

Source: https://developers.openai.com/api/docs/guides/function-calling_api-mode=chat

This example demonstrates how to use the OpenAI API with JavaScript to enable tool calling. It mirrors the Python example by defining a 'get_horoscope' tool, making an initial call to the model, processing the tool call, and then making a subsequent call with the tool's results.

```APIDOC
## POST /v1/chat/completions (Tool Calling - JavaScript)

### Description
This JavaScript example shows how to implement tool calling with the OpenAI API. It covers defining tools, sending them to the model, handling the model's decision to use a tool, executing the tool's logic, and feeding the results back to the model for a final answer.

### Method
POST

### Endpoint
/v1/chat/completions

### Parameters
Refer to the Python example for detailed parameter descriptions.

### Request Example
```javascript
import OpenAI from "openai";

const openai = new OpenAI();

// 1. Define a list of callable tools for the model
const tools = [
  {
    type: "function",
    function: {
      name: "get_horoscope",
      description: "Get today's horoscope for an astrological sign.",
      parameters: {
        type: "object",
        properties: {
          sign: {
            type: "string",
            description: "An astrological sign like Taurus or Aquarius",
          },
        },
        required: ["sign"],
      },
      strict: true,
    },
  },
];

function getHoroscope(sign) {
  return `${sign}: Next Tuesday you will befriend a baby otter.`;
}

const messages = [
  { role: "user", content: "What is my horoscope? I am an Aquarius." },
];

// 2. Prompt the model with tools defined
let response = await openai.chat.completions.create({
  model: "gpt-4.1",
  messages,
  tools,
});

messages.push(response.choices[0].message);

for (const toolCall of response.choices[0].message.tool_calls ?? []) {
  if (toolCall.function.name === "get_horoscope") {
    // 3. Execute the function logic for get_horoscope
    const args = JSON.parse(toolCall.function.arguments);
    const horoscope = getHoroscope(args.sign);

    // 4. Provide function call results to the model
    messages.push({
      role: "tool",
      tool_call_id: toolCall.id,
      content: JSON.stringify({ horoscope }),
    });
  }
}

response = await openai.chat.completions.create({
  model: "gpt-4.1",
  messages,
  tools,
});

// 5. The model should be able to give a response!
console.log(response.choices[0].message.content);
```

### Response
Refer to the Python example for detailed response descriptions.
```

--------------------------------

### Create Fine-Tuning Job with API (Bash)

Source: https://developers.openai.com/api/docs/guides/reinforcement-fine-tuning

This snippet demonstrates how to initiate a fine-tuning job using the OpenAI API via a `curl` command. It requires authentication with an API key and specifies training and validation files, the model to be fine-tuned, and a reinforcement learning method with a multi-grader configuration for evaluation.

```bash
curl https://api.openai.com/v1/fine_tuning/jobs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
  "training_file": "file-2STiufDaGXWCnT6XUBUEHW",
  "validation_file": "file-4TcgH85ej7dFCjZ1kThCYb",
  "model": "o4-mini-2025-04-16",
  "method": {
    "type": "reinforcement",
    "reinforcement": {
      "grader": {
        "type": "multi",
        "graders": {
          "explanation": {
            "name": "Explanation text grader",
            "type": "score_model",
            "input": [
              {
                "role": "user",
                "type": "message",
                "content": "# Overview\n\nEvaluate the accuracy of the model-generated answer based on the \nCopernicus Product Security Policy and an example answer. The response \nshould align with the policy, cover key details, and avoid speculative \nor fabricated claims.\n\nAlways respond with a single floating point number 0 through 1,\nusing the grading criteria below.\n\n## Grading Criteria:\n- **1.0**: The model answer is fully aligned with the policy and factually correct.\n- **0.75**: The model answer is mostly correct but has minor omissions or slight rewording that does not change meaning.\n- **0.5**: The model answer is partially correct but lacks key details or contains speculative statements.\n- **0.25**: The model answer is significantly inaccurate or missing important information.\n- **0.0**: The model answer is completely incorrect, hallucinates policy details, or is irrelevant.\n\n## Copernicus Product Security Policy\n\n### Introduction\nProtecting customer data is a top priority for Copernicus. Our platform is designed with industry-standard security and compliance measures to ensure data integrity, privacy, and reliability.\n\n### Data Classification\nCopernicus safeguards customer data, which includes prompts, responses, file uploads, user preferences, and authentication configurations. Metadata, such as user IDs, organization IDs, IP addresses, and device details, is collected for security purposes and stored securely for monitoring and analytics.\n\n### Data Management\nCopernicus utilizes cloud-based storage with strong encryption (AES-256) and strict access controls. Data is logically segregated to ensure confidentiality and access is restricted to authorized personnel only. Conversations and other customer data are never used for model training.\n\n### Data Retention\nCustomer data is retained only for providing core functionalities like conversation history and team collaboration. Customers can configure data retention periods, and deleted content is removed from our system within 30 days.\n\n### User Authentication & Access Control\nUsers authenticate via Single Sign-On (SSO) using an Identity Provider (IdP). Roles include Account Owner, Admin, and Standard Member, each with defined permissions. User provisioning can be automated through SCIM integration.\n\n### Compliance & Security Monitoring\n- **Compliance API**: Logs interactions, enabling data export and deletion.\n- **Audit Logging**: Ensures transparency for security audits.\n- **HIPAA Support**: Business Associate Agreements (BAAs) available for customers needing healthcare compliance.\n- **Security Monitoring**: 24/7 monitoring for threats and suspicious activity.\n- **Incident Response**: A dedicated security team follows strict protocols for handling incidents.\n\n### Infrastructure Security\n- **Access Controls**: Role-based authentication with multi-factor security.\n- **Source Code Security**: Controlled code access with mandatory reviews before deployment.\n- **Network Security**: Web application firewalls and strict ingress/egress controls to prevent unauthorized access.\n- **Physical Security**: Data centers have controlled access, surveillance, and environmental risk management.\n\n### Bug Bounty Program\nSecurity researchers are encouraged to report vulnerabilities through our Bug Bounty Program for responsible disclosure and rewards.\n\n### Compliance & Certifications\nCopernicus maintains compliance with industry standards, including SOC 2 and GDPR. Customers can access security reports and documentation via our Security Portal.\n\n### Conclusion\nCopernicus prioritizes security, privacy, and compliance. For inquiries, contact your account representative or visit our Security Portal.\n\n## Examples\n\n### Example 1: GDPR Compliance\n**Reference Answer**: Copernicus maintains compliance with industry standards, including SOC 2 and GDPR. Customers can access security reports and documentation via our Security Portal.\n\n**Model Answer 1**: Yes, Copernicus is GDP"
              }
            ]
          }
        }
      }
    }
  }
}
```
```

--------------------------------

### Create MCP Tool Response - C#

Source: https://developers.openai.com/api/docs/guides/tools-connectors-mcp

This C# example shows how to set up an OpenAI API client and create a response using an MCP tool. It configures the model, tool details, and approval policy programmatically. The input question pertains to transport protocols supported by a specific MCP specification.

```csharp
using OpenAI.Responses;

string key = Environment.GetEnvironmentVariable("OPENAI_API_KEY")!;
OpenAIResponseClient client = new(model: "gpt-5", apiKey: key);

ResponseCreationOptions options = new();
options.Tools.Add(ResponseTool.CreateMcpTool(
    serverLabel: "deepwiki",
    serverUri: new Uri("https://mcp.deepwiki.com/mcp"),
    allowedTools: new McpToolFilter() { ToolNames = { "ask_question", "read_wiki_structure" } },
    toolCallApprovalPolicy: new McpToolCallApprovalPolicy(GlobalMcpToolCallApprovalPolicy.NeverRequireApproval)
));

OpenAIResponse response = (OpenAIResponse)client.CreateResponse([
    ResponseItem.CreateUserMessageItem([
        ResponseContentPart.CreateInputTextPart("What transport protocols does the 2025-03-26 version of the MCP spec (modelcontextprotocol/modelcontextprotocol) support?")
    ])
], options);

Console.WriteLine(response.GetOutputText());
```

--------------------------------

### Generate Images with Responses API

Source: https://developers.openai.com/api/docs/guides/images-vision

This section demonstrates how to generate images using the Responses API with the `gpt-4.1-mini` model. It includes examples in both JavaScript and Python.

```APIDOC
## POST /v1/responses

### Description
Generates an image based on a text prompt using the Responses API.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation (e.g., `gpt-4.1-mini`).
- **input** (string) - Required - The text prompt describing the image to generate.
- **tools** (array) - Required - A list of tools to use, including `image_generation`.
  - **type** (string) - Required - The type of tool, must be `image_generation`.

### Request Example (JavaScript)
```javascript
import OpenAI from "openai";
const openai = new OpenAI();

const response = await openai.responses.create({
    model: "gpt-4.1-mini",
    input: "Generate an image of gray tabby cat hugging an otter with an orange scarf",
    tools: [{type: "image_generation"}],
});

// Save the image to a file
const imageData = response.output
  .filter((output) => output.type === "image_generation_call")
  .map((output) => output.result);

if (imageData.length > 0) {
  const imageBase64 = imageData[0];
  const fs = await import("fs");
  fs.writeFileSync("cat_and_otter.png", Buffer.from(imageBase64, "base64"));
}
```

### Request Example (Python)
```python
from openai import OpenAI
import base64

client = OpenAI()

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Generate an image of gray tabby cat hugging an otter with an orange scarf",
    tools=[{"type": "image_generation"}],
)

# Save the image to a file
image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if image_data:
    image_base64 = image_data[0]
    with open("cat_and_otter.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
```

### Response
#### Success Response (200)
- **output** (array) - A list of outputs from the tools used.
  - **type** (string) - The type of output, e.g., `image_generation_call`.
  - **result** (string) - The base64 encoded image data.

#### Response Example
```json
{
  "id": "resp_abc123",
  "model": "gpt-4.1-mini",
  "output": [
    {
      "type": "image_generation_call",
      "result": "/9j/4AAQSkZJRgABAQEAS..."
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 1024,
    "total_tokens": 1049
  }
}
```
```

--------------------------------

### Edit an image using a mask (inpainting) - Node.js

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=abstract-orbit

This example demonstrates how to edit an image using a mask with the OpenAI Node.js client. You provide an input image and a mask image to guide the editing process.

```APIDOC
## POST /v1/images/edits

### Description
Edits an image using a mask to specify areas for modification. The model uses the mask as guidance for editing.

### Method
POST

### Endpoint
/v1/images/edits

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for editing (e.g., "gpt-image-1").
- **image** (file) - Required - The image to edit. Must be a PNG image, less than 4MB.
- **mask** (file) - Required - The mask image. Must be a PNG image, less than 4MB. The transparent areas of the mask indicate where the image should be altered.
- **prompt** (string) - Required - A text description of the desired content for the edited image.
- **n** (integer) - Optional - The number of edits to generate. Must be between 1 and 10.
- **size** (string) - Optional - The desired size of the edited image. Must be one of `256x256`, `512x512`, or `1024x1024`.
- **response_format** (string) - Optional - The format in which the generated images are returned. Must be one of `url` or `b64_json`.

### Request Example
```javascript
import fs from "fs";
import OpenAI, { toFile } from "openai";

const client = new OpenAI();

const rsp = await client.images.edit({
    model: "gpt-image-1",
    image: await toFile(fs.createReadStream("sunlit_lounge.png"), null, {
        type: "image/png",
    }),
    mask: await toFile(fs.createReadStream("mask.png"), null, {
        type: "image/png",
    }),
    prompt: "A sunlit indoor lounge area with a pool containing a flamingo",
});

// Save the image to a file
const image_base64 = rsp.data[0].b64_json;
const image_bytes = Buffer.from(image_base64, "base64");
fs.writeFileSync("lounge.png", image_bytes);
```

### Response
#### Success Response (200)
- **created** (integer) - The Unix timestamp of when the image was created.
- **data** (array) - An array of image objects.
  - **b64_json** (string) - The base64 encoded JSON of the generated image, or null if `response_format` is `url`.
  - **url** (string) - The URL of the generated image, or null if `response_format` is `b64_json`.

#### Response Example
```json
{
  "created": 1678886400,
  "data": [
    {
      "b64_json": "...base64_encoded_image_data...",
      "url": null
    }
  ]
}
```
```

--------------------------------

### Edit an image using a mask (inpainting) - Python

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=abstract-orbit

This example demonstrates how to edit an image using a mask with the OpenAI Python client. You provide an input image and a mask image to guide the editing process.

```APIDOC
## POST /v1/images/edits

### Description
Edits an image using a mask to specify areas for modification. The model uses the mask as guidance for editing.

### Method
POST

### Endpoint
/v1/images/edits

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for editing (e.g., "gpt-image-1").
- **image** (file) - Required - The image to edit. Must be a PNG image, less than 4MB.
- **mask** (file) - Required - The mask image. Must be a PNG image, less than 4MB. The transparent areas of the mask indicate where the image should be altered.
- **prompt** (string) - Required - A text description of the desired content for the edited image.
- **n** (integer) - Optional - The number of edits to generate. Must be between 1 and 10.
- **size** (string) - Optional - The desired size of the edited image. Must be one of `256x256`, `512x512`, or `1024x1024`.
- **response_format** (string) - Optional - The format in which the generated images are returned. Must be one of `url` or `b64_json`.

### Request Example
```python
from openai import OpenAI
client = OpenAI()

result = client.images.edit(
    model="gpt-image-1",
    image=open("sunlit_lounge.png", "rb"),
    mask=open("mask.png", "rb"),
    prompt="A sunlit indoor lounge area with a pool containing a flamingo"
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("composition.png", "wb") as f:
    f.write(image_bytes)
```

### Response
#### Success Response (200)
- **created** (integer) - The Unix timestamp of when the image was created.
- **data** (array) - An array of image objects.
  - **b64_json** (string) - The base64 encoded JSON of the generated image, or null if `response_format` is `url`.
  - **url** (string) - The URL of the generated image, or null if `response_format` is `b64_json`.

#### Response Example
```json
{
  "created": 1678886400,
  "data": [
    {
      "b64_json": "...base64_encoded_image_data...",
      "url": null
    }
  ]
}
```
```

--------------------------------

### Initialize and Run MCP Server (Python)

Source: https://developers.openai.com/api/docs/mcp

This Python function initializes and runs the MCP server. It first verifies the OpenAI API key, then creates and configures the server to listen on port 8000 using SSE transport. Error handling for KeyboardInterrupt and other exceptions is included.

```python
def main():
    """Main function to start the MCP server."""
    # Verify OpenAI client is initialized
    if not openai_client:
        logger.error(
            "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
        )
        raise ValueError("OpenAI API key is required")

    logger.info(f"Using vector store: {VECTOR_STORE_ID}")

    # Create the MCP server
    server = create_server()

    # Configure and start the server
    logger.info("Starting MCP server on 0.0.0.0:8000")
    logger.info("Server will be accessible via SSE transport")

    try:
        # Use FastMCP's built-in run method with SSE transport
        server.run(transport="sse", host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
```

--------------------------------

### Analyze Image with URL (C#)

Source: https://developers.openai.com/api/docs/guides/images-vision_api-mode=responses

Analyzes an image from a URL using the OpenAI C# SDK. This example sets up the client with an API key and constructs a request containing both text and image URL parts. It requires the `OpenAI` NuGet package.

```csharp
using OpenAI.Responses;
using System;

string key = Environment.GetEnvironmentVariable("OPENAI_API_KEY")!;
OpenAIResponseClient client = new(model: "gpt-4.1-mini", apiKey: key);

Uri imageUrl = new("https://api.nga.gov/iiif/a2e6da57-3cd1-4235-b20e-95dcaefed6c8/full/!800,800/0/default.jpg");

OpenAIResponse response = (OpenAIResponse)client.CreateResponse([
    ResponseItem.CreateUserMessageItem([
        ResponseContentPart.CreateInputTextPart("What is in this image?"),
        ResponseContentPart.CreateInputImagePart(imageUrl)
    ])
]);

Console.WriteLine(response.GetOutputText());
```

--------------------------------

### Creating a Fine-tuning Job with JSON Configuration

Source: https://developers.openai.com/api/docs/guides/reinforcement-fine-tuning

This example shows how to define a fine-tuning job using a JSON configuration object. It specifies the model, training data, response format, and hyperparameters. This configuration is sent to the OpenAI API to initiate the fine-tuning process.

```json
{
  "training_file": "file-xxxxxxxxxxxxxxxxx",
  "validation_file": "file-yyyyyyyyyyyyyyyyy",
  "model": "gpt-4o-2024-08-06",
  "hyperparameters": {
    "n_epochs": 3
  },
  "response_format": {
    "type": "json_object"
  },
  "tools": [
    {
      "type": "json_object",
      "json_schema": {
        "name": "security_assistant",
        "strict": true,
        "schema": {
          "type": "object",
          "properties": {
            "compliant": {
              "type": "string"
            },
            "explanation": {
              "type": "string"
            }
          },
          "required": [
            "compliant",
            "explanation"
          ],
          "additionalProperties": false
        }
      }
    }
  ],
  "seed": 1234
}

```

--------------------------------

### GPT-5.2 Model Migration Recommendations

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=company-acronym-list

Provides specific recommendations for migrating from older OpenAI models to GPT-5.2. It suggests the appropriate GPT-5.2 model version and reasoning effort settings based on the original model used. Prompt tuning is often recommended for optimal results.

```text
  * **gpt-5.1** : `gpt-5.2` with default settings is meant to be a drop-in replacement.
  * **o3** : `gpt-5.2` with `medium` or `high` reasoning. Start with `medium` reasoning with prompt tuning, then increase to `high` if you aren’t getting the results you want.
  * **gpt-4.1** : `gpt-5.2` with `none` reasoning. Start with `none` and tune your prompts; increase if you need better performance.
  * **o4-mini or gpt-4.1-mini** : `gpt-5-mini` with prompt tuning is a great replacement.
  * **gpt-4.1-nano** : `gpt-5-nano` with prompt tuning is a great replacement.
```

--------------------------------

### Batch API - Example Response

Source: https://developers.openai.com/api/docs/api-reference/batch/create

This section provides an example of a successful response when interacting with the Batch API, detailing the structure of a batch object.

```APIDOC
## Batch API - Example Response

### Description
This endpoint returns an example of a batch object, which represents an asynchronous job for processing data.

### Method
GET

### Endpoint
/v1/batches/{batch_id}

### Parameters
#### Path Parameters
- **batch_id** (string) - Required - The ID of the batch job to retrieve.

### Response
#### Success Response (200)
- **id** (string) - The unique identifier for the batch job.
- **object** (string) - The type of object, always "batch".
- **endpoint** (string) - The API endpoint used for this batch job.
- **errors** (object or null) - Contains errors if the batch job failed.
- **input_file_id** (string) - The ID of the input file for the batch job.
- **completion_window** (string) - The time window for job completion.
- **status** (string) - The current status of the batch job (e.g., "validating", "queued", "processing").
- **output_file_id** (string or null) - The ID of the output file if the job completed successfully.
- **error_file_id** (string or null) - The ID of the error file if the job encountered errors.
- **created_at** (integer) - Timestamp of when the batch job was created.
- **in_progress_at** (integer or null) - Timestamp of when the batch job started processing.
- **expires_at** (integer or null) - Timestamp of when the batch job will expire.
- **finalizing_at** (integer or null) - Timestamp of when the batch job is being finalized.
- **completed_at** (integer or null) - Timestamp of when the batch job completed.
- **failed_at** (integer or null) - Timestamp of when the batch job failed.
- **expired_at** (integer or null) - Timestamp of when the batch job expired.
- **cancelling_at** (integer or null) - Timestamp of when the batch job was cancelled.
- **cancelled_at** (integer or null) - Timestamp of when the batch job was cancelled.
- **request_counts** (object) - Counts of requests within the batch job.
  - **total** (integer) - Total number of requests.
  - **completed** (integer) - Number of completed requests.
  - **failed** (integer) - Number of failed requests.
- **metadata** (object) - Custom metadata associated with the batch job.
  - **customer_id** (string) - Identifier for the customer.
  - **batch_description** (string) - A description of the batch job.

#### Response Example
```json
{
  "id": "batch_abc123",
  "object": "batch",
  "endpoint": "/v1/chat/completions",
  "errors": null,
  "input_file_id": "file-abc123",
  "completion_window": "24h",
  "status": "validating",
  "output_file_id": null,
  "error_file_id": null,
  "created_at": 1711471533,
  "in_progress_at": null,
  "expires_at": null,
  "finalizing_at": null,
  "completed_at": null,
  "failed_at": null,
  "expired_at": null,
  "cancelling_at": null,
  "cancelled_at": null,
  "request_counts": {
    "total": 0,
    "completed": 0,
    "failed": 0
  },
  "metadata": {
    "customer_id": "user_123456789",
    "batch_description": "Nightly eval job"
  }
}
```
```

--------------------------------

### Edit an image with a mask using GPT Image (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=cosmic-ballet

This example demonstrates how to edit an image using a mask with the GPT Image model in Python. The mask guides the editing process, and the model uses the prompt for instructions.

```APIDOC
## POST /v1/responses

### Description
Edits an image using a mask with the GPT Image model. The mask indicates which part of the image to edit, and the prompt guides the generation.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for image generation (e.g., "gpt-4o").
- **input** (array) - Required - An array of input objects, including text prompts and images.
  - **role** (string) - Required - The role of the message (e.g., "user").
  - **content** (array) - Required - An array of content objects.
    - **type** (string) - Required - The type of content (e.g., "input_text", "input_image").
    - **text** (string) - Optional - The text prompt.
    - **file_id** (string) - Optional - The ID of the uploaded file.
- **tools** (array) - Required - An array of tools to use.
  - **type** (string) - Required - The type of tool (e.g., "image_generation").
  - **quality** (string) - Optional - The quality of the generated image (e.g., "high").
  - **input_image_mask** (object) - Optional - Specifies the mask for image editing.
    - **file_id** (string) - Required - The ID of the uploaded mask file.

### Request Example
```json
{
  "model": "gpt-4o",
  "input": [
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "generate an image of the same sunlit indoor lounge area with a pool but the pool should contain a flamingo"
        },
        {
          "type": "input_image",
          "file_id": "file-xxxxxxxx"
        }
      ]
    }
  ],
  "tools": [
    {
      "type": "image_generation",
      "quality": "high",
      "input_image_mask": {
        "file_id": "file-yyyyyyyy"
      }
    }
  ]
}
```

### Response
#### Success Response (200)
- **output** (array) - An array of tool outputs.
  - **type** (string) - The type of output (e.g., "image_generation_call").
  - **result** (string) - The base64 encoded image data.

#### Response Example
```json
{
  "output": [
    {
      "type": "image_generation_call",
      "result": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    }
  ]
}
```
```

--------------------------------

### Make First API Request (curl)

Source: https://developers.openai.com/api/docs/index

This snippet demonstrates how to make your first API request using curl to the OpenAI API. It includes setting the necessary headers for content type and authorization, and provides a sample JSON payload for a text generation request.

```shell
curl https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-5.2",
    "input": "Write a short bedtime story about a unicorn."
  }'
```

--------------------------------

### GPT-5.2 Model Migration Guidance

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=asteroid-game-5.2

This snippet summarizes the recommended GPT-5.2 settings for migrating from older models. It highlights specific configurations for 'gpt-5.1', 'o3', 'gpt-4.1', and 'gpt-4.1-mini'/'gpt-4.1-nano' to ensure optimal performance and compatibility.

```text
* **gpt-5.1** : `gpt-5.2` with default settings is meant to be a drop-in replacement.
* **o3** : `gpt-5.2` with `medium` or `high` reasoning. Start with `medium` reasoning with prompt tuning, then increase to `high` if you aren’t getting the results you want.
* **gpt-4.1** : `gpt-5.2` with `none` reasoning. Start with `none` and tune your prompts; increase if you need better performance.
* **o4-mini or gpt-4.1-mini** : `gpt-5-mini` with prompt tuning is a great replacement.
* **gpt-4.1-nano** : `gpt-5-nano` with prompt tuning is a great replacement.
```

--------------------------------

### Generate Image using DALL-E 3 with Python (Second Alternative)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=album-cover

Another Python example for DALL-E 3 image generation, demonstrating the use of the 'client' object and its 'images.generate' method.

```python
from openai import OpenAI
client = OpenAI()

result = client.images.generate(
    model="dall-e-3",
    prompt="a white siamese cat",
    size="1024x1024"
)

print(result.data[0].url)
```

--------------------------------

### Edit an image using a mask (inpainting) - Python SDK

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=bottle

This example demonstrates how to edit an image using a mask with the OpenAI Python SDK. You provide an input image and a mask image, along with a text prompt, to guide the inpainting process.

```APIDOC
## POST /v1/responses

### Description
Edits an image based on a text prompt and a mask. The mask indicates which part of the image should be edited. This method uses the `gpt-4o` model and is designed for prompt-based image generation and editing.

### Method
POST

### Endpoint
`/v1/responses`

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for image generation (e.g., `gpt-4o`).
- **input** (array) - Required - An array of input objects, including text prompts and image file IDs.
  - **role** (string) - Required - Role of the message (e.g., `user`).
  - **content** (array) - Required - Content of the message.
    - **type** (string) - Required - Type of content (e.g., `input_text`, `input_image`).
    - **text** (string) - Required if type is `input_text` - The text prompt.
    - **file_id** (string) - Required if type is `input_image` - The ID of the input image file.
- **tools** (array) - Required - An array of tools to use, including image generation.
  - **type** (string) - Required - Type of tool (e.g., `image_generation`).
  - **quality** (string) - Optional - Quality of the generated image (e.g., `high`).
  - **input_image_mask** (object) - Optional - Configuration for the input image mask.
    - **file_id** (string) - Required - The ID of the mask image file.

### Request Example
```json
{
  "model": "gpt-4o",
  "input": [
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "generate an image of the same sunlit indoor lounge area with a pool but the pool should contain a flamingo"
        },
        {
          "type": "input_image",
          "file_id": "file-xxxxxxxxxxxxxxxxx"
        }
      ]
    }
  ],
  "tools": [
    {
      "type": "image_generation",
      "quality": "high",
      "input_image_mask": {
        "file_id": "file-yyyyyyyyyyyyyyyyy"
      }
    }
  ]
}
```

### Response
#### Success Response (200)
- **output** (array) - An array of tool outputs. For image generation, it contains results with `type: "image_generation_call"`.
  - **type** (string) - Type of the output (e.g., `image_generation_call`).
  - **result** (string) - Base64 encoded image data.

#### Response Example
```json
{
  "id": "resp_abc123xyz",
  "model": "gpt-4o",
  "output": [
    {
      "type": "image_generation_call",
      "result": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgJCwkJCQwL//2wBDAQMDAwQDBAgEBAgQCggLEA..."
    }
  ],
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 200,
    "total_tokens": 300
  }
}
```
```

--------------------------------

### Provide System Instructions for Model

Source: https://developers.openai.com/api/docs/api-reference/realtime-client-events/input_audio_buffer/commit

Guide the model's behavior and response style using system instructions. These instructions can influence content, format, and even audio characteristics like speaking speed or emotional tone, though adherence is not guaranteed.

```json
{
  "instructions": "Be extremely succinct and use a friendly tone."
}
```

--------------------------------

### Edit an image using a mask (inpainting) - cURL

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=clay-figurine

This example demonstrates how to edit an image using a mask with cURL. A mask is provided to indicate which part of the image should be edited, and additional instructions guide the editing process.

```APIDOC
## POST /v1/images/edits

### Description
Edits an image using a mask to specify the area to be modified. The model uses the mask as guidance, and the editing is prompt-based.

### Method
POST

### Endpoint
/v1/images/edits

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for editing. Example: `gpt-image-1`.
- **image** (file) - Required - The image to edit. Must be a PNG image, less than 4MB.
- **mask** (file) - Required - An additional image for the mask. Must be a PNG image, less than 4MB. The transparent index in the mask file will be filled.
- **prompt** (string) - Required - A text description of the desired image modifications.
- **n** (integer) - Optional - The number of edits to generate. Defaults to 1.
- **size** (string) - Optional - The size of the generated images. Must be one of `256x256`, `512x512`, or `1024x1024`.
- **response_format** (string) - Optional - The format in which the generated images are returned. Must be one of `url` or `b64_json`. Defaults to `url`.

### Request Example
```bash
curl -s -D >(grep -i x-request-id >&2) \
  -o >(jq -r '.data[0].b64_json' | base64 --decode > lounge.png) \
  -X POST "https://api.openai.com/v1/images/edits" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "model=gpt-image-1" \
  -F "mask=@mask.png" \
  -F "image[]=@sunlit_lounge.png" \
  -F 'prompt=A sunlit indoor lounge area with a pool containing a flamingo'
```

### Response
#### Success Response (200)
- **created** (integer) - The Unix timestamp of when the edit was created.
- **data** (array) - An array of image objects.
  - **url** (string) - The URL of the generated image (if `response_format` is `url`).
  - **b64_json** (string) - The base64 encoded JSON of the generated image (if `response_format` is `b64_json`).

#### Response Example
```json
{
  "created": 1678886400,
  "data": [
    {
      "url": "https://example.com/image.png",
      "b64_json": "...base64_encoded_image..."
    }
  ]
}
```
```

--------------------------------

### Streaming Function Calls with Python

Source: https://developers.openai.com/api/docs/guides/function-calling_api-mode=chat

This example demonstrates how to stream function calls using the OpenAI Python client. It shows setting up tools, initiating a streaming request, and iterating through the events to capture function call details.

```APIDOC
## POST /v1/chat/completions (Streaming Function Calls - Python)

### Description
This endpoint allows you to stream responses from the model, including function calls. You can observe the model filling its arguments and display them in real-time.

### Method
POST

### Endpoint
/v1/chat/completions

### Parameters
#### Query Parameters
- **stream** (boolean) - Required - Set to `true` to enable streaming.

#### Request Body
- **model** (string) - Required - The model to use for the chat completion (e.g., "gpt-4.1").
- **input** (array) - Required - An array of message objects representing the conversation history. Each object should have a `role` (e.g., "user") and `content` (e.g., "What's the weather like in Paris today?").
- **tools** (array) - Optional - A list of tool definitions the model may use. Each tool should have a `type`, `name`, `description`, and `parameters` object.
- **stream** (boolean) - Required - Set to `true` to enable streaming.

### Request Example
```python
from openai import OpenAI

client = OpenAI()

tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get current temperature for a given location.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City and country e.g. Bogotá, Colombia"
            }
        },
        "required": [
            "location"
        ],
        "additionalProperties": False
    }
}]

stream = client.chat.completions.create(
    model="gpt-4.1",
    messages=[{"role": "user", "content": "What's the weather like in Paris today?"}],
    tools=tools,
    stream=True
)

for event in stream:
    print(event)
```

### Response
#### Success Response (200)
Events are streamed back. Each event can be of different types, such as `response.output_item.added` for function call initiation and `response.function_call_arguments.delta` for argument chunks.

#### Response Example
```json
{
  "type": "response.output_item.added",
  "response_id": "resp_1234xyz",
  "output_index": 0,
  "item": {
    "type": "function_call",
    "id": "fc_1234xyz",
    "call_id": "call_1234xyz",
    "name": "get_weather",
    "arguments": ""
  }
}
{
  "type": "response.function_call_arguments.delta",
  "response_id": "resp_1234xyz",
  "item_id": "fc_1234xyz",
  "output_index": 0,
  "delta": "{\"location\":\""
}
// ... more delta events ...
{
  "type": "response.function_call_arguments.done",
  "response_id": "resp_1234xyz",
  "item_id": "fc_1234xyz",
  "output_index": 0,
  "arguments": "{\"location\":\"Paris, France\"}"
}
{
  "type": "response.output_item.done",
  "response_id": "resp_1234xyz",
  "output_index": 0,
  "item": {
    "type": "function_call",
    "id": "fc_1234xyz",
    "call_id": "call_1234xyz",
    "name": "get_weather",
    "arguments": "{\"location\":\"Paris, France\"}"
  }
}
```
```

--------------------------------

### Image Generation with Transparent Background (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=alien-rock

This example demonstrates how to generate an image with a transparent background using the OpenAI Python client library. It utilizes the `responses.create` method with the `image_generation` tool.

```APIDOC
## POST /v1/responses (Image Generation Tool)

### Description
Generates an image with a transparent background using the `image_generation` tool within the `responses.create` endpoint.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for image generation (e.g., "gpt-5").
- **input** (string) - Required - The prompt describing the image to generate.
- **tools** (array) - Required - A list of tools to use. For image generation, this should include an object with:
  - **type** (string) - Required - Must be "image_generation".
  - **background** (string) - Optional - Set to "transparent" to enable transparency. Supported with PNG and WEBP output formats.
  - **quality** (string) - Optional - "medium" or "high" recommended for transparency.

### Request Example
```json
{
  "model": "gpt-5",
  "input": "Draw a 2D pixel art style sprite sheet of a tabby gray cat",
  "tools": [
    {
      "type": "image_generation",
      "background": "transparent",
      "quality": "high"
    }
  ]
}
```

### Response
#### Success Response (200)
- **output** (array) - A list of outputs from the tools used. For image generation, contains objects with:
  - **type** (string) - "image_generation_call"
  - **result** (string) - Base64 encoded image data.
```

--------------------------------

### Example RFT Fine-Tuning Data Entry (JSON)

Source: https://developers.openai.com/api/docs/guides/reinforcement-fine-tuning

Illustrates a single entry in a JSONL file for RFT fine-tuning. Each entry includes a 'messages' array for the conversation and 'compliant' and 'explanation' fields for grading the model's output.

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Do you have a dedicated security team?"
    }
  ],
  "compliant": "yes",
  "explanation": "A dedicated security team follows strict protocols for handling incidents."
}
```

--------------------------------

### Sample Training Data for RFT Fine-Tuning (JSONL)

Source: https://developers.openai.com/api/docs/guides/reinforcement-fine-tuning

Provides sample lines of JSONL data suitable for training an RFT fine-tune job. These examples demonstrate the structure and content expected for the training set.

```jsonl
{"messages":[{"role":"user","content":"Do you have a dedicated security team?"}],"compliant":"yes","explanation":"A dedicated security team follows strict protocols for handling incidents."}
{"messages":[{"role":"user","content":"Have you undergone third-party security audits or penetration testing in the last 12 months?"}],"compliant":"needs review","explanation":"The policy does not explicitly mention undergoing third-party security audits or penetration testing. It only mentions SOC 2 and GDPR compliance."}
{"messages":[{"role":"user","content":"Is your software SOC 2, ISO 27001, or similarly certified?"}],"compliant":"yes","explanation":"The policy explicitly mentions SOC 2 compliance."}
```

--------------------------------

### Edit an image using a mask (inpainting) - JavaScript

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=school-lab

This example demonstrates how to edit an image using JavaScript, providing a mask to specify the editing area. The prompt guides the model's generation within the masked region.

```APIDOC
## POST /v1/images/edits

### Description
Edits an image based on a provided mask and prompt using JavaScript. The mask defines the region for modification, and the prompt provides instructions for the new content.

### Method
POST

### Endpoint
/v1/images/edits

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for image editing (e.g., "gpt-image-1").
- **image** (File) - Required - The image to edit. Must be a PNG image, less than 4MB.
- **mask** (File) - Required - An RGBA image, less than 4MB. Red channels of the mask indicate where to alter the image; other channels will be ignored.
- **prompt** (string) - Required - A text description of the desired content for the edited image.
- **n** (number) - Optional - The number of edits to generate. Defaults to 1.
- **size** (string) - Optional - The desired size of the generated images. Must be one of `256x256`, `512x512`, or `1024x1024` for `dall-e-2`.
- **response_format** (string) - Optional - The format in which the generated images are returned. Must be one of `url` or `b64_json`.

### Request Example
```javascript
import fs from "fs";
import OpenAI, { toFile } from "openai";

const client = new OpenAI();

const rsp = await client.images.edit({
    model: "gpt-image-1",
    image: await toFile(fs.createReadStream("sunlit_lounge.png"), null, {
        type: "image/png",
    }),
    mask: await toFile(fs.createReadStream("mask.png"), null, {
        type: "image/png",
    }),
    prompt: "A sunlit indoor lounge area with a pool containing a flamingo",
});

// Save the image to a file
const image_base64 = rsp.data[0].b64_json;
const image_bytes = Buffer.from(image_base64, "base64");
fs.writeFileSync("lounge.png", image_bytes);
```

### Response
#### Success Response (200)
- **created** (number) - Timestamp of when the image was created.
- **data** (array) - An array of image objects.
  - **b64_json** (string) - The base64 encoded image data.
  - **url** (string) - The URL of the generated image.

#### Response Example
```json
{
  "created": 1678886400,
  "data": [
    {
      "url": "https://example.com/image.png",
      "b64_json": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    }
  ]
}
```
```

--------------------------------

### Prompting Guidance for GPT-5.2

Source: https://developers.openai.com/api/docs/guides/latest-model

Recommendations and resources for crafting effective prompts for GPT-5.2, designed for coding and agentic tasks.

```APIDOC
## Prompting Guidance for GPT-5.2

### Description

GPT-5.2 is optimized for coding and agentic tasks. It functions as a reasoning model, breaking down problems into steps and generating an internal chain of thought. To maximize performance, it is recommended to pass these reasoning items back to the model in subsequent interactions. This prevents redundant reasoning and aligns the interactions with the model's training distribution. For multi-turn conversations, providing the `previous_response_id` automatically includes prior reasoning items. This is particularly crucial when utilizing tools, as it ensures necessary information is available for function calls, either via `previous_response_id` or by direct inclusion in `input`.

### Recommendations

- Iterate on prompts using the [prompt optimizer](https://platform.openai.com/chat/edit?optimize=true).
- Learn best practices for prompting GPT-5 models in the [Cookbook](https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide).
- Explore prompt samples specific to frontend development for GPT-5 family models in the [Cookbook](https://cookbook.openai.com/examples/gpt-5.2/gpt-5.2_frontend).

### Further Reading

- [GPT-5.2 Prompting Guide](https://developers.openai.com/cookbook/examples/gpt-5/gpt-5-2_prompting_guide)
- [GPT-5.2-Codex Prompting Guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide)
- [GPT-5.2 Blog Post](https://openai.com/index/introducing-gpt-5-2/)
- [GPT-5 Frontend Guide](https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_frontend)
- [GPT-5 Model Family: New Features Guide](https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_new_params_and_tools)
- [Cookbook on Reasoning Models](https://developers.openai.com/cookbook/examples/responses_api/reasoning_items)
- [Comparison of Responses API vs. Chat Completions](https://developers.openai.com/api/docs/guides/migrate-to-responses)
```

--------------------------------

### Edit an image using a mask (inpainting) - JavaScript

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=bottle

This example demonstrates how to edit an image using a mask with the OpenAI JavaScript client. The mask indicates which part of the image should be edited, and the prompt guides the model's changes.

```APIDOC
## POST /v1/images/edits

### Description
Edits an image using a mask to indicate the area to be modified. The model uses the prompt and the mask as guidance for the editing process.

### Method
POST

### Endpoint
/v1/images/edits

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for image editing (e.g., "gpt-image-1").
- **image** (file) - Required - The image to edit. Must be a PNG image, less than 4MB.
- **mask** (file) - Required - An RGBA image, less than 4MB. Red channels of the mask indicate where to alter the image. The image is altered where the mask is red. The mask should be the same dimensions as the image.
- **prompt** (string) - Required - A text description of the desired image modifications.
- **n** (integer) - Optional - The number of images to generate. Defaults to 1.
- **size** (string) - Optional - The desired size of the generated images. Must be one of 256x256, 512x512, or 1024x1024 for "dall-e-2" models. Defaults to 1024x1024.
- **response_format** (string) - Optional - The format in which the generated images are returned. Must be one of url or b64_json. Defaults to url.

### Request Example
```javascript
import fs from "fs";
import OpenAI, { toFile } from "openai";

const client = new OpenAI();

const rsp = await client.images.edit({
    model: "gpt-image-1",
    image: await toFile(fs.createReadStream("sunlit_lounge.png"), null, {
        type: "image/png",
    }),
    mask: await toFile(fs.createReadStream("mask.png"), null, {
        type: "image/png",
    }),
    prompt: "A sunlit indoor lounge area with a pool containing a flamingo",
});

// Save the image to a file
const image_base64 = rsp.data[0].b64_json;
const image_bytes = Buffer.from(image_base64, "base64");
fs.writeFileSync("lounge.png", image_bytes);
```

### Response
#### Success Response (200)
- **created** (integer) - The Unix timestamp of when the image was created.
- **data** (array) - An array of image objects.
  - **url** (string) - The URL of the generated image (if response_format is url).
  - **b64_json** (string) - The base64 encoded JSON of the generated image (if response_format is b64_json).

#### Response Example
```json
{
  "created": 1678886400,
  "data": [
    {
      "url": "https://example.com/image.png",
      "b64_json": "...base64_encoded_image..."
    }
  ]
}
```
```

--------------------------------

### Image Generation with Transparent Background (Node.js)

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=spacecraft-dashboard

This example shows how to generate an image with a transparent background using the OpenAI Node.js client. It uses the `client.responses.create` method, similar to the Python example, specifying `background: 'transparent'` and `quality: 'high'`.

```APIDOC
## POST /v1/responses

### Description
Generates an image with a transparent background using the `client.responses.create` method in Node.js.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for image generation (e.g., "gpt-5").
- **input** (string) - Required - The prompt for image generation.
- **tools** (array) - Required - A list of tools to use. For image generation, include an object with:
  - **type** (string) - Required - Must be "image_generation".
  - **background** (string) - Optional - Set to "transparent" to enable transparency. Supported for PNG and WEBP output formats.
  - **quality** (string) - Optional - Recommended to be "medium" or "high" for transparency. 

### Request Example
```json
{
  "model": "gpt-5",
  "input": "Draw a 2D pixel art style sprite sheet of a tabby gray cat",
  "tools": [
    {
      "type": "image_generation",
      "background": "transparent",
      "quality": "high"
    }
  ]
}
```

### Response
#### Success Response (200)
- **output** (array) - Contains the generated image data.
  - **type** (string) - Type of output, e.g., "image_generation_call".
  - **result** (string) - Base64 encoded image data.

#### Response Example
```json
{
  "output": [
    {
      "type": "image_generation_call",
      "result": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    }
  ]
}
```
```

--------------------------------

### Call GPT-5.1-Codex-Max for High Reasoning Tasks (JavaScript)

Source: https://developers.openai.com/api/docs/guides/code-generation

This JavaScript example demonstrates how to call the GPT-5.1-Codex-Max model for complex reasoning tasks, such as finding null pointer exceptions. It requires the 'openai' library and specifies the model and reasoning effort.

```javascript
import OpenAI from "openai";
const openai = new OpenAI();

const result = await openai.responses.create({
  model: "gpt-5.1-codex-max",
  input: "Find the null pointer exception: ...your code here...",
  reasoning: { effort: "high" },
});

console.log(result.output_text);
```

--------------------------------

### Image Generation API - Transparent Background (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=clay-garden-scene

This example demonstrates how to generate an image with a transparent background using the OpenAI Python client library. It utilizes the `responses.create` method with the `image_generation` tool and sets the `background` parameter to `transparent`.

```APIDOC
## POST /v1/responses (Image Generation Tool)

### Description
Generates an image with a transparent background using the `image_generation` tool within the `responses.create` endpoint.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for image generation (e.g., "gpt-5").
- **input** (string) - Required - The prompt for image generation.
- **tools** (array) - Required - A list of tools to use. For image generation, this should be an object with:
    - **type** (string) - Required - Must be "image_generation".
    - **background** (string) - Optional - Set to "transparent" to enable transparency. Supported for PNG and WEBP output formats.
    - **quality** (string) - Optional - "medium" or "high" recommended for transparency.

### Request Example
```json
{
  "model": "gpt-5",
  "input": "Draw a 2D pixel art style sprite sheet of a tabby gray cat",
  "tools": [
    {
      "type": "image_generation",
      "background": "transparent",
      "quality": "high"
    }
  ]
}
```

### Response
#### Success Response (200)
- **output** (array) - Contains results from the tools used. For image generation, it includes:
    - **type** (string) - "image_generation_call"
    - **result** (string) - Base64 encoded image data.

#### Response Example
```json
{
  "id": "resp_abc123",
  "model": "gpt-5",
  "output": [
    {
      "type": "image_generation_call",
      "result": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    }
  ]
}
```
```

--------------------------------

### Install OpenAI Agents Voice Package (Bash)

Source: https://developers.openai.com/api/docs/guides/voice-agents_voice-agent-architecture=chained

Command to install the necessary package for extending existing agents with voice capabilities using the OpenAI Agents SDK for Python. This includes the `VoicePipeline` support.

```bash
pip install openai-agents[voice]
```

--------------------------------

### Chat Completions API - Multi-turn Conversation Example

Source: https://developers.openai.com/api/docs/guides/conversation-state_api-mode=responses

This example demonstrates how to manually manage conversation state using the Chat Completions API by providing a history of messages in each request.

```APIDOC
## POST /v1/chat/completions

### Description
Manually construct a past conversation for multi-turn interactions using the Chat Completions API.

### Method
POST

### Endpoint
/v1/chat/completions

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use for completion.
- **messages** (array) - Required - A list of messages comprising the conversation so far. 
  - **role** (string) - Required - The role of the author of a message (e.g., `system`, `user`, or `assistant`).
  - **content** (string) - Required - The content of the message.

### Request Example
```json
{
  "model": "gpt-4o-mini",
  "messages": [
    { "role": "user", "content": "knock knock." },
    { "role": "assistant", "content": "Who's there?" },
    { "role": "user", "content": "Orange." }
  ]
}
```

### Response
#### Success Response (200)
- **choices** (array) - The list of completion choices for the prompt.
  - **message** (object) - Represents a message in the conversation.
    - **role** (string) - The role of the author of the message.
    - **content** (string) - The content of the message.

#### Response Example
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Orange who?"
      }
    }
  ]
}
```
```

--------------------------------

### Python Tool Calling Example

Source: https://developers.openai.com/api/docs/guides/function-calling_api-mode=chat

This example demonstrates how to use the OpenAI API with Python to enable tool calling. It includes defining a 'get_horoscope' function, prompting the model with this tool, executing the tool's logic when called by the model, and providing the results back to the model for a final response.

```APIDOC
## POST /v1/chat/completions (Tool Calling)

### Description
This endpoint allows you to prompt the model with defined tools, execute the tool logic when the model chooses to use a tool, and then provide the tool's output back to the model to generate a final response. This is useful for integrating external APIs or custom functions.

### Method
POST

### Endpoint
/v1/chat/completions

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for the chat completion (e.g., "gpt-4.1").
- **messages** (array) - Required - A list of message objects representing the conversation history.
  - **role** (string) - Required - The role of the message (e.g., "user", "assistant", "tool").
  - **content** (string) - Required - The content of the message.
  - **tool_call_id** (string) - Required (if role is "tool") - The ID of the tool call to which this message is a response.
- **tools** (array) - Optional - A list of tool definitions that the model can use.
  - **type** (string) - Required - The type of the tool (e.g., "function").
  - **function** (object) - Required - The definition of the function tool.
    - **name** (string) - Required - The name of the function.
    - **description** (string) - Optional - A description of what the function does.
    - **parameters** (object) - Required - The parameters the function accepts.
      - **type** (string) - Required - The type of the parameters (e.g., "object").
      - **properties** (object) - Required - A map of parameter names to their schemas.
      - **required** (array) - Optional - A list of parameter names that are required.
    - **strict** (boolean) - Optional - Whether to enforce strict parameter validation.

### Request Example
```python
from openai import OpenAI
import json

client = OpenAI()

# 1. Define a list of callable tools for the model
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_horoscope",
            "description": "Get today's horoscope for an astrological sign.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sign": {
                        "type": "string",
                        "description": "An astrological sign like Taurus or Aquarius",
                    },
                },
                "required": ["sign"],
            },
        },
    },
]

def get_horoscope(sign):
    return f"{sign}: Next Tuesday you will befriend a baby otter."

# Create a running input list we will add to over time
messages = [
    {"role": "user", "content": "What is my horoscope? I am an Aquarius."}
]

# 2. Prompt the model with tools defined
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=messages,
    tools=tools,
)

messages.append(response.choices[0].message)

for tool_call in response.choices[0].message.tool_calls or []:
    if tool_call.function.name == "get_horoscope":
        # 3. Execute the function logic for get_horoscope
        args = json.loads(tool_call.function.arguments)
        horoscope = get_horoscope(args["sign"])

        # 4. Provide function call results to the model
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps({"horoscope": horoscope}),
        })

response = client.chat.completions.create(
    model="gpt-4.1",
    messages=messages,
    tools=tools,
)

# 5. The model should be able to give a response!
print(response.choices[0].message.content)
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the completion.
- **object** (string) - Type of object returned, e.g., `chat.completion`.
- **created** (integer) - Unix timestamp of when the completion was created.
- **model** (string) - The model used for the completion.
- **choices** (array) - A list of completion choices.
  - **index** (integer) - The index of the choice.
  - **message** (object) - The message content.
    - **role** (string) - The role of the message (e.g., "assistant").
    - **content** (string) - The content of the message.
    - **tool_calls** (array) - Optional. If the model decided to call a tool, this will contain the tool call details.
      - **id** (string) - The ID of the tool call.
      - **type** (string) - The type of the tool call (e.g., "function").
      - **function** (object) - Details about the function call.
        - **name** (string) - The name of the function to call.
        - **arguments** (string) - JSON string of arguments to pass to the function.
  - **finish_reason** (string) - The reason the model stopped generating tokens (e.g., "stop", "tool_calls").
- **usage** (object) - Usage statistics for the completion.
  - **prompt_tokens** (integer) - Number of tokens in the prompt.
  - **completion_tokens** (integer) - Number of tokens in the completion.
  - **total_tokens** (integer) - Total tokens used.

#### Response Example
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-4.1",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Aquarius: Next Tuesday you will befriend a baby otter."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 20,
    "total_tokens": 70
  }
}
```
```

--------------------------------

### POST /v1/images/edit (Image Editing with High Input Fidelity - Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_image-generation-model=gpt-image-1

This Python example demonstrates image editing with high input fidelity using the `images.edit` method. It's the Python equivalent of the Node.js example for image editing.

```APIDOC
## POST /v1/images/edit

### Description
Edits an existing image using Python with high input fidelity, enabling detailed modifications.

### Method
POST

### Endpoint
/v1/images/edit

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for image editing (e.g., "gpt-image-1").
- **image** (list) - Required - A list of opened image files or file paths to be edited.
- **prompt** (string) - Required - A text description of the desired edits.
- **input_fidelity** (string) - Optional - The input fidelity level. Defaults to "low". Set to "high" for better detail preservation.

### Request Example
```python
{
    "model": "gpt-image-1",
    "image": [open("woman.jpg", "rb"), open("logo.png", "rb")],
    "prompt": "Add the logo to the woman's top, as if stamped into the fabric.",
    "input_fidelity": "high"
}
```

### Response
#### Success Response (200)
- **data** (list) - A list of image dictionaries.
  - **b64_json** (string) - The base64 encoded image data.

#### Response Example
```python
{
    "data": [
        {
            "b64_json": "<base64_encoded_image_data>"
        }
    ]
}
```
```

--------------------------------

### Create Custom Tool with Lark Grammar (Python & JavaScript)

Source: https://developers.openai.com/api/docs/guides/function-calling

Shows how to define a custom tool that uses a Lark context-free grammar to constrain the model's text input. This ensures the output conforms to a specific structure, demonstrated with a mathematical expression example.

```python
from openai import OpenAI

client = OpenAI()

grammar = """
start: expr
expr: term (SP ADD SP term)* -> add
| term
term: factor (SP MUL SP factor)* -> mul
| factor
factor: INT
SP: " "
ADD: "+"
MUL: "*"
%import common.INT
"""

response = client.responses.create(
    model="gpt-5",
    input="Use the math_exp tool to add four plus four.",
    tools=[
        {
            "type": "custom",
            "name": "math_exp",
            "description": "Creates valid mathematical expressions",
            "format": {
                "type": "grammar",
                "syntax": "lark",
                "definition": grammar,
            },
        }
    ]
)
print(response.output)
```

```javascript
import OpenAI from "openai";
const client = new OpenAI();

const grammar = `
start: expr
expr: term (SP ADD SP term)* -> add
| term
term: factor (SP MUL SP factor)* -> mul
| factor
factor: INT
SP: " "
ADD: "+"
MUL: "*"
%import common.INT
`;

const response = await client.responses.create({
  model: "gpt-5",
  input: "Use the math_exp tool to add four plus four.",
  tools: [
    {
      type: "custom",
      name: "math_exp",
      description: "Creates valid mathematical expressions",
      format: {
        type: "grammar",
        syntax: "lark",
        definition: grammar,
      },
    },
  ],
});

console.log(response.output);
```

--------------------------------

### Edit an image using a mask (inpainting) - Node.js

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=game-design

This example demonstrates how to edit an image using a mask with the OpenAI Node.js client. You provide an input image and a mask image, along with a text prompt, to guide the editing process.

```APIDOC
## POST /v1/images/edits

### Description
Edits an image based on a provided mask and prompt. The mask indicates which parts of the image should be altered.

### Method
POST

### Endpoint
/v1/images/edits

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for editing. Example: `gpt-image-1`
- **image** (file) - Required - The image to edit. Must be a PNG image, less than 2MB in size, and square.
- **mask** (file) - Required - The mask to use for editing. Must be a PNG image, less than 2MB in size, and square. The transparent areas of the mask indicate where the image should be edited.
- **prompt** (string) - Required - A text description of the desired image.
- **n** (integer) - Optional - The number of edits to generate. Defaults to 1.
- **size** (string) - Optional - The size of the generated images. Must be one of `256x256`, `512x512`, or `1024x1024`.
- **response_format** (string) - Optional - The format in which the generated images are returned. Must be one of `url` or `b64_json`. Defaults to `url`.

### Request Example
```javascript
import fs from "fs";
import OpenAI, { toFile } from "openai";

const client = new OpenAI();

const rsp = await client.images.edit({
    model: "gpt-image-1",
    image: await toFile(fs.createReadStream("sunlit_lounge.png"), null, {
        type: "image/png",
    }),
    mask: await toFile(fs.createReadStream("mask.png"), null, {
        type: "image/png",
    }),
    prompt: "A sunlit indoor lounge area with a pool containing a flamingo",
});

// Save the image to a file
const image_base64 = rsp.data[0].b64_json;
const image_bytes = Buffer.from(image_base64, "base64");
fs.writeFileSync("lounge.png", image_bytes);
```

### Response
#### Success Response (200)
- **created** (integer) - Timestamp of when the image was created.
- **data** (array) - An array of image objects.
  - **b64_json** (string) - The generated image data in base64 format.
  - **url** (string) - The URL of the generated image.

#### Response Example
```json
{
  "created": 1678886400,
  "data": [
    {
      "b64_json": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
      "url": "https://example.com/image.png"
    }
  ]
}
```
```

--------------------------------

### Handle Actions on Server (Python)

Source: https://developers.openai.com/api/docs/guides/chatkit-actions

Provides an example of implementing the `action` method in `ChatKitServer` to handle incoming actions on the server. It includes logic for processing the action, storing context, and generating a response.

```python
class MyChatKitServer(ChatKitServer[RequestContext])
    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: RequestContext,
    ) -> AsyncIterator[Event]:
        if action.type == "example":
          await do_thing(action.payload['id'])

          # often you'll want to add a HiddenContextItem so the model
          # can see that the user did something
          await self.store.add_thread_item(
              thread.id,
              HiddenContextItem(
                  id="item_123",
                  created_at=datetime.now(),
                  content=(
                      "<USER_ACTION>The user did a thing</USER_ACTION>"
                  ),
              ),
              context,
          )

          # then you might want to run inference to stream a response
          # back to the user.
          async for e in self.generate(context, thread):
              yield e
```

--------------------------------

### Edit an image using a mask (inpainting) - Python

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=botanical-perfume

This example demonstrates how to edit an image using a mask with the OpenAI Python client. You provide an input image and a mask image, along with a text prompt to guide the editing process.

```APIDOC
## POST /v1/images/edits

### Description
Edits an image using a mask to indicate which part of the image should be edited. The model uses the mask as guidance, and the editing is prompt-based.

### Method
POST

### Endpoint
/v1/images/edits

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for editing. Example: `gpt-image-1`.
- **image** (file) - Required - The image to edit. Must be a PNG image, less than 4MB.
- **mask** (file) - Required - The mask to edit. Must be a PNG image, less than 4MB. Transparent areas indicate where the image should be edited.
- **prompt** (string) - Required - A text description of the desired image modifications.
- **n** (integer) - Optional - The number of edits to generate. Defaults to 1.
- **size** (string) - Optional - The desired size of the edited image. Must be one of `256x256`, `512x512`, or `1024x1024`. Defaults to `1024x1024`.
- **response_format** (string) - Optional - The format in which the generated images are returned. Must be one of `url` or `b64_json`. Defaults to `url`.

### Request Example
```python
from openai import OpenAI
client = OpenAI()

result = client.images.edit(
    model="gpt-image-1",
    image=open("sunlit_lounge.png", "rb"),
    mask=open("mask.png", "rb"),
    prompt="A sunlit indoor lounge area with a pool containing a flamingo"
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("composition.png", "wb") as f:
    f.write(image_bytes)
```

### Response
#### Success Response (200)
- **created** (integer) - Timestamp of when the edit was created.
- **data** (array) - Array of image objects.
  - **url** (string) - URL of the generated image (if `response_format` is `url`).
  - **b64_json** (string) - Base64 encoded image data (if `response_format` is `b64_json`).

#### Response Example
```json
{
  "created": 1678886400,
  "data": [
    {
      "url": "https://example.com/image.png",
      "b64_json": "..."
    }
  ]
}
```
```

--------------------------------

### POST /v1/responses - Generate an image with high input fidelity (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=bottle

This Python example demonstrates how to generate an image using the Responses API with high input fidelity. It mirrors the Node.js example, showing the equivalent Python client usage for editing images with preserved details.

```APIDOC
## POST /v1/responses

### Description
Generates an image with high input fidelity, preserving details from input images.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation (e.g., "gpt-4.1").
- **input** (list) - Required - A list of message objects, each with a role and content.
  - **role** (string) - Required - The role of the message sender (e.g., "user").
  - **content** (list) - Required - A list of content blocks.
    - **type** (string) - Required - The type of content (e.g., "input_text", "input_image").
    - **text** (string) - Optional - The text content.
    - **image_url** (dict) - Optional - The URL of the input image.
- **tools** (list) - Required - A list of tool definitions.
  - **type** (string) - Required - The type of tool (e.g., "image_generation").
  - **input_fidelity** (string) - Optional - The input fidelity level (e.g., "high"). Defaults to "low".
  - **action** (string) - Optional - The action to perform (e.g., "edit").

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": [
    {
      "role": "user",
      "content": [
        { "type": "input_text", "text": "Add the logo to the woman's top, as if stamped into the fabric."}, 
        { "type": "input_image", "image_url": "https://cdn.openai.com/API/docs/images/woman_futuristic.jpg" },
        { "type": "input_image", "image_url": "https://cdn.openai.com/API/docs/images/brain_logo.png" }
      ]
    }
  ],
  "tools": [{"type": "image_generation", "input_fidelity": "high", "action": "edit"}]
}
```

### Response
#### Success Response (200)
- **output** (list) - A list of output objects.
  - **type** (string) - The type of output (e.g., "image_generation_call").
  - **result** (string) - The base64 encoded image data.

#### Response Example
```json
{
  "output": [
    { "type": "image_generation_call", "result": "<base64_encoded_image_data>" }
  ]
}
```
```

--------------------------------

### POST /v1/responses - Generate an image with high input fidelity (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=cliffside-portrait

This Python example demonstrates how to generate an image with high input fidelity using the `responses.create` method. It includes setting the `input_fidelity` parameter to `high` for the `image_generation` tool.

```APIDOC
## POST /v1/responses

### Description
Generates an image with high input fidelity, preserving details from input images. This is useful for elements like faces or logos that require accurate preservation.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation (e.g., `gpt-4.1`).
- **input** (list) - Required - A list of message objects, each containing `role` and `content`. Content can include `input_text` and `input_image` objects.
  - **role** (string) - Required - The role of the message sender (`user`).
  - **content** (list) - Required - A list of content parts.
    - **type** (string) - Required - The type of content (`input_text` or `input_image`).
    - **text** (string) - Required if type is `input_text` - The text content.
    - **image_url** (string) - Required if type is `input_image` - The URL of the image.
- **tools** (list) - Required - A list of tool definitions.
  - **type** (string) - Required - The type of tool (`image_generation`).
  - **input_fidelity** (string) - Required - Set to `high` to enable high input fidelity.
  - **action** (string) - Required - The action to perform (`edit`).

### Request Example
```python
{
    "model": "gpt-4.1",
    "input": [
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Add the logo to the woman's top, as if stamped into the fabric."},
                {
                    "type": "input_image",
                    "image_url": "https://cdn.openai.com/API/docs/images/woman_futuristic.jpg",
                },
                {
                    "type": "input_image",
                    "image_url": "https://cdn.openai.com/API/docs/images/brain_logo.png",
                },
            ],
        }
    ],
    "tools": [{"type": "image_generation", "input_fidelity": "high", "action": "edit"}],
}
```

### Response
#### Success Response (200)
- **output** (list) - A list of output objects.
  - **type** (string) - The type of output (`image_generation_call`).
  - **result** (string) - Base64 encoded image data.

#### Response Example
```python
{
    "output": [
        {"type": "image_generation_call", "result": "<base64_encoded_image_data>"}
    ]
}
```
```

--------------------------------

### Edit an image using a mask (inpainting) - Node.js

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=clay-figurine

This example demonstrates how to edit an image using a mask with the OpenAI Node.js client. A mask is provided to indicate which part of the image should be edited, and additional instructions guide the editing process.

```APIDOC
## POST /v1/images/edits

### Description
Edits an image using a mask to specify the area to be modified. The model uses the mask as guidance, and the editing is prompt-based.

### Method
POST

### Endpoint
/v1/images/edits

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for editing. Example: `gpt-image-1`.
- **image** (file) - Required - The image to edit. Must be a PNG image, less than 4MB.
- **mask** (file) - Required - An additional image for the mask. Must be a PNG image, less than 4MB. The transparent index in the mask file will be filled.
- **prompt** (string) - Required - A text description of the desired image modifications.
- **n** (integer) - Optional - The number of edits to generate. Defaults to 1.
- **size** (string) - Optional - The size of the generated images. Must be one of `256x256`, `512x512`, or `1024x1024`.
- **response_format** (string) - Optional - The format in which the generated images are returned. Must be one of `url` or `b64_json`. Defaults to `url`.

### Request Example
```javascript
import fs from "fs";
import OpenAI, { toFile } from "openai";

const client = new OpenAI();

const rsp = await client.images.edit({
    model: "gpt-image-1",
    image: await toFile(fs.createReadStream("sunlit_lounge.png"), null, {
        type: "image/png",
    }),
    mask: await toFile(fs.createReadStream("mask.png"), null, {
        type: "image/png",
    }),
    prompt: "A sunlit indoor lounge area with a pool containing a flamingo",
});

// Save the image to a file
const image_base64 = rsp.data[0].b64_json;
const image_bytes = Buffer.from(image_base64, "base64");
fs.writeFileSync("lounge.png", image_bytes);
```

### Response
#### Success Response (200)
- **created** (integer) - The Unix timestamp of when the edit was created.
- **data** (array) - An array of image objects.
  - **url** (string) - The URL of the generated image (if `response_format` is `url`).
  - **b64_json** (string) - The base64 encoded JSON of the generated image (if `response_format` is `b64_json`).

#### Response Example
```json
{
  "created": 1678886400,
  "data": [
    {
      "url": "https://example.com/image.png",
      "b64_json": "...base64_encoded_image..."
    }
  ]
}
```
```

--------------------------------

### Call GPT-5.1-Codex-Max for High Reasoning Tasks (Python)

Source: https://developers.openai.com/api/docs/guides/code-generation

This Python example shows how to use the GPT-5.1-Codex-Max model for demanding reasoning tasks, like identifying null pointer exceptions. It utilizes the 'openai' library and sets the model and high effort for reasoning.

```python
from openai import OpenAI
client = OpenAI()

result = client.responses.create(
    model="gpt-5.1-codex-max",
    input="Find the null pointer exception: ...your code here...",
    reasoning={ "effort": "high" },
)

print(result.output_text)
```

--------------------------------

### Generate Image using DALL-E 2 (Python and cURL)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=landscape

Code examples for generating images using the DALL-E 2 model via the OpenAI API. Includes examples in Python and cURL, demonstrating prompt, size, and quality parameters.

```python
from openai import OpenAI
client = OpenAI()

result = client.images.generate(
    model="dall-e-2",
    prompt="a white siamese cat",
    size="1024x1024",
    quality="standard",
    n=1,
)

print(result.data[0].url)
```

```curl
curl https://api.openai.com/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "dall-e-2",
    "prompt": "a white siamese cat",
    "n": 1,
    "size": "1024x1024"
  }'
```

--------------------------------

### List Run Steps using Python, Node.js, and cURL

Source: https://developers.openai.com/api/docs/assistants/tools/code-interpreter

Demonstrates how to retrieve a list of run steps for a specific thread and run ID. This is essential for monitoring the execution progress of an assistant and understanding the sequence of actions taken, including code interpreter usage. Examples are provided for Python, Node.js, and cURL.

```python
run_steps = client.beta.threads.runs.steps.list(
  thread_id=thread.id,
  run_id=run.id
)
```

```node.js
const runSteps = await openai.beta.threads.runs.steps.list(
  thread.id,
  run.id
);
```

```curl
curl https://api.openai.com/v1/threads/thread_abc123/runs/RUN_ID/steps \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2" \
```

--------------------------------

### Create Custom Tool for Code Execution (Python)

Source: https://developers.openai.com/api/docs/guides/function-calling_api-mode=chat

This Python example demonstrates creating a custom tool named 'code_exec' that allows the model to execute arbitrary Python code. The response from the model will contain the code to be executed.

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5",
    input="Use the code_exec tool to print hello world to the console.",
    tools=[
        {
            "type": "custom",
            "name": "code_exec",
            "description": "Executes arbitrary Python code.",
        }
    ]
)
print(response.output)
```

--------------------------------

### Analyze Content with Uploaded File

Source: https://developers.openai.com/api/docs/quickstart

Upload a file first and then use its ID to send it to the model for analysis. This is suitable for files stored locally or requiring pre-processing.

```APIDOC
## POST /v1/files

### Description
Uploads a file to be used with the OpenAI API.

### Method
POST

### Endpoint
https://api.openai.com/v1/files

### Parameters
#### Query Parameters
- **purpose** (string) - Required - The purpose of the file (e.g., "user_data").

#### Form Data
- **file** (file) - Required - The file to upload.

### Request Example
```bash
curl https://api.openai.com/v1/files \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -F purpose="user_data" \
    -F file="@draconomicon.pdf"
```

## POST /v1/responses

### Description
Analyzes content from an uploaded file using its file ID.

### Method
POST

### Endpoint
https://api.openai.com/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for analysis (e.g., "gpt-5").
- **input** (array) - Required - An array of input objects, typically containing user messages.
  - **role** (string) - Required - The role of the message sender (e.g., "user").
  - **content** (array) - Required - An array of content parts for the message.
    - **type** (string) - Required - The type of content (e.g., "input_text", "input_file").
    - **file_id** (string) - Required if type is "input_file" - The ID of the uploaded file.
    - **text** (string) - Required if type is "input_text" - The text content.

### Request Example
```json
{
    "model": "gpt-5",
    "input": [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_file",
                    "file_id": "file-6F2ksmvXxt4VdoqmHRw6kL"
                },
                {
                    "type": "input_text",
                    "text": "What is the first dragon in the book?"
                }
            ]
        }
    ]
}
```

### Response
#### Success Response (200)
- **output_text** (string) - The analysis result from the model.
```

--------------------------------

### Image Generation with Transparent Background (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=wedding-portrait

This example demonstrates how to generate an image with a transparent background using the OpenAI Python client library. It utilizes the `responses.create` method with the `image_generation` tool and specifies `background='transparent'` and `quality='high'`.

```APIDOC
## POST /v1/responses

### Description
Generates an image with a transparent background using the `responses.create` method.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for image generation (e.g., "gpt-5").
- **input** (string) - Required - The prompt describing the image to generate.
- **tools** (array) - Required - A list of tools to use. For image generation, include an object with `type: "image_generation"`, `background: "transparent"`, and `quality: "high"`.

### Request Example
```json
{
  "model": "gpt-5",
  "input": "Draw a 2D pixel art style sprite sheet of a tabby gray cat",
  "tools": [
    {
      "type": "image_generation",
      "background": "transparent",
      "quality": "high"
    }
  ]
}
```

### Response
#### Success Response (200)
- **output** (array) - A list of outputs, where each object with `type: "image_generation_call"` contains the base64 encoded image data in the `result` field.

#### Response Example
```json
{
  "output": [
    {
      "type": "image_generation_call",
      "result": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    }
  ]
}
```
```

--------------------------------

### Download Supporting Assets

Source: https://developers.openai.com/api/docs/guides/video-generation_gallery=open&galleryItem=maui

In addition to the main video, you can download supporting assets like thumbnails and spritesheets using the `variant` query parameter.

```APIDOC
## GET /videos/{video_id}/content?variant={asset_type}

### Description
Downloads supporting assets for a completed video generation job, such as a thumbnail or a spritesheet.

### Method
GET

### Endpoint
`/videos/{video_id}/content`

### Parameters
#### Path Parameters
- **video_id** (string) - Required - The unique identifier of the video job.

#### Query Parameters
- **variant** (string) - Required - Specifies the asset to download. Accepted values are `video` (default), `thumbnail`, and `spritesheet`.

### Request Example (cURL for Thumbnail)
```bash
curl -L "https://api.openai.com/v1/videos/video_abc123/content?variant=thumbnail" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  --output thumbnail.webp
```

### Request Example (cURL for Spritesheet)
```bash
curl -L "https://api.openai.com/v1/videos/video_abc123/content?variant=spritesheet" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  --output spritesheet.jpg
```

### Response
#### Success Response (200)
Streams the binary data for the requested asset (e.g., WebP for thumbnail, JPG for spritesheet).
```

--------------------------------

### Chat Completions with JSON Schema

Source: https://developers.openai.com/api/docs/guides/structured-outputs_context=with_parse

This endpoint demonstrates how to use the `response_format` parameter with `json_schema` to guide the model to output data conforming to a specified JSON schema. It includes examples for Python, Node.js, and cURL.

```APIDOC
## POST /v1/chat/completions

### Description
This endpoint allows you to generate chat completions from the OpenAI API. By specifying `response_format` with a `json_schema`, you can instruct the model to return output that strictly adheres to the provided schema.

### Method
POST

### Endpoint
`/v1/chat/completions`

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use for completion.
- **messages** (array) - Required - A list of messages comprising the conversation.
- **response_format** (object) - Optional - Specifies the format for the response. Should be an object with `type` set to `"json_schema"` and `json_schema` containing the schema definition.
  - **type** (string) - Required - Must be `"json_schema"`.
  - **json_schema** (object) - Required - The JSON schema object defining the desired output structure.
    - **name** (string) - Required - A name for the schema.
    - **schema** (object) - Required - The actual JSON schema.
    - **strict** (boolean) - Required - If true, the model will error if it cannot generate valid JSON according to the schema.

### Request Example (Python)
```python
response = client.chat.completions.create(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "You are a helpful math tutor. Guide the user through the solution step by step."},
        {"role": "user", "content": "how can I solve 8x + 7 = -23"}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "math_response",
            "schema": {
                "type": "object",
                "properties": {
                    "steps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "explanation": {"type": "string"},
                                "output": {"type": "string"}
                            },
                            "required": ["explanation", "output"],
                            "additionalProperties": False
                        }
                    },
                    "final_answer": {"type": "string"}
                },
                "required": ["steps", "final_answer"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
)

print(response.choices[0].message.content)
```

### Request Example (Node.js)
```javascript
const response = await openai.chat.completions.create({
model: "gpt-4o-2024-08-06",
messages: [
{ role: "system", content: "You are a helpful math tutor. Guide the user through the solution step by step." },
{ role: "user", content: "how can I solve 8x + 7 = -23" }
],
response_format: {
type: "json_schema",
json_schema: {
name: "math_response",
schema: {
type: "object",
properties: {
steps: {
type: "array",
items: {
type: "object",
properties: {
explanation: { type: "string" },
output: { type: "string" }
},
required: ["explanation", "output"],
additionalProperties: false
}
},
final_answer: { type: "string" }
},
required: ["steps", "final_answer"],
additionalProperties: false
},
strict: true
}
}
});

console.log(response.choices[0].message.content);
```

### Request Example (cURL)
```bash
curl https://api.openai.com/v1/chat/completions \
-H "Authorization: Bearer $OPENAI_API_KEY" \
-H "Content-Type: application/json" \
-d '{
"model": "gpt-4o-2024-08-06",
"messages": [
{
"role": "system",
"content": "You are a helpful math tutor. Guide the user through the solution step by step."
},
{
"role": "user",
"content": "how can I solve 8x + 7 = -23"
}
],
"response_format": {
"type": "json_schema",
"json_schema": {
"name": "math_response",
"schema": {
"type": "object",
"properties": {
"steps": {
"type": "array",
"items": {
"type": "object",
"properties": {
"explanation": { "type": "string" },
"output": { "type": "string" }
},
"required": ["explanation", "output"],
"additionalProperties": false
}
},
"final_answer": { "type": "string" }
},
"required": ["steps", "final_answer"],
"additionalProperties": false
},
"strict": true
}
}
}'
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the completion.
- **object** (string) - Type of object returned, e.g., `chat.completion`.
- **created** (integer) - Unix timestamp of when the completion was created.
- **model** (string) - The model used for the completion.
- **choices** (array) - A list of completion choices.
  - **index** (integer) - Index of the choice.
  - **message** (object) - The message content.
    - **role** (string) - Role of the author, e.g., `assistant`.
    - **content** (string) - The content of the message, formatted according to the specified JSON schema.
  - **logprobs** (null) - Null, as logprobs are not typically returned for structured outputs.
- **usage** (object) - Usage statistics for the request.
  - **prompt_tokens** (integer) - Number of tokens in the prompt.
  - **completion_tokens** (integer) - Number of tokens in the completion.
  - **total_tokens** (integer) - Total tokens used.

#### Response Example
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "gpt-4o-2024-08-06",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "{\"steps\": [{\"explanation\": \"Subtract 7 from both sides of the equation.\", \"output\": \"8x = -30\"}, {\"explanation\": \"Divide both sides by 8.\", \"output\": \"x = -3.75\"}], \"final_answer\": \"x = -3.75\"}"
      },
      "logprobs": null
    }
  ],
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 60,
    "total_tokens": 110
  }
}
```
```

--------------------------------

### Image API - Stream an image (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=solar-roof

This example demonstrates how to stream image generation using the Image API in Python. It shows how to handle partial images as they are generated and save them to files.

```APIDOC
## POST /v1/images/generations

### Description
Streams image generation results, allowing for partial image retrieval during the generation process.

### Method
POST

### Endpoint
/v1/images/generations

### Parameters
#### Query Parameters
- **stream** (boolean) - Required - Set to `true` to enable streaming.
- **partial_images** (integer) - Optional - The number of partial images to receive (0-3). If set to 0, only the final image is returned. If the full image is generated quickly, fewer partial images than requested may be returned.

#### Request Body
- **prompt** (string) - Required - The text prompt for image generation.
- **model** (string) - Required - The model to use for image generation (e.g., "gpt-image-1").

### Request Example
```python
client.images.generate(
    prompt="Draw a gorgeous image of a river made of white owl feathers, snaking its way through a serene winter landscape",
    model="gpt-image-1",
    stream=True,
    partial_images=2,
)
```

### Response
#### Success Response (200)
- **event** (object) - An event object representing a part of the generation process.
  - **type** (string) - The type of event (e.g., `image_generation.partial_image`).
  - **partial_image_index** (integer) - The index of the partial image.
  - **b64_json** (string) - The base64 encoded partial image data.

#### Response Example
```python
{
    "type": "image_generation.partial_image",
    "partial_image_index": 0,
    "b64_json": "/9j/4AAQSkZJRgABAQ...
}
```
```

--------------------------------

### Edit an image using a mask (inpainting) - Python

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=abstract-orbit

This example demonstrates how to edit an image using a mask with the OpenAI Python client. You provide an input image and a mask image to specify the area to be edited, along with a text prompt guiding the changes.

```APIDOC
## POST /v1/images/edits

### Description
Edits an image based on a provided mask and prompt. The mask indicates which part of the image should be edited.

### Method
POST

### Endpoint
/v1/images/edits

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for image editing (e.g., "gpt-image-1").
- **image** (file) - Required - The image to edit. Must be a PNG image, less than 4MB.
- **mask** (file) - Required - The mask image. Must be a PNG image, less than 4MB. The transparent areas of the mask indicate where the image should be edited.
- **prompt** (string) - Required - A text description of the desired image.
- **n** (integer) - Optional - The number of images to generate. Must be between 1 and 10.
- **size** (string) - Optional - The size of the generated images. Must be one of "256x256", "512x512", or "1024x1024".
- **response_format** (string) - Optional - The format in which the generated images are returned. Must be one of `url` or `b64_json`.

### Request Example
```python
from openai import OpenAI
client = OpenAI()

result = client.images.edit(
    model="gpt-image-1",
    image=open("sunlit_lounge.png", "rb"),
    mask=open("mask.png", "rb"),
    prompt="A sunlit indoor lounge area with a pool containing a flamingo"
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("composition.png", "wb") as f:
    f.write(image_bytes)
```

### Response
#### Success Response (200)
- **created** (integer) - The Unix timestamp of when the image was created.
- **data** (array) - An array of image objects.
  - **url** (string) - The URL of the generated image (if `response_format` is `url`).
  - **b64_json** (string) - The base64 encoded JSON of the generated image (if `response_format` is `b64_json`).

#### Response Example
```json
{
  "created": 1678887777,
  "data": [
    {
      "url": "https://example.com/image.png",
      "b64_json": "..."
    }
  ]
}
```
```

--------------------------------

### OpenAPI Specification for Inline File Upload

Source: https://developers.openai.com/api/docs/actions/sending-files

An OpenAPI specification example detailing the 'findPapers' GET endpoint. It shows how to define the 'topic' query parameter and the 'openaiFileResponse' in the 200 OK response, which expects an array of objects containing file name, MIME type, and base64 content.

```yaml
/papers:
  get:
    operationId: findPapers
    summary: Retrieve PDFs of relevant academic papers.
    description: Provided an academic topic, up to five relevant papers will be returned as PDFs.
    parameters:
      - in: query
        name: topic
        required: true
        schema:
          type: string
        description: The topic the papers should be about.
    responses:
      "200":
        description: Zero to five academic paper PDFs
        content:
          application/json:
            schema:
              type: object
              properties:
                openaiFileResponse:
                  type: array
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                        description: The name of the file.
                      mime_type:
                        type: string
                        description: The MIME type of the file.
                      content:
                        type: string
                        format: byte
                        description: The content of the file in base64 encoding.
```

--------------------------------

### Example of Assistants API Server-Sent Events Stream

Source: https://developers.openai.com/api/docs/api-reference/assistants

This example demonstrates the structure of events received when streaming data from the Assistants API. Each event includes an 'event' type and 'data' payload, which can vary based on the action occurring (e.g., thread creation, run updates).

```text
event: thread.created
data: {"id": "thread_123", "object": "thread", ...}

```

--------------------------------

### Function Calling with OpenAI API

Source: https://developers.openai.com/api/docs/guides/tools_api-mode=responses

Implement function calling to allow the model to invoke your custom functions. Define the function's name, description, and parameters. This example shows how to get weather information.

```javascript
import OpenAI from "openai";
const client = new OpenAI();

const tools = [
    {
        type: "function",
        name: "get_weather",
        description: "Get current temperature for a given location.",
        parameters: {
            type: "object",
            properties: {
                location: {
                    type: "string",
                    description: "City and country e.g. Bogotá, Colombia",
                },
            },
            required: ["location"],
            additionalProperties: false,
        },
        strict: true,
    },
];

const response = await client.responses.create({
    model: "gpt-5",
    input: [
        { role: "user", content: "What is the weather like in Paris today?" },
    ],
    tools,
});

console.log(response.output[0].to_json());
```

```python
from openai import OpenAI

client = OpenAI()

tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get current temperature for a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and country e.g. Bogotá, Colombia"
                }
            },
            "required": ["location"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

response = client.responses.create(
    model="gpt-5",
    input=[
        {"role": "user", "content": "What is the weather like in Paris today?"},
    ],

```

--------------------------------

### Image API - Stream an image (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=school-lab

This example demonstrates how to stream image generation using the Image API in Python. It shows how to set the `partial_images` parameter and process the streamed partial images.

```APIDOC
## POST /v1/images/generations/stream

### Description
Streams image generation results from the Image API, allowing for partial image delivery during the generation process.

### Method
POST

### Endpoint
/v1/images/generations/stream

### Parameters
#### Query Parameters
- **stream** (boolean) - Required - Set to `True` to enable streaming.
- **partial_images** (integer) - Optional - The number of partial images to receive (0-3). If set to 0, only the final image is returned. If the full image is generated quickly, fewer partial images than requested may be returned.

#### Request Body
- **prompt** (string) - Required - The text prompt for image generation.
- **model** (string) - Required - The image generation model to use (e.g., "gpt-image-1").

### Request Example
```python
{
    "prompt": "Draw a gorgeous image of a river made of white owl feathers, snaking its way through a serene winter landscape",
    "model": "gpt-image-1",
    "stream": True,
    "partial_images": 2
}
```

### Response
#### Success Response (200)
- **event.type** (string) - The type of event received (e.g., "image_generation.partial_image").
- **event.partial_image_index** (integer) - The index of the partial image.
- **event.b64_json** (string) - The base64 encoded partial image data.

#### Response Example
```json
{
  "type": "image_generation.partial_image",
  "partial_image_index": 0,
  "b64_json": "...base64_encoded_image_data..."
}
```
```

--------------------------------

### Using the 'instructions' parameter

Source: https://developers.openai.com/api/docs/guides/prompt-engineering

This section demonstrates how to use the 'instructions' parameter to provide high-level guidance to the model, which takes priority over the 'input' parameter.

```APIDOC
## POST /v1/responses

### Description
Sends a request to the OpenAI API to generate text with specific instructions.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation (e.g., "gpt-5").
- **reasoning** (object) - Required - Specifies the reasoning effort (e.g., `{"effort": "low"}`).
- **instructions** (string) - Required - High-level instructions for the model's behavior.
- **input** (string) - Required - The prompt or input text for the model.

### Request Example
```json
{
    "model": "gpt-5",
    "reasoning": {"effort": "low"},
    "instructions": "${semicolonsDevMsg}",
    "input": "${semicolonsPrompt}"
}
```

### Response
#### Success Response (200)
- **output_text** (string) - The generated text output from the model.

#### Response Example
```json
{
    "output_text": "Generated text based on instructions and input."
}
```
```

--------------------------------

### Analyze Image from Stream or Byte Array (C#)

Source: https://developers.openai.com/api/docs/guides/images-vision_api-mode=responses

This C# example demonstrates analyzing an image by downloading it as a stream or byte array from a URL and sending it to the OpenAI API. It utilizes the 'OpenAI.Responses' namespace and requires an API key. The input is a URL to an image, and the output is the model's textual analysis.

```csharp
using OpenAI.Responses;
using System;
using System.Net.Http;
using System.Threading.Tasks;

string key = Environment.GetEnvironmentVariable("OPENAI_API_KEY")!;
OpenAIResponseClient client = new(model: "gpt-5", apiKey: key);

Uri imageUrl = new("https://openai-documentation.vercel.app/images/cat_and_otter.png");
using HttpClient http = new();

// Download an image as stream
using var stream = await http.GetStreamAsync(imageUrl);

OpenAIResponse response1 = (OpenAIResponse)client.CreateResponse([
    ResponseItem.CreateUserMessageItem([
        ResponseContentPart.CreateInputTextPart("What is in this image?"),
        ResponseContentPart.CreateInputImagePart(BinaryData.FromStream(stream), "image/png")
    ])
]);

Console.WriteLine($"From image stream: {response1.GetOutputText()}");

// Download an image as byte array
byte[] bytes = await http.GetByteArrayAsync(imageUrl);

OpenAIResponse response2 = (OpenAIResponse)client.CreateResponse([
    ResponseItem.CreateUserMessageItem([
        ResponseContentPart.CreateInputTextPart("What is in this image?"),
        ResponseContentPart.CreateInputImagePart(BinaryData.FromBytes(bytes), "image/png")
    ])
]);

Console.WriteLine($"From byte array: {response2.GetOutputText()}")
```

--------------------------------

### Chat Completion API Example

Source: https://developers.openai.com/api/docs/guides/embeddings

This snippet shows how to use the Chat Completions API to get a response from a GPT model. It sets up a system message to define the model's behavior and a user query, then prints the model's response.

```python
response = client.chat.completions.create(
    messages=[
        {'role': 'system', 'content': 'You answer questions about the 2022 Winter Olympics.'},
        {'role': 'user', 'content': query},
    ],
    model=GPT_MODEL,
    temperature=0,
)

print(response.choices[0].message.content)
```

--------------------------------

### Migration Guidance and Parameter Compatibility

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=holiday-card-for-kids-5.2

Information on migrating from older models to GPT-5.2 and details on parameter compatibility, especially concerning reasoning effort.

```APIDOC
## GPT-5.2 Model Migration and Parameter Usage

### Description
This section provides guidance on migrating from older OpenAI models to GPT-5.2 and outlines parameter compatibility, particularly when using different `reasoning.effort` settings.

### Method
(Applies to POST requests to chat completion endpoints)

### Endpoint
/v1/chat/completions

### Parameters
#### Request Body Parameters (GPT-5.2 Specific)
- **reasoning** (object) - Optional - Controls the reasoning effort.
  - **effort** (string) - Required - One of: `none`, `low`, `medium`, `high`, `xhigh`.
- **text** (object) - Optional - Controls output verbosity.
  - **verbosity** (string) - Required - One of: `low`, `medium`, `high`.
- **max_output_tokens** (integer) - Optional - Maximum number of tokens to generate.

#### Parameters ONLY Supported with `reasoning.effort: "none"`
- **temperature** (number)
- **top_p** (number)
- **logprobs** (integer)

### Migration Notes
- **gpt-5.1**: `gpt-5.2` with default settings is a drop-in replacement.
- **o3**: Use `gpt-5.2` with `medium` or `high` reasoning. Start with `medium` and tune prompts.
- **gpt-4.1**: Use `gpt-5.2` with `none` reasoning. Start with `none` and tune prompts.
- **o4-mini / gpt-4.1-mini**: Migrate to `gpt-5-mini` with prompt tuning.
- **gpt-4.1-nano**: Migrate to `gpt-5-nano` with prompt tuning.

### Error Handling
Requests to GPT-5.2 or GPT-5.1 with unsupported parameters (e.g., `temperature` when `reasoning.effort` is not `none`) will raise an error.

### Alternatives for Higher Reasoning Effort or Other GPT-5 Models
- Use `reasoning: { effort: "..." }` for reasoning depth.
- Use `text: { verbosity: "..." }` for output verbosity.
- Use `max_output_tokens` for output length control.
```

--------------------------------

### Handling JSON Schema Responses in Python

Source: https://developers.openai.com/api/docs/guides/structured-outputs_api-mode=responses

This Python example illustrates how to use the OpenAI client library to obtain structured responses conforming to a JSON schema. It includes the necessary setup for messages and the response format, along with basic error handling.

```python
try:
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful math tutor. Guide the user through the solution step by step.",
            },
            {"role": "user", "content": "how can I solve 8x + 7 = -23"},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "math_response",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "explanation": {"type": "string"},
                                    "output": {"type": "string"}
                                },
                                "required": ["explanation", "output"],
                                "additionalProperties": False
                            },
                        },
                        "final_answer": {"type": "string"}
                    },
                    "required": ["steps", "final_answer"],
                    "additionalProperties": False
                },
            },
        },
        max_tokens=50,
    )

    # Process the response
    if response.choices[0].finish_reason == "length":
        print("Incomplete response")
    else:
        math_response = response.choices[0].message
        if hasattr(math_response, 'refusal') and math_response.refusal:
            print(math_response.refusal)
        elif hasattr(math_response, 'content') and math_response.content:
            print(math_response.content)
        else:
            print("No response content")

except Exception as e:
    # Handle edge cases
    print(f"An error occurred: {e}")
```

--------------------------------

### Few-Shot Learning Example for Sentiment Analysis (Developer Message)

Source: https://developers.openai.com/api/docs/guides/prompt-engineering

This example illustrates a developer message used for few-shot learning. It defines the assistant's identity, provides instructions for sentiment classification, and includes examples of product reviews with their corresponding labels (Positive, Negative, Neutral).

```plaintext
# Identity

You are a helpful assistant that labels short product reviews as
Positive, Negative, or Neutral.

# Instructions

* Only output a single word in your response with no additional formatting
  or commentary.
* Your response should only be one of the words "Positive", "Negative", or
  "Neutral" depending on the sentiment of the product review you are given.


```

--------------------------------

### Upload File and Get Chat Completion using Node.js

Source: https://developers.openai.com/api/docs/guides/pdf-files_api-mode=responses

This Node.js example demonstrates uploading a PDF file using the OpenAI SDK and then using the file ID in a request to the chat completions endpoint. It requires the 'openai' npm package and an environment variable OPENAI_API_KEY.

```javascript
import fs from "fs";
import OpenAI from "openai";
const client = new OpenAI();

const file = await client.files.create({
    file: fs.createReadStream("draconomicon.pdf"),
    purpose: "user_data",
});

const completion = await client.chat.completions.create({
    model: "gpt-5",
    messages: [
        {
            role: "user",
            content: [
                {
                    type: "file",
                    file: {
                        file_id: file.id,
                    }
                },
                {
                    type: "text",
                    text: "What is the first dragon in the book?",
                },
            ],
        },
    ],
});

console.log(completion.choices[0].message.content);
```

--------------------------------

### OpenAPI Specification for URL File Upload

Source: https://developers.openai.com/api/docs/actions/sending-files

An OpenAPI specification example for the 'findPapers' GET endpoint using URL-based file retrieval. The 'openaiFileResponse' in the 200 OK response is defined as an array of strings, where each string is a URI pointing to a file.

```yaml
/papers:
  get:
    operationId: findPapers
    summary: Retrieve PDFs of relevant academic papers.
    description: Provided an academic topic, up to five relevant papers will be returned as PDFs.
    parameters:
      - in: query
        name: topic
        required: true
        schema:
          type: string
        description: The topic the papers should be about.
    responses:
      '200':
        description: Zero to five academic paper PDFs
        content:
            application/json:
              schema:
                type: object
                properties:
                  openaiFileResponse:
                    type: array
                    items:
                    type: string
                    format: uri
                    description: URLs to fetch the files.
```

--------------------------------

### Preamble Configuration

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=holiday-card-for-kids-5.2

Enable preambles to generate user-visible explanations before tool invocation, improving transparency and debuggability.

```APIDOC
## System/Developer Instruction for Preambles

### Description
To enable preambles, which are explanations of the model's intent before tool calls, include a specific instruction in the system or developer message.

### Method
(Applies to POST requests to chat completion endpoints)

### Endpoint
/v1/chat/completions

### Parameters
#### Request Body (System/Developer Message)
- **role** (string) - Must be `system` or `developer`.
- **content** (string) - Instruction text, e.g., "Before you call a tool, explain why you are calling it."

### Request Example
```json
{
  "model": "gpt-5.2",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant. Before you call a tool, explain why you are calling it."}, 
    {"role": "user", "content": "What's the weather like in London?"}
  ]
}
```

### Response
#### Success Response (200)
- The response may include a preamble explaining the tool call before the actual tool call is presented.

#### Response Example
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "I need to call the get_weather tool to find out the weather in London.",
        "tool_calls": [
          {
            "id": "call_xyz789",
            "type": "function",
            "function": {
              "name": "get_weather",
              "arguments": "{\"location\": \"London\"}"
            }
          }
        ]
      }
    }
  ]
}
```
```

--------------------------------

### Create Audio Transcription with Word Timestamps (HTTP)

Source: https://developers.openai.com/api/docs/api-reference/audio/createTranscription

This example demonstrates how to create an audio transcription using the OpenAI API with word-level timestamp granularities. It requires an audio file and an API key. The response includes the transcribed text and detailed word timings.

```curl
curl https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F file="@/path/to/file/audio.mp3" \
  -F "timestamp_granularities[]=word" \
  -F model="whisper-1" \
  -F response_format="verbose_json"

```

```json
{
  "task": "transcribe",
  "language": "english",
  "duration": 8.470000267028809,
  "text": "The beach was a popular spot on a hot summer day. People were swimming in the ocean, building sandcastles, and playing beach volleyball.",
  "words": [
    {
      "word": "The",
      "start": 0.0,
      "end": 0.23999999463558197
    },
    ...
    {
      "word": "volleyball",
      "start": 7.400000095367432,
      "end": 7.900000095367432
    }
  ],
  "usage": {
    "type": "duration",
    "seconds": 9
  }
}

```

--------------------------------

### Chat Completions API - Sequential Jokes Example

Source: https://developers.openai.com/api/docs/guides/conversation-state_api-mode=responses

This example shows how to maintain conversation context across multiple requests to the Chat Completions API, allowing for more natural, sequential interactions.

```APIDOC
## POST /v1/chat/completions (Sequential Interaction)

### Description
Manually manage conversation state by appending previous assistant responses and new user prompts to the message history for subsequent API calls. This ensures the model retains context from earlier turns.

### Method
POST

### Endpoint
/v1/chat/completions

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use for completion.
- **messages** (array) - Required - A list of messages comprising the conversation so far, including previous user inputs and assistant responses.
  - **role** (string) - Required - The role of the author of a message (e.g., `system`, `user`, or `assistant`).
  - **content** (string) - Required - The content of the message.

### Request Example
```json
// First request
{
  "model": "gpt-4o-mini",
  "messages": [
    { "role": "user", "content": "tell me a joke" }
  ]
}

// Second request (after receiving and processing the first response)
{
  "model": "gpt-4o-mini",
  "messages": [
    { "role": "user", "content": "tell me a joke" },
    { "role": "assistant", "content": "Why don't scientists trust atoms? Because they make up everything!"
    }, 
    { "role": "user", "content": "tell me another" }
  ]
}
```

### Response
#### Success Response (200)
- **choices** (array) - The list of completion choices for the prompt.
  - **message** (object) - Represents a message in the conversation.
    - **role** (string) - The role of the author of the message.
    - **content** (string) - The content of the message.

#### Response Example
```json
// Response to the first request
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Why don't scientists trust atoms? Because they make up everything!"
      }
    }
  ]
}

// Response to the second request
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "What do you call a lazy kangaroo? Pouch potato!"
      }
    }
  ]
}
```
```

--------------------------------

### Setting up a Local Browsing Environment

Source: https://developers.openai.com/api/docs/guides/tools-computer-use

Instructions for setting up a local browsing environment using Playwright or Selenium for the Computer Use API.

```APIDOC
## Setting up a Local Browsing Environment

### Description
Prepare an environment capable of capturing screenshots and executing actions. Using a browser automation framework like Playwright or Selenium is recommended for minimal setup. Security risks can be mitigated by using a sandboxed environment, setting `env` to an empty object, and disabling extensions and the file system.

### Playwright SDK Installation

- **Python:** `pip install playwright`
- **JavaScript:** `npm i playwright` then `npx playwright install`

### Example Code (Conceptual)

```javascript
// Example for starting a Playwright browser instance (JavaScript)
const { chromium } = require('playwright');

async function startBrowser() {
  const browser = await chromium.launch({
    headless: false, // Set to true for non-visual execution
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-extensions',
      '--disable-web-security'
    ]
  });
  const page = await browser.newPage();
  await page.goto('about:blank'); // Navigate to a blank page initially
  // ... further setup and interaction logic
  return { browser, page };
}

// To be integrated with the Computer Use API loop
// startBrowser().then(({ browser, page }) => { /* ... */ });
```

### Security Recommendations
- Use a sandboxed environment.
- Set `env` to an empty object (`{}`) to prevent exposing host environment variables.
- Use flags to disable extensions and the file system.
```

--------------------------------

### Analyze Image with URL (cURL)

Source: https://developers.openai.com/api/docs/guides/images-vision_api-mode=responses

Analyzes an image from a URL using a cURL command. This example sends a POST request to the OpenAI API with the image URL specified in the JSON payload. It requires `curl` and an OpenAI API key.

```shell
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{ 
    "model": "gpt-4.1-mini", 
    "messages": [
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "what is in this image?"},
          {
            "type": "image_url",
            "image_url": {
              "url": "https://api.nga.gov/iiif/a2e6da57-3cd1-4235-b20e-95dcaefed6c8/full/!800,800/0/default.jpg"
            }
          }
        ]
      }
    ],
    "max_tokens": 300
  }'
```

--------------------------------

### Analyze Image with URL (Node.js)

Source: https://developers.openai.com/api/docs/guides/images-vision_api-mode=responses

Analyzes an image provided via a URL using the OpenAI Node.js client. This example demonstrates how to construct a request with an image URL within the `content` array. It requires the `openai` npm package.

```javascript
import OpenAI from "openai";

const openai = new OpenAI();

async function analyzeImageFromUrl() {
  const response = await openai.chat.completions.create({
    model: "gpt-4.1-mini",
    messages: [
      {
        role: "user",
        content: [
          { type: "text", text: "what's in this image?" },
          {
            type: "image_url",
            image_url: {
              url: "https://api.nga.gov/iiif/a2e6da57-3cd1-4235-b20e-95dcaefed6c8/full/!800,800/0/default.jpg",
            },
          },
        ],
      }
    ],
    max_tokens: 300,
  });

  console.log(response.choices[0].message.content);
}

analyzeImageFromUrl();
```

--------------------------------

### POST /v1/chat/completions - Custom Tools

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=artisan-csa

This example shows how to use custom tools with the Chat Completions API.

```APIDOC
## POST /v1/chat/completions - Custom Tools

### Description
This endpoint allows for custom tool integration within chat completions.

### Method
POST

### Endpoint
/v1/chat/completions

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation.
- **messages** (array) - Required - An array of message objects.
  - **role** (string) - Required - The role of the message (e.g., "user").
  - **content** (string) - Required - The content of the message.
- **tools** (array) - Optional - An array of tool definitions.
  - **type** (string) - Required - The type of tool (e.g., "custom").
  - **custom** (object) - Required - Custom tool configuration.
    - **name** (string) - Required - The name of the custom tool.
    - **description** (string) - Required - A description of the tool's functionality.

### Request Example
```json
{
  "model": "gpt-5.2",
  "messages": [
    { "role": "user", "content": "Use the code_exec tool to calculate the area of a circle with radius equal to the number of r letters in blueberry" }
  ],
  "tools": [
    {
      "type": "custom",
      "custom": {
        "name": "code_exec",
        "description": "Executes arbitrary python code"
      }
    }
  ]
}
```

### Response
#### Success Response (200)
- **choices** (array) - An array of completion choices.
  - **message** (object) - The message object.
    - **content** (string) - The content of the message, potentially including tool calls.

#### Response Example
```json
{
  "choices": [
    {
      "message": {
        "content": "The area of the circle is..."
      }
    }
  ]
}
```
```

--------------------------------

### Chat Completions with JSON Schema Response

Source: https://developers.openai.com/api/docs/guides/structured-outputs_context=with_parse

This section demonstrates how to use the OpenAI API to get chat completions, specifically requesting a JSON schema formatted response for a math problem. It includes examples in cURL, JavaScript (Node.js), and Python.

```APIDOC
## POST /v1/responses

### Description
This endpoint allows you to send a chat prompt to the OpenAI API and receive a structured response formatted according to a specified JSON schema. It's particularly useful for tasks requiring predictable output formats, such as step-by-step mathematical solutions.

### Method
POST

### Endpoint
`https://api.openai.com/v1/responses`

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use for completion (e.g., `gpt-4o-2024-08-06`).
- **input** (array) - Required - An array of message objects, each with a `role` (system or user) and `content`.
- **text** (object) - Required - Specifies the desired output format.
  - **format** (object) - Required - Details of the format.
    - **type** (string) - Required - The type of format, e.g., `json_schema`.
    - **name** (string) - Required - The name of the schema.
    - **schema** (object) - Required - The JSON schema definition.
      - **type** (string) - Required - The root type of the schema (e.g., `object`).
      - **properties** (object) - Required - Defines the properties of the object.
        - **steps** (object) - Required - An array of steps.
          - **type** (string) - Required - `array`.
          - **items** (object) - Required - Defines the structure of each item in the array.
            - **type** (string) - Required - `object`.
            - **properties** (object) - Required - Properties of each step object.
              - **explanation** (object) - Required - Description of the step.
                - **type** (string) - Required - `string`.
              - **output** (object) - Required - The result of the step.
                - **type** (string) - Required - `string`.
            - **required** (array) - Required - List of required properties for each item (`explanation`, `output`).
            - **additionalProperties** (boolean) - Required - `false`.
        - **final_answer** (object) - Required - The final answer to the problem.
          - **type** (string) - Required - `string`.
      - **required** (array) - Required - List of required properties for the root object (`steps`, `final_answer`).
      - **additionalProperties** (boolean) - Required - `false`.
    - **strict** (boolean) - Required - Whether to enforce strict schema adherence.

### Request Example (cURL)
```bash
curl https://api.openai.com/v1/responses \
-H "Authorization: Bearer $OPENAI_API_KEY" \
-H "Content-Type: application/json" \
-d '{
"model": "gpt-4o-2024-08-06",
"input": [
{
"role": "system",
"content": "You are a helpful math tutor. Guide the user through the solution step by step."
},
{
"role": "user",
"content": "how can I solve 8x + 7 = -23"
}
],
"text": {
"format": {
"type": "json_schema",
"name": "math_response",
"schema": {
"type": "object",
"properties": {
"steps": {
"type": "array",
"items": {
"type": "object",
"properties": {
"explanation": { "type": "string" },
"output": { "type": "string" }
},
"required": ["explanation", "output"],
"additionalProperties": false
}
},
"final_answer": { "type": "string" }
},
"required": ["steps", "final_answer"],
"additionalProperties": false
},
"strict": true
}
}
}'
```

### Response
#### Success Response (200)
Returns a JSON object containing the structured response based on the provided schema.

#### Response Example
```json
{
  "steps": [
    {
      "explanation": "Subtract 7 from both sides of the equation.",
      "output": "8x = -23 - 7"
    },
    {
      "explanation": "Simplify the right side.",
      "output": "8x = -30"
    },
    {
      "explanation": "Divide both sides by 8.",
      "output": "x = -30 / 8"
    },
    {
      "explanation": "Simplify the fraction.",
      "output": "x = -15 / 4"
    }
  ],
  "final_answer": "x = -15/4"
}
```

### Error Handling
- **Incomplete Response**: If the model does not return a complete response (e.g., due to `max_tokens` limit), an error should be handled.
- **Refusal**: If the model refuses to answer for safety reasons, the response might contain a `refusal` field.
- **No Content**: If the response does not contain the expected content, an error should be thrown.
```

--------------------------------

### Image Generation API - Transparent Background (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=underwater-ballerina

This example demonstrates how to generate an image with a transparent background using the OpenAI Python client. It sets the `background` parameter to `transparent` and `quality` to `high` for optimal results.

```APIDOC
## POST /v1/images

### Description
Generates an image with a transparent background using the OpenAI Image Generation API.

### Method
POST

### Endpoint
/v1/images

### Parameters
#### Query Parameters
- **model** (string) - Required - The model to use for image generation (e.g., `gpt-image-1`).
- **prompt** (string) - Required - A text description of the desired image.
- **size** (string) - Optional - The desired size of the generated image (e.g., `1024x1024`).
- **background** (string) - Optional - Set to `transparent` to enable transparency. Supported for `png` and `webp` formats.
- **quality** (string) - Optional - Set to `medium` or `high` for best transparency results.

### Request Example
```python
import OpenAI from "openai"
import fs from "fs"
const openai = new OpenAI();

const result = await openai.images.generate({
    model: "gpt-image-1",
    prompt: "Draw a 2D pixel art style sprite sheet of a tabby gray cat",
    size: "1024x1024",
    background: "transparent",
    quality: "high",
});

// Save the image to a file
const image_base64 = result.data[0].b64_json;
const image_bytes = Buffer.from(image_base64, "base64");
fs.writeFileSync("sprite.png", image_bytes);
```

### Response
#### Success Response (200)
- **data** (array) - Contains the generated image data.
  - **b64_json** (string) - The generated image in base64 encoded format.
```

--------------------------------

### Image Generation API - Transparent Background (Python - Direct Image Generation)

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=3d-city

This Python example shows how to generate an image with a transparent background using the `client.images.generate` method. It sets the model, prompt, size, background to 'transparent', and quality to 'high'.

```APIDOC
## POST /v1/images (Direct Image Generation - Python)

### Description
Generates an image with a transparent background using the `client.images.generate` method in Python.

### Method
POST

### Endpoint
/v1/images

### Parameters
#### Request Body
- **model** (string) - Required - The image model (e.g., "gpt-image-1").
- **prompt** (string) - Required - The image description.
- **size** (string) - Optional - Image dimensions (e.g., "1024x1024").
- **background** (string) - Optional - Set to "transparent" for transparency. Works with PNG and WEBP.
- **quality** (string) - Optional - "medium" or "high" recommended.

### Request Example
```json
{
  "model": "gpt-image-1",
  "prompt": "Draw a 2D pixel art style sprite sheet of a tabby gray cat",
  "size": "1024x1024",
  "background": "transparent",
  "quality": "high"
}
```

### Response
#### Success Response (200)
- **data** (array) - Contains the generated image(s).
  - **b64_json** (string) - Base64 encoded image data.
```

--------------------------------

### Get Word-Level Timestamps for Audio Transcription (Python)

Source: https://developers.openai.com/api/docs/guides/speech-to-text

This Python code uses the OpenAI library to transcribe an audio file and obtain word-level timestamps. Ensure you have the 'openai' package installed. The function returns a dictionary with detailed word data.

```python
from openai import OpenAI

client = OpenAI()
audio_file = open("/path/to/file/speech.mp3", "rb")

transcription = client.audio.transcriptions.create(
  file=audio_file,
  model="whisper-1",
  response_format="verbose_json",
  timestamp_granularities=["word"]
)

print(transcription.words)
```

--------------------------------

### Create and Upload Files to Vector Store

Source: https://developers.openai.com/api/docs/assistants/tools/file-search

This section covers the process of creating a vector store and uploading files to it. It shows how to prepare file streams and use the SDK's upload and poll functionality to ensure files are successfully added to the vector store for retrieval.

```python
# Create a vector store called "Financial Statements"
vector_store = client.vector_stores.create(name="Financial Statements")

# Ready the files for upload to OpenAI

file_paths = ["edgar/goog-10k.pdf", "edgar/brka-10k.txt"]
file_streams = [open(path, "rb") for path in file_paths]

# Use the upload and poll SDK helper to upload the files, add them to the vector store,

# and poll the status of the file batch for completion.

file_batch = client.vector_stores.file_batches.upload_and_poll(
vector_store_id=vector_store.id, files=file_streams
)

# You can print the status and the file counts of the batch to see the result of this operation.

print(file_batch.status)
print(file_batch.file_counts)
```

```node.js
const fileStreams = ["edgar/goog-10k.pdf", "edgar/brka-10k.txt"].map((path) =>
fs.createReadStream(path),
);

// Create a vector store including our two files.
let vectorStore = await openai.vectorStores.create({
name: "Financial Statement",
});

await openai.vectorStores.fileBatches.uploadAndPoll(vectorStore.id, fileStreams)
```

--------------------------------

### Upload Files and Create Vector Store (Node.js)

Source: https://developers.openai.com/api/docs/assistants/tools/file-search

This Node.js example illustrates uploading several files and subsequently creating a vector store. It utilizes the OpenAI Node.js library and includes a mechanism to wait for the files to be fully processed.

```node.js
const fs = require('fs');
const path = require('path');

const filePaths = [
  './company-policies.txt',
  './project-brief.pdf',
  './user-guide.docx',
];

async function uploadFiles() {
  const fileIds = [];
  for (const filePath of filePaths) {
    const file = fs.createReadStream(filePath);
    const response = await openai.files.create({
      file: file,
      purpose: 'assistants',
    });
    fileIds.push(response.id);
  }

  const vectorStore = await openai.vectorStores.create({
    name: "My Documents",
    file_ids: fileIds,
  });

  // Wait for the vector store to be ready
  await openai.vectorStores.poll(vectorStore.id);
  return vectorStore;
}

uploadFiles().then(vectorStore => console.log('Vector store created:', vectorStore.id));
```

--------------------------------

### Responses API - Image Generation with Transparency

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=barista-ad

This example demonstrates generating an image with a transparent background using the Responses API. It utilizes the `tools` parameter to specify image generation with transparency.

```APIDOC
## POST /v1/responses

### Description
Generates a response, which can include image generation with transparent backgrounds, using the Responses API.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation (e.g., "gpt-5").
- **input** (string) - Required - The input prompt for the model.
- **tools** (array) - Required - A list of tools to use. For image generation, include an object with `type: "image_generation"`, `background: "transparent"`, and `quality: "high"`.

### Request Example
```json
{
  "model": "gpt-5",
  "input": "Draw a 2D pixel art style sprite sheet of a tabby gray cat",
  "tools": [
    {
      "type": "image_generation",
      "background": "transparent",
      "quality": "high"
    }
  ]
}
```

### Response
#### Success Response (200)
- **output** (array) - A list of outputs from the model, including image generation results.
  - **type** (string) - The type of output, e.g., "image_generation_call".
  - **result** (string) - The base64 encoded image data.

#### Response Example
```json
{
  "id": "resp_abc123",
  "model": "gpt-5",
  "output": [
    {
      "type": "image_generation_call",
      "result": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    }
  ]
}
```
```

--------------------------------

### Run Object Example (Python)

Source: https://developers.openai.com/api/docs/assistants/migration

This snippet shows the structure of a 'Run' object returned by the Assistants API. It includes details about the run's status, associated assistant and thread, timing, and usage statistics. This is useful for understanding the state of an ongoing or completed run.

```json
{
  "id": "run_FKIpcs5ECSwuCmehBqsqkORj",
  "assistant_id": "asst_8fVY45hU3IM6creFkVi5MBKB",
  "cancelled_at": null,
  "completed_at": 1752857327,
  "created_at": 1752857322,
  "expires_at": null,
  "failed_at": null,
  "incomplete_details": null,
  "instructions": null,
  "last_error": null,
  "max_completion_tokens": null,
  "max_prompt_tokens": null,
  "metadata": {},
  "model": "gpt-4.1",
  "object": "thread.run",
  "parallel_tool_calls": true,
  "required_action": null,
  "response_format": "auto",
  "started_at": 1752857324,
  "status": "completed",
  "thread_id": "thread_CrXtCzcyEQbkAcXuNmVSKFs1",
  "tool_choice": "auto",
  "tools": [],
  "truncation_strategy": {
    "type": "auto",
    "last_messages": null
  },
  "usage": {
    "completion_tokens": 130,
    "prompt_tokens": 34,
    "total_tokens": 164,
    "prompt_token_details": {
      "cached_tokens": 0
    },
    "completion_tokens_details": {
      "reasoning_tokens": 0
    }
  },
  "temperature": 1.0,
  "top_p": 1.0,
  "tool_resources": {},
  "reasoning_effort": null
}
```

--------------------------------

### Image Generation with Transparent Background (Python - OpenAI Library)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=barista-ad

This example demonstrates how to generate an image with a transparent background using the OpenAI Python client library. It sets the background to 'transparent' and quality to 'high'.

```APIDOC
## POST /v1/images

### Description
Generates an image based on a text prompt, with support for transparent backgrounds.

### Method
POST

### Endpoint
/v1/images

### Parameters
#### Query Parameters
- **model** (string) - Required - The model to use for image generation (e.g., "gpt-image-1").
- **prompt** (string) - Required - A description of the desired image.
- **size** (string) - Optional - The desired size of the generated image (e.g., "1024x1024").
- **background** (string) - Optional - Set to "transparent" to enable transparent backgrounds. Supported for PNG and WEBP output formats.
- **quality** (string) - Optional - The quality of the generated image. "medium" or "high" recommended for transparency.
- **style** (string) - Optional - The style of the generated images. Can be `vivid` or `natural`.
- **n** (integer) - Optional - The number of images to generate. Defaults to 1.
- **response_format** (string) - Optional - The format in which the generated images are returned. Can be `url` or `b64_json`. Defaults to `url`.
- **user** (string) - Optional - A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse of their services.

### Request Example
```json
{
  "model": "gpt-image-1",
  "prompt": "Draw a 2D pixel art style sprite sheet of a tabby gray cat",
  "size": "1024x1024",
  "background": "transparent",
  "quality": "high"
}
```

### Response
#### Success Response (200)
- **data** (array) - A list of generated image objects.
  - **b64_json** (string) - The base64 encoded image data if `response_format` is `b64_json`.
  - **url** (string) - The URL of the generated image if `response_format` is `url`.
  - **revised_prompt** (string) - The revised prompt based on safety and quality filters.

#### Response Example
```json
{
  "created": 1678886400,
  "data": [
    {
      "b64_json": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
      "revised_prompt": "A 2D pixel art style sprite sheet of a tabby gray cat."
    }
  ]
}
```
```

--------------------------------

### Analyze Image with URL (Python)

Source: https://developers.openai.com/api/docs/guides/images-vision_api-mode=responses

Analyzes an image specified by a URL using the OpenAI Python client. This code snippet shows how to include an image URL in the `content` array for a chat completion request. Ensure you have the `openai` library installed.

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "what's in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://api.nga.gov/iiif/a2e6da57-3cd1-4235-b20e-95dcaefed6c8/full/!800,800/0/default.jpg"
                    },
                },
            ],
        }
    ],
    max_tokens=300
)

print(response.choices[0].message.content)
```

--------------------------------

### Upload and Analyze File using OpenAI API

Source: https://developers.openai.com/api/docs/quickstart

This snippet demonstrates how to upload a file to OpenAI and then use its ID to analyze its content. It first uploads the file with a specified purpose and then sends a request to the responses endpoint with the file ID and a text prompt.

```bash
curl https://api.openai.com/v1/files \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -F purpose="user_data" \
    -F file="@draconomicon.pdf"

curl "https://api.openai.com/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-5",
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "file_id": "file-6F2ksmvXxt4VdoqmHRw6kL"
                    },
                    {
                        "type": "input_text",
                        "text": "What is the first dragon in the book?"
                    }
                ]
            }
        ]
    }'
```

```javascript
import fs from "fs";
import OpenAI from "openai";
const client = new OpenAI();

const file = await client.files.create({
    file: fs.createReadStream("draconomicon.pdf"),
    purpose: "user_data",
});

const response = await client.responses.create({
    model: "gpt-5",
    input: [
        {
            role: "user",
            content: [
                {
                    type: "input_file",
                    file_id: file.id,
                },
                {
                    type: "input_text",
                    text: "What is the first dragon in the book?",
                },
            ],
        },
    ],
});

console.log(response.output_text);
```

```python
from openai import OpenAI
client = OpenAI()

file = client.files.create(
    file=open("draconomicon.pdf", "rb"),
    purpose="user_data"
)

response = client.responses.create(
    model="gpt-5",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_file",
                    "file_id": file.id,
                },
                {
                    "type": "input_text",
                    "text": "What is the first dragon in the book?",
                },
            ],
        },
    ]
)

print(response.output_text)
```

--------------------------------

### Recreate Vector Store with Existing Files (Node.js)

Source: https://developers.openai.com/api/docs/assistants/tools/file-search

This Node.js example shows how to rebuild a vector store using files from a previous one. It lists files from an expired vector store and uses their IDs to create and populate a new vector store.

```node.js
const fileIds = [];
for await (const file of openai.vectorStores.files.list(
"vs_toWTk90YblRLCkbE2xSVoJlF",
)) {
fileIds.push(file.id);
}

const vectorStore = await openai.vectorStores.create({
name: "rag-store",
});
await openai.beta.threads.update("thread_abcd", {
tool_resources: { file_search: { vector_store_ids: [vectorStore.id] } },
});

for (const fileBatch of _.chunk(fileIds, 100)) {
await openai.vectorStores.fileBatches.create(vectorStore.id, {
file_ids: fileBatch,
});
}
```

--------------------------------

### Use Skills with Hosted Shell (Python)

Source: https://developers.openai.com/api/docs/guides/tools-skills

Python example demonstrating how to mount skills in a hosted shell environment by attaching them via `tools[].environment.skills` when calling the shell tool.

```APIDOC
## POST /v1/chat/completions (or similar endpoint for responses.create)

### Description
This Python example shows how to integrate Agent Skills into a hosted shell environment using the OpenAI API. Skills are specified within the `tools` parameter, allowing the model to execute them.

### Method
POST

### Endpoint
`/v1/responses/create` (Illustrative, actual endpoint may vary)

### Parameters
#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use (e.g., `"gpt-5.2"`).
- **tools** (list) - Required - A list of tools, including shell tools with skills:
  - **type** (string) - Required - Must be `"shell"`.
  - **environment** (dict) - Required - Shell environment configuration:
    - **type** (string) - Required - Set to `"container_auto"` for hosted execution.
    - **skills** (list) - Required - List of skills to enable:
      - **type** (string) - Required - Must be `"skill_reference"`.
      - **skill_id** (string) - Required - Identifier for the skill.
      - **version** (int) - Optional - Specific version of the skill.
- **input** (string) - Required - The user's prompt, guiding the model's use of skills.

### Request Example
```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.2",
    tools=[
        {
            "type": "shell",
            "environment": {
                "type": "container_auto",
                "skills": [
                    {"type": "skill_reference", "skill_id": "<skill_id>"},
                    {"type": "skill_reference", "skill_id": "<skill_id>", "version": 2},
                ],
            },
        }
    ],
    input="Use the skills to add 144 and 377, then compute triangle area with base 9 height 13.",
)

print(response.output_text)
```

### Response
#### Success Response (200)
- **output_text** (string) - The model's output after potentially utilizing the specified skills.
```

--------------------------------

### Image Generation API - Transparent Background (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=album-cover

This example demonstrates how to generate an image with a transparent background using the OpenAI Python client library. It utilizes the `background` parameter set to `transparent` and specifies `png` or `webp` as the output format.

```APIDOC
## POST /v1/images

### Description
Generates an image with a transparent background. This feature is supported by GPT Image models (`gpt-image-1.5`, `gpt-image-1`, and `gpt-image-1-mini`) and requires the output format to be `png` or `webp`. Transparency works best with `medium` or `high` quality settings.

### Method
POST

### Endpoint
/v1/images

### Parameters
#### Query Parameters
- **model** (string) - Required - The model to use for image generation (e.g., `gpt-image-1`).
- **prompt** (string) - Required - A text description of the desired image.
- **size** (string) - Optional - The desired size of the generated image (e.g., `1024x1024`).
- **background** (string) - Optional - Set to `transparent` to enable transparent backgrounds. Supported formats are `png` and `webp`.
- **quality** (string) - Optional - The quality of the generated image. `medium` or `high` is recommended for transparency.
- **n** (integer) - Optional - The number of images to generate.
- **response_format** (string) - Optional - The format in which the generated images are returned. `b64_json` or `url`.

### Request Example
```python
import OpenAI
import base64
client = OpenAI()

result = client.images.generate(
    model="gpt-image-1",
    prompt="Draw a 2D pixel art style sprite sheet of a tabby gray cat",
    size="1024x1024",
    background="transparent",
    quality="high",
    response_format="b64_json"
)

image_base64 = result.json()["data"][0]["b64_json"]
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("sprite.png", "wb") as f:
    f.write(image_bytes)
```

### Response
#### Success Response (200)
- **data** (array) - A list of image objects, each containing `b64_json` or `url`.
  - **b64_json** (string) - The generated image in base64 encoded JSON format.
  - **url** (string) - The URL of the generated image.

#### Response Example
```json
{
  "created": 1678886400,
  "data": [
    {
      "b64_json": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
      "revised_prompt": "A 2D pixel art style sprite sheet of a tabby gray cat"
    }
  ]
}
```
```

--------------------------------

### Specifying Model and Sampling Parameters

Source: https://developers.openai.com/api/docs/api-reference/evals

Demonstrates how to select a model and configure sampling parameters for API requests. This includes setting the maximum completion tokens and reasoning effort.

```json
{
  "model": "o3-mini",
  "sampling_params": {
    "max_completion_tokens": 150,
    "reasoning_effort": "high"
  }
}
```

```json
{
  "model": "gpt-5.1",
  "sampling_params": {
    "max_completion_tokens": 200,
    "reasoning_effort": "low"
  }
}
```

--------------------------------

### Clear Input Audio Buffer (input_audio_buffer.clear)

Source: https://developers.openai.com/api/docs/api-reference/realtime-server-events/response/content_part/added

Clears all audio bytes currently stored in the input audio buffer. This action is confirmed by the server with an `input_audio_buffer.cleared` event. It's useful for resetting the audio input state, for example, if a user starts a new utterance or if an error occurs during audio capture.

```json
{
  "type": "input_audio_buffer.clear",
  "event_id": "evt_def456"
}
```

--------------------------------

### Webhook Payload Example for Video Generation Events

Source: https://developers.openai.com/api/docs/guides/video-generation_gallery=open&galleryItem=Cozy-Coffee-Shop-Interior

This example demonstrates the structure of a webhook payload emitted by the OpenAI API when a video generation job completes or fails. It includes event type and data related to the job.

```json
{
  "id": "evt_abc123",
  "object": "event",
  "created_at": 1758941485,
  "type": "video.completed", // or "video.failed"
  "data": {
    "id": "video_abc123"
  }
}
```

--------------------------------

### Python Grader Example with RapidFuzz

Source: https://developers.openai.com/api/docs/guides/graders

A practical Python grader example using the rapidfuzz library to calculate the similarity ratio between the model's output text and a reference answer. It demonstrates how to access sample outputs and item references, and normalize the score.

```python
import os
import requests

# get the API key from environment
api_key = os.environ["OPENAI_API_KEY"]
headers = {"Authorization": f"Bearer {api_key}"}

grading_function = """
from rapidfuzz import fuzz, utils

def grade(sample, item) -> float:
    output_text = sample["output_text"]
    reference_answer = item["reference_answer"]
    return fuzz.WRatio(output_text, reference_answer, processor=utils.default_process) / 100.0
"""

# define a dummy grader for illustration purposes
grader = {
    "type": "python",
    "source": grading_function
}
```

--------------------------------

### Example of an Eval Object Configuration

Source: https://developers.openai.com/api/docs/guides/evals

Illustrates a complete eval object, including its ID, data source configuration, testing criteria, name, and creation timestamp. The schema details are omitted for brevity.

```json
{
    "object": "eval",
    "id": "eval_67e321d23b54819096e6bfe140161184",
    "data_source_config": {
        "type": "custom",
        "schema": { ... omitted for brevity... }
    },
    "testing_criteria": [
        {
            "name": "Match output to human label",
            "id": "Match output to human label-c4fdf789-2fa5-407f-8a41-a6f4f9afd482",
            "type": "string_check",
            "input": "{{ sample.output_text }}",
            "reference": "{{ item.correct_label }}",
            "operation": "eq"
        }
    ],
    "name": "IT Ticket Categorization",
    "created_at": 1742938578,
    "metadata": {}
}
```

--------------------------------

### Create Response with JSON Schema Output (JavaScript)

Source: https://developers.openai.com/api/docs/guides/structured-outputs_context=with_parse

This example shows how to use the OpenAI API in JavaScript to get a structured JSON response. It configures the API to return a math problem solution broken down into steps, adhering to a defined JSON schema.

```APIDOC
## POST /v1/responses

### Description
Creates a response from the model with a specified format, such as JSON Schema, using JavaScript.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The ID of the model to use for this request.
- **input** (array) - Required - The input messages for the model.
  - **role** (string) - Required - The role of the author of a message (e.g., 'system', 'user', 'assistant').
  - **content** (string) - Required - The content of the message.
- **max_output_tokens** (integer) - Optional - The maximum number of tokens to generate in the completion.
- **text** (object) - Required - Specifies the desired output format.
  - **format** (object) - Required - Details about the output format.
    - **type** (string) - Required - The type of the output format (e.g., 'json_schema').
    - **name** (string) - Required - The name of the output format.
    - **schema** (object) - Required - The JSON schema defining the structure of the output.
      - **type** (string) - Required - The type of the schema (e.g., 'object').
      - **properties** (object) - Required - The properties of the schema.
        - **steps** (object) - Required - An array of steps.
          - **type** (string) - Required - The type of the property ('array').
          - **items** (object) - Required - The schema for items in the array.
            - **type** (string) - Required - The type of the item ('object').
            - **properties** (object) - Required - Properties of the item.
              - **explanation** (object) - Required - An explanation for a step.
                - **type** (string) - Required - The type of the property ('string').
              - **output** (object) - Required - The output of a step.
                - **type** (string) - Required - The type of the property ('string').
            - **required** (array) - Required - List of required properties for the item.
        - **final_answer** (object) - Required - The final answer to the problem.
          - **type** (string) - Required - The type of the property ('string').
      - **required** (array) - Required - List of required properties for the schema.
    - **strict** (boolean) - Required - Whether to enforce strict adherence to the schema.

### Request Example
```javascript
{
  "model": "gpt-4o-2024-08-06",
  "input": [
    {
      "role": "system",
      "content": "You are a helpful math tutor. Guide the user through the solution step by step."
    },
    {
      "role": "user",
      "content": "how can I solve 8x + 7 = -23"
    }
  ],
  "max_output_tokens": 50,
  "text": {
    "format": {
      "type": "json_schema",
      "name": "math_response",
      "schema": {
        "type": "object",
        "properties": {
          "steps": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "explanation": {"type": "string"},
                "output": {"type": "string"}
              },
              "required": ["explanation", "output"],
              "additionalProperties": false
            }
          },
          "final_answer": {"type": "string"}
        },
        "required": ["steps", "final_answer"],
        "additionalProperties": false
      },
      "strict": true
    }
  }
}
```

### Response
#### Success Response (200)
- **output** (array) - The model's response content.
  - **type** (string) - The type of the content (e.g., 'output_text', 'refusal').
  - **content** (array) - The actual content of the response.
    - **type** (string) - The type of the content element.
    - **text** (string) - The text content if type is 'output_text'.
    - **refusal** (string) - The refusal reason if type is 'refusal'.

#### Response Example
```json
{
  "output": [
    {
      "type": "output_text",
      "content": [
        {
          "type": "math_response",
          "math_response": {
            "steps": [
              {
                "explanation": "Subtract 7 from both sides of the equation.",
                "output": "8x = -23 - 7"
              },
              {
                "explanation": "Simplify the right side.",
                "output": "8x = -30"
              },
              {
                "explanation": "Divide both sides by 8.",
                "output": "x = -30 / 8"
              },
              {
                "explanation": "Simplify the fraction.",
                "output": "x = -15 / 4"
              }
            ],
            "final_answer": "x = -15/4"
          }
        }
      ]
    }
  ]
}
```
```

--------------------------------

### Voice Agent Conversation Flow Example (JSON)

Source: https://developers.openai.com/api/docs/guides/voice-agents_voice-agent-architecture=chained

An example of encoding common conversation flows for a voice agent using JSON markup within the prompt. This allows for structured handling of typical user interactions.

```json
{
  "conversation_flows": [
    {
      "trigger": "user_asks_for_order_status",
      "steps": [
        "ask_for_order_number",
        "lookup_order_status",
        "provide_status_update"
      ]
    },
    {
      "trigger": "user_wants_to_return_item",
      "steps": [
        "ask_for_reason",
        "check_return_policy",
        "provide_return_instructions"
      ]
    }
  ]
}
```

--------------------------------

### Upload File and Get Chat Completion using cURL

Source: https://developers.openai.com/api/docs/guides/pdf-files_api-mode=responses

This example shows how to upload a PDF file using cURL and then reference its file ID in a request to the chat completions endpoint. It requires an OpenAI API key and a local file named 'draconomicon.pdf'.

```curl
curl https://api.openai.com/v1/files \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -F purpose="user_data" \
    -F file="@draconomicon.pdf"

curl "https://api.openai.com/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
        "model": "gpt-5",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "file",
                        "file": {
                            "file_id": "file-6F2ksmvXxt4VdoqmHRw6kL"
                        }
                    },
                    {
                        "type": "text",
                        "text": "What is the first dragon in the book?"
                    }
                ]
            }
        ]
    }'
```

--------------------------------

### Input Audio Buffer Speech Started Event

Source: https://developers.openai.com/api/docs/api-reference/realtime-server-events/rate_limits/updated

In `server_vad` mode, this event is sent when speech is detected in the audio buffer. It indicates the start of speech and provides `audio_start_ms` relative to the session start. The client can use this for feedback or to interrupt playback.

```json
{
  "audio_start_ms": 1500,
  "event_id": "unique_server_event_id",
  "item_id": "id_of_user_message_item_to_be_created",
  "type": "input_audio_buffer.speech_started"
}
```

--------------------------------

### POST /v1/responses (Image Generation with High Input Fidelity - Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=abstract-orbit

This Python example shows how to generate an edited image with high input fidelity using the `responses.create` method. It utilizes multiple input images and sets `input_fidelity: "high"` for enhanced detail preservation.

```APIDOC
## POST /v1/responses

### Description
Generates an edited image with high input fidelity, preserving details from input images.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for image generation (e.g., "gpt-4.1").
- **input** (list) - Required - A list of input objects, each containing role and content.
  - **role** (string) - Required - The role of the input (e.g., "user").
  - **content** (list) - Required - A list of content objects.
    - **type** (string) - Required - The type of content (e.g., "input_text", "input_image").
    - **text** (string) - Optional - The text prompt.
    - **image_url** (string) - Optional - The URL of the input image.
- **tools** (list) - Required - A list of tool objects.
  - **type** (string) - Required - The type of tool (e.g., "image_generation").
  - **input_fidelity** (string) - Required - The input fidelity level (e.g., "high").
  - **action** (string) - Required - The action to perform (e.g., "edit").

### Request Example
```json
{
  "model": "gpt-4.1",
  "input": [
    {
      "role": "user",
      "content": [
        {"type": "input_text", "text": "Add the logo to the woman's top, as if stamped into the fabric."},
        {
          "type": "input_image",
          "image_url": "https://cdn.openai.com/API/docs/images/woman_futuristic.jpg"
        },
        {
          "type": "input_image",
          "image_url": "https://cdn.openai.com/API/docs/images/brain_logo.png"
        }
      ]
    }
  ],
  "tools": [{"type": "image_generation", "input_fidelity": "high", "action": "edit"}]
}
```

### Response
#### Success Response (200)
- **output** (list) - A list of output objects.
  - **type** (string) - The type of output (e.g., "image_generation_call").
  - **result** (string) - The base64 encoded image data.

#### Response Example
```json
{
  "output": [
    {
      "type": "image_generation_call",
      "result": "<base64_encoded_image_data>"
    }
  ]
}
```
```

--------------------------------

### Image API - Stream an image (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=neon

This Python example demonstrates streaming image generation with the Image API, processing partial image data as it arrives.

```APIDOC
## POST /v1/images/generations

### Description
Streams image generation results directly from the Image API, enabling real-time partial image delivery.

### Method
POST

### Endpoint
/v1/images/generations

### Parameters
#### Query Parameters
- **stream** (bool) - Required - Set to True to enable streaming of response chunks.
- **partial_images** (int) - Optional - Specifies the number of partial images to generate (0-3). If the final image is generated quickly, fewer partial images might be returned than requested. Defaults to 0.

#### Request Body
- **prompt** (str) - Required - The text description for the image to be generated.
- **model** (str) - Required - The image generation model to use (e.g., 'gpt-image-1').

### Request Example
```python
client.images.generate(
    prompt="Draw a gorgeous image of a river made of white owl feathers, snaking its way through a serene winter landscape",
    model="gpt-image-1",
    stream=True,
    partial_images=2,
)
```

### Response
#### Success Response (200)
- **type** (str) - The type of the event, e.g., 'image_generation.partial_image'.
- **partial_image_index** (int) - The index of the partial image.
- **b64_json** (str) - The base64 encoded JSON data of the partial image.

#### Response Example
```json
{
  "type": "image_generation.partial_image",
  "partial_image_index": 0,
  "b64_json": "/9j/4AAQSkZJRgABAQ..."
}
```
```

--------------------------------

### Image Generation with Transparency (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=botanical-perfume

Example of generating an image with a transparent background using the OpenAI Python client library.

```APIDOC
## POST /v1/images

### Description
Generates an image with a transparent background.

### Method
POST

### Endpoint
/v1/images

### Parameters
#### Query Parameters
- **model** (string) - Required - The model to use for image generation (e.g., `gpt-image-1`).
- **prompt** (string) - Required - A description of the desired image.
- **size** (string) - Optional - The desired size of the image (e.g., `1024x1024`).
- **background** (string) - Optional - Set to `transparent` to enable transparency. Supported for `png` and `webp` output formats.
- **quality** (string) - Optional - Set to `medium` or `high` for best transparency results.

### Request Example
```python
import OpenAI from "openai"
import fs from "fs"
const openai = new OpenAI()

const result = await openai.images.generate({
    model: "gpt-image-1",
    prompt: "Draw a 2D pixel art style sprite sheet of a tabby gray cat",
    size: "1024x1024",
    background: "transparent",
    quality: "high",
})

// Save the image to a file
const image_base64 = result.data[0].b64_json
const image_bytes = Buffer.from(image_base64, "base64")
fs.writeFileSync("sprite.png", image_bytes)
```

### Response
#### Success Response (200)
- **data** (array) - Contains the generated image data.
  - **b64_json** (string) - The image data in base64 encoded format.
```

--------------------------------

### Response Object Example

Source: https://developers.openai.com/api/docs/assistants/migration

Example JSON structure for a Response object when using the Responses API.

```APIDOC
## Response Object Example

### Description
This is an example of the JSON response when using the Responses API.

### Method
POST (Implied)

### Endpoint
/v1/responses

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the response.
- **created_at** (integer) - Timestamp when the response was created.
- **conversation** (object) - Details about the conversation.
- **error** (null) - Error object if the response generation failed.
- **incomplete_details** (null) - Details about incomplete responses.
- **instructions** (null) - Instructions provided for the response.
- **metadata** (object) - Key-value pairs for storing additional data.
- **model** (string) - The model used for the response.
- **object** (string) - The type of object, 'response'.
- **output** (array) - An array of output content objects.
- **parallel_tool_calls** (boolean) - Whether parallel tool calls are enabled.
- **temperature** (float) - The sampling temperature.
- **tool_choice** (string) - The tool choice, 'auto'.
- **tools** (array) - List of tools used for the response.
- **top_p** (float) - The nucleus sampling parameter.
- **background** (boolean) - Whether the response was generated in the background.
- **max_output_tokens** (null) - Maximum output tokens allowed.
- **previous_response_id** (null) - ID of the previous response.
- **reasoning** (object) - Reasoning details for the response generation.
- **service_tier** (string) - The service tier used.
- **status** (string) - The status of the response generation.
- **text** (object) - Text formatting details.
- **truncation** (string) - Truncation strategy.
- **usage** (object) - Token usage details for the response.
- **user** (null) - User identifier.
- **max_tool_calls** (null) - Maximum tool calls allowed.
- **store** (boolean) - Whether to store the response.
- **top_logprobs** (integer) - Top log probabilities.

#### Response Example
```json
{
  "id": "resp_687a7b53036c819baad6012d58b39bcb074adcd9e24850fc",
  "created_at": 1752857427,
  "conversation": {
    "id": "conv_689667905b048191b4740501625afd940c7533ace33a2dab"
  },
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "metadata": {},
  "model": "gpt-4.1-2025-04-14",
  "object": "response",
  "output": [
    {
      "id": "msg_687a7b542948819ba79e77e14791ef83074adcd9e24850fc",
      "content": [
        {
          "annotations": [],
          "text": "The \"5 Ds of Dodgeball\" are a humorous set of rules made famous by the 2004 comedy film **\"Dodgeball: A True Underdog Story.\"** In the movie, dodgeball coach Patches O’Houlihan teaches these basics to his team. The **5 Ds** are:\n\n1. **Dodge**\n2. **Duck**\n3. **Dip**\n4. **Dive**\n5. **Dodge** (yes, dodge is listed twice for emphasis!)\n\nIn summary:  \n> **\"If you can dodge a wrench, you can dodge a ball!\"**\n\nThese 5 Ds are not official competitive rules, but have become a fun and memorable pop culture reference for the sport of dodgeball.",
          "type": "output_text",
          "logprobs": []
        }
      ],
      "role": "assistant",
      "status": "completed",
      "type": "message"
    }
  ],
  "parallel_tool_calls": true,
  "temperature": 1.0,
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "background": false,
  "max_output_tokens": null,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "generate_summary": null,
    "summary": null
  },
  "service_tier": "scale",
  "status": "completed",
  "text": {
    "format": {
      "type": "text"
    }
  },
  "truncation": "disabled",
  "usage": {
    "input_tokens": 17,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 150,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 167
  },
  "user": null,
  "max_tool_calls": null,
  "store": true,
  "top_logprobs": 0
}
```
```

--------------------------------

### MCP Call Output Example (JSON)

Source: https://developers.openai.com/api/docs/guides/tools-connectors-mcp

This JSON object illustrates the output of an MCP tool call. It includes the tool's name, arguments passed, any errors encountered, and the output received from the tool, providing a record of the interaction.

```json
{
  "id": "mcp_68a6102d8948819c9b1490d36d5ffa4a0679e572a900e618",
  "type": "mcp_call",
  "approval_request_id": null,
  "arguments": "{\"diceRollExpression\":\"2d4 + 1\"}",
  "error": null,
  "name": "roll",
  "output": "4",
  "server_label": "dmcp"
}
```

--------------------------------

### MCP List Tools Output Example (JSON)

Source: https://developers.openai.com/api/docs/guides/tools-connectors-mcp

This JSON object represents the output from an MCP tool listing request. It details the available tools, including their names, descriptions, and input schemas, allowing the model to understand and utilize these tools.

```json
{
  "id": "mcpl_68a6102a4968819c8177b05584dd627b0679e572a900e618",
  "type": "mcp_list_tools",
  "server_label": "dmcp",
  "tools": [
    {
      "annotations": null,
      "description": "Given a string of text describing a dice roll...",
      "input_schema": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
          "diceRollExpression": {
            "type": "string"
          }
        },
        "required": ["diceRollExpression"],
        "additionalProperties": false
      },
      "name": "roll"
    }
  ]
}
```

--------------------------------

### Realtime Session Creation

Source: https://developers.openai.com/api/docs/api-reference/realtime-server-events/rate_limits/updated

This section describes the parameters for creating a realtime session, including model selection, audio configuration, and instructions.

```APIDOC
## POST /realtime/v1/sessions

### Description
Creates a new realtime session for communication with the model.

### Method
POST

### Endpoint
/realtime/v1/sessions

### Parameters
#### Request Body
- **type** (string) - Required - The type of session to create. Always `realtime` for the Realtime API.
- **audio** (object) - Optional - Configuration for input and output audio.
  - **input** (object) - Optional - Configuration for input audio.
  - **output** (object) - Optional - Configuration for output audio.
- **include** (array of strings) - Optional - Additional fields to include in server outputs. Example: `["item.input_audio_transcription.logprobs"]`.
- **instructions** (string) - Optional - Default system instructions to guide the model's responses and audio behavior.
- **max_output_tokens** (number or "inf") - Optional - Maximum number of output tokens for a single assistant response. Defaults to `inf`.
- **model** (string) - Optional - The Realtime model to use for the session. Examples: `"gpt-realtime"`, `"gpt-4o-realtime-preview"`.
- **output_modalities** (array of strings) - Optional - The set of modalities the model can respond with. Accepts `"text"` or `"audio"`. Defaults to `["audio"]`.
- **prompt** (object) - Optional - Reference to a prompt template and its variables.
- **tool_choice** (object) - Optional - How the model chooses tools.
- **tools** (object) - Optional - Tools available to the model.
- **tracing** (object) - Optional - Configuration for writing session traces to the Traces Dashboard. Set to `null` to disable.
- **truncation** (object) - Optional - Configuration for how the conversation is truncated when token limits are exceeded.

### Request Example
```json
{
  "type": "realtime",
  "audio": {
    "input": {},
    "output": {}
  },
  "instructions": "Act as a helpful assistant.",
  "model": "gpt-realtime",
  "output_modalities": ["audio", "text"],
  "max_output_tokens": 1024
}
```

### Response
#### Success Response (200)
- **event_id** (string) - The unique ID of the server event.
- **session** (object) - The session configuration.
  - **type** (string) - The type of session created.
  - **audio** (object) - Configuration for input and output audio.
  - **include** (array of strings) - Additional fields included in server outputs.
  - **instructions** (string) - System instructions used for the session.
  - **max_output_tokens** (number or "inf") - Maximum output tokens.
  - **model** (string) - The model used for the session.
  - **output_modalities** (array of strings) - Modalities the model can respond with.
  - **prompt** (object) - Prompt template reference.
  - **tool_choice** (object) - Tool choice configuration.
  - **tools** (object) - Available tools.
  - **tracing** (object) - Tracing configuration.
  - **truncation** (object) - Truncation configuration.

#### Response Example
```json
{
  "event_id": "evt_abc123",
  "session": {
    "type": "realtime",
    "audio": {
      "input": {},
      "output": {}
    },
    "include": [],
    "instructions": "Act as a helpful assistant.",
    "max_output_tokens": 1024,
    "model": "gpt-realtime",
    "output_modalities": ["audio", "text"],
    "prompt": null,
    "tool_choice": null,
    "tools": null,
    "tracing": null,
    "truncation": null
  }
}
```
```

--------------------------------

### Lark Grammar for Composing Discrete Tokens

Source: https://developers.openai.com/api/docs/guides/function-calling

Presents a correct usage example of Lark rules for composing discrete tokens like numbers and operators. This pattern is suitable for combining clearly delimited terminals into larger structures. It defines rules for expressions, terms, numbers, and operators.

```lark
start: expr
NUMBER: /[0-9]+/
PLUS: "+"
MINUS: "-"
expr: term (("+"|"-") term)*
term: NUMBER
```

--------------------------------

### Generate Image with Multiple References (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=game-design

Generates a new image using a text prompt and multiple image references provided as Base64 data URLs and file IDs. This example demonstrates creating files, encoding images, and constructing the API request for image generation. Requires 'openai' and 'base64' libraries.

```python
from openai import OpenAI
import base64

# Assuming encode_image and create_file functions are defined as above

client = OpenAI()

prompt = """Generate a photorealistic image of a gift basket on a white background 
labeled 'Relax & Unwind' with a ribbon and handwriting-like font, 
containing all the items in the reference pictures."""

base64_image1 = encode_image("body-lotion.png")
base64_image2 = encode_image("soap.png")
file_id1 = create_file("body-lotion.png")
file_id2 = create_file("incense-kit.png")

response = client.responses.create(
    model="gpt-4.1",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_image1}",
                },
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_image2}",
                },
                {
                    "type": "input_image",
                    "file_id": file_id1,
                },
                {
                    "type": "input_image",
                    "file_id": file_id2,
                }
            ],
        }
    ],
    tools=[{"type": "image_generation"}],
)

image_generation_calls = [
    output
    for output in response.output
    if output.type == "image_generation_call"
]

image_data = [output.result for output in image_generation_calls]

if image_data:
    image_base64 = image_data[0]
    with open("gift-basket.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
else:
    print(response.output.content)
```

--------------------------------

### Example API Response with Reasoning Summary

Source: https://developers.openai.com/api/docs/guides/reasoning_api-mode=responses

This is an example of an API response that includes both an assistant message and a summary of the model's reasoning. The `summary` array contains detailed information about how the model arrived at its answer.

```json
[
  {
    "id": "rs_6876cf02e0bc8192b74af0fb64b715ff06fa2fcced15a5ac",
    "type": "reasoning",
    "summary": [
      {
        "type": "summary_text",
        "text": "**Answering a simple question**\n\nI\u2019m looking at a straightforward question: the capital of France is Paris. It\u2019s a well-known fact, and I want to keep it brief and to the point. Paris is known for its history, art, and culture, so it might be nice to add just a hint of that charm. But mostly, I\u2019ll aim to focus on delivering a clear and direct answer, ensuring the user gets what they\u2019re looking for without any extra fluff."
      }
    ]
  },
  {
    "id": "msg_6876cf054f58819284ecc1058131305506fa2fcced15a5ac",
    "type": "message",
    "status": "completed",
    "content": [
      {
        "type": "output_text",
        "annotations": [],
        "logprobs": [],
        "text": "The capital of France is Paris."
      }
    ],
    "role": "assistant"
  }
]
```

--------------------------------

### Image Generation with Transparent Background (cURL)

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=cafe-friends

This example demonstrates how to generate an image with a transparent background using a cURL command.

```APIDOC
## POST /v1/images

### Description
Generates an image with a transparent background using cURL.

### Method
POST

### Endpoint
/v1/images

### Parameters
#### Request Body
- **prompt** (string) - Required - A text description of the desired image.
- **quality** (string) - Optional - Set to `high` for best results with transparency.
- **size** (string) - Optional - The desired size of the generated image (e.g., `1024x1024`).
- **background** (string) - Optional - Set to `transparent` to enable transparent backgrounds. Supported only with `png` and `webp` output formats.

### Request Example
```bash
curl -X POST "https://api.openai.com/v1/images" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-type: application/json" \
    -d '{ \
        "prompt": "Draw a 2D pixel art style sprite sheet of a tabby gray cat", \
        "quality": "high", \
        "size": "1024x1024", \
        "background": "transparent" \
    }' | jq -r 'data[0].b64_json' | base64 --decode > sprite.png
```

### Response
#### Success Response (200)
- **data** (array) - An array containing the generated image data.
  - **b64_json** (string) - The base64 encoded image data.
```

--------------------------------

### Define Function Parameters (JSON)

Source: https://developers.openai.com/api/docs/assistants/tools/function-calling

Defines function parameters using JSON schema for the Assistants API.  This includes specifying data types, descriptions, and constraints like `additionalProperties` and `required` fields.  The example shows how to define parameters for getting weather information and rain probability.

```json
{
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "The city and state, e.g., San Francisco, CA",
      },
      "unit": {
        "type": "string",
        "enum": ["Celsius", "Fahrenheit"],
        "description":
          "The temperature unit to use. Infer this from the user's location.",
      },
    },
    "required": ["location", "unit"],
    "additionalProperties": false
  },
  "strict": true
},
{
  "type": "function",
  "function": {
    "name": "getRainProbability",
    "description": "Get the probability of rain for a specific location",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {
          "type": "string",
          "description": "The city and state, e.g., San Francisco, CA",
        },
      },
      "required": ["location"],
      "additionalProperties": false
    },
    "strict": true
  },
},

```

--------------------------------

### Video Generation and Download (Python)

Source: https://developers.openai.com/api/docs/guides/video-generation_gallery=open&galleryItem=Cozy-Coffee-Shop-Interior

This snippet demonstrates how to create a video, monitor its generation progress, and download the resulting MP4 file using the OpenAI Python client.

```APIDOC
## POST /videos

### Description
Initiates the video generation process based on a provided prompt and model.

### Method
POST

### Endpoint
/videos

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for video generation (e.g., 'sora-2').
- **prompt** (string) - Required - The text prompt describing the desired video content.

### Request Example
```json
{
  "model": "sora-2",
  "prompt": "A video of the words 'Thank you' in sparkling letters"
}
```

### Response
#### Success Response (200)
- **id** (string) - The unique identifier for the video generation job.
- **status** (string) - The current status of the video generation job (e.g., 'queued', 'in_progress', 'completed', 'failed').
- **progress** (integer) - The completion percentage of the video generation.

#### Response Example
```json
{
  "id": "video_abc123",
  "object": "video",
  "created_at": 1758941485,
  "status": "in_progress",
  "progress": 50
}
```

## GET /videos/{video_id}

### Description
Retrieves the current status and progress of a specific video generation job.

### Method
GET

### Endpoint
/videos/{video_id}

### Parameters
#### Path Parameters
- **video_id** (string) - Required - The ID of the video generation job to retrieve.

### Response
#### Success Response (200)
- **id** (string) - The unique identifier for the video generation job.
- **status** (string) - The current status of the video generation job.
- **progress** (integer) - The completion percentage of the video generation.

#### Response Example
```json
{
  "id": "video_abc123",
  "object": "video",
  "created_at": 1758941485,
  "status": "completed",
  "progress": 100
}
```

## GET /videos/{video_id}/content

### Description
Downloads the generated video content, thumbnail, or spritesheet for a completed video job.

### Method
GET

### Endpoint
/videos/{video_id}/content

### Parameters
#### Path Parameters
- **video_id** (string) - Required - The ID of the completed video job.

#### Query Parameters
- **variant** (string) - Optional - Specifies the type of asset to download. Options: 'video' (default), 'thumbnail', 'spritesheet'.

### Response
#### Success Response (200)
- Returns the binary data of the requested asset (MP4 for video, WEBP for thumbnail, JPG for spritesheet).
- Standard content headers are included (e.g., `Content-Type`, `Content-Disposition`).

### Request Example (Download MP4)
```bash
curl -L "https://api.openai.com/v1/videos/video_abc123/content" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  --output video.mp4
```

### Request Example (Download Thumbnail)
```bash
curl -L "https://api.openai.com/v1/videos/video_abc123/content?variant=thumbnail" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  --output thumbnail.webp
```

### Request Example (Download Spritesheet)
```bash
curl -L "https://api.openai.com/v1/videos/video_abc123/content?variant=spritesheet" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  --output spritesheet.jpg
```

## Webhooks

### Description
Register webhooks to receive automatic notifications when a video generation job completes or fails, instead of polling the API.

### Event Types
- `video.completed`: Emitted when a video generation job successfully finishes.
- `video.failed`: Emitted when a video generation job fails.

### Event Payload Example
```json
{
  "id": "evt_abc123",
  "object": "event",
  "created_at": 1758941485,
  "type": "video.completed", // or "video.failed"
  "data": {
    "id": "video_abc123"
  }
}
```
```

--------------------------------

### Create Assistant with Code Interpreter

Source: https://developers.openai.com/api/docs/api-reference/assistants/createAssistant

This snippet demonstrates how to create an assistant that can execute Python code using the `code_interpreter` tool. It includes the necessary HTTP request headers and a JSON payload specifying the assistant's instructions, name, tools, and model.

```HTTP
curl "https://api.openai.com/v1/assistants" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Beta: assistants=v2" \
  -d '{
    "instructions": "You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
    "name": "Math Tutor",
    "tools": [{"type": "code_interpreter"}],
    "model": "gpt-4o"
  }'
```

```JSON
{
  "id": "asst_abc123",
  "object": "assistant",
  "created_at": 1698984975,
  "name": "Math Tutor",
  "description": null,
  "model": "gpt-4o",
  "instructions": "You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
  "tools": [
    {
      "type": "code_interpreter"
    }
  ],
  "metadata": {},
  "top_p": 1.0,
  "temperature": 1.0,
  "response_format": "auto"
}
```

--------------------------------

### Thread Object Example Response

Source: https://developers.openai.com/api/docs/api-reference/threads/createThread

This is an example of a successful response when retrieving or creating a thread object. It details the thread's ID, creation timestamp, metadata, object type, and the associated tool resources like code interpreter and file search.

```json
{
  "id": "id",
  "created_at": 0,
  "metadata": {
    "foo": "string"
  },
  "object": "thread",
  "tool_resources": {
    "code_interpreter": {
      "file_ids": [
        "string"
      ]
    },
    "file_search": {
      "vector_store_ids": [
        "string"
      ]
    }
  }
}
```

--------------------------------

### POST /v1/chat/completions - Custom Tools

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=music-theory-trainer

This example shows how to define and use custom tools with the Chat Completions API, highlighting the differences in tool definition structure.

```APIDOC
## POST /v1/chat/completions

### Description
Generates a chat completion that can utilize custom tools.

### Method
POST

### Endpoint
/v1/chat/completions

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation (e.g., "gpt-5.2").
- **messages** (array) - Required - An array of message objects representing the conversation.
  - **role** (string) - Required - The role of the message sender (e.g., "user").
  - **content** (string) - Required - The content of the message.
- **tools** (array) - Optional - A list of tools the model can use.
  - **type** (string) - Required - The type of tool (e.g., "custom").
  - **custom** (object) - Required for custom tools - Configuration for the custom tool.
    - **name** (string) - Required - The name of the custom tool.
    - **description** (string) - Optional - A description of what the tool does.

### Request Example
```json
{
  "model": "gpt-5.2",
  "messages": [
    { "role": "user", "content": "Use the code_exec tool to calculate the area of a circle with radius equal to the number of r letters in blueberry" }
  ],
  "tools": [
    {
      "type": "custom",
      "custom": {
        "name": "code_exec",
        "description": "Executes arbitrary python code"
      }
    }
  ]
}
```

### Response
#### Success Response (200)
- **choices** (array) - An array of completion choices.
  - **message** (object) - The message object.
    - **role** (string) - The role of the message sender.
    - **content** (string) - The content of the message, potentially including tool calls.

#### Response Example
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "[Generated response text or tool call]"
      }
    }
  ]
}
```
```

--------------------------------

### Weather API Call Examples for GPT Actions

Source: https://developers.openai.com/api/docs/actions/introduction

This snippet demonstrates the JSON payloads for two API calls to weather.gov used within a GPT Action. The first call uses latitude and longitude to get forecast office and grid coordinates, and the second uses these coordinates to retrieve a detailed forecast.

```json
{
  "latitude": 38.9072,
  "longitude": -77.0369
}
```

```json
{
  "wfo": "LWX",
  "x": 97,
  "y": 71
}
```

--------------------------------

### Migration Guidance to GPT-5.2

Source: https://developers.openai.com/api/docs/guides/latest-model

Provides guidance on migrating from older OpenAI models to GPT-5.2, highlighting key changes and recommended prompting strategies for optimal performance.

```APIDOC
## Migration to GPT-5.2

### Description
Guidance for migrating from previous OpenAI models to GPT-5.2, focusing on prompt adjustments and recommended reasoning levels for different model families.

### Method
API Call Configuration and Prompt Engineering.

### Endpoint
/v1/chat/completions

### Parameters
#### Request Body
- **model** (string) - Required - Set to `"gpt-5.2"` for the latest model.
- **messages** (array) - Required - Adjust prompts based on GPT-5.2 specific guidance.
- **reasoning** (string) - Optional - For older models like 'o3', consider setting to `"medium"` or `"high"`. For 'gpt-4.1', start with `"none"`.

### Migration Recommendations:
- **gpt-5.1**: `gpt-5.2` with default settings is intended as a drop-in replacement.
- **o3**: Use `gpt-5.2` with `medium` or `high` reasoning. Start with `medium` and tune prompts.
- **gpt-4.1**: Use `gpt-5.2` with `none` reasoning. Tune prompts for performance.
- **o4-mini or gpt-4.1-mini**: Consider `gpt-5-mini` with prompt tuning.
- **gpt-4.1-nano**: Consider `gpt-5-nano` with prompt tuning.

### Resources:
- **GPT-5.2 Prompting Guide**: [https://developers.openai.com/cookbook/examples/gpt-5/gpt-5-2_prompting_guide](https://developers.openai.com/cookbook/examples/gpt-5/gpt-5-2_prompting_guide)
- **Responses API Guide**: [https://developers.openai.com/cookbook/examples/responses_api/reasoning_items](https://developers.openai.com/cookbook/examples/responses_api/reasoning_items)
- **Prompt Optimizer**: [https://platform.openai.com/chat/edit?models=gpt-5.2&optimize=true](https://platform.openai.com/chat/edit?models=gpt-5.2&optimize=true)
```

--------------------------------

### Define and Use Tools with OpenAI API (Python)

Source: https://developers.openai.com/api/docs/guides/function-calling

This Python snippet defines a 'get_horoscope' function as a tool for the OpenAI model. It demonstrates how to structure the tool definition, make an initial model call to get a function call, execute the function, and then provide the output back to the model for a final response.

```python
import json

# 1. Define a list of callable tools for the model
tools = [
    {
        "type": "function",
        "name": "get_horoscope",
        "description": "Get today's horoscope for an astrological sign.",
        "parameters": {
            "type": "object",
            "properties": {
                "sign": {
                    "type": "string",
                    "description": "An astrological sign like Taurus or Aquarius",
                },
            },
            "required": ["sign"],
        },
    },
]

def get_horoscope(sign):
    return f"{sign}: Next Tuesday you will befriend a baby otter."

# Create a running input list we will add to over time
input_list = [
    {"role": "user", "content": "What is my horoscope? I am an Aquarius."}
]

# 2. Prompt the model with tools defined
response = client.responses.create(
    model="gpt-5",
    tools=tools,
    input=input_list,
)

# Save function call outputs for subsequent requests
input_list += response.output

for item in response.output:
    if item.type == "function_call":
        if item.name == "get_horoscope":
            # 3. Execute the function logic for get_horoscope
            horoscope = get_horoscope(json.loads(item.arguments))
            
            # 4. Provide function call results to the model
            input_list.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps({
                  "horoscope": horoscope
                })
            })

print("Final input:")
print(input_list)

response = client.responses.create(
    model="gpt-5",
    instructions="Respond only with a horoscope generated by a tool.",
    tools=tools,
    input=input_list,
)

# 5. The model should be able to give a response!
print("Final output:")
print(response.model_dump_json(indent=2))
print("\n" + response.output_text)

```

--------------------------------

### Handling Function Calls

Source: https://developers.openai.com/api/docs/guides/function-calling

Learn how the model generates function calls and how to process them to return results.

```APIDOC
## Handling Function Calls

When the model decides to call a function, its response will include an `output` array. Each entry in this array with a `type` of `function_call` contains a `call_id`, `name`, and JSON-encoded `arguments` for the function to be executed.

It is best practice to assume there may be multiple function calls in a single response.

### Processing Function Calls

1. **Iterate through the `output` array** in the model's response.
2. **Check if `type` is `function_call`**.
3. **Extract `call_id`, `name`, and `arguments`**.
4. **Execute the function** specified by `name` with the provided `arguments`.
5. **Format the result** of the function execution.
6. **Submit the result** back to the model using the `call_id`.
```

--------------------------------

### List Container Files Response Example

Source: https://developers.openai.com/api/docs/api-reference/container-files/listContainerFiles

This is an example of the JSON response when listing files in a container. It includes a list of file objects, each with details such as ID, size, container ID, creation timestamp, path, and source. Pagination information like `first_id`, `has_more`, and `last_id` is also provided.

```json
{
    "object": "list",
    "data": [
        {
            "id": "cfile_682e0e8a43c88191a7978f477a09bdf5",
            "object": "container.file",
            "created_at": 1747848842,
            "bytes": 880,
            "container_id": "cntr_682e0e7318108198aa783fd921ff305e08e78805b9fdbb04",
            "path": "/mnt/data/88e12fa445d32636f190a0b33daed6cb-tsconfig.json",
            "source": "user"
        }
    ],
    "first_id": "cfile_682e0e8a43c88191a7978f477a09bdf5",
    "has_more": false,
    "last_id": "cfile_682e0e8a43c88191a7978f477a09bdf5"
}
```

--------------------------------

### POST /v1/responses - Custom Tools

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=artisan-csa

This example demonstrates how to use custom tools with the Responses API.

```APIDOC
## POST /v1/responses - Custom Tools

### Description
This endpoint allows for custom tool integration for enhanced capabilities.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation.
- **input** (string) - Required - The prompt for the model.
- **tools** (array) - Optional - An array of tool definitions.
  - **type** (string) - Required - The type of tool (e.g., "custom").
  - **name** (string) - Required - The name of the custom tool.
  - **description** (string) - Required - A description of the tool's functionality.

### Request Example
```json
{
  "model": "gpt-5.2",
  "input": "Use the code_exec tool to calculate the area of a circle with radius equal to the number of r letters in blueberry",
  "tools": [
    {
      "type": "custom",
      "name": "code_exec",
      "description": "Executes arbitrary python code"
    }
  ]
}
```

### Response
#### Success Response (200)
- **response** (string) - The generated response from the model, potentially including tool calls.

#### Response Example
```json
{
  "response": "The area of the circle is..."
}
```
```

--------------------------------

### Correct Lark Grammar Pattern (Single Bounded Terminal)

Source: https://developers.openai.com/api/docs/guides/function-calling

Demonstrates a correct pattern for a Lark grammar using a single, bounded terminal for sentence structure. This approach ensures reliable parsing by the OpenAI API. It defines a 'start' rule and a 'SENTENCE' terminal with specific character sets and bounded quantifiers.

```lark
start: SENTENCE
SENTENCE: /[A-Za-z, ]*(the hero|a dragon|an old man|the princess)[A-Za-z, ]*(fought|saved|found|lost)[A-Za-z, ]*(a treasure|the kingdom|a secret|his way)[A-Za-z, ]*./
```

--------------------------------

### OpenAI API Transcription Response Example (HTTP)

Source: https://developers.openai.com/api/docs/api-reference/audio/createTranscription

This is an example of a typical response from the OpenAI API when creating an audio transcription. It highlights the 'text' field containing the transcription and the 'usage' object detailing token consumption.

```json
{
  "text": "Imagine the wildest idea that you've ever had, and you're curious about how it might scale to something that's a 100, a 1,000 times bigger. This is a place where you can get to do that.",
  "usage": {
    "type": "tokens",
    "input_tokens": 14,
    "input_token_details": {
      "text_tokens": 0,
      "audio_tokens": 14
    },
    "output_tokens": 45,
    "total_tokens": 59
  }
}

```

--------------------------------

### Define and Use Tools with OpenAI API (JavaScript)

Source: https://developers.openai.com/api/docs/guides/function-calling

This JavaScript snippet defines a 'get_horoscope' function as a tool for the OpenAI model. It mirrors the Python example, showing how to structure tool definitions, initiate model calls, handle function calls, and process the results within a Node.js environment using the OpenAI SDK.

```javascript
import OpenAI from "openai";
const openai = new OpenAI();

// 1. Define a list of callable tools for the model
const tools = [
  {
    type: "function",
    name: "get_horoscope",
    description: "Get today's horoscope for an astrological sign.",
    parameters: {
      type: "object",
      properties: {
        sign: {
          type: "string",
          description: "An astrological sign like Taurus or Aquarius",
        },
      },
      required: ["sign"],
    },
  },
];

function getHoroscope(sign) {
  return sign + " Next Tuesday you will befriend a baby otter.";
}

// Create a running input list we will add to over time
let input = [
  { role: "user", content: "What is my horoscope? I am an Aquarius." },
];

// 2. Prompt the model with tools defined
let response = await openai.responses.create({
  model: "gpt-5",
  tools,
  input,
});

response.output.forEach((item) => {
  if (item.type == "function_call") {
    if (item.name == "get_horoscope"):
      // 3. Execute the function logic for get_horoscope
      const horoscope = get_horoscope(JSON.parse(item.arguments))
      
      // 4. Provide function call results to the model
      input_list.push({
          type: "function_call_output",
          call_id: item.call_id,
          output: json.dumps({
            horoscope
          })
      })
  }
});

console.log("Final input:");
console.log(JSON.stringify(input, null, 2));

response = await openai.responses.create({
  model: "gpt-5",
  instructions: "Respond only with a horoscope generated by a tool.",
  tools,
  input,
});

// 5. The model should be able to give a response!
console.log("Final output:");
console.log(JSON.stringify(response.output, null, 2));

```

--------------------------------

### POST /images/edit with High Input Fidelity (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=cafe-friends

This Python example illustrates editing an image with high input fidelity using the `images.edit` endpoint. It shows how to provide image files and a prompt for the editing process.

```APIDOC
## POST /images/edit

### Description
Edits an existing image with high input fidelity using Python, preserving details from the input images.

### Method
POST

### Endpoint
/images/edit

### Parameters
#### Request Body
- **model** (string) - Required - The image model to use (e.g., "gpt-image-1").
- **image** (list) - Required - A list of opened image files in binary read mode.
- **prompt** (string) - Required - A text description of the desired image.
- **input_fidelity** (string) - Optional - Sets the input fidelity to "high" or "low". Defaults to "low".

### Request Example
```python
{
    "model": "gpt-image-1",
    "image": [open("woman.jpg", "rb"), open("logo.png", "rb")],
    "prompt": "Add the logo to the woman's top, as if stamped into the fabric.",
    "input_fidelity": "high"
}
```

### Response
#### Success Response (200)
- **data** (list) - A list of image dictionaries.
  - **b64_json** (string) - The base64 encoded image data.

#### Response Example
```python
{
  "data": [
    {
      "b64_json": "<base64_encoded_image_data>"
    }
  ]
}
```
```

--------------------------------

### Split Audio File using PyDub (Python)

Source: https://developers.openai.com/api/docs/guides/speech-to-text

This Python snippet utilizes the PyDub library to split a large audio file into smaller segments. It's useful for handling audio files that exceed the 25 MB limit of the OpenAI API. Ensure PyDub is installed. The example splits the audio into 10-minute chunks.

```python
from pydub import AudioSegment

song = AudioSegment.from_mp3("good_morning.mp3")

# PyDub handles time in milliseconds
ten_minutes = 10 * 60 * 1000

first_10_minutes = song[:ten_minutes]

first_10_minutes.export("good_morning_10.mp3", format="mp3")
```

--------------------------------

### Image Generation with Transparent Background (cURL)

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=daytime

This example demonstrates how to generate an image with a transparent background using a cURL command. It includes the `background` parameter set to `transparent` and specifies `png` or `webp` as output formats.

```APIDOC
## POST /v1/images

### Description
Generates an image with a transparent background.

### Method
POST

### Endpoint
/v1/images

### Parameters
#### Request Body
- **prompt** (string) - Required - A text description of the desired image.
- **quality** (string) - Optional - Set to `medium` or `high` for best transparency results.
- **size** (string) - Optional - The desired size of the generated image (e.g., `1024x1024`).
- **background** (string) - Optional - Set to `transparent` to enable transparency. Supported for `png` and `webp` output formats.

### Request Example
```bash
curl -X POST "https://api.openai.com/v1/images" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-type: application/json" \
    -d '{ \
        "prompt": "Draw a 2D pixel art style sprite sheet of a tabby gray cat", \
        "quality": "high", \
        "size": "1024x1024", \
        "background": "transparent" \
    }' | jq -r 'data[0].b64_json' | base64 --decode > sprite.png
```

### Response
#### Success Response (200)
- **data** (array) - Contains the generated image data.
  - **b64_json** (string) - The base64 encoded image data.
```

--------------------------------

### Send Text and File Input to OpenAI API (Python)

Source: https://developers.openai.com/api/docs/quickstart

This Python snippet shows how to send a file and a text prompt to the OpenAI API. It utilizes the OpenAI Python client library to upload a file and then include it as an input alongside a text question in a chat completion request. The response from the API is then printed.

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_file",
                    "file_id": file.id,
                },
                {
                    "type": "input_text",
                    "text": "What is the first dragon in the book?",
                },
            ]
        }
    ]
)

print(response.output_text)
```

--------------------------------

### Analyze Image using Uploaded File ID (C#)

Source: https://developers.openai.com/api/docs/guides/images-vision_api-mode=responses

This C# example shows how to upload an image to OpenAI using the Files API and then use the file ID to analyze the image. It requires the 'OpenAI.Files' and 'OpenAI.Responses' namespaces and an API key. The input is a URL from which the image is downloaded and uploaded, and the output is the model's textual response.

```csharp
using OpenAI.Files;
using OpenAI.Responses;
using System;
using System.Net.Http;
using System.Threading.Tasks;

string key = Environment.GetEnvironmentVariable("OPENAI_API_KEY")!;
OpenAIResponseClient client = new(model: "gpt-5", apiKey: key);

string filename = "cat_and_otter.png";
Uri imageUrl = new($"https://openai-documentation.vercel.app/images/{filename}");
using var http = new HttpClient();

// Download an image as stream
using var stream = await http.GetStreamAsync(imageUrl);

OpenAIFileClient files = new(key);
OpenAIFile file = await files.UploadFileAsync(BinaryData.FromStream(stream), filename, FileUploadPurpose.Vision);

OpenAIResponse response = (OpenAIResponse)client.CreateResponse([
    ResponseItem.CreateUserMessageItem([
        ResponseContentPart.CreateInputTextPart("what's in this image?"),
        ResponseContentPart.CreateInputImagePart(file.Id)
    ])
]);

Console.WriteLine(response.GetOutputText())
```

--------------------------------

### Upload Files and Create Vector Store

Source: https://developers.openai.com/api/docs/assistants/tools/file-search

This section covers uploading files and creating a Vector Store to hold them, including code examples for Python and Node.js.

```APIDOC
## File Upload and Vector Store Creation

### Description
Uploads files and creates a Vector Store. The SDK provides helpers to upload and poll the status of the files in one go.

### Python Example
```python
from openai import OpenAI
from openai.pagination import SyncCursorPage

client = OpenAI()

# Upload files
file_objects = []
for file_path in ['file_1.pdf', 'file_2.txt']:
    with open(file_path, "rb") as f:
        file_objects.append(client.files.create(file=f, purpose='assistants'))

file_ids = [f.id for f in file_objects]

# Create and poll Vector Store
vector_store = client.vector_stores.create_and_poll(
    name="Product Documentation",
    file_ids=file_ids,
    # Optional: Configure expiration policy
    expires_after={
      "anchor": "last_active_at",
      "days": 7
    }
)

print(f"Vector Store created: {vector_store.id}")
```

### Node.js Example
```javascript
const OpenAI = require('openai');
const fs = require('fs');

const openai = new OpenAI();

async function uploadFilesAndCreateVectorStore() {
  // Upload files
  const filePaths = ['file_1.pdf', 'file_2.txt'];
  const fileIds = [];

  for (const filePath of filePaths) {
    const file = await openai.files.create({
      file: fs.createReadStream(filePath),
      purpose: 'assistants',
    });
    fileIds.push(file.id);
  }

  // Create and poll Vector Store
  let vectorStore = await openai.vectorStores.create({
    name: "Product Documentation",
    file_ids: fileIds,
    // Optional: Configure expiration policy
    expires_after: {
      anchor: "last_active_at",
      days: 7
    }
  });

  // Polling is handled implicitly by create_and_poll in Python, 
  // but in Node.js, you might need to manually check status or use a helper.
  // For simplicity, assuming create resolves when ready or you'd poll vectorStore.status
  console.log(`Vector Store created: ${vectorStore.id}`);
}

uploadFilesAndCreateVectorStore();
```
```

--------------------------------

### Install OpenAI Library for TypeScript

Source: https://developers.openai.com/api/docs/api-reference/chat/completions/responses

Installs the OpenAI library for TypeScript using npm. This is the first step to integrating OpenAI's services into your TypeScript applications.

```bash
npm install openai
```

--------------------------------

### Example Function Definition Schema for OpenAI API

Source: https://developers.openai.com/api/docs/guides/function-calling

This JSON schema defines a 'get_weather' function for the OpenAI API. It specifies the function's type, name, description, and the structure of its input parameters using JSON Schema, including required fields and an enum for units. The 'strict' field indicates whether to enforce strict mode for the function call.

```json
{
  "type": "function",
  "name": "get_weather",
  "description": "Retrieves current weather for the given location.",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "City and country e.g. Bogotá, Colombia"
      },
      "units": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "Units the temperature will be returned in."
      }
    },
    "required": ["location", "units"],
    "additionalProperties": false
  },
  "strict": true
}
```

--------------------------------

### Edit an image using a mask (inpainting) - Node.js

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=floorplan

This example demonstrates how to edit an image using a mask with the OpenAI Node.js client. It mirrors the Python example, showing the equivalent asynchronous operations.

```APIDOC
## POST /v1/responses

### Description
Edits an image based on a text prompt and a mask using the OpenAI Node.js client. This function is asynchronous and handles file operations accordingly.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for image editing (e.g., "gpt-4o").
- **input** (array) - Required - An array of input objects, typically including text and image content.
  - **role** (string) - Required - The role of the message sender (e.g., "user").
  - **content** (array) - Required - An array of content objects.
    - **type** (string) - Required - The type of content (e.g., "input_text", "input_image").
    - **text** (string) - Required if type is "input_text" - The text prompt for editing.
    - **file_id** (string) - Required if type is "input_image" - The ID of the input image file.
- **tools** (array) - Required - An array of tool definitions.
  - **type** (string) - Required - The type of tool (e.g., "image_generation").
  - **quality** (string) - Optional - The quality of the generated image (e.g., "high").
  - **input_image_mask** (object) - Required if type is "image_generation" - Defines the input image mask.
    - **file_id** (string) - Required - The ID of the mask image file.

### Request Example
```javascript
import OpenAI from "openai";
const openai = new OpenAI();

const fileId = await createFile("sunlit_lounge.png");
const maskId = await createFile("mask.png");

const response = await openai.responses.create({
  model: "gpt-4o",
  input: [
    {
      role: "user",
      content: [
        {
          type: "input_text",
          text: "generate an image of the same sunlit indoor lounge area with a pool but the pool should contain a flamingo",
        },
        {
          type: "input_image",
          file_id: fileId,
        }
      ],
    },
  ],
  tools: [
    {
      type: "image_generation",
      quality: "high",
      input_image_mask: {
        file_id: maskId,
      }
    },
  ],
});

const imageData = response.output
  .filter((output) => output.type === "image_generation_call")
  .map((output) => output.result);

if (imageData.length > 0) {
  const imageBase64 = imageData[0];
  const fs = await import("fs");
  fs.writeFileSync("lounge.png", Buffer.from(imageBase64, "base64"));
}
```

### Response
#### Success Response (200)
- **output** (array) - An array of tool outputs. For image generation, this will contain the generated image data.
  - **type** (string) - The type of output (e.g., "image_generation_call").
  - **result** (string) - The base64 encoded image data.

#### Response Example
```json
{
  "id": "chatcmpl-xxxxxxxxxxxxxxxxxxxx",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "gpt-4o",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": [
          {
            "type": "image_generation_call",
            "result": "/9j/4AAQSkZJRgABAQ..."
          }
        ]
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "total_tokens": 150
  }
}
```
```

--------------------------------

### Incorrect Lark Grammar Pattern (Splitting Across Rules)

Source: https://developers.openai.com/api/docs/guides/function-calling

Illustrates an incorrect pattern in Lark grammars where free text is split across multiple rules and terminals. This can lead to unpredictable behavior as the lexer greedily matches free-text pieces, causing a loss of control over parsing. The example shows a 'sentence' rule attempting to partition text between subject, verb, and object.

```lark
start: sentence
sentence: /[A-Za-z, ]+/ subject /[A-Za-z, ]+/ verb /[A-Za-z, ]+/ object /[A-Za-z, ]+/
```

--------------------------------

### POST /v1/images/edit (Image Editing with High Input Fidelity - Node.js)

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=floorplan

This Node.js example shows how to edit an existing image and apply a prompt with high input fidelity. It uses local image files and sets `input_fidelity: "high"`.

```APIDOC
## POST /v1/images/edit

### Description
Edits an existing image based on a prompt, with high input fidelity for detail preservation.

### Method
POST

### Endpoint
/v1/images/edit

### Parameters
#### Request Body
- **model** (string) - Required - The image model to use (e.g., "gpt-image-1").
- **image** (array) - Required - An array of image streams or file objects to be edited.
- **prompt** (string) - Required - A text description of the desired image.
- **input_fidelity** (string) - Optional - Sets the input fidelity to 'high'. Defaults to 'low'.

### Request Example
```json
{
  "model": "gpt-image-1",
  "image": [
    "fs.createReadStream(\"woman.jpg\")",
    "fs.createReadStream(\"logo.png\")"
  ],
  "prompt": "Add the logo to the woman's top, as if stamped into the fabric.",
  "input_fidelity": "high"
}
```

### Response
#### Success Response (200)
- **data** (array) - An array of image objects.
  - **b64_json** (string) - Base64 encoded JSON representation of the image.

#### Response Example
```json
{
  "data": [
    { "b64_json": "<base64_encoded_image_data>" }
  ]
}
```
```

--------------------------------

### Edit an image using a mask (inpainting) - Node.js

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=chameleon-macro

This example demonstrates how to edit an image using a mask with the OpenAI Node.js client. It mirrors the Python example, showing the equivalent operations for JavaScript developers.

```APIDOC
## POST /v1/images/edits

### Description
Edits an image using a mask to indicate which part of the image should be edited. The model uses the mask as guidance, but may not follow its exact shape with complete precision. If multiple input images are provided, the mask will be applied to the first image.

### Method
POST

### Endpoint
/v1/images/edits

### Parameters
#### Form Data
- **model** (string) - Required - The model to use for image editing. Example: `gpt-image-1`.
- **prompt** (string) - Required - A text description of the desired image.
- **image** (file) - Required - The image to edit. Must be a PNG image, less than 2MB in size, and square.
- **mask** (file) - Required - An additional PNG image, less than 2MB in size, and square. Transparent areas of the mask indicate where the original image should be replaced. Other areas of the mask are not decoded by the model and are instead filled with their original image content.

### Request Example
```javascript
import fs from "fs";
import OpenAI, { toFile } from "openai";

const client = new OpenAI();

const rsp = await client.images.edit({
    model: "gpt-image-1",
    image: await toFile(fs.createReadStream("sunlit_lounge.png"), null, {
        type: "image/png",
    }),
    mask: await toFile(fs.createReadStream("mask.png"), null, {
        type: "image/png",
    }),
    prompt: "A sunlit indoor lounge area with a pool containing a flamingo",
});

// Save the image to a file
const image_base64 = rsp.data[0].b64_json;
const image_bytes = Buffer.from(image_base64, "base64");
fs.writeFileSync("lounge.png", image_bytes);
```

### Response
#### Success Response (200)
- **data** (array) - A list of image objects. Each object contains a `b64_json` field with the generated image in base64 format.

#### Response Example
```json
{
  "created": 1589478378,
  "data": [
    {
      "b64_json": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    }
  ]
}
```
```

--------------------------------

### Use Skills with Hosted Shell (JavaScript)

Source: https://developers.openai.com/api/docs/guides/tools-skills

Example demonstrating how to mount skills in a hosted shell environment by attaching them via `tools[].environment.skills` when calling the shell tool.

```APIDOC
## POST /v1/chat/completions (or similar endpoint for responses.create)

### Description
This endpoint allows you to use Agent Skills within a hosted, container-based shell environment. Skills are attached to the `tools` parameter, enabling the model to leverage them for tasks.

### Method
POST

### Endpoint
`/v1/responses/create` (Illustrative, actual endpoint may vary)

### Parameters
#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for generation (e.g., `gpt-5.2`).
- **tools** (array) - Required - A list of tools to use. For skills, this includes:
  - **type** (string) - Required - Must be `"shell"`.
  - **environment** (object) - Required - Defines the shell environment:
    - **type** (string) - Required - Must be `"container_auto"` for hosted environments.
    - **skills** (array) - Required - A list of skills to mount:
      - **type** (string) - Required - Must be `"skill_reference"`.
      - **skill_id** (string) - Required - The ID of the skill.
      - **version** (integer) - Optional - The specific version of the skill to use.
- **input** (string) - Required - The user's input prompt, which may instruct the model to use the mounted skills.

### Request Example
```javascript
import OpenAI from "openai";

const client = new OpenAI();

const response = await client.responses.create({
  model: "gpt-5.2",
  tools: [
    {
      type: "shell",
      environment: {
        type: "container_auto",
        skills: [
          { type: "skill_reference", skill_id: "<skill_id>" },
          { type: "skill_reference", skill_id: "<skill_id>", version: 2 },
        ],
      },
    },
  ],
  input: "Use the skills to add 144 and 377, then compute triangle area with base 9 height 13.",
});

console.log(response.output_text);
```

### Response
#### Success Response (200)
- **output_text** (string) - The result of the model's execution, potentially using the provided skills.
```

--------------------------------

### Example Math Reasoning Output

Source: https://developers.openai.com/api/docs/guides/structured-outputs_context=with_parse

An example of the structured output from the OpenAI API for solving a linear equation. It breaks down the solution into sequential steps, each with a clear explanation and the resulting equation state.

```json
{
  "steps": [
    {
      "explanation": "Start with the equation 8x + 7 = -23.",
      "output": "8x + 7 = -23"
    },
    {
      "explanation": "Subtract 7 from both sides to isolate the term with the variable.",
      "output": "8x = -23 - 7"
    },
    {
      "explanation": "Simplify the right side of the equation.",
      "output": "8x = -30"
    },
    {
      "explanation": "Divide both sides by 8 to solve for x.",
      "output": "x = -30 / 8"
    },
    {
      "explanation": "Simplify the fraction.",
      "output": "x = -15 / 4"
    }
  ],
  "final_answer": "x = -15 / 4"
}
```

--------------------------------

### Deep Research Model Examples (JavaScript)

Source: https://developers.openai.com/api/docs/guides/deep-research

Imports example functions for different deep research functionalities. These are placeholders for actual implementation details and demonstrate how to import specific deep research capabilities.

```javascript
import {
  deepResearchBasic,
  deepResearchClarification,
  deepResearchPromptEnrichment,
  deepResearchRemoteMCP,
} from "./deep-research-examples";
```

--------------------------------

### Server Error Event Example (JSON)

Source: https://developers.openai.com/api/docs/guides/realtime-conversations

An example of an error event that might be received from the server. This event includes details about the error type, code, message, the parameter that caused the error, and the original `event_id`.

```json
{
  "type": "invalid_request_error",
  "code": "invalid_value",
  "message": "Invalid value: 'scooby.dooby.doo' ...",
  "param": "type",
  "event_id": "my_awesome_event"
}
```

--------------------------------

### POST /v1/images/edit (Image Editing with High Input Fidelity - Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=buildings-sprite

This example shows how to edit an existing image with high input fidelity using the `images.edit` method in Python. It takes an image file and a logo file as input and applies the prompt with high fidelity.

```APIDOC
## POST /v1/images/edit

### Description
Edits an image with high input fidelity, preserving details from the input images.

### Method
POST

### Endpoint
/v1/images/edit

### Parameters
#### Request Body
- **model** (string) - Required - The image model to use (e.g., "gpt-image-1").
- **image** (list) - Required - A list of image file objects.
- **prompt** (string) - Required - A text description of the desired image.
- **input_fidelity** (string) - Optional - Sets the input fidelity to "high" or "low" (default).

### Request Example
```python
from openai import OpenAI
import base64

client = OpenAI()

result = client.images.edit(
    model="gpt-image-1",
    image=[open("woman.jpg", "rb"), open("logo.png", "rb")],
    prompt="Add the logo to the woman's top, as if stamped into the fabric.",
    input_fidelity="high"
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("woman_with_logo.png", "wb") as f:
    f.write(image_bytes)
```

### Response
#### Success Response (200)
- **data** (list) - A list of image objects.
  - **b64_json** (string) - Base64 encoded image data.

#### Response Example
```python
{
    "data": [
        {
            "b64_json": "<base64_encoded_image_data>"
        }
    ]
}
```
```

--------------------------------

### Image Generation with Transparent Background (Python - Image API)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&image-generation-model=gpt-image

This Python example shows how to generate an image with a transparent background using the Image API. It sets the `background` parameter to `transparent` and `quality` to `high`.

```APIDOC
## POST /v1/images

### Description
Generates an image with a transparent background using the Image API in Python.

### Method
POST

### Endpoint
/v1/images

### Parameters
#### Request Body
- **model** (string) - Required - The image model to use (e.g., "gpt-image-1").
- **prompt** (string) - Required - The prompt for image generation.
- **size** (string) - Optional - The size of the generated image (e.g., "1024x1024").
- **background** (string) - Optional - Set to "transparent" to enable transparency. Supported for PNG and WEBP.
- **quality** (string) - Optional - The quality of the image. "medium" or "high" recommended for transparency.

### Request Example
```python
from openai import OpenAI
import base64
client = OpenAI()

result = client.images.generate(
    model="gpt-image-1",
    prompt="Draw a 2D pixel art style sprite sheet of a tabby gray cat",
    size="1024x1024",
    background="transparent",
    quality="high",
)

image_base64 = result.json()["data"][0]["b64_json"]
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("sprite.png", "wb") as f:
    f.write(image_bytes)
```

### Response
#### Success Response (200)
- **data** (array) - Contains image objects, each with a `b64_json` field for the base64 encoded image.
```

--------------------------------

### Create Audio Transcription with Segment Timestamps (HTTP)

Source: https://developers.openai.com/api/docs/api-reference/audio/createTranscription

This example shows how to create an audio transcription using the OpenAI API with segment-level timestamp granularities. It requires an audio file and an API key. The response provides the transcribed text and timings for larger segments of audio.

```curl
curl https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F file="@/path/to/file/audio.mp3" \
  -F "timestamp_granularities[]=segment" \
  -F model="whisper-1" \
  -F response_format="verbose_json"

```

```json
{
  "task": "transcribe",
  "language": "english",
  "duration": 8.470000267028809,
  "text": "The beach was a popular spot on a hot summer day. People were swimming in the ocean, building sandcastles, and playing beach volleyball.",
  "segments": [
    {
      "id": 0,
      "seek": 0,
      "start": 0.0,
      "end": 3.319999933242798,
      "text": " The beach was a popular spot on a hot summer day.",
      "tokens": [
        50364, 440, 7534, 390, 257, 3743, 4008, 322, 257, 2368, 4266, 786, 13, 50530
      ],
      "temperature": 0.0,
      "avg_logprob": -0.2860786020755768,
      "compression_ratio": 1.2363636493682861,
      "no_speech_prob": 0.00985979475080967
    },
    ...
  ],
  "usage": {
    "type": "duration",
    "seconds": 9
  }
}

```

--------------------------------

### POST /images/edit - Image Editing with High Input Fidelity (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=clay-garden-scene

This Python example shows how to edit an image using the OpenAI API with high input fidelity. It sends the base image, a logo image, and a prompt to the API. By setting `input_fidelity` to 'high', the API ensures that the logo is accurately integrated into the woman's top, preserving fine details.

```APIDOC
## POST /images/edit

### Description
Edits an image using a mask and prompt, with high input fidelity enabled.

### Method
POST

### Endpoint
/images/edit

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for image editing (e.g., "gpt-image-1").
- **image** (list) - Required - A list containing image file objects.
- **prompt** (string) - Required - A text description of the desired image edits.
- **input_fidelity** (string) - Optional - Set to "high" to enable high input fidelity. Defaults to "low".
- **mask** (list) - Optional - A list containing mask image file objects.
- **n** (int) - Optional - The number of images to generate. Defaults to 1.
- **size** (string) - Optional - The size of the generated images (e.g., "1024x1024").
- **response_format** (string) - Optional - The format in which the generated images are returned (e.g., "url" or "b64_json"). Defaults to "url".

### Request Example
```python
{
    "model": "gpt-image-1",
    "image": [open("woman.jpg", "rb"), open("logo.png", "rb")],
    "prompt": "Add the logo to the woman's top, as if stamped into the fabric.",
    "input_fidelity": "high"
}
```

### Response
#### Success Response (200)
- **data** (list) - A list of image objects.
  - **url** (string) - The URL of the generated image (if response_format is "url").
  - **b64_json** (string) - Base64 encoded image data (if response_format is "b64_json").

#### Response Example
```python
{
    "data": [
        {
            "url": "<generated_image_url>"
        }
    ]
}
```
```

--------------------------------

### GPT-5.2 Model Migration Recommendations

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=math-practice-drills

Recommendations for migrating from older OpenAI models to GPT-5.2, including suggested reasoning levels and prompting strategies for optimal performance.

```APIDOC
## GPT-5.2 Model Migration Recommendations

### Description
This section outlines the recommended settings and strategies for migrating from various older OpenAI models to GPT-5.2 to ensure optimal performance and compatibility.

### Method
N/A (Informational)

### Endpoint
N/A (Informational)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
None

### Request Example
None

### Response
#### Success Response (200)
None

#### Response Example
None

### Model Migration Guidance:

*   **gpt-5.1**: Use `gpt-5.2` with default settings. It is designed as a drop-in replacement.
*   **o3**: Use `gpt-5.2` with `medium` or `high` reasoning. Start with `medium` reasoning and prompt tuning, then increase to `high` if needed.
*   **gpt-4.1**: Use `gpt-5.2` with `none` reasoning. Begin with `none` and tune prompts; increase reasoning if better performance is required.
*   **o4-mini or gpt-4.1-mini**: Use `gpt-5-mini` with prompt tuning for a suitable replacement.
*   **gpt-4.1-nano**: Use `gpt-5-nano` with prompt tuning for a suitable replacement.

### Prompting Strategies:

*   Experiment with reasoning levels and prompting strategies.
*   Utilize the prompt optimizer for automatic prompt updates based on best practices for GPT-5.2.
```

--------------------------------

### POST /v1/chat/completions - Custom Tools

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=podcast-homepage

This example illustrates how custom tools are defined and used within the Chat Completions API.

```APIDOC
## POST /v1/chat/completions - Custom Tools

### Description
This endpoint allows the use of custom tools within the Chat Completions API. Tools are defined in the `tools` parameter, with custom tool details nested under the `custom` key.

### Method
POST

### Endpoint
/v1/chat/completions

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation (e.g., "gpt-5.2").
- **messages** (array) - Required - A list of message objects representing the conversation history.
  - **role** (string) - Required - The role of the message (e.g., "user", "assistant").
  - **content** (string) - Required - The content of the message.
- **tools** (array) - Optional - A list of tool definitions.
  - **type** (string) - Required - The type of tool (e.g., "custom").
  - **custom** (object) - Required - Configuration for custom tools.
    - **name** (string) - Required - The name of the custom tool.
    - **description** (string) - Optional - A description of what the tool does.

### Request Example
```json
{
  "model": "gpt-5.2",
  "messages": [
    { "role": "user", "content": "Use the code_exec tool to calculate the area of a circle with radius equal to the number of r letters in blueberry" }
  ],
  "tools": [
    {
      "type": "custom",
      "custom": {
        "name": "code_exec",
        "description": "Executes arbitrary python code"
      }
    }
  ]
}
```

### Response
#### Success Response (200)
- **choices** (array) - A list of response choices.
  - **message** (object) - The message object containing the response.
    - **content** (string) - The generated response content, potentially including a tool call.

#### Response Example
```json
{
  "choices": [
    {
      "message": {
        "content": "The number of 'r' letters in 'blueberry' is 2. The area of a circle with radius 2 is approximately 12.57."
      }
    }
  ]
}
```
```

--------------------------------

### Image Generation Call with Mask - Python

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=abstract-orbit

This example demonstrates using the `responses.create` method with a tool for image generation, including a mask. This is part of a multimodal conversation.

```APIDOC
## POST /v1/responses/create

### Description
Creates a multimodal response, including image generation guided by a mask within a conversational context.

### Method
POST

### Endpoint
/v1/responses/create

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use (e.g., "gpt-4o").
- **input** (array) - Required - The conversation history, including user messages with text and image types.
  - **role** (string) - Required - The role of the message sender ('user' or 'assistant').
  - **content** (array) - Required - The content of the message.
    - **type** (string) - Required - The type of content ('input_text' or 'input_image').
    - **text** (string) - Required if type is 'input_text' - The text content.
    - **file_id** (string) - Required if type is 'input_image' - The ID of the uploaded image file.
- **tools** (array) - Required - A list of tools to use for the response.
  - **type** (string) - Required - The type of tool ('image_generation').
  - **quality** (string) - Optional - The quality of the generated image ('standard' or 'high').
  - **input_image_mask** (object) - Optional - Specifies the mask for image generation.
    - **file_id** (string) - Required - The ID of the uploaded mask image file.

### Request Example
```python
from openai import OpenAI
client = OpenAI()

fileId = create_file("sunlit_lounge.png")
maskId = create_file("mask.png")

response = client.responses.create(
    model="gpt-4o",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "generate an image of the same sunlit indoor lounge area with a pool but the pool should contain a flamingo",
                },
                {
                    "type": "input_image",
                    "file_id": fileId,
                }
            ],
        },
    ],
    tools=[
        {
            "type": "image_generation",
            "quality": "high",
            "input_image_mask": {
                "file_id": maskId,
            }
        },
    ],
)

image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if image_data:
    image_base64 = image_data[0]
    with open("lounge.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
```

### Response
#### Success Response (200)
- **output** (array) - The response from the model, which may include image generation calls.
  - **type** (string) - The type of output ('image_generation_call').
  - **result** (string) - The base64 encoded image data.

#### Response Example
```json
{
  "output": [
    {
      "type": "image_generation_call",
      "result": "...base64_encoded_image_data..."
    }
  ]
}
```
```

--------------------------------

### Image Generation API - Transparent Background (Python Client)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=clay-garden-scene

This Python example demonstrates generating an image with a transparent background using the `openai.images.generate` method. It specifies the `background` parameter as `transparent` and `quality` as `high`.

```APIDOC
## POST /v1/images

### Description
Generates an image with a transparent background using the `images.generate` endpoint.

### Method
POST

### Endpoint
/v1/images

### Parameters
#### Request Body
- **model** (string) - Required - The image generation model to use (e.g., "gpt-image-1").
- **prompt** (string) - Required - A description of the desired image.
- **size** (string) - Optional - The desired size of the generated image (e.g., "1024x1024").
- **background** (string) - Optional - Set to "transparent" to enable transparency. Supported for PNG and WEBP output formats.
- **quality** (string) - Optional - "medium" or "high" recommended for transparency.

### Request Example
```json
{
  "model": "gpt-image-1",
  "prompt": "Draw a 2D pixel art style sprite sheet of a tabby gray cat",
  "size": "1024x1024",
  "background": "transparent",
  "quality": "high"
}
```

### Response
#### Success Response (200)
- **data** (array) - Contains the generated image data.
    - **b64_json** (string) - Base64 encoded image data.

#### Response Example
```json
{
  "created": 1678886400,
  "data": [
    {
      "b64_json": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    }
  ]
}
```
```

--------------------------------

### Image Generation with Transparent Background (Python - Images API)

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=spacecraft-dashboard

This Python example shows how to generate an image with a transparent background using the `client.images.generate` method. It sets the `background` parameter to `transparent` and `quality` to `high`.

```APIDOC
## POST /v1/images

### Description
Generates an image with a transparent background using the `client.images.generate` method in Python.

### Method
POST

### Endpoint
/v1/images

### Parameters
#### Request Body
- **model** (string) - Required - The image generation model to use (e.g., "gpt-image-1").
- **prompt** (string) - Required - A description of the desired image.
- **size** (string) - Optional - The desired size of the generated image (e.g., "1024x1024").
- **background** (string) - Optional - Set to "transparent" to enable transparency. Supported for PNG and WEBP output formats.
- **quality** (string) - Optional - Recommended to be "medium" or "high" for transparency.

### Request Example
```json
{
  "model": "gpt-image-1",
  "prompt": "Draw a 2D pixel art style sprite sheet of a tabby gray cat",
  "size": "1024x1024",
  "background": "transparent",
  "quality": "high"
}
```

### Response
#### Success Response (200)
- **data** (array) - Contains the generated image details.
  - **b64_json** (string) - Base64 encoded image data.

#### Response Example
```json
{
  "data": [
    {
      "b64_json": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    }
  ]
}
```
```

--------------------------------

### POST /v1/chat/completions - Reasoning Effort

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=micro-habit-tracker

This example shows the equivalent call using the Chat Completions API, highlighting the difference in parameter usage for reasoning effort.

```APIDOC
## POST /v1/chat/completions

### Description
Generates a chat completion with a specified reasoning effort.

### Method
POST

### Endpoint
/v1/chat/completions

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation.
- **messages** (array) - Required - A list of message objects representing the conversation.
  - **role** (string) - Required - The role of the message (e.g., "user").
  - **content** (string) - Required - The content of the message.
- **reasoning_effort** (string) - Optional - The level of reasoning effort (e.g., "none").

### Request Example
```json
{
  "model": "gpt-5.2",
  "messages": [
    {
      "role": "user",
      "content": "How much gold would it take to coat the Statue of Liberty in a 1mm layer?"
    }
  ],
  "reasoning_effort": "none"
}
```

### Response
#### Success Response (200)
- **choices** (array) - A list of chat completion choices.
  - **message** (object) - The message from the model.
    - **content** (string) - The content of the message.

#### Response Example
```json
{
  "choices": [
    {
      "message": {
        "content": "[Generated response text]"
      }
    }
  ]
}
```
```

--------------------------------

### List Fine-Tuning Checkpoints Response Example

Source: https://developers.openai.com/api/docs/api-reference/fine-tuning/list-checkpoints

This is an example of the JSON response when listing fine-tuning checkpoints. It includes metadata about the list, such as `object`, `first_id`, `last_id`, and `has_more`, along with an array of `data` objects, each representing a fine-tuning job checkpoint.

```json
{
  "object": "list",
  "data": [
    {
      "object": "fine_tuning.job.checkpoint",
      "id": "ftckpt_zc4Q7MP6XxulcVzj4MZdwsAB",
      "created_at": 1721764867,
      "fine_tuned_model_checkpoint": "ft:gpt-4o-mini-2024-07-18:my-org:custom-suffix:96olL566:ckpt-step-2000",
      "metrics": {
        "full_valid_loss": 0.134,
        "full_valid_mean_token_accuracy": 0.874
      },
      "fine_tuning_job_id": "ftjob-abc123",
      "step_number": 2000
    },
    {
      "object": "fine_tuning.job.checkpoint",
      "id": "ftckpt_enQCFmOTGj3syEpYVhBRLTSy",
      "created_at": 1721764800,
      "fine_tuned_model_checkpoint": "ft:gpt-4o-mini-2024-07-18:my-org:custom-suffix:7q8mpxmy:ckpt-step-1000",
      "metrics": {
        "full_valid_loss": 0.167,
        "full_valid_mean_token_accuracy": 0.781
      },
      "fine_tuning_job_id": "ftjob-abc123",
      "step_number": 1000
    }
  ],
  "first_id": "ftckpt_zc4Q7MP6XxulcVzj4MZdwsAB",
  "last_id": "ftckpt_enQCFmOTGj3syEpYVhBRLTSy",
  "has_more": true
}
```

--------------------------------

### Preambles

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=camping-gear-checklist-5.2

Enables GPT-5.2 to generate user-visible explanations before invoking tools, improving transparency and debuggability.

```APIDOC
## Preambles

### Description
Preambles are brief explanations generated by GPT-5.2 before it invokes a tool or function. They outline the model's intent or plan, appearing after the chain-of-thought and before the tool call. This feature enhances transparency, debuggability, and user confidence.

### Method
N/A (Enabled via system or developer instructions)

### Endpoint
N/A (Enabled via system or developer instructions)

### Parameters
#### System/Developer Instruction
- **Instruction Text** (string) - Required - Provide an instruction such as: "Before you call a tool, explain why you are calling it."

### Request Example
```json
{
  "messages": [
    {"role": "system", "content": "Before you call a tool, explain why you are calling it."}, 
    {"role": "user", "content": "What is the weather in London?"}
  ]
}
```

### Response
#### Success Response (200)
- **Preamble** (string) - The generated explanation before the tool call.
- **Tool Call** (object) - The actual tool invocation.

#### Response Example
```json
{
  "role": "assistant",
  "content": null,
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"location\": \"London\"}"
      }
    }
  ],
  "í_preamble": "I need to call the get_weather tool to find out the current weather conditions in London."
}
```
```

--------------------------------

### Multi-turn Image Generation Example

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=winter-wolf-portrait

Demonstrates how to perform multi-turn image generation using the `previous_response_id` parameter to refine images across conversation turns.

```APIDOC
## Multi-turn Image Generation

### Description
This example shows how to use the Responses API for multi-turn image generation. First, an initial image is generated. Then, a follow-up request is made using the `previous_response_id` of the initial response to refine the image based on new instructions.

### Method
POST

### Endpoint
/responses

### Request Example (JavaScript)
```javascript
import OpenAI from "openai";
const openai = new OpenAI();

// Initial image generation
const response = await openai.responses.create({
  model: "gpt-5",
  input:
    "Generate an image of gray tabby cat hugging an otter with an orange scarf",
  tools: [{ type: "image_generation" }],
});

const imageData = response.output
  .filter((output) => output.type === "image_generation_call")
  .map((output) => output.result);

if (imageData.length > 0) {
  const imageBase64 = imageData[0];
  const fs = await import("fs");
  fs.writeFileSync("cat_and_otter.png", Buffer.from(imageBase64, "base64"));
}

// Follow up: Refine the image
const response_fwup = await openai.responses.create({
  model: "gpt-5",
  previous_response_id: response.id, // Use the ID from the previous response
  input: "Now make it look realistic",
  tools: [{ type: "image_generation" }],
});

const imageData_fwup = response_fwup.output
  .filter((output) => output.type === "image_generation_call")
  .map((output) => output.result);

if (imageData_fwup.length > 0) {
  const imageBase64 = imageData_fwup[0];
  const fs = await import("fs");
  fs.writeFileSync(
    "cat_and_otter_realistic.png",
    Buffer.from(imageBase64, "base64")
  );
}
```

### Request Example (Python)
```python
from openai import OpenAI
import base64

client = OpenAI()

# Initial image generation
response = client.responses.create(
    model="gpt-5",
    input="Generate an image of gray tabby cat hugging an otter with an orange scarf",
    tools=[{"type": "image_generation"}],
)

image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if image_data:
    image_base64 = image_data[0]
    with open("cat_and_otter.png", "wb") as f:
        f.write(base64.b64decode(image_base64))

# Follow up: Refine the image
response_fwup = client.responses.create(
    model="gpt-5",
    previous_response_id=response.id, # Use the ID from the previous response
    input="Now make it look realistic",
    tools=[{"type": "image_generation"}],
)

image_data_fwup = [
    output.result
    for output in response_fwup.output
    if output.type == "image_generation_call"
]

if image_data_fwup:
    image_base64 = image_data_fwup[0]
    with open("cat_and_otter_realistic.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
```

### Response
(See Success Response details in the POST /responses section above. The `previous_response_id` parameter facilitates the continuation of the image generation process.)
```

--------------------------------

### FastMCP Server Implementation (Python)

Source: https://developers.openai.com/api/docs/mcp

A Python server implementation using FastMCP for integrating search and fetch tools with ChatGPT. It includes basic setup for logging, environment variable configuration for OpenAI API key and vector store ID.

```python
"""
Sample MCP Server for ChatGPT Integration

This server implements the Model Context Protocol (MCP) with search and fetch
capabilities designed to work with ChatGPT's chat and deep research features.
"""

import logging
import os
from typing import Dict, List, Any

from fastmcp import FastMCP
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
VECTOR_STORE_ID = os.environ.get("VECTOR_STORE_ID", "")

```

--------------------------------

### Create Thread with Messages

Source: https://developers.openai.com/api/docs/api-reference/threads/createThread

This example shows how to create a thread and immediately populate it with user messages using the OpenAI API. It includes authentication headers and the API version. The response contains the thread details, similar to creating an empty thread.

```curl
curl https://api.openai.com/v1/threads \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $OPENAI_API_KEY" \
-H "OpenAI-Beta: assistants=v2" \
-d '{
    "messages": [{
      "role": "user",
      "content": "Hello, what is AI?"
    }, { 
      "role": "user",
      "content": "How does AI work? Explain it in simple terms."
    }]
  }'
```

```json
{
  "id": "thread_abc123",
  "object": "thread",
  "created_at": 1699014083,
  "metadata": {},
  "tool_resources": {}
}
```

--------------------------------

### Image Generation with Mask - Node.js

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=animation

This example demonstrates using the `responses.create` method with image generation and a mask in Node.js. It allows for more complex interactions where text, images, and masks are combined.

```APIDOC
## POST /v1/responses/create

### Description
Generates content using a multimodal model, supporting text, images, and tools like image generation with masks.

### Method
POST

### Endpoint
/v1/responses/create

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The multimodal model to use. Example: `gpt-4o`
- **input** (array) - Required - An array of input messages, each with a role and content.
  - **role** (string) - Required - The role of the message sender (`user` or `assistant`).
  - **content** (array) - Required - An array of content blocks, which can be text or images.
    - **type** (string) - Required - The type of content (`input_text` or `input_image`).
    - **text** (string) - Required if type is `input_text` - The text content.
    - **file_id** (string) - Required if type is `input_image` - The ID of the uploaded image file.
- **tools** (array) - Optional - A list of tools to use for the response.
  - **type** (string) - Required - The type of tool (`image_generation`).
  - **quality** (string) - Optional - The quality of the generated image (`standard` or `high`).
  - **input_image_mask** (object) - Optional - Configuration for the image mask.
    - **file_id** (string) - Required - The ID of the uploaded mask file.

### Request Example
```javascript
import OpenAI from "openai";
const openai = new OpenAI();

const fileId = await createFile("sunlit_lounge.png");
const maskId = await createFile("mask.png");

const response = await openai.responses.create({
  model: "gpt-4o",
  input: [
    {
      role: "user",
      content: [
        {
          type: "input_text",
          text: "generate an image of the same sunlit indoor lounge area with a pool but the pool should contain a flamingo",
        },
        {
          type: "input_image",
          file_id: fileId,
        }
      ],
    },
  ],
  tools: [
    {
      type: "image_generation",
      quality: "high",
      input_image_mask: {
        file_id: maskId,
      }
    },
  ],
});

const imageData = response.output
  .filter((output) => output.type === "image_generation_call")
  .map((output) => output.result);

if (imageData.length > 0) {
  const imageBase64 = imageData[0];
  const fs = await import("fs");
  fs.writeFileSync("lounge.png", Buffer.from(imageBase64, "base64"));
}
```

### Response
#### Success Response (200)
- **output** (array) - An array of tool outputs.
  - **type** (string) - The type of output (`image_generation_call`).
  - **result** (string) - The base64 encoded image data.

#### Response Example
```json
{
  "output": [
    {
      "type": "image_generation_call",
      "result": "/9j/4AAQSkZJRgABAQEASABIAAD..."
    }
  ]
}
```
```

--------------------------------

### POST /v1/images/edit - Image Editing with High Input Fidelity (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=alien

This Python example demonstrates how to perform image editing with high input fidelity using the `images.edit` endpoint. It utilizes local image files and a prompt, ensuring high fidelity preservation of input details.

```APIDOC
## POST /v1/images/edit

### Description
Edits an existing image using Python with a specified prompt and high input fidelity. This ensures that details from the input images are accurately preserved in the output.

### Method
POST

### Endpoint
/v1/images/edit

### Parameters
#### Request Body
- **model** (string) - Required - The image model to use (e.g., "gpt-image-1").
- **image** (list) - Required - A list of image file objects to be edited.
- **prompt** (string) - Required - A text description of the desired edits.
- **input_fidelity** (string) - Optional - The desired input fidelity ('high' or 'low'). Defaults to 'low'.

### Request Example
```python
result = client.images.edit(
    model="gpt-image-1",
    image=[open("woman.jpg", "rb"), open("logo.png", "rb")],
    prompt="Add the logo to the woman's top, as if stamped into the fabric.",
    input_fidelity="high"
)
```

### Response
#### Success Response (200)
- **data** (list) - A list containing the generated image data.
  - **b64_json** (string) - The generated image in base64 format.

#### Response Example
```json
{
  "data": [
    {
      "b64_json": "<base64_encoded_image_data>"
    }
  ]
}
```
```

--------------------------------

### Image Generation with Transparent Background (cURL)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=construction-crew

This example demonstrates how to generate an image with a transparent background using a cURL command. It sets the background to 'transparent' and quality to 'high'.

```APIDOC
## POST /v1/images

### Description
Generates an image with a transparent background using a cURL command.

### Method
POST

### Endpoint
/v1/images

### Parameters
#### Request Body
- **prompt** (string) - Required - The prompt for image generation.
- **quality** (string) - Optional - "high" for best transparency results.
- **size** (string) - Optional - The desired size of the image (e.g., "1024x1024").
- **background** (string) - Optional - Set to "transparent" to enable transparency.

### Request Example
```bash
curl -X POST "https://api.openai.com/v1/images" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-type: application/json" \
    -d '{ \
        "prompt": "Draw a 2D pixel art style sprite sheet of a tabby gray cat", \
        "quality": "high", \
        "size": "1024x1024", \
        "background": "transparent" \
    }' | jq -r 'data[0].b64_json' | base64 --decode > sprite.png
```

### Response
#### Success Response (200)
The response is piped to a file named 'sprite.png' after base64 decoding.
```

--------------------------------

### GET /fine_tuning/jobs/{fine_tuning_job_id}

Source: https://developers.openai.com/api/docs/api-reference/realtime_client_events

This endpoint retrieves information about a specific fine-tuning job. It allows you to get details about a fine-tuning job by its ID.

```APIDOC
## GET /fine_tuning/jobs/{fine_tuning_job_id}

### Description
Retrieves information about a specific fine-tuning job.

### Method
GET

### Endpoint
/fine_tuning/jobs/{fine_tuning_job_id}

### Parameters
#### Path Parameters
- **fine_tuning_job_id** (string) - Required - The ID of the fine-tuning job to retrieve.

### Request Example
```json
{}
```

### Response
#### Success Response (200)
- **id** (string) - The ID of the fine-tuning job.
- **status** (string) - The status of the fine-tuning job.

#### Response Example
```json
{
  "id": "ft-AF1Wo5J133Wv",
  "object": "fine_tuning.job",
  "model": "gpt-3.5-turbo",
  "created_at": 1677664797,
  "training_file": "file-XjGxS3KTG0uNmCyj",
  "status": "pending"
}
```
```

--------------------------------

### Realtime Session Creation

Source: https://developers.openai.com/api/docs/api-reference/realtime-server-events/input_audio_buffer/speech_started

Configure and create a realtime session with various parameters to control model behavior, audio input/output, and response modalities.

```APIDOC
## POST /v1/realtime/sessions

### Description
Creates a new realtime session for interacting with the Realtime API.

### Method
POST

### Endpoint
/v1/realtime/sessions

### Parameters
#### Request Body
- **type** (string) - Required - The type of session to create. Must be `"realtime"`.
- **audio** (RealtimeAudioConfig) - Optional - Configuration for input and output audio.
  - **input** (AudioInputConfig) - Optional - Configuration for audio input.
  - **output** (AudioOutputConfig) - Optional - Configuration for audio output.
- **include** (array of string) - Optional - Additional fields to include in server outputs. Example: `["item.input_audio_transcription.logprobs"]`.
- **instructions** (string) - Optional - Default system instructions to guide the model's responses and behavior.
- **max_output_tokens** (number or "inf") - Optional - Maximum number of output tokens for a single assistant response. Accepts an integer between 1 and 4096 or `"inf"`. Defaults to `"inf"`.
- **model** (string) - Optional - The Realtime model to use for the session. Accepts specific model names like `"gpt-realtime"`, `"gpt-realtime-2025-08-28"`, `"gpt-4o-realtime-preview"`, etc.
- **output_modalities** (array of string) - Optional - The set of modalities the model can respond with. Defaults to `["audio"]`. Can be `["text"]` for text-only responses. Cannot be both `"text"` and `"audio"`.
- **prompt** (ResponsePrompt) - Optional - Reference to a prompt template and its variables.
  - **id** (string) - Required - The ID of the prompt template.
  - **variables** (object) - Optional - Variables to populate the prompt template.
  - **version** (string) - Optional - The version of the prompt template.
- **tool_choice** (RealtimeToolChoiceConfig) - Optional - Configuration for how the model chooses tools.
- **tools** (RealtimeToolsConfig) - Optional - Tools available to the model.
  - **McpTool** (object) - Optional - Configuration for MCP tools.
- **tracing** (RealtimeTracingConfig) - Optional - Configuration for writing session traces to the Traces Dashboard. Set to `null` to disable.
- **truncation** (RealtimeTruncation) - Optional - Configuration for how the conversation is truncated when the token limit is exceeded.

### Request Example
```json
{
  "type": "realtime",
  "audio": {
    "input": {
      "encoding": "linear16",
      "sample_rate": 16000,
      "channels": 1
    },
    "output": {
      "encoding": "linear16",
      "sample_rate": 24000
    }
  },
  "instructions": "Be concise and friendly.",
  "model": "gpt-4o-realtime-preview",
  "output_modalities": ["audio", "text"]
}
```

### Response
#### Success Response (200)
- **session_id** (string) - The unique identifier for the created session.
- **type** (string) - The type of the created session.
- **created_at** (string) - Timestamp when the session was created.

#### Response Example
```json
{
  "session_id": "sess_abc123xyz789",
  "type": "realtime",
  "created_at": "2024-07-26T10:00:00Z"
}
```
```

--------------------------------

### Realtime Session Creation

Source: https://developers.openai.com/api/docs/api-reference/realtime-server-events/response/output_item/done

Configuration for creating a real-time session, including audio settings and system instructions.

```APIDOC
## POST /websites/developers_openai_api/realtime/sessions

### Description
Creates a real-time session for interacting with the OpenAI API. This endpoint allows for configuration of audio input/output, system instructions, and other session parameters.

### Method
POST

### Endpoint
/websites/developers_openai_api/realtime/sessions

### Parameters
#### Request Body
- **type** (string) - Required - The type of session to create. Must be `realtime` for the Realtime API.
- **audio** (object) - Optional - Configuration for input and output audio.
  - **input** (object) - Configuration for audio input.
  - **output** (object) - Configuration for audio output.
- **include** (array of strings) - Optional - Additional fields to include in server outputs. Example: `["item.input_audio_transcription.logprobs"]`.
- **instructions** (string) - Optional - Default system instructions prepended to model calls to guide model behavior and audio output.
- **semantic_vad** (object) - Optional - Configuration for server-side semantic turn detection.
  - **type** (string) - Required - Must be `semantic_vad`.
  - **create_response** (boolean) - Optional - Whether to automatically generate a response when a VAD stop event occurs.
  - **eagerness** (string) - Optional - The eagerness of the model to respond. Accepts `low`, `medium`, `high`, or `auto`. Defaults to `auto`.
  - **interrupt_response** (boolean) - Optional - Whether to automatically interrupt any ongoing response when a VAD start event occurs.
- **server_vad** (object) - Optional - Configuration for server-side VAD.
  - **create_response** (boolean) - Optional - Whether to automatically generate a response when a VAD stop event occurs.
  - **interrupt_response** (boolean) - Optional - Whether to automatically interrupt any ongoing response when a VAD start event occurs.
  - **idle_timeout_ms** (number) - Optional - Timeout in milliseconds after which a model response will be triggered automatically. Minimum: 5000, Maximum: 30000.
  - **prefix_padding_ms** (number) - Optional - Amount of audio in milliseconds to include before VAD detected speech. Defaults to 300ms.
  - **silence_duration_ms** (number) - Optional - Duration of silence in milliseconds to detect speech stop. Defaults to 500ms.
  - **threshold** (number) - Optional - Activation threshold for VAD (0.0 to 1.0). Defaults to 0.5.
- **voice** (string) - Optional - The voice the model uses to respond. Cannot be changed after the model has responded with audio at least once. Accepts `alloy`, `ash`, `ballad`, `coral`, `echo`, `sage`, `shimmer`, `verse`, `marin`, `cedar`.

### Request Example
```json
{
  "type": "realtime",
  "audio": {
    "input": {},
    "output": {}
  },
  "instructions": "Act like a helpful assistant.",
  "semantic_vad": {
    "type": "semantic_vad",
    "eagerness": "high"
  },
  "voice": "alloy"
}
```

### Response
#### Success Response (200)
- **session_id** (string) - The unique identifier for the created session.
- **status** (string) - The status of the session.

#### Response Example
```json
{
  "session_id": "sess_abc123xyz789",
  "status": "active"
}
```
```

--------------------------------

### POST /v1/chat/completions - Reasoning Effort

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=artisan-csa

This example shows how to set the reasoning effort for the Chat Completions API.

```APIDOC
## POST /v1/chat/completions - Reasoning Effort

### Description
This endpoint generates a chat completion with a specified reasoning effort.

### Method
POST

### Endpoint
/v1/chat/completions

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation.
- **messages** (array) - Required - An array of message objects.
  - **role** (string) - Required - The role of the message (e.g., "user").
  - **content** (string) - Required - The content of the message.
- **reasoning_effort** (string) - Required - The level of reasoning effort (e.g., "none").

### Request Example
```json
{
  "model": "gpt-5.2",
  "messages": [
    {
      "role": "user",
      "content": "How much gold would it take to coat the Statue of Liberty in a 1mm layer?"
    }
  ],
  "reasoning_effort": "none"
}
```

### Response
#### Success Response (200)
- **choices** (array) - An array of completion choices.
  - **message** (object) - The message object.
    - **content** (string) - The content of the message.

#### Response Example
```json
{
  "choices": [
    {
      "message": {
        "content": "The calculated amount of gold..."
      }
    }
  ]
}
```
```

--------------------------------

### Realtime Session Configuration

Source: https://developers.openai.com/api/docs/api-reference/realtime-client-events/input_audio_buffer/commit

Configure a realtime session with various parameters to control audio, model behavior, output, and more.

```APIDOC
## POST /sessions

### Description
Creates a new realtime session with specified configuration.

### Method
POST

### Endpoint
/sessions

### Parameters
#### Request Body
- **type** (string) - Required - The type of session to create. Must be `"realtime"`.
- **audio** (RealtimeAudioConfig) - Optional - Configuration for input and output audio.
  - **input** (object) - Optional - Audio input configuration.
  - **output** (object) - Optional - Audio output configuration.
- **include** (array of string) - Optional - Additional fields to include in server outputs. Example: `"item.input_audio_transcription.logprobs"`.
- **instructions** (string) - Optional - Default system instructions to guide the model's responses and behavior.
- **max_output_tokens** (number or "inf") - Optional - Maximum number of output tokens for a single assistant response. Accepts an integer between 1 and 4096 or `"inf"`. Defaults to `"inf"`.
- **model** (string) - Optional - The Realtime model to use for the session. Accepts specific model names like `"gpt-realtime"`, `"gpt-realtime-2025-08-28"`, `"gpt-4o-realtime-preview"`, and others.
- **output_modalities** (array of string) - Optional - The set of modalities the model can respond with. Defaults to `["audio"]`. Can be `["text"]` for text-only responses. Cannot be both `"text"` and `"audio"`.
- **prompt** (ResponsePrompt) - Optional - Reference to a prompt template and its variables.
- **tool_choice** (RealtimeToolChoiceConfig) - Optional - Configuration for how the model chooses tools.
- **tools** (RealtimeToolsConfig) - Optional - Tools available to the model.
- **tracing** (RealtimeTracingConfig) - Optional - Configuration for writing session traces to the Traces Dashboard. Set to `null` to disable.
- **truncation** (RealtimeTruncation) - Optional - Configuration for how the conversation is truncated when the token limit is exceeded.

### Request Example
```json
{
  "type": "realtime",
  "audio": {
    "input": {},
    "output": {}
  },
  "instructions": "Be concise and friendly.",
  "model": "gpt-4o-realtime-preview",
  "output_modalities": ["audio", "text"]
}
```

### Response
#### Success Response (200)
- **session_id** (string) - The unique identifier for the created session.
- **type** (string) - The type of the created session.
- **created_at** (string) - Timestamp of session creation.

#### Response Example
```json
{
  "session_id": "sess_abc123xyz789",
  "type": "realtime",
  "created_at": "2024-07-26T10:00:00Z"
}
```
```

--------------------------------

### Recreating Vector Stores

Source: https://developers.openai.com/api/docs/assistants/tools/file-search

Provides code examples for recreating vector stores, useful for managing or updating stored files.

```APIDOC
## Recreating Vector Stores

### Description
This section provides code examples for recreating vector stores, which can be useful for updating or managing stored files.

### Python Example
```python
from openai import OpenAI
from openai.pagination import SyncCursorPage

client = OpenAI()

# Get all files from an existing vector store
all_files = list(client.vector_stores.files.list("vs_expired"))

# Create a new vector store
vector_store = client.vector_stores.create(name="rag-store")

# Update an assistant or thread to use the new vector store (example for assistant)
client.beta.assistants.update(
    "asst_abc123",
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

# Add files to the new vector store in batches
for file_batch in chunked(all_files, 100): # Assuming chunked is a helper function
    client.vector_stores.file_batches.create_and_poll(
        vector_store_id=vector_store.id,
        file_ids=[file.id for file in file_batch]
    )
```

### Node.js Example
```javascript
const OpenAI = require('openai');
const _ = require('lodash'); // Assuming lodash is used for chunking

const openai = new OpenAI();

async function recreateVectorStore() {
  const fileIds = [];
  // Get all file IDs from an existing vector store
  for await (const file of openai.vectorStores.files.list("vs_toWTk90YblRLCkbE2xSVoJlF")) {
    fileIds.push(file.id);
  }

  // Create a new vector store
  const vectorStore = await openai.vectorStores.create({
    name: "rag-store",
  });

  // Update an assistant or thread to use the new vector store (example for thread)
  await openai.beta.threads.update("thread_abcd", {
    tool_resources: { file_search: { vector_store_ids: [vectorStore.id] } },
  });

  // Add files to the new vector store in batches
  for (const fileBatch of _.chunk(fileIds, 100)) {
    await openai.vectorStores.fileBatches.create(vectorStore.id, {
      file_ids: fileBatch,
    });
  }
}

recreateVectorStore();
```
```

--------------------------------

### POST /v1/responses - Reasoning Effort

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=artisan-csa

This example demonstrates how to set the reasoning effort for the Responses API.

```APIDOC
## POST /v1/responses - Reasoning Effort

### Description
This endpoint generates a response with a specified reasoning effort.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation.
- **input** (string) - Required - The prompt for the model.
- **reasoning** (object) - Required - Configuration for reasoning.
  - **effort** (string) - Required - The level of reasoning effort (e.g., "none").

### Request Example
```json
{
  "model": "gpt-5.2",
  "input": "How much gold would it take to coat the Statue of Liberty in a 1mm layer?",
  "reasoning": {
    "effort": "none"
  }
}
```

### Response
#### Success Response (200)
- **response** (string) - The generated response from the model.

#### Response Example
```json
{
  "response": "The calculated amount of gold..."
}
```
```

--------------------------------

### Image Generation with Transparent Background (Node.js)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=school-lab

This example shows how to generate an image with a transparent background using the OpenAI Node.js client. It configures the `background` parameter to `transparent` and suggests `medium` or `high` quality for optimal results.

```APIDOC
## POST /v1/images

### Description
Generates an image with a transparent background using the OpenAI API.

### Method
POST

### Endpoint
/v1/images

### Parameters
#### Query Parameters
- **model** (string) - Required - The model to use for image generation (e.g., `gpt-image-1`).
- **prompt** (string) - Required - A text description of the desired image.
- **size** (string) - Optional - The desired size of the generated image (e.g., `1024x1024`).
- **background** (string) - Optional - Set to `transparent` to enable transparency. Supported for `png` and `webp` output formats.
- **quality** (string) - Optional - Set to `medium` or `high` for best transparency results.

### Request Example
```javascript
import OpenAI from "openai";
import fs from "fs";

const client = new OpenAI();

const response = await client.responses.create({
  model: "gpt-5",
  input: "Draw a 2D pixel art style sprite sheet of a tabby gray cat",
  tools: [
    {
      type: "image_generation",
      background: "transparent",
      quality: "high",
    },
  ],
});

const imageData = response.output
  .filter((output) => output.type === "image_generation_call")
  .map((output) => output.result);

if (imageData.length > 0) {
  const imageBase64 = imageData[0];
  const imageBuffer = Buffer.from(imageBase64, "base64");
  fs.writeFileSync("sprite.png", imageBuffer);
}
```

### Response
#### Success Response (200)
- **output** (array) - An array of tool outputs.
  - **type** (string) - The type of tool output, e.g., `image_generation_call`.
  - **result** (string) - The generated image data in base64 format.
```

--------------------------------

### Image Generation with Transparency (cURL)

Source: https://developers.openai.com/api/docs/guides/image-generation_image-generation-model=gpt-image

Example of generating an image with a transparent background using cURL.

```APIDOC
## POST /v1/images

### Description
Generates an image with a transparent background.

### Method
POST

### Endpoint
/v1/images

### Parameters
#### Request Body
- **prompt** (string) - Required - A text description of the desired image.
- **quality** (string) - Optional - The quality of the generated image. Supports `medium` or `high` for transparency.
- **size** (string) - Optional - The desired size of the generated image (e.g., `1024x1024`).
- **background** (string) - Optional - Set to `transparent` to enable transparent backgrounds. Only supported with `png` and `webp` output formats.

### Request Example
```bash
curl -X POST "https://api.openai.com/v1/images" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-type: application/json" \
    -d '{ \
        "prompt": "Draw a 2D pixel art style sprite sheet of a tabby gray cat", \
        "quality": "high", \
        "size": "1024x1024", \
        "background": "transparent" \
    }' | jq -r 'data[0].b64_json' | base64 --decode > sprite.png
```

### Response
#### Success Response (200)
- **data** (array) - Contains the generated image data.
  - **b64_json** (string) - The base64 encoded image data.
```

--------------------------------

### Image Generation API

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=isometric-icons

This section details how to generate an initial image using the OpenAI API. It includes examples in Python and JavaScript, showing how to specify the model, input prompt, and image generation tool.

```APIDOC
## POST /v1/responses (Image Generation)

### Description
Generates an image based on a text prompt. This endpoint allows for the creation of new images using specified models and tools.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation (e.g., "gpt-5").
- **input** (string) - Required - The text prompt describing the desired image.
- **tools** (array) - Required - A list of tools to use, including `{"type": "image_generation"}`.

### Request Example (Python)
```python
import openai
import base64

response = openai.responses.create(
    model="gpt-5",
    input="Generate an image of gray tabby cat hugging an otter with an orange scarf",
    tools=[{"type": "image_generation"}],
)

image_generation_calls = [
    output
    for output in response.output
    if output.type == "image_generation_call"
]

image_data = [output.result for output in image_generation_calls]

if image_data:
    image_base64 = image_data[0]
    with open("cat_and_otter.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
```

### Request Example (JavaScript)
```javascript
import OpenAI from "openai";
const openai = new OpenAI();

const response = await openai.responses.create({
  model: "gpt-5",
  input:
    "Generate an image of gray tabby cat hugging an otter with an orange scarf",
  tools: [{ type: "image_generation" }],
});

const imageGenerationCalls = response.output.filter(
  (output) => output.type === "image_generation_call"
);

const imageData = imageGenerationCalls.map((output) => output.result);

if (imageData.length > 0) {
  const imageBase64 = imageData[0];
  const fs = await import("fs");
  fs.writeFileSync("cat_and_otter.png", Buffer.from(imageBase64, "base64"));
}
```

### Response
#### Success Response (200)
- **output** (array) - Contains results of the tool calls, including `image_generation_call` objects with base64 encoded image data.

#### Response Example (Conceptual)
```json
{
  "output": [
    {
      "type": "image_generation_call",
      "id": "img_abc123",
      "result": "<base64_encoded_image_data>"
    }
  ]
}
```
```

--------------------------------

### Migrating Threads to Conversations

Source: https://developers.openai.com/api/docs/assistants/migration

Code example demonstrating how to backfill an old thread by converting its messages into the format required for creating a new conversation.

```APIDOC
## Migrating Threads to Conversations

### Description
This Python code snippet shows how to iterate through messages of an old thread and convert them into a format suitable for creating a new conversation using the Responses API.

### Method
POST

### Endpoint
/v1/conversations

### Parameters
#### Path Parameters
- **thread_id** (string) - Required - The ID of the thread to backfill.

#### Query Parameters
None

#### Request Body
- **items** (array) - Required - An array of message objects to create the conversation.
  - **role** (string) - Required - The role of the message sender ('user' or 'assistant').
  - **content** (array) - Required - An array of content objects within the message.
    - **type** (string) - Required - The type of content ('input_text', 'output_text', 'input_image').
    - **text** (string) - Required if type is 'input_text' or 'output_text' - The text content.
    - **image_url** (string) - Required if type is 'input_image' - The URL of the image.
    - **detail** (string) - Optional - Detail level for image input.

### Request Example
```python
thread_id = "thread_EIpHrTAVe0OzoLQg3TXfvrkG"

messages = []
for page in openai.beta.threads.messages.list(thread_id=thread_id, order="asc").iter_pages():
    messages += page.data

items = []
for m in messages:
    item = {"role": m.role}
    item_content = []

    for content in m.content:
        match content.type:
            case "text":
                item_content_type = "input_text" if m.role == "user" else "output_text"
                item_content += [{"type": item_content_type, "text": content.text.value}]
            case "image_url":
                item_content += [
                    {
                        "type": "input_image",
                        "image_url": content.image_url.url,
                        "detail": content.image_url.detail,
                    }
                ]

    item |= {"content": item_content}
    items.append(item)

# create a conversation with your converted items
conversation = openai.conversations.create(items=items)
```
```

--------------------------------

### Responses API - Image Generation with Transparency (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=album-cover

This example demonstrates using the Responses API in Python to generate an image with a transparent background. It configures the `image_generation` tool with the `background` parameter set to `transparent`.

```APIDOC
## POST /v1/responses

### Description
Generates an image with a transparent background using the Responses API. This approach utilizes the `image_generation` tool within the `tools` parameter, setting `background` to `transparent`.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation (e.g., `gpt-5`).
- **input** (string) - Required - The prompt for the image generation.
- **tools** (array) - Required - A list of tools to use. For image generation, include an object with `type: "image_generation"`, `background: "transparent"`, and optionally `quality`.
  - **type** (string) - Must be `"image_generation"`.
  - **background** (string) - Set to `"transparent"`.
  - **quality** (string) - Optional - `"medium"` or `"high"` recommended.

### Request Example
```python
import openai
import base64

response = openai.responses.create(
    model="gpt-5",
    input="Draw a 2D pixel art style sprite sheet of a tabby gray cat",
    tools=[
        {
            "type": "image_generation",
            "background": "transparent",
            "quality": "high",
        },
    ],
)

image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if image_data:
    image_base64 = image_data[0]

    with open("sprite.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
```

### Response
#### Success Response (200)
- **output** (array) - A list of tool outputs. For image generation, this will contain the base64 encoded image data.
  - **type** (string) - The type of tool output, e.g., `"image_generation_call"`.
  - **result** (string) - The base64 encoded image data.

#### Response Example
```json
{
  "id": "resp_abc123",
  "model": "gpt-5",
  "output": [
    {
      "type": "image_generation_call",
      "result": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    }
  ]
}
```
```

--------------------------------

### Example openaiFileIdRefs Array Structure

Source: https://developers.openai.com/api/docs/actions/sending-files

This JSON structure represents an example of the `openaiFileIdRefs` array, which is populated with file details when sending files in a POST request. Each object includes the file's name, ID, MIME type, and a temporary download link.

```json
[
  {
    "name": "dalle-Lh2tg7WuosbyR9hk",
    "id": "file-XFlOqJYTPBPwMZE3IopCBv1Z",
    "mime_type": "image/webp",
    "download_link": "https://files.oaiusercontent.com/file-XFlOqJYTPBPwMZE3IopCBv1Z?se=2024-03-11T20%3A29%3A52Z&sp=r&sv=2021-08-06&sr=b&rscc=max-age%3D31536000%2C%20immutable&rscd=attachment%3B%20filename%3Da580bae6-ea30-478e-a3e2-1f6c06c3e02f.webp&sig=ZPWol5eXACxU1O9azLwRNgKVidCe%2BwgMOc/TdrPGYII%3D"
  },
  {
    "name": "2023 Benefits Booklet.pdf",
    "id": "file-s5nX7o4junn2ig0J84r8Q0Ew",
    "mime_type": "application/pdf",
    "download_link": "https://files.oaiusercontent.com/file-s5nX7o4junn2ig0J84r8Q0Ew?se=2024-03-11T20%3A29%3A52Z&sp=r&sv=2021-08-06&sr=b&rscc=max-age%3D299%2C%20immutable&rscd=attachment%3B%20filename%3D2023%2520Benefits%2520Booklet.pdf&sig=Ivhviy%2BrgoyUjxZ%2BingpwtUwsA4%2BWaRfXy8ru9AfcII%3D"
  }
]
```

--------------------------------

### Input Audio Buffer Speech Started Event

Source: https://developers.openai.com/api/docs/api-reference/realtime-server-events/response/output_item/done

Sent by the server in `server_vad` mode when speech is detected in the audio buffer. It signals the start of speech and provides timing information.

```APIDOC
## Event: input_audio_buffer.speech_started

### Description
Sent by the server when in `server_vad` mode to indicate that speech has been detected in the audio buffer. This can happen any time audio is added to the buffer (unless speech is already detected). The client may want to use this event to interrupt audio playback or provide visual feedback to the user. The client should expect to receive a `input_audio_buffer.speech_stopped` event when speech stops. The `item_id` property is the ID of the user message item that will be created when speech stops and will also be included in the `input_audio_buffer.speech_stopped` event (unless the client manually commits the audio buffer during VAD activation).

### Event Type
`input_audio_buffer.speech_started`

### Properties
- **audio_start_ms** (number) - Milliseconds from the start of all audio written to the buffer during the session when speech was first detected. This will correspond to the beginning of audio sent to the model, and thus includes the `prefix_padding_ms` configured in the Session.
- **event_id** (string) - The unique ID of the server event.
- **item_id** (string) - The ID of the user message item that will be created when speech stops.
- **type** (string) - The event type, must be `input_audio_buffer.speech_started`.

### Example
```json
{
  "audio_start_ms": 500,
  "event_id": "evt_def456",
  "item_id": "item_uvw123",
  "type": "input_audio_buffer.speech_started"
}
```
```

--------------------------------

### Image Generation with Transparent Background (Node.js)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=alien-rock

This example shows how to generate an image with a transparent background using the OpenAI Node.js client library. It uses the `responses.create` method with the `image_generation` tool.

```APIDOC
## POST /v1/responses (Image Generation Tool - Node.js)

### Description
Generates an image with a transparent background using the `image_generation` tool within the `responses.create` endpoint, demonstrated with Node.js.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for image generation (e.g., "gpt-5").
- **input** (string) - Required - The prompt describing the image to generate.
- **tools** (array) - Required - A list of tools to use. For image generation, this should include an object with:
  - **type** (string) - Required - Must be "image_generation".
  - **background** (string) - Optional - Set to "transparent" to enable transparency. Supported with PNG and WEBP output formats.
  - **quality** (string) - Optional - "medium" or "high" recommended for transparency.

### Request Example
```json
{
  "model": "gpt-5",
  "input": "Draw a 2D pixel art style sprite sheet of a tabby gray cat",
  "tools": [
    {
      "type": "image_generation",
      "background": "transparent",
      "quality": "high"
    }
  ]
}
```

### Response
#### Success Response (200)
- **output** (array) - A list of outputs from the tools used. For image generation, contains objects with:
  - **type** (string) - "image_generation_call"
  - **result** (string) - Base64 encoded image data.
```

--------------------------------

### Start Video Generation Job using OpenAI API

Source: https://developers.openai.com/api/docs/guides/video-generation_gallery=open&galleryItem=Cozy-Coffee-Shop-Interior

Initiates a video generation job by sending a POST request to the /videos endpoint. Requires a text prompt and parameters like size and seconds. The response includes a unique ID and initial status.

```javascript
import OpenAI from 'openai';

const openai = new OpenAI();

let video = await openai.videos.create({
    model: 'sora-2',
    prompt: "A video of the words 'Thank you' in sparkling letters",
});

console.log('Video generation started: ', video);
```

```python
from openai import OpenAI

openai = OpenAI()

video = openai.videos.create(
    model="sora-2",
    prompt="A video of a cool cat on a motorcycle in the night",
)

print("Video generation started:", video)
```

```curl
curl -X POST "https://api.openai.com/v1/videos" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F prompt="Wide tracking shot of a teal coupe driving through a desert highway, heat ripples visible, hard sun overhead." \
  -F model="sora-2-pro" \
  -F size="1280x720" \
  -F seconds="8" \

```

--------------------------------

### Configure Realtime Session with Logprobs Inclusion

Source: https://developers.openai.com/api/docs/api-reference/realtime-server-events/input_audio_buffer/speech_started

Sets up a realtime session to include log probabilities for input audio transcriptions. This can be useful for analyzing the confidence of the speech-to-text model.

```json
{
  "type": "realtime",
  "include": [
    "item.input_audio_transcription.logprobs"
  ]
}
```

--------------------------------

### POST /v1/chat/completions - Verbosity

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=artisan-csa

This example shows how to control verbosity using the Chat Completions API.

```APIDOC
## POST /v1/chat/completions - Verbosity

### Description
This endpoint generates a chat completion with a specified verbosity level.

### Method
POST

### Endpoint
/v1/chat/completions

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation.
- **messages** (array) - Required - An array of message objects.
  - **role** (string) - Required - The role of the message (e.g., "user").
  - **content** (string) - Required - The content of the message.
- **verbosity** (string) - Optional - The verbosity level (e.g., "low").

### Request Example
```json
{
  "model": "gpt-5.2",
  "messages": [
    { "role": "user", "content": "What is the answer to the ultimate question of life, the universe, and everything?" }
  ],
  "verbosity": "low"
}
```

### Response
#### Success Response (200)
- **choices** (array) - An array of completion choices.
  - **message** (object) - The message object.
    - **content** (string) - The content of the message.

#### Response Example
```json
{
  "choices": [
    {
      "message": {
        "content": "42"
      }
    }
  ]
}
```
```

--------------------------------

### Initialize Voice Agent with Realtime API (TypeScript)

Source: https://developers.openai.com/api/docs/guides/realtime

Demonstrates initializing a RealtimeAgent and establishing a connection for voice agent interactions using the Agents SDK. It automatically connects microphone and audio output. Requires an API key.

```typescript
import {
  RealtimeAgent,
  RealtimeSession,
} from "openai-agents";

const agent = new RealtimeAgent({
  name: "Assistant",
  instructions: "You are a helpful assistant.",
});

const session = new RealtimeSession(agent);

// Automatically connects your microphone and audio output
await session.connect({
  apiKey: "<client-api-key>",
});
```

--------------------------------

### POST /v1/images/edit (Image Editing with High Input Fidelity - Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=floorplan

This Python example demonstrates editing an image with high input fidelity. It takes local image files and a prompt, setting `input_fidelity` to `high` for enhanced detail preservation.

```APIDOC
## POST /v1/images/edit

### Description
Edits an existing image based on a prompt, with high input fidelity for detail preservation.

### Method
POST

### Endpoint
/v1/images/edit

### Parameters
#### Request Body
- **model** (string) - Required - The image model to use (e.g., "gpt-image-1").
- **image** (list) - Required - A list of image file objects to be edited.
- **prompt** (string) - Required - A text description of the desired image.
- **input_fidelity** (string) - Optional - Sets the input fidelity to 'high'. Defaults to 'low'.

### Request Example
```python
{
    "model": "gpt-image-1",
    "image": [open("woman.jpg", "rb"), open("logo.png", "rb")],
    "prompt": "Add the logo to the woman's top, as if stamped into the fabric.",
    "input_fidelity": "high"
}
```

### Response
#### Success Response (200)
- **data** (list) - A list of image objects.
  - **b64_json** (string) - Base64 encoded JSON representation of the image.

#### Response Example
```python
{
    "data": [
        {"b64_json": "<base64_encoded_image_data>"}
    ]
}
```
```

--------------------------------

### Create and Upload Files to Vector Store

Source: https://developers.openai.com/api/docs/assistants/tools/file-search

This section covers creating a vector store and uploading files to it using the OpenAI SDKs. It demonstrates the process for Python and Node.js.

```APIDOC
## POST /v1/vector_stores

### Description
Creates a new vector store and uploads files to it. This is used to organize files for retrieval by assistants.

### Method
POST

### Endpoint
/v1/vector_stores

### Parameters
#### Request Body
- **name** (string) - Required - The name of the vector store.
- **files** (array of file streams/objects) - Required - The files to upload and add to the vector store.

### Request Example (Conceptual - SDK handles file streams)
```json
{
  "name": "Financial Statements",
  "files": ["edgar/goog-10k.pdf", "edgar/brka-10k.txt"]
}
```

### Response
#### Success Response (200)
- **id** (string) - The unique identifier for the created vector store.
- **name** (string) - The name of the vector store.
- **file_counts** (object) - Contains counts of files in different states (e.g., completed, failed).

#### Response Example
```json
{
  "id": "vs_xyz789",
  "name": "Financial Statements",
  "file_counts": {
    "in_progress": 0,
    "completed": 2,
    "failed": 0,
    "total": 2
  }
}
```
```

--------------------------------

### Edit Image with Mask using Responses API (Node.js)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=alien

This example demonstrates editing an image using a mask with the Responses API in Node.js. It mirrors the Python example, showcasing the JavaScript implementation.

```APIDOC
## POST /v1/responses

### Description
Edits an image using a mask via the Responses API in Node.js. This method integrates image editing as a tool within a conversational or task-based API call.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use (e.g., "gpt-4o").
- **input** (array) - Required - A list of input messages or content.
  - **role** (string) - Required - The role of the message author (`user`).
  - **content** (array) - Required - The content of the message.
    - **type** (string) - Required - The type of content (`input_text` or `input_image`).
    - **text** (string) - Required if type is `input_text` - The text content.
    - **file_id** (string) - Required if type is `input_image` - The ID of the uploaded image file.
- **tools** (array) - Required - A list of tools to use.
  - **type** (string) - Required - The type of tool (`image_generation`).
  - **quality** (string) - Optional - The quality of the generated image (`standard` or `high`).
  - **input_image_mask** (object) - Required if type is `image_generation` - Configuration for the image mask.
    - **file_id** (string) - Required - The ID of the uploaded mask file.

### Request Example
```javascript
import OpenAI from "openai";
import fs from "fs";

const openai = new OpenAI();

// Assume createFile is a function that uploads a file and returns its ID
// const fileId = await createFile("sunlit_lounge.png");
// const maskId = await createFile("mask.png");

// Placeholder for actual file upload and ID retrieval
const fileId = "file-xxxxxxxxxxxxxxxxx";
const maskId = "file-yyyyyyyyyyyyyyyyy";

const response = await openai.responses.create({
  model: "gpt-4o",
  input: [
    {
      role: "user",
      content: [
        {
          type: "input_text",
          text: "generate an image of the same sunlit indoor lounge area with a pool but the pool should contain a flamingo",
        },
        {
          type: "input_image",
          file_id: fileId,
        }
      ],
    },
  ],
  tools: [
    {
      type: "image_generation",
      quality: "high",
      input_image_mask: {
        file_id: maskId,
      }
    },
  ],
});

const imageData = response.output
  .filter((output) => output.type === "image_generation_call")
  .map((output) => output.result);

if (imageData.length > 0) {
  const imageBase64 = imageData[0];
  const fs = await import("fs");
  fs.writeFileSync("lounge.png", Buffer.from(imageBase64, "base64"));
}
```

### Response
#### Success Response (200)
- **id** (string) - The ID of the response.
- **model** (string) - The model used for the response.
- **output** (array) - A list of tool outputs.
  - **type** (string) - The type of output (`image_generation_call`).
  - **result** (string) - The base64 encoded image data.

#### Response Example
```json
{
  "id": "resp_abc123",
  "model": "gpt-4o",
  "output": [
    {
      "type": "image_generation_call",
      "result": "...base64_encoded_image_data..."
    }
  ]
}
```
```

--------------------------------

### Generate Image using OpenAI API (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=animation

Provides Python code examples for generating images using the OpenAI API with DALL-E models. It shows how to specify the model, prompt, and desired image size. The generated image URL is then logged.

```python
import OpenAI from "openai";
const openai = new OpenAI();

const result = await openai.images.generate({
  model: "dall-e-3",
  prompt: "a white siamese cat",
  size: "1024x1024",
});

console.log(result.data[0].url);
```

```python
from openai import OpenAI
client = OpenAI()

result = client.images.generate(
    model="dall-e-2",
    prompt="a white siamese cat",
    size="1024x1024",
    quality="standard",
    n=1,
)

print(result.data[0].url)
```

```python
import OpenAI from "openai";
const openai = new OpenAI();

const result = await openai.images.generate({
  model: "dall-e-3",
  prompt: "a white siamese cat",
  size: "1024x1024",
});

console.log(result.data[0].url);
```

```python
from openai import OpenAI
client = OpenAI()

result = client.images.generate(
    model="dall-e-3",
    prompt="a white siamese cat",
    size="1024x1024"
)

print(result.data[0].url)
```

--------------------------------

### Image API - Stream Image Generation (Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=patterns

This Python example demonstrates streaming image generation using the Image API, allowing for partial image retrieval.

```APIDOC
## POST /v1/images/generations

### Description
Streams image generation results from the Image API in Python, enabling the retrieval of partial images as they are generated. The `partial_images` parameter controls the number of partial images to receive.

### Method
POST

### Endpoint
/v1/images/generations

### Parameters
#### Query Parameters
- **stream** (boolean) - Required - Set to `True` to enable streaming.
- **partial_images** (integer) - Optional - The number of partial images to request (0-3). If set to 0, only the final image is returned. If the final image is generated quickly, fewer partial images than requested may be returned.

#### Request Body
- **prompt** (string) - Required - The text prompt for image generation.
- **model** (string) - Required - The image generation model to use (e.g., "gpt-image-1").

### Request Example
```python
{
    "prompt": "Draw a gorgeous image of a river made of white owl feathers, snaking its way through a serene winter landscape",
    "model": "gpt-image-1",
    "stream": True,
    "partial_images": 2
}
```

### Response
#### Success Response (200)
- **event.type** (string) - The type of event received (e.g., `image_generation.partial_image`).
- **event.partial_image_index** (integer) - The index of the partial image.
- **event.b64_json** (string) - The base64 encoded partial image data.

#### Response Example
```json
{
  "type": "image_generation.partial_image",
  "partial_image_index": 0,
  "b64_json": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0a
... (base64 encoded image data) ...
"
}
```
```

--------------------------------

### POST /v1/responses - Custom Tools

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=online-course-landing-page

This example demonstrates how to define and use custom tools with the Responses API. The 'tools' parameter accepts an array of tool definitions.

```APIDOC
## POST /v1/responses

### Description
Generates a response that can utilize custom tools.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation.
- **input** (string) - Required - The prompt to send to the model.
- **tools** (array) - Optional - A list of tools the model can use.
  - **type** (string) - Required - The type of tool (e.g., "custom").
  - **name** (string) - Required - The name of the custom tool.
  - **description** (string) - Optional - A description of the tool.

### Request Example
```json
{
  "model": "gpt-5.2",
  "input": "Use the code_exec tool to calculate the area of a circle with radius equal to the number of r letters in blueberry",
  "tools": [
    {
      "type": "custom",
      "name": "code_exec",
      "description": "Executes arbitrary python code"
    }
  ]
}
```

### Response
#### Success Response (200)
- **id** (string) - The ID of the response.
- **object** (string) - The type of object returned.
- **created** (integer) - The creation timestamp.
- **model** (string) - The model used for the response.
- **choices** (array) - A list of response choices.
- **usage** (object) - Usage statistics for the request.

#### Response Example
```json
{
  "id": "resp_def456",
  "object": "text_completion",
  "created": 1677652347,
  "model": "gpt-5.2",
  "choices": [
    {
      "text": "...",
      "index": 0,
      "logprobs": null,
      "finish_reason": "tool_calls"
    }
  ],
  "usage": {
    "prompt_tokens": 30,
    "completion_tokens": 15,
    "total_tokens": 45
  }
}
```
```

--------------------------------

### Image Generation with Transparent Background (Node.js)

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=barista-ad

This example shows how to generate an image with a transparent background using the OpenAI Node.js client. It configures the `background` parameter to `transparent` and suggests using `png` or `webp` for output.

```APIDOC
## POST /v1/images

### Description
Generates an image with a transparent background.

### Method
POST

### Endpoint
/v1/images

### Parameters
#### Query Parameters
- **model** (string) - Required - The model to use for image generation (e.g., `gpt-image-1`).
- **prompt** (string) - Required - A text description of the desired image.
- **size** (string) - Optional - The desired size of the generated image (e.g., `1024x1024`).
- **background** (string) - Optional - Set to `transparent` to enable transparency. Only supported with `png` and `webp` output formats.
- **quality** (string) - Optional - Set to `medium` or `high` for best transparency results.

### Request Example
```javascript
import fs from "fs";
import OpenAI from "openai";

const client = new OpenAI();

const response = await client.responses.create({
  model: "gpt-5",
  input: "Draw a 2D pixel art style sprite sheet of a tabby gray cat",
  tools: [
    {
      type: "image_generation",
      background: "transparent",
      quality: "high",
    },
  ],
});

const imageData = response.output
  .filter((output) => output.type === "image_generation_call")
  .map((output) => output.result);

if (imageData.length > 0) {
  const imageBase64 = imageData[0];
  const imageBuffer = Buffer.from(imageBase64, "base64");
  fs.writeFileSync("sprite.png", imageBuffer);
}
```

### Response
#### Success Response (200)
- **output** (array) - An array of tool outputs.
  - **type** (string) - The type of tool output, e.g., `image_generation_call`.
  - **result** (string) - The generated image data in base64 encoded format.

#### Response Example
```json
{
  "id": "resp_abc123",
  "model": "gpt-5",
  "output": [
    {
      "type": "image_generation_call",
      "result": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    }
  ]
}
```
```

--------------------------------

### Install OpenAI Library for Python

Source: https://developers.openai.com/api/docs/api-reference/chat/completions/responses

Installs the OpenAI library for Python using pip. This enables Python developers to easily access and utilize OpenAI's powerful APIs.

```bash
pip install openai
```

--------------------------------

### POST /v1/images/edit (Image Editing with High Input Fidelity - Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=clay-figurine

This Python example demonstrates image editing with high input fidelity using the `images.edit` method. It allows for detailed modifications to an existing image by providing a prompt and input images.

```APIDOC
## POST /v1/images/edit

### Description
Edits an image with high input fidelity using Python, preserving details from the input image and prompt.

### Method
POST

### Endpoint
/v1/images/edit

### Parameters
#### Request Body
- **model** (string) - Required - The image model to use (e.g., "gpt-image-1").
- **image** (list) - Required - A list of image file objects. The first image is the base image, subsequent images can be used for masking or additional context.
- **prompt** (string) - Required - A text description of the desired image.
- **input_fidelity** (string) - Optional - The input fidelity level. Set to "high" to preserve details. Defaults to "low".

### Request Example
```json
{
  "model": "gpt-image-1",
  "image": [
    "open(\"woman.jpg\", \"rb\")",
    "open(\"logo.png\", \"rb\")"
  ],
  "prompt": "Add the logo to the woman's top, as if stamped into the fabric.",
  "input_fidelity": "high"
}
```

### Response
#### Success Response (200)
- **data** (list) - A list of image dictionaries.
  - **b64_json** (string) - The base64 encoded image data.

#### Response Example
```json
{
  "data": [
    { "b64_json": "<base64_encoded_image_data>" }
  ]
}
```
```

--------------------------------

### Realtime Session Configuration

Source: https://developers.openai.com/api/docs/api-reference/realtime-client-events/conversation/item/create

Configure a realtime session for interactive audio and text interactions with the model.

```APIDOC
## POST /v1/realtime/sessions

### Description
Creates a new realtime session for interactive voice and text communication.

### Method
POST

### Endpoint
/v1/realtime/sessions

### Parameters
#### Request Body
- **type** (string) - Required - The type of session to create. Must be `"realtime"`.
- **audio** (RealtimeAudioConfig) - Optional - Configuration for input and output audio.
  - **input** (object) - Optional - Audio input configuration.
  - **output** (object) - Optional - Audio output configuration.
- **include** (array of string) - Optional - Additional fields to include in server outputs. Example: `["item.input_audio_transcription.logprobs"]`.
- **instructions** (string) - Optional - Default system instructions to guide the model's responses and behavior.
- **max_output_tokens** (number or "inf") - Optional - Maximum number of output tokens for a single assistant response. Accepts an integer between 1 and 4096, or `"inf"`. Defaults to `"inf"`.
- **model** (string) - Optional - The Realtime model to use for the session. Examples: `"gpt-realtime"`, `"gpt-4o-realtime-preview"`.
- **output_modalities** (array of string) - Optional - The set of modalities the model can respond with. Defaults to `["audio"]`. Can be `["text"]` for text-only responses.
- **prompt** (ResponsePrompt) - Optional - Reference to a prompt template and its variables.
- **tool_choice** (RealtimeToolChoiceConfig) - Optional - Configuration for how the model chooses tools.
- **tools** (RealtimeToolsConfig) - Optional - Tools available to the model.
- **tracing** (RealtimeTracingConfig) - Optional - Configuration for writing session traces to the Traces Dashboard. Set to `null` to disable.
- **truncation** (RealtimeTruncation) - Optional - Configuration for how the conversation is truncated when the token limit is exceeded.

### Request Example
```json
{
  "type": "realtime",
  "audio": {
    "input": {},
    "output": {}
  },
  "instructions": "Be concise and friendly.",
  "model": "gpt-4o-realtime-preview"
}
```

### Response
#### Success Response (200)
- **session_id** (string) - The unique identifier for the created session.
- **type** (string) - The type of the created session.

#### Response Example
```json
{
  "session_id": "sess_abc123xyz",
  "type": "realtime"
}
```
```

--------------------------------

### POST /images/edit (Image Generation with High Input Fidelity - Python)

Source: https://developers.openai.com/api/docs/guides/image-generation_gallery=open&galleryItem=thunderstorm

This example demonstrates editing an image with high input fidelity using the `images.edit` endpoint in Python. It takes local image files and applies a prompt with high fidelity.

```APIDOC
## POST /images/edit

### Description
Edits an image with high input fidelity, preserving details from the input images. This is useful for elements like faces or logos.

### Method
POST

### Endpoint
/images/edit

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for image editing (e.g., `gpt-image-1`).
- **image** (list) - Required - A list of image file objects.
- **prompt** (string) - Required - A text description of the desired image.
- **input_fidelity** (string) - Optional - The input fidelity level (`high` or `low`). Defaults to `low`.

### Request Example
```json
{
  "model": "gpt-image-1",
  "image": [
    "open('woman.jpg', 'rb')",
    "open('logo.png', 'rb')"
  ],
  "prompt": "Add the logo to the woman's top, as if stamped into the fabric.",
  "input_fidelity": "high"
}
```

### Response
#### Success Response (200)
- **data** (list) - A list of image objects.
  - **b64_json** (string) - The base64 encoded image data.

#### Response Example
```json
{
  "data": [
    { "b64_json": "<base64_encoded_image_data>" }
  ]
}
```
```

--------------------------------

### Image Generation with Transparency (Node.js)

Source: https://developers.openai.com/api/docs/guides/image-generation_image-generation-model=gpt-image

Example of generating an image with a transparent background using the OpenAI Node.js client library.

```APIDOC
## POST /v1/images

### Description
Generates an image with a transparent background.

### Method
POST

### Endpoint
/v1/images

### Parameters
#### Query Parameters
- **model** (string) - Required - The model to use for image generation (e.g., `gpt-image-1`).
- **prompt** (string) - Required - A text description of the desired image.
- **size** (string) - Optional - The desired size of the generated image (e.g., `1024x1024`).
- **quality** (string) - Optional - The quality of the generated image. Supports `medium` or `high` for transparency.
- **background** (string) - Optional - Set to `transparent` to enable transparent backgrounds. Only supported with `png` and `webp` output formats.

### Request Example
```javascript
import OpenAI from "openai";
import fs from "fs";

const client = new OpenAI();

const response = await client.images.generate({
  model: "gpt-image-1",
  prompt: "Draw a 2D pixel art style sprite sheet of a tabby gray cat",
  size: "1024x1024",
  background: "transparent",
  quality: "high",
});

// Save the image to a file
const image_base64 = response.data[0].b64_json;
const image_bytes = Buffer.from(image_base64, "base64");
fs.writeFileSync("sprite.png", image_bytes);
```

### Response
#### Success Response (200)
- **data** (array) - Contains the generated image data.
  - **b64_json** (string) - The base64 encoded image data.
```

--------------------------------

### Voice Agent Metaprompt Reference

Source: https://developers.openai.com/api/docs/guides/voice-agents

Provides links to resources for creating voice agents. This includes a direct link to a ChatGPT GPT for voice agent metaprompting and a link to the raw metaprompt text file on GitHub.

```markdown
Instead of writing this out by hand, you can also check out this
[Voice Agent Metaprompter](https://chatgpt.com/g/g-678865c9fb5c81918fa28699735dd08e-voice-agent-metaprompt-gpt)
or [copy the metaprompt](https://github.com/openai/openai-realtime-agents/blob/main/src/app/agentConfigs/voiceAgentMetaprompt.txt) and use it directly.
```

--------------------------------

### Preambles

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=virtual-drum-kit-5.2

GPT-5.2 generates brief, user-visible explanations before invoking a tool, outlining its intent or plan. This enhances transparency and debuggability.

```APIDOC
## Preambles

### Description
Preambles are short, user-facing explanations generated by GPT-5.2 before a tool or function is invoked. They clarify the model's intent or plan, appearing after the chain-of-thought and before the tool call, thereby improving transparency, debuggability, and user confidence.

### Method
N/A (Enabled via system or developer instructions)

### Endpoint
N/A

### Parameters
#### System/Developer Instruction
- **Instruction Text** (string) - Required - A prompt instructing the model to explain its reasoning before calling a tool. Example: `"Before you call a tool, explain why you are calling it."`

### Request Example
(This is an instruction, not a direct API request body)
```
"Before you call a tool, explain why you are calling it."
```

### Response
#### Success Response (200)
N/A (This feature affects model output, not direct API responses)

#### Response Example
(Example of model output including a preamble)
```
"I need to find the weather for London, so I will call the get_weather tool."
{
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"location\": \"London\"}"
      }
    }
  ]
}
```
```

--------------------------------

### Create Video

Source: https://developers.openai.com/api/docs/guides/video-generation_gallery=open&galleryItem=indie-cafe-rainy-window

Initiates a new video render job. This is an asynchronous process. You can provide a text prompt, an image for reference, or a remix ID to guide the video generation.

```APIDOC
## POST /videos

### Description
Starts a new video render job from a prompt, with optional reference inputs or a remix ID.

### Method
POST

### Endpoint
/videos

### Parameters
#### Query Parameters
- **model** (string) - Required - The model to use for generation (e.g., `sora-2`, `sora-2-pro`).

#### Request Body
- **prompt** (string) - Required - The text prompt describing the desired video content.
- **input_image** (string) - Optional - A base64 encoded image to use as a reference for the video.
- **remix_id** (string) - Optional - The ID of an existing video to remix.
- **duration_seconds** (integer) - Optional - The desired duration of the video in seconds.
- **size** (string) - Optional - The desired resolution of the video (e.g., "1792x1024").

### Request Example
```json
{
  "prompt": "A peaceful, cinematic scene of two sea otters floating side by side on calm, sunlit water.",
  "model": "sora-2",
  "duration_seconds": 8,
  "size": "1792x1024"
}
```

### Response
#### Success Response (200)
- **job_id** (string) - The unique identifier for the video job.
- **status** (string) - The initial status of the job (e.g., "processing").

#### Response Example
```json
{
  "job_id": "job_abc123xyz",
  "status": "processing"
}
```
```

--------------------------------

### Preambles

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=tiny-kanban

GPT-5.2 generates brief, user-visible explanations before invoking a tool, outlining its intent or plan. This enhances transparency and debuggability.

```APIDOC
## Preambles

### Description
Preambles are short, human-readable explanations generated by GPT-5.2 before it executes a tool or function call. They articulate the model's intent or plan, appearing after the chain-of-thought and before the actual tool invocation. This feature improves transparency, debuggability, and user confidence.

### Method
N/A (Enabled via system or developer instructions)

### Endpoint
N/A (Enabled via system or developer instructions)

### Parameters
#### Enabling Preambles
- **Instruction** (string) - Required - Provide an instruction in the system or developer message, such as: "Before you call a tool, explain why you are calling it."

### Request Example
```json
{
  "role": "system",
  "content": "Before you call a tool, explain why you are calling it."
}
```

### Response
#### Success Response (Example of Model Output)
When a tool is invoked, the model might output a preamble like this:
```
I need to call the 'get_weather' tool to find out the current temperature in London.
```

#### Response Example
```json
{
  "role": "assistant",
  "content": "I need to call the 'get_weather' tool to find out the current temperature in London.",
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"location\": \"London\"}"
      }
    }
  ]
}
```
```

--------------------------------

### Image Generation API

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=clay-figurine

This section details how to generate an initial image using the OpenAI API. It includes examples in Python and JavaScript.

```APIDOC
## POST /v1/responses

### Description
Generates an image based on a text prompt and specified tools.

### Method
POST

### Endpoint
/v1/responses

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation (e.g., "gpt-5").
- **input** (string) - Required - The text prompt describing the desired image.
- **tools** (array) - Required - A list of tools to use, including `"image_generation"`.

### Request Example (Python)
```python
import openai
import base64

response = openai.responses.create(
    model="gpt-5",
    input="Generate an image of gray tabby cat hugging an otter with an orange scarf",
    tools=[{"type": "image_generation"}],
)

image_generation_calls = [
    output
    for output in response.output
    if output.type == "image_generation_call"
]

image_data = [output.result for output in image_generation_calls]

if image_data:
    image_base64 = image_data[0]
    with open("cat_and_otter.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
```

### Request Example (JavaScript)
```javascript
import OpenAI from "openai";
const openai = new OpenAI();

const response = await openai.responses.create({
  model: "gpt-5",
  input:
    "Generate an image of gray tabby cat hugging an otter with an orange scarf",
  tools: [{ type: "image_generation" }],
});

const imageGenerationCalls = response.output.filter(
  (output) => output.type === "image_generation_call"
);

const imageData = imageGenerationCalls.map((output) => output.result);

if (imageData.length > 0) {
  const imageBase64 = imageData[0];
  const fs = await import("fs");
  fs.writeFileSync("cat_and_otter.png", Buffer.from(imageBase64, "base64"));
}
```

### Response
#### Success Response (200)
- **output** (array) - A list of outputs, potentially including `image_generation_call` objects.
  - **type** (string) - The type of output, e.g., `"image_generation_call"`.
  - **id** (string) - The unique identifier for the image generation call.
  - **result** (string) - The base64 encoded image data.

#### Response Example
```json
{
  "output": [
    {
      "type": "image_generation_call",
      "id": "img_abc123",
      "result": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    }
  ]
}
```
```

--------------------------------

### POST /v1/chat/completions - Custom Tools

Source: https://developers.openai.com/api/docs/guides/latest-model_gallery=open&galleryItem=camping-gear-checklist-5.2

This example shows how to define custom tools for the Chat Completions API. The `tools` parameter contains a `custom` object with tool details.

```APIDOC
## POST /v1/chat/completions - Custom Tools

### Description
This endpoint generates a chat completion that may involve calling custom tools.

### Method
POST

### Endpoint
/v1/chat/completions

### Parameters
#### Request Body
- **model** (string) - Required - The model to use for generation.
- **messages** (array) - Required - A list of message objects representing the conversation.
  - **role** (string) - Required - The role of the message (e.g., "user").
  - **content** (string) - Required - The content of the message.
- **tools** (array) - Optional - A list of tools the model can use.
  - **type** (string) - Required - The type of tool (e.g., "custom").
  - **custom** (object) - Required - Details for a custom tool.
    - **name** (string) - Required - The name of the custom tool.
    - **description** (string) - Optional - A description of the custom tool.

### Request Example
```json
{
  "model": "gpt-5.2",
  "messages": [
    { "role": "user", "content": "Use the code_exec tool to calculate the area of a circle with radius equal to the number of r letters in blueberry" }
  ],
  "tools": [
    {
      "type": "custom",
      "custom": {
        "name": "code_exec",
        "description": "Executes arbitrary python code"
      }
    }
  ]
}
```

### Response
#### Success Response (200)
- **choices** (array) - A list of completion choices.
  - **message** (object) - The message content.
    - **role** (string) - The role of the message.
    - **content** (string) - The content of the message.

#### Response Example
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "..."
      }
    }
  ]
}
```
```

--------------------------------

### Edit an image using a mask (inpainting) - Node.js

Source: https://developers.openai.com/api/docs/guides/image-generation_api=responses&gallery=open&galleryItem=abstract-orbit

This example demonstrates how to edit an image using a mask with the OpenAI Node.js client. It mirrors the Python example, using asynchronous operations for file handling and API calls.

```APIDOC
## POST /v1/images/edits

### Description
Edits an image based on a provided mask and prompt. The mask indicates which part of the image should be edited.

### Method
POST

### Endpoint
/v1/images/edits

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for image editing (e.g., "gpt-image-1").
- **image** (File) - Required - The image to edit. Must be a PNG image, less than 4MB.
- **mask** (File) - Required - The mask image. Must be a PNG image, less than 4MB. The transparent areas of the mask indicate where the image should be edited.
- **prompt** (string) - Required - A text description of the desired image.
- **n** (integer) - Optional - The number of images to generate. Must be between 1 and 10.
- **size** (string) - Optional - The size of the generated images. Must be one of "256x256", "512x512", or "1024x1024".
- **response_format** (string) - Optional - The format in which the generated images are returned. Must be one of `url` or `b64_json`.

### Request Example
```javascript
import fs from "fs";
import OpenAI, { toFile } from "openai";

const client = new OpenAI();

const rsp = await client.images.edit({
    model: "gpt-image-1",
    image: await toFile(fs.createReadStream("sunlit_lounge.png"), null, {
        type: "image/png",
    }),
    mask: await toFile(fs.createReadStream("mask.png"), null, {
        type: "image/png",
    }),
    prompt: "A sunlit indoor lounge area with a pool containing a flamingo",
});

// Save the image to a file
const image_base64 = rsp.data[0].b64_json;
const image_bytes = Buffer.from(image_base64, "base64");
fs.writeFileSync("lounge.png", image_bytes);
```

### Response
#### Success Response (200)
- **created** (number) - The Unix timestamp of when the image was created.
- **data** (array) - An array of image objects.
  - **url** (string) - The URL of the generated image (if `response_format` is `url`).
  - **b64_json** (string) - The base64 encoded JSON of the generated image (if `response_format` is `b64_json`).

#### Response Example
```json
{
  "created": 1678887777,
  "data": [
    {
      "url": "https://example.com/image.png",
      "b64_json": "..."
    }
  ]
}
```
```