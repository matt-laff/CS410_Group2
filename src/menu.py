class Menu:

    def __init__(self) -> None:
        self._title = ""
        self._options = list()
        self._border_char = "*"
        self._width = 0
        self._height = 0
        self._width_mod = 12
    
    def __str__(self) -> str:
        menu_str = str(f"{self._border_char * (self._width + self._width_mod)}\n")
        option_num = 1
        for option in self._options:
            print("??")
            menu_str += str((self._border_char) + " [" + str(option_num) + "] " + str(option) + " \n")
            option_num += 1
        menu_str += str(f"{self._border_char * (self._width + self._width_mod)}\n")
        return menu_str


    def set_title(self, title: str):
        if (title == None):
            raise ValueError("Cant set title with null")
        if (len(title) > self._width):
            self._width = len(title) 
        self._title = str(title)

    
    def add_option(self, option: str):
        if (option == None):
            raise ValueError("Can't create an option with null option")

        if (len(option) > self._width):
            self._width = len(option)

        self._options.append(str(option))
        self._height += 1