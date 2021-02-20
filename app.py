
'''
TO DO:
Perform check (using lock file maybe?) when Sync is pressed
Display file size (in MB)
Display length (in hours)
Have Sync button stay on screen at all times
'''

from flask import Flask, render_template, url_for, jsonify, request
import requests
import os
import json
import shutil

app = Flask(__name__)

@app.route('/')
def index():
  def get_library():
    json_library = requests.get(url='http://192.168.1.2:5200/get_library').json()
    
    audiobook_authors_path = "/mnt/plexmedia/Audiobooks_Sync"
    previously_synced_audiobooks = {}
    author_dirpath, author_dirnames, author_filenames = next(os.walk(audiobook_authors_path))
    author_dirnames.remove(".stfolder") # Syncthing folder

    for author_dirname in author_dirnames:
      previously_synced_audiobooks[author_dirname] = []
      audiobook_book_path = os.path.join(author_dirpath, author_dirname)
      book_dirpath, book_dirnames, book_filenames = next(os.walk(audiobook_book_path))

      for book_dirname in book_dirnames:
        previously_synced_audiobooks[author_dirname].append(book_dirname)

    print(previously_synced_audiobooks)

    for author in previously_synced_audiobooks:
      print(f"* {author}")
      for book in previously_synced_audiobooks[author]:
        print(f"  * {book}")

        json_library[author][book]["previously_synced"] = 1


    # print(json_library["Agatha Christie"])
    return json_library
  
  return render_template(
    'index.html',
    # myname="Alan",
    library=get_library(),
    # current_track=get_current_track()
  )


@app.route('/sync_folders', methods=['POST'])
def sync_folders():
  decoded_value = request.data.decode('utf-8')
  json_value = json.loads(decoded_value)

  for folder in json_value["toBeSynced"]:
    source_folder = f"/mnt/plexmedia/Audiobooks/{folder}"
    destination_folder = f"/mnt/plexmedia/Audiobooks_Sync/{folder}"

    print("*** BEGINNING COPY ***")
    print(f"Source:      {source_folder}")
    print(f"Destination: {destination_folder}")
    shutil.copytree(source_folder, destination_folder)
    print("Copy complete")

  for folder in json_value["toBeRemoved"]:
    destination_folder = f"/mnt/plexmedia/Audiobooks_Sync/{folder}"
    
    print("*** BEGINNING DELETE ***")
    print(f"Deleting: {destination_folder}")
    shutil.rmtree(destination_folder)
    print("Delete complete")

  print("*** CHECKING FOR EMPTY FOLDERS ***")
  audiobook_authors_path = "/mnt/plexmedia/Audiobooks_Sync"
  author_dirpath, author_dirnames, author_filenames = next(os.walk(audiobook_authors_path))
  author_dirnames.remove(".stfolder") # Syncthing folder

  for author_dirname in author_dirnames:
    full_path = os.path.join(author_dirpath, author_dirname)
    if(len(os.listdir(full_path)) == 0):
      print(f"Deleting: {full_path}")
      shutil.rmtree(full_path)

  print("Check complete")

  return "Sync successful"


if __name__ == "__main__":
  app.run(debug=True, host= '0.0.0.0', port=5300)

