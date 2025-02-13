"""Simple workflow for downloading files via FTP."""

import subprocess
import logging
import re
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Union
from latch.executions import rename_current_execution
from latch import workflow, custom_task
from latch.types import (
    LatchAuthor,
    LatchDir,
    LatchMetadata,
    LatchParameter,
    LatchRule
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@dataclass_json
@dataclass
class Ftp_url:
    user: str
    password: str
    host: str = "usftp21.novogene.com"
    port: str = "21"


@custom_task(cpu=12, memory=64, storage_gib=2000)
def download_task(
    out_dir: str,
    source_url: Union[Ftp_url, str]
) -> LatchDir:
    logging.info(f"Attempting to set execution name to: {out_dir}")
    try:
        rename_current_execution(str(out_dir))
        logging.info("SUCCESS")
    except:
        logging.info("FAILED to rename")

    if type(source_url) is str:
        if source_url.startswith("lftp -c"):
            logging.info("Using lftp for download.")

            # set permissionon shell script
            subprocess.run(["chmod", "+x", "/root/wf/scripts/parallel_sftp.sh"])

            # make out_dir
            subprocess.run(["mkdir", "-p", f"/root/{out_dir}"])
            # Parse the SFTP URL
            pattern = r'sftp://([^:]+):([^@]+)@([^:]+):(\d+)'
            match = re.search(pattern, source_url)
            if match:
                username, password, host, port = match.groups()

                # Build the command for our shell script
                _ftp_cmd = f'/root/wf/scripts/parallel_sftp.sh -u "{username}" -p "{password}" -h "{host}" -P "{port}" -j 8 -r "01.RawData" -l "/root/{out_dir}"'

                # Print the command (for verification)
                print(f"Generated command: {_ftp_cmd}")
                useShell = True
            else:
                raise Exception(
                    "Download url incorrect format; please check url.")

        else:
            _ftp_cmd = [
                "wget",
                "-c",
                "-r",
                source_url,
                "-P",
                f"/root/{out_dir}"
            ]
            useShell = False
    elif type(source_url) is Ftp_url:
        _ftp_cmd = [
            "wget",
            "-c",
            "-r",
            (f"ftp://{source_url.user}:"
            f"{source_url.password}@"
            f"{source_url.host}:"
            f"{source_url.port}/"),
            "-P",
            f"/root/{out_dir}"
        ]
        useShell = False
    else:
        raise Exception("Download url incorrect format; please check url.")
    logging.info(f"Running command: {_ftp_cmd}")
    subprocess.run(_ftp_cmd, shell=useShell)

    return LatchDir(f'/root/{out_dir}', f'latch:///downloads/{out_dir}')


metadata = LatchMetadata(
    display_name="ftp downloader",
    author=LatchAuthor(
        name="AtlasXomics, Inc.",
        email="jamesm@atlasxomics.com",
        github="https://github.com/atlasxomics",
    ),
    repository="https://github.com/atlasxomics/ftp_downloader",
    license="MIT",
    parameters={
        "out_dir": LatchParameter(
            display_name="output directory",
            description="Name of Latch subdirectory for downloaded file; \
                files will be saved to /downloads/{output directory}.",
            batch_table_column=True,
            rules=[
                LatchRule(
                    regex="^[^/].*",
                    message="output directory cannot start with a '/'"
                )
            ]
        ),
        "source_url": LatchParameter(
            display_name="download url",
            description="Ftp parameters or single url for download.",
            batch_table_column=True
        )
    },
    tags=[],
)


@workflow(metadata)
def ftp_download(
    out_dir: str,
    source_url: Union[Ftp_url, str]
) -> LatchDir:
    """Simple workflow for downloading files via FTP.
    Downloader for FTP or other
    ----
    Simple Latch UI for downloading files directly into Latch Console.

    Allows downloads with either FTP parameters or download url.

    Files are saved in the specified output directory in
    latch:///downloads/outdir.

    FTP will download recursively with url format:
    ```
    ftp://user:password@host:port/
    ```
    Providing full url will download recurively for directories, once for
    files.

    Tested with ftp and https downloads; interally just calling
    ```
    wget -c  -r <link> -P <output>
    ```
    so should work with most download urls.
    """

    return download_task(out_dir=out_dir, source_url=source_url)
