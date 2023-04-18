# version 1, from ChatGPT
import os
from slack_bolt import App
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Initialize the Slack app with your app token and signing secret
app = App(token=os.environ["SLACK_BOT_TOKEN"], signing_secret=os.environ["SLACK_SIGNING_SECRET"])

# Load the Google Drive credentials from the client_secret.json file
creds = Credentials.from_authorized_user_file("client_secret.json", ["https://www.googleapis.com/auth/drive"])

# Define the ID of the template folder that you want to copy
template_folder_id = "INSERT_TEMPLATE_FOLDER_ID_HERE"

# Define the MIME type of the folder
folder_mime_type = "application/vnd.google-apps.folder"

# Define the error message that will be sent to the user in case of failure
error_message = "Oops! Something went wrong while creating the new customer folder. Please try again later."

# Define the function that will handle the slash command
@app.command("/new-customer")
def handle_new_customer_command(ack, respond, command):
    # Get the name of the new customer from the slash command
    new_customer_name = command["text"]
    
    try:
        # Create a copy of the template folder and rename it
        service = build("drive", "v3", credentials=creds)
        copied_folder = service.files().copy(fileId=template_folder_id, body={"name": new_customer_name, "parents": [template_folder_id], "mimeType": folder_mime_type}).execute()
        
        # Set the owner of the new folder to the same person who sent the command
        owner_email = command["user_id"] + "@slack.com"
        service.permissions().create(fileId=copied_folder["id"], body={"type": "user", "role": "owner", "emailAddress": owner_email}).execute()
        
        # Send a success message to the user
        ack(f"New customer folder '{new_customer_name}' created successfully!")
    except HttpError:
        # Send an error message to the user
        respond({"response_type": "ephemeral", "text": error_message})

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
