from pathlib import Path


class SwitchModule:
    def __init__(self, switch_lib_path: str, serial_number: str):
        # noinspection PyUnresolvedReferences
        import clr
        clr.AddReference(str(Path(switch_lib_path).resolve()))
        # noinspection PyUnresolvedReferences
        from mcl_SolidStateSwitch64 import USB_Digital_Switch
        self._switch = USB_Digital_Switch()
        self._switch.Connect(serial_number)

    def _send_scpi_command(self, command: str):
        return self._switch.Send_SCPI(command, '')[2]

    def set_switch_port(self, port):
        command = ':SP16T:STATE:' + str(port)
        ret = self._send_scpi_command(command)
        return int(ret)

    def get_switch_port(self):
        command = ':SP16T:STATE?'
        ret = self._send_scpi_command(command)
        return int(ret)
