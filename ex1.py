from datetime import datetime
myFile = open('output.txt', 'a')
myFile.write('\nAccessed on ' + str(datetime.now()))
