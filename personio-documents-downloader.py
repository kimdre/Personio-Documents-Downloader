#!/usr/bin/env python3

import re
import requests
import datetime
from bs4 import BeautifulSoup
from argparse import ArgumentParser, SUPPRESS


def get_arguments():
    """Load program arguments"""
    parser = ArgumentParser(
        prog="Personio Documents Downloader",
        description="Downloads the latest documents from Personio of a specific user",
        epilog="For more informations see https://github.com/kimdre/personio-documents-downloader",
        add_help=False
    )

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument(
        "-l", "--url",
        dest="personio_url",
        help="Link/Url to your Personio Web UI",
        metavar="https://your-company.personio.de",
        required=True
    )

    required.add_argument(
        "-u", "--username",
        dest="username",
        help="Username or email of your Personio user",
        metavar="some@mail.com",
        required=True
    )
    required.add_argument(
        "-p", "--password",
        dest="password",
        help="Password of your Personio user",
        required=True
    )

    optional.add_argument(
        '-h',
        '--help',
        action='help',
        default=SUPPRESS,
        help='Show this help message and exit.'
    )

    optional.add_argument(
        "-d", "--directory",
        dest="download_path",
        help="Target directory of the downloaded file. Can be absolute or relative. Default is the current directory.",
        default="./",
    )

    optional.add_argument(
        "-t", "--timerange",
        dest="timerange",
        type=int,
        help="Time range in days from today in which to search for files. Defaults to last 7 days.",
        metavar="7",
        default="7",
    )

    return parser.parse_args()


def get_employee_id(response: requests.models.Response) -> int:
    """Get employee id from response in Personio Web UI"""
    soup = BeautifulSoup(response.content, "html.parser")
    try:
        return int(re.search('window.EMPLOYEE={id:(.*)};', str(soup)).group(1))
    except ValueError as e:
        raise ValueError("The employee ID could not be retrieved.", e)


def login(url: str, credentials: dict) -> [requests.Session, int]:
    """Create session, login to Personio Web UI and return the session and the employee id"""
    session = requests.session()
    response = session.post(url, data=credentials)
    if response.status_code == 200:  # If the request went Ok we usually get a 200 status.
        return session, get_employee_id(response)
    else:
        exit("Login failed")


def get_latest_files(url: str, session: requests.Session, timerange: int) -> tuple[str, datetime.datetime, str]:
    """Return name, url and datetime of all files found in the specified timerange in the user's documents page"""
    response = session.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    files = []
    date_format = '%d.%m.%Y'
    now = datetime.datetime.now()

    for row in soup.find_all('table')[0].tbody.find_all('tr')[1:]:
        row = row.find_all('td')
        files.append(
            {
                "name": row[1].text.strip(),
                "date": datetime.datetime.strptime(row[4].text.strip(), date_format),
                "url": row[5].find(class_="download-document-link").get("href").strip()
            }
        )

    return [file for file in files if (now - file["date"]).days <= timerange]


def download_file(url: str, path: str, session: requests.Session) -> None:
    """Open url and download file using the given session"""
    print(f"Starting download to \"{path}\"")
    response = session.get(url)
    fd = open(path, 'wb')
    fd.write(response.content)
    fd.close()
    print("Download completed")


if __name__ == '__main__':
    args = get_arguments()
    session, employee_id = login(
        url=f"{args.personio_url}/login/index",
        credentials={"email": str(args.username), "password": str(args.password)}
    )

    files = get_latest_files(
        url=f"{args.personio_url}/documents/employee-documents/{employee_id}/",
        session=session,
        timerange=args.timerange
    )

    for file in files:
        download_file(path=args.download_path + file["name"], url=file["url"], session=session)

    session.close()
