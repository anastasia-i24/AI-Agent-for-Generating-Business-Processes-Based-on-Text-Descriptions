import os
import json
from gather_data import gather_data
from build_empty_xml import empty_builder
from gpd import gpd_builder
from process_definition import process_definition_builder
from generate_par import create_zip_with_par_extension
from variables import variables

def main():
    #собираем данные (пока вручную)
    gather_data()
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    #собираем xml файлы
    empty_builder("comments", "versions")
    empty_builder("forms", "forms")
    empty_builder("variables", "variables")
    gpd_builder(data)
    process_definition_builder(data)
    variables('variables.xml', data[5])

    files_to_archive = [
        "gpd.xml",
        "processdefinition.xml",
        "comments.xml",
        "forms.xml",
        "variables.xml"
    ]

    result = create_zip_with_par_extension(
        file_list=files_to_archive,
        output_name="result"
    )
    if result:
        print(f"\nSuccessfully created: {result}")
        for i in files_to_archive:
            os.remove(i)

        import zipfile

        try:
            with zipfile.ZipFile(result, 'r') as zipf:
                print(f"\nContents of {result}:")
                for file_info in zipf.infolist():
                    print(f"  {file_info.filename} ({file_info.file_size} bytes)")
        except zipfile.BadZipFile:
            print(f"\nWarning: {result} is not a valid zip file!")


main()