

# Access config functions using dot notation
from apps.telegram_bot import config

# Access utils functions using dot notation
from apps.telegram_bot import utils






def main():
    print("Running smoke test...")
    pdf_path = config.ORIGINALS_DIR /"RBC_Scholarship.pdf"

    # filename function from utils
    filename = utils.get_filename(pdf_path)

    # doc_id function from utils
    doc_id = utils.get_doc_id(pdf_path)

    #

    # chunking function from utils
    chunks = utils.text_splitter(md_path)

    # record function from utils
    records = utils.get_chunk_record(chunks, doc_id, filename)

    utils.write_jsonl(records, json_path)

    """
    TODO: create function for md_text, and other
    spaghetti code

    tasks.json, etc
    groq
    

    """

  


    


 



