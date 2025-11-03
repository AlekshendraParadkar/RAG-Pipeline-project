from pypdf  import PdfReader

def pdf_to_chunk(pdf_path , chunk_size=500, overlap= 100):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    paragraphs = [para.strip() for para in text.split("\n") if para.strip()]

    # Join all for character-based overlapping chunking
    joined_text = " ".join(paragraphs)
    chunks = []
    start = 0
    text_len = len(joined_text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = joined_text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap  # advance by (chunk_size - overlap)
    return chunks

if __name__ == "__main__":
    chunks = pdf_to_chunk("Document.pdf", chunk_size=500, overlap=100)
    with open("chunks.txt" , "w" , encoding = "utf-8") as f:
        f.write("\n\n---\n\n".join(chunks))