"""Run explicit Audacity scripting commands with bounded response waits."""
import argparse, json, os, queue, threading, time
from pathlib import Path

class AudacityPipe:
    def __init__(self, timeout=45):
        self.timeout = timeout
        if os.name != 'nt':
            raise RuntimeError('This helper targets the Windows Audacity named pipes.')
        prefix = chr(92)*2 + '.' + chr(92) + 'pipe' + chr(92)
        self.to_name = prefix + 'ToSrvPipe'
        self.from_name = prefix + 'FromSrvPipe'
        self.writer = open(self.to_name, 'w', encoding='utf-8', newline='')
        self.reader = open(self.from_name, 'r', encoding='utf-8', newline=None)

    def command(self, command):
        self.writer.write(command + '\r\n\0')
        self.writer.flush()
        result_queue = queue.Queue()
        def receive():
            lines = []
            try:
                while True:
                    line = self.reader.readline()
                    if line == '':
                        raise RuntimeError('Audacity disconnected before returning a result.')
                    if line.strip() == '' and lines:
                        break
                    if line.strip():
                        lines.append(line)
                result_queue.put((''.join(lines), None))
            except Exception as error:
                result_queue.put((None, error))
        threading.Thread(target=receive, daemon=True).start()
        try:
            result, error = result_queue.get(timeout=self.timeout)
        except queue.Empty:
            raise TimeoutError('Audacity response timed out; inspect its state before retrying.')
        if error:
            raise error
        if 'BatchCommand finished: OK' not in result:
            raise RuntimeError(f'Audacity command failed: {command}\n{result}')
        return result

    def close(self):
        self.writer.close()
        self.reader.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--commands', type=Path, required=True)
    parser.add_argument('--log', type=Path, required=True)
    parser.add_argument('--timeout', type=float, default=45)
    args = parser.parse_args()
    commands = json.loads(args.commands.read_text(encoding='utf-8-sig'))
    client = AudacityPipe(args.timeout)
    with args.log.open('w', encoding='utf-8') as log:
        for command in commands:
            print(command, flush=True)
            response = client.command(command)
            log.write(json.dumps({'command':command,'response':response}, ensure_ascii=False)+'\n')
            log.flush()
            print(response, flush=True)
    client.close()

if __name__ == '__main__':
    main()
