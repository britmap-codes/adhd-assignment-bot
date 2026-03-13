

# Access config functions using dot notation
# from apps.telegram_bot import config

# Access utils functions using dot notation
from apps.telegram_bot import utils


"""
    TODO: create function for md_text, and other
    spaghetti code

    tasks.json, etc
    groq
    

    """



def main():
    print("Starting Assignment Helper...")

    while True:
        print("Select assignment type:")
        print("1 - Essay")
        print("2 - Coding")
        print("3 - Reading")
        print("4 - Other")
        choice = (input("Select an option(1-4): ")).strip()
        menu = {
            "1": "essay",
            "2": "coding",
            "3": "reading",
            "4": "other"
        }
        assignment_type = menu.get(choice, None)

        if assignment_type:
            break
        else: 
            print("Invalid option, choose from (1-4).")


    description = (input("Write one sentence describing the assignment: ")).strip()

    steps = utils.generate_steps(assignment_type, description)
    print("" * 50)
    print(f"Breakdown")
    print("-" * 50)
    print("\n".join(steps))
    print("-" * 50)
if __name__ == "__main__":
    main()

    # pdf_path = config.ORIGINALS_DIR /"RBC_Scholarship.pdf"

    # # filename function from utils
    # filename = utils.get_filename(pdf_path)

    # # doc_id function from utils
    # doc_id = utils.get_doc_id(pdf_path)
    #  # define cleaned pdf path
    # cleaned_pdf_path = config.CLEANED_DIR/f"{doc_id}.pdf"

    # # prepare pdf function from utils
    # profile = "rbc"
    # utils.prepare_pdf(pdf_path,cleaned_pdf_path, profile)
    
    # md_path = config.CLEANED_DIR / f"{doc_id}.md"

    # # chunking function from utils
    # chunks = utils.text_splitter(md_path)

    # # record function from utils
    # records = utils.get_chunk_record(chunks, doc_id, filename)

    # json_path = config.CHUNKS_DIR / f"{doc_id}.jsonl"

    # utils.write_jsonl(records, json_path)

    

  

     
    


 



