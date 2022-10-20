import colorsys


class Color:
    def __init__(self, color_value):
        if type(color_value) == tuple:
            # Its an RGB
            r,g,b = color_value
            color_value = '%02x%02x%02x' % (r,g,b)
        elif type(color_value) == str:
            if color_value[0] == "#":
                color_value = color_value.replace("#", "")
        self.hex = color_value
        self.rgb, self.hsv, self.hsb = self.explode_hex(self.hex)
        self.rgb_index = (self.rgb[0]/255, self.rgb[1]/255, self.rgb[2]/255)
        # Comlimentary
        self.comp = self.hue_shift(180)

        # Analagous
        self.ap10 = self.hue_shift(10)
        self.ap20 = self.hue_shift(20)
        self.ap30 = self.hue_shift(30)

        self.am10 = self.hue_shift(-10)
        self.am20 = self.hue_shift(-20)
        self.am30 = self.hue_shift(-30)

        # Split complimentary 1
        self.splitp = self.hue_shift(150)
        self.splitm = self.hue_shift(-150)

        # Triadic
        self.trip = self.hue_shift(60)
        self.trim = self.hue_shift(-60)



    def generate_palette(self):

        print(f"RGB: {self.rgb}")
        print(f"HSV: {self.hsv}")
        print(f"HSB: {self.hsb}")
        print(f"Split_C1: {self.split_c1}")
        print(f"Split_C2: {self.split_c2}")

    def hsb_to_rgb(self, _ah,_as,_ab):
        h = _ah / 360
        s =  _as / 100
        v = _ab / (100/255)
        r,g,b = colorsys.hsv_to_rgb(h,s,v)
        return round(r), round(g), round(b)

    def hsb_to_hex(self, _ah, _as, _ab):
        h = _ah / 360
        s =  _as / 100
        v = _ab / (100/255)
        r,g,b = colorsys.hsv_to_rgb(h,s,v)
        r,g,b = round(r), round(g), round(b)
        _hex = '%02x%02x%02x' % (r,g,b)
        return _hex

    def hue_shift(self, amount):
        cc_s1_h, cc_s1_s, cc_s1_v = self.hsv

        cc_s1_h, cc_s1_s, cc_s1_v = cc_s1_h+(amount/360), cc_s1_s, cc_s1_v
        if cc_s1_h < 0:
            cc_s1_h = 1 + cc_s1_h
        elif cc_s1_h > 1:
            cc_s1_h = 0 + cc_s1_h
        r,g,b = colorsys.hsv_to_rgb(cc_s1_h, cc_s1_s, cc_s1_v)
        r,g,b = round(r), round(g), round(b)
        
        return '%02x%02x%02x' % (r,g,b)


    # Darkens and desaturates.
    def mute(self, amount, hex_value=None):
        if not hex_value:
            hex_value = self.hex
        rgb, hsv, hsb = self.explode_hex(hex_value)
        h,s,b = hsb
        h = h
        s = round(s * ((100-amount)/100))
        b = round(b * ((100-amount)/100))
        return self.hsb_to_hex(h,s,b)

    def explode_hex(self, _hex):
        r,g,b = _hex[0:2], _hex[2:4], _hex[4:]
        r,g,b = (round(float.fromhex(r)), round(float.fromhex(g)), round(float.fromhex(b)))
        h,s,v = colorsys.rgb_to_hsv(r,g,b)
        _ah, _as, _ab = (round(h*360), round(s*100), round((v/255)*100))
        return (r,g,b), (h,s,v), (_ah, _as, _ab)


    def hex_to_rgb1(self, _hex):
        rgb, hsv, hsb = self.explode_hex(_hex)
        return [rgb[0]/255, rgb[1]/255, rgb[2]/255]
        

    def hue_shift(self, amount, hex_value=None):
        if not hex_value:
            hex_value = self.hex
        rgb, hsv, hsb = self.explode_hex(hex_value)
        h,s,b = hsb
        h = h + amount
        if h < 0: 
            h = 360 + amount
        elif h >= 360:
            h = 0 + amount
        s = s
        b = b
        return self.hsb_to_hex(h,s,b)

    def saturation(self, amount, hex_value=None):
        if not hex_value:
            hex_value = self.hex
        rgb, hsv, hsb = self.explode_hex(hex_value)
        h,s,b = hsb
        h = h
        s = round(s * ((100+amount)/100))
        if s >= 100:
            s = 100
        elif s <= 0:
            s = 0
        b = b
        return self.hsb_to_hex(h,s,b)

    def darken(self, amount, hex_value=None):
        if not hex_value:
            hex_value = self.hex
            rgb, hsv, hsb = self.explode_hex(hex_value)
        h,s,b = hsb
        h = h
        s = s
        b = round(b * ((100-amount)/100))
        return self.hsb_to_hex(h,s,b)


