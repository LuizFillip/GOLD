import datetime

class split_filename:
    
    def __init__(self, filename):
        
        self.filename = filename
        args = self.filename.split('_')
        
        # operation and data types
        self._level = args[1]
              
        if self._level == 'L2': 
            self._product = args[2]
            self._year = int(args[3])
            self._doy = int(args[4])
   
        else:

            self._channel = args[2]
            self._product = args[3]
            
            self._year = int(args[4])
            self._doy = int(args[5])
            self._hour = int(args[6])
            self._minute = int(args[7])
            self._time = datetime.time(self._hour, self._minute)
            
        self._date = datetime.date(self._year, 1, 1) + datetime.timedelta(self._doy - 1)
        
    
    @property
    def level(self):
        return self._level
    @property
    def channel(self):
        return self._channel
    @property
    def product(self):
        return self._product
    @property
    def year(self):
        return self._year
    @property
    def doy(self):
        return self._doy
    @property
    def hour(self):
        return self._hour
    @property
    def minute(self):
        return self._minute
    
    @property 
    def datetime(self):
        return datetime.datetime.combine(self._date, self._time)
    
    def date(self, extent = True):
        if extent:
            return self._date.strftime("%d %B, %Y")
        else:
            return self._date
        
    def time(self, extent = True):
        if extent:
            return self._time.strftime("%H:%M")
        else:
            return self._time
        if self._level == 'L2':
            raise "Products of level 2 not have informations about time"