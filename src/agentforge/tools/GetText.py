import pypdf
import requests
import io


class GetText:
    def read_file(self, file_name_or_url):
        if file_name_or_url.startswith('http://') or file_name_or_url.startswith('https://'):
            return self.read_from_url(file_name_or_url)
        else:
            if file_name_or_url.endswith('.pdf'):
                return self.read_pdf(file_name_or_url)
            elif file_name_or_url.endswith('.txt'):
                return self.read_txt(file_name_or_url)
            else:
                return "Unsupported file format"

    def read_pdf(self, filename):
        with open(filename, 'rb') as file:
            text = self.extract_text_from_pdf(file)
        return text

    @staticmethod
    def read_txt(filename):
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

    @staticmethod
    def extract_text_from_pdf(file_stream):
        text = ""
        reader = pypdf.PdfReader(file_stream)
        for page in reader.pages:
            text += page.extract_text()
        return text


if __name__ == "__main__":
    gettext_instance = GetText()
    filename_or_url = 'Documents'  # Replace with your file path or URL
    file_content = gettext_instance.read_file(filename_or_url)
    print(file_content)
