ascii_tv = """
      \\     /
       \\   /
        \\ /
       /~~~~~\\
,-------------------,
| ,---------------, |
| |               | |
| |               | |
| |               | |
| |               | |
| |_______________| |
|___________________|
|___________________| 

_________ _______ _________            _______ _________ _        ______   _______  _______ 
\__   __/(  ____ )\__   __/|\     /|  (  ____ \\__   __/( (    /|(  __  \ (  ____ \(  ____ )
   ) (   | (    )|   ) (   | )   ( |  | (    \/   ) (   |  \  ( || (  \  )| (    \/| (    )|
   | |   | (____)|   | |   | |   | |  | (__       | |   |   \ | || |   ) || (__    | (____)|
   | |   |  _____)   | |   ( (   ) )  |  __)      | |   | (\ \) || |   | ||  __)   |     __)
   | |   | (         | |    \ \_/ /   | (         | |   | | \   || |   ) || (      | (\ (   
___) (___| )         | |     \   /    | )      ___) (___| )  \  || (__/  )| (____/\| ) \ \__
\_______/|/          )_(      \_/     |/       \_______/|/    )_)(______/ (_______/|/   \__/


"""

print(ascii_tv)

import requests
import subprocess
import time

CHANNELS_JSON_URL = "https://iptv-org.github.io/api/channels.json"
STREAMS_JSON_URL = "https://iptv-org.github.io/api/streams.json"


def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []


def search_channels_by_country(channels, country_code):
    return [channel for channel in channels if channel.get('country') == country_code.upper()]


def match_channels_to_streams(channels, streams):
    channel_stream_map = {}
    for channel in channels:
        channel_streams = [stream['url'] for stream in streams if stream['channel'] == channel['id']]
        if channel_streams:
            channel_stream_map[channel['name']] = channel_streams[0]
    return channel_stream_map


def open_stream_with_streamlink(stream_url):
    # Command to open the stream with Streamlink; adjust the quality as needed
    command = ['streamlink', stream_url, 'best']
    try:
        # Launch Streamlink and wait for it to start streaming (non-blocking)
        process = subprocess.Popen(command)
        return process
    except subprocess.CalledProcessError as e:
        print(f"Error opening stream with Streamlink: {e}")
        return None


def check_stream(process):
    """Check if the Streamlink process is still running."""
    if process.poll() is None:
        return True  # Stream is still active
    return False  # Stream has ended or failed


def restart_stream(process, stream_url):
    if process:
        process.terminate()  # Terminate the old process if it's still running
    return open_stream_with_streamlink(stream_url)


def main():
    channels = fetch_data(CHANNELS_JSON_URL)
    streams = fetch_data(STREAMS_JSON_URL)

    if not channels or not streams:
        return

    country_code = input("Enter the country code you are looking for (e.g., 'US', 'CN'): ").upper()
    filtered_channels = search_channels_by_country(channels, country_code)
    channel_stream_map = match_channels_to_streams(filtered_channels, streams)

    if not channel_stream_map:
        print("No channels found for this country.")
        return

    for idx, channel_name in enumerate(channel_stream_map, 1):
        print(f"{idx}. {channel_name}")

    choice = int(input("Select a channel to open with VLC (enter number): ")) - 1
    selected_channel = list(channel_stream_map.keys())[choice]
    selected_stream_url = channel_stream_map[selected_channel]

    print(f"Opening {selected_channel} with VLC...")
    process = open_stream_with_streamlink(selected_stream_url)

    # Monitor the stream and restart if necessary
    while True:
        time.sleep(60)  # Check every 1 minute
        if not check_stream(process):
            print("Stream has ended or failed, restarting...")
            process = restart_stream(process, selected_stream_url)


if __name__ == "__main__":
    main()
