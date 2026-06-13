# Sophie 1.1v - Autonomous YouTube Content Creator

Sophie is an intelligent robot powered by Python that autonomously creates and uploads YouTube content without any human intervention. From downloading assets to publishing videos and sending reports, Sophie handles the entire pipeline seamlessly.

## New YouTube Channel
Visit the New YouTube channel to see the final results. **[Calm & Green - Sophie's Channel](https://www.youtube.com/@CalmGreen-x6x).**


## New Features

The second version of Sophie Robot is more intelligent than the initial version 1.0, Features of the new version 1.1v:

1. Create two types of videos (regular and short) videos, instead of one.
2. Changes to the storage, editing, and import mechanisms with Drive, making them more efficient on the one hand and overcoming authentication issues on the other.
3. One of the most powerful features of the new version is automatic error handling. This version is capable of handling errors and sending all results in a daily email report.
4. The image with waves has been replaced with HD and 4K pixel video, which brings the video to life more than the first version.
5. It is capable of distinguishing between regular and short videos and processing them accordingly.


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
   cd sophie-robot/sophie-v-1-1
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
   python sophie_v_1_1.py
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
