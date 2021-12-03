from lib.preprocessingData import PreprocessingData
class GSP:
    def __init__(self,opsi,fileDataExcel="data.xlsx",fileData="data.txt",fileParameter="para.txt",fileOuput="result.txt",minSupport=0.001):
        import copy
        import os
        from collections import defaultdict
        self.__os = os
        self.__copy = copy
        self.__opsi = opsi
        self.__defaultdict = defaultdict
        self.__fileData = fileData
        self.__fileParameter = fileParameter
        self.__fileOuput = fileOuput
        self.__fileDataExcel = fileDataExcel
        self.__minSupport = minSupport
        self.__removeExistFile(fileData)
        self.__removeExistFile(fileParameter)
        self.__removeExistFile(fileOuput)
        self.__PD = PreprocessingData(file=self.__fileDataExcel,minSupport=self.__minSupport)


    def main(self):
        self.__PD.run(outputFileData=self.__fileData,outputFileParameter=self.__fileParameter)
        tempDict = self.__PD.getProductDictList()
        print(tempDict)
        DataTuple = sorted(tempDict.items())
        DataDict={}
        for data in DataTuple:
            (x,y)=data
            DataDict[x]=y
        print(DataDict)
        count = self.__defaultdict(int)
        F = self.__defaultdict(list)
        support = self.__defaultdict(list)
        confidence = self.__defaultdict(list)
        k=1
        S=self.__Read_Data(self.__fileData)
        MS,SDC=self.__Read_Para(self.__fileParameter)
        N=len(S)
        print("N = ",N)
        if self.__opsi==1:
            self.__minSupport = float(self.__minSupport/float(N))
        print("Minimal Support = ",self.__minSupport)
        M=[] # according to MIS(i)’s stored in MS
        for i ,v in sorted(MS.items(),key=lambda kv:kv[1]):
            M.append(i)
        L,Count_L=self.__Init_Pass(M,S,N,MS)   #first pass over S, countL = frekuensi kemunculan
        F[k],support[k],confidence[k]=self.__F1gen(L,MS,Count_L,count,N,S)
        self.__printOutput(k, F[k], count, DataDict, support[k], N, confidence[k])
        k=k+1
        y = True
        while (F[k-1]):
            Candidates=[]
            
            if k==2:
                Candidates=self.__Cand2Gen(DataDict,L,Count_L,MS,SDC,N)
            else:
                Candidates=self.__MSCandGen(F[k-1],Count_L,SDC,MS,N) # To be Written
                print("Candidates = ",Candidates)
                # idx = 1
                # temp = []
                # for q in Candidates:
                #     for r in range(idx,len(Candidates)):
                #         if q == Candidates[r]:
                #             temp.append(q)
                #     idx+=1
                
                # for data in temp :
                #     Candidates.remove(data)  
                not_duplicate=[]
                for i in range(0, len(Candidates)-1):
                        if Candidates[i] not in not_duplicate:
                            not_duplicate.append(Candidates[i])
                Candidates = not_duplicate
            for t,s in S.items():
                for cand in Candidates:
                    isSequence=self.__isSubsequence(cand,s)
                    if isSequence:
                        count[str(cand)]+=1

            F[k],support[k],confidence[k]=self.__GenFk(Candidates,MS,count,N,S)

            self.__printOutput(k, F[k], count, DataDict, support[k], N, confidence[k])
            k+=1
        return
    
    def __removeExistFile(self,path):
        if self.__os.path.exists(path):
            self.__os.remove(path)

    def __Read_Data(self,file):
        with open(file) as f:
            line=f.readline()
            cnt=0
            S=self.__defaultdict(list)
            while line: 
                sequence=[]
                cnt+=1
                line=line.replace(">",'').replace('<','').replace("}{","_").replace("{","")
                for i in line.split("}, "):
                    element=[]
                    for item in i.replace("}","").split(", "):
                        element.append(int(item.strip(" \n")))
                    sequence.append(element)
                S[cnt]=sequence
                line=f.readline()
        return S

    def __Read_Para(self,file):
        with open(file) as f:
            line=f.readline()
            MS=self.__defaultdict()
            while line:
                if "MIS" in line:
                    element=line[line.find("(")+1:line.find(")")]
                    mis=line[line.find("=")+1:].lstrip(" ").lstrip("\n")
                    MS[int(element)]=float(mis)
                else:SDC=float(line[line.find("=")+1:].lstrip(" "))
                line=f.readline()
        return MS,SDC

    # Initial pass over transaction and counting the occurence of each item
    #this is eliminate any item that is below the lowest MIS
    def __Init_Pass(self,M,S,N,MS):
        Count=self.__defaultdict(int)
        Count_L=self.__defaultdict(int)
        L=[]
        for i,s in S.items():
            for item in M:
                if item in sum(s,[]):
                    Count[item]+=1
        Minimum_MIS = float('inf')
        for item in M:
            if float(Count[item]/N) >= float(self.__minSupport):
                Minimum_MIS,i=float(self.__minSupport),M.index(item)
                break
        for index in range(i-1,len(M)):
            if float(Count[M[index]]/N) >= Minimum_MIS:
                L.append(M[index])
                Count_L[M[index]]=Count[M[index]]
        return L,Count_L

    def __F1gen(self,L,MS,Count,count, N, S):
        F1=[]
        support = []
        confidence = []
        for item in L:
            counterConfidence = 0
            #Item satisfying its own MIS
            if float(Count[item]/N)>=self.__minSupport:
                itemString= "[" + str(item) +"]"
                count[itemString] = Count[item]
                F1.append([item])
                support.append(float(Count[item]/N))
                for SID in S:
                    for transaction in S[SID]:
                        if set([item]).intersection(set(transaction)):
                            counterConfidence += 1
                            break
            confidence.append(counterConfidence)
        return F1,support,confidence

    def __Cand2Gen(self,DataDict,L,L_count,MS,sdc,n):
        def Duplicate_Removal(C2):
            #remove candidates with same element like [10,10] and candidates not in lexicographic order like [30,20]
            C2[:] = [c for c in C2 if type(c[0]) is int  and  c[0]<c[1] or type(c[0]) is list]
            return C2
        if L:
            new_L = [list(DataDict.keys())[list(DataDict.values()).index(z)] for z in L]
            new_L.sort()
            print("new L =",new_L)
            L = []
            for z in new_L:
                L.append(DataDict[z])
            print("L =",L)
            c2 = []
            print("L count=",L_count)
            print("MS =",MS)
            for elemt in L:
                if(L_count[elemt] >= MS[elemt]):

                    for next_elemt in L:
                        # if elemt != next_elemt:
                            c2.append([[elemt], [next_elemt]])
                    for next_elemt in L[L.index(elemt):]:
                        if elemt != next_elemt:
                            # c2.append([next_elemt , elemt])
                            # c2.append([[elemt],[next_elemt]])
                            c2.append([elemt,next_elemt])
        # C2=Duplicate_Removal(c2)
        return c2

    def __isSubsequence(self,c,s):
        #to handle cases like [10,20,30] convert it into [[10,20,30]]
        if type(c[0]) is int:
            c=[c]

        NumElement_C=len(c)
        if NumElement_C>2:
            for elem in c:
                if type(elem) == int:
                    return False 
        flag=[0]*len(s)
        index=-1
        for element in c:
                # print("\nc = ",c)
                for i in range(index+1,len(s)):
                        tempA = set()
                        tempB = set()
                        # print("\nelement = ", element)
                        for el in element:
                            if type(el) is int:
                                tempA.add(tuple([el]))
                            else:
                                tempA.add(tuple(el))
                            
                        for men in s[i]:
                            if type(men) is int:
                                tempB.add(tuple([men]))
                            else:
                                tempB.add(tuple(men))
                        
                        # print("element = ",tempA, "S =",tempB)
                    # if len(element)==len(set(element)):
                        # print("Set A =",set(tempA))
                        # print("Set B =",set(tempB))

                        if set(tempA).issubset(set(tempB)) and not flag[i]:
                            # print("mashok")
                            index=i
                            flag[i]=1
                            break
                        # else:
                        #     print(set(tempA),"subset",set(tempB),"condition",set(tempA).issubset(set(tempB)))
        # print("Flags = ",flag)
        if sum(flag)==NumElement_C:
            return True
        else:
            return False

    def __GenFk(self,Candidates,MS,count,N,S):
        F=[]
        support = []
        confidence = []
        for cand in Candidates:
            counterConfidence = 0
            # if type(cand[0]) is list:
            #     temp=sum(cand,[])
            # temp=self.__copy.deepcopy(cand)
            # min_mis=float('inf')
            
            # for item in temp:
            #     min_mis=min(min_mis,self.__minSupport)
            if float(count[str(cand)]/N)>=float(self.__minSupport) :
                F.append(cand)
                support.append(float(count[str(cand)]/N))
                for SID in S:
                    for transaction in S[SID]:
                        tempCand = cand[0]
                        if type(tempCand) is not list:
                            tempCand = [tempCand]
                        if set(tempCand).intersection(set(transaction)):
                            counterConfidence += 1
                            break
            confidence.append(counterConfidence)
        return F,support,confidence

    def __MSCandGen(self,F,Lcount,SDC,MS,N):
        convert=lambda s:sum(s,[]) if type(s[0]) is list else self.__copy.deepcopy(s) # merges lists
        candlist=[]
        def CheckLastMIS(s2,MS):
            convert=lambda s2:sum(s2,[]) if type(s2[0]) is list else self.__copy.deepcopy(s2) 
            temp=convert(s2)
            # min_mis=float('inf')
            last_item=temp[-1]
            if len(set(temp))==1:return False # for s=[[30],[30]]
            for item in temp:
                if self.__minSupport<=MS[last_item] and item!=last_item:
                    return False
            return True
        
        def checkIfFirstMISIsSmallest(s, MS):
            convert=lambda s2:sum(s2,[]) if type(s2[0]) is list else self.__copy.deepcopy(s2) 
            temp=convert(s)
            # min_mis=float('inf')
            first_item=temp[0]
            if len(set(temp))==1:return False
            for item in temp:
                if self.__minSupport<=MS[first_item] and item!=first_item:
                    return False
            return True

        def Size(s):
            if type(s[0]) is list:
                return len(s)
            else:
                return 1

        def length(s):
            convert=lambda s:sum(s,[]) if type(s[0]) is list else self.__copy.deepcopy(s)
            return len(convert(s))
        
        def Last_MIS_Less(s1,s2):
            temp_s1=convert(s1)
            temp_s2=convert(s2)
            s1first=temp_s1[0]
            s2first=temp_s2[0]
            MISfirsts1=MS[temp_s1[0]]
            MISlasts2=MS[temp_s2[-1]]
            firstS1=temp_s1.pop(0) #remove first
            if len(temp_s2) == 2 :
                secondlastS2=temp_s2.pop(0)
            else:
                secondlastS2=temp_s2.pop(-2)# remove last but 1
            if temp_s1==temp_s2 and MISlasts2<MISfirsts1 and abs(float(Lcount[firstS1]/N)-float((Lcount[secondlastS2]/N)))<=SDC:
                if type(s1[0]) is list and len(s1[0])==1:# first is seperate element in s1
                    if type(s2[0]) is int: # if s2=[10,20] then first element of s1 should be added as list and appended with s2
                        cand=[]
                        cand.append(self.__copy.deepcopy(s1[0]))
                        cand.append(self.__copy.deepcopy(s2)) 
                        candlist.append(cand)                 
                                        
                    else:
                        cand=[self.__copy.deepcopy(s1[0])]+self.__copy.deepcopy(s2) #if s2=[[10],[20]] add just the first element of s1 as list to s2 .
                        candlist.append(cand)

                    if length(s2)==2 and Size(s2)==2 and s1first<s2first: # generate c2
                        cand=self.__copy.deepcopy(s2)
                        cand[0].insert(0,s1[0][0])
                        candlist.append(cand)       

                elif (length(s2)==2 and Size(s2)==1 and s1first<s2first) or length(s2)>2: # just generate c1
                    if type(s2[0]) is int:
                        cand=self.__copy.deepcopy(s2)
                        cand.insert(0,s1[0])
                        candlist.append(cand)

                    else:
                        first=self.__copy.deepcopy(s1[0])
                        if isinstance(first,list):item=first[0]
                        else:item=first                    
                        cand=self.__copy.deepcopy(s2)
                        cand[0].insert(0,item)
                        candlist.append(cand)
                        
        def DefaultJoin(s1,s2):
            #Fisrt probability
            temp_s1A=convert(s1)
            temp_s2A=convert(s2)
            #second probability, the elements are mirrored (flipped)
            temp_s1B=temp_s1A
            temp_s2B=temp_s2A
            # print("s1=",s1,"s2=",s2)
            # if type(s1)==int:
            #     if type(s2)==int:
            #         firstS1A=temp_s1A.pop(0) #remove first
            #         lastS2A=temp_s2A.pop()#remove last
            #     else:
            #         firstS1A=temp_s1A.pop(0) #remove first
            #         lastS2A=temp_s2A#remove last
            # else:
            #     if type(s2)==int:
            #         firstS1A=temp_s1A #remove first
            #         lastS2A=temp_s2A.pop()#remove last
            #     else:
            #         firstS1A=temp_s1A #remove first
            #         lastS2A=temp_s2A#remove last
                
            # if type(s2) == int:
            #     if type(s1) == int:
            #         firstS2B=temp_s2B.pop(0)#remove first
            #         lastS1B=temp_s1B.pop() #remove last
            #     else :
            #         firstS2B=temp_s2B.pop(0)#remove first
            #         lastS1B=temp_s1B #remove last
            # else :
            #     if type(s1) == int:
            #         firstS2B=temp_s2B#remove first
            #         lastS1B=temp_s1B.pop() #remove last
            #     else :
            #         firstS2B=temp_s2B#remove first
            #         lastS1B=temp_s1B #remove last
            # Normal
            firstS1A=temp_s1A[1:] #remove first
            lastS2A=temp_s2A[:-1] #remove last
            #Flipped
            firstS2B=temp_s2B[1:] #remove first
            lastS1B=temp_s1B[:-1] #remove last
            # print("Normal ",firstS1A,lastS2A)
            # print("Flip ",firstS2B,lastS1B)
            first_element = firstS1A
            last_element = lastS2A
            for i in range(2):
                if (first_element==last_element) and len(s2)>0 and s1 != s2:

                    last=s2[-1]

                    if type(last) is list and len(last)==1:
                        if type(s1[0]) is not int:    
                            cand=[]
                            for i in range(len(s1)):
                                cand.append(s1[i])
                            
                            print(s1,s2,"atas A before",cand,"\n")
                            cand.append(self.__copy.deepcopy(s2[-1]))
                            candlist.append(cand)
                            print("atas A",cand,"\n")
                        else:                    
                            cand = [self.__copy.deepcopy(convert(s1))]+self.__copy.deepcopy(s2[1:])
                            candlist.append(cand)
                            print("atas B", cand,"\n",s1,s2,"\nconvert s1 =",convert(s1))
                            
                    else:
                        if type(s1[0]) is int: # add the last element at end of list
                            if isinstance(last,list):
                                item=s2[-1]
                                cand=self.__copy.deepcopy(s1)
                                cand.append(item)
                                print("bawah A", cand,"\n")
                            else:
                                item=last
                                cand=self.__copy.deepcopy(s1)
                                cand.append(item)
                                print("Bawah B", cand,"\n")
                            candlist.append(cand)
                        else: # s1 adalah list 
                            if isinstance(last,list):
                                # item=s2
                                # cand=self.__copy.deepcopy(s1)
                                # cand[-1].append(item)
                                # ////////////////////////////////

                                cand=self.__copy.deepcopy(convert(s1[:len(s1)-1]))+[self.__copy.deepcopy(convert(convert(s2[-1])))] 
                                print("Bawah C", cand,"\n",s1,s2)
                            else:
                                item=s2
                                cand=self.__copy.deepcopy([s1[0]])
                                cand.append(item)
                                print("Bawah D",cand,"\n")
                            candlist.append(cand)
                first_element = firstS2B
                last_element = lastS1B
                temp = s1
                s1 = s2
                s2 = temp
                        
        def FirstMISList(s1, s2):           
                temp_s1 = convert(s1)
                temp_s2 = convert(s2)
                pop_temp_s1 = self.__copy.deepcopy(temp_s1)
                pop_temp_s1.pop(1) #remove s1's 2nd element
                pop_temp_s2 = temp_s2[:-1] #remove last element from s1
                if pop_temp_s1 == pop_temp_s2 and MS[temp_s2[-1]]>= MS[temp_s1[0]] and abs(float(Lcount.get(temp_s2[-1])/N)- float(Lcount.get(temp_s1[1])/N)) <= SDC:#check if s1 without element at 2 and s2 without last element are the same
                    
                    if isinstance(s2[-1], list) and length(s2[-1]) == 1: #l is added at the end of the last element of s1 to form another candidate sequence c2.
                        #if last element of s2 is a list and if its the only element in it     
                        #if s1 is a not a list of lists
                        if isinstance(s1[-1], int): 
                            cand=[]
                            cand.append(self.__copy.deepcopy(s1))
                            cand.append(self.__copy.deepcopy(s2[-1]))
                            candlist.append(cand)   
                            
                        else: #if s2 is a list
                            cand=self.__copy.deepcopy(s1)+[self.__copy.deepcopy(s2[-1])] #if s2=[[10],[20]] add just the first element of s1 as list to s2 .
                            candlist.append(cand)


                        if length(s1) == 2 and Size(s1) == 2 and temp_s2[-1] > temp_s1[-1]: 
                            #check leng and size of s1 and the last item of s2 is greater than the last item of s1
                            cand=self.__copy.deepcopy(s1)
                            cand[-1].extend(self.__copy.deepcopy(s2[-1]))
                            candlist.append(cand)     

                    elif (length(s1) == 2 and Size(s1) == 1 and temp_s2[-1] > temp_s1[-1]) or length(s1) > 2:

                        if type(s1[-1]) is int:
                            cand=self.__copy.deepcopy(s1)
                            cand.append(s2[-1])
                            candlist.append(cand)

                        else:
                            last=self.__copy.deepcopy(s2[-1])
                            if isinstance(last,list):item=last[-1]
                            else:item=last
                            cand=self.__copy.deepcopy(s1)
                            cand[-1].append(item)                    
                            candlist.append(cand)            
        for s1 in F:
            for s2 in F:            
                if checkIfFirstMISIsSmallest(s1, MS):  
                    FirstMISList(s1, s2)
                elif CheckLastMIS(s2,MS):
                    Last_MIS_Less(s1,s2)
                else:
                    DefaultJoin(s1,s2)
        # print("\ncandidate = ",candlist)

        prune_result = []
        for c in candlist:
            if self.__prune(c,MS,F):
                prune_result.append(c)
        candlist = prune_result
        print("\ncandidate after prune = ",candlist)
        return candlist

    def __prune(self,c,MS,F):
        # def MinMIS(s, MS):
        #     convert=lambda s2:sum(s2,[]) if type(s2[0]) is list else self.__copy.deepcopy(s2) 
        #     temp=convert(s)
        #     Min_MIS=float('inf')
            
        #     for item in temp:
        #         Min_MIS=min(Min_MIS,self.__minSupport)
        #     return Min_MIS

        # Min_MIS=MinMIS(c, self.__minSupport)
        # print("C = ",c)
        if isinstance(c[0],list):
            for I in range(len(c)):
                for item in range(len(c[I])):
                    temp=self.__copy.deepcopy(c)                    
                    if len(c[I])==1:
                        temp.remove(c[I])
                        if len(temp)==1:temp=temp[0]
                    else:
                        temp[I].remove(c[I][item])
                    temp_mis=self.__minSupport
                    if temp_mis==self.__minSupport:
                        if temp not in F:
                            return False
                        
        else:
            for i in range(len(c)):
                temp=self.__copy.deepcopy(c)
                temp.remove(c[i])
                # temp_mis=MinMIS(temp, MS)
                temp_mis=self.__minSupport
                if temp_mis==self.__minSupport:
                    if temp not in F:
                        return False
        return True

    def __printOutput(self,k, F, count, DataDict, support=[], N=0, counterConfidence=[0]):
        file = open(self.__fileOuput, "a")
        file.write("\nNo of length :{}  Frequent sequences: {}\n".format(k, len(F)))
        couter = 0
        cobain = []
        for item in counterConfidence:
            if item !=0:
                cobain.append(item)
        counterConfidence = cobain
        for cand in F:
            if type(cand[0]) is int:
                new_cand = [list(DataDict.keys())[list(DataDict.values()).index(a)] for a in cand ]
            else:
                new_cand = [[list(DataDict.keys())[list(DataDict.values()).index(z)] for z in i] for i in cand]
            cand_string = list(str(new_cand))
            if isinstance(cand[-1],list):
                cand_string[0] = '<'
                cand_string[-1] = '>'
            else:
                cand_string[0] = '<{'
                cand_string[-1] = '}>'
            for i in range(0, len(cand_string)):
                if(cand_string[i] == '['):
                    cand_string[i] = '{'
                if(cand_string[i] == ']'):
                    cand_string[i] = '}'
                if(cand_string[i] == ','):
                    if(cand_string[i-1] == '}'):
                        cand_string[i] = ''
                        cand_string[i+1] = ''
            cand_string = ''.join(cand_string)
            if support != [] and counterConfidence[couter] > 0:
                file.write("{} count: {} support: {} confidence: {}\n".format(cand_string, count[str(cand)],support[couter],count[str(cand)]/counterConfidence[couter]))
            couter += 1
        couter = 0


if __name__ =='__main__':
    main() 

