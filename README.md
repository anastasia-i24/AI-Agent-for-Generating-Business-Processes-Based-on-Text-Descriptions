<a id="readme-top"></a>
# ИИ-агент для генерации бизнес-процессов по тектовому описанию
### Содержание
  <ol>
    <li><a href="#описание">Описание</a></li>
    <li><a href="#начало-работы">Начало работы</a>
    <li><a href="#использование">Использование</a></li>
    <li><a href="#лицензия">Лицензия</a></li>
    <li><a href="#участники-проекта">Участники проекта</a></li>
    <li><a href="#контакты">Контакты</a></li>
  </ol>


## Описание

BPMN Generator — это инструмент на основе больших языковых моделей (LLM), который автоматически преобразует текстовое описание бизнес-процесса в готовый PAR-архив для системы RunaWFE. Вы описываете процесс словами — программа генерирует диаграмму и все необходимые файлы для загрузки в редактор бизнес-процессов.


## Начало работы
[![Windows](https://img.shields.io/badge/Windows-Download-blue?style=for-the-badge&logo=windows)](https://github.com/anastasia-i24/AI-Agent-for-Generating-Business-Processes-Based-on-Text-Descriptions/releases/latest/download/BPMNGenerator.exe)\
[![macOS](https://img.shields.io/badge/macOS-Download-lightblue?style=for-the-badge&logo=apple)](https://github.com/anastasia-i24/AI-Agent-for-Generating-Business-Processes-Based-on-Text-Descriptions/releases/latest/download/BPMNGenerator.zip)\
Внимание! Если программа не открывается на macOS, введите в терминале 
```sh
   xattr -dr com.apple.quarantine /путь_к_программе/BPMNGenerator.app
```

## Использование
Для работы с программой Вам понадобится [OpenAI API](https://github.com/dan1471/FREE-openai-api-keys) ключ

1. Введите текстовое описание бизнес-процесса. Чем подробнее описание - тем лучше
2. Введите свой OpenAI API ключ
3. Введите значение температуры (по умолчанию значение 0 для воспроизводимых результатов)
4. Программа выдаст результат - архив result.par
5. Чтобы увидеть получившийся бизнес-процесс, загрузите архив
- [в онлайн-редактор бизнес-процессов RunaWFE Online Lite](https://runawfe.ru/RunaWFE_Cloud_Lite)
- [в приложение для редактирования бизнес-процессов Runa-gpd](https://runawfe.ru/RunaWFE)

## Лицензия

Распространяется по лицензии LGPL-2.1 license. Дополнительную информацию смотрите в файле LICENSE.txt.

## Участники проекта

* [Швайковский Сергей](https://github.com/SiriusIsMe)
* [Алексеев Максим](https://github.com/AlekseevMD)
* [Вишнякова Анастасия](https://github.com/anastasia-i24)

## Контакты

Вишнякова Анастасия - [@anastasia_i24](https://t.me/anastasia_i24) - asvishnyakova@edu.hse.ru

Ссылка на проект: [https://github.com/anastasia-i24/AI-Agent-for-Generating-Business-Processes-Based-on-Text-Descriptions](https://github.com/anastasia-i24/AI-Agent-for-Generating-Business-Processes-Based-on-Text-Descriptions)

<p align="right">(<a href="#readme-top">наверх</a>)</p>
