class CmnBase():
    def SizeOf(self, data):
        output = 0
        if data != None:
            output = len(data)
        return output