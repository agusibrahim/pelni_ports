# Pelni Port Scraper

This project is designed to scrape port and destination data from the Pelni website (pelni.co.id). The resulting data is saved in JSON format. This process can be run locally or fully automated using GitHub Actions.

## Features

- **Port Data Scraping**: Fetches detailed information about each port served by Pelni, including its name, code, city, and unique ID.
- **Destination Data Scraping**: Fetches the list of connected destinations for each origin port.
- **Local Execution**: The script can be run in a local environment using the Bun runtime.
- **Automation**: The scraping process is scheduled to run automatically every week via GitHub Actions, ensuring the data remains up-to-date.

## Output File

The output of the scraping process is saved in the `pelni_ports.json` file, with the following data structure for each port entry:

```json
[
  {
    "name": "TANJUNG PRIOK",
    "code": "TPR",
    "city": "JAKARTA",
    "id": 1,
    "dest": "2,3,4,5,6,7,8,9,10"
  }
]
```

- `name`: The name of the port.
- `code`: The unique code for the port.
- `city`: The city where the port is located.
- `id`: The internal ID used by the Pelni system.
- `dest`: A string containing the IDs of connected destinations, separated by commas.

## Usage

### 1. Local Execution

To run the scraper script locally, follow these steps:

1.  **Ensure Bun is installed.** If not, install it from the [official Bun website](https://bun.sh/).
2.  **Install project dependencies:**
    ```sh
    bun install
    ```
3.  **Run the scraper script:**
    ```sh
    bun run scrape.ts
    ```
4.  Once completed, an output file named `pelni-destinations.json` will be created in the root directory.

### 2. Automated Execution (GitHub Actions)

- This project is configured to run the scraping process automatically every Sunday at 00:00 UTC.
- The GitHub Actions workflow will execute the script, output file is `pelni_ports.json`, and automatically commit and push the updated file to the repository.
- You can also trigger this workflow manually through the **Actions** tab on the repository's GitHub page.

## Technology Stack

- **Runtime**: [Bun](https://bun.sh/)
- **Language**: TypeScript
- **Scraping**: Puppeteer
- **Automation**: GitHub Actions
