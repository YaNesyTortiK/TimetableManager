import zipfile
from bs4 import BeautifulSoup as Soup

class Parser:
    class Style:
        """
        Class to represent a style of Cell or collection of Cells.

        color: hex value of text color (examples: #000000, #ffff00)
        font: family of used font
        """
        def __init__(self, color: str | None = '00000000', bgcolor: str | None = '00000000', font: str | None = None, font_size: str | None = None):
            self.color = color
            self.font = font
            self.bgcolor = bgcolor
            self.font_size = font_size

        def __str__(self) -> str:
            return f"Color: {self.color}; Bgcolor: {self.bgcolor}; Font family: \"{self.font}\"; Font size: {self.font_size}"

    class Font:
        """
        Class to add compatibility with openpyxl. Do not use for any other reasons.
        """
        class _Color:
            def __init__(self, color: str = '00000000'):
                self.rgb = color
        def __init__(self, color: str = '00000000'):
            self.color = Parser.Font._Color(color)

    class Cell:
        """
        Class to represent a Cell in spreadsheet.

        pos: position of cell in spreadsheet (A1, B3, ...)
        content_type: type of value stored in cell (string, float, ...)
        value: value of cell
        style: style of cell (required to use Parser.Style class)
        """
        def __init__(self, pos: str, content_type: str, value, style = None):
            self.pos = pos
            self.content_type = content_type
            self.value = value
            self.style = style
            self.font = Parser.Font(self.style.color)

    class Sheet:
        def __init__(self, name: str, data: dict) -> None:
            self.name = name
            self._data = data

        def __getitem__(self, position: str):
            if position not in self._data:
                return Parser.Cell(position, 'None type', None, Parser.Style())
            return self._data[position]

    alph = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    def __init__(self, filename: str):
        self.filename = filename
        self._data = {
            'tables': []
        }
        self._styles = {
            'default': self.Style(color='00000000')
        }
        self._parse()
        self.worksheets = list(map(lambda x: self.Sheet(x, self._data[x]), self._data['tables']))
        self.active = self.worksheets[0]

    def _get_next_alph(self, cur_pos: str):
        # Функция получения имени следующего столбца
        # Прим: _next_pos('Z') -> 'AA'
        new_pos = ''
        add = True
        for x in cur_pos[::-1]:
            ind = self.alph.find(x)
            if add and ind+1 < len(self.alph):
                new_pos += self.alph[ind+1]
                add = False
            elif add and ind+1 >= len(self.alph):
                new_pos += self.alph[0]
            else:
                new_pos += x
        if add:
            new_pos += self.alph[0]
        return new_pos[::-1]

    def _get_alph(self, position: int):
        cur = 'A'
        for i in range(0, position):
            cur = self._get_next_alph(cur)
        return cur

    def _parse_styles(self, soup: Soup) -> None:
        for style in soup.find_all('style:style'):
            if style.get_attribute_list('style:family')[0] == 'table-cell':
                s_name = style.get_attribute_list('style:name')[0]
                cur_style = self.Style()
                for elem in map(str, style.contents):
                    if "fo:color=" in elem: # text color
                        cur_style.color = '00'+elem[elem.find('fo:color="')+10:elem.find('fo:color="')+17][1:]
                    if "style:font-name=" in elem: # font family
                        _temp = elem[elem.find('style:font-name="')+17:]
                        cur_style.font = _temp[:_temp.find('"')]
                    if "fo:background-color" in elem: # background color
                        cur_style.bgcolor = '00'+elem[elem.find('fo:background-color="')+21:elem.find('fo:background-color="')+28][1:]
                    if "fo:font-size" in elem: # font size
                        _temp = elem[elem.find('fo:font-size="')+14:]
                        cur_style.font_size = _temp[:_temp.find('"')]

                self._styles[s_name] = cur_style

    def _parse(self) -> None:
        fl = zipfile.ZipFile(self.filename)
        try:
            temp = fl.read('content.xml')
        except Exception as ex:
            raise f"Parsing file error (\"{ex}\"). Произошла ошибка при чтении content.xml из файла."
        soup = Soup(temp, 'xml')

        self._parse_styles(soup)

        for table in soup.find_all("table:table"):
            name = table.get_attribute_list("table:name")[0]
            self._data['tables'].append(name)
            self._data[name] = {}
            row_i = 0
            for row in table.find_all("table:table-row"):
                if not row.get_attribute_list("table:number-rows-repeated")[0] is None:
                    row_i += int(row.get_attribute_list("table:number-rows-repeated")[0])
                    continue
                c = 0
                for cell in row.find_all(["table:table-cell", "table:covered-table-cell"]):
                    if not cell.get_attribute_list('table:number-columns-repeated')[0] is None:
                        c += int(cell.get_attribute_list('table:number-columns-repeated')[0])
                    elif cell.get_attribute_list('office:value-type')[0] is None:
                        c += 1
                    else:
                        val = '\n'.join(map(lambda x: x.text, cell.find_all('text:p')))
                        style = cell.get_attribute_list('table:style-name')[0]
                        if style is None:
                            style = 'default'
                        content_type = cell.get_attribute_list('office:value-type')[0]
                        pos = self._get_alph(c)+str(row_i+1)
                        self._data[name][pos] = self.Cell(pos, content_type, val, self._styles[style])
                        c += 1
                row_i += 1
        fl.close()

    def get(self, position: str, table_name: str | None = None) -> Cell:
        """
        Getting Cell from spreadsheet.

        position: position of cell (A1, B3, ...)
        table_name(optional): table (list) name, by default - first available
        """
        if table_name is None:
            table_name = self._data['tables'][0]
        if position not in self._data[table_name]:
            return None
        return self._data[table_name][position]

    def add(self, position: str, cell: Cell, table_name: str | None = None) -> None:
        """
        Adding (or replacing) cell content.

        position: position of cell (A1, B3, ...)
        cell: instance of Parser.Cell class
        table_name(optional): table (list) name, by default - first available
        """
        if table_name is None:
            table_name = self._data['tables'][0]
        self._data[table_name][position] = cell
    
    def close(self):
        """
        Added for compatibility with openpyxl based parser
        """
        pass