#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import yaml

def call(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE):
    try:
        return (subprocess.check_output(command, stdin=stdin, stderr=stderr), None)
    except subprocess.CalledProcessError as error:
        return (None, error)

def check_local_system():
    print("Checking local system...")

    if is_call_returns_error(call("./local_system_check.sh")):
        print("  This system does not meet project requirements")
        print("  Call `local_system_check.sh` for more detailed report")

        sys.exit(1)

    print("  Success")

    return True

def check_remote_system(domain):
    print("Checking remote connection...")

    if is_call_returns_error(call(["ssh", "-T", domain, "exit"])):
        print("  Cannot connect to given domain")

        sys.exit(1)

    print("  Success")

    print("Checking remote system...")

    if is_call_returns_error(call(["scp", "./remote_system_check.sh", domain + ":."])):
        print("  Remote system does not meet project requirements")
        print("  Call `remote_system_check.sh` on this system for more detailed report")

        sys.exit(1)

    print("  Success")

    print("Cleaning remote system...")

    if is_call_returns_error(call(["ssh", "-T", domain, "rm -f remote_system_check.sh"])):
        print("  Error during cleaning remote system")
        print("  You need manually delete `remote_system_check.sh`")
    else:
        print("  Success")

    return True

def is_call_returns_error(call):
    return (call[0] == None) and (call[1] != None)


def main():
    parser=argparse.ArgumentParser(description="Test launcher")
    parser.add_argument("domain", help="Where will you host your test servers?")
    parser.add_argument("-u", "--users", type=int, default=32, help="Number of JMeter users (default 32)")
    parser.add_argument("-r", "--repeats", type=int, default=8, help="Number of JMeter scripts repeats (default 8)")
    
    args=parser.parse_args()

    domain=args.domain
    users=args.users
    repeats=args.repeats

    check_local_system()

    check_remote_system(domain)

    send_package(domain)

    directory=unpack_package(domain)

    test(domain, directory, users, repeats)

    remove_directory(domain, directory)

def remove_directory(domain, directory):
    print("Cleaning Docker...")

    if is_call_returns_error(call(["ssh", "-T", domain, "cd " + directory + " && docker-compose stop"])):
        print("  Cannot stop using `docker-compose` command")

        sys.exit(1)
    else:
        print("  Success")

    print("Removing temporary directory...")

    if is_call_returns_error(call(["ssh", "-T", domain, "rm -rf " + directory])):
        print("  Cannot delete temporary directory")
        print("  Try do it manually: `" + directory + "`")
    else:
        print("  Success")

def send_package(domain):
    print("Preparing package...")

    if is_call_returns_error(call(["zip", "-r9", ".package.zip", ".env.example", "docker-compose.yml", "disable_service.sh", "enable_service.sh", "httpd/", "lighttpd/", "nginx/", "public/"])):
        print("  Error during packing")

        sys.exit(1)

    print("  Success")

    print("Sending package...")

    if is_call_returns_error(call(["scp", "./.package.zip", "./unpack.sh", domain + ":."])):
        print("  Cannot send package to " + domain)

        sys.exit(1)

    print("  Success")

    print("Removing package...")

    if is_call_returns_error(call(["rm", "-f", ".package.zip"])):
        print("  Cannot remove package")
        print("  You need manually delete `.package.zip`")
    else:
        print("  Success")

def test(domain, directory, users, repeats):
    def get_public_ip(domain):
        print("Getting server public IP...")

        output, error=call(["ssh", "-T", domain, "curl -s http://whatismyip.akamai.com/"])

        if is_call_returns_error((output, error)):
            print("  Cannot get server public IP")

            sys.exit(1)

        print("  Success")

        return output.decode("utf-8").strip()

    def get_scripts_as_parameters():
        scripts=[file for file in os.listdir("./public/scripts/") if not file.endswith(".gitkeep")]
        return ["-Jfiles.scripts." + str(index) + "=" + file for index, file in enumerate(scripts, 1)]

    def get_static_files_as_parameters():
        static_files=[file for file in os.listdir("./public/static/") if not file.endswith(".gitkeep")]
        return ["-Jfiles.static." + str(index) + "=" + file for index, file in enumerate(static_files, 1)]

    def list_services():
        services=[]

        with open("./docker-compose.yml", "r") as stream:
            try:
                compose=yaml.load(stream)

                for service in compose["services"]:
                    if "depends_on" in compose["services"][service]:
                        services.append(service)
            except yaml.YAMLError as error:
                print("  Error during docker-compose.yml reading")

                sys.exit(1)

        return services

    def save_cadvisor_logs(service, logs):
        print("Saving cAdvisor logs...")

        cadvisor=open("./" + service + "/cadvisor.json", "wb")

        if cadvisor.write(logs) > 0:
            print("  Success")
        else:
            print("  Error during saving cAdvisor logs")

    def test_service(service, target, users, repeats):
        print("Testing " + service.upper() + " server...")

        start=call(["ssh", "-T", domain, "cd " + directory + " && ./enable_service.sh " + service])
        jmeter=call(["jmeter", "-n", "-t", "./test_plan.jmx", "-l", "./" + service + "/log.jtl", "-j", "./" + service + "/jmeter.log", "-Jtarget=" + target, "-Jservice=" + service, "-Jusers=" + str(users), "-Jrepeats=" + str(repeats)] + get_static_files_as_parameters() + get_scripts_as_parameters())
        cadvisor=call(["ssh", "-T", domain, "curl", "http://localhost:8080/api/v1.3/docker/$(docker ps | grep " + service + " | awk -F ' ' '{print $1}')"])
        stop=call(["ssh", "-T", domain, "cd " + directory + " && ./disable_service.sh " + service])

        if is_call_returns_error(start) or is_call_returns_error(jmeter) or is_call_returns_error(cadvisor) or is_call_returns_error(stop):
            print("  Error during testing server " + service)
        else:
            print("  Success")

        output, error=cadvisor
        save_cadvisor_logs(service, output)

    ip=get_public_ip(domain)

    services=list_services()

    for service in services:
        test_service(service, ip, users, repeats)

def unpack_package(domain):
    print("Unpacking package...")

    output, error=call(["ssh", "-T", domain, "./unpack.sh"])

    if is_call_returns_error((output, error)):
        print("  Cannot unpack package")

        sys.exit(1)

    print("  Success")

    temporary_directory=output.decode("utf-8").strip()

    print("Removing unpacker...")

    if is_call_returns_error(call(["ssh", "-T", domain, "rm -f unpack.sh .package.zip"])):
        print("  Cannot remove unpacker and package")
        print("  You need remove this files manually")
    else:
        print("  Success")

    return temporary_directory

if __name__ == "__main__":
    main()

