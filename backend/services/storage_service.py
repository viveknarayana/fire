import supabase
from config import SUPABASE_URL, SUPABASE_KEY

# Initialize Supabase client
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

async def upload_fire_image(user_uuid, frame_number, file_content):
    """Upload a fire image to Supabase storage."""
    try:
        supabase_filename = f"{user_uuid}/{user_uuid}_fire_frame_{frame_number}.jpg"
        
        upload_result = supabase_client.storage.from_("fireimages").upload(
            supabase_filename,
            file_content,
            file_options={"content-type": "image/jpeg"}
        )
        
        # Get public URL for the uploaded file
        public_url = supabase_client.storage.from_("fireimages").get_public_url(supabase_filename)
        
        return {"success": True, "url": public_url}
    except Exception as e:
        print(f"Error uploading to Supabase: {e}")
        return {"success": False, "error": str(e)}

async def get_latest_fire_image(user_uuid):
    """Get the most recent fire image for a specific user from Supabase storage."""
    try:
        # List all objects in the user's directory
        list_result = supabase_client.storage.from_("fireimages").list(user_uuid)
        
        sorted_files = sorted(list_result, key=lambda x: x['name'], reverse=True)
        
        if not sorted_files:
            return None
        
        # Get the latest file
        latest_file = sorted_files[0]
        file_path = f"{user_uuid}/{latest_file['name']}"
        
        # Download the file content
        response = supabase_client.storage.from_("fireimages").download(file_path)
        
        # Get the public URL for reference
        public_url = supabase_client.storage.from_("fireimages").get_public_url(file_path)
        
        return {
            "content": response,
            "name": latest_file['name'],
            "url": public_url
        }
    except Exception as e:
        print(f"Error retrieving latest fire image: {e}")
        return None