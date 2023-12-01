import PyPDF2
import requests
import io

class GetText:
    def read_file(self, filename_or_url):
        if filename_or_url.startswith('http://') or filename_or_url.startswith('https://'):
            return self.read_from_url(filename_or_url)
        else:
            if filename_or_url.endswith('.pdf'):
                return self.read_pdf(filename_or_url)
            elif filename_or_url.endswith('.txt'):
                return self.read_txt(filename_or_url)
            else:
                return "Unsupported file format"

    def read_pdf(self, filename):
        text = ""
        with open(filename, 'rb') as file:
            text = self.extract_text_from_pdf(file)
        return text

    def read_txt(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()

    def read_from_url(self, url):
        response = requests.get(url)
        if url.endswith('.pdf'):
            return self.extract_text_from_pdf(io.BytesIO(response.content))
        elif url.endswith('.txt'):
            return response.text
        else:
            return "Unsupported file format"

    def extract_text_from_pdf(self, file_stream):
        text = ""
        reader = PyPDF2.PdfFileReader(file_stream)
        for page in range(reader.numPages):
            text += reader.getPage(page).extractText()
        return text


if __name__ == "__main__":
    gettext_instance = GetText()
    filename_or_url = 'example.pdf'  # Replace with your file path or URL
    file_content = gettext_instance.read_file(filename_or_url)
    print(file_content)
