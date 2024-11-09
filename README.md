```markdown
# Document Tracking System

This is a web application for tracking document batches in multiple stages, including sender and receiver details. The system supports document batch creation with QR code generation, status updating, and document retrieval based on multiple criteria.

## Features

- **Document Batch Creation**: Create a batch with multiple documents, including sender and receiver details. A unique batch ID is generated for each batch.
- **QR Code Generation**: Each batch has a QR code that links to a page for checking batch status.
- **Status Update**: Users can update the status of each batch and document based on specific locations.
- **Document Search**: Search for batches based on Batch ID, Sender, Receiver, or view all records.
- **Time Zone Handling**: Converts times to local time (Asia/Bangkok) for display.
- **Pagination**: Both search and status pages support pagination for large datasets.

## Requirements

- **Python 3.10+**
- **Flask**
- **Flask-Mail**
- **Flask-SQLAlchemy**
- **SQLite** (for development)
- **pytz** (for timezone handling)
- **qrcode** (for QR code generation)
- **Semantic UI** (for front-end)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/document-tracking-system.git
   cd document-tracking-system
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables for email configuration in `.env` file or directly in the `app.py`:
   ```plaintext
   MAIL_SERVER=smtp.example.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your_email@example.com
   MAIL_PASSWORD=your_email_password
   ```

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration."
   flask db upgrade
   ```

## Configuration

- Update the `BASE_URL` in `app.py` for QR code generation, based on your server settings.
- Modify the timezone in `app.py` to your local timezone if needed:
  ```python
  local_timezone = pytz.timezone("Asia/Bangkok")
  ```

## Usage

1. **Run the Application**:
   ```bash
   flask run
   ```

2. **Access the Application**:
   Open a web browser and navigate to `http://127.0.0.1:5000`.

### Application Pages

- **Home Page (`/`)**: Main page with navigation.
- **Create Document Batch (`/create_batch`)**: Form to create a new batch with multiple documents.
- **Search Batches (`/search_batches`)**: Search for batches by ID, sender, or receiver, or view all.
- **Update Status (`/update_status/<batch_id>`)**: Update the status and location of specific documents within a batch.
- **Check Status (`/check_status`)**: View status and document details in a batch, with QR code for direct access.

## File Structure

```plaintext
document-tracking-system/
├── app.py                  # Main Flask application
├── models.py               # Database models
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates for different pages
│   ├── create_batch.html
│   ├── search_batches.html
│   ├── check_status.html
│   ├── update_status.html
│   └── menu.html
└── static/                 # Static files, including QR codes
    └── qr_codes/
```

## Deployment

For production, configure a WSGI server like Gunicorn or uWSGI and use a reverse proxy server like Nginx. Adjust the database settings for production use.

## License

This project is licensed under the GPL-3.0 License.

---

### Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

```

### Explanation of Key Sections:
- **Features**: Provides an overview of the system's functionality.
- **Installation**: Includes all setup commands.
- **Configuration**: Explains configuration of environment variables and timezone adjustments.
- **Usage**: Describes the main pages of the app and their purposes.
- **File Structure**: Shows the project layout to help new users navigate

readme.md สร้างโดย chatgpt ด้วย prompt "ช่วยเขียน readme.md ให้ด้วยสิ"
