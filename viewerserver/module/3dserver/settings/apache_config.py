from fileinput import FileInput
import argparse
import os
from dotenv import load_dotenv
load_dotenv(verbose=True)

def modified_apache_config(
    file_path: str, 
    config_key: str, 
    new_value: str
) -> None:
    with FileInput(file_path, inplace=True) as file:
        for line in file:
            if config_key in line:
                line = " ".join(line.split(" ")[:-1]) + f" {new_value}\n"
            print(line, end='')

if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="Apache Server Config")
    parse.add_argument(
        "--config",
        default=None,
        help="path to config file"
    )
    args = parse.parse_args()
    config_key = "ProxyPass"
    host = os.getenv('HOST')[:-1]
    port_launcher = os.getenv('PORT_LAUNCHER')[:-1]
    new_value = f"http://{host}:{port_launcher}/viewer/"
    if not args.config is None:
        modified_apache_config(args.config, config_key, new_value)