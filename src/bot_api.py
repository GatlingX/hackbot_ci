import os
import aiohttp
import asyncio
import json
import argparse
import requests
import jq


def generate_github_issues(issues, github_api_key, issues_repo):
    """
    Generate GitHub issues for bugs discovered by the bot.

    This function creates a master issue in the specified GitHub repository
    containing all the bugs found. It uses the GitHub API to create issues
    and requires appropriate authentication and permissions.

    Args:
        issues (list): A list of dictionaries containing bug information.
        github_api_key (str): The GitHub token for authentication.
        issues_repo (str): The full name of the GitHub repository (e.g., "owner/repo").

    Returns:
        None

    Raises:
        Exception: If there are permission issues or other errors when interacting with the GitHub API.

    Note:
        - This function requires a GitHub token with 'issues: write' and 'contents: read' permissions.
        - It creates a master issue with a title format of "HB-{number}".
    """
    from github import Github
    from github import GithubException
    from github import Auth

    auth = Auth.Token(github_api_key)
    g = Github(auth=auth)

    if not issues_repo:
        print("Error: GitHub repository is not specified.")
        return

    # Get a list of the bugs discovered by the bot
    issues_found = [issue for issue in issues if issue.get("bug_id") is not None]
    if len(issues_found) == 0:
        print("No bugs found, skipping issue generation")
        return

    # Get the output repository. This will fail if the github token does not have access to the repository
    repo = None
    try:
        repo = g.get_repo(issues_repo)
    except GithubException as e:
        print(f"Error accessing repository: {e}")
        return

    last_hb_issue = 0
    # Fetch all existing issues in the repository and find the last one created by the bot
    for issue in repo.get_issues(state="all"):
        if issue.title.startswith("HB-"):
            last_hb_issue = int(issue.title.split("-")[1])
            break

    # Create a master issue in the repository that will contain all the bugs.
    # This will fail if the github token does not have write access to the issues
    # permissions:
    # - issues: write
    master_issue = None
    try:
        master_issue = repo.create_issue(title=f"HB-{last_hb_issue + 1}")
    except GithubException as e:
        print(f"Error creating issue: {e}")
        if e.status == 422:
            raise Exception(
                "Validation failed, aborting. This functionality requires a GITHUB_TOKEN with 'issues: write' in the workflow permissions section."
            )
        elif e.status == 403:
            raise Exception(
                "Forbidden, aborting. This functionality requires a GITHUB_TOKEN with 'issues: write' in the workflow permissions section."
            )
        elif e.status == 410:
            raise Exception("Gone, aborting. The repository does not allow issues.")

    # Add each bug as a comment to the master issue
    for issue in issues_found:
        body = f"#{issue.get('bug_id')} - {issue.get('bug_title')}\n{issue.get('bug_description')}"
        master_issue.create_comment(body=body)

    print(f"Created issue: {master_issue.title}")


