# How to Get Your Credentials 🔑

Since you're stuck, follow these exact steps. It will take about 5 minutes.

## Part 1: Get the Gemini API Key (Easiest)
1.  Open this link: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2.  Sign in with your main Google Account.
3.  Click the big blue button **"Create API key"**.
4.  Click "Create key in new project".
5.  Copy the long string of characters (starts with `AIza...`).
6.  **Paste that key in the chat.**

---

## Part 2: Get the Service Account (for Sheets/Drive)
This looks scary but just click the buttons in order:

1.  **Create Project**:
    *   Go to [https://console.cloud.google.com/projectcreate](https://console.cloud.google.com/projectcreate)
    *   Name it "Job Agent" and click **Create**.

2.  **Enable APIs**:
    *   Go here: [https://console.cloud.google.com/apis/library/sheets.googleapis.com](https://console.cloud.google.com/apis/library/sheets.googleapis.com) -> Click **Enable**.
    *   Go here: [https://console.cloud.google.com/apis/library/drive.googleapis.com](https://console.cloud.google.com/apis/library/drive.googleapis.com) -> Click **Enable**.

3.  **Create Credentials**:
    *   Go to: [https://console.cloud.google.com/iam-admin/serviceaccounts/create](https://console.cloud.google.com/iam-admin/serviceaccounts/create)
    *   **Service account name**: `agent`
    *   Click **Create and Continue** -> **Done**.

4.  **Download Key (The JSON File)**:
    *   You should see an email like `agent@job-agent-xyz.iam.gserviceaccount.com` in the list.
    *   Click the **Three Dots** (actions) on the right -> **Manage keys**.
    *   Click **Add Key** -> **Create new key** -> Select **JSON** -> **Create**.
    *   A file (e.g., `job-agent-38492.json`) will download to your computer.

5.  **Give It to Me**:
    *   Open that downloaded JSON file with Notepad/TextEdit.
    *   Copy EVERYTHING inside it.
    *   **Paste it in the chat.**

6.  **Crucial Step (Share the Sheet)**:
    *   Copy the email address from step 4 (the `agent@...` one).
    *   Go to your "35 Active Product Roles" Google Sheet.
    *   Click **Share** (top right).
    *   Paste the email and make sure it says **Editor**.
    *   Click **Send**.
