# Voice to Text Server Developer Documentation

## Overview

The Voice to Text Server is a Flask-based application designed for converting voice (audio) inputs to text using the `transformers` library's Wav2Vec2 model. This server is suitable for applications requiring automatic speech recognition (ASR) capabilities.

## Prerequisites

Before deploying or developing with this server, ensure you have the following prerequisites installed:

- Python 3.8 or newer
- Flask
- gunicorn
- gevent
- torch
- torchaudio
- transformers

## Configuration

The application requires a `config.json` file located in the `config/` directory. This file should contain the following keys:

- `apikey`: A secret key for API access control.
- `modelName`: The name of the Wav2Vec2 model to be used for speech recognition.

### Changing the API Key

It's crucial to change the `apikey` in the `config.json` file to a secure value before deploying the application in a production environment. This key is used to authenticate API requests.

## Deployment

The application is designed to be containerized and deployed as a Docker image for production environments. The provided `Dockerfile` outlines the steps for creating the Docker image.

### Docker Deployment Steps

1. Build the Docker image:

```sh
docker build -t pp-ai-eava-voice-to-text .
```

2. Run the container:

```sh
docker run -d -p 5000:5000 pp-ai-eava-voice-to-text
```

The application listens on port 5000 by default, but you can adjust this as needed.

## API Endpoints

### `/transcribe` (POST)

Converts PCM audio data to text.

- Requires an `Authorization` header with the API key.
- JSON payload with the `pcm_data` key, containing the audio data.


## Security

Ensure that the API key is kept secure and not exposed in public repositories or client-side code. Use environment variables or secure secrets management tools to manage the API key in production environments.

## Development Notes

- The server uses a background thread for processing tasks, which are managed through a queue. This design helps in decoupling the receipt of requests from the processing of audio data.
- Audio data is normalized and potentially resampled to match the requirements of the Wav2Vec2 model.

## Handling PCM Data and Conversion from Mu-law

The PP AI EAVA Voice to Text Server requires audio input in PCM (Pulse-Code Modulation) format for processing. However, certain sources, such as Twilio's WebSocket audio stream, provide audio data in mu-law (µ-law) encoding. Mu-law encoding is a form of non-linear PCM encoding commonly used in telephony systems to compress the dynamic range of audio signals.

Before sending audio data to the PP AI EAVA Voice to Text Server, it's necessary to convert mu-law encoded data to linear PCM format. This conversion process is essential for ensuring the audio data is in the correct format for the automatic speech recognition (ASR) pipeline to process accurately.

### Mu-law to PCM Conversion in Rust

When integrating with sources that provide mu-law encoded audio, such as Twilio, you may need to perform the conversion to PCM format. Below is a conceptual approach to converting mu-law to PCM in Rust, a system programming language known for its performance and safety features.

#### Conceptual Steps for Conversion:

1. **Receive Mu-law Encoded Data**: The first step involves receiving the mu-law encoded audio stream from the source (e.g., Twilio's WebSocket).

2. **Perform Mu-law to PCM Conversion**: Implement or utilize an existing Rust library function to convert the mu-law encoded data into linear PCM format. The conversion process involves expanding the compressed mu-law values back into their original linear PCM amplitude values.

3. **Prepare Audio Data for the API**: Once converted to PCM, the audio data should be formatted according to the API's expected input structure. In the case of the PP AI EAVA Voice to Text Server, the `pcm_data` field in the API request payload should contain the linear PCM data as an array of integers.

4. **Send the API Request**: With the audio data in the correct format, construct and send the request to the `/transcribe` endpoint of the Voice to Text Server.

#### Rust Implementation Note:

While a specific code example is not provided here, Rust developers can leverage the `audiopus` crate (or similar libraries) that support audio encoding and decoding, including mu-law to PCM conversion. The process involves reading the mu-law encoded audio, converting each sample to linear PCM format using the appropriate algorithm, and then formatting the data for API consumption.

### Example API Request with PCM Data

Following the conversion, the API request payload with PCM data should look similar to the example provided:

```json
{
  "pcm_data": [2496, 1952, 848, 78, -488, -1184, -1824, -2112, -2240, -2240, -1632, -1440, -1248, -720, -98, 196, 424, 360, -53, -180, -424, -944, -1504, -1568, -1696, -1760]
}
```

This JSON structure sends the linear PCM audio data to the server for transcription, ensuring compatibility with the ASR model's input requirements.

By accurately converting mu-law encoded data to PCM and formatting it correctly for the Voice to Text API, developers can integrate a wide range of audio sources with the PP AI EAVA Voice to Text Server, extending its applicability and utility in real-world applications.
