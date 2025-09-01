"""
Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import vertexai
from vertexai.preview import reasoning_engines
from vertexai import agent_engines
from dotenv import load_dotenv
import os
from weather_agent.agent import root_agent

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")

# Initialize Vertex AI with staging bucket
STAGING_BUCKET = os.getenv("GOOGLE_CLOUD_STAGING_BUCKET")
GOOGLE_CLOUD_PROJECT_ID=os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_REGION=os.getenv("GOOGLE_CLOUD_LOCATION")

# Load API keys for different models
WEATHERBIT_API_KEY = os.getenv("WEATHERBIT_API_KEY")


vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

adk_app = reasoning_engines.AdkApp(
    agent=root_agent,
)

remote_app = agent_engines.create(
    agent_engine=adk_app,
    display_name="weather-agent",
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
        "a2a-sdk==0.2.16",
    ],
    extra_packages=[
        "./weather_agent",
    ],
    env_vars={
        "GOOGLE_GENAI_USE_VERTEXAI": os.environ["GOOGLE_GENAI_USE_VERTEXAI"],
        "WEATHERBIT_API_KEY": WEATHERBIT_API_KEY,
        "GOOGLE_CLOUD_PROJECT_ID": GOOGLE_CLOUD_PROJECT_ID,
        "GOOGLE_CLOUD_REGION":GOOGLE_CLOUD_REGION
    },
)

print(f"Deployed remote app resource: {remote_app.resource_name}")