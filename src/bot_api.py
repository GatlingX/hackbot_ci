import os
import aiohttp
import asyncio
import json
import argparse
import requests

def authenticate(bot_address, bot_port, api_key):
    url = f"http://{bot_address}:{bot_port}/api/authenticate"
    headers = {"X-API-KEY": f"{api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return True
    else:
        raise Exception(f"Failed: {response.status_code}")


def hack(bot_address, bot_port, api_key):
    async def make_request(session, url, data, headers):
        async with session.post(url, data=data, headers=headers) as response:
            # print(f"Content type: {response.content_type}")
            return response.status, await response.text()

    async def process_ndjson(ndjson_str):
        results = []
        for line in ndjson_str.strip().split("\n"):
            if line.startswith("data: "):
                try:
                    json_str = line[5:].strip()  # Remove 'data: ' prefix
                    json_obj = json.loads(json_str)
                    results.append(json_obj)
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON: {json_str}")
        return results

    async def main():
        url = f"http://{bot_address}:{bot_port}/api/hack"
        headers = {"X-API-KEY": f"{api_key}", "Connection": "keep-alive"}

        data = aiohttp.FormData()
        data.add_field(
            "file",
            open("src.zip", "rb"),
            filename="src.zip",
            content_type="application/zip",
        )
        data.add_field("repo_url", f"https://github.com/${{github.repository}}")

        async with aiohttp.ClientSession() as session:
            status, response = await make_request(session, url, data, headers)
            results = await process_ndjson(response)

        # Append each result to a JSON file
        with open("results.json", "w") as f:
            json.dump(results, f, indent=2)

        return status, response, results

    status, response, results = asyncio.run(main())
    if status != 200:
        raise Exception(f"Failed: {status}: {response}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bot_address", type=str, required=True)
    parser.add_argument("--bot_port", type=str, required=True)
    parser.add_argument("--api_key", type=str, required=True)
    parser.add_argument("--authenticate", action="store_true", default=False)
    args = parser.parse_args()

    # Try the credentials before doing anything else
    try:
        authenticate(args.bot_address, args.bot_port, args.api_key)
        print("Authentication successful")
    except Exception as e:
        print(e)
        exit(1)

    # If we only want to authenticate, we can exit here
    if args.authenticate:
        exit(0)

    # Hack the contract
    try:
        results = hack(args.bot_address, args.bot_port, args.api_key)

        # Get GITHUB_OUTPUT environment variable
        github_output = os.environ.get("GITHUB_OUTPUT")

        if github_output:
            with open(github_output, "a") as f:
                f.write(f"results={json.dumps(results)}\n")
        else:
            print("GITHUB_OUTPUT environment variable not found.")
            print(f"results={json.dumps(results)}\n")

    except Exception as e:
        print(e)
        exit(1)
