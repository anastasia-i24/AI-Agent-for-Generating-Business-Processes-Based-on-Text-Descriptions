import os
import zipfile

def create_zip_with_par_extension(file_list, output_name):
    temp_zip = f"{output_name}.zip"
    final_par = f"{output_name}.par"

    try:
        with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in file_list:
                if os.path.exists(file_path):
                    zipf.write(file_path, arcname=os.path.basename(file_path))
                else:
                    print(f"Warning: File not found - {file_path}")


        if os.path.exists(final_par):
            os.remove(final_par)
        os.rename(temp_zip, final_par)

        return final_par

    except Exception as e:
        print(f"Error: {e}")
        if os.path.exists(temp_zip):
            os.remove(temp_zip)
        return None