def authenticate(address, port, api_key):
    url = f"http://{address}:{port}/api/authenticate"
    headers = {"X-API-KEY": f"{api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return True
    else:
        raise Exception(f"Failed: {response.status_code}")


def hack(address: str, port: int, api_key: str, output: str):
    """
    Call the hackbot service on the received source code.

    Args:
        address (str): The ip address of the hackbot service.
        port (int): The port number of the hackbot service.
        api_key (str): The API key for authentication.
        output (str): The file path to save the output results.
    Returns:
        tuple: A tuple containing the status code and response data.

    Raises:
        Exception: If there's an error during the hacking process.
    """

    async def process_stream(response):
        results = []
        async for line in response.content:
            line = line.decode("utf-8")
            if line.startswith("data: "):
                try:
                    json_str = line[5:].strip()  # Remove 'data: ' prefix
                    # Stream to stdout
                    print(f"{json_str}")
                    json_obj = json.loads(json_str)
                    results.append(json_obj)
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON: {json_str}")
        return results

    async def make_request(session, url, data, headers):
        async with session.post(url, data=data, headers=headers) as response:
            return response.status, await process_stream(response)

    async def main():
        # Create the API call for the hackbot service
        url = f"http://{address}:{port}/api/hack"
        headers = {"X-API-KEY": f"{api_key}", "Connection": "keep-alive"}

        data = aiohttp.FormData()
        data.add_field(
            "file",
            open("src.zip", "rb"),
            filename="src.zip",
            content_type="application/zip",
        )
        data.add_field("repo_url", "https://github.com/not_impemented")

        # Make the request to the hackbot service
        async with aiohttp.ClientSession() as session:
            status, response = await make_request(session, url, data, headers)

        # Save the results to a file if the output path is specified
        if output is not None:
            # Check if the output contains a directory
            output_dir = os.path.dirname(output)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    # Append each result to a JSON file
                except OSError as e:
                    print(f"Error creating output file {output}: {e}")

            with open(output, "w") as f:
                json.dump(response, f, indent=2)

        return status, response

    status, response = asyncio.run(main())
    if status != 200:
        raise Exception(f"Failed: {status}: {response}")

    return response


def handle_options():
    parser = argparse.ArgumentParser(
        description="Hackbot API client for interacting with the bot server."
    )
    parser.add_argument(
        "--address", type=str, required=True, help="The address of the bot server."
    )
    parser.add_argument(
        "--port", type=str, required=True, help="The port number of the bot server."
    )
    parser.add_argument(
        "--api_key",
        type=str,
        required=True,
        help="API key for authentication with the bot server.",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=False,
        help="Path to the output file for storing results.",
    )
    parser.add_argument(
        "--authenticate",
        action="store_true",
        default=False,
        help="Perform authentication only without hacking.",
    )

    # Create a subparser for the issue generation options
    issue_parser = parser.add_argument_group("Issue Generation Options")
    issue_parser.add_argument(
        "--generate_issues",
        type=lambda x: x.lower() == "true",
        default=False,
        help="Generate issues based on the hack results (true/false)",
    )
    issue_parser.add_argument(
        "--issues_repo",
        type=str,
        help="The repository to generate issues in (format: username/repo)",
    )
    issue_parser.add_argument(
        "--github_api_key",
        type=str,
        help="GitHub API key for issue generation",
    )
    args = parser.parse_args()

    # Add validation for issue generation options
    if args.generate_issues:
        if not args.issues_repo:
            parser.error("--issues_repo is required when --generate_issues is set")
        if not args.github_api_key:
            parser.error("--github_api_key is required when --generate_issues is set")

    return args


if __name__ == "__main__":

    args = handle_options()

    # Get GITHUB_OUTPUT environment variable
    github_output = os.environ.get("GITHUB_OUTPUT")

    # Print program CLI header
    print("=" * 50)
    print(f"Hackbot {'CI Action' if github_output else 'API Client'}")
    print(f"Server: {args.address}:{args.port}")
    print(f"API Key: {'Set' if args.api_key else 'Not set'}")
    print(f"Output: {args.output if args.output else 'Not specified'}")
    if args.generate_issues:
        print(f"Issue Generation: {args.issues_repo}")
    if args.authenticate:
        print("Authentication only")
    print("=" * 50)
    print()

    # Try the credentials before doing anything else
    try:
        authenticate(args.address, args.port, args.api_key)
        print("Authentication successful")
    except Exception as e:
        print(e)
        exit(1)

    # If we only want to authenticate, we can exit here
    if args.authenticate:
        exit(0)

    # Hack the contract
    try:
        results = hack(
            address=args.address,
            port=args.port,
            api_key=args.api_key,
            output=args.output
        )

        if github_output:
            with open(github_output, "a") as f:
                compact_json = jq.compile(".").input(json.dumps(results)).text()
                f.write(f"results={compact_json}\n")

        # Print the contents of github_output
        if github_output:
            print("Contents of GITHUB_OUTPUT:")
            with open(github_output, "r") as f:
                print(f.read())

    except Exception as e:
        print(e)
        exit(1)

    if args.generate_issues:
        try:
            generate_github_issues(results, args.github_api_key, args.issues_repo)
        except Exception as e:
            print(e)
            exit(1)
