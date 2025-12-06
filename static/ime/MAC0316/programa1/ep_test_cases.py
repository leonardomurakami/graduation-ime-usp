import sys
import os

def clearEnvironment():
    os.system("raco pkg show plai-typed >/dev/null 2>&1 || raco pkg install --auto plai-typed")
    with open("notas.txt","w") as f:
        f.write("")
    with open("descricao_dos_resultados.txt","w") as f:
        f.write("")

def clearUnusedFiles():
    deletePaths = ["input_data.in","result.out"]
    for dp in deletePaths:
        os.remove(dp)

def getrktFiles(folderPath):
    if os.path.isfile(folderPath):
        return [folderPath]

    filePaths = []
    for f in os.listdir(folderPath):
        filePath = os.path.join(folderPath,f)
        if not (os.path.isfile(filePath) and filePath.endswith(".rkt")):
            continue

        filePaths.append(filePath)
    
    return filePaths

def getCaseTests(testsPath):
    with open(testsPath,"r") as f:
        lines = f.readlines()
    
    caseTests = {}
    curCaseTest = ""
    curGroup = ""
    for line in lines:
        if line.startswith("Case ="):
            curCaseTest = line.split("Case =")[1].strip()
            caseTests[curCaseTest] = {"input": "", "output": ""}
        elif line.startswith("input ="):
            curGroup = "input" 
            remainingInput = line.split("input =")[1]
            caseTests[curCaseTest][curGroup] += remainingInput
        elif line.startswith("output ="):
            curGroup = "output" 
            remainingOutput = line.split("output =")[1]
            caseTests[curCaseTest][curGroup] += remainingOutput
        else:
            caseTests[curCaseTest][curGroup] += line

    return caseTests

def updateInputFile(caseData):
    inputData = caseData["input"]
    with open("input_data.in","w") as f:
        f.write(inputData)

def compareOutputs(caseData):
    outputExpected = caseData["output"]
    with open("result.out","r") as f:
        outputGenerated = f.read()
    
    isEqual = (outputExpected == outputGenerated)

    return isEqual, outputExpected, outputGenerated

def testCase(caseName,caseData,filePath):
    updateInputFile(caseData)
    executionCmd = f"racket {filePath} < input_data.in > result.out 2>&1"
    os.system(executionCmd)
    isEqual, outputExpected, outputGenerated = compareOutputs(caseData)
    outputText = f"Case ={caseName}; Status ={'Success' if isEqual else 'Failure'}; Output Expected ={outputExpected}; Output Generated ={outputGenerated}\n"

    return isEqual, outputText    

def gradeFile(filePath,caseFile):
    outputString = f"File Path = {filePath}\n\n"
    outputStatus = []
    for caseName, caseData in caseFile.items():
        successOutput, curOutputString = testCase(caseName,caseData,filePath)
        outputString += curOutputString
        outputStatus.append(successOutput)
    
    grade = round(10*sum(outputStatus)/len(outputStatus),2)
    
    with open("notas.txt","a") as f:
        f.write(f"{filePath} = {grade}\n")

    with open("descricao_dos_resultados.txt","a") as f:
        f.write(f"{outputString}\n-----------------------------------\n")

def evaluateFiles():
    try:
        filesFolderPath = sys.argv[1]
        casesFilePath = sys.argv[2]
        
        clearEnvironment()
        rktFiles = getrktFiles(filesFolderPath)
        caseTests = getCaseTests(casesFilePath)

        for f in rktFiles:
            gradeFile(f,caseTests)
        
        clearUnusedFiles()
        print("Encontre a descrição dos resultados em: descricao_dos_resultados.txt")
        print("Encontre a nota dos arquivos em: notas.txt")
    except:
        print("Erro: O formato da entrada é: python3 ep_test_cases.py <caminho/da/pasta/com/arquivos/ou/do/arquivo/unico> <arquivo/de/testes>")

evaluateFiles()