import os
import requests
import subprocess
import yaml
import re

def send_to_discord(webhook_url, message):
    data = {
        "content": message
    }
    response = requests.post(webhook_url, json=data)
    if response.status_code != 204:
        print(f"Failed to send message to Discord: {response.status_code}, {response.text}")

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Command failed with error: {e.stderr}"

def process_output(output):
    lines = output.splitlines()
    highest_iteration = 0
    total_lines = 0
    iteration_pattern = re.compile(r'output/findit_noformat_(\d+)\.csv')

    for line in lines:
        if line.strip():
            parts = line.split()
            if len(parts) == 2:
                match = iteration_pattern.search(parts[1])
                if match:
                    iteration = int(match.group(1))
                    highest_iteration = max(highest_iteration, iteration)
                    total_lines += int(parts[0])

    iteration_info = f"Current iteration: output/findit_noformat_{highest_iteration}.csv"
    total_lines_info = f"Total lines: {total_lines}"
    
    return f"FindIt experiment status\n\n{iteration_info}\n{total_lines_info}"

def main():
    config_file = "discord_notify.yaml"
    
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    
    command = config.get('command')
    webhook_url = config.get('webhook_url')
    
    output = run_command(command)
    message = process_output(output)
    send_to_discord(webhook_url, message)

if __name__ == "__main__":
    main()

