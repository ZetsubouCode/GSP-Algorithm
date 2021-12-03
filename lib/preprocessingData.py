class PreprocessingData:
    def __init__(self,file="Data.xlsx",minSupport=0.5) -> None:
        '''
        Class PreprocessingData berfungsi untuk mempersiapkan
        data dan file yang akan dijalankan algoritma GSP
        '''
        import pandas as pd
        self.__pd = pd
        self.__minSupport = minSupport
        self.__rawData = self.__pd.read_excel(file)
        self.__data = {}
        self.__dataProduct = {}
    
    def __makeParameterFile(self,Output="para.txt"):
        '''
        Tujuan:
        membuat file parameter seperti minimum support
        untuk proses GSP
        '''
        f = open(Output, "w")
        for product in self.__dataProduct:
            f.write("MIS({idProduct}) = {MS}\n".format(idProduct=self.__dataProduct[product],MS=self.__minSupport))
        f.write("SDC = 0.00001")
        f.close()

    def __makeTransactionFile(self,Output="data.txt"):
        '''
        Tujuan:
        membuat file transaksi dalam format
        txt yang akan diproses dengan GSP
        '''
        f = open(Output, "w")
        for customerID in self.__data:
            finalData = []
            for transaction in self.__data[customerID]:
                finalData.append(set(self.__data[customerID][transaction]))
            finalData = str(finalData).replace("[","<")
            finalData = finalData.replace("]",">")
            f.write(finalData+"\n")
        f.close()

    def __preprocessingDataProduct(self):
        '''
        Tujuan:
        membuat dictionary yang key nya nama product
        dan isi nya berupa id product dari counter
        '''
        Counter = 1
        for x in range(len(self.__rawData["Product Name"])):
            productName = self.__rawData["Product Name"][x]
            if productName not in self.__dataProduct:
                self.__dataProduct[productName] = Counter
                Counter += 1
    
    def __formatingData(self):
        '''
        Tujuan:
        data dari excel diubah menjadi dictionary
        yang sudah dirapikan, dengan sudah di
        preprocessing data product.
        '''
        for x in range(len(self.__rawData["Product Name"])):
            custID = self.__rawData["Customer ID"][x]
            ordrID = self.__rawData["Order ID"][x]
            productName = self.__rawData["Product Name"][x]
            productID = self.__dataProduct[productName]
            
            if custID not in self.__data:
                self.__data[custID] = {}
                if ordrID not in self.__data[custID]:
                    self.__data[custID][ordrID] = []
                    if productID not in self.__data[custID][ordrID]:
                        self.__data[custID][ordrID].append(productID)
                        #jika product id sudah ada dalam 1 transaksi tidak di input
                else:
                    if productID not in self.__data[custID][ordrID]:
                        self.__data[custID][ordrID].append(productID)
                        #jika product id sudah ada dalam 1 transaksi tidak di input
            else:
                if ordrID not in self.__data[custID]:
                    self.__data[custID][ordrID] = []
                    if productID not in self.__data[custID][ordrID]:
                        self.__data[custID][ordrID].append(productID)
                        #jika product id sudah ada dalam 1 transaksi tidak di input
                else:
                    if productID not in self.__data[custID][ordrID]:
                        self.__data[custID][ordrID].append(productID)
                        #jika product id sudah ada dalam 1 transaksi tidak di input
    
    def __preprocessingData(self):
        '''
        Tujuan:
        memproses data dari excel menjadi dictionary
        yang rapi siap digunakan pada proses selanjutnya
        '''
        self.__preprocessingDataProduct()
        self.__formatingData()

    def getProductDictList(self):
        return self.__dataProduct

    def run(self,outputFileData="finalData.txt",outputFileParameter="para.txt"):
        '''
        Tujuan:
        memproses data dari excel lalu di proses sedemikian rupa
        untuk membuat file dan data data yang diperlukan untuk
        menjalankan algoritma GSP
        '''
        self.__preprocessingData()
        self.__makeTransactionFile(outputFileData)
        self.__makeParameterFile(outputFileParameter)


if __name__ == "__main__":
    PD = PreprocessingData(file="Data.xlsx",minSupport=0.01)
    PD.run(self,outputFileData="finalData.txt",outputFileParameter="para.txt")