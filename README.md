# Парсер книг с сайта tululu.org
Скрипты скачивания книг в текстовом формате и изображений обложек.

## Как установить
* Python3 должен быть установлен
* Установите необходимые библиотеки командой
  ```
  pip install -r requirements.txt
  ```
* Чтобы скачать все книги запустите скрипт командой
  ```
  python parse_tululu_books.py
  ```
* Чтобы скачать все книги из категории "Научная фантастика" запустите скрипт командой
  ```
  python parse_tululu_category.py
  ```
  
## Аргументы parse_tululu_books
Скрипт скачивает книги по их id.
Файлы сохраняются в директории `media` в каталогах `books` и `images` соответственно.
Для скачанных книг в консоль выводится их название, жанр и комментариии.
По умолчанию установлены два аргумента:

`start_id` - id книги с которой начнется качивание, по умолчанию 0

`stop_id` - id книги на которой завершится скачивание, по умолчанию 10

Например, при запуске следующей команды:
  ```
  python parse_tululu_books.py 20 30
  ```
скрипт скачает книги с 20 по 30.

Пример работы:

![](https://i.ibb.co/X4Qpmv4/image.png)


## Аргументы parse_tululu_category
Скрипт скачивает книги из категории "Научная фантастика".
Помимо файлов книг скрипт создает файл `books_data.json` с информацией о скачанных книгах.
По умолчанию файлы сохраняются в директории проекта.
Изменить ее можно указав соответствующий аргумент.

`--start_page` - номер стартовой страницы, с которой начнется скачивание (по умолчанию 1),

`--end_page` - номер конечной страницы для скачивания (по умолчанию 701),

`--dest_folder` - путь к каталогу с результатами парсинга: картинкам, книгам, JSON, (по умолчанию директория скрипта),

`--skip_imgs` - если указан, обложки книг не будут скачаны,

`--skip_txt` - если указан, файлы книг не будут скачаны.

Например, при запуске следующей команды:
  ```
  python parse_tululu_books.py --start_page 2 --end_page 4 --dest_folder C:\folder --skip_imgs
  ```
скрипт скачает все книги со второй по четвертую страницы в директорию `C:\folder`, при этом не
будет скачивать обложки книг.

## Сайт библиотеки
Онлан-версия сайта доступна по [ссылке](https://free-flow-code.github.io/online-library/).

Чтобы запустить сайт локально, введите команду:
```
python render_website.py
```
и перейдите в браузере по ссылке `http://127.0.0.1:5500`

Скрипт принимает аргумент:

`--json-folder` - путь к JSON файлу с данными книг.

HTML страницы сайта будут автоматически сгенерированы в директории `pages` в каталоге проекта.

Внешний вид сайта:

![](https://i.ibb.co/rFBP7WW/image.png)

## Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
