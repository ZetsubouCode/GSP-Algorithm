from lib.GSP import GSP

if __name__ == "__main__":
    '''
    File excelnya hanya memerlukan 3 kolom
    yaitu Customer ID, Order ID, dan Product Name
    '''
    print("OPSI")
    print("1. MS dengan frekuensi")
    print("2. MS dengan nilau pecahan")
    opsi = int(input("Pilihan :"))
    if opsi==1:
        ms = int(input("Masukkan Minimal support ="))
    elif opsi==2:
        ms = float(input("Masukkan Minimal support ="))
    else :
        print("Opsi tidak ada!")
        exit()
    
    gsp = GSP(opsi=opsi,fileDataExcel="DatasetPDF2.xlsx",minSupport=ms)
    # gsp = GSP(opsi=opsi,fileDataExcel="Dataset SPMF.xlsx",minSupport=ms)
    gsp.main()