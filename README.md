# Personio Documents Downloader

Downloads the latest document from Personio of a specific user using the Personio Web UI.
This script is for normal users, who don't have access to the Personio API.

## Options

### Required arguments:
- `-l https://your-company.personio.de`, `--url https://your-company.personio.de`: Link/Url to your Personio Web UI
- `-u some@mail.com`, `--username some@mail.com`: Username or email of your Personio user
- `-p PASSWORD`, `--password PASSWORD`: Password of your Personio user

### Optional arguments:
- `-h`, `--help`: Show this help message and exit.
- `-d DOWNLOAD_PATH`, --directory DOWNLOAD_PATH`: Target directory of the downloaded file. Can be absolute or relative. Default is the current directory.
