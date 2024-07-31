class Menu:

    def __init__(self) -> None:
        self._title = ""
        self._options = list()
        self._option_map = {}
        self._func_map = {}
        self._num_options = 0
        self._border_char = "*"
        self._width = 0
        self._height = 0
        self._width_mod = 12
    
    def __str__(self) -> str:
        menu_str = str(f"{self._border_char * (self._width + self._width_mod)}\n")
        option_num = 1
        for option in self._options:
            add_width = (self._width) - len(option) + 5
            menu_str += str((self._border_char) + " [" + str(option_num) + "] " + str(option) + str((" " * add_width)) + "*\n")
            option_num += 1
        menu_str += str(f"{self._border_char * (self._width + self._width_mod)}\n")
        return menu_str


    def set_title(self, title: str):
        if (title == None):
            raise ValueError("Cant set title with null")
        if (len(title) > self._width):
            self._width = len(title) 
        self._title = str(title)

    
    def add_option(self, option, func, *args):
        if (option == None):
            raise ValueError("Can't create an option with null option")

        if (len(option) > self._width):
            self._width = len(option)

        self._options.append(str(option))
        self._height += 1
        self._num_options += 1
        self._option_map[self._num_options] = str(option)
        if( func == None):
            self._func_map[option] = None
        else:
            self._func_map[option] = lambda:func(*args)


    def get_selection(self):
        selection = int(input("Please make a selection "))
        if selection > self._num_options or selection <= 0:
            print("Option does not exist")
            return None
        return (self._option_map[selection])


    def execute_option(self, option_str):
        if not option_str in self._func_map:
            raise ValueError("Option not in map")
        else:
           if (self._func_map[option_str] == None):
               return None
           success = self._func_map[option_str]()
           return success 





