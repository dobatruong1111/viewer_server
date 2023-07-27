import argparse
import json
import os
from dotenv import load_dotenv
load_dotenv(verbose=True)

def modified_launcher_config(
    path: str, 
    host: str, 
    port_launcher: str, 
    port_apache: str
) -> None:
    with open(path, mode='r+') as file:
        config = json.load(file)
        config["configuration"]["host"] = host
        config["configuration"]["port"] = int(port_launcher)
        config["configuration"]["sessionURL"] = f"ws://{host}:{port_apache}" + "/proxy?sessionId=${id}&path=ws"
        config["resources"][0]["host"] = host
        file.seek(0)
        json.dump(config, file, indent=4)
        file.truncate()

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Launcher Config")
    parser.add_argument(
        "--config",
        default=None,
        help="launcher config file"
    )
    args = parser.parse_args()
    host = os.getenv('HOST')[:-1]
    port_launcher = os.getenv('PORT_LAUNCHER')[:-1]
    port_apache = os.getenv('PORT_APACHE')[:-1]
    if not args.config is None:
        modified_launcher_config(args.config, host, port_launcher, port_apache)