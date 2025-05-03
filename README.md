## Inspiration

I knew I wanted to build something with AI this weekend, especially around the idea of agentic AI. I thought it would be exciting (and meaningful) to combine that with a life-saving use case. After reflecting on recent wildfires, especially the Palisades Fire, I was inspired to create a system that could not only detect fires but also make decisions and take action autonomously — potentially helping first responders and saving lives.

## What it does

Firewatch is a real-time fire detection and emergency response system. It continuously processes video data using a **custom object detection model trained on Roboflow** to detect fire with high confidence. When fire is detected, the frame is passed to **Gemini**, which evaluates the severity and decides whether to notify the local fire department.

If action is required, Gemini generates context around the fire by analyzing the image, and that response is passed to **Cerebras** and used with **Twilio** to hold a real-time, autonomous conversation with emergency operators via phone call.

The system also:
- Sends an **email alert** to the user (via **Mailjet**) with fire details and a viewable image from the file stored in **Supabase**.
- Listens for **email replies** via **IMAP**; if the user requests an update, it re-analyzes the scene and may re-trigger an emergency call if the fire has intensified.

## How we built it

I began by using a custom fire detection model from **Roboflow**. This model continuously scans incoming video frames for signs of fire.

Once fire is detected:
- The frame is passed to **Gemini**, which analyzes its severity using a carefully engineered prompt.
- I exposed a `call_operator_help` function as a **tool** to Gemini, allowing it to autonomously decide when and how to escalate situations.
- If Gemini determines that emergency services should be contacted, it invokes this tool with the necessary context.
- The context is passed to the **Cerebras API**, which enables real-time, intelligent conversation with a 911 operator. Cerebras allowed for extremely quick AI responses that made the interaction with the 911 operator flow like a real conversation. 
- **Twilio** is used to make the actual phone call, connecting the AI-driven response system directly with human responders.

For user alerts:
- I implemented **OAuth login** to collect user emails.
- When fire is detected, we use **Mailjet** to send a detailed notification email, including the image of the fire that was uploaded to **Supabase**.
- The system listens for **email responses** using **IMAP** and polling. If a response comes in, it fetches the latest image, runs another analysis, and follows up as needed.

The backend was developed in **Python** using **FastAPI**. To ensure the system responds in real-time, I leveraged asynchronous services, enabling efficient handling of tasks such as video processing, fire detection, and communication with external APIs like **Cerebras** and **Twilio**.

For the front end:
- I used **React** to build a responsive user interface where users can interact with the system.
- **Shadcn** was utilized for designing intuitive and user-friendly UI components.
- **Tailwind CSS** was used to style the interface, ensuring a clean, modern look 

## Challenges we ran into

One of the biggest challenges was detecting email replies. Initially, I explored several services, but after much trial and error, I decided to use **IMAP** with continuous polling to check for updates in the inbox. 

Another major hurdle was establishing a real-time AI-to-operator connection. Initially, I struggled with how to let Twilio respond with AI-generated responses from Cerebras. To solve this, I used ngrok to expose my local endpoints as webhooks, allowing Twilio to access them and enter a conversation loop with whoever was on the phone.

## Accomplishments that we're proud of

I’m most proud of creating an autonomous system that can converse with the fire department in real-time during an emergency, potentially saving lives.

## What we learned

Through this project, I gained experience working with a variety of technologies, including Twilio for real-time voice communication with emergency responders, and IMAP for checking email responses and automating follow-ups. Additionally, I explored Mailjet for programmatically sending notifications and Cerebras API to enable AI-powered conversations with 911 operators. Building the backend with FastAPI and handling asynchronous services gave me insight into creating responsive, real-time systems. Overall, this project taught me how to combine multiple technologies to create an efficient and effective emergency response system.

## What's next for Firewatch

I’d like to switch from email notifications to SMS notifications for quicker, more convenient updates. While email responses are functional, they can be cumbersome for users. I only used emails because Twilio required a 2-day verification for SMS, so I plan to implement that in the near future. This will make the system more user-friendly and efficient in emergency situations. I would also like to enable location services in the case where an operator asks where the fire is located. I think this would be a simple implementation, so I plan to develop this functionality soon.


