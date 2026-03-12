# -----------------------------
# 题目：实现简单的单位换算器。
# 描述：支持长度、重量、温度等单位换算。
# -----------------------------

class UnitConverter:
    def __init__(self):
        self.length_units = {
            'mm': 0.001,
            'cm': 0.01,
            'm': 1,
            'km': 1000,
            'in': 0.0254,
            'ft': 0.3048,
            'yd': 0.9144,
            'mi': 1609.344
        }
        
        self.weight_units = {
            'mg': 0.001,
            'g': 1,
            'kg': 1000,
            'oz': 28.3495,
            'lb': 453.592
        }
        
        self.temperature_units = ['c', 'f', 'k']
    
    def convert_length(self, value, from_unit, to_unit):
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        if from_unit not in self.length_units or to_unit not in self.length_units:
            return None
        
        meters = value * self.length_units[from_unit]
        return meters / self.length_units[to_unit]
    
    def convert_weight(self, value, from_unit, to_unit):
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        if from_unit not in self.weight_units or to_unit not in self.weight_units:
            return None
        
        grams = value * self.weight_units[from_unit]
        return grams / self.weight_units[to_unit]
    
    def convert_temperature(self, value, from_unit, to_unit):
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        if from_unit not in self.temperature_units or to_unit not in self.temperature_units:
            return None
        
        if from_unit == to_unit:
            return value
        
        if from_unit == 'c':
            if to_unit == 'f':
                return value * 9/5 + 32
            elif to_unit == 'k':
                return value + 273.15
        
        elif from_unit == 'f':
            if to_unit == 'c':
                return (value - 32) * 5/9
            elif to_unit == 'k':
                return (value - 32) * 5/9 + 273.15
        
        elif from_unit == 'k':
            if to_unit == 'c':
                return value - 273.15
            elif to_unit == 'f':
                return (value - 273.15) * 9/5 + 32
        
        return None
    
    def convert(self, value, from_unit, to_unit, category='auto'):
        if category == 'length':
            return self.convert_length(value, from_unit, to_unit)
        elif category == 'weight':
            return self.convert_weight(value, from_unit, to_unit)
        elif category == 'temperature':
            return self.convert_temperature(value, from_unit, to_unit)
        else:
            result = self.convert_length(value, from_unit, to_unit)
            if result is not None:
                return result
            
            result = self.convert_weight(value, from_unit, to_unit)
            if result is not None:
                return result
            
            result = self.convert_temperature(value, from_unit, to_unit)
            return result
    
    def list_units(self, category):
        if category == 'length':
            return list(self.length_units.keys())
        elif category == 'weight':
            return list(self.weight_units.keys())
        elif category == 'temperature':
            return self.temperature_units
        return []

def main():
    converter = UnitConverter()
    
    print("长度换算:")
    print(f"  1 km = {converter.convert_length(1, 'km', 'm')} m")
    print(f"  1 ft = {converter.convert_length(1, 'ft', 'cm'):.2f} cm")
    
    print("\n重量换算:")
    print(f"  1 kg = {converter.convert_weight(1, 'kg', 'g')} g")
    print(f"  1 lb = {converter.convert_weight(1, 'lb', 'kg'):.2f} kg")
    
    print("\n温度换算:")
    print(f"  0°C = {converter.convert_temperature(0, 'c', 'f')}°F")
    print(f"  100°C = {converter.convert_temperature(100, 'c', 'k')}K")


if __name__ == "__main__":
    main()
