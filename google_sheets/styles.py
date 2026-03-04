from .spreadsheet_requests import Color, ColorStyle, Border, BorderStyle


class Border_:
    DOTTED = Border(style=BorderStyle.DOTTED)
    DASHED = Border(style=BorderStyle.DASHED)
    SOLID = THIN = Border(style=BorderStyle.SOLID)
    SOLID_MEDIUM = MEDIUM = Border(style=BorderStyle.SOLID_MEDIUM)
    SOLID_THICK = THICK = Border(style=BorderStyle.SOLID_THICK)
    NONE = Border(style=BorderStyle.NONE)
    DOUBLE = Border(style=BorderStyle.DOUBLE)


def hex_to_rgb(hex_color) -> dict[str, float]:
    hex_color = hex_color.lstrip('#')
    red = int(hex_color[:2], 16) / 255.0
    green = int(hex_color[2:4], 16) / 255.0
    blue = int(hex_color[4:], 16) / 255.0
    return {'red': red, 'green': green, 'blue': blue}


CS = lambda c: ColorStyle(rgb_color=c)

class Color_:
    """
    Example of usage:
        from google_sheets import Color_

        CELL_STYLE_1 = CellFormat(background_color_style=Color_(hex_code='#696969'))
        CELL_STYLE_2 = CellFormat(background_color_style=Color_(red=69, green=69, blue=69))
        CELL_STYLE_3 = CellFormat(background_color_style=Color_(rgb=(69, 69, 69)))
        CELL_STYLE_4 = CellFormat(background_color_style=Color_.Basic.DARK_PURPLE_2)
        CELL_STYLE_5 = CellFormat(background_color_style=Color_.Basic.PLACE_7_10)
    """
    def __new__(
        cls, *,
        red: int = None, green: int = None, blue: int = None,
        rgb: tuple[int, int, int] = None,
        hex_code: str = None,
    ) -> ColorStyle:
        assert red is not None and green is not None and blue is not None and all(item is None for item in (rgb, hex_code,)) or \
               hex_code is not None and all(item is None for item in (red, green, blue, rgb,)) or \
               rgb is not None and all(item is None for item in (red, green, blue, hex_code,))
        if hex_code:
            return ColorStyle(rgb_color=Color(**hex_to_rgb(hex_code)))
        elif rgb:
            return ColorStyle(rgb_color=Color(red=rgb[0]/255, green=rgb[1]/255, blue=rgb[2]/255))
        else:
            return ColorStyle(rgb_color=Color(red=red/255, green=green/255, blue=blue/255))

    class ConditionalFormatting:
        # Single color templates
        GREEN_LIGHT = CS(Color(red=183/255, green=225/255, blue=205/255))
        YELLOW_LIGHT = CS(Color(red=252/255, green=232/255, blue=178/255))
        RED_LIGHT = CS(Color(red=244/255, green=199/255, blue=195/255))
        GREEN_TEXT = CS(Color(red=11/255, green=128/255, blue=67/255))
        YELLOW_TEXT = CS(Color(red=240/255, green=147/255, blue=0))
        RED_TEXT = CS(Color(red=197/255, green=57/255, blue=41/255))

        # Gradient templates
        GREEN = CS(Color(red=87/255, green=187/255, blue=138/255))
        YELLOW = CS(Color(red=1, green=214/255, blue=102/255))
        RED = CS(Color(red=230/255, green=124/255, blue=115/255))

    class Basic:  # Готовые цвета в гугл-таблице, формат констант: "PLACE_<строка>_<столбец>", индексация с единицы
        # 1 строка - серые оттенки
        PLACE_1_1 = BLACK = CS(Color(red=0, green=0, blue=0))  #000000 - черный
        PLACE_1_2 = DARK_GRAY_4 = CS(Color(red=67/255, green=67/255, blue=67/255))  #434343 - темно-серый (4)
        PLACE_1_3 = DARK_GRAY_3 = CS(Color(red=102/255, green=102/255, blue=102/255))  #666666 - темно-серый (3)
        PLACE_1_4 = DARK_GRAY_2 = CS(Color(red=153/255, green=153/255, blue=153/255))  #999999 - темно-серый (2)
        PLACE_1_5 = DARK_GRAY_1 = CS(Color(red=183/255, green=183/255, blue=183/255))  #B7B7B7 - темно-серый (1)
        PLACE_1_6 = GRAY = CS(Color(red=204/255, green=204/255, blue=204/255))  #CCCCCC - серый
        PLACE_1_7 = LIGHT_GRAY_1 = CS(Color(red=217/255, green=217/255, blue=217/255))  #D9D9D9 - светло-серый (1)
        PLACE_1_8 = LIGHT_GRAY_2 = CS(Color(red=239/255, green=239/255, blue=239/255))  #EFEFEF - светло-серый (2)
        PLACE_1_9 = LIGHT_GRAY_3 = CS(Color(red=243/255, green=243/255, blue=243/255))  #F3F3F3 - светло-серый (3)
        PLACE_1_10 = WHITE = CS(Color(red=1, green=1, blue=1))  #FFFFFF - белый

        # 2 строка - обычные цвета
        PLACE_2_1 = VINOUS = CS(Color(red=152/255, green=0, blue=0))  #980000 - бордовый
        PLACE_2_2 = RED = CS(Color(red=1, green=0, blue=0))  #FF0000 - красный
        PLACE_2_3 = ORANGE = CS(Color(red=1, green=153/255, blue=0))  #FF9900 - оранжевый
        PLACE_2_4 = YELLOW = CS(Color(red=1, green=1, blue=0))  #FFFF00 - желтый
        PLACE_2_5 = GREEN = CS(Color(red=0, green=1, blue=0))  #00FF00 - зеленый
        PLACE_2_6 = TURQUOISE = CS(Color(red=0, green=1, blue=1))  #00FFFF - бирюзовый
        PLACE_2_7 = CYAN = CS(Color(red=74/255, green=134/255, blue=232/255))  #4A86E8 - голубой
        PLACE_2_8 = BLUE = CS(Color(red=0, green=0, blue=1))  #0000FF - синий
        PLACE_2_9 = VIOLET = CS(Color(red=153/255, green=0, blue=1))  #9900FF - фиолетовый
        PLACE_2_10 = PURPLE = CS(Color(red=1, green=0, blue=1))  #FF00FF - пурпурный

        # 3 строка - "светло-... (3)"
        PLACE_3_1 = LIGHT_VINOUS_3 = CS(Color(red=230/255, green=184/255, blue=175/255))  #E6B8AF - светло-бордовый (3)
        PLACE_3_2 = LIGHT_RED_3 = CS(Color(red=244/255, green=204/255, blue=204/255))  #F4CCCC - светло-красный (3)
        PLACE_3_3 = LIGHT_ORANGE_3 = CS(Color(red=252/255, green=229/255, blue=205/255))  #FCE5CD - светло-оранжевый (3)
        PLACE_3_4 = LIGHT_YELLOW_3 = CS(Color(red=1, green=242/255, blue=204/255))  #FFF2CC - светло-желтый (3)
        PLACE_3_5 = LIGHT_GREEN_3 = CS(Color(red=217/255, green=234/255, blue=211/255))  #D9EAD3 - светло-зеленый (3)
        PLACE_3_6 = LIGHT_TURQUOISE_3 = CS(Color(red=208/255, green=224/255, blue=227/255))  #D0E0E3 - светло-бирюзовый (3)
        PLACE_3_7 = LIGHT_CYAN_3 = CS(Color(red=201/255, green=218/255, blue=248/255))  #C9DAF8 - светло-голубой (3)
        PLACE_3_8 = LIGHT_BLUE_3 = CS(Color(red=207/255, green=226/255, blue=243/255))  #CFE2F3 - светло-синий (3)
        PLACE_3_9 = LIGHT_VIOLET_3 = CS(Color(red=217/255, green=210/255, blue=233/255))  #D9D2E9 - светло-фиолетовый (3)
        PLACE_3_10 = LIGHT_PURPLE_3 = CS(Color(red=234/255, green=209/255, blue=220/255))  #EAD1DC - светло-пурпурный (3)

        # 4 строка - "светло-... (2)"
        PLACE_4_1 = LIGHT_VINOUS_2 = CS(Color(red=221/255, green=126/255, blue=107/255))  #DD7E6B - светло-бордовый (2)
        PLACE_4_2 = LIGHT_RED_2 = CS(Color(red=234/255, green=153/255, blue=153/255))  #EA9999 - светло-красный (2)
        PLACE_4_3 = LIGHT_ORANGE_2 = CS(Color(red=249/255, green=203/255, blue=156/255))  #F9CB9C - светло-оранжевый (2)
        PLACE_4_4 = LIGHT_YELLOW_2 = CS(Color(red=1, green=229/255, blue=153/255))  #FFE599 - светло-желтый (2)
        PLACE_4_5 = LIGHT_GREEN_2 = CS(Color(red=182/255, green=215/255, blue=168/255))  #B6D7A8 - светло-зеленый (2)
        PLACE_4_6 = LIGHT_TURQUOISE_2 = CS(Color(red=162/255, green=196/255, blue=201/255))  #A2C4C9 - светло-бирюзовый (2)
        PLACE_4_7 = LIGHT_CYAN_2 = CS(Color(red=164/255, green=194/255, blue=244/255))  #A4C2F4 - светло-голубой (2)
        PLACE_4_8 = LIGHT_BLUE_2 = CS(Color(red=159/255, green=197/255, blue=232/255))  #9FC5E8 - светло-синий (2)
        PLACE_4_9 = LIGHT_VIOLET_2 = CS(Color(red=180/255, green=167/255, blue=214/255))  #B4A7D6 - светло-фиолетовый (2)
        PLACE_4_10 = LIGHT_PURPLE_2 = CS(Color(red=213/255, green=166/255, blue=189/255))  #D5A6BD - светло-пурпурный (2)

        # 5 строка - "светло-... (1)"
        PLACE_5_1 = LIGHT_VINOUS_1 = CS(Color(red=204/255, green=65/255, blue=37/255))  #CC4125 - светло-бордовый (1)
        PLACE_5_2 = LIGHT_RED_1 = CS(Color(red=224/255, green=102/255, blue=102/255))  #E06666 - светло-красный (1)
        PLACE_5_3 = LIGHT_ORANGE_1 = CS(Color(red=246/255, green=178/255, blue=107/255))  #F6B26B - светло-оранжевый (1)
        PLACE_5_4 = LIGHT_YELLOW_1 = CS(Color(red=1, green=217/255, blue=102/255))  #FFD966 - светло-желтый (1)
        PLACE_5_5 = LIGHT_GREEN_1 = CS(Color(red=147/255, green=196/255, blue=125/255))  #93C47D - светло-зеленый (1)
        PLACE_5_6 = LIGHT_TURQUOISE_1 = CS(Color(red=118/255, green=165/255, blue=175/255))  #76A5AF - светло-бирюзовый (1)
        PLACE_5_7 = LIGHT_CYAN_1 = CS(Color(red=109/255, green=158/255, blue=235/255))  #6D9EEB - светло-голубой (1)
        PLACE_5_8 = LIGHT_BLUE_1 = CS(Color(red=111/255, green=168/255, blue=220/255))  #6FA8DC - светло-синий (1)
        PLACE_5_9 = LIGHT_VIOLET_1 = CS(Color(red=142/255, green=124/255, blue=195/255))  #8E7CC3 - светло-фиолетовый (1)
        PLACE_5_10 = LIGHT_PURPLE_1 = CS(Color(red=194/255, green=123/255, blue=160/255))  #C27BA0 - светло-пурпурный (1)

        # 6 строка - "темно-... (1)"
        PLACE_6_1 = DARK_VINOUS_1 = CS(Color(red=166/255, green=28/255, blue=0))  #A61C00 - темно-бордовый (1)
        PLACE_6_2 = DARK_RED_1 = CS(Color(red=204/255, green=0, blue=0))  #CC0000 - темно-красный (1)
        PLACE_6_3 = DARK_ORANGE_1 = CS(Color(red=230/255, green=145/255, blue=56/255))  #E69138 - темно-оранжевый (1)
        PLACE_6_4 = DARK_YELLOW_1 = CS(Color(red=241/255, green=194/255, blue=50/255))  #F1C232 - темно-желтый (1)
        PLACE_6_5 = DARK_GREEN_1 = CS(Color(red=106/255, green=168/255, blue=79/255))  #6AA84F - темно-зеленый (1)
        PLACE_6_6 = DARK_TURQUOISE_1 = CS(Color(red=69/255, green=129/255, blue=142/255))  #45818E - темно-бирюзовый (1)
        PLACE_6_7 = DARK_CYAN_1 = CS(Color(red=60/255, green=120/255, blue=216/255))  #3C78D8 - темно-голубой (1)
        PLACE_6_8 = DARK_BLUE_1 = CS(Color(red=61/255, green=133/255, blue=198/255))  #3D85C6 - темно-синий (1)
        PLACE_6_9 = DARK_VIOLET_1 = CS(Color(red=103/255, green=78/255, blue=167/255))  #674EA7 - темно-фиолетовый (1)
        PLACE_6_10 = DARK_PURPLE_1 = CS(Color(red=166/255, green=77/255, blue=121/255))  #A64D79 - темно-пурпурный (1)

        # 7 строка - "темно-... (2)"
        PLACE_7_1 = DARK_VINOUS_2 = CS(Color(red=133/255, green=32/255, blue=12/255))  #85200C - темно-бордовый (2)
        PLACE_7_2 = DARK_RED_2 = CS(Color(red=153/255, green=0, blue=0))  #990000 - темно-красный (2)
        PLACE_7_3 = DARK_ORANGE_2 = CS(Color(red=180/255, green=95/255, blue=6/255))  #B45F06 - темно-оранжевый (2)
        PLACE_7_4 = DARK_YELLOW_2 = CS(Color(red=191/255, green=144/255, blue=0))  #BF9000 - темно-желтый (2)
        PLACE_7_5 = DARK_GREEN_2 = CS(Color(red=56/255, green=118/255, blue=29/255))  #38761D - темно-зеленый (2)
        PLACE_7_6 = DARK_TURQUOISE_2 = CS(Color(red=19/255, green=79/255, blue=92/255))  #134F5C - темно-бирюзовый (2)
        PLACE_7_7 = DARK_CYAN_2 = CS(Color(red=17/255, green=85/255, blue=204/255))  #1155CC - темно-голубой (2)
        PLACE_7_8 = DARK_BLUE_2 = CS(Color(red=11/255, green=83/255, blue=148/255))  #0B5394 - темно-синий (2)
        PLACE_7_9 = DARK_VIOLET_2 = CS(Color(red=53/255, green=28/255, blue=117/255))  #351C75 - темно-фиолетовый (2)
        PLACE_7_10 = DARK_PURPLE_2 = CS(Color(red=116/255, green=27/255, blue=71/255))  #741B47 - темно-пурпурный (2)

        # 8 строка - "темно-... (3)"
        PLACE_8_1 = DARK_VINOUS_3 = CS(Color(red=91/255, green=15/255, blue=0))  #5B0F00 - темно-бордовый (3)
        PLACE_8_2 = DARK_RED_3 = CS(Color(red=102/255, green=0, blue=0))  #660000 - темно-красный (3)
        PLACE_8_3 = DARK_ORANGE_3 = CS(Color(red=120/255, green=63/255, blue=4/255))  #783F04 - темно-оранжевый (3)
        PLACE_8_4 = DARK_YELLOW_3 = CS(Color(red=127/255, green=96/255, blue=0))  #7F6000 - темно-желтый (3)
        PLACE_8_5 = DARK_GREEN_3 = CS(Color(red=39/255, green=78/255, blue=19/255))  #274E13 - темно-зеленый (3)
        PLACE_8_6 = DARK_TURQUOISE_3 = CS(Color(red=12/255, green=52/255, blue=61/255))  #0C343D - темно-бирюзовый (3)
        PLACE_8_7 = DARK_CYAN_3 = CS(Color(red=28/255, green=69/255, blue=135/255))  #1C4587 - темно-голубой (3)
        PLACE_8_8 = DARK_BLUE_3 = CS(Color(red=7/255, green=55/255, blue=99/255))  #073763 - темно-синий (3)
        PLACE_8_9 = DARK_VIOLET_3 = CS(Color(red=32/255, green=18/255, blue=77/255))  #20124D - темно-фиолетовый (3)
        PLACE_8_10 = DARK_PURPLE_3 = CS(Color(red=76/255, green=17/255, blue=48/255))  #4C1130 - темно-пурпурный (3)
