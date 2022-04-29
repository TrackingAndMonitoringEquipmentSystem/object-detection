
import time
import os
import can
from dotenv import load_dotenv
from threading import Timer
load_dotenv()


class ScanTagService:
    def __init__(self):
        self.totalCanNode = int(os.getenv('TOTAL_CAN_NODE'))
        self.bus = can.interface.Bus(bustype='socketcan',
                                     channel='can0', bitrate=25000)
        self.notifier = can.Notifier(self.bus, [self.onMessage])
        self.macAddresses = []
        self.finishedCount = 0

    def scan(self):
        for i in range(self.totalCanNode):
            # print('i:', i)
            msg = can.Message(
                arbitration_id=i+1, data=[83, 67, 65, 78], is_extended_id=True
            )
            try:
                self.bus.send(msg)
                # print("Message sent on {}".format(self.bus.channel_info))
            except can.CanError:
                # print("Message NOT sent")
                pass
            time.sleep(0.1)
        self.macAddresses = []
        self.finishedCount = 0
        self.isScanning = True
        saveTime = time.time()
        self.isTimeout = False

        while self.isScanning:
            if time.time() - saveTime >= 20:
                self.isTimeout = True
                break
        return {'isSucceed': True, 'message': 'Succeed', 'data':  list(set(self.macAddresses))}

    def onMessage(self, msg):
        if msg.arbitration_id == 0:
            if msg.data == b'finished':
                self.finishedCount += 1
                if self.finishedCount >= self.totalCanNode:
                    self.isScanning = False
            else:
                self.macAddresses.append(msg.data.hex())
        # print('msg:', msg)
        # print('self.finishedCount:', self.finishedCount)
        # print('self.macAddresses:', self.macAddresses)

    def cleanup(self):
        self.notifier.stop()
        self.bus.shutdown()


def main():
    scanTagService = ScanTagService()
    result = scanTagService.scan()
    if result['isSucceed']:
        print(result['data'])
    else:
        print(result['message'])


if __name__ == "__main__":
    main()
