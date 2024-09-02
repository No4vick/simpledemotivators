import io
import sys
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
import os


class Demotivator:
    def __init__(self, top_text='', bottom_text=''):
        self._top_text = top_text
        self._bottom_text = bottom_text
        self.raw_data: bytes | None = None

    def get_text_width(self, font):
        left, _, right, _ = font.getbbox(self._top_text)
        width = right - left
        return width

    def create(self, file: str | bytes, watermark=None, result_filename='demresult.jpg',
               font_color='white', fill_color='black',
               font_name='times.ttf', top_size=80, bottom_size=60,
               arrange=False, use_url=False, use_bytes=False, delete_file=False, return_raw=False, down_arrange=False) \
            -> bool:  # Returns True if method executed successfully

        if use_bytes:
            file = io.BytesIO(file)
        elif type(file) is not str:
            raise TypeError("Нельзя использовать байты по умолчанию.")

        if use_url:
            p = requests.get(file)
            file = io.BytesIO(p.content)

        """
        Создаем шаблон для демотиватора
        Вставляем фотографию в рамку
        """

        if arrange or down_arrange:
            user_img = Image.open(file).convert("RGBA")
            (width, height) = user_img.size
            if down_arrange:
                coefficient = height / 710
                width = int(width / coefficient)
                height = 710
                user_img = user_img.resize((width, height))
                img = Image.new('RGB', (width + 250, height + 314), color=fill_color)
            else:
                img = Image.new('RGB', (width + 250, height + 260), color=fill_color)
            img_border = Image.new('RGB', (width + 10, height + 10), color='#000000')
            border = ImageOps.expand(img_border, border=2, fill='#ffffff')
            img.paste(border, (111, 96))
            img.paste(user_img, (118, 103))
            drawer = ImageDraw.Draw(img)
        else:
            img = Image.new('RGB', (1280, 1024), color=fill_color)
            img_border = Image.new('RGB', (1060, 720), color='#000000')
            border = ImageOps.expand(img_border, border=2, fill='#ffffff')
            user_img = Image.open(file).convert("RGBA").resize((1050, 710))
            (width, height) = user_img.size
            img.paste(border, (111, 96))
            img.paste(user_img, (118, 103))
            drawer = ImageDraw.Draw(img)

        """Подбираем оптимальный размер шрифта
        
        Добавляем текст в шаблон для демотиватора

        """
        font_1 = ImageFont.truetype(font=f"/app/{font_name}", size=top_size, encoding='UTF-8')
        # text_width = font_1.getsize(self._top_text)[0]
        text_width = self.get_text_width(font_1)

        while text_width >= (width + 250) - 20:
            font_1 = ImageFont.truetype(font=f"/app/{font_name}", size=top_size, encoding='UTF-8')
            text_width = self.get_text_width(font_1)
            top_size -= 1

        font_2 = ImageFont.truetype(font=f"/app/{font_name}", size=bottom_size, encoding='UTF-8')
        text_width = self.get_text_width(font_2)

        while text_width >= (width + 250) - 20:
            font_2 = ImageFont.truetype(font=f"/app/{font_name}", size=bottom_size, encoding='UTF-8')
            text_width = self.get_text_width(font_2)
            bottom_size -= 1

        left, top, right, bottom = drawer.textbbox([0, 0] ,self._top_text, font=font_1)
        size_1 = right - left, bottom - top
        left, top, right, bottom = drawer.textbbox([0, 0], self._bottom_text, font=font_2)
        size_2 = right - left, bottom - top

        if arrange or down_arrange:
            top_y = 840 if down_arrange else ((height + 190) - size_1[1])
            bottom_y = 930 if down_arrange else ((height + 235) - size_2[1])
            drawer.text((((width + 250) - size_1[0]) / 2, top_y),
                        self._top_text, fill=font_color,
                        font=font_1)
            drawer.text((((width + 250) - size_2[0]) / 2, bottom_y),
                        self._bottom_text, fill=font_color,
                        font=font_2)
        else:
            drawer.text(((1280 - size_1[0]) / 2, 840), self._top_text, fill=font_color, font=font_1)
            drawer.text(((1280 - size_2[0]) / 2, 930), self._bottom_text, fill=font_color, font=font_2)

        if watermark is not None:
            (width, height) = img.size
            idraw = ImageDraw.Draw(img)

            idraw.line((1000 - len(watermark) * 5, 817, 1008 + len(watermark) * 5, 817), fill=0, width=4)

            font_2 = ImageFont.truetype(font=f"/app/{font_name}", size=20, encoding='UTF-8')
            left, top, right, bottom = idraw.textbbox([0, 0], watermark.lower(), font=font_2)
            size_2 = right - left, bottom - top
            idraw.text((((width + 729) - size_2[0]) / 2, ((height - 192) - size_2[1])),
                       watermark.lower(), font=font_2)

        if return_raw:
            data = io.BytesIO()
            img.save(data, format="JPEG")
            self.raw_data = data.getvalue()
        else:
            img.save(result_filename)

        if delete_file:
            os.remove(file)

        return True

    def clear_data(self):
        self.raw_data = None
