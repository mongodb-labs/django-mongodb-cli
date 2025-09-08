import requests
import subprocess

# Define groups: each group has a name, a list of packages, and a test command
groups = [
    {
        "name": "default",
        "packages": ["dnspython"],
        "test_command": [
            "python",
            "-c",
            "import pymongo; print('pymongo imported successfully')",
        ],
    },
]

results = {}

for group in groups:
    group_name = group["name"]
    test_command = group["test_command"]
    packages = group["packages"]

    print(f"\n=== Processing group: {group_name} ===")
    results[group_name] = {}

    for package_name in packages:
        print(f"\nFetching versions for {package_name}...")
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url)
        data = response.json()

        # Sorted list of versions (excluding alphas/betas/rc/dev)
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
                    ["pip", "install", f"{package_name}=={version}"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                # Run test command
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

            # Uninstall before moving to next version
            subprocess.run(
                ["pip", "uninstall", "-y", package_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        results[group_name][package_name] = package_results

# Markdown Summary
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
