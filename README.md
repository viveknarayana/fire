# Firewatch - Real-time Fire Detection and Emergency Response System

## Overview

Firewatch is an autonomous, real-time fire detection and emergency response system built using cutting-edge AI technologies. The system continuously processes video data to detect fire and communicates with emergency services in real-time to assist during critical fire situations.

When fire is detected, Firewatch evaluates the severity and decides whether to notify the local fire department. It can then hold an autonomous conversation with emergency operators via AI-powered chat, ensuring swift and effective communication during an emergency. 

## Features

- **Fire Detection**: Continuously scans video frames for fire using a custom object detection model trained on Roboflow.
- **Real-time Emergency Response**: AI-powered decision-making to evaluate fire severity and determine whether to notify emergency services.
- **Twilio Integration**: Enables autonomous conversation with emergency responders via phone call.
- **Email Alerts**: Sends fire details and image alerts to users through Mailjet, stored in Supabase.
- **Email Response Handling**: Listens for email responses via IMAP polling to provide updates on fire status.
- **Backend**: Built with FastAPI for high-performance asynchronous handling of video frames and real-time communication.

## Demo

- [Watch the Demo Video Here](<link-to-demo-video>)

## Technologies Used

- **Python**: Core backend language using FastAPI.
- **Twilio**: For handling real-time phone communication with emergency operators.
- **Cerebras**: AI-powered system for generating responses based on fire severity.
- **IMAP**: Used for continuous email checking and automating follow-ups.
- **Roboflow**: For training a custom fire detection model on video frames.
- **Mailjet**: To send email alerts to users with fire details and images.
- **Supabase**: For storing fire images and related data.
- **React**: Frontend framework for building a responsive user interface.
- **Tailwind CSS & Shadcn**: For styling and building UI components.

## How It Works

1. **Fire Detection**: The system processes video data in real-time, analyzing each frame using the custom fire detection model. If fire is detected, it triggers the response system.
   
2. **AI Decision-making**: Once fire is detected, the frame is passed to Gemini, which evaluates the severity. If needed, Gemini triggers the `call_operator_help` function to notify emergency responders.

3. **Emergency Communication**: The context surrounding the fire is passed to the Cerebras API, which generates real-time responses to communicate with the operator. Twilio is used to place the phone call and interact with the operator.

4. **Email Alerts**: When fire is detected, users receive an email with fire details and an image of the scene. If the user replies to the email requesting an update, the system re-analyzes the scene and updates the user.

5. **Backend Services**: The backend, built with FastAPI, handles all incoming requests, processes video frames, communicates with external APIs like Twilio, Mailjet, and Cerebras, and performs AI-driven decision-making asynchronously for real-time responsiveness.
