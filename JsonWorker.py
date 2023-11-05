import json

class JsonWorker():
    __filePath : str
    __dataFrame = None
    def __init__(self, filePath : str) -> None:
        self.__filePath = filePath
        fd = open(filePath)
        if fd != None:
            self.__dataFrame = json.load(fd)
        else:
            pass

    def __del__(self):
        pass
    
    def GetSpreadId(self) -> str:
        output = ""
        if self.__dataFrame.get("ID"):
            output = self.__dataFrame["ID"]
        return output
    
    def GetGmailScope(self) -> str:
        output = ""
        if self.__dataFrame.get("Gmail Scope"):
            output = self.__dataFrame["Gmail Scope"]
        return output

    def GetSheetScope(self) -> str:
        output = ""
        if self.__dataFrame.get("Sheet Scope"):
            output = self.__dataFrame["Sheet Scope"]
        return output

    def GetSheetRange(self) -> str:
        output = ""
        if self.__dataFrame.get("Range"):
            output = self.__dataFrame["Range"]
        return output
    
    def GetGmailTitle(self) -> list:
        output = []
        if self.__dataFrame.get("Title"):
            output = self.__dataFrame["Title"]
        return output

    def GetDataTitle(self) -> list:
        output = []
        all_data = self.__dataFrame.get("Data")
        for data in all_data:
            if self.__dataFrame["Data"][data].get("Title"):
                output.append(self.__dataFrame["Data"][data].get("Title"))
        return output

    def GetDataFilter(self) -> list:
        output = []
        all_data = self.__dataFrame["Data"]
        for data in all_data:
            my_filter = []
            if self.__dataFrame["Data"][data].get("Filter"):
                if self.__dataFrame["Data"][data]["Filter"].get("Before"):
                    my_filter.append(self.__dataFrame["Data"][data]["Filter"].get("Before"))
                if self.__dataFrame["Data"][data]["Filter"].get("After"):
                    my_filter.append(self.__dataFrame["Data"][data]["Filter"].get("After"))
            output.append(my_filter)
        return output

    def GetIsSheetName(self) -> list:
        output = []
        all_data = self.__dataFrame.get("Data")
        for data in all_data:
            if self.__dataFrame["Data"][data].get("Sheet Name"):
                output.append(self.__dataFrame["Data"][data].get("Sheet Name"))
        return output

    def GetInitEmailNum(self) -> int:
        output = 0
        if self.__dataFrame.get("Initial Email Number"):
            output = self.__dataFrame["Initial Email Number"]
        return output

    def GetNormalEmailNum(self) -> int:
        output = 0
        if self.__dataFrame.get("Normal Email Number"):
            output = self.__dataFrame["Normal Email Number"]
        return output

    def GetEmailLabels(self) -> list:
        output = []
        if self.__dataFrame.get("Email Labels"):
            output = self.__dataFrame["Email Labels"]
        return output