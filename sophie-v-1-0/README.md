# Sophie 1.0v - Autonomous YouTube Content Creator

Sophie is an intelligent robot powered by Python that autonomously creates and uploads YouTube content without any human intervention. From downloading assets to publishing videos and sending reports, Sophie handles the entire pipeline seamlessly.

The process begins by:

1. Downloading the necessary resources for content creation.
2. Combining these resources to produce the final content.
3. Upload this content to the YouTube platform.
4. Send a report containing all details of previous operations.

## YouTube Channel
Visit the YouTube channel to see the final results. **[Music House - Sophie's Channel](https://www.youtube.com/@music-house1245).**


## Features

Sophie automates the complete YouTube content creation workflow:

1. **Asset Download**
   - Automatically downloads background images.
   - Fetches audio tracks/songs for video creation.

2. **Waveform Generation**
   - Creates dynamic audio waveform visualizations from songs.
   - Generates engaging visual representations of audio.

3. **Video Production**
   - Combines background images, audio, and waveforms.
   - Renders professional-quality videos automatically.

4. **YouTube Upload**
   - Uploads finished videos directly to YouTube.
   - Utilizes YouTube Data API v3 for seamless integration.
   - Handles Titles, Descriptions, Tages, and Category.

5. **Automated Reporting**
   - Generates detailed reports of completed tasks.
   - Sends reports directly to your Gmail account.
   - Includes upload status, video links, and performance data.



# Getting Started

## Prerequisites

- Python 3.8+
- Pixabay API key & Jamendo API key.
- Google Cloud Project with YouTube Data API v3 enabled.
- Google app password for email reporting.

## Get Prerequisites

1. **Pixabay API & Jamendo API Key**
   - **Pixabay API**: get your API key from [Here](https://pixabay.com/api/docs/).
   - **Jamendo API Key**: 
      - Get your API key from [Here](https://developer.jamendo.com/v3.0).
      - Copy the client id.
   - Replace the value of these variables with your API keys:
      ```python
      # API Keys
      PIXABAY_API_KEY = "YOUR_API_HERE"
      JAMENDO_API_KEY = "YOUR_API_HERE"
      JAMENDO_CLIENT_ID = "YOUR_CLIENT_ID"
      ```

2. **YouTube Data API v3**
   - Login [Google Cloud Console](https://console.cloud.google.com) with your google account.
   - Create new project.
   - Search for **_"YouTube Data API v3"_**.
   - Enable YouTube Data API.
   - Download `client_secret.json` file.
   - Place your YouTube Data API `client_secret.json` in the `credentials/` folder

3. **Google App Key**
   - Click on your profile photo.
   - Click on "manage your google account".
   - Navigate to **Security**.
   - Ensure 2-Step Verification is turned on.
   - Click on **2-Step Verification** and scroll to the bottom, and select **"App password"**.
   - Enter a custom name and click **Create**.
   - Replace the value of this variable with your new keys:
      ```python
      APP_PASSWORD = "YOUR_KEY_HERE"
      ```


## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ruwo36/sophie-robot.git
   cd sophie-robot/sophie-v-1-0
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```


## Usage

Set your sender and reciver Email:
   ```python
   SENDER_EMAIL = "SENDER_EMAIL_HERE"
   RECEIVER_EMAIL = "RECIVER_EMAIL_HERE"
   ```

Run Sophie via command line:
   ```bash
   python sophie.py
   ```


## Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Contact

For any inquiries or support, please contact:
- My [Gmail](mailto:mayasajeeb123@gmail.com).
- [LinkedIn](https://www.linkedin.com/in/ali-n-ajeeb).
