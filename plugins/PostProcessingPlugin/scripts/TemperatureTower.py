import re
from ..Script import Script

class TemperatureTower(Script):
    """Create Temperature Tower Settings"""
    
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        """Return script identification and GUI options."""
        # Note: The "version" key is not this script's version, but the API
        # version of the PostProcessingPlugin.
        return '''\
            {
                "name": "Temperature Tower",
                "key": "TemperatureTower",
                "metadata": {},
                "version": 2,
                "settings": {
                    "start_temperature": {
                        "label": "Start Temperature",
                        "description": "",
                        "type": "int",
                        "default_value": 260,
                        "minimum_value": "170"
                    },
                    "temperature_step": {
                        "label": "Temperature Step",
                        "description": "",
                        "type": "int",
                        "default_value": 5,
                        "minimum_value": "1"
                    },
                    "temperature_hold_height": {
                        "label": "Temperature Hold Height",
                        "description": "",
                        "type": "float",
                        "default_value": 10.0,
                        "minimum_value": "0.1"
                    },
                    "initial_z_height": {
                        "label": "Starting Z Height",
                        "description": "",
                        "type": "float",
                        "default_value": 0.0,
                        "minimum_value": "0.0"
                    }
                }
            }'''
            
    def getValue(self, line, key, default = None):
        if not key in line or (";" in line and line.find(key) > line.find(";")):
            return default
        subPart = line[line.find(key) + len(key):]
        m = re.search("^[-]?[0-9]*\.?[0-9]*", subPart)
        if m == None:
            return default
        try:
            return float(m.group(0))
        except:
            return default

    def execute(self, data):
        temperature_hold_height = self.getSettingValueByKey("temperature_hold_height")
        temperature_step = self.getSettingValueByKey("temperature_step")
        current_z_height = 0.0
        next_temp_change_height = self.getSettingValueByKey("initial_z_height")
        next_temperature = self.getSettingValueByKey("start_temperature")
        
        for index, layer in enumerate(data):
            if ';LAYER:' not in layer:
                # this may be a control layer, skip it
                continue
            modified_gcode = ''
            for line in layer.splitlines():
                if 'G0' in line or 'G1' in line:
                    z_value = self.getValue(line, 'Z', current_z_height)
                    x_value = self.getValue(line, 'X')
                    y_value = self.getValue(line, 'Y')
                    if x_value is None and y_value is None:
                        # from ChangeZ, this should be retraction
                        pass
                    elif z_value != current_z_height:
                        # if we have a layer change
                        current_z_height = z_value
                        if current_z_height >= next_temp_change_height:
                            line += '\n;TEMPERARURE TOWER\nM104 S{:.1f}'.format(next_temperature)
                            next_temp_change_height += temperature_hold_height
                            next_temperature -= temperature_step
                modified_gcode += line + '\n'
            data[index] = modified_gcode
        return data