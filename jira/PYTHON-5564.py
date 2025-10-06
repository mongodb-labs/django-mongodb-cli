import argparse
import requests
import subprocess
import sys

# Define groups: each group has a name, a list of packages, and a test command
groups = [
    {
        "name": "default",
        "packages": [
            {
                "name": "dnspython",
                "test_command": [
                    "python",
                    "-c",
                    "import dns; print('imported successfully')",
                ],
            }
        ],
    },
    {
        "name": "aws",
        "packages": [
            {
                "name": "pymongo-auth-aws",
                "test_command": [
                    "python",
                    "-c",
                    "import pymongo_auth_aws; print('imported successfully')",
                ],
            }
        ],
    },
    {
        "name": "encryption",
        "packages": [
            {
                "name": "pymongo-auth-aws",
                "test_command": [
                    "python",
                    "-c",
                    "import pymongo_auth_aws; print('imported successfully')",
                ],
            },
            {
                "name": "pymongocrypt",
                "test_command": [
                    "python",
                    "-c",
                    "import pymongocrypt; print('imported successfully')",
                ],
            },
            # {
            #     "name": "certifi",
            #     "test_command": [
            #         "python",
            #         "-c",
            #         "import certifi; print('imported successfully')",
            #     ],
            # },
        ],
    },
    {
        "name": "gssapi",
        "packages": [
            {
                "name": "pykerberos",
                "test_command": [
                    "python",
                    "-c",
                    "import kerberos; print('imported successfully')",
                ],
            },
            {
                "name": "winkerberos",
                "test_command": [
                    "python",
                    "-c",
                    "import winkerberos; print('imported successfully')",
                ],
            },
        ],
    },
    {
        "name": "ocsp",
        "packages": [
            # {
            #     "name": "certifi",
            #     "test_command": [
            #         "python",
            #         "-c",
            #         "import certifi; print('imported successfully')",
            #     ],
            # },
            {
                "name": "pyopenssl",
                # "test_command": [
                #     "python",
                #     "-c",
                #     "import sys\ntry:\n    import OpenSSL\nexcept OSError:\n    print('import failed')\n    sys.exit(1)\nprint('imported successfully')",
                # ],
                "test_command": [
                    "python",
                    "-c",
                    # "from pymongo.ssl_support import HAVE_PYSSL; print(HAVE_PYSSL)",
                    "import sys\ntry:\n    import OpenSSL\nexcept OSError:\n    print('import failed')\n    sys.exit(1)\nprint('imported successfully')",
                ],
            },
            # {
            #     "name": "requests",
            #     "test_command": [
            #         "python",
            #         "-c",
            #         "import pyopenssl; print('imported successfully')",
            #     ],
            # },
            {
                "name": "cryptography",
                "test_command": [
                    "python",
                    "-c",
                    "import cryptography; print('imported successfully')",
                ],
            },
            {
                "name": "service_identity",
                "test_command": [
                    "python",
                    "-c",
                    "import service_identity; print('imported successfully')",
                ],
            },
        ],
    },
    {
        "name": "snappy",
        "packages": [
            {
                "name": "python-snappy",
                "test_command": [
                    "python",
                    "-c",
                    "import snappy; print('imported successfully')",
                ],
            },
        ],
    },
    {
        "name": "zstd",
        "packages": [
            {
                "name": "zstandard",
                "test_command": [
                    "python",
                    "-c",
                    "import zstd; print('imported successfully')",
                ],
            },
        ],
    },
]


def main():
    parser = argparse.ArgumentParser(
        description="Compatibility tester for package groups."
    )
    parser.add_argument(
        "--group",
        help="Run only this group (must match one of the defined group names). If omitted, runs all groups.",
    )
    parser.add_argument(
        "--package",
        help="Run only this package (must match a package in the selected group(s)). If omitted, runs all packages in selected groups.",
    )

    args = parser.parse_args()

    # Decide which groups to run
    if args.group:
        selected_groups = [g for g in groups if g["name"] == args.group]
        if not selected_groups:
            print(f"Group '{args.group}' not found.")
            sys.exit(1)
    else:
        selected_groups = groups

    # If a package is specified, filter the packages inside selected groups
    if args.package:
        found_any = False
        filtered_groups = []
        for g in selected_groups:
            matching_pkgs = [
                pkg for pkg in g["packages"] if pkg["name"] == args.package
            ]
            if matching_pkgs:
                filtered_groups.append({"name": g["name"], "packages": matching_pkgs})
                found_any = True
        if not found_any:
            print(f"Package '{args.package}' not found in selected group(s).")
            sys.exit(1)
        selected_groups = filtered_groups

    results = {}

    for group in selected_groups:
        group_name = group["name"]
        results[group_name] = {}

        print(f"\n=== Processing group: {group_name} ===")

        for pkg_info in group["packages"]:
            package_name = pkg_info["name"]
            test_command = pkg_info["test_command"]

            print(f"\nFetching versions for {package_name}...")
            url = f"https://pypi.org/pypi/{package_name}/json"
            response = requests.get(url)
            data = response.json()

            versions = sorted(
                v
                for v in data["releases"].keys()
                if all(x not in v for x in ["a", "b", "rc", "dev"])
            )

            package_results = []
            for version in versions:
                print(f"\nInstalling {package_name}=={version}...")
                try:
                    subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "install",
                            f"{package_name}=={version}",
                        ],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )

                    try:
                        subprocess.run(test_command, check=True)
                        print(f"✅ Success for {version}")
                        package_results.append((version, "success"))
                    except subprocess.CalledProcessError:
                        print(f"⚠️ Installed {version} but test failed")
                        package_results.append((version, "test failed"))

                except subprocess.CalledProcessError:
                    print(f"❌ Fail for {version}")
                    package_results.append((version, "install failed"))

                subprocess.run(
                    [sys.executable, "-m", "pip", "uninstall", "-y", package_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

            results[group_name][package_name] = package_results

    # Markdown Summary (per group)
    print("\n# Compatibility Test Report\n")
    for group_name, pkgs in results.items():
        print(f"## Group: {group_name}\n")
        for pkg, res in pkgs.items():
            print(f"### Package: `{pkg}`\n")
            print("| Version | Status |")
            print("|---------|--------|")
            for version, status in res:
                status_icon = {
                    "success": "✅",
                    "install failed": "❌",
                    "test failed": "⚠️",
                }.get(status, status)
                print(f"| {version} | {status_icon} {status} |")
            print("\n")

    # Aggregate Report
    print("\n# Aggregate Compatibility Summary\n")
    print("| Group | Package | Version | Status |")
    print("|-------|---------|---------|--------|")
    for group_name, pkgs in results.items():
        for pkg, res in pkgs.items():
            for version, status in res:
                status_icon = {
                    "success": "✅",
                    "install failed": "❌",
                    "test failed": "⚠️",
                }.get(status, status)
                print(f"| {group_name} | {pkg} | {version} | {status_icon} {status} |")


if __name__ == "__main__":
    main()
