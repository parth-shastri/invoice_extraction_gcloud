import requests
import os
import glob
import pandas as pd

# Replace these values with your actual endpoint, file path, and bearer token
# url = "https://icici-invoice-extraction-dot-document-warehouse-poc-392110.el.r.appspot.com/predict"
url = "http://127.0.0.1:8080/predict"



# Path to the directory containing the files
directory_path = "/Users/parthshastri/Downloads/invoices_tagging/Hyundai"

dest_dir_path = "/Users/parthshastri/Downloads/invoice_csv/Hyundai"

d = 1
data_ = []
# Loop through each file in the directory
for filepath in glob.glob(os.path.join(directory_path, "**/*.*"), recursive=True):
    filename = filepath.split('/')[-1]
    if filename.startswith(".DS_Store"):
        continue  # Skip .DS_Store files
    

    file_path = filepath



# ["DL", "VI", "PAN", "PSS", "ADH", "INV", "OTH"]
    # Open the file and prepare it for upload
    with open(file_path, "rb") as file:
        print(f"hitting ======> {d}, {file_path}")
        d+=1
        files = {'document':file}
        data = {"parser":"hyundai"}
        response = requests.post(url, files=files)
    

   # Print the response
    if response.status_code == 200:
        content_disposition = response.headers.get('content-disposition')
        if content_disposition:
            # filename = content_disposition.split('filename=')[1]
            file_name = filename.split('.')[:-1]
            file_name =   '/' + ''.join(file_name) + '.csv'
            with open(dest_dir_path + file_name, 'wb') as f:
                f.write(response.content)
            print(f"Response saved as {filename}")
        else:
            print("Response doesn't contain a filename")
        data_.append([filename,file_name])
    else:
        print(f"Request failed with status code: {response.status_code}")





# Convert the list to a DataFrame
columns = ["source_docs","csv_docs"]
df = pd.DataFrame(data_, columns=columns)

# Save the DataFrame to a CSV file
csv_filename = "toyota.csv"
df.to_csv(csv_filename, index=False)

print(f"CSV file '{csv_filename}' created successfully.")
