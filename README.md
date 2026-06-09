<<<<<<< HEAD
# FIFA 21 Messy Dataset Cleaner

Учебный проект по очистке грязного CSV с игроками FIFA 21.

## Датасет

Источник: **FIFA 21 messy, raw dataset for cleaning/ exploring** на Kaggle:
https://www.kaggle.com/datasets/yagunnersya/fifa-21-messy-raw-dataset-for-cleaning-exploring/data?select=fifa21_raw_data.csv
В проекте используется файл `data/fifa21_raw_data_v2.csv`.

В датасете хранятся данные о футболистах:

- `ID`, `Name`, `LongName` - идентификатор и имена игрока;
- `Nationality`, `Club` - страна и клуб;
- `Age`, `↓OVA`, `POT` - возраст, текущий рейтинг и потенциал;
- `Positions`, `Best Position`, `Preferred Foot` - позиции и рабочая нога;
- `Height`, `Weight` - рост и вес в грязном строковом формате, например `183cm`, `75kg`;
- `Value`, `Wage`, `Release Clause` - стоимость, зарплата и отступные, например `€50M`, `€560K`;
- `W/F`, `SM`, `IR` - рейтинги со звездочками, например `4 ★`, `5★`;
- `Contract`, `Joined`, `Hits` - контракт, дата перехода и просмотры.

Проект умеет приводить такие значения к нормальному виду:

- `€103.5M` -> `103500000`;
- `€560K` -> `560000`;
- `183cm` -> `183`;
- `75kg` -> `75`;
- `4 ★` -> `4`;
- `1.2K` -> `1200`.

## Что делает pandas-обработка

В модуле `fifa_cleaner.pandas_processing` выполняется основная очистка:

- переименование `↓OVA` в обычный `overall`;
- очистка текстовых полей от лишних переносов строк и пробелов;
- парсинг денег, роста, веса, звездных рейтингов и просмотров;
- обработка пропусков в клубе, позициях и отступных;
- фильтрация строк с плохим возрастом, рейтингом и обязательными полями;
- создание новых колонок `primary_position`, `growth`, `value_per_overall`;
- разбор контракта на `contract_type`, `contract_start_year`, `contract_end_year`;
- сохранение очищенного CSV и JSON-отчета.

## Ленивая обработка без pandas

В модуле `fifa_cleaner.pipeline` есть отдельный pipeline без pandas:

- `PlayerDataSource` лениво читает CSV через `csv.DictReader`;
- `PlayerRowCleaner` оборачивает входной итератор и чистит строки по одной;
- `PlayerRatingFilter` лениво фильтрует игроков по рейтингу и возрасту;
- `CsvExporter` сохраняет результат.

Этот pipeline не загружает весь датасет в память.

## ООП и паттерн

В проекте есть несколько рабочих классов:

- `PlayerDataSource` - источник данных;
- `PlayerRowCleaner` - преобразователь строк;
- `PlayerRatingFilter` - ленивый фильтр;
- `CsvExporter` - экспорт результата;
- `PandasPlayerCleaner` - pandas-очистка и отчет.

Используется паттерн **Strategy**: разные правила парсинга вынесены в классы `MoneyParser`, `HeightParser`, `WeightParser`, `StarParser`, `HitsParser`. Класс `PlayerNormalizer` применяет эти стратегии к нужным колонкам.

## Исключения и декоратор

Пользовательские исключения:

- `DataFileError` - файл не найден, пустой заголовок или сломанный CSV;
- `ParseValueError` - значение поля не удалось распарсить.

Собственный декоратор `track_time` используется в `PandasPlayerCleaner.clean` и `CsvExporter.export`. Он замеряет время последнего запуска функции.

## Как запустить

Нужен Python 3.11+.

```bash
pip install -r requirements.txt
python main.py
```

После запуска появятся файлы:

- `outputs/fifa21_cleaned.csv` - очищенный датасет;
- `outputs/report.json` - короткий аналитический отчет;
- `outputs/young_top_players_lazy.csv` - результат ленивого pipeline без pandas.

## Как запустить тесты

```bash
pytest
```

В тестах используются `fixture`, `parametrize`, `pytest.raises` и пользовательская mark `integration`.
=======
# fifa21
>>>>>>> 6f94e947cc6fbdd72e7027ea45ea2ab7469d1a74
