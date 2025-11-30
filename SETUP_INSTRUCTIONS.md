# Google Cloud Credentials Setup Guide

To use the Diary App, you need to set up a Google Cloud Project and generate a `credentials.json` file. This allows the app to securely access your Google Docs.

## Step 1: Create a Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown at the top left and select **New Project**.
3. Name it "Diary App" (or similar) and click **Create**.
4. Select the newly created project.

## Step 2: Enable APIs
1. In the left sidebar, go to **APIs & Services** > **Library**.
2. Search for **Google Docs API**.
3. Click on it and click **Enable**.
4. Go back to the Library, search for **Google Drive API**.
5. Click on it and click **Enable**.

## Step 3: Configure OAuth Consent Screen
1. In the left sidebar, go to **APIs & Services** > **OAuth consent screen**.
2. Select **External** and click **Create**.
3. **App Information**:
   - App name: "Diary App"
   - User support email: Select your email.
   - Developer contact information: Enter your email.
4. Click **Save and Continue**.
5. **Scopes**: You can skip this step (click Save and Continue).
6. **Test Users**:
   - Click **Add Users**.
   - Enter your own Google email address (the one you want to save the diary to).
   - Click **Add**, then **Save and Continue**.
7. Review and click **Back to Dashboard**.

## Step 4: Create Credentials
1. In the left sidebar, go to **APIs & Services** > **Credentials**.
2. Click **Create Credentials** at the top and select **OAuth client ID**.
3. **Application type**: Select **Desktop app**.
4. **Name**: Leave as "Desktop client 1" or change it.
5. Click **Create**.

## Step 5: Download and Place File
1. A pop-up will appear. Click **Download JSON** (the download icon).
2. Rename the downloaded file to **`credentials.json`**.
3. Move this file into your project folder:
   `c:\Users\peakb\antigravity\new_diary\`

## Step 6: Run the App
Once the file is in place, let me know, and I will start the server!
