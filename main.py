import os
from gather_data import gather_data
from build_empty_xml import empty_builder
from gpd import gpd
from process_definition import process_definition_builder
from generate_par import create_zip_with_par_extension
from variables import variables
from generate_ids import generate_ids

def main():
    #собираем данные (пока вручную)
    data = gather_data()

    #получаем id
    ids = generate_ids(data)
    
    #собираем xml файлы
    empty_builder("comments", "versions")
    empty_builder("forms", "forms")
    empty_builder("variables", "variables")
    empty_builder("gpd", "process-diagram")
    process_definition_builder(data, ids)
    gpd("gpd.xml", data, ids)
    variables('variables.xml', data)

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