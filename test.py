import os
from time import sleep
import time
import sys
import re
try:
    from pexpect import pxssh as pxssh
except:
    print("pxssh is not installled")

class SshConnection(object):
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
        try:
            self.ssh_conn = self.ssh_conn(self.hostname, self.username, self.password)
            self.ssh_conn.PROMPT = "[#>$]"
            self.ssh_conn.timeout = 5000
        except Exception as err:
            print("Connection to %s failed" % self.hostname)

    def ssh_conn(self, hostname, username, password):
        try:
            print("Connecting to ", hostname)
            self.ssh = pxssh.pxssh()
            print(hostname, username, password)
            self.ssh.login(hostname, username, password, original_prompt="[#>$]", login_timeout=5000, auto_prompt_reset=False)
            print("Connected")
        except pxssh.ExceptionPxssh as error:
            print("Login failed")
            print(str(error))
            self.ssh = False
        return self.ssh

    def cmd(self, command, allowPrint=True, sleep=False, killApptest=False):
        prompt_repeat = 0

        retries = self.ssh_conn.timeout
        tmpbuf = ''
        self.ssh_conn.buffer = ''
        self.ssh_conn.sendline(command)
        time.sleep(0.02)
        if command.find("exit") != -1:
            return self.ssh_conn.before
        if sleep:
            time.sleep(20)
        if not self.ssh_conn.prompt(timeout=1):
            while self.ssh_conn.prompt(timeout=1) is not True and prompt_repeat < retries:
                if (self.ssh_conn.buffer != None):
                    tmpbuf = tmpbuf + self.ssh_conn.buffer
                self.ssh_conn.buffer = ''
                prompt_repeat += 1
            if prompt_repeat == retries:
                print("Failed to detect prompt %s for %s times" % (self.ssh_conn.PROMPT, retries))
                print(tmpbuf)
                if killApptest:
                    print("=" * 100)
                    print(
                    "Failed to detect prompt %s for %s times for %s cmd" % (self.ssh_conn.PROMPT, retries, command))
                    print("=" * 100)
                    cleanup()
                    sys.exit()
                return False
            else:
                #print(prompt_repeat)
                #print("return from else: prompt_repeat == retries")
                return tmpbuf
        else:
            # if(debug == "ON"):
            tmpbuf = self.ssh_conn.before

            if allowPrint:
                print(tmpbuf)
            return tmpbuf

    def close(self):
        try:
            self.ssh_conn.close()
            print("connection to %s closed" % self.hostname)
        except Exception as err:
            print(err)

def usage():
    print("python test.py <ip> <username> <passwd> <xdk_path> <type> <testname or command> <enableLog>")
    print("    command = ls / ... (shell command)")
    print("    type = input is testname or command, 0 = testname, 1 = command")
    print("    enableLog = 0 or 1")
    cleanup()
    sys.exit()

def main():
    argmnts = sys.argv[1:]  # ip username passwd xdk_path type testname/command enableLog
    if len(argmnts) == 0:
        usage()
    elif argmnts[0] in "help":
        usage()
    elif len(argmnts) < 7:
        usage
    else:
        global testName
        global testType
        global pathToXdk
        global tmpbuf
        global enableLog
        global command

        LOGS_DIR = os.path.join("TestResults")
        print("Run results location: {}".format(os.path.abspath(LOGS_DIR)))
        print(argmnts)

        ip = argmnts[0]
        username = argmnts[1]
        passwd = argmnts[2]
        connection = SshConnection(ip, username, passwd)
        pathToXdk = argmnts[3]
        testType = argmnts[4]
        
        if argmnts[4] == '0':
            testName = argmnts[5]
            print("type is 0")
        elif argmnts[4] == '1':
            command = str(argmnts[5])
            print("type is 1")

        if argmnts[6] == '0':
            enableLog = False
            print("enableLog is False")
        elif argmnts[6] == '1':
            enableLog = True
            print("enableLog is True")

        print("command: " + command)
        connection.cmd(command, enableLog)
#        print(connection.cmd(command, enableLog))
        

def cleanup():
#    LOGS_DIR = os.path.join("TestResults")
#    CMD = "chmod -R a+rwx " + LOGS_DIR
#    os.system(CMD)
    return

if __name__ == "__main__":
    try:
        main()
        cleanup()
    except:
        cleanup()
