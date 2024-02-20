import fitz
from PIL import Image
import os
import zipfile
from progress.bar import Bar
from concurrent.futures import ThreadPoolExecutor

def convert_page_to_image(page, output_folder, image_format):
    image = page.get_pixmap()
    # Преобразуем изображение в формат RGB (если оно не RGB)
    if image.n == 1:
        image = image.convert_to_pil()

    # Сохраняем изображение
    image_path = f"{output_folder}/page_{page.number + 1}.{image_format.lower()}"
    image.save(image_path, image_format)
    return image_path

def convert_pdf_to_images(pdf_path, output_folder, save_to_zip=False, image_format="PNG"):
    # Открываем PDF файл
    pdf_document = fitz.open(pdf_path)

    # Создаем папку для сохранения изображений, если её нет
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_paths = []

    # Используем ThreadPoolExecutor для многопоточной обработки страниц
    with ThreadPoolExecutor() as executor, Bar("Processing", max=pdf_document.page_count) as bar:
        # Итерируем по страницам PDF и сохраняем их как изображения в выбранном формате
        for image_path in executor.map(lambda page: convert_page_to_image(page, output_folder, image_format), pdf_document.pages()):
            image_paths.append(image_path)
            bar.next()

    # Закрываем PDF файл
    pdf_document.close()

    if save_to_zip:
        # Запрашиваем у пользователя настройки ZIP архива
        zip_filename = input("Введите название ZIP архива (без расширения): ")
        compression_method = int(input("Выберите метод сжатия (0 - без сжатия, 8 - сжатие Deflate): "))
        compression_level = int(input("Выберите уровень сжатия (от 0 до 9, где 0 - без сжатия, 9 - максимальное сжатие): "))
        store_files_method = int(input("Выберите метод хранения файлов в архиве (0 - вложенные папки, 1 - без вложенных папок): "))

        # Формируем полный путь к ZIP файлу
        zip_file_path = f"{output_folder}/{zip_filename}.zip"

        # Сохраняем изображения в zip-архив с выбранными настройками
        with zipfile.ZipFile(zip_file_path, 'w', compression=compression_method, compresslevel=compression_level) as zip_file, Bar("Creating ZIP", max=len(image_paths)) as bar:
            for image_path in image_paths:
                arcname = os.path.basename(image_path) if store_files_method == 1 else image_path.replace(output_folder, "")
                zip_file.write(image_path, arcname)
                bar.next()

        print(f"Изображения сохранены в zip-файл: {zip_file_path}")
    else:
        print(f"Изображения сохранены в папку: {output_folder}")

if __name__ == "__main__":
    # Пользователь выбирает путь к PDF файлу
    pdf_path = input("Введите путь к PDF файлу: ")

    # Пользователь выбирает путь для сохранения изображений или zip-файла
    output_folder = input("Введите путь для сохранения изображений или zip-файла: ")

    # Пользователь выбирает, сохранять в папку или в zip-файл
    save_to_zip = input("Хотите сохранить изображения в zip-файл? (y/n): ").lower() == 'y'

    # Пользователь выбирает формат изображения
    image_format = input("Выберите формат изображения (например, PNG, JPEG): ").upper()

    convert_pdf_to_images(pdf_path, output_folder, save_to_zip, image_format)
