import re
import requests
COCOAPOD_SPEC_URL = "https://raw.githubusercontent.com/CocoaPods/Specs/master/Specs/{pkg_name}/{version}/{pkg_name}.podspec.json"
API_URL = "http://metrics.cocoapods.org/api/v1/pods/{pkg_name}.json"
PATTERNS = [r"^pod '([\wd]+)',\s{0,}'~>\s{0,}?([\wd.]+)", r"^pod '([\wd]+)'$"]


def fetch_info_from_spec(pkg_name, version):
    r = requests.get(COCOAPOD_SPEC_URL.format(
        version=version,
        pkg_name=pkg_name
    ))
    if r.ok:
        print "{} - {}".format(pkg_name, r.json()["summary"])
    else:
        digits = version.split(".")
        if len(digits) < 3:
            digits.append(0)
            version = ".".join(map(str, digits[:3]))
            fetch_info_from_spec(pkg_name, version)
        else:
            fetch_info_from_api(pkg_name)


def fetch_info_from_api(pkg_name):
    r = requests.get(API_URL.format(
        pkg_name=pkg_name
    ))
    summary = r.json()["cocoadocs"]["rendered_summary"]
    print "{package} - {summary}".format(
        package=pkg_name,
        summary=summary.replace("<p>", "").replace("</p>", "")
    )


def main():
    with open("Podfile") as f:
        lines = f.read()
        for line in lines.split("\n"):
            for PATTERN in PATTERNS:
                matched = re.match(PATTERN, line)
                if matched is not None:
                    groups = matched.groups()
                    pkg_name, version = (None, None)
                    if len(groups) > 1:
                        pkg_name, version = groups
                    else:
                        (pkg_name, ) = groups

                    if version is not None:
                        fetch_info_from_spec(pkg_name, version)
                    else:
                        fetch_info_from_api(pkg_name)

                    break


if __name__ == "__main__":
    main()
