def read_document(docs_service, document_id):
    doc = docs_service.documents().get(documentId=document_id).execute()
    content = doc.get("body").get("content")
    lists = doc.get("lists", {})

    formatted_text = []

    for element in content:
        if "paragraph" not in element:
            continue

        para = element["paragraph"]
        elements = para.get("elements", [])
        para_text = ""

        for elem in elements:
            text_run = elem.get("textRun")
            if not text_run:
                continue

            text = text_run.get("content", "")
            style = text_run.get("textStyle", {})

            # Apply inline styles
            if style.get("bold"):
                text = f"**{text.strip()}**"
            if style.get("italic"):
                text = f"*{text.strip()}*"

            para_text += text

        # Handle headings
        para_style = para.get("paragraphStyle", {})
        heading_type = para_style.get("namedStyleType", "")
        if heading_type and heading_type.startswith("HEADING_"):
            level = heading_type.split("_")[-1]
            hashes = "#" * int(level)
            para_text = f"{hashes} {para_text.strip()}"

        # Handle bullet points
        if "bullet" in para:
            para_text = f"- {para_text.strip()}"

        formatted_text.append(para_text.strip())

    # Join paragraphs with newlines
    return "\n\n".join([line for line in formatted_text if line])
