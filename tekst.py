# импортируем средство для разбиения текста на токены
from nltk.tokenize import word_tokenize

# создаем класс для удобства возврата результатов из функции mainFunc
class forResult:
    def __init__(self, res1, res2, lenUniq):
        self.dictAllWordsLen = res1 # словарь для длин словоупотреблений
        self.dictOnlyUniqLen = res2 # словарь для длин словоформ
        self.averageLenUniq = lenUniq # значение средней длины словоформы

# функция, возвращающая результат подсчета словоупотреблений и словоформ для 2 языков
def mainFunc(language):
    DEBUG_MODE = False
    if language == "RUSSIAN":
        fileName = "rus1.txt"
    elif language == "ENGLISH":
        fileName = "engl1.txt"
    else:
        fileName = "textsDebug/" + language
        DEBUG_MODE = True
    
    dictAllWordsLen = {} # локальный словарь для длин словоупотреблений
    dictOnlyUniq = {}    # локальный словарь для словоупотреблений
    dictOnlyUniqLen = {} # локальный словарь для длин словоформ

    fileElem = open( fileName, 'r', encoding = "utf-8-sig" ) # открываем файл с текстом на выбранном языке
    fileText = fileElem.read() # читаем текст с файла

    # т.к. nltk разбивает на токены без учета знаков препинания, убираем их ручками
    signsToDelete = ['-', ',', '.', '–', "'", "`", ";", "!", "?", ":", " ", "<", ">", "\n", "(", ")", "“", "”", "’", "…"]
    signsDict = {} # перегоняем созданный руками лист в словарь для дальнейшего удобства
    for sign in signsToDelete:
        signsDict[sign] = True

    # функция, проверяющая оставлять нам токен или выкидывать
    def hasForbiddenSymbols(strElem):
        for symbol in strElem:
            if signsDict.get(symbol, None) == None:
                return False
        return True

    tokens = word_tokenize( fileText ) # само разбиение на токены
    newTokens = [] # создаем лист, куда будем складывать новые токены (корректные)

    for token in tokens:
        if not hasForbiddenSymbols(token): # если токен нам подходит
            if token[-1] == '.' or token[-1] == '…': # проверка нужна, ибо nltk в некоторых языках такие особенности сам не убирает
                token = token[:-1]
            token = token.lower() # изменяем регистр у токена, чтобы слова "нет" и "Нет" считались за одно (в случае словоформы это важно)
            newTokens.append(token) # добавляем токен в лист валидных токенов
            lenToken = len(token) # получаем длину токена
            dictAllWordsLen[lenToken] = dictAllWordsLen.get(lenToken, 0) + 1 # нашли токен нужной длины -> увеличиваем значение в словаре
            dictOnlyUniq[token] = True # а в этом случае нам нужны уникальные, поэтому пока просто храним, что такой есть
    
    averageLen = 0 # переменная для подсчета средней длины словоформы
    # проходимся по словарю уникальных токенов и считаем сумму длин всех словоформ
    allCountUniq = 0 # общее количество словоформ
    for token in dictOnlyUniq:
        lenToken = len(token)
        allCountUniq += 1
        averageLen += lenToken
        dictOnlyUniqLen[lenToken] = dictOnlyUniqLen.get(lenToken, 0) + 1
    averageLen = averageLen / ( allCountUniq ) # ищем среднюю длину словоформы как мат. ожидание
    # т.е. у нас есть несколько длин - умножаем их на абсолютную частоту встречаемости в тексте и затем делим на общее количество слоформ
    # возвращаем экземляр класс с 3 результатами работы, о которых описано выше
    # если нужно напечатать дебаг информацию о конечных и промежуточных результатах
    if DEBUG_MODE:
        import os, json # импортируем для записи json формата объектов, os - для того, создавать ли директорию debug
        if not os.path.exists("debug"):
            os.makedirs("debug")
        f = open( 'debug/UniqText.txt', 'w', encoding = "utf-8-sig" )
        f.write( "Словоформы:\n" )
        f.write( json.dumps( dictOnlyUniq, ensure_ascii=False ) )
        f.write( "\nОбщее количество словоформ: " + str( allCountUniq ) )
        f.write( "\nСредняя длин словоформы: " + str( averageLen ) )
        f.close()
        f = open( 'debug/AllText.txt', "w", encoding = "utf-8-sig" )
        f.write( "Словоупотребления:\n ")
        f.write( json.dumps( newTokens, ensure_ascii=False ) )
        f.close()
        f = open( 'debug/AnotherRes.txt', "w", encoding = "utf-8-sig" )
        f.write( "Длины словоупотреблений: " )
        f.write( json.dumps( dictAllWordsLen, ensure_ascii=False ) )
        f.write( "\nДлины словоформ: " )
        f.write( json.dumps( dictOnlyUniqLen, ensure_ascii=False ) )
        f.write( "\nСредняя длина словоформы: " + str( averageLen ) )
        f.close()
    return forResult(dictAllWordsLen, dictOnlyUniqLen, averageLen)

# функция, которая делает метки на графике с нужными интервалами (чтобы числа на осях друг на друга не наложились)
def createValidListTicks(values):
    import math # импортируем модуль для взятия абсолютной величины числа
    maximum = max( values ) # получаем максимум в листе
    values.sort() # сортируем список, чтобы потом было легче смотреть разницу между числами
    allowedInterval = maximum // 20 # назначаем интервал
    ansList = [values[0]] # кладем 1-ый элемент, чтобы от него ровняться дальше при добавлении нужных величин в массив
    for i in range(1, len( values ) - 1): # идем до предпоследнего, т.к. последний в любой случай добавить должны
        if abs(values[i] - ansList[-1]) >= allowedInterval: # проверка, не маленький ли модуль разности отметок
            ansList.append(values[i]) # если нет, то добавляем число к нам в результат
    ansList.append(values[-1]) # и добавляем последний элемент в лист
    return ansList # возвращаем наш самый лист

# импортируем нужные средства для работы с графиками
import matplotlib.pyplot as plt
from matplotlib import mlab
import numpy as np 

resultEnglish = mainFunc("ENGLISH") # получаем результаты для Английского
resultRussian = mainFunc("RUSSIAN") # получаем результаты для Русского

plt.figure(figsize=(20, 4))

# будем рисовать 4 графика: 2 сверху и 2 снизу
plt.subplot(1, 2, 1)
# График словоупотреблений в английском
plt.bar(x = resultEnglish.dictAllWordsLen.keys(), height = resultEnglish.dictAllWordsLen.values())
# делаем нужные метки на оси х
plt.xticks( list( resultEnglish.dictAllWordsLen.keys() ) )
# делаем нужные метки на оси y
plt.yticks( createValidListTicks( list( resultEnglish.dictAllWordsLen.values() ) ) )
plt.xlabel('Длина словоупотребления в английском языке')
plt.ylabel('Сколько встречается')

plt.subplot(1, 2, 2)
# График словоупотреблений в русском
plt.xlabel('Длина словоупотребления в русском языке')
plt.ylabel('Сколько встречается')
plt.xticks( list( resultRussian.dictAllWordsLen.keys() ) )
plt.yticks( createValidListTicks( list( resultRussian.dictAllWordsLen.values() ) ) )
plt.bar(x = resultRussian.dictAllWordsLen.keys(), height = resultRussian.dictAllWordsLen.values())
print(f"Средняя длина словоформы в русском: {resultRussian.averageLenUniq}")
print(f"Средняя длина словоформы в английском: {resultEnglish.averageLenUniq}")
plt.figure(figsize=(20, 4))
plt.subplot(1, 2, 1)
# График словоформ в английском
plt.bar(x = resultEnglish.dictOnlyUniqLen.keys(), height = resultEnglish.dictOnlyUniqLen.values())
plt.xlabel('Длина словоформы в английском языке')
plt.ylabel('Сколько встречается')
plt.xticks( list( resultEnglish.dictOnlyUniqLen.keys() ) )
plt.yticks( createValidListTicks( list( resultEnglish.dictOnlyUniqLen.values() ) ) )

plt.subplot(1, 2, 2)
# График словоформ в русском
plt.xlabel('Длина словоформы в русском языке')
plt.ylabel('Сколько встречается')
plt.bar(x = resultRussian.dictOnlyUniqLen.keys(), height = resultRussian.dictOnlyUniqLen.values() )
plt.xticks( list( resultRussian.dictOnlyUniqLen.keys() ) )
plt.yticks( createValidListTicks( list( resultRussian.dictOnlyUniqLen.values() ) ) )

# показываем наши результаты
plt.show()

# для тестов корректности работы программы
mainFunc("text1.txt")